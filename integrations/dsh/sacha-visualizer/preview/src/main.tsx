import React, { useEffect, useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import type { ObservableSnapshot, SessionListState } from '@deepseek-ai/dsh-client-runtime/client'
import panelCss from '../../src/client/ActivityPanel.module.css'
import { ActivityPanel } from '../../src/client/ActivityPanel.tsx'
import { CatArt, type CatKind, type CatProp } from '../../src/client/cats.tsx'
import { PANEL_LAYOUT_STORAGE_KEY } from '../../src/client/panel-geometry.ts'
import { MemberStatusArt } from '../../src/client/status-art.tsx'
import type { TeamMemberSnapshot } from '../../src/types.ts'
import { PANEL_SCENARIOS, PANEL_SCENARIO_BY_ID, type PanelScenario } from './scenarios.ts'
import './styles.css'

type MotionState = 'running' | 'waiting' | 'completed' | 'blocked'
type Surface = 'light' | 'dark' | 'checker'
type Speed = 'slow' | 'normal' | 'fast'
type PreviewControls = {
  readonly paused: boolean
  readonly reduced: boolean
  readonly speed: Speed
  readonly surface: Surface
  readonly propScale: number
  readonly propGap: number
}

const DEFAULT_CONTROLS: PreviewControls = {
  paused: false,
  reduced: false,
  speed: 'normal',
  surface: 'light',
  propScale: 0.86,
  propGap: 9,
}

const CAT_KINDS: readonly CatKind[] = ['sacha', 'jojo']
const PROPS: readonly CatProp[] = [
  'none', 'conductor', 'explore', 'research', 'engineer', 'security', 'docs',
  'data', 'operator', 'design', 'qa', 'working', 'sleeping', 'thinking',
]
const MOTIONS: ReadonlyArray<readonly [MotionState, string, string]> = [
  ['running', '运行', '上浮 2px，同时 -4° ↔ +4°'],
  ['waiting', '等待', '原地 -7° ↔ +7°'],
  ['completed', '完成', '透明度与 1 ↔ 1.06 呼吸缩放'],
  ['blocked', '阻塞', '保持静止'],
]
const MEMBER_STATUSES: readonly TeamMemberSnapshot['status'][] = ['running', 'idle', 'inactive', 'provisioning', 'failed']
const STATUS_LABELS: Record<TeamMemberSnapshot['status'], string> = {
  running: '运行中', idle: '空闲', inactive: '未激活', provisioning: '准备中', failed: '失败',
}

const search = new URLSearchParams(window.location.search)
const panelScenario = search.get('mode') === 'panel'
  ? PANEL_SCENARIO_BY_ID.get(search.get('scenario') ?? '')
  : undefined

if (panelScenario !== undefined) {
  window.localStorage.removeItem(PANEL_LAYOUT_STORAGE_KEY)
  const originalFetch = window.fetch.bind(window)
  window.fetch = async (input, init) => {
    const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url
    if (url.startsWith('/plugins/sacha-visualizer/state')) {
      return new Response(JSON.stringify(panelScenario.snapshot), {
        status: 200,
        headers: { 'content-type': 'application/json' },
      })
    }
    return originalFetch(input, init)
  }
}

function PanelScenarioApp({ scenario }: { readonly scenario: PanelScenario }) {
  const [controls, setControls] = useState<PreviewControls>(DEFAULT_CONTROLS)
  const sessionsList = useMemo(() => {
    const state = { current: scenario.snapshot.sessionId } as SessionListState
    return {
      getSnapshot: () => state,
      subscribe: (_listener: () => void) => () => {},
    } as ObservableSnapshot<SessionListState>
  }, [scenario])

  useEffect(() => {
    const receive = (event: MessageEvent): void => {
      if (event.origin !== window.location.origin || event.data?.type !== 'sacha-preview-controls') return
      setControls(event.data.controls as PreviewControls)
    }
    window.addEventListener('message', receive)
    return () => { window.removeEventListener('message', receive) }
  }, [])

  useEffect(() => {
    const rate = controls.speed === 'slow' ? 0.5 : controls.speed === 'fast' ? 2 : 1
    const update = (): void => {
      for (const animation of document.getAnimations()) animation.updatePlaybackRate(rate)
    }
    const frame = requestAnimationFrame(update)
    const timer = window.setTimeout(update, 200)
    return () => { cancelAnimationFrame(frame); window.clearTimeout(timer) }
  }, [controls.speed])

  useEffect(() => {
    if (scenario.collapsed !== true) return
    const collapse = (): void => {
      const button = document.querySelector<HTMLButtonElement>('button[aria-label="收起 Sacha 可视化"]')
      if (button === null) return
      observer.disconnect()
      button.click()
    }
    const observer = new MutationObserver(collapse)
    observer.observe(document.body, { childList: true, subtree: true })
    collapse()
    return () => { observer.disconnect() }
  }, [scenario.collapsed])

  return (
    <div
      className="panelPage"
      data-shell-overlay
      data-surface={controls.surface}
      data-speed={controls.speed}
      data-paused={controls.paused}
      data-reduced={controls.reduced}
      style={{ '--cat-prop-scale': controls.propScale, '--cat-prop-offset-x': `${controls.propGap}px` } as React.CSSProperties}
    >
      <div className="fakeConversation" data-phase="active">
        <span>DSH 会话区域</span>
        <small>{scenario.title}</small>
      </div>
      <ActivityPanel sessionsList={sessionsList} />
    </div>
  )
}

function CatCard({ kind, prop, size, label }: {
  readonly kind: CatKind
  readonly prop: CatProp
  readonly size: number
  readonly label: string
}) {
  return (
    <article className="effectCard">
      <div className="artStage"><CatArt kind={kind} prop={prop} size={size} title={label} /></div>
      <strong>{label}</strong>
      <span>{kind === 'sacha' ? 'Sacha' : 'Jojo'} · {prop}</span>
    </article>
  )
}

function MotionCard({ state, paused }: { readonly state: MotionState; readonly paused: boolean }) {
  const spec = MOTIONS.find(([candidate]) => candidate === state)
  const label = spec?.[1] ?? state
  const description = spec?.[2] ?? ''
  return (
    <article className="motionCard">
      <div className="motionStage">
        <span
          className={`${panelCss.captainAvatar} motionAvatar`}
          data-state={state}
          data-preview-motion={state}
          data-paused={paused}
        >
          <CatArt kind="sacha" prop={state === 'blocked' ? 'thinking' : 'conductor'} size={88} title={`${label}动画`} />
        </span>
      </div>
      <strong>{label}</strong>
      <span>{description}</span>
    </article>
  )
}

function StatusCard({ status }: { readonly status: TeamMemberSnapshot['status'] }) {
  return (
    <article className="statusCard">
      <div className={`${panelCss.memberAvatar} statusStage`} data-status={status}>
        <CatArt kind="jojo" prop="engineer" size={54} title="成员头像" />
        <span className={`${panelCss.stateArt} statusBadge`} data-status={status}>
          <MemberStatusArt status={status} size={22} title={`${STATUS_LABELS[status]}状态`} />
        </span>
      </div>
      <strong>{STATUS_LABELS[status]}</strong>
      <span>{status}</span>
    </article>
  )
}

function App() {
  const [detailSize, setDetailSize] = useState(64)
  const [paused, setPaused] = useState(DEFAULT_CONTROLS.paused)
  const [reduced, setReduced] = useState(DEFAULT_CONTROLS.reduced)
  const [surface, setSurface] = useState<Surface>(DEFAULT_CONTROLS.surface)
  const [speed, setSpeed] = useState<Speed>(DEFAULT_CONTROLS.speed)
  const [propScale, setPropScale] = useState(DEFAULT_CONTROLS.propScale)
  const [propGap, setPropGap] = useState(DEFAULT_CONTROLS.propGap)
  const controls = useMemo<PreviewControls>(() => ({ paused, reduced, speed, surface, propScale, propGap }), [paused, reduced, speed, surface, propScale, propGap])

  const sendControls = (target: Window | null): void => {
    target?.postMessage({ type: 'sacha-preview-controls', controls }, window.location.origin)
  }

  useEffect(() => {
    for (const frame of document.querySelectorAll<HTMLIFrameElement>('.scenarioCard iframe')) sendControls(frame.contentWindow)
    const rate = speed === 'slow' ? 0.5 : speed === 'fast' ? 2 : 1
    for (const animation of document.getAnimations()) animation.updatePlaybackRate(rate)
  }, [controls, speed])

  return (
    <main
      className="previewApp"
      data-surface={surface}
      data-speed={speed}
      data-paused={paused}
      data-reduced={reduced}
      style={{ '--cat-prop-scale': propScale, '--cat-prop-offset-x': `${propGap}px` } as React.CSSProperties}
    >
      <header className="hero">
        <div>
          <p className="eyebrow">Sacha Visualizer · 开发预览</p>
          <h1>猫咪效果台</h1>
          <p>同一页检查生产底图、全部道具、真实流程映射、状态角标和动画。</p>
        </div>
        <div className="heroCats" aria-label="基础猫咪">
          <CatArt kind="sacha" size={104} title="Sacha 基础猫" />
          <CatArt kind="jojo" size={104} title="Jojo 基础猫" />
        </div>
      </header>

      <section className="controlBar" aria-label="预览控制">
        <label>效果台尺寸 <input type="range" min="20" max="96" value={detailSize} onInput={(event) => setDetailSize(Number(event.currentTarget.value))} /> <output>{detailSize}px</output></label>
        <label>道具缩放 <input type="range" min="70" max="115" value={Math.round(propScale * 100)} onInput={(event) => setPropScale(Number(event.currentTarget.value) / 100)} /> <output>{Math.round(propScale * 100)}%</output></label>
        <label>离身距离 <input type="range" min="0" max="14" value={propGap} onInput={(event) => setPropGap(Number(event.currentTarget.value))} /> <output>{propGap}px</output></label>
        <label>背景 <select value={surface} onChange={(event) => setSurface(event.target.value as Surface)}><option value="light">浅色</option><option value="dark">深色</option><option value="checker">透明棋盘</option></select></label>
        <label>速度 <select value={speed} onChange={(event) => setSpeed(event.target.value as Speed)}><option value="slow">0.5×</option><option value="normal">1×</option><option value="fast">2×</option></select></label>
        <button type="button" aria-pressed={paused} onClick={() => setPaused((value) => !value)}>{paused ? '继续动画' : '暂停动画'}</button>
        <button type="button" aria-pressed={reduced} onClick={() => setReduced((value) => !value)}>{reduced ? '关闭减弱动效' : '模拟减弱动效'}</button>
      </section>

      <section>
        <div className="sectionHeading"><div><p className="eyebrow">Full panel</p><h2>完整插件场景</h2></div><p>每个窗口都运行真实 `ActivityPanel`；首个窗口展示宽屏停靠，其余窗口展示紧凑布局和特殊状态。</p></div>
        <div className="scenarioGrid">
          {PANEL_SCENARIOS.map((scenario) => (
            <article className={`scenarioCard${scenario.id === 'running-dependencies' ? ' scenarioWide' : ''}`} key={scenario.id}>
              <header><div><strong>{scenario.title}</strong><span>{scenario.description}</span></div><a href={`/?mode=panel&scenario=${scenario.id}`} target="_blank" rel="noreferrer">单独打开</a></header>
              <iframe title={`${scenario.title}完整插件预览`} src={`/?mode=panel&scenario=${scenario.id}`} onLoad={(event) => { sendControls(event.currentTarget.contentWindow) }} />
            </article>
          ))}
        </div>
      </section>

      <section>
        <div className="sectionHeading"><div><p className="eyebrow">Motion</p><h2>全部动画状态</h2></div><p>四种状态同时运行，便于比较幅度、节奏和静止边界。</p></div>
        <div className="motionGrid">{MOTIONS.map(([state]) => <MotionCard key={state} state={state} paused={paused} />)}</div>
      </section>

      <section>
        <div className="sectionHeading"><div><p className="eyebrow">Runtime</p><h2>成员状态符号</h2></div><p>主猫表达 Role 并执行状态动画；头顶符号只表达当前 Runtime 状态。</p></div>
        <div className="statusGrid">{MEMBER_STATUSES.map((status) => <StatusCard key={status} status={status} />)}</div>
      </section>

      <section>
        <div className="sectionHeading"><div><p className="eyebrow">Props</p><h2>全部 Role 道具</h2></div><p>拖动尺寸后，Sacha 与 Jojo 的全部道具组合同时更新。</p></div>
        {CAT_KINDS.map((kind) => (
          <div className="catRow" key={kind}>
            <h3>{kind === 'sacha' ? 'Sacha' : 'Jojo'}</h3>
            <div className="effectGrid">{PROPS.map((prop) => <CatCard key={prop} kind={kind} prop={prop} size={detailSize} label={prop} />)}</div>
          </div>
        ))}
      </section>

      <section>
        <div className="sectionHeading"><div><p className="eyebrow">Scale</p><h2>实际尺寸检查</h2></div><p>20/40/44px 是插件实际消费尺寸，64/96px 用于观察边缘和叠层。</p></div>
        <div className="sizeGrid">
          {[20, 40, 44, 64, 96].map((size) => (
            <article className="sizeCard" key={size}><div><CatArt kind="sacha" prop="conductor" size={size} /><CatArt kind="jojo" prop="engineer" size={size} /></div><strong>{size}px</strong></article>
          ))}
        </div>
      </section>
    </main>
  )
}

createRoot(document.getElementById('app')!).render(panelScenario === undefined ? <App /> : <PanelScenarioApp scenario={panelScenario} />)
