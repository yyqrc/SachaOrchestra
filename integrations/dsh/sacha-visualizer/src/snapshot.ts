/** Fold durable tool calls into the panel's current Sacha state. */

import { normalizeVisualEvent } from './normalize.ts'
import type {
  EvidenceLayer, RecordedVisualEvent, SachaGate, SachaVisualEvent, VisualEventInput, VisualState,
} from './types.ts'

interface EventLike {
  readonly type: string
  readonly seq: number
  readonly time: number
  readonly data: unknown
}

interface PendingCall {
  readonly seq: number
  readonly time: number
  readonly input: VisualEventInput
}

function record(value: unknown): Record<string, unknown> | undefined {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
    ? value as Record<string, unknown>
    : undefined
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

/** Return every successfully recorded event in committed result order. */
export function recordedVisualEvents(events: readonly EventLike[]): { events: RecordedVisualEvent[]; warnings: string[] } {
  const pending = new Map<string, PendingCall>()
  const committed: RecordedVisualEvent[] = []
  const warnings: string[] = []
  for (const event of events) {
    const data = record(event.data)
    if (event.type === 'tool/call' && data?.['name'] === 'sacha_visual_event') {
      const callId = data['callId']
      const args = data['arguments']
      if (typeof callId !== 'string' || typeof args !== 'string') continue
      try {
        pending.set(callId, { seq: event.seq, time: event.time, input: JSON.parse(args) as VisualEventInput })
      } catch {
        warnings.push(`无法解析可视化调用 ${callId}`)
      }
      continue
    }
    if (event.type !== 'tool/result') continue
    const message = record(data?.['message'])
    const source = record(message?.['source'])
    const callId = source?.['kind'] === 'tool' && typeof source['callId'] === 'string' ? source['callId'] : undefined
    if (callId === undefined) continue
    const call = pending.get(callId)
    if (call === undefined) continue
    pending.delete(callId)
    if (!successfulToolResult(event.data, callId)) continue
    try {
      committed.push({ seq: event.seq, time: event.time, value: normalizeVisualEvent(call.input) })
    } catch (error: unknown) {
      warnings.push(`忽略无效可视化调用 ${callId}: ${String(error)}`)
    }
  }
  return { events: committed, warnings }
}

/** Fold the event timeline into current cards without discarding history. */
export function foldVisualState(events: readonly RecordedVisualEvent[]): VisualState {
  let phase: Extract<SachaVisualEvent, { eventType: 'phase' }> | undefined
  let review: Extract<SachaVisualEvent, { eventType: 'review' }> | undefined
  const gates: Partial<Record<SachaGate, Extract<SachaVisualEvent, { eventType: 'gate' }>>> = {}
  const waves = new Map<string, Extract<SachaVisualEvent, { eventType: 'manager_wave' }>>()
  const evidence: Partial<Record<EvidenceLayer, Extract<SachaVisualEvent, { eventType: 'evidence' }>>> = {}
  for (const item of events) {
    const value = item.value
    switch (value.eventType) {
      case 'phase': phase = value; break
      case 'gate': gates[value.gate] = value; break
      case 'manager_wave': waves.set(value.waveId, value); break
      case 'review': review = value; break
      case 'evidence': evidence[value.layer] = value; break
    }
  }
  return {
    ...(phase === undefined ? {} : { phase }),
    gates,
    waves: [...waves.values()],
    ...(review === undefined ? {} : { review }),
    evidence,
  }
}

