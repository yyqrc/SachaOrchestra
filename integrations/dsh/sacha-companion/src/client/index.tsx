/** Browser entry registering the Sacha panel in the DSH shell overlay. */

import type { Context } from '@deepseek-ai/cordis'
import type { ISessions } from '@deepseek-ai/dsh-api-session-controller/client'
import type {} from '@deepseek-ai/dsh-client-ui-layout/client'
import type {} from '@deepseek-ai/dsh-client-ui-renderer/client'
import { ActivityPanel } from './ActivityPanel.tsx'

export const inject = ['slots', 'sessions']

/** Client face: the merged cordis Context with the client-side sessions service. */
type ClientContext = Context & { sessions: ISessions }

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

