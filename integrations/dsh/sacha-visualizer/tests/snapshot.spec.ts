import { describe, expect, it } from 'vitest'
import { foldVisualState, recordedVisualEvents } from '../src/snapshot.ts'

function call(seq: number, callId: string, args: object) {
  return {
    type: 'tool/call', seq, time: 1_000 + seq,
    data: { callId, name: 'sacha_visual_event', arguments: JSON.stringify(args) },
  }
}

function result(seq: number, callId: string, isError = false) {
  return {
    type: 'tool/result', seq, time: 1_000 + seq,
    data: {
      message: {
        source: { kind: 'tool', callId },
        content: [{ type: 'tool-result', isError }],
      },
      ...(isError ? { error: { message: 'failed' } } : {}),
    },
  }
}

describe('visual event replay', () => {
  it('commits only calls with successful matching tool results', () => {
    const replay = recordedVisualEvents([
      call(0, 'phase', { event_type: 'phase', summary: '进入实施', phase: 'executor', phase_state: 'entered' }),
      result(1, 'phase'),
      call(2, 'failed', { event_type: 'gate', summary: '不会进入状态', gate: 'reviewer', gate_decision: 'open' }),
      result(3, 'failed', true),
      call(4, 'pending', { event_type: 'review', summary: '没有结果', outcome: 'accepted' }),
    ])
    expect(replay.warnings).toEqual([])
    expect(replay.events).toHaveLength(1)
    expect(replay.events[0]?.seq).toBe(1)
    expect(replay.events[0]?.value).toMatchObject({ eventType: 'phase', phase: 'executor' })
  })

  it('folds latest phase, gate, wave, review, and evidence values', () => {
    const replay = recordedVisualEvents([
      call(0, 'p1', { event_type: 'phase', summary: '入口', phase: 'intake', phase_state: 'entered' }), result(1, 'p1'),
      call(2, 'g1', { event_type: 'gate', summary: '需要协调', gate: 'manager', gate_decision: 'open' }), result(3, 'g1'),
      call(4, 'w1', { event_type: 'manager_wave', summary: '派发', wave_id: 'wave-1', wave_state: 'dispatched', unit_ids: ['u1', 'u2'] }), result(5, 'w1'),
      call(6, 'e1', { event_type: 'evidence', summary: 'Runtime 未验证', evidence_layer: 'runtime', evidence_status: 'unverified' }), result(7, 'e1'),
      call(8, 'r1', { event_type: 'review', summary: '需要补证', outcome: 'needs_evidence' }), result(9, 'r1'),
    ])
    const state = foldVisualState(replay.events)
    expect(state.phase?.phase).toBe('intake')
    expect(state.gates.manager?.decision).toBe('open')
    expect(state.waves[0]?.unitIds).toEqual(['u1', 'u2'])
    expect(state.evidence.runtime?.status).toBe('unverified')
    expect(state.review?.outcome).toBe('needs_evidence')
  })
})

