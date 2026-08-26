/** Whale artwork lookup for the Sacha Lead, Role members, and runtime state. */

import type { TeamMemberSnapshot } from '../types.ts'

export const ART_BASE = '/plugins/sacha-visualizer/assets/'
export const LEAD_ART = `${ART_BASE}team-lead-v2.png`

const ROLE_ART: ReadonlyArray<readonly [RegExp, string]> = [
  [/data|analys|metric|performance|数据|分析|指标|性能/, 'member-data-v2.png'],
  [/planner|resear|investig|explor|study|研究|调查|探索|调研|规划/, 'member-researcher-v2.png'],
  [/\bqa\b|test|verif|quality|测试|质量|验证/, 'member-qa-v2.png'],
  [/executor|engineer|dev\b|server|backend|\bapi\b|runtime|工程|后端|服务|接口|开发|实施|代码/, 'member-engineer-v2.png'],
  [/design|\bui\b|\bux\b|front|theme|accessib|visual|设计|前端|主题|无障碍|可视化/, 'member-designer-v2.png'],
  [/reviewer|secur|audit|risk|threat|review|安全|审计|审查|评审|风险/, 'member-security-v2.png'],
  [/docs|writer|product|\bspec\b|specification|roadmap|撰写|文案|写作|文档|规范|路线图/, 'member-docs-v2.png'],
  [/manager|release|\bbuild\b|deploy|\bops\b|\bci\b|ship|coordin|发布|构建|部署|运维|协调|管理/, 'member-operator-v2.png'],
]

export const ACTION_ART: Record<TeamMemberSnapshot['status'], string> = {
  running: `${ART_BASE}action-working-v2.png`,
  idle: `${ART_BASE}action-sleeping-v2.png`,
  inactive: `${ART_BASE}action-sleeping-v2.png`,
  provisioning: `${ART_BASE}action-thinking-v2.png`,
  failed: `${ART_BASE}action-thinking-v2.png`,
}

/** Return the closest role illustration, preserving the initial fallback for unknown roles. */
export function memberArtUrl(member: TeamMemberSnapshot): string | null {
  const identity = `${member.name} ${member.description ?? ''}`.toLowerCase()
  for (const [pattern, filename] of ROLE_ART) {
    if (pattern.test(identity)) return `${ART_BASE}${filename}`
  }
  return null
}

