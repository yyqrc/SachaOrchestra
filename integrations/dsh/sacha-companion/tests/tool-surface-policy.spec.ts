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
  classifyRootMessage,
  createToolCatalog,
  filterPromptAssembly,
  foldToolSurfaceState,
  isLiveRootAgent,
  mergeToolCatalog,
  profileAllowsTool,
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
    profile: 'inspect', unlocked: [], advertised: ['read', 'grep', 'sacha_research', 'sacha_tools'],
    source: 'user-message', warnings: [], ...overrides,
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

describe('Root task classification and profile allow lists', () => {
  it('classifies explicit execution and review while keeping questions conservative', () => {
    expect(classifyRootMessage('修复构建脚本并运行测试')).toBe('execute')
    expect(classifyRootMessage('修复构建脚本！')).toBe('execute')
    expect(classifyRootMessage('修复构建脚本，不要修改 Core；交付前完成独立复核。')).toBe('execute')
    expect(classifyRootMessage('先显式加载 using-sacha，再迭代 DSH 适配层；交付前需要独立复核。')).toBe('execute')
    expect(classifyRootMessage('先只读调查，然后修复构建脚本')).toBe('execute')
    expect(classifyRootMessage('严格执行只读验证后写入结果')).toBe('execute')
    expect(classifyRootMessage('请复核这次改动')).toBe('review')
    expect(classifyRootMessage('只读审查这些改动，给出修改建议')).toBe('review')
    expect(classifyRootMessage('执行一次只读复核')).toBe('review')
    expect(classifyRootMessage('应该不会修改到 core 的规则？')).toBe('inspect')
    expect(classifyRootMessage('如何修复构建脚本？')).toBe('inspect')
    expect(classifyRootMessage('安装步骤是什么？')).toBe('inspect')
    expect(classifyRootMessage('Can you fix this?')).toBe('execute')
    expect(classifyRootMessage('严格执行该只读任务')).toBe('inspect')
    expect(classifyRootMessage('请执行这个只读调查，不要修改文件')).toBe('inspect')
    expect(classifyRootMessage('Human 目标是迭代 DSH 适配层；第一阶段保持只读，确认后再实施。')).toBe('inspect')
    expect(classifyRootMessage('看看为什么构建失败')).toBe('inspect')
    expect(classifyRootMessage('ambiguous request')).toBe('inspect')
  })

  it('classifies explicit Chinese synchronization and path-prefixed edits as execution', () => {
    expect(classifyRootMessage('从.codex的Agents.md 同步规则过来.dsh下的Agents.md')).toBe('execute')
    expect(classifyRootMessage('同步文件')).toBe('execute')
    expect(classifyRootMessage('把规则同步到 .dsh')).toBe('execute')
    expect(classifyRootMessage('C:\\Users\\shifengzhou\\.dsh\\agent-plugins.yml 还是把cgame-unity改成Client 和 LookDevProject两个工作区开启 不全局开启了')).toBe('execute')
    expect(classifyRootMessage('如何同步这些规则？')).toBe('inspect')
  })

  it('keeps MCP, Agent Teams, ordinary subagent/workflow, and writes hidden by default', () => {
    expect(profileAllowsTool('inspect', 'read')).toBe(true)
    expect(profileAllowsTool('inspect', 'sacha_research')).toBe(true)
    expect(profileAllowsTool('inspect', 'write')).toBe(false)
    expect(profileAllowsTool('execute', 'write')).toBe(true)
    expect(profileAllowsTool('execute', 'job_output')).toBe(true)
    expect(profileAllowsTool('review', 'pwsh')).toBe(true)
    expect(profileAllowsTool('review', 'write')).toBe(false)
    for (const name of ['mcp_unity', 'spawn_teammate', 'subagent', 'workflow']) {
      expect(profileAllowsTool('execute', name)).toBe(false)
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
  it('replays task changes in event order and ignores old controls that finish later', () => {
    const events = [
      user(0, '只读调查'),
      call(1, 'old', { action: 'unlock', tools: ['mcp_unity'] }),
      user(2, '实现当前功能'),
      result(3, 'old', false, { action: 'unlock', unlocked: ['mcp_unity'] }),
      user(4, '继续'),
    ]
    expect(foldToolSurfaceState(events, catalog)).toMatchObject({ profile: 'execute', unlocked: [], source: 'user-message' })
    events.push(call(5, 'current', { action: 'unlock', tools: ['mcp_unity'] }), result(6, 'current'))
    expect(foldToolSurfaceState(events, catalog)).toMatchObject({ profile: 'execute', unlocked: ['mcp_unity'] })
    events.push(user(7, '请复核改动'))
    expect(foldToolSurfaceState(events, catalog)).toMatchObject({ profile: 'review', unlocked: [] })
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
      profile: 'execute', source: 'control', unlocked: [],
      advertised: ['read', 'pwsh', 'sacha_tools'],
    })
  })

  it('falls back from first human transcript to pending human inbox to bootstrap', () => {
    const pending = {
      type: 'agent/inbox/spliced', seq: 0, time: 0,
      data: {
        target: 'next-turn', start: 0,
        inserted: [{ id: 'u', role: 'user', source: { kind: 'user' }, content: [{ type: 'text', text: '请复核改动' }] }],
      },
    }
    expect(foldToolSurfaceState([pending], catalog)).toMatchObject({ profile: 'review', source: 'pending-inbox' })
    expect(foldToolSurfaceState([], catalog)).toMatchObject({ profile: 'inspect', source: 'bootstrap' })
    expect(foldToolSurfaceState([
      user(-2, '只读调查'), call(-1, 'old', { action: 'unlock', tools: ['mcp_unity'] }),
      pending, result(1, 'old', false, { action: 'unlock', unlocked: ['mcp_unity'] }),
      call(2, 'new', { action: 'unlock', tools: ['write'] }), result(3, 'new'),
    ], catalog)).toMatchObject({ profile: 'review', source: 'control', unlocked: ['write'] })
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

  it('resets temporary unlocks to the classified base profile', () => {
    const { controller } = controllerWithLog()
    controller.unlock(['write', 'mcp_unity'])
    expect(controller.snapshot().unlocked).toEqual(['mcp_unity', 'write'])
    expect(controller.reset()).toMatchObject({ profile: 'inspect', unlocked: [] })
    expect(controller.guardReason('write')).toBeDefined()
  })

  it('updates explicit tasks, clears unlocks, and preserves neutral continuation', () => {
    const bootstrap = controllerWithLog(recovery({ source: 'bootstrap', advertised: [] })).controller
    expect(bootstrap.classifyHuman(user(0, '只读调查').data)).toBe('inspect')
    bootstrap.unlock(['mcp_unity'])
    expect(bootstrap.classifyHuman(user(1, '实现这个功能').data)).toBe('execute')
    expect(bootstrap.snapshot().unlocked).toEqual([])
    expect(bootstrap.guardReason('write')).toBeDefined()
    bootstrap.noteRequestHeader([{ name: 'write' }])
    expect(bootstrap.guardReason('write')).toBeUndefined()
    bootstrap.unlock(['mcp_unity'])
    expect(bootstrap.classifyHuman(user(2, '继续').data)).toBe('execute')
    expect(bootstrap.classifyHuman(user(3, '进度怎么样？').data)).toBe('execute')
    expect(bootstrap.classifyHuman(user(30, '查看当前进度').data)).toBe('execute')
    expect(bootstrap.snapshot().unlocked).toEqual(['mcp_unity'])
    expect(bootstrap.classifyHuman(user(4, '请复核改动').data)).toBe('review')
    expect(bootstrap.snapshot().unlocked).toEqual([])
    bootstrap.unlock(['write'])
    expect(bootstrap.reset()).toMatchObject({ profile: 'review', unlocked: [] })
    expect(bootstrap.classifyHuman(user(5, '先只读调查').data)).toBe('inspect')
  })

  it('does not commit a task change when the native policy installation fails', () => {
    const controller = new RootToolSurfaceController('root', catalog, recovery(), () => { throw new Error('install failed') })
    const before = controller.snapshot()
    expect(() => controller.classifyHuman(user(1, '实现功能').data)).toThrow()
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
