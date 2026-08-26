/** Validation and normalization for the model-facing visualization recorder. */

import {
  EVIDENCE_LAYERS, EVIDENCE_STATUSES, GATE_DECISIONS, PHASE_STATES, REVIEW_OUTCOMES,
  SACHA_GATES, SACHA_PHASES, WAVE_STATES,
  type SachaVisualEvent, type VisualEventInput,
} from './types.ts'

const MAX_SUMMARY_CHARS = 400
const MAX_SCOPE_CHARS = 128
const MAX_ID_CHARS = 80
const MAX_REFERENCE_CHARS = 512
const MAX_ITEMS = 32
const MAX_REFERENCES = 10
const STABLE_ID = /^[A-Za-z0-9][A-Za-z0-9._:-]*$/

function oneOf<T extends string>(name: string, value: unknown, values: readonly T[]): T {
  if (typeof value !== 'string' || !values.includes(value as T)) {
    throw new TypeError(`${name} must be one of ${values.join(', ')}`)
  }
  return value as T
}

function text(name: string, value: unknown, maxChars: number): string {
  if (typeof value !== 'string') throw new TypeError(`${name} must be a string`)
  const normalized = value.trim()
  if (normalized.length === 0 || normalized.length > maxChars) {
    throw new TypeError(`${name} must contain 1 through ${maxChars} characters`)
  }
  return normalized
}

function optionalText(name: string, value: unknown, maxChars: number): string | undefined {
  return value === undefined ? undefined : text(name, value, maxChars)
}

function identifiers(name: string, value: unknown): string[] {
  if (!Array.isArray(value) || value.length < 1 || value.length > MAX_ITEMS) {
    throw new TypeError(`${name} must contain 1 through ${MAX_ITEMS} ids`)
  }
  return value.map((item, index) => {
    const id = text(`${name}[${index}]`, item, MAX_ID_CHARS)
    if (!STABLE_ID.test(id)) throw new TypeError(`${name}[${index}] is not a stable id`)
    return id
  })
}

function references(value: unknown): string[] {
  if (value === undefined) return []
  if (!Array.isArray(value) || value.length > MAX_REFERENCES) {
    throw new TypeError(`references must contain at most ${MAX_REFERENCES} entries`)
  }
  return value.map((item, index) => text(`references[${index}]`, item, MAX_REFERENCE_CHARS))
}

/** Convert one tool input into the exact event consumed by the panel. */
export function normalizeVisualEvent(input: VisualEventInput): SachaVisualEvent {
  const summary = text('summary', input.summary, MAX_SUMMARY_CHARS)
  switch (input.event_type) {
    case 'phase': {
      const scopeRevision = optionalText('scope_revision', input.scope_revision, MAX_SCOPE_CHARS)
      return {
        eventType: 'phase',
        summary,
        phase: oneOf('phase', input.phase, SACHA_PHASES),
        state: oneOf('phase_state', input.phase_state, PHASE_STATES),
        ...(scopeRevision === undefined ? {} : { scopeRevision }),
      }
    }
    case 'gate':
      return {
        eventType: 'gate',
        summary,
        gate: oneOf('gate', input.gate, SACHA_GATES),
        decision: oneOf('gate_decision', input.gate_decision, GATE_DECISIONS),
      }
    case 'manager_wave': {
      const waveId = text('wave_id', input.wave_id, MAX_ID_CHARS)
      if (!STABLE_ID.test(waveId)) throw new TypeError('wave_id is not a stable id')
      return {
        eventType: 'manager_wave',
        summary,
        waveId,
        state: oneOf('wave_state', input.wave_state, WAVE_STATES),
        unitIds: identifiers('unit_ids', input.unit_ids),
      }
    }
    case 'review':
      return {
        eventType: 'review',
        summary,
        outcome: oneOf('outcome', input.outcome, REVIEW_OUTCOMES),
      }
    case 'evidence':
      return {
        eventType: 'evidence',
        summary,
        layer: oneOf('evidence_layer', input.evidence_layer, EVIDENCE_LAYERS),
        status: oneOf('evidence_status', input.evidence_status, EVIDENCE_STATUSES),
        references: references(input.references),
      }
    default:
      throw new TypeError(`unsupported event_type ${String(input.event_type)}`)
  }
}

