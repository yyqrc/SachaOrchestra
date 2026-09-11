import { describe, expect, it } from 'vitest'
import { groupTools, phaseSummary } from '../src/client/tool-surface-view.ts'
import type { ToolSurfaceSnapshot } from '../src/types.ts'

function surface(overrides: Partial<ToolSurfaceSnapshot> = {}): ToolSurfaceSnapshot {
  return {
    sessionId: 's1',
    phase: 'resident',
    visibleCount: 3,
    hiddenCount: 1,
    visible: ['read', 'grep', 'pwsh'],
    hidden: ['workflow'],
    advertised: ['read'],
    unlocked: [],
    toolFamilies: { read: 'filesystem-read', grep: 'filesystem-read', pwsh: 'shell', workflow: 'other' },
    source: 'runtime',
    fallback: false,
    warnings: [],
    ...overrides,
  }
}

describe('reader-facing tool surface grouping', () => {
  it('groups names into family sections in presentation order', () => {
    const groups = groupTools(surface(), ['pwsh', 'read', 'grep'])
    expect(groups.map(group => group.key)).toEqual(['filesystem-read', 'shell'])
    expect(groups[0]?.label).toBe('读取文件')
    expect(groups[0]?.tools.map(tool => tool.name)).toEqual(['read', 'grep'])
    expect(groups[1]?.tools.map(tool => tool.name)).toEqual(['pwsh'])
  })

  it('labels known tools in Chinese while keeping the identifier', () => {
    const groups = groupTools(surface(), ['read', 'pwsh'])
    const read = groups.flatMap(group => group.tools).find(tool => tool.name === 'read')
    expect(read?.label).toBe('读取文件')
  })

  it('keeps an unknown tool visible under 其他工具 instead of dropping it', () => {
    const groups = groupTools(surface({ toolFamilies: {} }), ['some_new_plugin_tool'])
    expect(groups).toHaveLength(1)
    expect(groups[0]?.key).toBe('other')
    expect(groups[0]?.tools[0]).toMatchObject({ name: 'some_new_plugin_tool', unlocked: false })
    expect(groups[0]?.tools[0]?.label).toBeUndefined()
  })

  it('marks temporary unlocks so a reader can tell them from the phase default', () => {
    const groups = groupTools(surface({ unlocked: ['pwsh'] }), ['read', 'pwsh'])
    const tools = groups.flatMap(group => group.tools)
    expect(tools.find(tool => tool.name === 'pwsh')?.unlocked).toBe(true)
    expect(tools.find(tool => tool.name === 'read')?.unlocked).toBe(false)
  })

  it('omits families with no members', () => {
    const groups = groupTools(surface(), ['read'])
    expect(groups.map(group => group.key)).toEqual(['filesystem-read'])
  })

  it('states the phase as a consequence rather than an internal name', () => {
    expect(phaseSummary(surface({ phase: 'bootstrap' }))).toContain('查看')
    expect(phaseSummary(surface({ phase: 'resident' }))).toContain('工作')
    for (const summary of [phaseSummary(surface({ phase: 'bootstrap' })), phaseSummary(surface({ phase: 'resident' }))]) {
      expect(summary).not.toContain('bootstrap')
      expect(summary).not.toContain('resident')
    }
  })
})
