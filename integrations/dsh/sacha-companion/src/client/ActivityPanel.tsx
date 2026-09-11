/** Sacha workflow, Manager DAG, and continuable-subagent observability panel. */

import {
  useEffect, useLayoutEffect, useMemo, useRef, useState, useSyncExternalStore, type CSSProperties,
} from 'react'
import type { ObservableSnapshot } from '@deepseek-ai/dsh-client-store'
import type { SessionListState } from '@deepseek-ai/dsh-api-session-controller/client'
import { useSachaActivity } from './activity-monitor.ts'
import { CONDUCTOR_CAT, MEMBER_CAT, subagentCatProp } from './artwork.ts'
import { CatArt } from './cats.tsx'
import { MemberStatusArt } from './status-art.tsx'
import { MANAGER_NODE_HEIGHT, MANAGER_NODE_WIDTH, managerGraphLayout } from './manager-graph.ts'
import {
  DEFAULT_PANEL_LAYOUT, PANEL_LAYOUT_STORAGE_KEY, compactPanel, dockPanel, floatPanel,
  panelMaximumHeight, panelUsesAutoHeight, parsePanelLayout, resolvePanelLayout,
  type PanelBounds, type PanelLayout,
} from './panel-geometry.ts'
import { placePopover, type AnchorRect, type PopoverPlacement } from './popover-position.ts'
import { PANEL_DISMISSED_KEY, dismissSession, parseDismissedSessions } from './panel-visibility.ts'
import { groupTools, phaseSummary, type ToolFamilyView, type ToolView } from './tool-surface-view.ts'
import type {
  SachaActivitySnapshot, SachaGate, SachaPhase, SubagentSnapshot, ToolSurfaceSnapshot, VisualState,
} from '../types.ts'
import css from './ActivityPanel.module.css'

const PANEL_OPEN_ATTRIBUTE = 'data-sacha-panel-open'
const PANEL_SHIFT_PROPERTY = '--sacha-panel-shift'

const PHASE_LABEL: Record<SachaPhase, string> = {
  intake: '准备中', direct: '处理中', planner: '确认目标', explore: '查找资料', executor: '处理中',
  reviewer: '确认结果', roadmap: '整理计划', 'document-project': '整理文档', closeout: '收尾中',
  feedback: '转交中', 'human-decision': '等待你的决定', complete: '已完成', blocked: '暂时无法继续',
}
const PHASE_STATE_LABEL: Record<NonNullable<VisualState['phase']>['state'], string> = {
  entered: '进行中', waiting: '等待中', completed: '已完成', blocked: '遇到问题', cancelled: '已停止',
}
const GATE_NOTICE: Record<SachaGate, string> = {
  planner: '需要确认目标和做法', manager: '多项工作需要协调', reviewer: '结果正在确认',
}
const REVIEW_LABEL: Record<NonNullable<VisualState['review']>['outcome'], string> = {
  accepted: '结果已确认',
  accepted_with_follow_up: '结果已确认，仍有后续事项',
  needs_fix: '发现问题，正在调整',
  needs_replan: '需要重新确定做法',
  needs_evidence: '还缺一次实际验证',
  blocked: '暂时无法继续',
}
const CHILD_STATUS_LABEL: Record<SubagentSnapshot['status'], string> = {
  running: '工作中', idle: '空闲', ready: '可恢复',
}
const WAVE_STATE_LABEL: Record<VisualState['waves'][number]['state'], string> = {
  planned: '准备中', dispatched: '进行中', waiting: '等待中', completed: '已完成', blocked: '遇到问题',
}
const UNIT_STATE_LABEL: Record<VisualState['waves'][number]['units'][number]['state'], string> = {
  ready: '可开始', running: '进行中', waiting: '等待中', completed: '已完成', blocked: '遇到问题',
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
  return snapshot !== undefined && (snapshot.events.length > 0 || snapshot.subagents.children.length > 0)
}

function StateBadges({ state }: { readonly state: VisualState }): JSX.Element | null {
  const gates = (Object.entries(state.gates) as [SachaGate, VisualState['gates'][SachaGate]][])
    .filter((entry): entry is [SachaGate, NonNullable<VisualState['gates'][SachaGate]>] => entry[1]?.decision === 'open')
  if (gates.length === 0 && state.review === undefined) return null
  return (
    <div className={css.badges}>
      {gates.map(([gate]) => (
        <span key={gate} className={css.stateBadge} data-tone="warning">
          {GATE_NOTICE[gate]}
        </span>
      ))}
      {state.review !== undefined ? (
        <span className={css.stateBadge} data-tone="review">
          {REVIEW_LABEL[state.review.outcome]}
        </span>
      ) : null}
    </div>
  )
}

function Conductor({ snapshot, stale }: { readonly snapshot: SachaActivitySnapshot; readonly stale: boolean }): JSX.Element {
  const phase = snapshot.state.phase
  const running = stale ? 0 : snapshot.subagents.children.filter(child => child.status === 'running').length
  const nodeState = stale ? 'waiting' : phase?.state ?? (running > 0 ? 'entered' : 'waiting')
  return (
    <section className={css.conductor} data-state={nodeState}>
      <CatArt kind={CONDUCTOR_CAT.kind} prop={CONDUCTOR_CAT.prop} size={44} />
      <div className={css.conductorText}>
        <div className={css.rowTitle}>
          <strong>{stale ? '上次进展' : '当前进展'}</strong>
          <small>{stale ? '等待重新连接' : running > 0 ? `${running} 项工作正在进行` : '跟随任务推进'}</small>
        </div>
        <div className={css.summary}>{phase?.summary ?? (running > 0 ? `${running} 项工作正在进行` : '等待新的任务进展')}</div>
        <div className={css.meta}>{stale ? '以下记录来自上次连接' : phase === undefined ? '尚无新的进展' : `${PHASE_LABEL[phase.phase]} · ${PHASE_STATE_LABEL[phase.state]}`}</div>
      </div>
    </section>
  )
}

function ToolChip({ tool }: { readonly tool: ToolView }): JSX.Element {
  return (
    <span className={css.toolChip} data-unlocked={tool.unlocked || undefined}>
      {tool.label ?? tool.name}
      {tool.label === undefined ? null : <code className={css.toolChipName}>{tool.name}</code>}
    </span>
  )
}

function ToolFamilyList({ families, empty }: {
  readonly families: readonly ToolFamilyView[]
  readonly empty: string
}): JSX.Element {
  if (families.length === 0) return <span className={css.meta}>{empty}</span>
  return (
    <div className={css.toolFamilies}>
      {families.map(family => (
        <div key={family.key} className={css.toolFamily}>
          <span className={css.toolFamilyLabel}>{family.label}<small>{family.tools.length}</small></span>
          <div className={css.toolChips}>
            {family.tools.map(tool => <ToolChip key={tool.name} tool={tool} />)}
          </div>
        </div>
      ))}
    </div>
  )
}

/**
 * The full tool lists, revealed on hover rather than always shown: the panel's
 * job is to report progress, and a 90-entry catalogue would dominate it.
 *
 * Rendered as a sibling of the scrolling `.body`, not inside it, because that
 * body clips its overflow. Positioned in viewport coordinates and translated
 * into the panel's own frame (the panel is the containing block: it carries the
 * transform that places it).
 */
function ToolSurfacePopover({ surface, anchor, panel, onEnter, onLeave }: {
  readonly surface: ToolSurfaceSnapshot
  readonly anchor: AnchorRect
  readonly panel: DOMRect
  readonly onEnter: () => void
  readonly onLeave: () => void
}): JSX.Element {
  const contentRef = useRef<HTMLDivElement | null>(null)
  const [placement, setPlacement] = useState<PopoverPlacement>(() => placePopover(anchor, 0, {
    width: window.innerWidth, height: window.innerHeight,
  }))
  useLayoutEffect(() => {
    const measure = (): void => {
      const height = contentRef.current?.getBoundingClientRect().height ?? 0
      setPlacement(placePopover(anchor, height, { width: window.innerWidth, height: window.innerHeight }))
    }
    measure()
    window.addEventListener('resize', measure)
    return () => { window.removeEventListener('resize', measure) }
  }, [anchor])

  const visibleFamilies = groupTools(surface, surface.visible)
  const hiddenFamilies = groupTools(surface, surface.hidden)
  return (
    <div ref={contentRef} className={css.popover} role="tooltip"
      onMouseEnter={onEnter} onMouseLeave={onLeave}
      style={{
        left: placement.left - panel.left,
        top: placement.top - panel.top,
        width: placement.width,
        maxHeight: placement.maxHeight,
      }}>
      <div className={css.popoverHead}>
        <strong>当前可用能力</strong>
        <small>{phaseSummary(surface)}</small>
      </div>
      <div className={css.popoverBody}>
        <span className={css.popoverGroupTitle}>模型现在能用的 {surface.visibleCount} 个</span>
        <ToolFamilyList families={visibleFamilies} empty="当前没有可用工具" />
        {surface.unlocked.length > 0 ? (
          <span className={css.meta}>虚线框的 {surface.unlocked.length} 个是本轮按需增加的</span>
        ) : null}
        {surface.hiddenCount > 0 ? (
          <>
            <span className={css.popoverGroupTitle}>被隐藏的 {surface.hiddenCount} 个</span>
            <p className={css.emptyHint}>模型当前看不到这些；需要时它会自己按需启用。</p>
            <ToolFamilyList families={hiddenFamilies} empty="没有被隐藏的工具" />
          </>
        ) : null}
        {surface.fallback ? <span className={css.toolSurfaceWarning}>能力收窄出现异常，请查看日志。</span> : null}
      </div>
    </div>
  )
}

/**
 * Header chip: the surface's current size, sitting beside the panel title so the
 * panel's content area stays for progress. Hovering (or focusing) opens the
 * detail popover; the chip alone carries only what fits in a title row.
 */
function ToolSurfaceChip({ surface, onOpen, onClose }: {
  readonly surface?: ToolSurfaceSnapshot
  readonly onOpen: (anchor: AnchorRect, panel: DOMRect) => void
  readonly onClose: () => void
}): JSX.Element | null {
  const triggerRef = useRef<HTMLButtonElement | null>(null)
  if (surface === undefined) return null

  const open = (): void => {
    const rect = triggerRef.current?.getBoundingClientRect()
    const panel = triggerRef.current?.closest('[data-sacha-visualizer]')?.getBoundingClientRect()
    if (rect === undefined || panel === undefined || panel === null) return
    onOpen({ left: rect.left, top: rect.top, bottom: rect.bottom }, panel)
  }

  return (
    <button ref={triggerRef} type="button" className={css.surfaceChip}
      data-fallback={surface.fallback || undefined}
      onMouseEnter={open} onMouseLeave={onClose} onFocus={open} onBlur={onClose}
      aria-label={`当前可用能力：${surface.visibleCount} 个可用；悬停查看明细`}>
      <span className={css.surfaceChipCount}>{surface.visibleCount}</span>
      <span className={css.surfaceChipUnit}>个可用</span>
    </button>
  )
}

function ChildCard({ child, state, stale }: { readonly child: SubagentSnapshot; readonly state: VisualState; readonly stale: boolean }): JSX.Element {
  const prop = subagentCatProp(child)
  const delegation = state.delegations.find(value => value.childId === child.id)
  const task = delegation === undefined
    ? undefined
    : state.waves.flatMap(wave => wave.units).find(unit => unit.id === delegation.unitId)
  return (
    <article className={css.childCard} data-status={stale ? 'idle' : child.status}>
      <div className={css.childAvatar} data-status={stale ? 'idle' : child.status}>
        <CatArt kind={MEMBER_CAT.kind} prop={prop ?? MEMBER_CAT.prop} size={40} />
        <span className={css.statusArt}><MemberStatusArt status={stale ? 'idle' : child.status} size={18} /></span>
      </div>
      <div className={css.childText}>
        <div className={css.rowTitle}>
          <strong title={task?.label ?? '协作任务'}>{task?.label ?? '协作任务'}</strong>
          <small>{stale ? `上次：${CHILD_STATUS_LABEL[child.status]}` : CHILD_STATUS_LABEL[child.status]}</small>
        </div>
        {child.hasChildren ? <span className={css.nestingWarning}>发现重复分派，需要处理</span> : null}
      </div>
    </article>
  )
}

function ManagerWaveGraph({ wave }: { readonly wave: VisualState['waves'][number] }): JSX.Element {
  const layout = useMemo(() => managerGraphLayout(wave.units), [wave.units])
  return (
    <article className={css.waveCard} data-state={wave.state}>
      <div className={css.rowTitle}>
        <strong>本组工作</strong>
        <small>{WAVE_STATE_LABEL[wave.state]}</small>
      </div>
      <span className={css.summary}>{wave.summary}</span>
      <div className={css.graphViewport}>
        <div className={css.graphCanvas} style={{ width: Math.max(layout.width, MANAGER_NODE_WIDTH), height: Math.max(layout.height, MANAGER_NODE_HEIGHT) }}>
          <svg className={css.graphEdges} width={layout.width} height={layout.height} aria-hidden>
            {layout.edges.map(edge => <path key={`${edge.from}:${edge.to}`} d={edge.path} />)}
          </svg>
          {layout.nodes.map(node => {
            return (
              <div key={node.unit.id} className={css.graphNode} data-state={node.unit.state}
                style={{ left: node.x, top: node.y, width: MANAGER_NODE_WIDTH, height: MANAGER_NODE_HEIGHT }}>
                <span className={css.graphNodeHead}><strong title={node.unit.label}>{node.unit.label}</strong><small>{UNIT_STATE_LABEL[node.unit.state]}</small></span>
              </div>
            )
          })}
        </div>
      </div>
    </article>
  )
}

function ManagerSection({ snapshot }: { readonly snapshot: SachaActivitySnapshot }): JSX.Element | null {
  if (snapshot.state.waves.length === 0) return null
  return (
    <section className={css.section} aria-label="工作依赖">
      <div className={css.sectionHead}>
        <h3>工作依赖</h3>
        <small>按先后关系推进</small>
      </div>
      <div className={css.waveList}>
        {snapshot.state.waves.map(wave => <ManagerWaveGraph key={wave.waveId} wave={wave} />)}
      </div>
    </section>
  )
}

function CollapsedBadge({ count, busy, onClick }: {
  readonly count: number; readonly busy: boolean; readonly onClick: () => void
}): JSX.Element {
  return (
    <button type="button" className={css.badge} data-busy={busy || undefined} onClick={onClick}
      aria-label={`打开任务进展（${count} 项更新）`}>
      <span className={css.badgeDot} data-busy={busy || undefined} aria-hidden />
      <span>任务进展</span>
    </button>
  )
}

export function ActivityPanel({ sessionsList }: { readonly sessionsList: ObservableSnapshot<SessionListState> }): JSX.Element | null {
  const current = useSyncExternalStore(sessionsList.subscribe, sessionsList.getSnapshot).current
  const [open, setOpen] = useState(false)
  const observation = useSachaActivity(current, open)
  const snapshot = observation?.snapshot
  const stale = observation?.stale ?? false
  const active = hasActivity(snapshot)
  const [autoOpenedFor, setAutoOpenedFor] = useState<string>()
  // Kept here rather than inside the section: the popover must render as a
  // sibling of the scrolling body, and a closed timer keeps a short grace period
  // so the pointer can travel from the trigger into the popover.
  const [surfaceAnchor, setSurfaceAnchor] = useState<{ readonly rect: AnchorRect; readonly panel: DOMRect } | null>(null)
  const surfaceCloseTimer = useRef<number | undefined>(undefined)
  const cancelSurfaceClose = (): void => {
    if (surfaceCloseTimer.current === undefined) return
    window.clearTimeout(surfaceCloseTimer.current)
    surfaceCloseTimer.current = undefined
  }
  const scheduleSurfaceClose = (): void => {
    cancelSurfaceClose()
    surfaceCloseTimer.current = window.setTimeout(() => { setSurfaceAnchor(null) }, 120)
  }
  const closeSurfaceNow = (): void => {
    cancelSurfaceClose()
    setSurfaceAnchor(null)
  }
  useEffect(() => () => { cancelSurfaceClose() }, [])
  useEffect(() => {
    if (surfaceAnchor === null) return
    const onKey = (event: KeyboardEvent): void => { if (event.key === 'Escape') closeSurfaceNow() }
    window.addEventListener('keydown', onKey)
    return () => { window.removeEventListener('keydown', onKey) }
  }, [surfaceAnchor])
  const [dismissedSessions, setDismissedSessions] = useState<Set<string>>(initialDismissedSessions)
  const [layout, setLayout] = useState<PanelLayout>(initialPanelLayout)
  const [bounds, setBounds] = useState<PanelBounds>(initialBounds)
  const geometry = useMemo(() => resolvePanelLayout(layout, bounds), [layout, bounds])

  useLayoutEffect(() => {
    const update = (): void => {
      const measured = measureShellBounds()
      if (measured !== undefined) setBounds(measured)
    }
    update()
    const overlay = document.querySelector<HTMLElement>('[data-shell-overlay]')
    const conversation = document.querySelector<HTMLElement>("[data-phase='active']")
    const observer = new ResizeObserver(update)
    if (overlay !== null) observer.observe(overlay)
    if (conversation !== null) observer.observe(conversation)
    window.addEventListener('resize', update)
    return () => { observer.disconnect(); window.removeEventListener('resize', update) }
  }, [])

  useEffect(() => {
    if (snapshot === undefined || (snapshot.events.length === 0 && snapshot.subagents.children.length === 0)) return
    if (dismissedSessions.has(snapshot.sessionId) || autoOpenedFor === snapshot.sessionId) return
    setOpen(true)
    setAutoOpenedFor(snapshot.sessionId)
  }, [autoOpenedFor, dismissedSessions, snapshot])

  useEffect(() => {
    const root = document.documentElement
    if (!open || !active || snapshot === undefined) {
      root.removeAttribute(PANEL_OPEN_ATTRIBUTE)
      root.style.removeProperty(PANEL_SHIFT_PROPERTY)
      return
    }
    root.setAttribute(PANEL_OPEN_ATTRIBUTE, geometry.mode)
    root.style.setProperty(PANEL_SHIFT_PROPERTY, geometry.mode === 'docked' ? `${geometry.width}px` : '0px')
    return () => {
      root.removeAttribute(PANEL_OPEN_ATTRIBUTE)
      root.style.removeProperty(PANEL_SHIFT_PROPERTY)
    }
  }, [active, geometry.mode, geometry.width, open, snapshot])

  if (!active || snapshot === undefined) return null
  const busy = !stale && snapshot.subagents.children.some(child => child.status === 'running')
  const count = snapshot.events.length + snapshot.subagents.children.length
  if (!open) return <CollapsedBadge count={count} busy={busy} onClick={() => { setOpen(true) }} />

  const compact = compactPanel(bounds)
  const autoHeight = panelUsesAutoHeight(geometry, bounds)
  const panelStyle: CSSProperties = {
    width: geometry.width,
    height: autoHeight ? 'auto' : geometry.height,
    maxHeight: panelMaximumHeight(geometry, bounds),
    transform: `translate3d(${geometry.x}px, ${geometry.y}px, 0)`,
  }
  const toggleDock = (): void => {
    const next = geometry.mode === 'docked' ? floatPanel(geometry, bounds) : dockPanel(geometry, bounds)
    setLayout(next)
    window.localStorage.setItem(PANEL_LAYOUT_STORAGE_KEY, JSON.stringify(next))
  }

  return (
    <aside className={css.panel} style={panelStyle} aria-label="任务进展"
      data-sacha-visualizer data-mode={geometry.mode} data-compact={compact || undefined}>
      <header className={css.panelHead}>
        <span className={css.panelTitle}>任务进展 <span className={css.panelDot} data-busy={busy || undefined} /></span>
        {!stale ? (
          <ToolSurfaceChip surface={snapshot.toolSurface}
            onOpen={(rect, panel) => { cancelSurfaceClose(); setSurfaceAnchor({ rect, panel }) }}
            onClose={scheduleSurfaceClose} />
        ) : null}
        <span className={css.panelControls}>
          {!compact ? <button type="button" onClick={toggleDock}>{geometry.mode === 'docked' ? '浮动' : '停靠'}</button> : null}
          <button type="button" onClick={() => {
            setOpen(false)
            if (current === undefined) return
            setDismissedSessions(previous => {
              const next = new Set(dismissSession([...previous], current))
              window.localStorage.setItem(PANEL_DISMISSED_KEY, JSON.stringify([...next]))
              return next
            })
          }}>收起</button>
        </span>
      </header>
      <div className={css.body}>
        {stale ? <p className={css.staleNotice} role="status" title={observation?.error}>连接失败，正在重试。以下是上次快照，当前进展和结果尚未确认。</p> : null}
        <Conductor snapshot={snapshot} stale={stale} />
        {!stale ? <StateBadges state={snapshot.state} /> : null}
        {!stale ? <ManagerSection snapshot={snapshot} /> : null}
        {snapshot.events.some(({ value }) => (value.eventType === 'review' || value.eventType === 'evidence')
          && (value.scopeRevision === undefined || value.scopeRevision !== snapshot.state.phase?.scopeRevision))
          ? <p className={css.emptyHint}>历史结果未确认适用于当前改动，不能作为本次通过的依据。</p> : null}
        <section className={css.section} aria-label="协作任务">
          <div className={css.sectionHead}>
            <h3>协作任务</h3>
            <small>{snapshot.subagents.available ? `${snapshot.subagents.children.length} 项` : '状态暂不可用'}</small>
          </div>
          {snapshot.subagents.children.length === 0
            ? <p className={css.emptyHint}>当前没有并行处理的工作。</p>
            : <div className={css.childList}>{snapshot.subagents.children.map(child => <ChildCard key={child.id} child={child} state={snapshot.state} stale={stale} />)}</div>}
        </section>
        {snapshot.warnings.length > 0 ? (
          <section className={css.warningBox} aria-label="需要处理的问题">{snapshot.warnings.map(warning => (
            <p key={warning}>{warning.includes('下级 child') ? '发现重复分派，需要处理。' : '协作状态出现异常，请查看日志。'}</p>
          ))}</section>
        ) : null}
      </div>
      {surfaceAnchor === null || snapshot.toolSurface === undefined ? null : (
        <ToolSurfacePopover surface={snapshot.toolSurface} anchor={surfaceAnchor.rect} panel={surfaceAnchor.panel}
          onEnter={cancelSurfaceClose} onLeave={scheduleSurfaceClose} />
      )}
    </aside>
  )
}
