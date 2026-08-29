/** Compact continuable-subagent state symbols shown above child avatars. */

import type { JSX } from 'react'
import type { SubagentSnapshot } from '../types.ts'

export interface MemberStatusArtProps {
  readonly status: SubagentSnapshot['status']
  readonly size?: number
  readonly title?: string
}

const STATUS_LABEL: Record<SubagentSnapshot['status'], string> = {
  running: '工作中',
  idle: '空闲',
  ready: '可恢复',
}

function StatusShape({ status }: { readonly status: SubagentSnapshot['status'] }): JSX.Element {
  switch (status) {
    case 'running':
      return (
        <>
          <circle cx="10" cy="10" r="8.25" fill="#eef2ff" stroke="#4d6bfe" strokeWidth="1.1" />
          <circle cx="6.2" cy="10" r="1.25" fill="#4d6bfe" />
          <circle cx="10" cy="10" r="1.25" fill="#4d6bfe" />
          <circle cx="13.8" cy="10" r="1.25" fill="#4d6bfe" />
        </>
      )
    case 'idle':
      return (
        <>
          <circle cx="10" cy="10" r="8.25" fill="#f6f2ec" stroke="#9a8172" strokeWidth="1.1" />
          <text x="4.1" y="12.8" fill="#80675a" fontFamily="ui-rounded, system-ui, sans-serif" fontSize="6.4" fontWeight="800">z</text>
          <text x="9.2" y="9.6" fill="#80675a" fontFamily="ui-rounded, system-ui, sans-serif" fontSize="8" fontWeight="800">Z</text>
        </>
      )
    case 'ready':
      return (
        <>
          <circle cx="10" cy="10" r="8.25" fill="#f1f3f5" stroke="#8b949d" strokeWidth="1.1" />
          <path d="M12.8 4.7 C8.3 5.3 6.6 10.7 9.7 13.6 C11.5 15.2 13.7 14.9 15.1 13.8 C13.8 16.5 9.9 17.1 7.2 14.8 C3.4 11.6 4.9 5.6 9.3 4.2 C10.6 3.8 11.8 4 12.8 4.7 Z" fill="#77828d" />
        </>
      )
  }
}

export function MemberStatusArt({ status, size = 18, title }: MemberStatusArtProps): JSX.Element {
  const label = title ?? STATUS_LABEL[status]
  return (
    <svg width={size} height={size} viewBox="0 0 20 20" role="img" aria-label={label}>
      <title>{label}</title>
      <StatusShape status={status} />
    </svg>
  )
}
