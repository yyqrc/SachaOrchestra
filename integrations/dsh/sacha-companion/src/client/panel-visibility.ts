/** Pure per-session dismissed-state persistence for the Sacha overlay panel. */

export const PANEL_DISMISSED_KEY = 'sacha-visualizer:panel-dismissed:v1'
const DISMISSED_CAP = 24

/** Parse the persisted dismissed-session list; corrupt or foreign values restore empty. */
export function parseDismissedSessions(raw: string | null): string[] {
  if (raw === null) return []
  try {
    const parsed: unknown = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed
      .filter((id): id is string => typeof id === 'string' && id.length > 0)
      .slice(-DISMISSED_CAP)
  } catch {
    return []
  }
}

/** Append one session id, deduplicating it to the tail and trimming to the cap. */
export function dismissSession(ids: readonly string[], sessionId: string): string[] {
  const next = ids.filter(id => id !== sessionId)
  next.push(sessionId)
  return next.slice(-DISMISSED_CAP)
}
