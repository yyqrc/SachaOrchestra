/** Validation and normalization for the model-facing visualization recorder. */

import {
  DELEGATION_ROLES, DELEGATION_STATES, EVIDENCE_LAYERS, EVIDENCE_STATUSES, GATE_DECISIONS,
  MANAGER_UNIT_STATES, PHASE_STATES, REVIEW_OUTCOMES, SACHA_GATES, SACHA_PHASES, WAVE_STATES,
  type ManagerUnitSnapshot, type SachaVisualEvent, type VisualEventInput,
} from './types.ts'

const MAX_SUMMARY_CHARS = 400
const MAX_SCOPE_CHARS = 128
const MAX_ID_CHARS = 80
const MAX_LABEL_CHARS = 180
const MAX_ROUTE_CHARS = 180
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

function stableId(name: string, value: unknown): string {
  const id = text(name, value, MAX_ID_CHARS)
  if (!STABLE_ID.test(id)) throw new TypeError(`${name} is not a stable id`)
  return id
}

function identifiers(name: string, value: unknown, allowEmpty = false): string[] {
  if (!Array.isArray(value) || value.length > MAX_ITEMS || (!allowEmpty && value.length < 1)) {
    throw new TypeError(`${name} must contain ${allowEmpty ? '0' : '1'} through ${MAX_ITEMS} ids`)
  }
  return value.map((item, index) => stableId(`${name}[${index}]`, item))
}

function references(value: unknown): string[] {
  if (value === undefined) return []
  if (!Array.isArray(value) || value.length > MAX_REFERENCES) {
    throw new TypeError(`references must contain at most ${MAX_REFERENCES} entries`)
  }
  return value.map((item, index) => text(`references[${index}]`, item, MAX_REFERENCE_CHARS))
}

function record(value: unknown): Record<string, unknown> {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    throw new TypeError('manager_units entries must be objects')
  }
  return value as Record<string, unknown>
}

function managerUnits(value: unknown): ManagerUnitSnapshot[] {
  if (!Array.isArray(value) || value.length < 1 || value.length > MAX_ITEMS) {
    throw new TypeError(`manager_units must contain 1 through ${MAX_ITEMS} units`)
  }
  const units = value.map((raw, index): ManagerUnitSnapshot => {
    const item = record(raw)
    return {
      id: stableId(`manager_units[${index}].id`, item['id']),
      label: text(`manager_units[${index}].label`, item['label'], MAX_LABEL_CHARS),
      state: oneOf(`manager_units[${index}].state`, item['state'], MANAGER_UNIT_STATES),
      blockedBy: item['blocked_by'] === undefined
        ? []
        : identifiers(`manager_units[${index}].blocked_by`, item['blocked_by'], true),
    }
  })
  const byId = new Map<string, ManagerUnitSnapshot>()
  for (const unit of units) {
    if (byId.has(unit.id)) throw new TypeError(`manager_units contains duplicate id ${unit.id}`)
    byId.set(unit.id, unit)
  }
  for (const unit of units) {
    for (const dependency of unit.blockedBy) {
      if (dependency === unit.id) throw new TypeError(`manager unit ${unit.id} cannot depend on itself`)
      if (!byId.has(dependency)) throw new TypeError(`manager unit ${unit.id} depends on unknown unit ${dependency}`)
    }
  }
  const visiting = new Set<string>()
  const visited = new Set<string>()
  const visit = (id: string): void => {
    if (visited.has(id)) return
    if (visiting.has(id)) throw new TypeError('manager_units dependency graph contains a cycle')
    visiting.add(id)
    for (const dependency of byId.get(id)?.blockedBy ?? []) visit(dependency)
    visiting.delete(id)
    visited.add(id)
  }
  for (const unit of units) visit(unit.id)
  return units
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
    case 'manager_wave':
      return {
        eventType: 'manager_wave',
        summary,
        waveId: stableId('wave_id', input.wave_id),
        state: oneOf('wave_state', input.wave_state, WAVE_STATES),
        units: managerUnits(input.manager_units),
      }
    case 'delegation': {
      const role = input.role === undefined ? undefined : oneOf('role', input.role, DELEGATION_ROLES)
      const surface = optionalText('surface', input.surface, MAX_ID_CHARS)
      const requestedRoute = optionalText('requested_route', input.requested_route, MAX_ROUTE_CHARS)
      const effectiveRoute = optionalText('effective_route', input.effective_route, MAX_ROUTE_CHARS)
      return {
        eventType: 'delegation',
        summary,
        unitId: stableId('unit_id', input.unit_id),
        childId: stableId('child_id', input.child_id),
        state: oneOf('delegation_state', input.delegation_state, DELEGATION_STATES),
        ...(role === undefined ? {} : { role }),
        ...(surface === undefined ? {} : { surface }),
        ...(requestedRoute === undefined ? {} : { requestedRoute }),
        ...(effectiveRoute === undefined ? {} : { effectiveRoute }),
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
