import { describe, expect, it } from 'vitest'
import { managerGraphLayout } from '../src/client/manager-graph.ts'
import type { ManagerUnitSnapshot } from '../src/types.ts'

function unit(id: string, blockedBy: string[]): ManagerUnitSnapshot {
  return { id, label: id, state: blockedBy.length === 0 ? 'ready' : 'waiting', blockedBy }
}

describe('managerGraphLayout', () => {
  it('places dependencies before downstream units and renders every edge', () => {
    const units = [
      unit('a', []),
      unit('b', []),
      unit('review', ['b']),
      unit('closeout', ['a', 'review']),
    ]
    const layout = managerGraphLayout(units)
    const x = new Map(layout.nodes.map(node => [node.unit.id, node.x]))
    expect(x.get('a')).toBeLessThan(x.get('closeout') ?? 0)
    expect(x.get('b')).toBeLessThan(x.get('review') ?? 0)
    expect(x.get('review')).toBeLessThan(x.get('closeout') ?? 0)
    expect(layout.edges).toHaveLength(3)
  })
})
