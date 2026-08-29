/** Sacha workflow, Manager DAG, and continuable-subagent observability panel. */

import {
  useEffect, useLayoutEffect, useMemo, useState, useSyncExternalStore, type CSSProperties,
} from 'react'
import type { ObservableSnapshot, SessionListState } from '@deepseek-ai/dsh-client-runtime/client'
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
import { PANEL_DISMISSED_KEY, dismissSession, parseDismissedSessions } from './panel-visibility.ts'
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
const TOOL_SURFACE_LABEL: Record<ToolSurfaceSnapshot['profile'], string> = {
  inspect: '已收窄为查看工具', execute: '已开放处理工具', review: '已收窄为确认工具',
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

function Conductor({ snapshot }: { readonly snapshot: SachaActivitySnapshot }): JSX.Element {
  const phase = snapshot.state.phase
  const running = snapshot.subagents.children.filter(child => child.status === 'running').length
  const nodeState = phase?.state ?? (running > 0 ? 'entered' : 'waiting')
  return (
    <section className={css.conductor} data-state={nodeState}>
      <CatArt kind={CONDUCTOR_CAT.kind} prop={CONDUCTOR_CAT.prop} size={44} />
      <div className={css.conductorText}>
        <div className={css.rowTitle}>
          <strong>当前进展</strong>
          <small>{running > 0 ? `${running} 项工作正在进行` : '跟随任务推进'}</small>
        </div>
        <div className={css.summary}>{phase?.summary ?? (running > 0 ? `${running} 项工作正在进行` : '等待新的任务进展')}</div>
        <div className={css.meta}>{phase === undefined ? '尚无新的进展' : `${PHASE_LABEL[phase.phase]} · ${PHASE_STATE_LABEL[phase.state]}`}</div>
      </div>
    </section>
  )
}

function ToolSurfaceSection({ surface }: { readonly surface?: ToolSurfaceSnapshot }): JSX.Element | null {
  if (surface === undefined) return null
  return (
    <section className={css.section} aria-label="当前可用能力">
      <div className={css.sectionHead}>
        <h3>当前可用能力</h3>
        <small>{surface.visibleCount} 个可用</small>
      </div>
      <article className={css.toolSurface} data-fallback={surface.fallback || undefined}>
        <span className={css.summary}>{TOOL_SURFACE_LABEL[surface.profile]}</span>
        <span className={css.meta}>
          {surface.hiddenCount > 0 ? `${surface.hiddenCount} 个暂时收起` : '没有暂时收起的工具'}
          {surface.unlocked.length > 0 ? ` · 已按需增加 ${surface.unlocked.length} 个` : ' · 需要时可按需增加'}
        </span>
        {surface.fallback ? <span className={css.toolSurfaceWarning}>能力收窄出现异常，请查看日志。</span> : null}
      </article>
    </section>
  )
}

function ChildCard({ child, state }: { readonly child: SubagentSnapshot; readonly state: VisualState }): JSX.Element {
  const prop = subagentCatProp(child)
  const delegation = state.delegations.find(value => value.childId === child.id)
  const task = delegation === undefined
    ? undefined
    : state.waves.flatMap(wave => wave.units).find(unit => unit.id === delegation.unitId)
  return (
    <article className={css.childCard} data-status={child.status}>
      <div className={css.childAvatar} data-status={child.status}>
        <CatArt kind={MEMBER_CAT.kind} prop={prop ?? MEMBER_CAT.prop} size={40} />
        <span className={css.statusArt}><MemberStatusArt status={child.status} size={18} /></span>
      </div>
      <div className={css.childText}>
        <div className={css.rowTitle}>
          <strong title={task?.label ?? '协作任务'}>{task?.label ?? '协作任务'}</strong>
          <small>{CHILD_STATUS_LABEL[child.status]}</small>
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
  const snapshot = useSachaActivity(current)
  const active = hasActivity(snapshot)
  const [open, setOpen] = useState(false)
  const [autoOpenedFor, setAutoOpenedFor] = useState<string>()
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
  const busy = snapshot.subagents.children.some(child => child.status === 'running')
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
        <Conductor snapshot={snapshot} />
        <ToolSurfaceSection surface={snapshot.toolSurface} />
        <StateBadges state={snapshot.state} />
        <ManagerSection snapshot={snapshot} />
        <section className={css.section} aria-label="协作任务">
          <div className={css.sectionHead}>
            <h3>协作任务</h3>
            <small>{snapshot.subagents.available ? `${snapshot.subagents.children.length} 项` : '状态暂不可用'}</small>
          </div>
          {snapshot.subagents.children.length === 0
            ? <p className={css.emptyHint}>当前没有并行处理的工作。</p>
            : <div className={css.childList}>{snapshot.subagents.children.map(child => <ChildCard key={child.id} child={child} state={snapshot.state} />)}</div>}
        </section>
        {snapshot.warnings.length > 0 ? (
          <section className={css.warningBox} aria-label="需要处理的问题">{snapshot.warnings.map(warning => (
            <p key={warning}>{warning.includes('下级 child') ? '发现重复分派，需要处理。' : '协作状态出现异常，请查看日志。'}</p>
          ))}</section>
        ) : null}
      </div>
    </aside>
  )
}
