/** Demand-scoped polling of the Sacha state route for the current DSH session. */

import { useEffect, useState } from 'react'
import type { SachaActivitySnapshot } from '../types.ts'

const HOT_POLL_MS = 1000
const COLD_POLL_MS = 5000

/** Orchestration presence: committed Sacha events, dispatched teammates, or
 *  shared tasks. A lone lead member is ambient Team state, not orchestration,
 *  so it neither warms the poll cadence nor triggers any activity UI. */
function active(snapshot: SachaActivitySnapshot): boolean {
  return snapshot.events.length > 0
    || snapshot.team.members.some(m => m.role === 'teammate')
    || snapshot.team.tasks.length > 0
}

/** Keep render state bound to the requested session while effects replace an older snapshot. */
export function selectSessionSnapshot(
  snapshot: SachaActivitySnapshot | undefined,
  sessionId: string | undefined,
): SachaActivitySnapshot | undefined {
  return snapshot?.sessionId === sessionId ? snapshot : undefined
}

/** Poll only while a concrete current session exists. */
export function useSachaActivity(sessionId: string | undefined): SachaActivitySnapshot | undefined {
  const [snapshot, setSnapshot] = useState<SachaActivitySnapshot>()
  useEffect(() => {
    setSnapshot(undefined)
    if (sessionId === undefined) return
    let stopped = false
    let timer: ReturnType<typeof setTimeout> | undefined
    let controller: AbortController | undefined
    const tick = async (): Promise<void> => {
      controller = new AbortController()
      let nextDelay = COLD_POLL_MS
      try {
        const response = await fetch(`/plugins/sacha-visualizer/state?sessionId=${encodeURIComponent(sessionId)}`, {
          cache: 'no-store',
          signal: controller.signal,
        })
        if (response.ok) {
          const next = await response.json() as SachaActivitySnapshot
          if (!stopped) setSnapshot(next)
          if (active(next)) nextDelay = HOT_POLL_MS
        }
      } catch {
        // A route may appear after the optional Web service binds; the next cold probe retries.
      }
      if (!stopped) timer = setTimeout(() => { void tick() }, nextDelay)
    }
    void tick()
    return () => {
      stopped = true
      if (timer !== undefined) clearTimeout(timer)
      controller?.abort()
    }
  }, [sessionId])
  return selectSessionSnapshot(snapshot, sessionId)
}

