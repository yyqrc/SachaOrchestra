import type {
  RecordedVisualEvent, SachaActivitySnapshot, SachaVisualEvent, TeamMemberSnapshot, TeamTaskSnapshot, VisualState,
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

function task(value: Partial<TeamTaskSnapshot> & Pick<TeamTaskSnapshot, 'id' | 'subject' | 'status'>): TeamTaskSnapshot {
  return {
    revision: 1,
    description: value.subject,
    blockedBy: [],
    writeScopes: [],
    ready: value.status !== 'pending',
    writeScopeWarnings: [],
    ...value,
  }
}

function member(value: Partial<TeamMemberSnapshot> & Pick<TeamMemberSnapshot, 'id' | 'name' | 'status'>): TeamMemberSnapshot {
  return { role: 'teammate', diagnostics: [], ...value }
}

function makeSnapshot(id: string, state: VisualState, events: readonly RecordedVisualEvent[], options: {
  readonly teamAvailable?: boolean
  readonly members?: readonly TeamMemberSnapshot[]
  readonly tasks?: readonly TeamTaskSnapshot[]
  readonly warnings?: readonly string[]
} = {}): SachaActivitySnapshot {
  return {
    available: true,
    sessionId: `preview-${id}`,
    events,
    state,
    team: {
      available: options.teamAvailable ?? true,
      members: options.members ?? [],
      tasks: options.tasks ?? [],
    },
    warnings: options.warnings ?? [],
  }
}

const plannerPhase = { eventType: 'phase', phase: 'planner', state: 'entered', summary: '正在澄清目标并冻结可执行范围' } as const
const executorPhase = { eventType: 'phase', phase: 'executor', state: 'entered', summary: '三项工作并行实施，等待第一批回报' } as const
const reviewerPhase = { eventType: 'phase', phase: 'reviewer', state: 'waiting', summary: '实现已返回，等待独立审查结论' } as const
const blockedPhase = { eventType: 'phase', phase: 'blocked', state: 'blocked', summary: '写入范围冲突，需要 Human 决定' } as const
const completePhase = { eventType: 'phase', phase: 'complete', state: 'completed', summary: '实现、审查和证据均已收齐' } as const

const lead = member({ id: 'lead', name: 'Sacha Lead', role: 'lead', status: 'running', description: '主任务 / 指挥' })
const workingMembers: readonly TeamMemberSnapshot[] = [
  lead,
  member({ id: 'planner', name: 'Planner', status: 'idle', description: 'Planner · research and scope' }),
  member({ id: 'executor', name: 'Executor', status: 'running', description: 'Executor · implementation' }),
  member({ id: 'reviewer', name: 'Reviewer', status: 'provisioning', description: 'Reviewer · security audit' }),
  member({ id: 'docs', name: 'Docs', status: 'inactive', description: 'Docs · release notes' }),
  member({ id: 'specialist', name: 'Mika', status: 'idle', description: 'Domain specialist' }),
]

const dependencyTasks: readonly TeamTaskSnapshot[] = [
  task({ id: 'T1', subject: '冻结交互方案', status: 'completed', ownerName: 'Planner', ready: true, writeScopes: ['preview/**'] }),
  task({ id: 'T2', subject: '实现角色与状态卡', status: 'in_progress', ownerName: 'Executor', ready: true, blockedBy: ['T1'], writeScopes: ['src/client/**'] }),
  task({ id: 'T3', subject: '独立审查视觉与边界', status: 'pending', ownerName: 'Reviewer', ready: false, blockedBy: ['T2'], writeScopes: ['src/client/**'] }),
  task({ id: 'T4', subject: '更新使用说明', status: 'pending', ownerName: 'Docs', ready: false, blockedBy: ['T2'], writeScopes: ['README.md'] }),
]

const parallelTasks: readonly TeamTaskSnapshot[] = [
  task({ id: 'P1', subject: '检查猫咪底图', status: 'completed', ownerName: 'Planner', ready: true }),
  task({ id: 'P2', subject: '调整动画幅度', status: 'in_progress', ownerName: 'Executor', ready: true }),
  task({ id: 'P3', subject: '复核 Role 道具', status: 'pending', ownerName: 'Reviewer', ready: true }),
  task({ id: 'P4', subject: '检查中文文案', status: 'in_progress', ownerName: 'Docs', ready: true }),
]

const completedTasks = dependencyTasks.map((item) => ({ ...item, status: 'completed' as const, ready: true }))

export const PANEL_SCENARIOS: readonly PanelScenario[] = [
  {
    id: 'sacha-only',
    title: '仅 Sacha 流程',
    description: '没有 Agent Teams 时的入口、Gate 和提示。',
    snapshot: makeSnapshot('sacha-only', {
      phase: plannerPhase,
      gates: { planner: { eventType: 'gate', gate: 'planner', decision: 'open', summary: 'Planner Gate 已打开' } },
      waves: [], evidence: {},
    }, [recorded(1, plannerPhase)], { teamAvailable: false }),
  },
  {
    id: 'running-dependencies',
    title: '多人执行与依赖',
    description: '成员、总进度、依赖 DAG、任务详情和状态角标。',
    snapshot: makeSnapshot('running-dependencies', {
      phase: executorPhase,
      gates: {
        planner: { eventType: 'gate', gate: 'planner', decision: 'closed', summary: '范围已冻结' },
        manager: { eventType: 'gate', gate: 'manager', decision: 'open', summary: 'Manager 协调已启用' },
      },
      waves: [{ eventType: 'manager_wave', waveId: 'wave-1', state: 'dispatched', unitIds: ['T2', 'T3', 'T4'], summary: '第一波已派发' }],
      evidence: {},
    }, [recorded(1, executorPhase)], { members: workingMembers, tasks: dependencyTasks }),
  },
  {
    id: 'parallel',
    title: '并行任务',
    description: '无依赖时的并行布局、就绪和执行中状态。',
    snapshot: makeSnapshot('parallel', {
      phase: executorPhase, gates: {}, waves: [], evidence: {},
    }, [recorded(1, executorPhase)], { members: workingMembers, tasks: parallelTasks }),
  },
  {
    id: 'review',
    title: '等待审查',
    description: 'Reviewer Gate、Review Needs Fix 与等待动画。',
    snapshot: makeSnapshot('review', {
      phase: reviewerPhase,
      gates: { reviewer: { eventType: 'gate', gate: 'reviewer', decision: 'open', summary: 'Reviewer Gate 已打开' } },
      waves: [],
      review: { eventType: 'review', outcome: 'needs_fix', summary: 'Needs Fix：补充资源失败兜底' },
      evidence: { source: { eventType: 'evidence', layer: 'source', status: 'verified', references: ['src/client'], summary: '源码已核对' } },
    }, [recorded(1, reviewerPhase)], { members: workingMembers, tasks: dependencyTasks }),
  },
  {
    id: 'blocked',
    title: '阻塞与冲突',
    description: '阻塞阶段、失败成员、写入冲突和 Runtime 警告。',
    snapshot: makeSnapshot('blocked', {
      phase: blockedPhase,
      gates: { reviewer: { eventType: 'gate', gate: 'reviewer', decision: 'open', summary: '等待修复后重审' } },
      waves: [],
      review: { eventType: 'review', outcome: 'blocked', summary: 'Blocked：需要 Human 选择写入 Owner' },
      evidence: {},
    }, [recorded(1, blockedPhase)], {
      members: [lead, member({ id: 'failed-reviewer', name: 'Reviewer', status: 'failed', description: 'Reviewer · audit', diagnostics: ['worker disconnected'] })],
      tasks: [task({
        id: 'B1', subject: '解决样式写入冲突', status: 'pending', ownerName: 'Reviewer', ready: false,
        blockedBy: ['external-decision'], writeScopes: ['src/client/ActivityPanel.module.css'],
        writeScopeWarnings: ['与 Executor 的写入范围重叠'],
      })],
      warnings: ['可视化读取到一次 Runtime 警告：Reviewer 连接已断开'],
    }),
  },
  {
    id: 'complete',
    title: '全部完成',
    description: '完成动画、全绿进度、Review Accepted 和已交付任务。',
    snapshot: makeSnapshot('complete', {
      phase: completePhase,
      gates: {
        planner: { eventType: 'gate', gate: 'planner', decision: 'closed', summary: '无需规划' },
        manager: { eventType: 'gate', gate: 'manager', decision: 'closed', summary: '无需协调' },
        reviewer: { eventType: 'gate', gate: 'reviewer', decision: 'closed', summary: '审查已结束' },
      },
      waves: [],
      review: { eventType: 'review', outcome: 'accepted', summary: 'Accepted' },
      evidence: {
        source: { eventType: 'evidence', layer: 'source', status: 'verified', references: ['source'], summary: '源码通过' },
        package: { eventType: 'evidence', layer: 'package', status: 'verified', references: ['package'], summary: '打包通过' },
        runtime: { eventType: 'evidence', layer: 'runtime', status: 'verified', references: ['desktop'], summary: 'Desktop 通过' },
      },
    }, [recorded(1, completePhase)], { members: workingMembers.map(item => ({ ...item, status: 'idle' as const })), tasks: completedTasks }),
  },
  {
    id: 'collapsed',
    title: '收起徽标',
    description: '面板收起后的事件数和忙碌脉冲。',
    collapsed: true,
    snapshot: makeSnapshot('collapsed', {
      phase: executorPhase, gates: {}, waves: [], evidence: {},
    }, [recorded(1, executorPhase), recorded(2, { eventType: 'gate', gate: 'manager', decision: 'open', summary: 'Manager Gate 已打开' })], { members: workingMembers, tasks: parallelTasks }),
  },
]

export const PANEL_SCENARIO_BY_ID = new Map(PANEL_SCENARIOS.map((scenario) => [scenario.id, scenario]))
