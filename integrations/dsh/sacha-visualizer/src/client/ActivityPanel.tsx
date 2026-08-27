/** Sacha workflow and continuable-subagent observability panel. */

import {
  useEffect, useLayoutEffect, useMemo, useState, useSyncExternalStore, type CSSProperties,
} from 'react'
import type { ObservableSnapshot, SessionListState } from '@deepseek-ai/dsh-client-runtime/client'
import { useSachaActivity } from './activity-monitor.ts'
import { CONDUCTOR_CAT, MEMBER_CAT, subagentCatProp } from './artwork.ts'
import { CatArt } from './cats.tsx'
import { MemberStatusArt } from './status-art.tsx'
import {
  DEFAULT_PANEL_LAYOUT, PANEL_LAYOUT_STORAGE_KEY, compactPanel, dockPanel, floatPanel,
  panelMaximumHeight, panelUsesAutoHeight, parsePanelLayout, resolvePanelLayout,
  type PanelBounds, type PanelLayout,
} from './panel-geometry.ts'
import { PANEL_DISMISSED_KEY, dismissSession, parseDismissedSessions } from './panel-visibility.ts'
import type {
  SachaActivitySnapshot, SachaGate, SachaPhase, SubagentSnapshot, VisualState,
} from '../types.ts'
import css from './ActivityPanel.module.css'

const PANEL_OPEN_ATTRIBUTE = 'data-sacha-panel-open'
const PANEL_SHIFT_PROPERTY = '--sacha-panel-shift'

const PHASE_LABEL: Record<SachaPhase, string> = {
  intake: '入口判断', direct: '直接执行', planner: '规划', explore: '探索', executor: '实施',
  reviewer: '独立评审', roadmap: '路线图', 'document-project': '项目文档', closeout: '收口',
  feedback: '反馈移交', 'human-decision': '等待决定', complete: '完成', blocked: '阻塞',
}
const GATE_LABEL: Record<SachaGate, string> = {
  planner: 'Planner Gate', manager: 'Manager Gate', reviewer: 'Reviewer Gate',
}
const CHILD_STATUS_LABEL: Record<SubagentSnapshot['status'], string> = {
  running: '工作中', idle: '空闲', ready: '可恢复',
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

function hasOrchestration(snapshot: SachaActivitySnapshot): boolean {
  return snapshot.events.length > 0 || snapshot.subagents.children.length > 0
}

function StateBadges({ state }: { readonly state: VisualState }): JSX.Element | null {
  const gates = (Object.entries(state.gates) as [SachaGate, VisualState['gates'][SachaGate]][])
    .filter((entry): entry is [SachaGate, NonNullable<VisualState['gates'][SachaGate]>] => entry[1] !== undefined)
  if (gates.length === 0 && state.review === undefined) return null
  return (
    <div className={css.badges}>
      {gates.map(([gate, value]) => (
        <span key={gate} className={css.stateBadge} data-tone={value.decision === 'open' ? 'warning' : 'neutral'} title={value.summary}>
          {GATE_LABEL[gate]} · {value.decision === 'open' ? '开' : '关'}
        </span>
      ))}
      {state.review !== undefined ? (
        <span className={css.stateBadge} data-tone="review" title={state.review.summary}>
          Review · {state.review.outcome}
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
          <strong>指挥</strong>
          <small>主任务 · Manager · 汇总</small>
        </div>
        <div className={css.summary}>{phase?.summary ?? (running > 0 ? `${running} 个 child 正在工作` : '等待 Sacha 活动')}</div>
        <div className={css.meta}>{phase === undefined ? '当前无已提交 phase' : `${PHASE_LABEL[phase.phase]} · ${phase.state}`}</div>
      </div>
    </section>
  )
}

function ChildCard({ child }: { readonly child: SubagentSnapshot }): JSX.Element {
  const prop = subagentCatProp(child)
  return (
    <article className={css.childCard} data-status={child.status}>
      <div className={css.childAvatar}>
        <CatArt kind={MEMBER_CAT.kind} prop={prop ?? MEMBER_CAT.prop} size={40} />
        <span className={css.statusArt}><MemberStatusArt status={child.status} size={18} /></span>
      </div>
      <div className={css.childText}>
        <div className={css.rowTitle}>
          <strong title={child.label}>{child.label}</strong>
          <small>{CHILD_STATUS_LABEL[child.status]}</small>
        </div>
        <code className={css.childId}>{child.id}</code>
        {child.hasChildren ? <span className={css.nestingWarning}>观察到下级 child · 需复核单层派发</span> : null}
      </div>
    </article>
  )
}

function WaveList({ state }: { readonly state: VisualState }): JSX.Element | null {
  if (state.waves.length === 0) return null
  return (
    <section className={css.section} aria-label="Manager 波次">
      <h3>Manager 波次</h3>
      <div className={css.waveList}>
        {state.waves.map(wave => (
          <article key={wave.waveId} className={css.waveRow} data-state={wave.state}>
            <div className={css.rowTitle}>
              <strong>{wave.waveId}</strong>
              <small>{wave.state}</small>
            </div>
            <span className={css.summary}>{wave.summary}</span>
            {wave.unitIds.length > 0 ? <code>{wave.unitIds.join(' · ')}</code> : null}
          </article>
        ))}
      </div>
    </section>
  )
}

function CollapsedBadge({ count, busy, onClick }: {
  readonly count: number; readonly busy: boolean; readonly onClick: () => void
}): JSX.Element {
  return (
    <button type="button" className={css.badge} data-busy={busy || undefined} onClick={onClick}
      aria-label={`打开 Sacha 可视化（${count} 项活动）`}>
      <span className={css.badgeDot} data-busy={busy || undefined} aria-hidden />
      <span>S · {count}</span>
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
    if (snapshot === undefined || !hasOrchestration(snapshot)) return
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
    <aside className={css.panel} style={panelStyle} aria-label="Sacha 编排与 subagent 可视化"
      data-sacha-visualizer data-mode={geometry.mode} data-compact={compact || undefined}>
      <header className={css.panelHead}>
        <span className={css.panelTitle}>Sacha 编排 <span className={css.panelDot} data-busy={busy || undefined} /></span>
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
        <StateBadges state={snapshot.state} />
        <WaveList state={snapshot.state} />
        <section className={css.section} aria-label="Continuable subagents">
          <div className={css.sectionHead}>
            <h3>Continuable children</h3>
            <small>{snapshot.subagents.available ? `${snapshot.subagents.children.length} 个 direct child` : 'subagent service 不可用'}</small>
          </div>
          {snapshot.subagents.children.length === 0
            ? <p className={css.emptyHint}>当前 Root Session 没有 continuable direct child。</p>
            : <div className={css.childList}>{snapshot.subagents.children.map(child => <ChildCard key={child.id} child={child} />)}</div>}
        </section>
        {snapshot.warnings.length > 0 ? (
          <section className={css.warningBox} aria-label="观测警告">{snapshot.warnings.map(warning => <p key={warning}>{warning}</p>)}</section>
        ) : null}
      </div>
    </aside>
  )
}
