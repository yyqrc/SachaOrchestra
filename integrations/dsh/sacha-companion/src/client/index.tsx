/** Browser entry registering the Sacha panel in the DSH shell overlay. */

import type { ClientContext } from '@deepseek-ai/dsh-client-runtime/client'
import type {} from '@deepseek-ai/dsh-client-ui-layout/client'
import { ActivityPanel } from './ActivityPanel.tsx'

export const inject = ['slots', 'sessions']

/** Register one session-scoped overlay panel. */
export function apply(ctx: ClientContext): void {
  const Panel = () => <ActivityPanel sessionsList={ctx.sessions.list} />
  ctx.slots.inject('shell.overlay', () => ctx.slots.register({
    name: 'shell.overlay',
    id: 'sacha-visualizer',
    order: 82,
    label: 'Sacha visualization',
  }, Panel))
}

