import React, { useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import type { ObservableSnapshot, SessionListState } from '@deepseek-ai/dsh-client-runtime/client'
import { ActivityPanel } from '../../src/client/ActivityPanel.tsx'
import { CatArt, type CatKind, type CatProp } from '../../src/client/cats.tsx'
import { PANEL_LAYOUT_STORAGE_KEY } from '../../src/client/panel-geometry.ts'
import { MemberStatusArt } from '../../src/client/status-art.tsx'
import type { SubagentSnapshot } from '../../src/types.ts'
import { PANEL_SCENARIOS, PANEL_SCENARIO_BY_ID, type PanelScenario } from './scenarios.ts'
import './styles.css'

const CAT_KINDS: readonly CatKind[] = ['sacha', 'jojo']
const PROPS: readonly CatProp[] = [
  'none', 'conductor', 'explore', 'research', 'engineer', 'security', 'docs',
  'data', 'operator', 'design', 'qa', 'working', 'sleeping', 'thinking',
]
const CHILD_STATUSES: readonly SubagentSnapshot['status'][] = ['running', 'idle', 'ready']
const STATUS_LABELS: Record<SubagentSnapshot['status'], string> = {
  running: '运行中', idle: '空闲', ready: '可恢复',
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

function PanelScenarioApp({ scenario }: { readonly scenario: PanelScenario }): JSX.Element {
  const sessionsList = useMemo(() => {
    const state = { current: scenario.snapshot.sessionId } as SessionListState
    return {
      getSnapshot: () => state,
      subscribe: (_listener: () => void) => () => {},
    } as ObservableSnapshot<SessionListState>
  }, [scenario])
  return (
    <div className="panelPage" data-shell-overlay>
      <div className="fakeConversation" data-phase="active">
        <span>DSH 会话区域</span>
        <small>{scenario.title}</small>
      </div>
      <ActivityPanel sessionsList={sessionsList} />
    </div>
  )
}

function CatCard({ kind, prop }: { readonly kind: CatKind; readonly prop: CatProp }): JSX.Element {
  return (
    <article className="effectCard">
      <div className="artStage"><CatArt kind={kind} prop={prop} size={72} title={`${kind} ${prop}`} /></div>
      <strong>{prop}</strong>
      <span>{kind === 'sacha' ? 'Sacha' : 'Jojo'}</span>
    </article>
  )
}

function StatusCard({ status }: { readonly status: SubagentSnapshot['status'] }): JSX.Element {
  return (
    <article className="statusCard">
      <div className="artStage" style={{ position: 'relative' }}>
        <CatArt kind="jojo" prop="engineer" size={58} title="child" />
        <span style={{ position: 'absolute', right: 2, bottom: 2 }}>
          <MemberStatusArt status={status} size={22} />
        </span>
      </div>
      <strong>{STATUS_LABELS[status]}</strong>
      <span>{status}</span>
    </article>
  )
}

function App(): JSX.Element {
  const [kind, setKind] = useState<CatKind>('jojo')
  return (
    <main className="previewApp">
      <header className="hero">
        <div>
          <p className="eyebrow">Sacha Visualizer · 开发预览</p>
          <h1>Continuable subagent 可视化效果台</h1>
          <p>检查生产猫咪素材、Role 道具、running/idle/ready 状态与新的 Sacha panel scenarios。</p>
        </div>
        <div className="heroCats">
          <CatArt kind="sacha" prop="conductor" size={96} title="Sacha conductor" />
          <CatArt kind="jojo" prop="engineer" size={96} title="Jojo child" />
        </div>
      </header>

      <section className="previewSection">
        <div className="sectionHeading">
          <div><p className="eyebrow">Runtime child</p><h2>状态角标</h2></div>
        </div>
        <div className="statusGrid">{CHILD_STATUSES.map(status => <StatusCard key={status} status={status} />)}</div>
      </section>

      <section className="previewSection">
        <div className="sectionHeading">
          <div><p className="eyebrow">Display only</p><h2>Role 道具</h2></div>
          <select value={kind} onChange={event => { setKind(event.target.value as CatKind) }}>
            {CAT_KINDS.map(value => <option key={value} value={value}>{value}</option>)}
          </select>
        </div>
        <div className="effectGrid">{PROPS.map(prop => <CatCard key={prop} kind={kind} prop={prop} />)}</div>
      </section>

      <section className="previewSection">
        <div className="sectionHeading">
          <div><p className="eyebrow">Production panel</p><h2>场景</h2></div>
        </div>
        <div className="scenarioGrid">
          {PANEL_SCENARIOS.map(scenario => (
            <article key={scenario.id} className="scenarioCard">
              <header><strong>{scenario.title}</strong><span>{scenario.description}</span></header>
              <iframe title={scenario.title} src={`?mode=panel&scenario=${encodeURIComponent(scenario.id)}`} />
            </article>
          ))}
        </div>
      </section>
    </main>
  )
}

const root = document.getElementById('root')
if (root === null) throw new Error('preview root missing')
createRoot(root).render(panelScenario === undefined ? <App /> : <PanelScenarioApp scenario={panelScenario} />)
