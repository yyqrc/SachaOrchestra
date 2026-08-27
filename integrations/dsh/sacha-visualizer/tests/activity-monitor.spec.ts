import { describe, expect, it } from 'vitest'
import { selectSessionSnapshot } from '../src/client/activity-monitor.ts'
import type { SachaActivitySnapshot } from '../src/types.ts'

function snapshot(sessionId: string): SachaActivitySnapshot {
  return {
    available: true,
    sessionId,
    events: [],
    state: { gates: {}, waves: [], evidence: {} },
    team: { available: false, members: [], tasks: [] },
    warnings: [],
  }
}

describe('session-scoped activity snapshots', () => {
  it('hides an older session snapshot until the requested session arrives', () => {
    const previous = snapshot('session-a')
    expect(selectSessionSnapshot(previous, 'session-b')).toBeUndefined()
    expect(selectSessionSnapshot(previous, undefined)).toBeUndefined()
    expect(selectSessionSnapshot(previous, 'session-a')).toBe(previous)
  })
})
