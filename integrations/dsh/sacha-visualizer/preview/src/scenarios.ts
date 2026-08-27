import type {
  RecordedVisualEvent, SachaActivitySnapshot, SachaVisualEvent, SubagentSnapshot, VisualState,
} from '../../src/types.ts'

export type PanelScenario = {
  readonly id: string
  readonly title: string
  readonly description: string
  readonly snapshot: SachaActivitySnapshot
  readonly collapsed?: boolean
}

const NOW = 1_787_735_000_000

function recorded(seq: number, value: SachaVisualEvent): RecordedVisualEvent {
  return { seq, time: NOW + seq * 1000, value }
}

function child(label: string, status: SubagentSnapshot['status'], options: Partial<SubagentSnapshot> = {}): SubagentSnapshot {
  return { id: `child-${label.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`, label, status, hasChildren: false, ...options }
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

const activeChildren: readonly SubagentSnapshot[] = [
  child('Research auth surface', 'idle'),
  child('Executor implementation', 'running'),
  child('Reviewer security audit', 'ready'),
]

export const PANEL_SCENARIOS: readonly PanelScenario[] = [
  {
    id: 'sacha-only',
    title: '仅 Sacha 流程',
    description: '没有 direct child 时只显示入口、Gate 和 Sacha 状态。',
    snapshot: makeSnapshot('sacha-only', {
      phase: plannerPhase,
      gates: { planner: { eventType: 'gate', gate: 'planner', decision: 'open', summary: 'Planner Gate 已打开' } },
      waves: [], evidence: {},
    }, [recorded(1, plannerPhase)]),
  },
  {
    id: 'running-children',
    title: 'Continuable children',
    description: '显示 durable child id、label、活动状态与 Sacha Manager 波次。',
    snapshot: makeSnapshot('running-children', {
      phase: executorPhase,
      gates: { manager: { eventType: 'gate', gate: 'manager', decision: 'open', summary: 'Manager 协调已启用' } },
      waves: [{ eventType: 'manager_wave', waveId: 'wave-1', state: 'dispatched', unitIds: ['auth-read', 'implementation'], summary: '两个直接 child 已派发' }],
      evidence: {},
    }, [recorded(1, executorPhase)], activeChildren),
  },
  {
    id: 'review',
    title: '等待独立审查',
    description: 'Reviewer Gate、Review Outcome 与独立 Reviewer child。',
    snapshot: makeSnapshot('review', {
      phase: reviewerPhase,
      gates: { reviewer: { eventType: 'gate', gate: 'reviewer', decision: 'open', summary: 'Reviewer Gate 已打开' } },
      waves: [],
      review: { eventType: 'review', outcome: 'needs_fix', summary: 'Needs Fix：验证发现行为不符' },
      evidence: { source: { eventType: 'evidence', layer: 'source', status: 'verified', references: ['src'], summary: '源码已核对' } },
    }, [recorded(1, reviewerPhase)], [child('Reviewer security audit', 'running')]),
  },
  {
    id: 'nested-warning',
    title: '单层派发偏差',
    description: '观察到 direct child 又创建了下级 child，仅显示 Runtime warning。',
    snapshot: makeSnapshot('nested-warning', {
      phase: blockedPhase,
      gates: { manager: { eventType: 'gate', gate: 'manager', decision: 'open', summary: '需要复核派发偏差' } },
      waves: [{ eventType: 'manager_wave', waveId: 'wave-2', state: 'blocked', unitIds: ['nested-unit'], summary: '观察到下级 child' }],
      evidence: {},
    }, [recorded(1, blockedPhase)], [child('Executor nested attempt', 'idle', { hasChildren: true })], ['观察到下级 child；Sacha 单层派发约束需要复核']),
  },
  {
    id: 'complete',
    title: '全部完成',
    description: '完成 phase、Review Accepted 和 evidence 状态。',
    snapshot: makeSnapshot('complete', {
      phase: completePhase,
      gates: {
        planner: { eventType: 'gate', gate: 'planner', decision: 'closed', summary: '无需规划' },
        manager: { eventType: 'gate', gate: 'manager', decision: 'closed', summary: '协调已结束' },
        reviewer: { eventType: 'gate', gate: 'reviewer', decision: 'closed', summary: '审查已结束' },
      },
      waves: [{ eventType: 'manager_wave', waveId: 'wave-1', state: 'completed', unitIds: ['auth-read', 'implementation'], summary: '本波结果已全部消费' }],
      review: { eventType: 'review', outcome: 'accepted', summary: 'Accepted' },
      evidence: {
        source: { eventType: 'evidence', layer: 'source', status: 'verified', references: ['source'], summary: '源码通过' },
        runtime: { eventType: 'evidence', layer: 'runtime', status: 'verified', references: ['runtime'], summary: 'Runtime 通过' },
      },
    }, [recorded(1, completePhase)], activeChildren.map(item => ({ ...item, status: 'ready' as const }))),
  },
  {
    id: 'collapsed',
    title: '收起徽标',
    description: '面板收起后的活动计数和运行脉冲。',
    collapsed: true,
    snapshot: makeSnapshot('collapsed', {
      phase: executorPhase, gates: {}, waves: [], evidence: {},
    }, [recorded(1, executorPhase)], activeChildren),
  },
]

export const PANEL_SCENARIO_BY_ID = new Map(PANEL_SCENARIOS.map((scenario) => [scenario.id, scenario]))
