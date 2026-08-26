import { describe, expect, it } from 'vitest'
import { compactDagLayout, relatedTaskIds } from '../src/client/activity-model.ts'
import type { TeamTaskSnapshot } from '../src/types.ts'

function task(id: string, blockedBy: string[]): TeamTaskSnapshot {
  return {
    id,
    revision: 1,
    subject: id,
    description: id,
    status: 'pending',
    blockedBy,
    writeScopes: [],
    ready: blockedBy.length === 0,
    writeScopeWarnings: [],
  }
}

describe('compact DAG', () => {
  const tasks = [task('task-1', []), task('task-2', ['task-1']), task('task-3', ['task-1']), task('task-4', ['task-2', 'task-3'])]

  it('places dependency stages from left to right and emits every edge', () => {
    const layout = compactDagLayout(tasks)
    const positions = new Map(layout.nodes.map(node => [node.task.id, node.x]))
    expect(positions.get('task-1')).toBeLessThan(positions.get('task-2') ?? 0)
    expect(positions.get('task-2')).toBeLessThan(positions.get('task-4') ?? 0)
    expect(layout.edges).toHaveLength(4)
  })

  it('highlights the complete upstream and downstream chain', () => {
    expect([...relatedTaskIds('task-2', tasks)].sort()).toEqual(['task-1', 'task-2', 'task-4'])
  })
})

