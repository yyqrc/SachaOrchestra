/** Pure compact DAG layout for committed Sacha Manager unit snapshots. */

import type { ManagerUnitSnapshot } from '../types.ts'

export const MANAGER_NODE_WIDTH = 132
export const MANAGER_NODE_HEIGHT = 50
const COLUMN_GAP = 34
const ROW_GAP = 12

export interface ManagerGraphNode {
  readonly unit: ManagerUnitSnapshot
  readonly x: number
  readonly y: number
}

export interface ManagerGraphEdge {
  readonly from: string
  readonly to: string
  readonly path: string
}

export interface ManagerGraphLayout {
  readonly width: number
  readonly height: number
  readonly nodes: readonly ManagerGraphNode[]
  readonly edges: readonly ManagerGraphEdge[]
}

function depths(units: readonly ManagerUnitSnapshot[]): Map<string, number> {
  const byId = new Map(units.map(unit => [unit.id, unit]))
  const memo = new Map<string, number>()
  const depthOf = (id: string): number => {
    const cached = memo.get(id)
    if (cached !== undefined) return cached
    const unit = byId.get(id)
    const depth = unit === undefined || unit.blockedBy.length === 0
      ? 0
      : 1 + Math.max(...unit.blockedBy.map(depthOf))
    memo.set(id, depth)
    return depth
  }
  for (const unit of units) depthOf(unit.id)
  return memo
}

export function managerGraphLayout(units: readonly ManagerUnitSnapshot[]): ManagerGraphLayout {
  if (units.length === 0) return { width: 0, height: 0, nodes: [], edges: [] }
  const unitDepths = depths(units)
  const columns = new Map<number, ManagerUnitSnapshot[]>()
  for (const unit of units) {
    const depth = unitDepths.get(unit.id) ?? 0
    const values = columns.get(depth) ?? []
    values.push(unit)
    columns.set(depth, values)
  }
  const ordered = [...columns.entries()].sort(([left], [right]) => left - right)
  const positions = new Map<string, { x: number; y: number }>()
  const nodes: ManagerGraphNode[] = []
  for (const [column, [, values]] of ordered.entries()) {
    values.sort((left, right) => left.id.localeCompare(right.id, 'en', { numeric: true }))
    for (const [row, unit] of values.entries()) {
      const x = column * (MANAGER_NODE_WIDTH + COLUMN_GAP)
      const y = row * (MANAGER_NODE_HEIGHT + ROW_GAP)
      positions.set(unit.id, { x, y })
      nodes.push({ unit, x, y })
    }
  }
  const edges: ManagerGraphEdge[] = []
  for (const unit of units) {
    const target = positions.get(unit.id)
    if (target === undefined) continue
    for (const dependency of unit.blockedBy) {
      const source = positions.get(dependency)
      if (source === undefined) continue
      const x1 = source.x + MANAGER_NODE_WIDTH
      const y1 = source.y + MANAGER_NODE_HEIGHT / 2
      const x2 = target.x
      const y2 = target.y + MANAGER_NODE_HEIGHT / 2
      edges.push({
        from: dependency,
        to: unit.id,
        path: `M${x1} ${y1}C${x1 + 18} ${y1},${x2 - 18} ${y2},${x2} ${y2}`,
      })
    }
  }
  const rows = Math.max(...ordered.map(([, values]) => values.length))
  return {
    width: ordered.length * MANAGER_NODE_WIDTH + Math.max(0, ordered.length - 1) * COLUMN_GAP,
    height: rows * MANAGER_NODE_HEIGHT + Math.max(0, rows - 1) * ROW_GAP,
    nodes,
    edges,
  }
}
