/**
 * Human-facing view model for the Root tool surface.
 *
 * The Host reports machine facts (names, families, unlock state). This module
 * owns the reader-facing translation: short Chinese labels and the grouping
 * that makes a 90-entry surface scannable. Internal names stay verbatim because
 * they are identifiers, not prose.
 */

import type { ToolSurfaceSnapshot } from '../types.ts'

/** One family section as the panel renders it. */
export interface ToolFamilyView {
  readonly key: string
  readonly label: string
  readonly tools: readonly ToolView[]
}

/** One tool as the panel renders it. */
export interface ToolView {
  /** Registered tool name — kept verbatim; it is an identifier the model uses. */
  readonly name: string
  /** Short Chinese purpose, or undefined when this build has no label for it. */
  readonly label?: string
  /** Whether a temporary unlock added it beyond the current phase. */
  readonly unlocked: boolean
}

/** Family keys the Host can report, in the order the panel presents them. */
const FAMILY_ORDER = [
  'filesystem-read',
  'filesystem-write',
  'shell',
  'sacha-delegation',
  'web',
  'jobs',
  'other',
] as const

const FAMILY_LABEL: Record<string, string> = {
  'filesystem-read': '读取文件',
  'filesystem-write': '写入文件',
  shell: '执行命令',
  'sacha-delegation': '派发子代理',
  web: '联网',
  jobs: '后台任务',
  other: '其他工具',
}

/**
 * Short Chinese purposes for the tools this deployment ships. Deliberately a
 * label rather than the tool's full description: the panel answers "what can it
 * do", and the model-facing description stays the authority for how to call it.
 */
const TOOL_LABEL: Record<string, string> = {
  read: '读取文件',
  read_image: '查看图片',
  glob: '按名称找文件',
  grep: '搜索文件内容',
  write: '写入文件',
  edit: '修改文件',
  pwsh: '执行命令',
  bash: '执行命令',
  pty: '交互式终端',
  skill: '加载技能',
  web_search: '搜索网页',
  web_fetch: '抓取网页',
  ask_user_question: '向你提问',
  todo_write: '记录待办',
  present: '交付文件',
  sacha_tools: '调整可用能力',
  sacha_research: '派调查子代理',
  sacha_worker: '派执行子代理',
  sacha_review: '派复核子代理',
  sacha_visual_event: '记录任务进展',
  subagent: '派子代理',
  subagent_fork: '派继承上下文的子代理',
  list_agents: '查看子代理',
  send_message: '给子代理发消息',
  interrupt_agent: '中断子代理',
  workflow: '批量编排子代理',
  ralph: '循环迭代推进',
  job_list: '查看后台任务',
  job_output: '读取任务输出',
  job_kill: '停止后台任务',
  exit_plan_mode: '提交计划',
  create_goal: '设定目标',
  get_goal: '查看目标',
  update_goal: '更新目标',
}

function familyOf(surface: ToolSurfaceSnapshot, name: string): string {
  return surface.toolFamilies?.[name] ?? 'other'
}

function toView(surface: ToolSurfaceSnapshot, name: string, unlocked: ReadonlySet<string>): ToolView {
  const label = TOOL_LABEL[name]
  return {
    name,
    ...(label === undefined ? {} : { label }),
    unlocked: unlocked.has(name),
  }
}

/**
 * Group one name list into family sections in presentation order. Families with
 * no members are omitted, and tools of unknown family collect under 其他工具 so
 * a newly registered plugin tool is still visible rather than silently dropped.
 */
export function groupTools(surface: ToolSurfaceSnapshot, names: readonly string[]): readonly ToolFamilyView[] {
  const unlocked = new Set(surface.unlocked)
  const byFamily = new Map<string, ToolView[]>()
  for (const name of names) {
    const family = familyOf(surface, name)
    const bucket = byFamily.get(family)
    const view = toView(surface, name, unlocked)
    if (bucket === undefined) byFamily.set(family, [view])
    else bucket.push(view)
  }
  const known = FAMILY_ORDER.filter(key => byFamily.has(key))
  const extra = [...byFamily.keys()].filter(key => !(FAMILY_ORDER as readonly string[]).includes(key)).sort()
  return [...known, ...extra].map(key => ({
    key,
    label: FAMILY_LABEL[key] ?? '其他工具',
    tools: byFamily.get(key) ?? [],
  }))
}

/**
 * One-line summary of what the current phase means for the reader. States the
 * consequence rather than the internal phase name.
 */
export function phaseSummary(surface: ToolSurfaceSnapshot): string {
  return surface.phase === 'bootstrap'
    ? '刚起步：只开放了查看类工具'
    : '已开放工作工具'
}
