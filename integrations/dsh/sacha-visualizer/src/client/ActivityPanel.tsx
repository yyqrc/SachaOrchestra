/** Session-scoped Sacha workflow, evidence, roster, and task-DAG panel. */

import {
  useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState, useSyncExternalStore,
  type CSSProperties, type PointerEvent as ReactPointerEvent,
} from 'react'
import type { ObservableSnapshot, SessionListState } from '@deepseek-ai/dsh-client-runtime/client'
import { compactDagLayout, NODE_HEIGHT, NODE_WIDTH, relatedTaskIds } from './activity-model.ts'
import { useSachaActivity } from './activity-monitor.ts'
import { ACTION_ART, LEAD_ART, memberArtUrl } from './artwork.ts'
import {
  DEFAULT_PANEL_LAYOUT, PANEL_LAYOUT_STORAGE_KEY, compactPanel, dockPanel, floatPanel, movePanel,
  panelMaximumHeight, panelUsesAutoHeight, parsePanelLayout, resizePanel, resolvePanelLayout,
  type PanelBounds, type PanelLayout, type PanelResizeEdge,
} from './panel-geometry.ts'
import type {
  EvidenceLayer, SachaActivitySnapshot, SachaGate, SachaPhase, TeamMemberSnapshot, TeamTaskSnapshot,
} from '../types.ts'
import css from './ActivityPanel.module.css'

const PANEL_OPEN_ATTRIBUTE = 'data-sacha-panel-open'
const PANEL_SHIFT_PROPERTY = '--sacha-panel-shift'
const MOVE_THRESHOLD = 4
const PHASE_LABEL: Record<SachaPhase, string> = {
  intake: '入口判断', direct: '直接执行', planner: '规划', explore: '探索', executor: '实施', reviewer: '独立评审',
  roadmap: '路线图', 'document-project': '项目文档', closeout: '收口', feedback: '反馈移交',
  'human-decision': '等待 Human 决定', complete: '完成', blocked: '阻塞',
}
const GATE_LABEL: Record<SachaGate, string> = { planner: 'Planner Gate', manager: 'Manager Gate', reviewer: 'Reviewer Gate' }
const EVIDENCE_LABEL: Record<EvidenceLayer, string> = {
  source: '源码/静态', package: '包/安装', runtime: 'Runtime', human: 'Human 验收',
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

function taskTone(task: TeamTaskSnapshot): string {
  if (task.status === 'completed') return 'completed'
  if (task.status === 'in_progress') return 'running'
  return task.ready ? 'ready' : 'blocked'
}

function taskStatusLabel(task: TeamTaskSnapshot): string {
  if (task.status === 'completed') return '已完成'
  if (task.status === 'in_progress') return '进行中'
  if (task.status === 'deleted') return '已删除'
  return task.ready ? '已就绪' : '等待依赖'
}

function memberStatusLabel(member: TeamMemberSnapshot): string {
  switch (member.status) {
    case 'running': return '工作中'
    case 'idle': return '空闲'
    case 'inactive': return '未激活'
    case 'provisioning': return '创建中'
    case 'failed': return '失败'
  }
}

function stableHash(value: string): number {
  let hash = 0
  for (let index = 0; index < value.length; index += 1) hash = ((hash << 5) - hash + value.charCodeAt(index)) | 0
  return Math.abs(hash)
}

const MEMBER_ACCENTS = ['#4d6bfe', '#7c5ce7', '#07966b', '#ca6f1e', '#d44747'] as const
function memberAccent(id: string): string {
  return MEMBER_ACCENTS[stableHash(id) % MEMBER_ACCENTS.length] ?? MEMBER_ACCENTS[0]
}

function memberInitial(name: string): string {
  return name.trim().slice(0, 1).toUpperCase() || '?'
}

function roleLabel(member: TeamMemberSnapshot): string {
  if (member.role === 'lead') return '主任务 / Lead'
  const description = member.description?.trim()
  if (description === undefined || description === '') return '委派 Agent'
  const lower = description.toLowerCase()
  if (lower.includes('planner')) return 'Planner'
  if (lower.includes('reviewer')) return 'Reviewer'
  if (lower.includes('executor')) return 'Executor'
  if (lower.includes('explore') || lower.includes('research')) return 'Explore'
  return description
}

function taskSummary(tasks: readonly TeamTaskSnapshot[]): { text: string; tone: string } {
  if (tasks.length === 0) return { text: '等待主任务拆解工作单元', tone: 'idle' }
  const completed = tasks.filter(task => task.status === 'completed')
  const running = tasks.filter(task => task.status === 'in_progress')
  const blocked = tasks.filter(task => task.status === 'pending' && !task.ready)
  const ready = tasks.filter(task => task.status === 'pending' && task.ready)
  if (completed.length === tasks.length) return { text: `全部 ${completed.length} 项任务已交付`, tone: 'completed' }
  if (running.length > 0 && blocked.length > 0) return { text: `${running.length} 项执行中，${blocked.length} 项等待依赖`, tone: 'warning' }
  if (running.length > 0) return { text: `${running.map(task => task.id).join('、')} 正在执行`, tone: 'running' }
  if (ready.length > 0) return { text: `${ready.map(task => task.id).join('、')} 已就绪`, tone: 'ready' }
  return { text: `${blocked.length} 项等待前置任务`, tone: 'warning' }
}

function ProgressOverview({ tasks }: { readonly tasks: readonly TeamTaskSnapshot[] }) {
  const visible = tasks.filter(task => task.status !== 'deleted')
  const completed = visible.filter(task => task.status === 'completed').length
  const running = visible.filter(task => task.status === 'in_progress').length
  const blocked = visible.filter(task => task.status === 'pending' && !task.ready).length
  const ready = visible.filter(task => task.status === 'pending' && task.ready).length
  const summary = taskSummary(visible)
  return (
    <section className={css.progressOverview} aria-label="团队总进度">
      <span className={css.progressTitle}>总进度</span>
      <span className={css.progressSegments} aria-hidden>
        {visible.length === 0 ? <span data-tone="empty" /> : visible.map(task => <span key={task.id} data-tone={taskTone(task)} />)}
      </span>
      <span className={css.progressLegend}>
        <span data-tone="running">■ 进行中 {running}</span><span data-tone="ready">■ 就绪 {ready}</span>
        <span data-tone="blocked">■ 等待 {blocked}</span><span data-tone="completed">■ 完成 {completed}</span>
      </span>
      <span className={css.progressSummary} data-tone={summary.tone}><span className={css.progressDot} />{summary.text}</span>
    </section>
  )
}

function DependencyMap({ tasks }: { readonly tasks: readonly TeamTaskSnapshot[] }) {
  const visible = tasks.filter(task => task.status !== 'deleted')
  const [open, setOpen] = useState(true)
  const [hovered, setHovered] = useState<string>()
  const [keyboard, setKeyboard] = useState<string>()
  const [pinned, setPinned] = useState<string>()
  const hoverTimer = useRef<ReturnType<typeof setTimeout>>()
  const focused = pinned ?? keyboard ?? hovered
  const layout = useMemo(() => compactDagLayout(visible), [visible])
  const related = useMemo(() => focused === undefined ? undefined : relatedTaskIds(focused, visible), [focused, visible])
  const parallel = visible.length > 0 && visible.every(task => task.blockedBy.length === 0)
  const fallback = visible.find(task => task.status === 'in_progress')
    ?? visible.find(task => task.status === 'pending' && !task.ready)
    ?? visible[0]
  const detail = visible.find(task => task.id === focused) ?? fallback
  const waitingOn = detail?.blockedBy.filter(id => visible.find(task => task.id === id)?.status !== 'completed') ?? []
  const dependents = detail === undefined ? [] : visible.filter(task => task.blockedBy.includes(detail.id))
  const scheduleHover = (id: string | undefined): void => {
    if (hoverTimer.current !== undefined) clearTimeout(hoverTimer.current)
    if (id === undefined) { setHovered(undefined); return }
    hoverTimer.current = setTimeout(() => { setHovered(id) }, 160)
  }
  useEffect(() => {
    const onKey = (event: KeyboardEvent): void => { if (event.key === 'Escape') setPinned(undefined) }
    window.addEventListener('keydown', onKey)
    return () => {
      window.removeEventListener('keydown', onKey)
      if (hoverTimer.current !== undefined) clearTimeout(hoverTimer.current)
    }
  }, [])
  if (visible.length === 0) return <p className={css.empty}>暂无官方 Agent Teams 任务。</p>
  const renderNode = (task: TeamTaskSnapshot, position?: { x: number; y: number }) => (
    <button
      type="button" key={task.id} className={css.dagNode}
      style={position === undefined ? { height: NODE_HEIGHT } : { left: position.x, top: position.y, width: NODE_WIDTH, height: NODE_HEIGHT }}
      data-tone={taskTone(task)} data-focused={related?.has(task.id) || undefined}
      data-dimmed={related !== undefined && !related.has(task.id) || undefined} aria-pressed={pinned === task.id}
      title={`${task.id} · ${task.subject}`} onClick={() => { setPinned(current => current === task.id ? undefined : task.id) }}
      onMouseEnter={() => { scheduleHover(task.id) }} onMouseLeave={() => { scheduleHover(undefined) }}
      onFocus={() => { setKeyboard(task.id) }} onBlur={() => { setKeyboard(undefined) }}
    >
      <span className={css.taskHead}><span className={css.taskDot} />{task.id}</span>
      <span className={css.taskSubject}>{task.subject}</span>
      <span className={css.taskOwner}>{task.ownerName ?? (task.ready ? '待领取' : '等待依赖')}</span>
    </button>
  )
  return (
    <section className={css.dependencySection}>
      <header className={css.sectionHeader}>
        <button type="button" onClick={() => { setOpen(current => !current) }} aria-expanded={open}>
          <span className={css.chevron} data-open={open}>›</span>{parallel ? '并行任务' : '任务依赖'}
        </button>
        <small>{pinned === undefined ? '悬停高亮 · 点击固定' : `${pinned} 已固定 · Esc 取消`}</small>
      </header>
      {open && <>
        <div className={css.dagViewport}>
          <div className={css.dagCanvas} data-layout={parallel ? 'parallel' : 'dependency'} style={parallel ? undefined : { width: layout.width, height: layout.height }}>
            {!parallel && <svg className={css.dagEdges} width={layout.width} height={layout.height} aria-hidden>
              {layout.edges.map(edge => {
                const highlighted = related?.has(edge.from) === true && related.has(edge.to)
                return <path key={`${edge.from}:${edge.to}`} d={edge.path} data-highlighted={highlighted || undefined} data-dimmed={related !== undefined && !highlighted || undefined} />
              })}
            </svg>}
            {parallel ? visible.map(task => renderNode(task)) : layout.nodes.map(node => renderNode(node.task, node))}
          </div>
        </div>
        {detail !== undefined && <section className={css.taskDetail} data-tone={taskTone(detail)}>
          <span className={css.taskDetailHead}><code>{detail.id}</code><strong title={detail.subject}>{detail.subject}</strong><span>{taskStatusLabel(detail)}</span></span>
          <span>{detail.ownerName ?? '未分配'} · revision {detail.revision}</span>
          <span>{detail.status === 'completed'
            ? '任务已经完成并交付'
            : detail.status === 'in_progress'
              ? '任务正在执行'
              : waitingOn.length > 0
                ? `等待 ${waitingOn.join('、')}`
                : '前置已满足，可执行'}</span>
          <span>{dependents.length > 0 ? `完成后解锁 ${dependents.map(task => task.id).join('、')}` : '无下游任务'}</span>
          {detail.writeScopes.length > 0 && <span>写入范围：{detail.writeScopes.join('、')}</span>}
          {detail.writeScopeWarnings.length > 0 && <span className={css.taskWarning}>{detail.writeScopeWarnings.join('；')}</span>}
        </section>}
      </>}
    </section>
  )
}

function DelegationTree({ snapshot }: { readonly snapshot: SachaActivitySnapshot }) {
  const [open, setOpen] = useState(true)
  const tasks = snapshot.team.tasks.filter(task => task.status !== 'deleted')
  const members = snapshot.team.members
  const lead = members.find(member => member.role === 'lead')
  const teammates = members.filter(member => member.role === 'teammate')
  const running = teammates.filter(member => member.status === 'running').length
  const assigned = tasks.filter(task => task.ownerName !== undefined).length
  return (
    <section className={css.delegationSection}>
      <div className={css.leadNode}>
        <span className={css.leadAvatar}><img className={css.leadArt} src={LEAD_ART} alt="" aria-hidden /></span>
        <span className={css.leadInfo}>
          <span><strong>{lead?.name ?? '主任务'}</strong><small>Lead · 拆解 · 派发 · 汇总</small></span>
          <span>已派发 {assigned} 项任务给 {teammates.length} 名成员</span>
        </span>
        <span className={css.leadState} data-busy={running > 0}>{running > 0 ? `${running} 人执行中` : tasks.length > 0 && tasks.every(task => task.status === 'completed') ? '已收齐' : '等待回报'}</span>
      </div>
      <ProgressOverview tasks={tasks} />
      <button type="button" className={css.membersToggle} onClick={() => { setOpen(current => !current) }} aria-expanded={open}>
        <span><span className={css.chevron} data-open={open}>›</span>Role / 成员 {teammates.length}</span><span>{open ? '收起' : '展开'}</span>
      </button>
      {open && <div className={css.delegationTree}>
        {teammates.length === 0 && <p className={css.empty}>暂无 teammate；Sacha 流程仍可只在主任务中运行。</p>}
        {teammates.map(member => {
          const owned = tasks.filter(task => task.ownerName === member.name)
          const completed = owned.filter(task => task.status === 'completed').length
          const roleArt = memberArtUrl(member)
          return <div key={member.id} className={css.memberBlock} data-status={member.status}>
            <span className={css.memberBranch} aria-hidden />
            <div className={css.memberRow}>
              <span className={css.memberAvatar}>
                {roleArt === null
                  ? <span className={css.memberInitial} style={{ background: memberAccent(member.id) }}>{memberInitial(member.name)}</span>
                  : <img className={css.memberArt} src={roleArt} alt="" aria-hidden />}
                <img className={css.memberAction} data-status={member.status} src={ACTION_ART[member.status]} alt="" aria-hidden />
              </span>
              <span className={css.memberInfo}><span><strong>{member.name}</strong><small>{roleLabel(member)}</small></span><span>{member.description ?? '等待主任务派工'}</span></span>
              <span className={css.memberState} data-status={member.status}>{memberStatusLabel(member)}</span>
              <span className={css.memberCount}>{completed}/{owned.length}</span>
            </div>
            <div className={css.assignmentLine}>
              <span>Lead 派发</span><span>{owned.length === 0 ? <em>暂无任务</em> : owned.map(task => <span key={task.id} data-tone={taskTone(task)} title={task.subject}>{task.id}</span>)}</span>
            </div>
          </div>
        })}
      </div>}
    </section>
  )
}

function WorkflowSection({ snapshot }: { readonly snapshot: SachaActivitySnapshot }) {
  const phase = snapshot.state.phase
  return <section className={css.section}>
    <h3>当前流程</h3>
    <div className={css.phaseCard} data-state={phase?.state ?? 'unknown'}>
      <span className={css.phaseName}>{phase === undefined ? '尚未记录' : PHASE_LABEL[phase.phase]}</span>
      <span className={css.phaseSummary}>{phase?.summary ?? '等待 Sacha DSH Adapter 记录已提交转换。'}</span>
      {phase?.scopeRevision !== undefined && <code>{phase.scopeRevision}</code>}
    </div>
    <div className={css.gates}>{(Object.keys(GATE_LABEL) as SachaGate[]).map(gate => {
      const value = snapshot.state.gates[gate]
      return <span key={gate} data-decision={value?.decision ?? 'unknown'} title={value?.summary}>{GATE_LABEL[gate]} · {value?.decision === 'open' ? '开' : value?.decision === 'closed' ? '关' : '未记录'}</span>
    })}</div>
    {snapshot.state.review !== undefined && <div className={css.review} data-outcome={snapshot.state.review.outcome}><strong>Review</strong><span>{snapshot.state.review.outcome}</span><small>{snapshot.state.review.summary}</small></div>}
  </section>
}

function EvidenceSection({ snapshot }: { readonly snapshot: SachaActivitySnapshot }) {
  return <section className={css.section}><h3>证据层</h3><div className={css.evidenceGrid}>
    {(Object.keys(EVIDENCE_LABEL) as EvidenceLayer[]).map(layer => {
      const value = snapshot.state.evidence[layer]
      return <div key={layer} data-status={value?.status ?? 'unverified'} title={value?.references.join('\n')}><strong>{EVIDENCE_LABEL[layer]}</strong><span>{value?.status ?? 'unverified'}</span><small>{value?.summary ?? '尚无记录'}</small></div>
    })}
  </div></section>
}

function TeamSection({ snapshot }: { readonly snapshot: SachaActivitySnapshot }) {
  return <section className={css.section}><h3>DSH Agent Team</h3>
    {!snapshot.team.available && <p className={css.empty}>当前 Profile 未组合官方 experimental Agent Teams，或当前 Session 不是 Team member。</p>}
    {snapshot.team.available && <DelegationTree snapshot={snapshot} />}
    <DependencyMap tasks={snapshot.team.tasks} />
  </section>
}

function Timeline({ snapshot }: { readonly snapshot: SachaActivitySnapshot }) {
  const entries = snapshot.events.slice(-16).reverse()
  return <section className={css.section}><h3>已提交时间线</h3>{entries.length === 0 ? <p className={css.empty}>暂无 Sacha 转换记录。</p> : <ol className={css.timeline}>{entries.map(event => <li key={event.seq} data-type={event.value.eventType}><time>{new Date(event.time).toLocaleTimeString()}</time><span>{event.value.summary}</span></li>)}</ol>}</section>
}

export function ActivityPanel({ sessionsList }: { readonly sessionsList: ObservableSnapshot<SessionListState> }) {
  const current = useSyncExternalStore(sessionsList.subscribe, sessionsList.getSnapshot).current
  const snapshot = useSachaActivity(current)
  const active = hasActivity(snapshot)
  const [open, setOpen] = useState(false)
  const [autoOpenedFor, setAutoOpenedFor] = useState<string>()
  const [layout, setLayout] = useState<PanelLayout>(initialPanelLayout)
  const [bounds, setBounds] = useState<PanelBounds>(initialBounds)
  const [interaction, setInteraction] = useState<'dragging' | 'resizing'>()
  const panelRef = useRef<HTMLElement | null>(null)
  const geometry = useMemo(() => resolvePanelLayout(layout, bounds), [layout, bounds])
  const layoutRef = useRef(geometry)
  const boundsRef = useRef(bounds)
  const gestureRef = useRef<PanelGesture>()
  useEffect(() => { layoutRef.current = geometry }, [geometry])
  useEffect(() => { boundsRef.current = bounds }, [bounds])
  useLayoutEffect(() => {
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
  useEffect(() => {
    if (!active || current === undefined || autoOpenedFor === current) return
    setOpen(true); setAutoOpenedFor(current)
  }, [active, autoOpenedFor, current])
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
  const busy = snapshot.team.members.some(member => member.status === 'running')
  if (!open) return <button type="button" className={css.badge} data-busy={busy || undefined} onClick={() => { setOpen(true) }} aria-label="打开 Sacha 可视化"><span />S · {snapshot.events.length}</button>
  const compact = compactPanel(bounds)
  const autoHeight = panelUsesAutoHeight(geometry, bounds)
  const panelStyle: CSSProperties = { width: geometry.width, height: autoHeight ? 'auto' : geometry.height, maxHeight: panelMaximumHeight(geometry, bounds), transform: `translate3d(${geometry.x}px, ${geometry.y}px, 0)` }
  return <aside ref={panelRef} className={css.panel} style={panelStyle} aria-label="Sacha 工作流可视化" data-sacha-visualizer data-mode={geometry.mode} data-height-mode={autoHeight ? 'auto' : 'manual'} data-compact={compact || undefined} data-interaction={interaction}>
    <header className={css.header} onPointerDown={beginMove} onPointerMove={updateGesture} onPointerUp={endGesture} onPointerCancel={cancelGesture} data-drag-handle={!compact || undefined}>
      <span><strong>Sacha</strong><small>DSH Runtime</small><i data-busy={busy || undefined} /></span>
      <span className={css.panelControls}>
        {!compact && <button type="button" onClick={toggleDock} title={geometry.mode === 'docked' ? '切换为浮动面板' : '停靠到右侧'}>{geometry.mode === 'docked' ? '浮动' : '停靠'}</button>}
        <button type="button" onClick={() => { setOpen(false) }} aria-label="收起 Sacha 可视化">收起</button>
      </span>
    </header>
    <div className={css.body}>
      <WorkflowSection snapshot={snapshot} />
      {snapshot.state.waves.length > 0 && <section className={css.section}><h3>Manager 波次</h3><div className={css.waves}>{snapshot.state.waves.map(wave => <div key={wave.waveId} data-state={wave.state}><strong>{wave.waveId}</strong><span>{wave.state}</span><small>{wave.unitIds.join('、')} · {wave.summary}</small></div>)}</div></section>}
      <EvidenceSection snapshot={snapshot} /><TeamSection snapshot={snapshot} /><Timeline snapshot={snapshot} />
      {snapshot.warnings.length > 0 && <p className={css.warning}>{snapshot.warnings.join('；')}</p>}
    </div>
    {!compact && <div className={css.resizeHandle} data-edge="left" onPointerDown={event => { beginResize('left', event) }} onPointerMove={updateGesture} onPointerUp={endGesture} onPointerCancel={cancelGesture} />}
    {!compact && geometry.mode === 'floating' && <><div className={css.resizeHandle} data-edge="bottom" onPointerDown={event => { beginResize('bottom', event) }} onPointerMove={updateGesture} onPointerUp={endGesture} onPointerCancel={cancelGesture} /><div className={css.resizeHandle} data-edge="corner" onPointerDown={event => { beginResize('corner', event) }} onPointerMove={updateGesture} onPointerUp={endGesture} onPointerCancel={cancelGesture} /></>}
  </aside>
}

