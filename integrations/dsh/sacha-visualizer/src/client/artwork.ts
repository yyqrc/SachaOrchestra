/**
 * Cat Role artwork lookup for the Sacha conductor, Role members, and runtime state.
 * Returns the cat kind + prop for the hybrid `CatArt` component: a packaged
 * 256px cat portrait plus small inline SVG role/state overlays.
 */

import type { TeamMemberSnapshot } from '../types.ts'
import type { CatKind, CatProp } from './cats.tsx'

export interface CatArtwork {
  readonly kind: CatKind
  readonly prop: CatProp
}

/** Sacha (Ragdoll) is the conductor cat; Jojo (Shorthair) is the teammate cat. */
export const CONDUCTOR_CAT: CatArtwork = { kind: 'sacha', prop: 'conductor' }
export const MEMBER_CAT: CatArtwork = { kind: 'jojo', prop: 'none' }

const ROLE_CAT: ReadonlyArray<readonly [RegExp, CatProp]> = [
  [/data|analys|metric|performance|数据|分析|指标|性能/, 'data'],
  [/brainstorm|clarif|grill|\bexplore\b|脑暴|澄清|头脑风暴|追问|质询|探索/, 'explore'],
  [/planner|resear|investig|study|研究|调查|调研|规划/, 'research'],
  [/\bqa\b|test|verif|quality|测试|质量|验证/, 'qa'],
  [/executor|engineer|dev\b|server|backend|\bapi\b|runtime|工程|后端|服务|接口|开发|实施|代码/, 'engineer'],
  [/design|\bui\b|\bux\b|front|theme|accessib|visual|设计|前端|主题|无障碍|可视化/, 'design'],
  [/reviewer|secur|audit|risk|threat|review|安全|审计|审查|评审|风险/, 'security'],
  [/docs|writer|product|\bspec\b|specification|roadmap|撰写|文案|写作|文档|规范|路线图/, 'docs'],
  [/manager|release|\bbuild\b|deploy|\bops\b|\bci\b|ship|coordin|发布|构建|部署|运维|协调|管理/, 'operator'],
]

/** Return the closest role prop for a member, or undefined for the plain cat. */
export function memberCatProp(member: TeamMemberSnapshot): CatProp | undefined {
  const identity = `${member.name} ${member.description ?? ''}`.toLowerCase()
  for (const [pattern, prop] of ROLE_CAT) {
    if (pattern.test(identity)) return prop
  }
  return undefined
}
