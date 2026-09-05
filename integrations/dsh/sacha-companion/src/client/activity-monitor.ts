/** Demand-scoped polling of the Sacha state route for the current DSH session. */

import { useEffect, useRef, useState } from 'react'
import type { SachaActivitySnapshot } from '../types.ts'

const HOT_POLL_MS = 1000
const COLD_POLL_MS = 5000

export interface ActivityObservation {
  readonly sessionId: string
  readonly snapshot?: SachaActivitySnapshot
  readonly stale: boolean
  readonly error?: string
}

/** 历史记录的存在不代表仍有工作进行。 */
export function activityPollDelay(snapshot: SachaActivitySnapshot | undefined, visible: boolean): number {
  if (!visible || snapshot === undefined) return COLD_POLL_MS
  if (snapshot.subagents.children.some(child => child.status === 'running')) return HOT_POLL_MS
  const phase = snapshot.state.phase
  if (phase !== undefined) {
    return phase.state === 'entered' && phase.phase !== 'complete' && phase.phase !== 'blocked'
      ? HOT_POLL_MS : COLD_POLL_MS
  }
  return snapshot.state.waves.some(wave => wave.state === 'dispatched'
    && wave.units.some(unit => unit.state === 'running')) ? HOT_POLL_MS : COLD_POLL_MS
}

/** Keep render state bound to the requested session while effects replace an older snapshot. */
export function selectSessionSnapshot(
  snapshot: SachaActivitySnapshot | undefined,
  sessionId: string | undefined,
): SachaActivitySnapshot | undefined {
  return snapshot?.sessionId === sessionId ? snapshot : undefined
}

/** 单个会话的请求、计时器与最后快照拥有同一生命周期。 */
export function observeSachaActivity(
  sessionId: string,
  publish: (observation: ActivityObservation) => void,
  visible: () => boolean,
): () => void {
  let stopped = false
  let timer: ReturnType<typeof setTimeout> | undefined
  let controller: AbortController | undefined
  let snapshot: SachaActivitySnapshot | undefined
  const tick = async (): Promise<void> => {
    controller = new AbortController()
    let nextDelay = COLD_POLL_MS
    try {
      const response = await fetch(`/plugins/sacha-visualizer/state?sessionId=${encodeURIComponent(sessionId)}`, {
        cache: 'no-store', signal: controller.signal,
      })
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const next = await response.json() as SachaActivitySnapshot
      if (next.sessionId !== sessionId || !next.available) throw new Error('Session state unavailable')
      if (stopped) return
      snapshot = next
      publish({ sessionId, snapshot, stale: false })
      nextDelay = activityPollDelay(snapshot, visible())
    } catch (error: unknown) {
      if (stopped) return
      publish({ sessionId, ...(snapshot === undefined ? {} : { snapshot }), stale: true, error: String(error) })
    }
    if (!stopped) timer = setTimeout(() => { void tick() }, nextDelay)
  }
  void tick()
  return () => {
    stopped = true
    if (timer !== undefined) clearTimeout(timer)
    controller?.abort()
  }
}

export function useSachaActivity(sessionId: string | undefined, panelVisible: boolean): ActivityObservation | undefined {
  const [observation, setObservation] = useState<ActivityObservation>()
  const visible = useRef(panelVisible)
  visible.current = panelVisible
  useEffect(() => {
    setObservation(undefined)
    if (sessionId === undefined) return
    return observeSachaActivity(sessionId, setObservation,
      () => visible.current && document.visibilityState === 'visible')
  }, [sessionId])
  return observation?.sessionId === sessionId ? observation : undefined
}
