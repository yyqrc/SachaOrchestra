import { afterEach, describe, expect, it, vi } from 'vitest'
import { activityPollDelay, observeSachaActivity, selectSessionSnapshot, type ActivityObservation } from '../src/client/activity-monitor.ts'
import type { SachaActivitySnapshot } from '../src/types.ts'

function snapshot(sessionId: string): SachaActivitySnapshot {
  return {
    available: true,
    sessionId,
    events: [],
    state: { gates: {}, waves: [], delegations: [], evidence: {} },
    subagents: { available: true, children: [] },
    warnings: [],
  }
}

describe('session-scoped activity snapshots', () => {
  afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals() })
  it('hides an older session snapshot until the requested session arrives', () => {
    const previous = snapshot('session-a')
    expect(selectSessionSnapshot(previous, 'session-b')).toBeUndefined()
    expect(selectSessionSnapshot(previous, undefined)).toBeUndefined()
    expect(selectSessionSnapshot(previous, 'session-a')).toBe(previous)
  })

  it('uses cold polling for history and hidden panels, and hot polling for ongoing work', () => {
    const idle = snapshot('a')
    const running = { ...idle, subagents: { available: true, children: [{ id: 'child', label: 'child', status: 'running' as const, hasChildren: false }] } }
    expect(activityPollDelay(idle, true)).toBe(5000)
    expect(activityPollDelay(running, true)).toBe(1000)
    expect(activityPollDelay(running, false)).toBe(5000)
    const phase = { eventType: 'phase' as const, phase: 'complete' as const, state: 'completed' as const, summary: '完成' }
    const completed = { ...idle, events: [{ seq: 1, time: 1, value: phase }], state: { ...idle.state, phase } }
    expect(activityPollDelay(completed, true)).toBe(5000)
  })

  it('changes the actual timer between visible activity and hidden or idle state', async () => {
    vi.useFakeTimers()
    let visible = true
    const idle = snapshot('a')
    let current: SachaActivitySnapshot = { ...idle, subagents: { available: true, children: [{ id: 'child', label: 'child', status: 'running', hasChildren: false }] } }
    const fetcher = vi.fn().mockImplementation(async () => ({ ok: true, json: async () => current }))
    vi.stubGlobal('fetch', fetcher)
    const stop = observeSachaActivity('a', () => {}, () => visible)
    await vi.advanceTimersByTimeAsync(0)
    await vi.advanceTimersByTimeAsync(1000)
    expect(fetcher).toHaveBeenCalledTimes(2)
    visible = false
    await vi.advanceTimersByTimeAsync(1000)
    expect(fetcher).toHaveBeenCalledTimes(3)
    await vi.advanceTimersByTimeAsync(4999)
    expect(fetcher).toHaveBeenCalledTimes(3)
    visible = true
    await vi.advanceTimersByTimeAsync(1)
    expect(fetcher).toHaveBeenCalledTimes(4)
    current = idle
    await vi.advanceTimersByTimeAsync(1000)
    expect(fetcher).toHaveBeenCalledTimes(5)
    await vi.advanceTimersByTimeAsync(4999)
    expect(fetcher).toHaveBeenCalledTimes(5)
    stop()
    expect(vi.getTimerCount()).toBe(0)
  })

  it('retains the last snapshot on failure, retries cold, and clears the error after recovery', async () => {
    vi.useFakeTimers()
    const current = snapshot('a')
    const fetcher = vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => current })
      .mockResolvedValueOnce({ ok: false, status: 503 })
      .mockResolvedValueOnce({ ok: true, json: async () => current })
    vi.stubGlobal('fetch', fetcher)
    const updates: ActivityObservation[] = []
    const stop = observeSachaActivity('a', value => updates.push(value), () => true)
    await vi.advanceTimersByTimeAsync(0)
    expect(updates.at(-1)).toEqual({ sessionId: 'a', snapshot: current, stale: false })
    await vi.advanceTimersByTimeAsync(5000)
    expect(updates.at(-1)).toMatchObject({ snapshot: current, stale: true })
    expect(updates.at(-1)?.error).toBeDefined()
    await vi.advanceTimersByTimeAsync(4999)
    expect(fetcher).toHaveBeenCalledTimes(2)
    await vi.advanceTimersByTimeAsync(1)
    expect(updates.at(-1)).toEqual({ sessionId: 'a', snapshot: current, stale: false })
    stop()
    expect(vi.getTimerCount()).toBe(0)
  })

  it('aborts disposed sessions and never publishes their late response into a new session', async () => {
    vi.useFakeTimers()
    let finish: (value: unknown) => void = () => {}
    const oldResponse = new Promise(resolve => { finish = resolve })
    const fetcher = vi.fn().mockReturnValueOnce(oldResponse)
      .mockResolvedValueOnce({ ok: true, json: async () => snapshot('b') })
    vi.stubGlobal('fetch', fetcher)
    const updates: ActivityObservation[] = []
    const stopOld = observeSachaActivity('a', value => updates.push(value), () => true)
    stopOld()
    expect(fetcher.mock.calls[0]?.[1].signal.aborted).toBe(true)
    const stopNew = observeSachaActivity('b', value => updates.push(value), () => true)
    finish({ ok: true, json: async () => snapshot('a') })
    await vi.advanceTimersByTimeAsync(0)
    expect(updates.map(value => value.sessionId)).toEqual(['b'])
    stopNew()
    expect(vi.getTimerCount()).toBe(0)
  })
})
