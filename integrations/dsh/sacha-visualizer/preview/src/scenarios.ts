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
  return {
    available: true,
    sessionId: `preview-${id}`,
    events,
    state,
    subagents: { available: true, children },
    warnings,
  }
}

const plannerPhase = { eventType: 'phase', phase: 'planner', state: 'entered', summary: '正在澄清目标并冻结可执行范围' } as const
const executorPhase = { eventType: 'phase', phase: 'executor', state: 'entered', summary: '两个独立工作单元已派发，主任务继续推进' } as const
const reviewerPhase = { eventType: 'phase', phase: 'reviewer', state: 'waiting', summary: '实现已返回，等待独立审查结论' } as const
const blockedPhase = { eventType: 'phase', phase: 'blocked', state: 'blocked', summary: '依赖尚未满足，需要继续等待恢复条件' } as const
const completePhase = { eventType: 'phase', phase: 'complete', state: 'completed', summary: '实现、审查和证据均已收齐' } as const

const researchChild = child('Research auth surface', 'idle')
const executorChild = child('Executor implementation', 'running')
const reviewerChild = child('Reviewer security audit', 'ready')
const activeChildren: readonly SubagentSnapshot[] = [researchChild, executorChild, reviewerChild]

const managerUnits: readonly ManagerUnitSnapshot[] = [
  unit('auth-read', '调查鉴权边界', 'running'),
  unit('implementation', '实施最小修改', 'running'),
  unit('final-review', '独立复核', 'waiting', ['implementation']),
  unit('closeout', '汇总并收口', 'waiting', ['auth-read', 'final-review']),
]

const activeDelegations: VisualState['delegations'] = [
  { eventType: 'delegation', summary: 'auth-read 已派发', unitId: 'auth-read', childId: researchChild.id, state: 'dispatched', role: 'explore', surface: 'sacha_research', requestedRoute: 'deepseek/v4-flash', effectiveRoute: 'deepseek/v4-flash' },
  { eventType: 'delegation', summary: 'implementation 已派发', unitId: 'implementation', childId: executorChild.id, state: 'dispatched', role: 'executor', surface: 'sacha_worker' },
  { eventType: 'delegation', summary: 'final-review 已创建', unitId: 'final-review', childId: reviewerChild.id, state: 'settled', role: 'reviewer', surface: 'sacha_review' },
]

export const PANEL_SCENARIOS: readonly PanelScenario[] = [
  {
    id: 'sacha-only',
    title: '仅 Sacha 流程',
    description: '没有 direct child 时只显示入口、Gate 和 Sacha 状态。',
    snapshot: makeSnapshot('sacha-only', {
      phase: plannerPhase,
      gates: { planner: { eventType: 'gate', gate: 'planner', decision: 'open', summary: 'Planner Gate 已打开' } },
      waves: [], delegations: [], evidence: {},
    }, [recorded(1, plannerPhase)]),
  },
  {
    id: 'running-children',
    title: 'Manager DAG + children',
    description: '显示 Sacha 依赖图、波次、work unit 与 durable child 的绑定。',
    snapshot: makeSnapshot('running-children', {
      phase: executorPhase,
      gates: { manager: { eventType: 'gate', gate: 'manager', decision: 'open', summary: 'Manager 协调已启用' } },
      waves: [{ eventType: 'manager_wave', waveId: 'wave-1', state: 'dispatched', units: managerUnits, summary: '两个 ready unit 已派发；Reviewer 等待 implementation' }],
      delegations: activeDelegations,
      evidence: {},
    }, [recorded(1, executorPhase)], activeChildren),
  },
  {
    id: 'review',
    title: '等待独立审查',
    description: 'Reviewer Gate、Review Outcome、依赖与 Reviewer child 映射。',
    snapshot: makeSnapshot('review', {
      phase: reviewerPhase,
      gates: { reviewer: { eventType: 'gate', gate: 'reviewer', decision: 'open', summary: 'Reviewer Gate 已打开' } },
      waves: [{
        eventType: 'manager_wave', waveId: 'wave-review', state: 'waiting', summary: '实现已完成，独立复核正在运行',
        units: [unit('implementation', '实施最小修改', 'completed'), unit('final-review', '独立复核', 'running', ['implementation'])],
      }],
      delegations: [activeDelegations[1]!, { ...activeDelegations[2]!, state: 'dispatched' }],
      review: { eventType: 'review', outcome: 'needs_fix', summary: 'Needs Fix：验证发现行为不符' },
      evidence: { source: { eventType: 'evidence', layer: 'source', status: 'verified', references: ['src'], summary: '源码已核对' } },
    }, [recorded(1, reviewerPhase)], [executorChild, { ...reviewerChild, status: 'running' }]),
  },
  {
    id: 'nested-warning',
    title: '单层派发偏差',
    description: '观察到 direct child 又创建了下级 child，仅显示 Runtime warning。',
    snapshot: makeSnapshot('nested-warning', {
      phase: blockedPhase,
      gates: { manager: { eventType: 'gate', gate: 'manager', decision: 'open', summary: '需要复核派发偏差' } },
      waves: [{ eventType: 'manager_wave', waveId: 'wave-2', state: 'blocked', units: [unit('nested-unit', '检查嵌套派发', 'blocked')], summary: '观察到下级 child' }],
      delegations: [{ eventType: 'delegation', summary: 'nested-unit 已派发', unitId: 'nested-unit', childId: 'child-executor-nested-attempt', state: 'dispatched', role: 'executor', surface: 'sacha_worker' }],
      evidence: {},
    }, [recorded(1, blockedPhase)], [child('Executor nested attempt', 'idle', { hasChildren: true })], ['观察到下级 child；Sacha 单层派发约束需要复核']),
  },
  {
    id: 'complete',
    title: '全部完成',
    description: '完成 phase、完整依赖图、Review Accepted 和 evidence 状态。',
    snapshot: makeSnapshot('complete', {
      phase: completePhase,
      gates: {
        planner: { eventType: 'gate', gate: 'planner', decision: 'closed', summary: '无需规划' },
        manager: { eventType: 'gate', gate: 'manager', decision: 'closed', summary: '协调已结束' },
        reviewer: { eventType: 'gate', gate: 'reviewer', decision: 'closed', summary: '审查已结束' },
      },
      waves: [{ eventType: 'manager_wave', waveId: 'wave-1', state: 'completed', units: managerUnits.map(value => ({ ...value, state: 'completed' as const })), summary: '本波依赖全部满足并已消费' }],
      delegations: activeDelegations.map(value => ({ ...value, state: 'settled' as const })),
      review: { eventType: 'review', outcome: 'accepted', summary: 'Accepted' },
      evidence: {
        source: { eventType: 'evidence', layer: 'source', status: 'verified', references: ['source'], summary: '源码通过' },
        runtime: { eventType: 'evidence', layer: 'runtime', status: 'verified', references: ['runtime'], summary: 'Runtime 通过' },
      },
    }, [recorded(1, completePhase)], activeChildren.map(item => ({ ...item, status: 'ready' as const }))),
  },
]

export const PANEL_SCENARIO_BY_ID = new Map(PANEL_SCENARIOS.map((scenario) => [scenario.id, scenario]))
