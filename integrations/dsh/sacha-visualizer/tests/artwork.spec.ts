import { describe, expect, it } from 'vitest'
import { CONDUCTOR_CAT, MEMBER_CAT, subagentCatProp } from '../src/client/artwork.ts'
import type { SubagentSnapshot } from '../src/types.ts'

function child(label: string): SubagentSnapshot {
  return { id: label, label, status: 'idle', hasChildren: false }
}

describe('cat artwork mapping', () => {
  it('maps child labels to display-only cat props', () => {
    expect(CONDUCTOR_CAT).toEqual({ kind: 'sacha', prop: 'conductor' })
    expect(MEMBER_CAT).toEqual({ kind: 'jojo', prop: 'none' })
    expect(subagentCatProp(child('Planner research and exploration'))).toBe('research')
    expect(subagentCatProp(child('Brainstorm and clarify the approach'))).toBe('explore')
    expect(subagentCatProp(child('Executor implementation'))).toBe('engineer')
    expect(subagentCatProp(child('Reviewer security audit'))).toBe('security')
  })

  it('keeps unknown labels on the plain child cat', () => {
    expect(subagentCatProp(child('domain specialist'))).toBeUndefined()
  })
})
