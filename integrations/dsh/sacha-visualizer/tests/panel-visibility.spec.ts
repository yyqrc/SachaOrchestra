import { describe, expect, it } from 'vitest'
import { dismissSession, parseDismissedSessions } from '../src/client/panel-visibility.ts'

describe('panel dismissed-session persistence', () => {
  it('parses a valid list and tolerates corrupt input', () => {
    expect(parseDismissedSessions(null)).toEqual([])
    expect(parseDismissedSessions('not-json')).toEqual([])
    expect(parseDismissedSessions('{"a":1}')).toEqual([])
    expect(parseDismissedSessions('[1, "s1", null, "s2"]')).toEqual(['s1', 's2'])
  })

  it('appends a session id deduplicated to the tail', () => {
    expect(dismissSession([], 's1')).toEqual(['s1'])
    expect(dismissSession(['s1', 's2'], 's1')).toEqual(['s2', 's1'])
    expect(dismissSession(['s1', 's2'], 's3')).toEqual(['s1', 's2', 's3'])
  })

  it('trims the list to the persistence cap', () => {
    const ids = Array.from({ length: 30 }, (_, index) => `s${index}`)
    const next = dismissSession(ids, 's-new')
    expect(next.length).toBeLessThanOrEqual(24)
    expect(next[next.length - 1]).toBe('s-new')
  })
})
