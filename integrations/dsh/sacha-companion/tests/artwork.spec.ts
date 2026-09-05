import { describe, expect, it } from 'vitest'
import { subagentCatProp } from '../src/client/artwork.ts'
import type { SubagentSnapshot } from '../src/types.ts'

function child(label: string): SubagentSnapshot {
  return { id: label, label, status: 'idle', hasChildren: false }
}

describe('cat artwork mapping', () => {
  it('maps child labels to display-only cat props', () => {
    expect(subagentCatProp(child('Planner research and exploration'))).toBe('research')
  })

  it('keeps unknown labels on the plain child cat', () => {
    expect(subagentCatProp(child('domain specialist'))).toBeUndefined()
  })
})
