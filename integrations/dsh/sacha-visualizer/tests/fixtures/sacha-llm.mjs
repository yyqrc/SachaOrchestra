/** Keyless DSH adapter that records a deterministic Sacha workflow slice. */

import { CallId, LlmAdapter } from '@deepseek-ai/dsh-llm'

let nextCall = 0

function calls(messages) {
  return messages.flatMap(message => message.role === 'assistant'
    ? message.content.filter(block => block.type === 'tool-call').map(block => block.name)
    : [])
}

function tool(name, args) {
  const id = CallId(`sacha-visual-smoke-${++nextCall}`)
  const json = JSON.stringify(args)
  return [
    { type: 'block-start', index: 0, blockType: 'tool-call' },
    { type: 'tool-call-delta', index: 0, id, name, argumentsDelta: json },
    { type: 'block-end', index: 0, block: { type: 'tool-call', id, name, arguments: json } },
    { type: 'usage', usage: { inputTokens: 8, outputTokens: 4 } },
    { type: 'finish', reason: { kind: 'tool-calls' } },
  ]
}

function text(value) {
  return [
    { type: 'block-start', index: 0, blockType: 'text' },
    { type: 'text-delta', index: 0, text: value },
    { type: 'block-end', index: 0, block: { type: 'text', text: value } },
    { type: 'usage', usage: { inputTokens: 8, outputTokens: 4 } },
    { type: 'finish', reason: { kind: 'stop' } },
  ]
}

class SachaVisualFixtureAdapter extends LlmAdapter {
  async * stream(options) {
    const count = calls(options.messages).filter(name => name === 'sacha_visual_event').length
    const chunks = count === 0
      ? tool('sacha_visual_event', {
          event_type: 'phase', summary: '进入隔离 Executor 冒烟', phase: 'executor', phase_state: 'entered', scope_revision: 'smoke-r1',
        })
      : count === 1
        ? tool('sacha_visual_event', {
            event_type: 'gate', summary: '隔离冒烟不需要 Reviewer', gate: 'reviewer', gate_decision: 'closed',
          })
        : count === 2
          ? tool('sacha_visual_event', {
              event_type: 'evidence', summary: '隔离 DSH Agent loop 已执行记录工具', evidence_layer: 'runtime', evidence_status: 'verified', references: ['keyless-smoke'],
            })
          : text('SACHA_VISUAL_SMOKE_OK')
    for (const chunk of chunks) {
      options.signal?.throwIfAborted()
      yield chunk
    }
  }
}

export const name = 'sacha-visual-fixture-llm'
export const inject = ['llm']

export function apply(ctx) {
  ctx.llm.registerAdapter(['deepseek-official'], new SachaVisualFixtureAdapter())
}

