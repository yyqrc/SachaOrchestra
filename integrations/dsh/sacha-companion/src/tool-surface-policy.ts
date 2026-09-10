/** Task-aware Root tool-surface policy for the DSH companion. */

import type { Context } from '@deepseek-ai/cordis'
import type { Agent } from '@deepseek-ai/dsh-agent'
import { defineTool } from '@deepseek-ai/dsh-tools'
import type { InferValue, ValueSchemaSpec } from '@deepseek-ai/dsh-tools'
import type { JsonValue } from '@deepseek-ai/dsh-util-values'

export const SACHA_TOOLS_NAME = 'sacha_tools'
/**
 * Two-phase Root surface. A session's first request sees only the bootstrap
 * pair, and the first durable signal — a `tool/call` or an `assistant/message`,
 * whichever comes first — opens the resident working set. Phase is derived from
 * durable session events, so resume, reload and context compaction keep it.
 */
export const TOOL_SURFACE_PHASES = ['bootstrap', 'resident'] as const
export type ToolSurfacePhase = (typeof TOOL_SURFACE_PHASES)[number]

export const TOOL_FAMILIES = [
  'filesystem-read',
  'filesystem-write',
  'shell',
  'web',
  'jobs',
  'sacha-delegation',
] as const
export type ToolFamily = (typeof TOOL_FAMILIES)[number]

const MAX_DESCRIPTION_CHARS = 240
const MAX_PARAMETER_DESCRIPTION_CHARS = 160
const MAX_PARAMETERS = 32
const MAX_CATALOG_RESULTS = 24
const DEFAULT_CATALOG_RESULTS = 12
const MAX_QUERY_CHARS = 96

/**
 * First-request surface. Deliberately read-only: it is the smallest set that
 * still lets the model look at the task before its first reply. Promotion
 * opens the resident set on the very next step, so this is a one-step cost
 * rather than a capability ceiling.
 */
const BOOTSTRAP_TOOLS = new Set([
  'read',
  'read_image',
  'glob',
  'grep',
  'sacha_visual_event',
])

/**
 * Working set exposed after the first durable promotion signal or an explicit
 * model phase switch. The three Sacha delegation surfaces live here so a Root
 * session can actually delegate instead of implementing everything itself.
 * Longer-tail tools stay one `sacha_tools` catalog query away.
 */
const RESIDENT_TOOLS = new Set([
  'read',
  'read_image',
  'glob',
  'grep',
  'skill',
  'web_search',
  'ask_user_question',
  'write',
  'edit',
  'bash',
  'pwsh',
  'todo_write',
  'sacha_research',
  'sacha_worker',
  'sacha_review',
  'sacha_visual_event',
])

const DEFAULT_GUIDANCE_OWNERS: Readonly<Record<string, readonly string[]>> = {
  'team:policy': [
    'spawn_teammate', 'send_message', 'followup_task', 'list_agents',
    'wait_agent', 'interrupt_agent', 'team_task_create', 'team_task_list',
    'team_task_get', 'team_task_update',
  ],
  'tool:jobs': ['job_list', 'job_output', 'job_kill'],
  'tool:goal': ['create_goal', 'get_goal', 'update_goal'],
}

interface ToolSchemaLike {
  readonly name: string
  readonly description: string
  readonly parameters: Record<string, unknown>
}

interface EventLike {
  readonly type: string
  readonly seq: number
  readonly time: number
  readonly data: unknown
}

interface MessageLike {
  readonly id?: string
  readonly source?: { readonly kind?: unknown }
  readonly content?: readonly unknown[]
}

export interface ToolParameterMetadata {
  readonly name: string
  readonly type: string
  readonly required: boolean
  readonly description: string
}

export interface ToolCatalogEntry {
  readonly name: string
  readonly description: string
  readonly families: readonly ToolFamily[]
  readonly parameters: readonly ToolParameterMetadata[]
  readonly parametersTruncated: boolean
}

export interface ToolCatalogSnapshot {
  readonly entries: readonly ToolCatalogEntry[]
  readonly sourceCount: number
  readonly truncated: boolean
}

export interface ToolScopeSnapshot {
  readonly catalog: ToolCatalogSnapshot
  readonly inheritedNames: ReadonlySet<string>
}

export interface ToolCatalogResult {
  readonly items: readonly Pick<ToolCatalogEntry, 'name' | 'description' | 'families'>[]
  readonly total: number
  readonly returned: number
  readonly truncated: boolean
}

export interface ToolHelpResult {
  readonly name: string
  readonly description: string
  readonly families: readonly ToolFamily[]
  readonly parameters: readonly ToolParameterMetadata[]
  readonly parametersTruncated: boolean
}

export interface ToolSurfaceRecovery {
  readonly phase: ToolSurfacePhase
  readonly unlocked: readonly string[]
  readonly advertised: readonly string[]
  readonly source: 'control' | 'runtime' | 'bootstrap'
  /**
   * Whether an explicit model phase control was replayed. When true, automatic
   * promotion must not override the model's deliberate choice.
   */
  readonly explicitPhase: boolean
  readonly warnings: readonly string[]
}

/** Serializable state consumed by the Host status route and the Web projection. */
export interface RootToolSurfaceSnapshot {
  readonly sessionId: string
  readonly phase: ToolSurfacePhase
  readonly visibleCount: number
  readonly hiddenCount: number
  readonly visible: readonly string[]
  readonly hidden: readonly string[]
  readonly advertised: readonly string[]
  readonly unlocked: readonly string[]
  readonly source: ToolSurfaceRecovery['source']
  readonly fallback: boolean
  readonly warnings: readonly string[]
}

export interface PromptAssemblyLike {
  readonly sections: readonly { readonly name: string; readonly text: string }[]
  readonly contexts: readonly { readonly name: string; readonly text: string }[]
  readonly tools: readonly ToolSchemaLike[]
  readonly variables: Readonly<Record<string, string | undefined>>
}

export interface RootToolSurfacePolicyOptions {
  /** Extra prompt section -> tool ownership mappings for deployment-specific guidance. */
  readonly guidanceOwners?: Readonly<Record<string, readonly string[]>>
}

export interface RootToolSurfacePolicyHost {
  /** Current state for one live Root Session; non-Root and disposed sessions return undefined. */
  snapshot(sessionId: string): RootToolSurfaceSnapshot | undefined
  /** Current state for every installed live Root Session. */
  snapshots(): RootToolSurfaceSnapshot[]
  /** Idempotently remove all listeners and per-Root policy registrations owned by this install. */
  dispose(): void
}

export interface SurfacePolicyRegistration {
  readonly allowed: ReadonlySet<string>
  dispose(): void
}

export type SurfacePolicyInstaller = (allowed: ReadonlySet<string>) => void

function record(value: unknown): Record<string, unknown> | undefined {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
    ? value as Record<string, unknown>
    : undefined
}

function boundedText(value: unknown, maxChars: number): string {
  if (typeof value !== 'string') return ''
  const normalized = value.replace(/\s+/g, ' ').trim()
  return normalized.length <= maxChars ? normalized : `${normalized.slice(0, maxChars - 1)}…`
}

/**
 * Durable session events that promote a session out of the bootstrap phase.
 * `tool/call` and `assistant/message` are both written by the Runtime itself,
 * so promotion never depends on interpreting human wording.
 */
const PROMOTION_EVENT_TYPES = new Set(['tool/call', 'assistant/message'])

/**
 * Derive the phase from durable session events only. The first promotion
 * signal wins; later events never demote. Context compaction appends a
 * shadowing `user/message` but keeps every original event in the log, so a
 * promoted session stays promoted across compaction.
 *
 * This companion's own control calls are excluded: `sacha_tools` is always
 * visible, so counting it would let a bare `status` query — or the very
 * `phase: 'bootstrap'` narrowing itself — open the working set, and it would
 * turn an explicit single-tool `unlock` into a full promotion.
 */
export function phaseFromEvents(events: readonly EventLike[]): ToolSurfacePhase {
  for (const event of events) {
    if (!PROMOTION_EVENT_TYPES.has(event.type)) continue
    if (event.type === 'tool/call') {
      const data = record(event.data)
      if (data?.['name'] === SACHA_TOOLS_NAME) continue
    }
    return 'resident'
  }
  return 'bootstrap'
}

/** Phase predicate shared by restriction, assembly filtering, guard, and tests. */
export function phaseAllowsTool(phase: ToolSurfacePhase, name: string): boolean {
  return phase === 'bootstrap' ? BOOTSTRAP_TOOLS.has(name) : RESIDENT_TOOLS.has(name)
}

/**
 * Runtime Root identity combines AgentRegistry roots with the native subagent
 * descriptor. Continuable activations are registry roots by construction, so
 * roots() alone is insufficient; durable parentSession is deliberately unused.
 */
export function isLiveRootAgent(
  agent: unknown,
  roots: readonly unknown[],
  events: readonly { readonly type: string }[] = [],
): boolean {
  return roots.some(root => root === agent)
    && !events.some(event => event.type === 'subagent/descriptor')
}

/** Deterministic families used by catalog search and explicit family unlocks. */
export function toolFamilies(name: string): readonly ToolFamily[] {
  const families: ToolFamily[] = []
  if (['read', 'read_image', 'glob', 'grep'].includes(name)) families.push('filesystem-read')
  if (['write', 'edit'].includes(name)) families.push('filesystem-write')
  if (['bash', 'pwsh', 'pty'].includes(name)) families.push('shell')
  if (name === 'web_search' || name === 'web_fetch') families.push('web')
  if (name.startsWith('job_')) families.push('jobs')
  if (['sacha_research', 'sacha_worker', 'sacha_review'].includes(name)) families.push('sacha-delegation')
  return families
}

function parameterType(value: Record<string, unknown>): string {
  if (typeof value['type'] === 'string') return value['type']
  if (Array.isArray(value['enum'])) return 'enum'
  if (Array.isArray(value['oneOf'])) return 'oneOf'
  return 'unknown'
}

function parameterMetadata(parameters: Record<string, unknown>): {
  readonly items: ToolParameterMetadata[]
  readonly truncated: boolean
} {
  const properties = record(parameters['properties']) ?? {}
  const required = new Set(Array.isArray(parameters['required'])
    ? parameters['required'].filter((item): item is string => typeof item === 'string')
    : [])
  const entries = Object.entries(properties).sort(([left], [right]) => left.localeCompare(right))
  const items = entries.slice(0, MAX_PARAMETERS).map(([name, raw]): ToolParameterMetadata => {
    const value = record(raw) ?? {}
    return {
      name,
      type: parameterType(value),
      required: required.has(name) || value['required'] === true,
      description: boundedText(value['description'], MAX_PARAMETER_DESCRIPTION_CHARS),
    }
  })
  return { items, truncated: entries.length > items.length }
}

/** Capture bounded, immutable metadata from the agent's first unrestricted schema view. */
export function createToolCatalog(schemas: readonly ToolSchemaLike[]): ToolCatalogSnapshot {
  const unique = new Map<string, ToolCatalogEntry>()
  for (const schema of schemas) {
    const name = schema.name.trim()
    if (name === '' || name === SACHA_TOOLS_NAME || unique.has(name)) continue
    const parameters = parameterMetadata(schema.parameters)
    unique.set(name, Object.freeze({
      name,
      description: boundedText(schema.description, MAX_DESCRIPTION_CHARS),
      families: Object.freeze([...toolFamilies(name)]),
      parameters: Object.freeze(parameters.items),
      parametersTruncated: parameters.truncated,
    }))
  }
  return Object.freeze({
    entries: Object.freeze([...unique.values()].sort((left, right) => left.name.localeCompare(right.name))),
    sourceCount: schemas.filter(schema => schema.name !== SACHA_TOOLS_NAME).length,
    truncated: schemas.filter(schema => schema.name !== SACHA_TOOLS_NAME).length > unique.size,
  })
}

/** Extend the immutable initial snapshot with late global registrations, preserving its bounds. */
export function mergeToolCatalog(
  catalog: ToolCatalogSnapshot,
  schemas: readonly ToolSchemaLike[],
): ToolCatalogSnapshot {
  const discovered = createToolCatalog(schemas)
  const entries = new Map(catalog.entries.map(entry => [entry.name, entry]))
  for (const entry of discovered.entries) {
    if (!entries.has(entry.name)) entries.set(entry.name, entry)
  }
  if (entries.size === catalog.entries.length) return catalog
  const sorted = [...entries.values()].sort((left, right) => left.name.localeCompare(right.name))
  return Object.freeze({
    entries: Object.freeze(sorted),
    sourceCount: Math.max(catalog.sourceCount, entries.size, discovered.sourceCount),
    truncated: catalog.truncated || discovered.truncated,
  })
}

/**
 * Split inherited from exact-scope tools through the rc.2 public restriction seam.
 * `allow: []` synchronously hides only restrictable inherited tools; exact-scope
 * registrations remain visible and the probe is lifted before any await or model step.
 */
export function captureToolScope(agent: Agent): ToolScopeSnapshot {
  const schemas = agent.ctx.tools.schemas(agent) as ToolSchemaLike[]
  const liftProbe = agent.ctx.tools.restrict({ allow: [] })
  let exactScopeSchemas: ToolSchemaLike[]
  try {
    exactScopeSchemas = agent.ctx.tools.schemas(agent) as ToolSchemaLike[]
  } finally {
    liftProbe()
  }
  const exactScopeNames = new Set(exactScopeSchemas.map(schema => schema.name))
  return {
    catalog: createToolCatalog(schemas),
    inheritedNames: new Set(schemas
      .map(schema => schema.name)
      .filter(name => !exactScopeNames.has(name))),
  }
}

/** Remove this companion's Root control tool from one descendant scope only. */
export function suppressInheritedControlTool(agent: Agent): (() => void) | undefined {
  if (!agent.ctx.tools.schemas(agent).some(schema => schema.name === SACHA_TOOLS_NAME)) return
  return agent.ctx.tools.restrict({ deny: [SACHA_TOOLS_NAME] })
}

/**
 * Match a query against the hidden catalog. Terms are split on whitespace and
 * any term may match, so a natural multi-word query such as "unity editor
 * bridge" still returns the tools it names. A single term keeps the original
 * substring behaviour.
 */
export function searchToolCatalog(
  catalog: ToolCatalogSnapshot,
  query = '',
  requestedLimit = DEFAULT_CATALOG_RESULTS,
): ToolCatalogResult {
  const normalizedQuery = query.trim().toLowerCase()
  if (normalizedQuery.length > MAX_QUERY_CHARS) {
    throw new Error(`catalog query must be at most ${MAX_QUERY_CHARS} characters`)
  }
  const limit = Math.max(1, Math.min(MAX_CATALOG_RESULTS, Math.trunc(requestedLimit)))
  const terms = normalizedQuery === '' ? [] : normalizedQuery.split(/\s+/).filter(term => term !== '')
  const matches = catalog.entries.filter((entry) => {
    if (terms.length === 0) return true
    const haystacks = [
      entry.name.toLowerCase(),
      entry.description.toLowerCase(),
      entry.families.join(' ').toLowerCase(),
    ]
    return terms.some(term => haystacks.some(haystack => haystack.includes(term)))
  })
  const items = matches.slice(0, limit).map(entry => ({
    name: entry.name,
    description: entry.description,
    families: entry.families,
  }))
  return {
    items,
    total: matches.length,
    returned: items.length,
    truncated: catalog.truncated || matches.length > items.length,
  }
}

export function toolHelp(catalog: ToolCatalogSnapshot, name: string): ToolHelpResult | undefined {
  const entry = catalog.entries.find(candidate => candidate.name === name)
  if (entry === undefined) return
  return {
    name: entry.name,
    description: entry.description,
    families: entry.families,
    parameters: entry.parameters,
    parametersTruncated: entry.parametersTruncated,
  }
}

function successfulToolResult(data: unknown, callId: string): boolean {
  const result = record(data)
  if (result === undefined || result['error'] !== undefined) return false
  const message = record(result['message'])
  const source = record(message?.['source'])
  if (source?.['kind'] !== 'tool' || source['callId'] !== callId) return false
  const content = message?.['content']
  if (!Array.isArray(content)) return true
  return !content.some((block) => {
    const value = record(block)
    return value?.['type'] === 'tool-result' && value['isError'] === true
  })
}

function committedControlState(data: unknown): {
  action: string
  unlocked: string[]
  phase?: ToolSurfacePhase
} | undefined {
  const result = record(data)
  const message = record(result?.['message'])
  const content = message?.['content']
  if (!Array.isArray(content)) return
  for (const block of content) {
    const toolResult = record(block)
    if (toolResult?.['type'] !== 'tool-result' || !Array.isArray(toolResult['content'])) continue
    for (const child of toolResult['content']) {
      const text = record(child)
      if (text?.['type'] !== 'text' || typeof text['text'] !== 'string') continue
      try {
        const payload = record(JSON.parse(text['text']))
        const action = payload?.['action']
        const unlocked = payload?.['unlocked']
        const phase = payload?.['phase']
        if (typeof action === 'string' && Array.isArray(unlocked)
          && unlocked.every((name): name is string => typeof name === 'string')) {
          return {
            action,
            unlocked: [...new Set(unlocked)],
            ...(typeof phase === 'string' && (TOOL_SURFACE_PHASES as readonly string[]).includes(phase)
              ? { phase: phase as ToolSurfacePhase }
              : {}),
          }
        }
      } catch {
        continue
      }
    }
  }
  return
}

function controlUnlockNames(
  args: Record<string, unknown>,
  catalog: ToolCatalogSnapshot,
): string[] {
  const result = new Set<string>()
  const requested = args['tools']
  if (Array.isArray(requested)) {
    for (const name of requested) {
      if (typeof name !== 'string' || toolHelp(catalog, name) === undefined) {
        throw new Error(`cannot recover unknown tool ${JSON.stringify(name)}`)
      }
      result.add(name)
    }
  }
  const family = args['family']
  if (family !== undefined) {
    if (typeof family !== 'string' || !TOOL_FAMILIES.includes(family as ToolFamily)) {
      throw new Error(`cannot recover unknown tool family ${JSON.stringify(family)}`)
    }
    for (const entry of catalog.entries) {
      if (entry.families.includes(family as ToolFamily)) result.add(entry.name)
    }
  }
  if (result.size === 0) throw new Error('unlock requires at least one known tool or non-empty family')
  return [...result]
}

/**
 * Rebuild phase, temporary unlocks, and the last advertised header from durable
 * session events. Phase never depends on human wording: it comes from the
 * Runtime's own promotion events, plus any explicit model phase control. Both
 * survive resume, reload and compaction because the underlying events stay in
 * the log.
 */
export function foldToolSurfaceState(
  events: readonly EventLike[],
  catalog: ToolCatalogSnapshot,
): ToolSurfaceRecovery {
  const warnings: string[] = []
  // Automatic promotion is derived from the whole durable log first; an
  // explicit phase control replayed below can still narrow it deliberately.
  let phase: ToolSurfacePhase = phaseFromEvents(events)
  let explicitPhase = false
  let source: ToolSurfaceRecovery['source'] = 'bootstrap'

  const pendingCalls = new Map<string, Record<string, unknown>>()
  const unlocked = new Set<string>()
  let advertised: string[] = []
  for (const event of events) {
    const data = record(event.data)
    if (event.type === 'request/header') {
      const header = record(data?.['header'])
      const tools = header?.['tools']
      if (Array.isArray(tools)) {
        advertised = tools.flatMap((tool) => {
          const schema = record(tool)
          return typeof schema?.['name'] === 'string' ? [schema['name']] : []
        })
      } else {
        advertised = []
      }
      continue
    }
    if (event.type === 'tool/call' && data?.['name'] === SACHA_TOOLS_NAME) {
      const callId = data['callId']
      const rawArguments = data['arguments']
      if (typeof callId !== 'string' || typeof rawArguments !== 'string') continue
      try {
        const args = record(JSON.parse(rawArguments))
        if (args !== undefined) pendingCalls.set(callId, args)
      } catch {
        warnings.push(`ignored malformed ${SACHA_TOOLS_NAME} call ${callId}`)
      }
      continue
    }
    if (event.type !== 'tool/result') continue
    const message = record(data?.['message'])
    const resultSource = record(message?.['source'])
    const callId = resultSource?.['kind'] === 'tool' && typeof resultSource['callId'] === 'string'
      ? resultSource['callId']
      : undefined
    if (callId === undefined) continue
    const args = pendingCalls.get(callId)
    if (args === undefined) continue
    pendingCalls.delete(callId)
    if (!successfulToolResult(event.data, callId)) continue
    try {
      const committed = committedControlState(event.data)
      if (args['action'] === 'phase' && committed?.action === 'phase' && committed.phase !== undefined) {
        phase = committed.phase
        explicitPhase = true
        // Mirror the live controller: an explicit phase control resets the
        // surface, so temporary unlocks are dropped and any control call that
        // started earlier may not re-unlock when its result arrives late.
        unlocked.clear()
        pendingCalls.clear()
        source = 'control'
        continue
      }
      if ((args['action'] === 'unlock' || args['action'] === 'reset')
        && committed?.action === args['action']) {
        unlocked.clear()
        for (const name of committed.unlocked) unlocked.add(name)
        source = 'control'
        continue
      }
      if (args['action'] === 'unlock') {
        if (args['family'] !== undefined) {
          warnings.push(`ignored legacy ${SACHA_TOOLS_NAME} family unlock without committed exact names`)
          continue
        }
        for (const name of controlUnlockNames(args, catalog)) {
          if (!phaseAllowsTool(phase, name)) unlocked.add(name)
        }
        source = 'control'
      } else if (args['action'] === 'reset') {
        unlocked.clear()
        source = 'control'
      }
    } catch (error: unknown) {
      warnings.push(`ignored invalid ${SACHA_TOOLS_NAME} result ${callId}: ${String(error)}`)
    }
  }
  if (catalog.truncated) warnings.push(`tool snapshot truncated at ${catalog.entries.length} entries`)
  return {
    phase,
    unlocked: [...unlocked].sort(),
    advertised: [...new Set(advertised)],
    source,
    explicitPhase,
    warnings,
  }
}

function guidanceOwners(
  sectionName: string,
  configured: Readonly<Record<string, readonly string[]>>,
): readonly string[] | undefined {
  const explicit = configured[sectionName] ?? DEFAULT_GUIDANCE_OWNERS[sectionName]
  if (explicit !== undefined) return explicit
  return sectionName.startsWith('tool:') ? [sectionName.slice('tool:'.length)] : undefined
}

/** Remove same-scope schemas and their known guidance using the same effective allow set. */
export function filterPromptAssembly<T extends PromptAssemblyLike>(
  assembly: T,
  allowed: ReadonlySet<string>,
  configuredGuidanceOwners: Readonly<Record<string, readonly string[]>> = {},
): T {
  const isAllowed = (name: string): boolean => name === SACHA_TOOLS_NAME || allowed.has(name)
  const sections = assembly.sections.filter((section) => {
    const owners = guidanceOwners(section.name, configuredGuidanceOwners)
    return owners === undefined || owners.some(isAllowed)
  })
  return {
    ...assembly,
    sections,
    tools: assembly.tools.filter(tool => isAllowed(tool.name)),
  } as T
}

/** A replacement slot whose install always completes before the prior registration is disposed. */
export class NewFirstPolicySlot {
  private current: SurfacePolicyRegistration | undefined

  replace(install: () => SurfacePolicyRegistration): void {
    const candidate = install()
    const previous = this.current
    this.current = candidate
    previous?.dispose()
  }

  dispose(): void {
    const current = this.current
    this.current = undefined
    current?.dispose()
  }
}

/** Pure state controller; the Host supplies the paired Runtime registration installer. */
export class RootToolSurfaceController {
  private phase: ToolSurfacePhase
  private unlocked: Set<string>
  private advertised: Set<string>
  private readonly warnings: string[]
  private source: ToolSurfaceRecovery['source']
  private fallback = false
  private initialized = false
  private catalogState: ToolCatalogSnapshot
  /**
   * Once the model commits an explicit phase control, automatic promotion stops
   * for this session. Without this flag the live path would re-promote after a
   * deliberate narrowing while the replay path would not, so a resume would
   * disagree with the running session.
   */
  private explicitPhase: boolean

  constructor(
    readonly sessionId: string,
    catalog: ToolCatalogSnapshot,
    recovery: ToolSurfaceRecovery,
    private readonly installPolicy: SurfacePolicyInstaller,
  ) {
    this.catalogState = catalog
    this.phase = recovery.phase
    this.unlocked = new Set(recovery.unlocked)
    this.advertised = new Set(recovery.advertised)
    this.warnings = [...recovery.warnings]
    this.source = recovery.source
    this.explicitPhase = recovery.explicitPhase
  }

  get catalog(): ToolCatalogSnapshot {
    return this.catalogState
  }

  /** Install the first paired policy after the exact-scope control tool exists. */
  activate(): void {
    if (this.initialized) throw new Error('tool-surface controller is already active')
    this.installPolicy(this.effectiveAllow())
    this.initialized = true
    this.fallback = false
  }

  markFallback(message: string): void {
    this.fallback = true
    if (!this.warnings.includes(message)) this.warnings.push(message)
  }

  /** Replace the bounded catalog and atomically reinstall policy from durable state. */
  refreshCatalog(catalog: ToolCatalogSnapshot, recovery: ToolSurfaceRecovery): boolean {
    if (catalog === this.catalogState) return false
    const previousCatalog = this.catalogState
    this.catalogState = catalog
    try {
      this.installPolicy(this.effectiveAllow(recovery.phase, new Set(recovery.unlocked)))
    } catch (error: unknown) {
      this.catalogState = previousCatalog
      throw error
    }
    this.phase = recovery.phase
    this.unlocked = new Set(recovery.unlocked)
    this.advertised = new Set(recovery.advertised)
    this.source = recovery.source
    this.explicitPhase = recovery.explicitPhase
    for (const warning of recovery.warnings) {
      if (!this.warnings.includes(warning)) this.warnings.push(warning)
    }
    this.fallback = false
    return true
  }

  /**
   * Promote on the first durable Runtime signal. The model's own first tool call
   * or first reply is proof that it understood the task, so the surface opens
   * without anyone having to read the human's wording. This companion's own
   * control calls are excluded, matching {@link phaseFromEvents}.
   */
  noteDurableEvent(event: { readonly type: string; readonly data?: unknown }): void {
    if (this.explicitPhase || this.phase === 'resident') return
    if (!PROMOTION_EVENT_TYPES.has(event.type)) return
    if (event.type === 'tool/call' && record(event.data)?.['name'] === SACHA_TOOLS_NAME) return
    this.transition('resident', this.unlocked)
    this.source = 'runtime'
  }

  /**
   * Explicit model phase control. This is the self-rescue path: the model may
   * narrow back to the bootstrap pair or open the resident set immediately
   * without waiting for a promotion signal. Temporary unlocks are cleared so a
   * deliberate narrowing is not silently defeated by an earlier unlock.
   */
  setPhase(phase: ToolSurfacePhase): RootToolSurfaceSnapshot {
    this.transition(phase, new Set())
    this.explicitPhase = true
    this.source = 'control'
    return this.snapshot()
  }

  noteRequestHeader(tools: readonly { readonly name: string }[]): void {
    this.advertised = new Set(tools.map(tool => tool.name))
  }

  guardReason(name: string, allowed = this.effectiveAllow()): string | undefined {
    if (name === SACHA_TOOLS_NAME) return
    if (!allowed.has(name)) return `tool "${name}" is hidden by the active Sacha Root tool surface`
    if (!this.advertised.has(name)) {
      return `tool "${name}" was not advertised in the latest request header; retry only after the next model step exposes it`
    }
    return
  }

  catalogSearch(query?: string, limit?: number): ToolCatalogResult {
    const allowed = this.effectiveAllow()
    const hidden = this.catalog.entries.filter(entry => !allowed.has(entry.name))
    return searchToolCatalog({ entries: hidden, sourceCount: hidden.length, truncated: this.catalog.truncated }, query, limit)
  }

  help(name: string): ToolHelpResult {
    const result = toolHelp(this.catalog, name)
    if (result === undefined) throw new Error(`unknown tool "${name}"`)
    return result
  }

  unlock(names: readonly string[] = [], family?: ToolFamily): RootToolSurfaceSnapshot {
    const requested = controlUnlockNames({ tools: names, ...(family === undefined ? {} : { family }) }, this.catalog)
    const next = new Set(this.unlocked)
    for (const name of requested) {
      if (!phaseAllowsTool(this.phase, name)) next.add(name)
    }
    if (!sameSet(next, this.unlocked)) this.transition(this.phase, next)
    this.source = 'control'
    return this.snapshot()
  }

  reset(): RootToolSurfaceSnapshot {
    if (this.unlocked.size > 0) this.transition(this.phase, new Set())
    this.source = 'control'
    return this.snapshot()
  }

  snapshot(): RootToolSurfaceSnapshot {
    const effective = this.effectiveAllow()
    const visible = this.catalog.entries.filter(entry => effective.has(entry.name)).map(entry => entry.name)
    const hidden = this.catalog.entries.filter(entry => !effective.has(entry.name)).map(entry => entry.name)
    return {
      sessionId: this.sessionId,
      phase: this.phase,
      visibleCount: visible.length + 1,
      hiddenCount: hidden.length,
      visible: [...visible, SACHA_TOOLS_NAME].sort(),
      hidden,
      advertised: [...this.advertised].sort(),
      unlocked: [...this.unlocked].sort(),
      source: this.source,
      fallback: this.fallback,
      warnings: [...this.warnings],
    }
  }

  effectiveAllow(
    phase: ToolSurfacePhase = this.phase,
    unlocked: ReadonlySet<string> = this.unlocked,
  ): ReadonlySet<string> {
    return new Set(this.catalog.entries
      .filter(entry => phaseAllowsTool(phase, entry.name) || unlocked.has(entry.name))
      .map(entry => entry.name))
  }

  private transition(phase: ToolSurfacePhase, unlocked: ReadonlySet<string>): void {
    const allowed = this.effectiveAllow(phase, unlocked)
    this.installPolicy(allowed)
    this.phase = phase
    this.unlocked = new Set(unlocked)
    this.fallback = false
  }
}

function sameSet(left: ReadonlySet<string>, right: ReadonlySet<string>): boolean {
  return left.size === right.size && [...left].every(item => right.has(item))
}

function jsonOutput<const S extends ValueSchemaSpec>(schema: S): {
  schema: S
  render: (args: unknown, value: InferValue<S>) => [{ type: 'text'; text: string }]
} {
  return {
    schema,
    render: (_args, value) => [{ type: 'text', text: JSON.stringify(value) }],
  }
}

const TOOL_RESULT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    action: { type: 'string', required: true },
    phase: { type: 'string', required: true, enum: [...TOOL_SURFACE_PHASES] },
    visible_count: { type: 'integer', required: true },
    hidden_count: { type: 'integer', required: true },
    source: { type: 'string', required: true, enum: ['control', 'runtime', 'bootstrap'] },
    unlocked: { type: 'array', required: true, items: { type: 'string' } },
    fallback: { type: 'boolean', required: true },
    warnings: { type: 'array', required: true, items: { type: 'string' } },
    catalog: { type: 'json' },
    help: { type: 'json' },
    notice: { type: 'string' },
  },
} as const

type ControlToolValue = InferValue<typeof TOOL_RESULT_SCHEMA>

function jsonValue(value: unknown): JsonValue {
  return JSON.parse(JSON.stringify(value)) as JsonValue
}

function toolResult(
  action: string,
  snapshot: RootToolSurfaceSnapshot,
  extra: Partial<Pick<ControlToolValue, 'catalog' | 'help' | 'notice'>> = {},
): ControlToolValue {
  return {
    action,
    phase: snapshot.phase,
    visible_count: snapshot.visibleCount,
    hidden_count: snapshot.hiddenCount,
    source: snapshot.source,
    unlocked: [...snapshot.unlocked],
    fallback: snapshot.fallback,
    warnings: [...snapshot.warnings],
    ...extra,
  }
}

const CONTROL_ACTIONS = ['status', 'catalog', 'help', 'phase', 'unlock', 'reset'] as const

function createControlTool(controller: RootToolSurfaceController) {
  return defineTool({
    name: SACHA_TOOLS_NAME,
    description: 'Inspect the current Root tool surface, search bounded hidden-tool metadata, choose the working phase, unlock known tools for the next model step, or reset temporary unlocks. This changes visibility only and grants no authority.',
    parameters: {
      action: { type: 'string', required: true, enum: [...CONTROL_ACTIONS] },
      query: { type: 'string', description: 'Catalog search terms; used only with catalog. Multiple words match any word across a tool name, description, or family.' },
      name: { type: 'string', description: 'Exact tool name; required with help.' },
      phase: { type: 'string', enum: [...TOOL_SURFACE_PHASES], description: 'Working phase to adopt: bootstrap keeps the minimal read-only pair, resident opens the standard working set. Used only with phase.' },
      tools: { type: 'array', items: { type: 'string' }, description: 'Exact snapshot tool names to unlock.' },
      family: { type: 'string', enum: [...TOOL_FAMILIES], description: 'Defined tool family to unlock.' },
      limit: { type: 'integer', description: `Catalog result limit, clamped to 1-${MAX_CATALOG_RESULTS}.` },
    },
    output: jsonOutput(TOOL_RESULT_SCHEMA),
    execute(args) {
      if (args.action === 'status') return Promise.resolve(toolResult('status', controller.snapshot()))
      if (args.action === 'catalog') {
        const catalog = controller.catalogSearch(args.query, args.limit)
        return Promise.resolve(toolResult('catalog', controller.snapshot(), { catalog: jsonValue(catalog) }))
      }
      if (args.action === 'help') {
        if (args.name === undefined) throw new Error('help requires name')
        return Promise.resolve(toolResult('help', controller.snapshot(), { help: jsonValue(controller.help(args.name)) }))
      }
      if (args.action === 'phase') {
        if (args.phase === undefined) throw new Error('phase requires phase')
        return Promise.resolve(toolResult('phase', controller.setPhase(args.phase), {
          notice: 'The chosen phase applies from the next model step, once a later request header advertises it.',
        }))
      }
      if (args.action === 'unlock') {
        return Promise.resolve(toolResult('unlock', controller.unlock(args.tools ?? [], args.family), {
          notice: 'Unlocked tools become callable only after a later request header advertises them.',
        }))
      }
      return Promise.resolve(toolResult('reset', controller.reset()))
    },
  })
}

function installComposite(factories: readonly (() => () => void)[]): () => void {
  const disposers: Array<() => void> = []
  try {
    for (const factory of factories) disposers.push(factory())
  } catch (error: unknown) {
    for (const dispose of disposers.reverse()) dispose()
    throw error
  }
  let disposed = false
  return () => {
    if (disposed) return
    disposed = true
    for (const dispose of disposers.reverse()) dispose()
  }
}

function requestHeaderTools(event: EventLike): { name: string }[] | undefined {
  if (event.type !== 'request/header') return
  const data = record(event.data)
  const header = record(data?.['header'])
  const tools = header?.['tools']
  if (!Array.isArray(tools)) return []
  return tools.flatMap((tool) => {
    const schema = record(tool)
    return typeof schema?.['name'] === 'string' ? [{ name: schema['name'] }] : []
  })
}

function installForRoot(
  agent: Agent,
  options: RootToolSurfacePolicyOptions,
): { readonly controller: RootToolSurfaceController; dispose(): void } {
  const scope = captureToolScope(agent)
  const catalog = scope.catalog
  const inheritedNames = new Set(scope.inheritedNames)
  const recovery = foldToolSurfaceState(agent.session.snapshotEvents() as readonly EventLike[], catalog)
  const slot = new NewFirstPolicySlot()
  let controller: RootToolSurfaceController
  const installer: SurfacePolicyInstaller = (allowed) => {
    const allowedSnapshot = new Set(allowed)
    const inheritedAllow = [...allowedSnapshot].filter(name => inheritedNames.has(name))
    const dispose = installComposite([
      () => agent.ctx.tools.restrict({ allow: inheritedAllow }),
      () => agent.ctx.on('system-prompt/assemble', async (_assembly, _context, next) => {
        const assembled = await next()
        return filterPromptAssembly(assembled, allowedSnapshot, options.guidanceOwners)
      }),
      () => agent.ctx.tools.guard(exec => controller.guardReason(exec.name, allowedSnapshot)),
    ])
    const registration: SurfacePolicyRegistration = { allowed: allowedSnapshot, dispose }
    slot.replace(() => registration)
  }
  controller = new RootToolSurfaceController(String(agent.id), catalog, recovery, installer)
  const disposeTool = agent.ctx.tools.register(createControlTool(controller))
  try {
    controller.activate()
  } catch (error: unknown) {
    const message = `inherited restriction unavailable; assembly and execution remain fail-closed: ${String(error)}`
    controller.markFallback(message)
    const allowed = controller.effectiveAllow()
    const fallback = installComposite([
      () => agent.ctx.on('system-prompt/assemble', async (_assembly, _context, next) => {
        const assembled = await next()
        return filterPromptAssembly(assembled, allowed, options.guidanceOwners)
      }),
      () => agent.ctx.tools.guard(exec => controller.guardReason(exec.name, allowed)),
    ])
    slot.replace(() => ({ allowed, dispose: fallback }))
  }

  const stopSession = agent.ctx.on('session/event', (_session, event) => {
    const headerTools = requestHeaderTools(event as EventLike)
    if (headerTools !== undefined) controller.noteRequestHeader(headerTools)
    // Promotion reads the Runtime's own durable signals, never human wording.
    controller.noteDurableEvent(event as EventLike)
  })
  const stopTools = agent.ctx.on('tools/change', () => {
    const globalSchemas = agent.ctx.tools.schemas() as ToolSchemaLike[]
    const merged = mergeToolCatalog(controller.catalog, globalSchemas)
    if (merged === controller.catalog) return
    for (const schema of globalSchemas) inheritedNames.add(schema.name)
    try {
      controller.refreshCatalog(
        merged,
        foldToolSurfaceState(agent.session.snapshotEvents() as readonly EventLike[], merged),
      )
    } catch (error: unknown) {
      controller.markFallback(`late tool-catalog refresh failed closed: ${String(error)}`)
    }
  })
  return {
    controller,
    dispose: installComposite([
      () => stopSession,
      () => stopTools,
      () => () => slot.dispose(),
      () => disposeTool,
    ]),
  }
}

/** Install the companion policy for all live roots and future roots after composition completes. */
export function installRootToolSurfacePolicy(
  ctx: Context,
  options: RootToolSurfacePolicyOptions = {},
): RootToolSurfacePolicyHost {
  const installed = new Map<Agent, ReturnType<typeof installForRoot>>()
  const suppressedChildren = new Map<Agent, () => void>()
  const bySessionId = new Map<string, RootToolSurfaceController>()
  let disposed = false
  const isRoot = (agent: Agent): boolean => isLiveRootAgent(
    agent,
    ctx.agents.roots(),
    agent.session.snapshotEvents() as readonly EventLike[],
  )

  const maybeInstall = (agent: Agent): ReturnType<typeof installForRoot> | undefined => {
    if (disposed || !isRoot(agent)) return
    const existing = installed.get(agent)
    if (existing !== undefined) return existing
    const runtime = installForRoot(agent, options)
    installed.set(agent, runtime)
    bySessionId.set(String(agent.id), runtime.controller)
    return runtime
  }
  const maybeSuppressChild = (agent: Agent): void => {
    if (disposed || suppressedChildren.has(agent) || isRoot(agent)) return
    const dispose = suppressInheritedControlTool(agent)
    if (dispose !== undefined) suppressedChildren.set(agent, dispose)
  }
  for (const agent of ctx.agents.list()) {
    if (isRoot(agent)) maybeInstall(agent)
    else maybeSuppressChild(agent)
  }
  const stopStarted = ctx.on('agent/session-start', ({ agent }) => {
    if (isRoot(agent)) maybeInstall(agent)
    else maybeSuppressChild(agent)
  })
  const stopInbox = ctx.on('agent/inbox/inserted', ({ agent }) => {
    // A new human turn installs the policy for a not-yet-seen Root, but it no
    // longer selects a phase: the phase follows durable Runtime signals.
    maybeInstall(agent)
  })
  const stopDisposed = ctx.on('agent/disposed', ({ agent }) => {
    suppressedChildren.delete(agent)
    const runtime = installed.get(agent)
    if (runtime === undefined) return
    installed.delete(agent)
    bySessionId.delete(String(agent.id))
    runtime.dispose()
  })

  const dispose = (): void => {
    if (disposed) return
    disposed = true
    stopStarted()
    stopInbox()
    stopDisposed()
    for (const runtime of installed.values()) runtime.dispose()
    for (const suppress of suppressedChildren.values()) suppress()
    installed.clear()
    suppressedChildren.clear()
    bySessionId.clear()
  }
  return {
    snapshot(sessionId) {
      return bySessionId.get(sessionId)?.snapshot()
    },
    snapshots() {
      return [...bySessionId.values()].map(controller => controller.snapshot())
    },
    dispose,
  }
}

