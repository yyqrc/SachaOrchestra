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
export const MANAGER_UNIT_STATES = ['ready', 'running', 'waiting', 'completed', 'blocked'] as const
export type ManagerUnitState = (typeof MANAGER_UNIT_STATES)[number]
export const DELEGATION_STATES = ['dispatched', 'settled', 'interrupted', 'failed'] as const
export type DelegationState = (typeof DELEGATION_STATES)[number]
export const DELEGATION_ROLES = ['planner', 'explore', 'executor', 'reviewer', 'support'] as const
export type DelegationRole = (typeof DELEGATION_ROLES)[number]
export const REVIEW_OUTCOMES = [
  'accepted', 'accepted_with_follow_up', 'needs_fix', 'needs_replan', 'needs_evidence', 'blocked',
] as const
export type ReviewOutcome = (typeof REVIEW_OUTCOMES)[number]
export const EVIDENCE_LAYERS = ['source', 'package', 'runtime', 'human'] as const
export type EvidenceLayer = (typeof EVIDENCE_LAYERS)[number]
export const EVIDENCE_STATUSES = ['verified', 'failed', 'unverified', 'skipped'] as const
export type EvidenceStatus = (typeof EVIDENCE_STATUSES)[number]
export type VisualEventType = 'phase' | 'gate' | 'manager_wave' | 'delegation' | 'review' | 'evidence'

export interface ManagerUnitInput {
  readonly id: string
  readonly label: string
  readonly state: ManagerUnitState
  readonly blocked_by?: readonly string[]
}

export interface ManagerUnitSnapshot {
  readonly id: string
  readonly label: string
  readonly state: ManagerUnitState
  readonly blockedBy: readonly string[]
}

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
  readonly manager_units?: readonly ManagerUnitInput[]
  readonly unit_id?: string
  readonly child_id?: string
  readonly delegation_state?: DelegationState
  readonly role?: DelegationRole
  readonly surface?: string
  readonly requested_route?: string
  readonly effective_route?: string
  readonly outcome?: ReviewOutcome
  readonly evidence_layer?: EvidenceLayer
  readonly evidence_status?: EvidenceStatus
  readonly references?: readonly string[]
}

export type SachaVisualEvent =
  | { readonly eventType: 'phase'; readonly summary: string; readonly phase: SachaPhase; readonly state: PhaseState; readonly scopeRevision?: string }
  | { readonly eventType: 'gate'; readonly summary: string; readonly gate: SachaGate; readonly decision: GateDecision }
  | { readonly eventType: 'manager_wave'; readonly summary: string; readonly waveId: string; readonly state: WaveState; readonly units: readonly ManagerUnitSnapshot[] }
  | {
      readonly eventType: 'delegation'
      readonly summary: string
      readonly unitId: string
      readonly childId: string
      readonly state: DelegationState
      readonly role?: DelegationRole
      readonly surface?: string
      readonly requestedRoute?: string
      readonly effectiveRoute?: string
    }
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
  readonly delegations: readonly Extract<SachaVisualEvent, { eventType: 'delegation' }>[]
  readonly review?: Extract<SachaVisualEvent, { eventType: 'review' }>
  readonly evidence: Partial<Record<EvidenceLayer, Extract<SachaVisualEvent, { eventType: 'evidence' }>>>
}

export interface SubagentSnapshot {
  readonly id: string
  readonly label: string
  readonly status: 'running' | 'idle' | 'ready'
  readonly hasChildren: boolean
}

export interface SachaActivitySnapshot {
  readonly available: boolean
  readonly sessionId: string
  readonly events: readonly RecordedVisualEvent[]
  readonly state: VisualState
  readonly subagents: {
    readonly available: boolean
    readonly children: readonly SubagentSnapshot[]
  }
  readonly warnings: readonly string[]
}
