import React, { useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import type { ObservableSnapshot, SessionListState } from '@deepseek-ai/dsh-client-runtime/client'
import { ActivityPanel } from '../../src/client/ActivityPanel.tsx'
import panelCss from '../../src/client/ActivityPanel.module.css'
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
const STATUS_DESCRIPTIONS: Record<SubagentSnapshot['status'], string> = {
  running: '正在处理', idle: '暂时空闲', ready: '可以继续',
}
const CAT_LABELS: Record<CatKind, string> = { sacha: 'Sacha', jojo: 'Jojo' }
const PROP_LABELS: Record<CatProp, string> = {
  none: '无道具', conductor: '协调', explore: '探索', research: '调研', engineer: '开发',
  security: '安全', docs: '文档', data: '数据', operator: '运维', design: '设计', qa: '测试',
  working: '工作中', sleeping: '休息', thinking: '思考',
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
        <span>会话内容</span>
        <small>{scenario.title}</small>
      </div>
      <ActivityPanel sessionsList={sessionsList} />
    </div>
  )
}

function CatCard({ kind, prop }: { readonly kind: CatKind; readonly prop: CatProp }): JSX.Element {
  return (
    <article className="effectCard">
      <div className="artStage"><CatArt kind={kind} prop={prop} size={72} title={`${CAT_LABELS[kind]} · ${PROP_LABELS[prop]}`} /></div>
      <strong>{PROP_LABELS[prop]}</strong>
      <span>{CAT_LABELS[kind]}</span>
    </article>
  )
}

function StatusCard({ status }: { readonly status: SubagentSnapshot['status'] }): JSX.Element {
  return (
    <article className="statusCard">
      <div className="artStage">
        <span className={panelCss.childAvatar} data-status={status}>
          <CatArt kind="jojo" prop="engineer" size={58} title="协作任务" />
          <span className={panelCss.statusArt}>
            <MemberStatusArt status={status} size={22} />
          </span>
        </span>
      </div>
      <strong>{STATUS_LABELS[status]}</strong>
      <span>{STATUS_DESCRIPTIONS[status]}</span>
    </article>
  )
}

function App(): JSX.Element {
  const [kind, setKind] = useState<CatKind>('jojo')
  return (
    <main className="previewApp">
      <header className="hero">
        <div>
          <p className="eyebrow">任务协作 · 开发预览</p>
          <h1>任务协作可视化效果台</h1>
          <p>检查猫咪素材、工作状态、任务依赖和异常提示在真实面板中的表现。</p>
        </div>
        <div className="heroCats">
          <CatArt kind="sacha" prop="conductor" size={96} title="Sacha · 协调" />
          <CatArt kind="jojo" prop="engineer" size={96} title="Jojo · 协作" />
        </div>
      </header>

      <section className="previewSection">
        <div className="sectionHeading">
          <div><p className="eyebrow">工作状态</p><h2>状态图标</h2></div>
        </div>
        <div className="statusGrid">{CHILD_STATUSES.map(status => <StatusCard key={status} status={status} />)}</div>
      </section>

      <section className="previewSection">
        <div className="sectionHeading">
          <div><p className="eyebrow">猫咪素材</p><h2>工作道具</h2></div>
          <select value={kind} onChange={event => { setKind(event.target.value as CatKind) }}>
            {CAT_KINDS.map(value => <option key={value} value={value}>{CAT_LABELS[value]}</option>)}
          </select>
        </div>
        <div className="effectGrid">{PROPS.map(prop => <CatCard key={prop} kind={kind} prop={prop} />)}</div>
      </section>

      <section className="previewSection">
        <div className="sectionHeading">
          <div><p className="eyebrow">实际面板</p><h2>典型场景</h2></div>
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

const root = document.getElementById('app')
if (root === null) throw new Error('preview app root missing')
createRoot(root).render(panelScenario === undefined ? <App /> : <PanelScenarioApp scenario={panelScenario} />)
