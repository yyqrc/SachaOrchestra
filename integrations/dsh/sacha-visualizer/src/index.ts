/** DSH host plugin exposing the Sacha recorder and current-session snapshot route. */

import type { Context } from '@deepseek-ai/cordis'
import type { Agent } from '@deepseek-ai/dsh-agent'
import { SessionId } from '@deepseek-ai/dsh-session'
import type { SubagentListEntry } from '@deepseek-ai/dsh-subagent'
import z from '@deepseek-ai/schemastery'
import { defineTool } from '@deepseek-ai/dsh-tools'
import type { InferValue, ValueSchemaSpec } from '@deepseek-ai/dsh-tools'
import type { IncomingMessage, ServerResponse } from 'node:http'
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { normalizeVisualEvent } from './normalize.ts'
import { foldVisualState, recordedVisualEvents } from './snapshot.ts'
import type { SachaActivitySnapshot, SubagentSnapshot, VisualEventInput } from './types.ts'

interface WebRouteHost {
  register(route: {
    kind: 'exact' | 'prefix'
    path: string
    handler: (req: IncomingMessage, res: ServerResponse) => void | Promise<void>
  }): () => void
}

const WEB_SERVER_KEYS = ['webServer', 'httpServer'] as const
const ART_DIRECTORY = fileURLToPath(new URL('../assets/cats/', import.meta.url))
const ART_ALLOWLIST = new Set(['cat-sacha-base.png', 'cat-jojo-base.png'])
export const name = 'sacha-visualizer'
export const inject = ['agents', 'sessions', 'subagents', 'tools']

const EVENT_OUTPUT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    recorded: { type: 'boolean', required: true, const: true },
    eventType: {
      type: 'string',
      required: true,
      enum: ['phase', 'gate', 'manager_wave', 'review', 'evidence'],
    },
  },
} as const

function jsonOutput<const S extends ValueSchemaSpec>(schema: S): {
  schema: S
  render: (args: unknown, value: InferValue<S>) => [{ type: 'text'; text: string }]
} {
  return {
    schema,
    render: (_args, value) => [{ type: 'text', text: JSON.stringify(value) }],
  }
}

const visualEventTool = defineTool({
  name: 'sacha_visual_event',
  description: 'Record one already-committed Sacha workflow transition for the optional DSH visualization. This never changes Sacha routing, authorization, review, or completion.',
  parameters: {
    event_type: {
      type: 'string', required: true,
      enum: ['phase', 'gate', 'manager_wave', 'review', 'evidence'],
      description: 'Committed transition category.',
    },
    summary: { type: 'string', required: true, description: 'Concise Human-facing Chinese summary.' },
    phase: { type: 'string', enum: ['intake', 'direct', 'planner', 'explore', 'executor', 'reviewer', 'roadmap', 'document-project', 'closeout', 'feedback', 'human-decision', 'complete', 'blocked'] },
    phase_state: { type: 'string', enum: ['entered', 'waiting', 'completed', 'blocked', 'cancelled'] },
    scope_revision: { type: 'string' },
    gate: { type: 'string', enum: ['planner', 'manager', 'reviewer'] },
    gate_decision: { type: 'string', enum: ['open', 'closed'] },
    wave_id: { type: 'string' },
    wave_state: { type: 'string', enum: ['planned', 'dispatched', 'waiting', 'completed', 'blocked'] },
    unit_ids: { type: 'array', items: { type: 'string' } },
    outcome: { type: 'string', enum: ['accepted', 'accepted_with_follow_up', 'needs_fix', 'needs_replan', 'needs_evidence', 'blocked'] },
    evidence_layer: { type: 'string', enum: ['source', 'package', 'runtime', 'human'] },
    evidence_status: { type: 'string', enum: ['verified', 'failed', 'unverified', 'skipped'] },
    references: { type: 'array', items: { type: 'string' } },
  },
  output: jsonOutput(EVENT_OUTPUT_SCHEMA),
  execute(args) {
    const value = normalizeVisualEvent(args as VisualEventInput)
    return Promise.resolve({ recorded: true as const, eventType: value.eventType })
  },
})

function childStatus(agents: { get(id: ReturnType<typeof SessionId>): Agent | undefined }, id: ReturnType<typeof SessionId>): SubagentSnapshot['status'] {
  const agent = agents.get(id)
  if (agent === undefined) return 'ready'
  return agent.status === 'running' ? 'running' : 'idle'
}

async function readSubagents(ctx: Context, parentSessionId: ReturnType<typeof SessionId>): Promise<{
  readonly subagents: SachaActivitySnapshot['subagents']
  readonly warnings: readonly string[]
}> {
  try {
    const entries = await ctx.subagents.listChildren(parentSessionId)
    const children: SubagentSnapshot[] = []
    const warnings: string[] = []
    for (const entry of entries as readonly SubagentListEntry[]) {
      if (entry.kind === 'diagnostic') {
        warnings.push(`subagent ${String(entry.id)} 无法读取：${entry.reason}`)
        continue
      }
      if (entry.mode !== 'continuable') continue
      children.push({
        id: String(entry.id),
        label: entry.label,
        status: childStatus(ctx.agents, entry.id),
        hasChildren: entry.hasChildren,
      })
      if (entry.hasChildren) warnings.push(`subagent ${String(entry.id)} 观察到下级 child；Sacha 单层派发约束需要复核`)
    }
    return { subagents: { available: true, children }, warnings }
  } catch (error: unknown) {
    return {
      subagents: { available: false, children: [] },
      warnings: [`读取 continuable subagent 状态失败：${String(error)}`],
    }
  }
}

function json(res: ServerResponse, status: number, body: unknown): void {
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'cache-control': 'no-store',
  })
  res.end(JSON.stringify(body))
}

/** Register the recorder immediately and the Web route when its optional service appears. */
export function apply(ctx: Context): void {
  ctx.effect(() => ctx.tools.register(visualEventTool), 'sacha-visualizer: recorder tool')

  let webRegistered = false
  const registerWeb = (): void => {
    if (webRegistered) return
    const webServer = (ctx.get(WEB_SERVER_KEYS[0]) ?? ctx.get(WEB_SERVER_KEYS[1])) as WebRouteHost | undefined
    if (webServer === undefined) return
    webRegistered = true
    ctx.effect(() => webServer.register({
      kind: 'exact',
      path: '/plugins/sacha-visualizer/state',
      handler: async (req, res) => {
        const url = new URL(req.url ?? '/', 'http://localhost')
        const rawSessionId = url.searchParams.get('sessionId')?.trim()
        if (rawSessionId === undefined || rawSessionId === '') {
          json(res, 400, { error: 'sessionId is required' })
          return
        }
        const sessionId = SessionId(rawSessionId)
        const session = ctx.sessions.get(sessionId)
        if (session === undefined) {
          json(res, 404, { error: 'session is not live' })
          return
        }
        const folded = recordedVisualEvents(session.events)
        const observed = await readSubagents(ctx, sessionId)
        const snapshot: SachaActivitySnapshot = {
          available: true,
          sessionId: rawSessionId,
          events: folded.events,
          state: foldVisualState(folded.events),
          subagents: observed.subagents,
          warnings: [...folded.warnings, ...observed.warnings],
        }
        json(res, 200, snapshot)
      },
    }), 'sacha-visualizer: state route')
    ctx.effect(() => webServer.register({
      kind: 'prefix',
      path: '/plugins/sacha-visualizer/assets',
      handler: async (req, res) => {
        let filename: string
        try {
          filename = decodeURIComponent(new URL(req.url ?? '/', 'http://localhost').pathname.split('/').pop() ?? '')
        } catch {
          res.writeHead(404); res.end(); return
        }
        if (!ART_ALLOWLIST.has(filename)) {
          res.writeHead(404); res.end(); return
        }
        try {
          const content = await readFile(join(ART_DIRECTORY, filename))
          res.writeHead(200, { 'content-type': 'image/png', 'cache-control': 'public, max-age=86400' })
          res.end(content)
        } catch (error: unknown) {
          ctx.logger.warn(`sacha-visualizer: cat artwork read failed for ${filename}: ${String(error)}`)
          res.writeHead(404); res.end()
        }
      },
    }), 'sacha-visualizer: artwork route')
  }

  registerWeb()
  ctx.on('internal/service', (serviceName) => {
    if (WEB_SERVER_KEYS.includes(serviceName as (typeof WEB_SERVER_KEYS)[number])) registerWeb()
  })
}
