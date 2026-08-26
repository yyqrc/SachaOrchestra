/** Pure compact DAG layout for official DSH Agent Teams tasks. */

import type { TeamTaskSnapshot } from '../types.ts'

export const NODE_WIDTH = 108
export const NODE_HEIGHT = 38
const COLUMN_GAP = 30
const ROW_GAP = 10

export interface DagNode {
  readonly task: TeamTaskSnapshot
  readonly x: number
  readonly y: number
}

export interface DagEdge {
  readonly from: string
  readonly to: string
  readonly path: string
}

export interface DagLayout {
  readonly width: number
  readonly height: number
  readonly nodes: readonly DagNode[]
  readonly edges: readonly DagEdge[]
}

function taskDepths(tasks: readonly TeamTaskSnapshot[]): Map<string, number> {
  const byId = new Map(tasks.map(task => [task.id, task]))
  const memo = new Map<string, number>()
  const visiting = new Set<string>()
  const depthOf = (id: string): number => {
    const cached = memo.get(id)
    if (cached !== undefined) return cached
    if (visiting.has(id)) return 0
    visiting.add(id)
    const task = byId.get(id)
    const depth = task === undefined || task.blockedBy.length === 0
      ? 0
      : 1 + Math.max(0, ...task.blockedBy.map(depthOf))
    visiting.delete(id)
    memo.set(id, depth)
    return depth
  }
  for (const task of tasks) depthOf(task.id)
  return memo
}

/** Place tasks in dependency-depth columns and stable id rows. */
export function compactDagLayout(tasks: readonly TeamTaskSnapshot[]): DagLayout {
  const depths = taskDepths(tasks)
  const stages = new Map<number, TeamTaskSnapshot[]>()
  for (const task of tasks) {
    const depth = depths.get(task.id) ?? 0
    const rows = stages.get(depth) ?? []
    rows.push(task)
    stages.set(depth, rows)
  }
  const ordered = [...stages.entries()].sort(([left], [right]) => left - right)
    .map(([depth, rows]) => ({ depth, rows: rows.sort((left, right) => left.id.localeCompare(right.id, 'en', { numeric: true })) }))
  const positions = new Map<string, { x: number; y: number }>()
  const nodes: DagNode[] = []
  for (const [column, stage] of ordered.entries()) {
    for (const [row, task] of stage.rows.entries()) {
      const x = column * (NODE_WIDTH + COLUMN_GAP)
      const y = row * (NODE_HEIGHT + ROW_GAP)
      positions.set(task.id, { x, y })
      nodes.push({ task, x, y })
    }
  }
  const edges: DagEdge[] = []
  for (const task of tasks) {
    const target = positions.get(task.id)
    if (target === undefined) continue
    for (const dependency of task.blockedBy) {
      const source = positions.get(dependency)
      if (source === undefined) continue
      const x1 = source.x + NODE_WIDTH
      const y1 = source.y + NODE_HEIGHT / 2
      const x2 = target.x
      const y2 = target.y + NODE_HEIGHT / 2
      edges.push({
        from: dependency,
        to: task.id,
        path: `M${x1} ${y1}C${x1 + 16} ${y1},${x2 - 16} ${y2},${x2} ${y2}`,
      })
    }
  }
  const rows = Math.max(1, ...ordered.map(stage => stage.rows.length))
  return {
    width: ordered.length === 0 ? 0 : ordered.length * NODE_WIDTH + (ordered.length - 1) * COLUMN_GAP,
    height: ordered.length === 0 ? 0 : rows * NODE_HEIGHT + (rows - 1) * ROW_GAP,
    nodes,
    edges,
  }
}

/** Return complete upstream/downstream relationships around one task. */
export function relatedTaskIds(taskId: string, tasks: readonly TeamTaskSnapshot[]): ReadonlySet<string> {
  const byId = new Map(tasks.map(task => [task.id, task]))
  const downstream = new Map<string, string[]>()
  for (const task of tasks) {
    for (const dependency of task.blockedBy) {
      const values = downstream.get(dependency) ?? []
      values.push(task.id)
      downstream.set(dependency, values)
    }
  }
  const result = new Set<string>()
  const upstreamSeen = new Set<string>()
  const visitUp = (id: string): void => {
    if (upstreamSeen.has(id)) return
    upstreamSeen.add(id)
    result.add(id)
    for (const dependency of byId.get(id)?.blockedBy ?? []) visitUp(dependency)
  }
  const downSeen = new Set<string>()
  const visitDown = (id: string): void => {
    if (downSeen.has(id)) return
    downSeen.add(id)
    result.add(id)
    for (const child of downstream.get(id) ?? []) visitDown(child)
  }
  visitUp(taskId)
  visitDown(taskId)
  return result
}

