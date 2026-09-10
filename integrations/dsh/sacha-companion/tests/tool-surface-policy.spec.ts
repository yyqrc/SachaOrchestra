import { describe, expect, it } from 'vitest'
import { Context } from '@deepseek-ai/cordis'
import type { Agent } from '@deepseek-ai/dsh-agent'
import { bindScopeParent, createScope, type Scope } from '@deepseek-ai/dsh-scope'
import type { SessionId } from '@deepseek-ai/dsh-session'
import SystemPrompt from '@deepseek-ai/dsh-system-prompt'
import ToolRuntime from '@deepseek-ai/dsh-tools'
import {
  NewFirstPolicySlot,
  RootToolSurfaceController,
  captureToolScope,
  createToolCatalog,
  filterPromptAssembly,
  foldToolSurfaceState,
  isLiveRootAgent,
  mergeToolCatalog,
  phaseAllowsTool,
  phaseFromEvents,
  searchToolCatalog,
  suppressInheritedControlTool,
  toolHelp,
  type ToolCatalogSnapshot,
  type ToolSurfaceRecovery,
} from '../src/tool-surface-policy.ts'

function schema(name: string, description = `${name} description`, propertyCount = 0) {
  return {
    name,
    description,
    parameters: {
      type: 'object',
      required: propertyCount > 0 ? ['p0'] : [],
      properties: Object.fromEntries(Array.from({ length: propertyCount }, (_, index) => [
        `p${index}`,
        { type: 'string', description: `parameter ${index}` },
      ])),
    },
  }
}

function runtimeTool(name: string) {
  return {
    name,
    description: `${name} description`,
    parameters: { type: 'object' as const, properties: {} },
    output: {
      schema: { type: 'string' as const },
      render: (_args: unknown, value: string) => [{ type: 'text' as const, text: value }],
    },
    execute: () => Promise.resolve(name),
  }
}

const catalog = createToolCatalog([
  schema('read'), schema('grep'), schema('write'), schema('pwsh'), schema('job_output'),
  schema('sacha_research'), schema('sacha_worker'), schema('sacha_review'), schema('mcp_unity'),
])

function user(seq: number, text: string) {
  return {
    type: 'user/message', seq, time: seq,
    data: { id: `u${seq}`, role: 'user', source: { kind: 'user' }, content: [{ type: 'text', text }] },
  }
}

function call(seq: number, callId: string, args: object) {
  return {
    type: 'tool/call', seq, time: seq,
    data: { callId, name: 'sacha_tools', arguments: JSON.stringify(args), turn: 1, step: 1 },
  }
}

function result(seq: number, callId: string, isError = false, payload?: object) {
  return {
    type: 'tool/result', seq, time: seq,
    data: {
      message: {
        source: { kind: 'tool', callId },
        content: [{
          type: 'tool-result', toolCallId: callId,
          content: payload === undefined ? [] : [{ type: 'text', text: JSON.stringify(payload) }],
          isError,
        }],
      },
      ...(isError ? { error: { name: 'Error', code: 'FAILED' } } : {}),
    },
  }
}

function header(seq: number, names: string[]) {
  return {
    type: 'request/header', seq, time: seq,
    data: { header: { config: { provider: 'test', model: 'test' }, tools: names.map(name => schema(name)) }, reason: 'initial' },
  }
}

function recovery(overrides: Partial<ToolSurfaceRecovery> = {}): ToolSurfaceRecovery {
  return {
    phase: 'bootstrap', unlocked: [], advertised: ['read', 'grep', 'sacha_research', 'sacha_tools'],
    source: 'bootstrap', explicitPhase: false, warnings: [], ...overrides,
  }
}

function controllerWithLog(
  initial = recovery(),
  sourceCatalog: ToolCatalogSnapshot = catalog,
) {
  const log: string[] = []
  const slot = new NewFirstPolicySlot()
  const controller = new RootToolSurfaceController('root-1', sourceCatalog, initial, (allowed) => {
    const label = [...allowed].sort().join(',')
    const registration = {
      allowed,
      dispose() { log.push(`dispose:${label}`) },
    }
    log.push(`install:${label}`)
    slot.replace(() => registration)
  })
  controller.activate()
  return { controller, log, slot }
}

describe('durable phase derivation and phase allow lists', () => {
  it('derives promotion from Runtime signals and never from human wording', () => {
    // Human wording alone never promotes: an unrecognised or ambiguous task
    // must not be able to strand the session, and it must not promote either.
    expect(phaseFromEvents([user(1, '修复构建脚本并运行测试')])).toBe('bootstrap')
    expect(phaseFromEvents([user(1, '继续')])).toBe('bootstrap')
    expect(phaseFromEvents([user(1, '读一下上下文 然后继续')])).toBe('bootstrap')
    // The Runtime's own first durable signal promotes, whichever arrives first.
    expect(phaseFromEvents([{ type: 'assistant/message' }])).toBe('resident')
    expect(phaseFromEvents([{ type: 'tool/call' }])).toBe('resident')
    expect(phaseFromEvents([{ type: 'step/start' }, { type: 'assistant/message' }])).toBe('resident')
    // Once promoted, the phase never falls back on later events.
    expect(phaseFromEvents([{ type: 'assistant/message' }, { type: 'step/end' }])).toBe('resident')
  })

  it('never promotes on this companion\'s own control calls', () => {
    // `sacha_tools` is always visible, so a bare status query or a single-tool
    // unlock must not be mistaken for the model starting real work.
    const control = (seq: number, id: string, args: object) => ({
      type: 'tool/call', seq, time: seq,
      data: { callId: id, name: 'sacha_tools', arguments: JSON.stringify(args), turn: 1, step: 1 },
    })
    expect(phaseFromEvents([control(1, 'c1', { action: 'status' })])).toBe('bootstrap')
    expect(phaseFromEvents([control(1, 'c1', { action: 'unlock', tools: ['mcp_unity'] })])).toBe('bootstrap')
    expect(phaseFromEvents([control(1, 'c1', { action: 'phase', phase: 'bootstrap' })])).toBe('bootstrap')
    // Any other tool call is real work and does promote.
    expect(phaseFromEvents([{
      type: 'tool/call', seq: 1, time: 1, data: { name: 'read', callId: 'r1', arguments: '{}' },
    }])).toBe('resident')
  })

  it('keeps a promoted session promoted across context compaction', () => {
    // Compaction appends a shadowing user/message but keeps the original
    // events in the durable log, so promotion survives it.
    const events = [
      { type: 'assistant/message' },
      { type: 'compaction/start' },
      { type: 'compaction/summary' },
      { type: 'compaction/end' },
      user(9, '继续'),
    ]
    expect(phaseFromEvents(events)).toBe('resident')
  })

  it('keeps MCP, Agent Teams, ordinary subagent/workflow hidden in both phases', () => {
    expect(phaseAllowsTool('bootstrap', 'read')).toBe(true)
    expect(phaseAllowsTool('bootstrap', 'grep')).toBe(true)
    // The bootstrap phase is deliberately read-only.
    expect(phaseAllowsTool('bootstrap', 'write')).toBe(false)
    expect(phaseAllowsTool('bootstrap', 'pwsh')).toBe(false)
    expect(phaseAllowsTool('bootstrap', 'sacha_research')).toBe(false)
    // The resident phase exposes the working set including all three surfaces.
    expect(phaseAllowsTool('resident', 'write')).toBe(true)
    expect(phaseAllowsTool('resident', 'pwsh')).toBe(true)
    expect(phaseAllowsTool('resident', 'sacha_research')).toBe(true)
    expect(phaseAllowsTool('resident', 'sacha_worker')).toBe(true)
    expect(phaseAllowsTool('resident', 'sacha_review')).toBe(true)
    for (const name of ['mcp_unity', 'spawn_teammate', 'subagent', 'workflow']) {
      expect(phaseAllowsTool('resident', name)).toBe(false)
    }
  })

  it('excludes native subagent descriptors even when a continuation is a registry root', () => {
    const root = { id: 'same' }
    const impostor = { id: 'same', session: { header: {} } }
    expect(isLiveRootAgent(root, [root])).toBe(true)
    expect(isLiveRootAgent(impostor, [root])).toBe(false)
    expect(isLiveRootAgent(root, [root], [{ type: 'subagent/descriptor' }])).toBe(false)
  })
})

describe('hidden catalog discovery', () => {
  it('matches any term of a natural multi-word query', () => {
    // The old whole-string match returned nothing for these, which is how a
    // session failed to discover the delegation surfaces.
    const hidden = createToolCatalog([
      schema('sacha_worker', 'Scoped implementation subagent for one work unit.'),
      schema('mcp_unity', 'Unity editor bridge and console access.'),
      schema('job_output', 'Read output from a background job.'),
    ])
    expect(searchToolCatalog(hidden, 'unity editor bridge').items.map(item => item.name)).toEqual(['mcp_unity'])
    expect(searchToolCatalog(hidden, 'worker subagent').items.map(item => item.name)).toEqual(['sacha_worker'])
    expect(searchToolCatalog(hidden, 'background job').items.map(item => item.name)).toEqual(['job_output'])
    // A single term keeps the original substring behaviour.
    expect(searchToolCatalog(hidden, 'sacha').items.map(item => item.name)).toEqual(['sacha_worker'])
    // An unmatched query still returns nothing.
    expect(searchToolCatalog(hidden, 'nonexistent thing').items).toEqual([])
  })
})

describe('rc.2 inherited and exact-scope split', () => {
  it('uses an empty inherited allow probe without losing exact-scope tools', async () => {
    const ctx = new Context()
    await ctx.plugin(SystemPrompt, {})
    await ctx.plugin(ToolRuntime)
    const agent = { id: 'root-probe' as SessionId } as Agent
    let scope!: Scope
    await ctx.plugin(Object.assign((inner: Context) => {
      scope = createScope(inner, agent)
      Object.assign(agent, { ctx: scope.ctx })
    }, { inject: ['tools', 'systemPrompt'] }))
    ctx.tools.register(runtimeTool('read'))
    scope.ctx.tools.register(runtimeTool('wait_agent'))

    const captured = captureToolScope(agent)
    expect(captured.catalog.entries.map(entry => entry.name)).toEqual(['read', 'wait_agent'])
    expect([...captured.inheritedNames]).toEqual(['read'])

    ctx.tools.register(runtimeTool('mcp_late'))
    const refreshed = mergeToolCatalog(captured.catalog, ctx.tools.schemas())
    expect(refreshed.entries.map(entry => entry.name)).toEqual(['mcp_late', 'read', 'wait_agent'])

    const lift = scope.ctx.tools.restrict({ allow: [...captured.inheritedNames] })
    expect(ctx.tools.schemas(agent).map(tool => tool.name).sort()).toEqual(['read', 'wait_agent'])
    lift()
    await scope.dispose()
  })

  it('removes the Root control tool from a child without changing the Root', async () => {
    const ctx = new Context()
    await ctx.plugin(SystemPrompt, {})
    await ctx.plugin(ToolRuntime)
    const rootAgent = { id: 'root-control' as SessionId } as Agent
    const childAgent = { id: 'child-control' as SessionId } as Agent
    let rootScope!: Scope
    let childScope!: Scope
    await ctx.plugin(Object.assign((inner: Context) => {
      rootScope = createScope(inner, rootAgent)
      Object.assign(rootAgent, { ctx: rootScope.ctx })
    }, { inject: ['tools', 'systemPrompt'] }))
    bindScopeParent(childAgent, rootAgent)
    await ctx.plugin(Object.assign((inner: Context) => {
      childScope = createScope(inner, childAgent)
      Object.assign(childAgent, { ctx: childScope.ctx })
    }, { inject: ['tools', 'systemPrompt'] }))
    rootScope.ctx.tools.register(runtimeTool('sacha_tools'))
    expect(ctx.tools.schemas(childAgent).map(tool => tool.name)).toEqual(['sacha_tools'])

    const lift = suppressInheritedControlTool(childAgent)
    expect(ctx.tools.schemas(childAgent)).toEqual([])
    expect(ctx.tools.schemas(rootAgent).map(tool => tool.name)).toEqual(['sacha_tools'])
    lift?.()
    await childScope.dispose()
    await rootScope.dispose()
  })
})

describe('catalog metadata bounds', () => {
  it('bounds descriptions, parameter metadata, result count, and help payload', () => {
    const large = createToolCatalog(Array.from({ length: 300 }, (_, index) =>
      schema(`tool_${String(index).padStart(3, '0')}`, 'x'.repeat(400), 40)))
    expect(large.entries).toHaveLength(300)
    expect(large.truncated).toBe(false)
    expect(large.entries[0]?.description.length).toBe(240)
    expect(large.entries[0]?.parameters).toHaveLength(32)
    expect(large.entries[0]?.parametersTruncated).toBe(true)
    const page = searchToolCatalog(large, 'tool', 999)
    expect(page.items).toHaveLength(24)
    expect(page.truncated).toBe(true)
    expect(() => searchToolCatalog(large, 'q'.repeat(97))).toThrow()
    const merged = mergeToolCatalog(large, [schema('tool_300')])
    expect(merged.entries).toHaveLength(301)
    const { controller } = controllerWithLog(recovery(), merged)
    expect(controller.help('tool_299')).toMatchObject({ name: 'tool_299', parametersTruncated: true })
    expect(controller.unlock(['tool_299', 'tool_300']).unlocked).toEqual(['tool_299', 'tool_300'])
    expect(toolHelp(large, 'missing')).toBeUndefined()
  })
})

describe('durable recovery fold', () => {
  it('promotes from durable signals and ignores old controls that finish later', () => {
    const events = [
      user(0, '只读调查'),
      call(1, 'old', { action: 'unlock', tools: ['mcp_unity'] }),
      user(2, '实现当前功能'),
      { type: 'assistant/message', seq: 3, time: 3, data: {} },
      result(4, 'old', false, { action: 'unlock', unlocked: ['mcp_unity'] }),
      user(5, '继续'),
    ]
    // Promotion comes from the durable signal; the human turns contribute nothing.
    // `source` reports the last state-affecting control, which here is the unlock.
    expect(foldToolSurfaceState(events, catalog)).toMatchObject({ phase: 'resident', source: 'control' })
    events.push(call(6, 'current', { action: 'unlock', tools: ['mcp_unity'] }), result(7, 'current'))
    expect(foldToolSurfaceState(events, catalog)).toMatchObject({ phase: 'resident', unlocked: ['mcp_unity'] })
  })

  it('replays an explicit phase control and stops automatic promotion afterwards', () => {
    const narrowed = foldToolSurfaceState([
      { type: 'assistant/message', seq: 0, time: 0, data: {} },
      call(1, 'phase', { action: 'phase', phase: 'bootstrap' }),
      result(2, 'phase', false, { action: 'phase', phase: 'bootstrap', unlocked: [] }),
    ], catalog)
    expect(narrowed).toMatchObject({ phase: 'bootstrap', explicitPhase: true, source: 'control' })
  })

  it('applies only successful paired controls, then audits the latest request header', () => {
    const folded = foldToolSurfaceState([
      user(0, '修复当前实现'),
      call(1, 'unlock-ok', { action: 'unlock', tools: ['mcp_unity'] }), result(2, 'unlock-ok'),
      call(3, 'unlock-failed', { action: 'unlock', tools: ['write'] }), result(4, 'unlock-failed', true),
      call(5, 'reset', { action: 'reset' }), result(6, 'reset'),
      call(7, 'unlock-family', { action: 'unlock', family: 'shell' }), result(8, 'unlock-family'),
      header(9, ['read', 'pwsh', 'sacha_tools']),
    ], catalog)
    expect(folded).toMatchObject({
      source: 'control', unlocked: [],
      advertised: ['read', 'pwsh', 'sacha_tools'],
    })
  })

  it('starts in bootstrap for an empty or human-only log', () => {
    const pending = {
      type: 'agent/inbox/spliced', seq: 0, time: 0,
      data: {
        target: 'next-turn', start: 0,
        inserted: [{ id: 'u', role: 'user', source: { kind: 'user' }, content: [{ type: 'text', text: '请复核改动' }] }],
      },
    }
    // Human messages never select a phase, so these stay in bootstrap.
    expect(foldToolSurfaceState([pending], catalog)).toMatchObject({ phase: 'bootstrap', source: 'bootstrap' })
    expect(foldToolSurfaceState([], catalog)).toMatchObject({ phase: 'bootstrap', source: 'bootstrap' })
    // Human turns no longer reset unlocks, so two successful unlocks both hold.
    expect(foldToolSurfaceState([
      user(-2, '只读调查'), call(-1, 'old', { action: 'unlock', tools: ['mcp_unity'] }),
      pending, result(1, 'old', false, { action: 'unlock', unlocked: ['mcp_unity'] }),
      call(2, 'new', { action: 'unlock', tools: ['write'] }), result(3, 'new'),
    ], catalog)).toMatchObject({ phase: 'bootstrap', source: 'control', unlocked: ['mcp_unity', 'write'] })
  })

  it('discards an unlock that was started before an explicit phase control', () => {
    // An explicit phase control is the boundary that still resets the surface,
    // so a control call started earlier may not re-unlock when it lands later.
    const folded = foldToolSurfaceState([
      call(1, 'stale', { action: 'unlock', tools: ['mcp_unity'] }),
      call(2, 'phase', { action: 'phase', phase: 'resident' }),
      result(3, 'phase', false, { action: 'phase', phase: 'resident', unlocked: [] }),
      result(4, 'stale', false, { action: 'unlock', unlocked: ['mcp_unity'] }),
    ], catalog)
    expect(folded).toMatchObject({ phase: 'resident', explicitPhase: true, unlocked: [] })
  })

  it('recovers committed exact family members without unlocking later same-family tools', () => {
    const expanded = createToolCatalog([
      schema('read'), schema('web_fetch'), schema('web_search'),
    ])
    const folded = foldToolSurfaceState([
      user(0, '只读查看当前状态'),
      call(1, 'unlock-web', { action: 'unlock', family: 'web' }),
      result(2, 'unlock-web', false, { action: 'unlock', unlocked: ['web_fetch'] }),
    ], expanded)
    expect(folded.unlocked).toEqual(['web_fetch'])
    expect(folded.unlocked).not.toContain('web_search')
  })
})

describe('controller transitions and same-response guard', () => {
  it('unlocks known tools, denies them before a new header, then permits after advertisement', () => {
    const { controller } = controllerWithLog()
    expect(controller.catalogSearch('write').items.map(item => item.name)).toEqual(['write'])
    expect(controller.guardReason('write')).toBeDefined()
    const unlocked = controller.unlock(['write'])
    expect(unlocked.unlocked).toEqual(['write'])
    expect(unlocked.source).toBe('control')
    expect(unlocked.visible).toContain('write')
    expect(unlocked.hidden).not.toContain('write')
    expect(controller.catalogSearch('write').items).toEqual([])
    expect(controller.guardReason('write')).toBeDefined()
    controller.noteRequestHeader([{ name: 'read' }, { name: 'write' }, { name: 'sacha_tools' }])
    expect(controller.guardReason('write')).toBeUndefined()
    expect(controller.guardReason('mcp_unity')).toBeDefined()
    expect(controller.guardReason('sacha_tools')).toBeUndefined()
  })

  it('resets temporary unlocks to the current phase', () => {
    const { controller } = controllerWithLog()
    controller.unlock(['write', 'mcp_unity'])
    expect(controller.snapshot().unlocked).toEqual(['mcp_unity', 'write'])
    expect(controller.reset()).toMatchObject({ phase: 'bootstrap', unlocked: [] })
    expect(controller.guardReason('write')).toBeDefined()
  })

  it('promotes on the first durable signal and keeps unlocks across it', () => {
    const controller = controllerWithLog(recovery({ advertised: [] })).controller
    expect(controller.snapshot().phase).toBe('bootstrap')
    controller.unlock(['mcp_unity'])
    // A human turn alone never promotes.
    expect(controller.snapshot().phase).toBe('bootstrap')
    // The Runtime's own first tool call does.
    controller.noteDurableEvent({ type: 'tool/call' })
    expect(controller.snapshot().phase).toBe('resident')
    expect(controller.snapshot().source).toBe('runtime')
    expect(controller.snapshot().unlocked).toEqual(['mcp_unity'])
    expect(controller.guardReason('write')).toBeDefined()
    controller.noteRequestHeader([{ name: 'write' }])
    expect(controller.guardReason('write')).toBeUndefined()
  })

  it('lets the model switch phase explicitly and stops automatic promotion afterwards', () => {
    const controller = controllerWithLog(recovery({ advertised: [] })).controller
    controller.noteDurableEvent({ type: 'assistant/message' })
    expect(controller.snapshot().phase).toBe('resident')
    controller.unlock(['mcp_unity'])
    // Narrowing back to bootstrap clears temporary unlocks.
    expect(controller.setPhase('bootstrap')).toMatchObject({ phase: 'bootstrap', unlocked: [] })
    expect(controller.guardReason('write')).toBeDefined()
    // A later durable signal must not silently undo the model's choice.
    controller.noteDurableEvent({ type: 'tool/call' })
    expect(controller.snapshot().phase).toBe('bootstrap')
    // The model can also open the resident set without waiting for a signal.
    expect(controller.setPhase('resident')).toMatchObject({ phase: 'resident' })
  })

  it('does not commit a phase change when the native policy installation fails', () => {
    const controller = new RootToolSurfaceController('root', catalog, recovery(), () => { throw new Error('install failed') })
    const before = controller.snapshot()
    expect(() => controller.setPhase('resident')).toThrow()
    expect(controller.snapshot()).toEqual(before)
  })
})

describe('paired presentation and replacement invariants', () => {
  it('filters same-scope schemas and both conventional and configured guidance', () => {
    const assembly = {
      sections: [
        { name: 'harness:identity', text: 'identity' },
        { name: 'tool:read', text: 'read guidance' },
        { name: 'tool:write', text: 'write guidance' },
        { name: 'team:policy', text: 'team guidance' },
        { name: 'custom:mcp', text: 'mcp guidance' },
      ],
      contexts: [],
      tools: [schema('read'), schema('write'), schema('spawn_teammate'), schema('mcp_unity'), schema('sacha_tools')],
      variables: {},
    }
    const filtered = filterPromptAssembly(assembly, new Set(['read']), { 'custom:mcp': ['mcp_unity'] })
    expect(filtered.tools.map(tool => tool.name)).toEqual(['read', 'sacha_tools'])
    expect(filtered.sections.map(section => section.name)).toEqual(['harness:identity', 'tool:read'])
  })

  it('restores Agent Teams guidance when one of its real same-scope tools is unlocked', () => {
    const assembly = {
      sections: [{ name: 'team:policy', text: 'team guidance' }],
      contexts: [],
      tools: [schema('wait_agent'), schema('sacha_tools')],
      variables: {},
    }
    const filtered = filterPromptAssembly(assembly, new Set(['wait_agent']))
    expect(filtered.tools.map(tool => tool.name)).toEqual(['wait_agent', 'sacha_tools'])
    expect(filtered.sections.map(section => section.name)).toEqual(['team:policy'])
  })

  it('restores shared goal guidance when one real goal tool is unlocked', () => {
    const assembly = {
      sections: [{ name: 'tool:goal', text: 'goal guidance' }],
      contexts: [],
      tools: [schema('get_goal'), schema('sacha_tools')],
      variables: {},
    }
    const filtered = filterPromptAssembly(assembly, new Set(['get_goal']))
    expect(filtered.tools.map(tool => tool.name)).toEqual(['get_goal', 'sacha_tools'])
    expect(filtered.sections.map(section => section.name)).toEqual(['tool:goal'])
  })

  it('installs the candidate before disposing old and preserves old when install fails', () => {
    const slot = new NewFirstPolicySlot()
    const log: string[] = []
    slot.replace(() => ({ allowed: new Set(['old']), dispose: () => { log.push('dispose:old') } }))
    slot.replace(() => {
      log.push('install:new')
      return { allowed: new Set(['new']), dispose: () => { log.push('dispose:new') } }
    })
    expect(log).toEqual(['install:new', 'dispose:old'])
    expect(() => slot.replace(() => {
      log.push('install:failed')
      throw new Error('candidate failed')
    })).toThrow()
    slot.dispose()
    expect(log).toEqual(['install:new', 'dispose:old', 'install:failed', 'dispose:new'])
  })
})
