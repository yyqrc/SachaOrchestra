# Sacha / Jojo 猫咪 Role 贴图精修提示词（交给 Codex）

> 用途：把这段完整粘贴给 Codex，让它精修 `integrations/dsh/sacha-visualizer/src/client/cats.tsx` 里的猫咪 SVG 贴图。
> 目标：在**不改动任何其他文件**的前提下，只重写 `cats.tsx` 内部的 SVG 绘制，产出更精致、更生动的布偶猫 Sacha 与长毛美短 Jojo 卡通形象。

---

## 1. 任务

重写 `cats.tsx`，精修两只卡通猫及其 Role 道具贴图。当前版本是我手写的粗糙 SVG，形状生硬、缺少神韵，需要你重新绘制。

**硬性工程约束（必须遵守）**：
- 保持导出的组件接口完全不变：`CatArt({ kind, prop, size, title })`，其中 `kind: 'sacha' | 'jojo'`，`prop: CatProp`，`size: number`，`title?: string`。
- 保持导出的类型不变：`CatKind`、`CatProp`、`CatProps`。
- `CatProp` 枚举值不变：`'none' | 'conductor' | 'explore' | 'research' | 'engineer' | 'security' | 'docs' | 'data' | 'operator' | 'design' | 'qa' | 'working' | 'sleeping' | 'thinking'`。
- 只输出 `cats.tsx` 一个文件的完整新内容；不改 `artwork.ts`、`ActivityPanel.tsx`、CSS 或测试。
- 纯内联 SVG + React，不引入任何新依赖、不请求外部图片/字体。

---

## 2. 角色设定（Character Bible）

### Sacha —— 布偶猫（Ragdoll）
- **毛色**：重点色（seal point）。身体奶白/奶油白（暖白），耳朵、面罩（鼻梁到眼周）、四肢末端、尾巴为柔和灰棕色（soft seal brown）。
- **眼睛**：**大而圆的蓝色眼睛**（布偶猫最标志性特征），明亮的宝石蓝，有清晰高光与眼线，眼神温润。
- **毛感**：中长毛、蓬松，**下巴与胸前有明显的大围脖（ruff）**，脸部轮廓柔和、略圆。
- **气质**：甜美、温顺、放松。

### Jojo —— 长毛美国短毛猫（longhair American Shorthair）
- **毛色**：银色经典虎斑（silver classic tabby）。底毛银灰，**额头有清晰的 "M" 形纹**，眼周有眼线纹，**脸颊有平行细条纹**，身体有漩涡/牡蛎状斑纹。
- **眼睛**：**绿琥珀色（green-gold）眼睛**，圆而明亮，有高光。
- **毛感**：长而蓬松，颈部有明显颈毛，圆脸。
- **气质**：机灵、专注。

两只猫必须是**同一套视觉语言**：相同视角（正面微 3/4）、相同头身比、相同描边粗细、相同光源、相同上色逻辑；只靠花色、眼色、耳形与气质区分，一眼就能认出"这只是布偶、这只是美短"。

---

## 3. 风格与技术规格

- **风格**：扁平卡通贴纸风（flat vector sticker / kawaii-chibi），**大头比例**（可以只画头部 + 一点肩颈围脖），圆润造型，适度粗描边，简洁干净。
- **画布**：统一 `viewBox="0 0 64 64"`，主体居中，四周留出安全边距。
- **色板**：每只猫一组命名调色常量（fur / furShade / point / pointShade / inner-ear / eye / eyeDeep / nose / muzzle / ruff 等），便于后续主题化；颜色用柔和的扁平色，避免廉价高饱和。
- **分层分组**（便于动画与精修）：把 SVG 内部按 `<g class="cat-ears">`、`<g class="cat-face">`、`<g class="cat-eyes">`、`<g class="cat-markings">`、`<g class="cat-ruff">`、`<g class="cat-prop">` 分组，类名稳定。
- **微动画**：保留并改进两处——
  1. **眨眼**：眼睑周期性闭合（约 4–6 秒一次），用 SVG `<animate>` 或 CSS 实现，不要太频繁；
  2. **耳朵轻颤**：偶尔一次小幅摆动。
  外层整体动画（浮动/思考/呼吸）由面板 CSS 负责，SVG 内部只做眨眼 + 耳朵。
  支持 `prefers-reduced-motion` 时可关闭（可用 CSS 媒体查询包一层）。
- **可访问性**：根 `<svg>` 带 `role="img"` 与 `<title>`；保证与浅色背景有足够对比度。

---

## 4. 完整贴图清单

**两只基础猫**（无道具时的默认头像）：
- `sacha`：布偶猫正脸，蓝眼，重点色面罩与耳朵，大围脖。
- `jojo`：长毛美短正脸，绿琥珀眼，M 额纹 + 脸颊条纹，颈毛蓬松。

**Role 道具**（戴在头部右下/头顶的小配件，小巧、不遮脸、与角色风格统一、一眼可辨）：
| prop | 道具 | 建议 |
| --- | --- | --- |
| `conductor` | 指挥棒 | 乐团指挥（Sacha 主任务）的标志：细长棒 + 小握柄，举在右下 |
| `explore` | 灯泡 + 问号气泡 | Explore 节点 = 脑暴/澄清/追问（grill）的组合：亮灯泡 + 对话问号小气泡 |
| `research` | 放大镜 | 右下，圆镜片 + 短柄（仅表示"研究/调研"，与 `explore` 区分） |
| `engineer` | 笔记本电脑 | 右下，小屏幕带光标 |
| `security` | 盾牌 | 右下，内含对勾 |
| `docs` | 纸张/卷轴 | 右下，带两行字线 |
| `data` | 柱状图 | 右下，三根递增柱 |
| `operator` | 齿轮 | 右下，8 齿 |
| `design` | 画笔/调色 | 右下，画笔 + 颜料点 |
| `qa` | 对勾 + 叉 / 测试标记 | 右下，验讫章感 |
| `working` | 三个工作点 | 角标用，动态省略号感 |
| `sleeping` | `z Z` 睡眠符 | 角标用，递增大小的 z |
| `thinking` | 思考气泡 | 角标用，三个递增气泡圈 |

**状态用法**：`working / sleeping / thinking` 主要作为右下角小角标；其余 prop 可作为主道具直接画在角色头像里。

**术语对齐**：Sacha 是多智能体编排（Orchestra），主任务是乐团"**指挥**"（不是"队长"），用 `conductor` 指挥棒而非皇冠；Explore 节点包含脑暴、澄清、追问（grill）等工作意图，不是单纯的"研究/放大镜"，用 `explore`（灯泡+气泡）而非 `research`。

---

## 5. 精修方向（当前版本的具体不足，请针对性改进）

- 布偶的重点色面罩形状太生硬、边界突兀 → 重新设计自然过渡的面罩/耳色分区，体现"奶白身体 + 灰棕重点色"的柔和渐变感（可用轻微 opacity 叠色）。
- 美短虎斑纹太少太粗 → 补足额头 M 纹、眼周眼线、脸颊平行纹与体侧漩涡纹，线条细而清晰。
- 眼睛无神 → 加瞳孔、多层高光（主高光 + 反光点）、上眼线/睫毛暗示，让蓝眼更"宝石"、绿眼更"透亮"。
- 围脖/身体比例单调 → 加毛流分组与层次，布偶的大围脖更蓬松、美短的颈毛更分明。
- 道具与头部衔接突兀 → 道具加统一描边与投影，位置固定（右下为主），尺寸约头部的 1/4。
- 整体比例 → 更"团子"、更可爱：更大的头身比、更短的耳距、更圆润的下颌。

---

## 6. 验收标准

- `pnpm typecheck` 与 `pnpm test`（在 `integrations/dsh/sacha-visualizer` 下）全部通过；`artwork.spec.ts` 不需要改。
- `cats.tsx` 导出接口与类型完全不变，其它文件零改动。
- 两只猫在 40–46px 渲染下仍能一眼区分品种与眼色；12 种 prop 全部可辨。
- 眨眼与耳朵微动画自然、不喧宾夺主；reduced-motion 下静止。
- SVG 体积小、无外部资源、无新依赖。
