import { describe, expect, it } from 'vitest'
import { ACTION_ART, LEAD_ART, memberArtUrl } from '../src/client/artwork.ts'
import type { TeamMemberSnapshot } from '../src/types.ts'

function member(name: string, description: string): TeamMemberSnapshot {
  return { id: name, name, description, role: 'teammate', status: 'idle', diagnostics: [] }
}

describe('whale artwork mapping', () => {
  it('maps Sacha Role descriptions to distinct packaged illustrations', () => {
    expect(LEAD_ART).toMatch(/team-lead-v2\.png$/u)
    expect(memberArtUrl(member('planner', 'Planner research and exploration'))).toMatch(/member-researcher-v2\.png$/u)
    expect(memberArtUrl(member('executor', 'Executor implementation'))).toMatch(/member-engineer-v2\.png$/u)
    expect(memberArtUrl(member('reviewer', 'Reviewer security audit'))).toMatch(/member-security-v2\.png$/u)
    expect(memberArtUrl(member('manager', 'Manager coordination'))).toMatch(/member-operator-v2\.png$/u)
  })

  it('keeps unknown roles on the initial fallback and maps every runtime status action', () => {
    expect(memberArtUrl(member('custom', 'domain specialist'))).toBeNull()
    expect(Object.keys(ACTION_ART).sort()).toEqual(['failed', 'idle', 'inactive', 'provisioning', 'running'])
    expect(ACTION_ART.running).toMatch(/action-working-v2\.png$/u)
  })
})

