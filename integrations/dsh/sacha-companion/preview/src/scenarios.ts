import type {
  ManagerUnitSnapshot, RecordedVisualEvent, SachaActivitySnapshot, SachaVisualEvent, SubagentSnapshot, VisualState,
} from '../../src/types.ts'

export type PanelScenario = {
  readonly id: string
  readonly title: string
  readonly description: string
  readonly snapshot: SachaActivitySnapshot
}

const NOW = 1_787_735_000_000

function recorded(seq: number, value: SachaVisualEvent): RecordedVisualEvent {
  return { seq, time: NOW + seq * 1000, value }
}

function child(label: string, status: SubagentSnapshot['status'], options: Partial<SubagentSnapshot> = {}): SubagentSnapshot {
  return { id: `child-${label.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`, label, status, hasChildren: false, ...options }
}

function unit(id: string, label: string, state: ManagerUnitSnapshot['state'], blockedBy: readonly string[] = []): ManagerUnitSnapshot {
  return { id, label, state, blockedBy }
}

function makeSnapshot(
  id: string,
  state: VisualState,
  events: readonly RecordedVisualEvent[],
  children: readonly SubagentSnapshot[] = [],
  warnings: readonly string[] = [],
): SachaActivitySnapshot {
  const profile = state.phase?.phase === 'reviewer'
    ? 'review' as const
    : state.phase?.phase === 'executor'
      ? 'execute' as const
      : 'inspect' as const
  return {
    available: true,
    sessionId: `preview-${id}`,
    events,
    state,
    subagents: { available: true, children },
    toolSurface: {
      sessionId: `preview-${id}`,
      profile,
      visibleCount: profile === 'execute' ? 14 : 9,
      hiddenCount: profile === 'execute' ? 37 : 42,
      visible: ['read', 'grep', 'sacha_tools'],
      hidden: ['mcp_unity'],
      advertised: ['read', 'grep', 'sacha_tools'],
      unlocked: [],
      source: 'user-message',
      fallback: false,
      warnings: [],
    },
    warnings,
  }
}

const plannerPhase = { eventType: 'phase', phase: 'planner', state: 'entered', summary: '正在确认目标和下一步' } as const
const executorPhase = { eventType: 'phase', phase: 'executor', state: 'entered', summary: '两项工作正在同时推进' } as const
const reviewerPhase = { eventType: 'phase', phase: 'reviewer', state: 'waiting', summary: '修改已经完成，正在确认结果' } as const
const blockedPhase = { eventType: 'phase', phase: 'blocked', state: 'blocked', summary: '发现异常分派，暂时无法继续' } as const
const completePhase = { eventType: 'phase', phase: 'complete', state: 'completed', summary: '工作与验证均已完成' } as const

const researchChild = child('Research auth surface', 'idle')
const executorChild = child('Executor implementation', 'running')
const reviewerChild = child('Reviewer security audit', 'ready')
const activeChildren: readonly SubagentSnapshot[] = [researchChild, executorChild, reviewerChild]

const managerUnits: readonly ManagerUnitSnapshot[] = [
  unit('auth-read', '调查鉴权边界', 'running'),
  unit('implementation', '实施最小修改', 'running'),
  unit('final-review', '确认最终结果', 'waiting', ['implementation']),
  unit('closeout', '汇总结果', 'waiting', ['auth-read', 'final-review']),
]

const activeDelegations: VisualState['delegations'] = [
  { eventType: 'delegation', summary: 'auth-read 已派发', unitId: 'auth-read', childId: researchChild.id, state: 'dispatched', role: 'explore', surface: 'sacha_research', requestedRoute: 'deepseek/v4-flash', effectiveRoute: 'deepseek/v4-flash' },
  { eventType: 'delegation', summary: 'implementation 已派发', unitId: 'implementation', childId: executorChild.id, state: 'dispatched', role: 'executor', surface: 'sacha_worker' },
  { eventType: 'delegation', summary: 'final-review 已创建', unitId: 'final-review', childId: reviewerChild.id, state: 'settled', role: 'reviewer', surface: 'sacha_review' },
]

export const PANEL_SCENARIOS: readonly PanelScenario[] = [
  {
    id: 'sacha-only',
    title: '仅显示当前进展',
    description: '没有并行工作时，显示当前状态和需要关注的信息。',
    snapshot: makeSnapshot('sacha-only', {
      phase: plannerPhase,
      gates: { planner: { eventType: 'gate', gate: 'planner', decision: 'open', summary: '需要先确认目标和做法' } },
      waves: [], delegations: [], evidence: {},
    }, [recorded(1, plannerPhase)]),
  },
  {
    id: 'running-children',
    title: '多项工作同时进行',
    description: '显示工作先后关系和当前进度。',
    snapshot: makeSnapshot('running-children', {
      phase: executorPhase,
      gates: { manager: { eventType: 'gate', gate: 'manager', decision: 'open', summary: '多项工作需要协调' } },
      waves: [{ eventType: 'manager_wave', waveId: 'wave-1', state: 'dispatched', units: managerUnits, summary: '两项工作正在进行，最终确认需要等待修改完成' }],
      delegations: activeDelegations,
      evidence: {},
    }, [recorded(1, executorPhase)], activeChildren),
  },
  {
    id: 'review',
    title: '等待结果确认',
    description: '修改完成后，显示结果状态和下一步。',
    snapshot: makeSnapshot('review', {
      phase: reviewerPhase,
      gates: { reviewer: { eventType: 'gate', gate: 'reviewer', decision: 'open', summary: '正在确认最终结果' } },
      waves: [{
        eventType: 'manager_wave', waveId: 'wave-review', state: 'waiting', summary: '修改已完成，正在确认最终结果',
        units: [unit('implementation', '实施最小修改', 'completed'), unit('final-review', '确认最终结果', 'running', ['implementation'])],
      }],
      delegations: [activeDelegations[1]!, { ...activeDelegations[2]!, state: 'dispatched' }],
      review: { eventType: 'review', outcome: 'needs_fix', summary: '验证发现问题，需要调整' },
      evidence: { source: { eventType: 'evidence', layer: 'source', status: 'verified', references: ['src'], summary: '源码已核对' } },
    }, [recorded(1, reviewerPhase)], [executorChild, { ...reviewerChild, status: 'running' }]),
  },
  {
    id: 'nested-warning',
    title: '发现重复分派',
    description: '出现异常分派时给出清晰提示。',
    snapshot: makeSnapshot('nested-warning', {
      phase: blockedPhase,
      gates: { manager: { eventType: 'gate', gate: 'manager', decision: 'open', summary: '发现重复分派，需要处理' } },
      waves: [{ eventType: 'manager_wave', waveId: 'wave-2', state: 'blocked', units: [unit('nested-unit', '处理重复分派', 'blocked')], summary: '发现重复分派' }],
      delegations: [{ eventType: 'delegation', summary: 'nested-unit 已派发', unitId: 'nested-unit', childId: 'child-executor-nested-attempt', state: 'dispatched', role: 'executor', surface: 'sacha_worker' }],
      evidence: {},
    }, [recorded(1, blockedPhase)], [child('Executor nested attempt', 'idle', { hasChildren: true })], ['观察到下级 child；Sacha 单层派发约束需要复核']),
  },
  {
    id: 'complete',
    title: '全部完成',
    description: '工作、验证和结果都已收齐。',
    snapshot: makeSnapshot('complete', {
      phase: completePhase,
      gates: {
        planner: { eventType: 'gate', gate: 'planner', decision: 'closed', summary: '无需规划' },
        manager: { eventType: 'gate', gate: 'manager', decision: 'closed', summary: '协调已结束' },
        reviewer: { eventType: 'gate', gate: 'reviewer', decision: 'closed', summary: '结果已确认' },
      },
      waves: [{ eventType: 'manager_wave', waveId: 'wave-1', state: 'completed', units: managerUnits.map(value => ({ ...value, state: 'completed' as const })), summary: '本波依赖全部满足并已消费' }],
      delegations: activeDelegations.map(value => ({ ...value, state: 'settled' as const })),
      review: { eventType: 'review', outcome: 'accepted', summary: '结果已确认' },
      evidence: {
        source: { eventType: 'evidence', layer: 'source', status: 'verified', references: ['source'], summary: '源码通过' },
        runtime: { eventType: 'evidence', layer: 'runtime', status: 'verified', references: ['runtime'], summary: 'Runtime 通过' },
      },
    }, [recorded(1, completePhase)], activeChildren.map(item => ({ ...item, status: 'ready' as const }))),
  },
]

export const PANEL_SCENARIO_BY_ID = new Map(PANEL_SCENARIOS.map((scenario) => [scenario.id, scenario]))
