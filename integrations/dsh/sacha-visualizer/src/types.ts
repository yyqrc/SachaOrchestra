/** Shared host/client values for Sacha workflow visualization. */

export const SACHA_PHASES = [
  'intake', 'direct', 'planner', 'explore', 'executor', 'reviewer', 'roadmap',
  'document-project', 'closeout', 'feedback', 'human-decision', 'complete', 'blocked',
] as const
export type SachaPhase = (typeof SACHA_PHASES)[number]

export const PHASE_STATES = ['entered', 'waiting', 'completed', 'blocked', 'cancelled'] as const
export type PhaseState = (typeof PHASE_STATES)[number]
export const SACHA_GATES = ['planner', 'manager', 'reviewer'] as const
export type SachaGate = (typeof SACHA_GATES)[number]
export const GATE_DECISIONS = ['open', 'closed'] as const
export type GateDecision = (typeof GATE_DECISIONS)[number]
export const WAVE_STATES = ['planned', 'dispatched', 'waiting', 'completed', 'blocked'] as const
export type WaveState = (typeof WAVE_STATES)[number]
export const REVIEW_OUTCOMES = [
  'accepted', 'accepted_with_follow_up', 'needs_fix', 'needs_replan', 'needs_evidence', 'blocked',
] as const
export type ReviewOutcome = (typeof REVIEW_OUTCOMES)[number]
export const EVIDENCE_LAYERS = ['source', 'package', 'runtime', 'human'] as const
export type EvidenceLayer = (typeof EVIDENCE_LAYERS)[number]
export const EVIDENCE_STATUSES = ['verified', 'failed', 'unverified', 'skipped'] as const
export type EvidenceStatus = (typeof EVIDENCE_STATUSES)[number]
export type VisualEventType = 'phase' | 'gate' | 'manager_wave' | 'review' | 'evidence'

export interface VisualEventInput {
  readonly event_type: VisualEventType
  readonly summary: string
  readonly phase?: SachaPhase
  readonly phase_state?: PhaseState
  readonly scope_revision?: string
  readonly gate?: SachaGate
  readonly gate_decision?: GateDecision
  readonly wave_id?: string
  readonly wave_state?: WaveState
  readonly unit_ids?: readonly string[]
  readonly outcome?: ReviewOutcome
  readonly evidence_layer?: EvidenceLayer
  readonly evidence_status?: EvidenceStatus
  readonly references?: readonly string[]
}

export type SachaVisualEvent =
  | { readonly eventType: 'phase'; readonly summary: string; readonly phase: SachaPhase; readonly state: PhaseState; readonly scopeRevision?: string }
  | { readonly eventType: 'gate'; readonly summary: string; readonly gate: SachaGate; readonly decision: GateDecision }
  | { readonly eventType: 'manager_wave'; readonly summary: string; readonly waveId: string; readonly state: WaveState; readonly unitIds: readonly string[] }
  | { readonly eventType: 'review'; readonly summary: string; readonly outcome: ReviewOutcome }
  | { readonly eventType: 'evidence'; readonly summary: string; readonly layer: EvidenceLayer; readonly status: EvidenceStatus; readonly references: readonly string[] }

export interface RecordedVisualEvent {
  readonly seq: number
  readonly time: number
  readonly value: SachaVisualEvent
}

export interface VisualState {
  readonly phase?: Extract<SachaVisualEvent, { eventType: 'phase' }>
  readonly gates: Partial<Record<SachaGate, Extract<SachaVisualEvent, { eventType: 'gate' }>>>
  readonly waves: readonly Extract<SachaVisualEvent, { eventType: 'manager_wave' }>[]
  readonly review?: Extract<SachaVisualEvent, { eventType: 'review' }>
  readonly evidence: Partial<Record<EvidenceLayer, Extract<SachaVisualEvent, { eventType: 'evidence' }>>>
}

export interface TeamMemberSnapshot {
  readonly id: string
  readonly name: string
  readonly role: 'lead' | 'teammate'
  readonly status: 'running' | 'idle' | 'inactive' | 'provisioning' | 'failed'
  readonly description?: string
  readonly provider?: string
  readonly model?: string
  readonly diagnostics: readonly string[]
}

export interface TeamTaskSnapshot {
  readonly id: string
  readonly revision: number
  readonly subject: string
  readonly description: string
  readonly status: 'pending' | 'in_progress' | 'completed' | 'deleted'
  readonly blockedBy: readonly string[]
  readonly writeScopes: readonly string[]
  readonly ownerName?: string
  readonly ready: boolean
  readonly writeScopeWarnings: readonly string[]
}

export interface SachaActivitySnapshot {
  readonly available: boolean
  readonly sessionId: string
  readonly events: readonly RecordedVisualEvent[]
  readonly state: VisualState
  readonly team: {
    readonly available: boolean
    readonly members: readonly TeamMemberSnapshot[]
    readonly tasks: readonly TeamTaskSnapshot[]
  }
  readonly warnings: readonly string[]
}

