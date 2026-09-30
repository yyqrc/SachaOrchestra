/** Browser entry registering the Sacha panel in the DSH shell overlay. */

import type { Context } from '@deepseek-ai/cordis'
import type { ISessions } from '@deepseek-ai/dsh-api-session-controller/client'
import type {} from '@deepseek-ai/dsh-client-ui-layout/client'
import type {} from '@deepseek-ai/dsh-client-ui-renderer/client'
import type {} from '@deepseek-ai/dsh-client-ui-session/client'
import type {} from '@deepseek-ai/dsh-client-ui-slots'
import { ActivityPanel } from './ActivityPanel.tsx'

export const inject = ['slots', 'sessions']

/** Client face: the merged cordis Context with the client-side sessions service. */
type ClientContext = Context & { sessions: ISessions }

/**
 * 本插件自己的会话作用域座位。
 *
 * `shell.overlay` 是 root 作用域，拿不到会话身份；而 0.2.0 起
 * `ISessions` 已不再向功能插件暴露"当前会话"。声明这个会话作用域子座位后，
 * 框架会向宿主条目注入 `SessionProvider`，由 ui-session 供给当前 Controller 绑定。
 */
declare module '@deepseek-ai/dsh-client-ui-slots' {
  interface SlotMap {
    'sacha.activity': { kind: 'single'; scope: 'session' }
  }
}

/** Session-scoped body: `sessionId` comes from ui-session's standard kit. */
function ActivitySeat({ sessionId }: { readonly sessionId: string }): JSX.Element {
  return <ActivityPanel sessionId={sessionId} />
}

/** Register one session-scoped overlay panel. */
export function apply(ctx: ClientContext): void {
  ctx.slots.inject('shell.overlay', () => {
    // 宿主条目先声明子座位，子条目才可注册进该座位。
    const disposeOverlay = ctx.slots.register({
      name: 'shell.overlay',
      id: 'sacha-visualizer',
      order: 82,
      label: 'Sacha visualization',
      children: { 'sacha.activity': { kind: 'single', scope: 'session' } },
    }, props => (
      <props.SessionProvider>
        {props.renderSlot('sacha.activity', {})}
      </props.SessionProvider>
    ))
    const disposeSeat = ctx.slots.register({ name: 'sacha.activity' }, ActivitySeat)
    return () => {
      disposeSeat()
      disposeOverlay()
    }
  })
}
