/**
 * Sacha activity panel — Sacha workflow observability companion.
 * The shell, gestures, layout, and visual hierarchy mirror the DSH AgentTeams
 * reference plugin (NanmiCoder/dsh-agent-teams). The Sacha face is an animated
 * phase rail: one glance shows the current workflow node; gates and review
 * ride the rail as compact markers instead of text cards.
 */

import {
  useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState, useSyncExternalStore,
  type CSSProperties, type PointerEvent as ReactPointerEvent,
} from 'react'
import type { ObservableSnapshot, SessionListState } from '@deepseek-ai/dsh-client-runtime/client'
import { compactDagLayout, NODE_HEIGHT, NODE_WIDTH, relatedTaskIds } from './activity-model.ts'
import { useSachaActivity } from './activity-monitor.ts'
import { CONDUCTOR_CAT, MEMBER_CAT, memberCatProp } from './artwork.ts'
import { CatArt } from './cats.tsx'
import { MemberStatusArt } from './status-art.tsx'
import {
  DEFAULT_PANEL_LAYOUT, PANEL_LAYOUT_STORAGE_KEY, compactPanel, dockPanel, floatPanel, movePanel,
  panelMaximumHeight, panelUsesAutoHeight, parsePanelLayout, resizePanel, resolvePanelLayout,
  type PanelBounds, type PanelLayout, type PanelResizeEdge,
} from './panel-geometry.ts'
import { PANEL_DISMISSED_KEY, dismissSession, parseDismissedSessions } from './panel-visibility.ts'
import type {
  SachaActivitySnapshot, SachaGate, SachaPhase,
  TeamMemberSnapshot, TeamTaskSnapshot, VisualState,
} from '../types.ts'
import css from './ActivityPanel.module.css'

const PANEL_OPEN_ATTRIBUTE = 'data-sacha-panel-open'
const PANEL_SHIFT_PROPERTY = '--sacha-panel-shift'
const MOVE_THRESHOLD = 4

const PHASE_LABEL: Record<SachaPhase, string> = {
  intake: '入口判断', direct: '直接执行', planner: '规划', explore: '探索', executor: '实施',
  reviewer: '独立评审', roadmap: '路线图', 'document-project': '项目文档', closeout: '收口',
  feedback: '反馈移交', 'human-decision': '等待决定', complete: '完成', blocked: '阻塞',
}
const GATE_LABEL: Record<SachaGate, string> = {
  planner: 'Planner Gate', manager: 'Manager Gate', reviewer: 'Reviewer Gate',
}
const GATE_DECISION_LABEL: Record<string, string> = { open: '开', closed: '关' }

const MEMBER_STATUS_LABEL: Record<TeamMemberSnapshot['status'], string> = {
  running: '工作中', idle: '空闲', inactive: '未激活', provisioning: '创建中', failed: '失败',
}

type PanelGesture = {
  readonly kind: 'move' | 'resize'
  readonly edge?: PanelResizeEdge
  readonly pointerId: number
  readonly originX: number
  readonly originY: number
  readonly start: PanelLayout
  activated: boolean
}

function initialPanelLayout(): PanelLayout {
  if (typeof window === 'undefined') return DEFAULT_PANEL_LAYOUT
  return parsePanelLayout(window.localStorage.getItem(PANEL_LAYOUT_STORAGE_KEY))
}

function initialBounds(): PanelBounds {
  if (typeof window === 'undefined') return { width: 1440, height: 900, anchorRight: 1440 }
  return { width: window.innerWidth, height: window.innerHeight, anchorRight: window.innerWidth }
}

function initialDismissedSessions(): Set<string> {
  if (typeof window === 'undefined') return new Set()
  return new Set(parseDismissedSessions(window.localStorage.getItem(PANEL_DISMISSED_KEY)))
}

/**
 * Measure geometry against the shell overlay, mirroring the AgentTeams
 * reference: the overlay box is the drag/float range, while the conversation's
 * real right edge is the dock anchor (it already excludes side plugins that
 * push the app shell). This lets the panel float anywhere over the shell —
 * including beside a right workbench — while the dock still lands next to the
 * conversation instead of under the plugin layer.
 */
function measureShellBounds(): PanelBounds | undefined {
  if (typeof document === 'undefined') return undefined
  const overlay = document.querySelector<HTMLElement>('[data-shell-overlay]')
  if (overlay === null) return undefined
  const overlayRect = overlay.getBoundingClientRect()
  if (overlayRect.width <= 0 || overlayRect.height <= 0) return undefined
  const conversation = document.querySelector<HTMLElement>("[data-phase='active']")
  const conversationRect = conversation?.getBoundingClientRect()
  return {
    width: overlayRect.width,
    height: overlayRect.height,
    anchorRight: conversationRect === undefined
      ? overlayRect.width
      : Math.min(Math.max(conversationRect.right - overlayRect.left, 0), overlayRect.width),
  }
}

function hasActivity(snapshot: SachaActivitySnapshot | undefined): boolean {
  return snapshot !== undefined
    && (snapshot.events.length > 0 || snapshot.team.members.length > 0 || snapshot.team.tasks.length > 0)
}

/** Orchestration signals that may auto-open the panel once per session:
 *  committed Sacha events, dispatched teammates, or shared tasks. A lone
 *  conductor member (the native `role: 'lead'` entry) is ambient Agent Teams
 *  state, not orchestration. */
function hasOrchestration(snapshot: SachaActivitySnapshot): boolean {
  return snapshot.events.length > 0
    || snapshot.team.members.some(m => m.role === 'teammate')
    || snapshot.team.tasks.length > 0
}

function memberActivityTone(status: TeamMemberSnapshot['status']): 'working' | 'idle' | 'unknown' {
  if (status === 'running') return 'working'
  if (status === 'idle') return 'idle'
  return 'unknown'
}

function memberAccent(seed: string): string {
  let hash = 0
  for (let index = 0; index < seed.length; index += 1) hash = ((hash << 5) - hash + seed.charCodeAt(index)) | 0
  return Math.abs(hash).toString(16).padStart(6, '0').slice(0, 6)
}

function memberInitial(name: string): string {
  const first = name.trim().charAt(0)
  return first === '' ? '?' : first.toUpperCase()
}

function memberRoleLabel(member: TeamMemberSnapshot): string {
  if (member.role === 'lead') return '主任务 / 指挥'
  const description = member.description?.trim()
  if (description === undefined || description === '') return '委派 Agent'
  return description
}

function teamDisplayName(snapshot: SachaActivitySnapshot): string {
  const lead = snapshot.team.members.find(m => m.role === 'lead')
  if (lead !== undefined) return '乐团'
  if (snapshot.team.tasks.length > 0) return 'Agent 乐团'
  return '当前乐团'
}

function progressSummary(tasks: readonly TeamTaskSnapshot[]): { text: string; tone: 'running' | 'warning' | 'completed' | 'idle' } {
  const visible = tasks.filter(t => t.status !== 'deleted')
  if (visible.length === 0) return { text: '等待主任务拆解工作单元', tone: 'idle' }
  const completed = visible.filter(t => t.status === 'completed').length
  const running = visible.filter(t => t.status === 'in_progress').length
  const blocked = visible.filter(t => t.status === 'pending' && !t.ready).length
  if (completed === visible.length) return { text: `全部 ${completed} 项任务已交付`, tone: 'completed' }
  if (running > 0 && blocked > 0) return { text: `${running} 项执行中，${blocked} 项等待依赖`, tone: 'warning' }
  if (running > 0) return { text: `${running} 项正在执行`, tone: 'running' }
  if (blocked > 0) return { text: `${blocked} 项等待前置任务`, tone: 'warning' }
  return { text: `${visible.length} 项任务待领取`, tone: 'idle' }
}

function Chevron({ open }: { readonly open: boolean }): JSX.Element {
  return (
    <svg className={css.chevron} data-open={open} width="9" height="9" viewBox="0 0 10 10" fill="none"
      stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" aria-hidden>
      <path d="M3.5 2l3 3-3 3" />
    </svg>
  )
}

function WorkGlyph({ active }: { readonly active: boolean }): JSX.Element {
  return (
    <svg className={css.workGlyph} data-active={active} width="11" height="11" viewBox="0 0 11 11"
      fill="currentColor" aria-hidden>
      {[[0, 0], [4.2, 0], [8.4, 0], [0, 4.2], [4.2, 4.2], [8.4, 4.2]].map(([x, y], i) => (
        <rect key={`${x}:${y}`} x={x} y={y} width="2.6" height="2.6" rx=".6" style={{ animationDelay: `${i * 0.15}s` }} />
      ))}
    </svg>
  )
}

function CollapsedBadge({ count, busy, onClick }: {
  readonly count: number; readonly busy: boolean; readonly onClick: () => void
}): JSX.Element {
  return (
    <button type="button" className={css.badge} data-busy={busy || undefined} onClick={onClick}
      aria-label={`打开 Sacha 可视化（${count} 项事件）`}>
      <span className={css.badgeDot} data-busy={busy || undefined} aria-hidden />
      <span className={css.badgeCount}>S · {count}</span>
    </button>
  )
}

function IconPanelLeft(): JSX.Element {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.4"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <rect x="2.5" y="3" width="11" height="10" rx="1.5" />
      <line x1="6" y1="3" x2="6" y2="13" />
    </svg>
  )
}
function IconChevronDown(): JSX.Element {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d="M3 6l5 5 5-5" />
    </svg>
  )
}

/** Gate + review badges shared by the conductor card. */
function StateBadges({ state }: { readonly state: VisualState }): JSX.Element | null {
  const gates = (Object.entries(state.gates) as [SachaGate, VisualState['gates'][SachaGate]][])
    .filter((entry): entry is [SachaGate, NonNullable<VisualState['gates'][SachaGate]>] => entry[1] !== undefined)
  const review = state.review
  if (gates.length === 0 && review === undefined) return null
  return (
    <>
      {gates.length > 0 ? (
        <div className={css.sachaGates} role="group" aria-label="Gate 状态">
          {gates.map(([gate, value]) => (
            <span key={gate} className={css.sachaGate} data-decision={value.decision} title={value.summary}>
              <span className={css.sachaGateDot} />
              {GATE_LABEL[gate]} · {GATE_DECISION_LABEL[value.decision] ?? value.decision}
            </span>
          ))}
        </div>
      ) : null}
      {review !== undefined && review.eventType === 'review' ? (
        <span className={css.sachaReview} data-outcome={review.outcome} title={review.summary}>
          Review · {review.summary}
        </span>
      ) : null}
    </>
  )
}

/** The conductor card: the conductor cat always holds the baton; the
 *  workflow phase still drives the card state and summary line. */
function ConductorNode({ snapshot, runningCount, taskCount, assignedCount, teammateCount }: {
  readonly snapshot: SachaActivitySnapshot
  readonly runningCount: number
  readonly taskCount: number
  readonly assignedCount: number
  readonly teammateCount: number
}): JSX.Element {
  const phase = snapshot.state.phase
  const nodeState = phase === undefined ? 'waiting'
    : phase.state === 'blocked' ? 'blocked'
    : phase.state === 'completed' ? 'completed'
    : phase.state === 'waiting' ? 'waiting' : 'running'
  return (
    <div className={css.captainNode} data-state={nodeState}>
      <span className={css.captainAvatar} data-state={nodeState}>
        <CatArt kind={CONDUCTOR_CAT.kind} prop={CONDUCTOR_CAT.prop} size={44} />
      </span>
      <span className={css.captainInfo}>
        <span className={css.captainLine}>
          <strong className={css.captainName}>指挥</strong>
          <small className={css.captainRole}>拆解 · 派发 · 汇总</small>
        </span>
        <span className={css.captainSummary} title={phase?.summary}>
          {phase !== undefined
            ? phase.summary
            : teammateCount > 0 ? `已派发 ${assignedCount} 项任务给 ${teammateCount} 名成员` : '等待主任务派工'}
        </span>
      </span>
      <span className={css.captainState} data-busy={nodeState === 'running' || undefined} data-state={nodeState}>
        {phase !== undefined
          ? `${PHASE_LABEL[phase.phase]} · ${nodeState === 'running' ? '进行中' : nodeState === 'waiting' ? '等待中' : nodeState === 'blocked' ? '阻塞' : '已完成'}`
          : runningCount > 0 ? `${runningCount} 人执行中` : taskCount > 0 ? '已收齐' : '等待回报'}
      </span>
    </div>
  )
}

function ProgressOverview({ tasks }: { readonly tasks: readonly TeamTaskSnapshot[] }): JSX.Element {
  const visible = tasks.filter(t => t.status !== 'deleted')
  const completed = visible.filter(t => t.status === 'completed').length
  const running = visible.filter(t => t.status === 'in_progress').length
  const blocked = visible.filter(t => t.status === 'pending' && !t.ready).length
  const ready = visible.filter(t => t.status === 'pending' && t.ready).length
  const summary = progressSummary(visible)
  return (
    <section className={css.progressOverview} aria-label="团队总进度">
      <span className={css.progressTitle}>总进度</span>
      <span className={css.progressSegments} aria-hidden>
        {visible.length === 0
          ? <span className={css.progressEmpty} />
          : visible.map(t => <span key={t.id} data-state={t.status === 'in_progress' ? 'running' : t.status === 'completed' ? 'completed' : t.ready ? 'running' : 'blocked'} />)}
      </span>
      <span className={css.progressLegend}>
        <span data-state="running">■ 进行中 {running}</span>
        <span data-state="blocked">■ 等待 {blocked}</span>
        <span data-state="completed">■ 完成 {completed}</span>
        {ready > 0 ? <span data-state="running">■ 就绪 {ready}</span> : null}
      </span>
      <span className={css.progressSummary} data-state={summary.tone}>
        <span className={css.progressSummaryDot} />
        <span>{summary.text}</span>
      </span>
    </section>
  )
}

function DependencyMap({ tasks }: { readonly tasks: readonly TeamTaskSnapshot[] }): JSX.Element {
  const visible = tasks.filter(t => t.status !== 'deleted')
  const [open, setOpen] = useState(true)
  const [hovered, setHovered] = useState<string>()
  const [keyboard, setKeyboard] = useState<string>()
  const [pinned, setPinned] = useState<string>()
  const hoverTimer = useRef<ReturnType<typeof setTimeout>>()
  const focused = pinned ?? keyboard ?? hovered
  const layout = useMemo(() => compactDagLayout(visible), [visible])
  const related = useMemo(() => focused === undefined ? undefined : relatedTaskIds(focused, visible), [focused, visible])
  const parallel = visible.length > 0 && visible.every(t => t.blockedBy.length === 0)
  const fallback = visible.find(t => t.status === 'in_progress')
    ?? visible.find(t => t.status === 'pending' && !t.ready)
    ?? visible[0]
  const detail = visible.find(t => t.id === focused) ?? fallback
  const waitingOn = detail?.blockedBy.filter(id => visible.find(t => t.id === id)?.status !== 'completed') ?? []
  const dependents = detail === undefined ? [] : visible.filter(t => t.blockedBy.includes(detail.id))
  const scheduleHover = (id: string | undefined): void => {
    if (hoverTimer.current !== undefined) clearTimeout(hoverTimer.current)
    if (id === undefined) { setHovered(undefined); return }
    hoverTimer.current = setTimeout(() => { setHovered(id) }, 160)
  }
  useEffect(() => {
    const onKey = (e: KeyboardEvent): void => { if (e.key === 'Escape') setPinned(undefined) }
    window.addEventListener('keydown', onKey)
    return () => {
      window.removeEventListener('keydown', onKey)
      if (hoverTimer.current !== undefined) clearTimeout(hoverTimer.current)
    }
  }, [])
  if (visible.length === 0) return <p className={css.emptyHint}>暂无任务。</p>

  const toneFor = (task: TeamTaskSnapshot): 'running' | 'completed' | 'blocked' | 'failed' | 'pending' => {
    if (task.status === 'completed') return 'completed'
    if (task.status === 'in_progress') return 'running'
    if (task.status === 'pending' && task.ready) return 'running'
    return 'blocked'
  }

  const renderNode = (task: TeamTaskSnapshot, position?: { x: number; y: number }): JSX.Element => (
    <button
      type="button" key={task.id} className={css.dagNode}
      style={position === undefined ? { height: NODE_HEIGHT } : { left: position.x, top: position.y, width: NODE_WIDTH, height: NODE_HEIGHT }}
      data-state={toneFor(task)}
      data-focused={related?.has(task.id) || undefined}
      data-dimmed={related !== undefined && !related.has(task.id) || undefined}
      aria-pressed={pinned === task.id}
      title={`${task.id} · ${task.subject}`}
      onClick={() => { setPinned(current => current === task.id ? undefined : task.id) }}
      onMouseEnter={() => { scheduleHover(task.id) }}
      onMouseLeave={() => { scheduleHover(undefined) }}
      onFocus={() => { setKeyboard(task.id) }}
      onBlur={() => { setKeyboard(undefined) }}
    >
      <span className={css.dagNodeHead}>
        <span className={css.dagNodeDot} />
        {task.id}
        {toneFor(task) === 'running' ? <span className={css.dagRunningState}><WorkGlyph active /></span> : null}
      </span>
      <span className={css.dagNodeLabel}>{task.subject}</span>
    </button>
  )

  return (
    <section className={css.dependencySection} aria-label="任务依赖">
      <header className={css.sectionHead}>
        <button type="button" className={css.sectionToggleTitle} onClick={() => { setOpen(c => !c) }} aria-expanded={open}>
          <Chevron open={open} />
          {parallel ? '并行任务' : '任务依赖'}
        </button>
        <small className={css.sectionHint}>
          {pinned === undefined ? '悬停高亮 · 点击固定' : `${pinned} 已固定 · Esc 取消`}
        </small>
      </header>
      {open && (
        <>
          <div className={css.dagViewport}>
            <div className={css.dagCanvas} data-layout={parallel ? 'parallel' : 'dependency'}
              style={parallel ? undefined : { width: layout.width, height: layout.height }}>
              {!parallel && (
                <svg className={css.dagEdges} width={layout.width} height={layout.height} aria-hidden>
                  {layout.edges.map(edge => {
                    const highlighted = related?.has(edge.from) === true && related.has(edge.to)
                    return (
                      <path key={`${edge.from}:${edge.to}`} d={edge.path}
                        data-active={highlighted || undefined}
                        data-dimmed={related !== undefined && !highlighted || undefined} />
                    )
                  })}
                </svg>
              )}
              {parallel
                ? visible.map(t => renderNode(t))
                : layout.nodes.map(n => renderNode(n.task, n))}
            </div>
          </div>
          {detail !== undefined && (
            <section className={css.taskDetail} data-state={toneFor(detail)}>
              <span className={css.taskDetailHead}>
                <code className={css.taskDetailId}>{detail.id}</code>
                <strong className={css.taskDetailSubject} title={detail.subject}>{detail.subject}</strong>
                <span className={css.taskDetailBadge} data-state={toneFor(detail)}>
                  {detail.status === 'completed' ? '已完成' : detail.status === 'in_progress' ? '进行中' : detail.ready ? '就绪' : '等待依赖'}
                </span>
              </span>
              <span className={css.taskDetailMeta}>
                {detail.ownerName ?? '未分配'} · revision {detail.revision}
              </span>
              <span className={css.taskDetailLine}>
                {detail.status === 'completed' ? '任务已经完成并交付'
                  : detail.status === 'in_progress' ? '任务正在执行'
                  : waitingOn.length > 0 ? `等待 ${waitingOn.join('、')}`
                  : '前置已满足，可执行'}
              </span>
              <span className={css.taskDetailLine}>
                {dependents.length > 0 ? `完成后解锁 ${dependents.map(t => t.id).join('、')}` : '无下游任务'}
              </span>
              {detail.writeScopes.length > 0 ? (
                <span className={css.taskDetailLine}>写入范围：{detail.writeScopes.join('、')}</span>
              ) : null}
              {detail.writeScopeWarnings.length > 0 ? (
                <span className={css.taskDetailLine} style={{ color: 'var(--dsw-alias-state-warning)' }}>
                  {detail.writeScopeWarnings.join('；')}
                </span>
              ) : null}
            </section>
          )}
        </>
      )}
    </section>
  )
}

function TeamSection({ snapshot }: { readonly snapshot: SachaActivitySnapshot }): JSX.Element {
  const [membersOpen, setMembersOpen] = useState(true)
  const tasks = snapshot.team.tasks
  const visibleTasks = tasks.filter(t => t.status !== 'deleted')
  const members = snapshot.team.members
  const teammates = members.filter(m => m.role === 'teammate')
  const lead = members.find(m => m.role === 'lead')
  const runningCount = teammates.filter(m => m.status === 'running').length
  const completedCount = visibleTasks.filter(t => t.status === 'completed').length
  return (
    <section className={css.team} aria-label="Agent 乐团">
      <header className={css.teamHead}>
        <span className={css.teamName}>{teamDisplayName(snapshot)}</span>
        <span className={css.teamStats}>
          <span><span className={css.statDot} style={{ background: 'var(--dsw-alias-state-business-primary)' }} />{teammates.length} 成员</span>
          <span><span className={css.statDot} style={{ background: 'var(--dsw-alias-state-success)' }} />{completedCount}/{visibleTasks.length} 完成</span>
          {runningCount > 0 ? <span style={{ color: 'var(--dsw-alias-state-business-primary)' }}>{runningCount} 人执行中</span> : null}
        </span>
      </header>

      <section className={css.delegationSection} aria-label="指挥与成员">
        <ConductorNode snapshot={snapshot} runningCount={runningCount} taskCount={visibleTasks.length} assignedCount={visibleTasks.filter(t => t.ownerName !== undefined).length} teammateCount={teammates.length} />
        <StateBadges state={snapshot.state} />
        <ProgressOverview tasks={visibleTasks} />
        {teammates.length > 0 ? (
          <>
            <button type="button" className={css.membersToggle} onClick={() => { setMembersOpen(c => !c) }} aria-expanded={membersOpen}>
              <span><Chevron open={membersOpen} />Role / 成员 {teammates.length}</span>
              <span>{membersOpen ? '收起' : '展开'}</span>
            </button>
            {membersOpen && (
              <div className={css.delegationTree}>
                {teammates.map(member => {
                  const owned = visibleTasks.filter(t => t.ownerName === member.name)
                  const completed = owned.filter(t => t.status === 'completed').length
                  const tone = memberActivityTone(member.status)
                  const prop = memberCatProp(member)
                  return (
                    <div key={member.id} className={css.memberBlock} data-status={member.status}>
                      <span className={css.memberBranch} aria-hidden />
                      <button type="button" className={css.memberRow} data-activity={tone}>
                        <span className={css.memberAvatar} data-status={member.status}>
                          {prop === undefined
                            ? <span className={css.memberInitial} style={{ background: `#${memberAccent(member.id)}` }}>{memberInitial(member.name)}</span>
                            : <CatArt kind={MEMBER_CAT.kind} prop={prop} size={40} />}
                          <span className={css.stateArt} data-status={member.status}>
                            <MemberStatusArt status={member.status} size={18} />
                          </span>
                        </span>
                        <span className={css.memberInfo}>
                          <span className={css.memberLine}>
                            <strong className={css.memberName}>{member.name}</strong>
                            <small className={css.memberRole}>{memberRoleLabel(member)}</small>
                          </span>
                          <span className={css.memberStatusLine}>{member.description ?? '等待主任务派工'}</span>
                        </span>
                        <span className={css.memberState} data-activity={tone}>{MEMBER_STATUS_LABEL[member.status]}</span>
                      </button>
                      <div className={css.assignmentLine}>
                        <span className={css.assignmentLabel}>指挥派发</span>
                        <span className={css.assignmentTasks}>
                          {owned.length === 0
                            ? <em className={css.taskEmpty}>暂无任务</em>
                            : owned.map(t => (
                              <span key={t.id} className={css.assignmentChip} data-state={t.status === 'completed' ? 'completed' : t.status === 'in_progress' ? 'running' : t.ready ? 'running' : 'blocked'}>
                                {t.id}
                              </span>
                            ))}
                        </span>
                      </div>
                      {owned.length > 0 ? <span className={css.memberCount} style={{ alignSelf: 'flex-end' }}>{completed}/{owned.length}</span> : null}
                    </div>
                  )
                })}
              </div>
            )}
          </>
        ) : null}
      </section>

      <DependencyMap tasks={visibleTasks} />
    </section>
  )
}

export function ActivityPanel({ sessionsList }: { readonly sessionsList: ObservableSnapshot<SessionListState> }): JSX.Element | null {
  const current = useSyncExternalStore(sessionsList.subscribe, sessionsList.getSnapshot).current
  const snapshot = useSachaActivity(current)
  const active = hasActivity(snapshot)
  const [open, setOpen] = useState(false)
  const [autoOpenedFor, setAutoOpenedFor] = useState<string>()
  const [dismissedSessions, setDismissedSessions] = useState<Set<string>>(initialDismissedSessions)
  const [layout, setLayout] = useState<PanelLayout>(initialPanelLayout)
  const [bounds, setBounds] = useState<PanelBounds>(initialBounds)
  const [interaction, setInteraction] = useState<'dragging' | 'resizing'>()
  const hostRef = useRef<HTMLElement | null>(null)
  const panelRef = useRef<HTMLElement | null>(null)
  const geometry = useMemo(() => resolvePanelLayout(layout, bounds), [layout, bounds])
  const layoutRef = useRef(geometry)
  const boundsRef = useRef(bounds)
  const gestureRef = useRef<PanelGesture>()
  useEffect(() => { layoutRef.current = geometry }, [geometry])
  useEffect(() => { boundsRef.current = bounds }, [bounds])
  useLayoutEffect(() => {
    // Observe both the overlay and the conversation column so bounds stay
    // correct while side plugins open/close and the conversation yields.
    const overlay = document.querySelector<HTMLElement>('[data-shell-overlay]')
    const conversation = document.querySelector<HTMLElement>("[data-phase='active']")
    let frame: number | null = null
    const apply = (): void => {
      frame = null
      const measured = measureShellBounds()
      if (measured === undefined) return
      const previous = boundsRef.current
      if (previous.width === measured.width
        && previous.height === measured.height
        && previous.anchorRight === measured.anchorRight) return
      boundsRef.current = measured
      setBounds(measured)
    }
    const schedule = (): void => { frame ??= requestAnimationFrame(apply) }
    apply()
    const observer = typeof ResizeObserver === 'undefined' ? null : new ResizeObserver(schedule)
    if (overlay !== null) observer?.observe(overlay)
    if (conversation !== null) observer?.observe(conversation)
    window.addEventListener('resize', schedule)
    return () => {
      if (frame !== null) cancelAnimationFrame(frame)
      observer?.disconnect()
      window.removeEventListener('resize', schedule)
    }
  }, [current])
  // Every session starts collapsed; the panel auto-opens once when Sacha
  // orchestration arrives, unless the Human has dismissed this session
  // before. Dismissal is persisted per session, so a refresh or a
  // switch-away-and-back never pops the panel open again.
  const orchestration = snapshot !== undefined && hasOrchestration(snapshot)
  useEffect(() => {
    if (!orchestration || current === undefined) return
    if (autoOpenedFor === current || dismissedSessions.has(current)) return
    setOpen(true); setAutoOpenedFor(current)
  }, [orchestration, autoOpenedFor, current, dismissedSessions])

  // Switching sessions resets the panel to its per-session default: collapsed.
  useEffect(() => {
    setOpen(false)
  }, [current])
  useLayoutEffect(() => {
    const root = document.documentElement
    const shifted = open && active && !compactPanel(bounds) && geometry.mode === 'docked'
    if (shifted) { root.setAttribute(PANEL_OPEN_ATTRIBUTE, ''); root.style.setProperty(PANEL_SHIFT_PROPERTY, `${geometry.width + 34}px`) }
    else { root.removeAttribute(PANEL_OPEN_ATTRIBUTE); root.style.removeProperty(PANEL_SHIFT_PROPERTY) }
    return () => { root.removeAttribute(PANEL_OPEN_ATTRIBUTE); root.style.removeProperty(PANEL_SHIFT_PROPERTY) }
  }, [active, bounds, geometry.mode, geometry.width, open])
  const commitLayout = useCallback((next: PanelLayout): void => {
    const resolved = resolvePanelLayout(next, boundsRef.current)
    layoutRef.current = resolved; setLayout(resolved)
    window.localStorage.setItem(PANEL_LAYOUT_STORAGE_KEY, JSON.stringify(resolved))
  }, [])
  const panelGeometryForGesture = useCallback((): PanelLayout => {
    const measured = panelRef.current?.getBoundingClientRect().height
    if (measured === undefined || measured <= 0) return geometry
    return { ...geometry, height: measured }
  }, [geometry])
  const beginMove = useCallback((event: ReactPointerEvent<HTMLElement>): void => {
    if (compactPanel(boundsRef.current) || (event.target as HTMLElement).closest('button') !== null) return
    gestureRef.current = { kind: 'move', pointerId: event.pointerId, originX: event.clientX, originY: event.clientY, start: panelGeometryForGesture(), activated: false }
    event.currentTarget.setPointerCapture(event.pointerId)
  }, [panelGeometryForGesture])
  const beginResize = useCallback((edge: PanelResizeEdge, event: ReactPointerEvent<HTMLElement>): void => {
    if (compactPanel(boundsRef.current)) return
    event.stopPropagation()
    gestureRef.current = { kind: 'resize', edge, pointerId: event.pointerId, originX: event.clientX, originY: event.clientY, start: panelGeometryForGesture(), activated: true }
    setInteraction('resizing'); event.currentTarget.setPointerCapture(event.pointerId)
  }, [panelGeometryForGesture])
  const updateGesture = useCallback((event: ReactPointerEvent<HTMLElement>): void => {
    const gesture = gestureRef.current
    if (gesture === undefined || gesture.pointerId !== event.pointerId) return
    const dx = event.clientX - gesture.originX; const dy = event.clientY - gesture.originY
    if (!gesture.activated && Math.hypot(dx, dy) < MOVE_THRESHOLD) return
    if (!gesture.activated) { gesture.activated = true; setInteraction('dragging') }
    const next = gesture.kind === 'move' ? movePanel(gesture.start, dx, dy, boundsRef.current) : resizePanel(gesture.start, gesture.edge ?? 'corner', dx, dy, boundsRef.current)
    layoutRef.current = next; setLayout(next)
  }, [])
  const endGesture = useCallback((event: ReactPointerEvent<HTMLElement>): void => {
    const gesture = gestureRef.current
    if (gesture === undefined || gesture.pointerId !== event.pointerId) return
    updateGesture(event)
    if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId)
    gestureRef.current = undefined; setInteraction(undefined); commitLayout(layoutRef.current)
  }, [commitLayout, updateGesture])
  const cancelGesture = useCallback((event: ReactPointerEvent<HTMLElement>): void => {
    if (gestureRef.current?.pointerId !== event.pointerId) return
    gestureRef.current = undefined; setInteraction(undefined); commitLayout(layoutRef.current)
  }, [commitLayout])
  const toggleDock = useCallback((): void => {
    const live = panelGeometryForGesture()
    commitLayout(live.mode === 'docked' ? floatPanel(live, boundsRef.current) : dockPanel(live, boundsRef.current))
  }, [commitLayout, panelGeometryForGesture])
  if (!active || snapshot === undefined) return null
  const busy = snapshot.team.members.some(m => m.status === 'running')
  if (!open) {
    return <CollapsedBadge count={snapshot.events.length} busy={busy} onClick={() => { setOpen(true) }} />
  }
  const compact = compactPanel(bounds)
  const autoHeight = panelUsesAutoHeight(geometry, bounds)
  const panelStyle: CSSProperties = {
    width: geometry.width,
    height: autoHeight ? 'auto' : geometry.height,
    maxHeight: panelMaximumHeight(geometry, bounds),
    transform: `translate3d(${geometry.x}px, ${geometry.y}px, 0)`,
  }
  return (
    <aside
      ref={(node) => { panelRef.current = node; hostRef.current = node?.parentElement ?? null }}
      className={css.panel}
      style={panelStyle}
      aria-label="Sacha 多智能体编排可视化"
      data-sacha-visualizer
      data-mode={geometry.mode}
      data-height-mode={autoHeight ? 'auto' : 'manual'}
      data-compact={compact || undefined}
      data-dragging={interaction === 'dragging' || undefined}
      data-resizing={interaction === 'resizing' || undefined}
    >
      <header
        className={css.panelHead}
        onPointerDown={beginMove}
        onPointerMove={updateGesture}
        onPointerUp={endGesture}
        onPointerCancel={cancelGesture}
        data-drag-handle={!compact || undefined}
      >
        <span className={css.panelTitle}>
          Sacha 编排
          <span className={css.panelDot} data-busy={busy || undefined} aria-hidden />
        </span>
        <span className={css.panelControls}>
          {!compact && (
            <button type="button" className={css.iconButton} data-control="dock" data-mode={geometry.mode}
              onClick={toggleDock}
              aria-label={geometry.mode === 'docked' ? '切换为浮动面板' : '停靠到右侧'}
              title={geometry.mode === 'docked' ? '切换为浮动面板' : '停靠到右侧'}>
              <IconPanelLeft />
            </button>
          )}
          <button type="button" className={css.iconButton} data-control="collapse"
            onClick={() => {
              setOpen(false)
              if (current === undefined) return
              setDismissedSessions(prev => {
                if (prev.has(current)) return prev
                const next = new Set(dismissSession([...prev], current))
                window.localStorage.setItem(PANEL_DISMISSED_KEY, JSON.stringify([...next]))
                return next
              })
            }}
            aria-label="收起 Sacha 可视化"
            title="收起 Sacha 可视化">
            <IconChevronDown />
          </button>
        </span>
      </header>
      <div className={css.teams}>
        {snapshot.team.available
          ? <TeamSection snapshot={snapshot} />
          : (
            <section className={css.team} aria-label="Agent 乐团">
              <section className={css.delegationSection} aria-label="指挥与成员">
                <ConductorNode snapshot={snapshot} runningCount={0} taskCount={0} assignedCount={0} teammateCount={0} />
                <StateBadges state={snapshot.state} />
              </section>
              <p className={css.emptyHint}>当前 Profile 未组合官方 Agent Teams，或当前 Session 不是 Team member。</p>
            </section>
          )}
        {snapshot.warnings.length > 0 ? (
          <section className={css.sachaCard}>
            <span className={css.sachaSummary}>{snapshot.warnings.join('；')}</span>
          </section>
        ) : null}
      </div>
      {!compact && (
        <div className={css.resizeHandle} data-resize-edge="left"
          onPointerDown={(e) => { beginResize('left', e) }}
          onPointerMove={updateGesture}
          onPointerUp={endGesture}
          onPointerCancel={cancelGesture}
          aria-hidden />
      )}
      {!compact && geometry.mode === 'floating' && (
        <>
          <div className={css.resizeHandle} data-resize-edge="bottom"
            onPointerDown={(e) => { beginResize('bottom', e) }}
            onPointerMove={updateGesture}
            onPointerUp={endGesture}
            onPointerCancel={cancelGesture}
            aria-hidden />
          <div className={css.resizeHandle} data-resize-edge="corner"
            onPointerDown={(e) => { beginResize('corner', e) }}
            onPointerMove={updateGesture}
            onPointerUp={endGesture}
            onPointerCancel={cancelGesture}
            aria-hidden />
        </>
      )}
    </aside>
  )
}
