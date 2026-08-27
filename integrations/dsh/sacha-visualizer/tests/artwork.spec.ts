import { describe, expect, it } from 'vitest'
import { CONDUCTOR_CAT, MEMBER_CAT, memberCatProp } from '../src/client/artwork.ts'
import type { TeamMemberSnapshot } from '../src/types.ts'

function member(name: string, description: string): TeamMemberSnapshot {
  return { id: name, name, description, role: 'teammate', status: 'idle', diagnostics: [] }
}

describe('cat artwork mapping', () => {
  it('maps Sacha Role descriptions to distinct cat props', () => {
    expect(CONDUCTOR_CAT).toEqual({ kind: 'sacha', prop: 'conductor' })
    expect(MEMBER_CAT).toEqual({ kind: 'jojo', prop: 'none' })
    expect(memberCatProp(member('planner', 'Planner research and exploration'))).toBe('research')
    expect(memberCatProp(member('brainstormer', 'Brainstorm and clarify the approach'))).toBe('explore')
    expect(memberCatProp(member('executor', 'Executor implementation'))).toBe('engineer')
    expect(memberCatProp(member('reviewer', 'Reviewer security audit'))).toBe('security')
    expect(memberCatProp(member('manager', 'Manager coordination'))).toBe('operator')
  })

  it('keeps unknown roles on the initial fallback', () => {
    expect(memberCatProp(member('custom', 'domain specialist'))).toBeUndefined()
  })
})
