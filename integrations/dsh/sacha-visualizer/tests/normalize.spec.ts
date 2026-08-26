import { describe, expect, it } from 'vitest'
import { normalizeVisualEvent } from '../src/normalize.ts'

describe('normalizeVisualEvent', () => {
  it('normalizes each supported committed event category', () => {
    expect(normalizeVisualEvent({
      event_type: 'phase', summary: ' 进入 Executor ', phase: 'executor', phase_state: 'entered', scope_revision: 'r2',
    })).toEqual({ eventType: 'phase', summary: '进入 Executor', phase: 'executor', state: 'entered', scopeRevision: 'r2' })
    expect(normalizeVisualEvent({
      event_type: 'gate', summary: '需要独立复核', gate: 'reviewer', gate_decision: 'open',
    })).toEqual({ eventType: 'gate', summary: '需要独立复核', gate: 'reviewer', decision: 'open' })
    expect(normalizeVisualEvent({
      event_type: 'manager_wave', summary: '并行派发', wave_id: 'wave-1', wave_state: 'dispatched', unit_ids: ['u1', 'u2'],
    })).toEqual({ eventType: 'manager_wave', summary: '并行派发', waveId: 'wave-1', state: 'dispatched', unitIds: ['u1', 'u2'] })
    expect(normalizeVisualEvent({
      event_type: 'review', summary: '通过并保留跟进项', outcome: 'accepted_with_follow_up',
    })).toEqual({ eventType: 'review', summary: '通过并保留跟进项', outcome: 'accepted_with_follow_up' })
    expect(normalizeVisualEvent({
      event_type: 'evidence', summary: '源码验证通过', evidence_layer: 'source', evidence_status: 'verified', references: ['tests/output.json'],
    })).toEqual({ eventType: 'evidence', summary: '源码验证通过', layer: 'source', status: 'verified', references: ['tests/output.json'] })
  })

  it('rejects incomplete and unbounded records', () => {
    expect(() => normalizeVisualEvent({ event_type: 'phase', summary: 'x' })).toThrow(/phase/)
    expect(() => normalizeVisualEvent({
      event_type: 'manager_wave', summary: 'x', wave_id: 'bad id', wave_state: 'planned', unit_ids: ['u1'],
    })).toThrow(/stable id/)
    expect(() => normalizeVisualEvent({
      event_type: 'evidence', summary: 'x', evidence_layer: 'source', evidence_status: 'verified', references: Array(11).fill('x'),
    })).toThrow(/at most 10/)
  })
})

