# 南网总部基地领导汇报 · 单文件 HTML 翻页演示（ppt-animation · clean-white）

小七落版 · 文案 文秘·Opus · 2026-09-06 · 共 23 页

这是与歸藏瑞士风（PR #70）**并行的另一个试版**，两条线互不改动。同一套文案，两种视觉与两套翻页机制，供挑版。

## 怎么打开

双击 `leader-deck-20260906_by小七_ppt-animation-clean-white.html`，Chrome 或 Edge 打开，`F11` 全屏投屏。

| 操作 | 键 |
| --- | --- |
| 翻页 | `←` `→`，或 `↑` `↓`，或 `PageUp` `PageDown`，或空格 / 回车 |
| 首页 / 末页 | `Home` / `End` |
| 页面总览（点标题直接跳页） | `ESC` |
| 也支持 | 鼠标滚轮、点击左右半屏、触屏左右滑、顶部进度条分段点击 |

地址栏带页面 id，`...html#green-attr` 可直接开到绿色属性页。

## 单文件到什么程度

整份幻灯**就是一个 HTML 文件**，CSS 和 JS 全部内联，不依赖任何前端框架，`images/` 之类的同级目录一个都没有。

- **图形全部是手写 SVG / CSS**：六边形属性图、对照条、四级监测嵌套框、控制闭环、一杆多用、环境公示牌、参观路线、四步台阶等 23 页图形，没有引用仓库里的任何图片，拷走单个文件就能放。
- 唯一的外部请求是 **Google Fonts**（Noto Sans SC / Noto Serif SC），skill 允许。断网时自动回落到 PingFang SC／微软雅黑，版式不变形，只是字形换一档。

页面按 1600×900 固定画布等比缩放，任何窗口尺寸下都保持 16:9 不变形。

## 风格出处

`ppt-animation` skill（https://github.com/Unclecheng-li/AI_Animation/tree/master/skills/ppt-animation），主题锁定 **`clean-white`：白底 + 深色字 + 彩色点缀**。

按 skill 的生成规范落的几条硬要求：

| skill 规范 | 本文件怎么落的 |
| --- | --- |
| 单文件 HTML，CSS/JS 全内联 | 是，仅 Google Fonts 外链 |
| 16:9，适配全屏播放 | 1600×900 固定画布 + `scale()` 等比适配 |
| 键盘 ← → / 滚轮 / 点击左右区域翻页 | 三种都支持，滚轮做了 520ms 节流防连翻 |
| 页码 + 细进度条 | 右下角 `07 / 23`，顶部 23 段进度条（可点击跳页） |
| 每次翻页后元素**依次缓入**，标题先出、正文图形后出 | `.a` 元素按 DOM 顺序排队，`setTimeout` 序列 + CSS transition |
| 单页所有元素出现总计 1.5–2.5 秒 | 末位延时 ≤ 1440ms，叠加 620ms 过渡，整页 ≈ 2.0 秒收尾 |
| 重要图形用纯 CSS/SVG，不依赖外部图片 | 全部手写 SVG |
| 不使用外部 CSS/JS 框架（可用 Google Fonts） | 是 |
| 每页至少 1 个图形化元素 | 23 页各有一个 |

缓入的节奏是脚本按每页元素数自动算的：`step = min(110ms, 1350ms / (n-1))`，页面元素多就自动压缩间隔，保证不越出 2.5 秒上限。单个元素想手工定时，在标签上加 `data-delay="600"` 即可覆盖。

**页数超了 skill 建议的 5–10 页**：skill 那条是给科普短片定的，本任务是领导汇报，按锁定页序落满 23 页，以内容完整为准；翻页缓入动效与 16:9 两条照旧。

## 文案来自哪里

本轮只做落版、排版、配图、页序，**一句领导话术都没有另写**。每页的标题、导语、正文、页脚一句都逐字取自下面三个 Markdown 文案包（文秘·Claude Opus 5.0 出品）：

| 文案包 | 供给哪些页 |
| --- | --- |
| `../slides/human-voice-rewrite-mainchain-20260906.md`（PR #67） | 主链 18 页 |
| `../slides/human-voice-green-efficient-2pages-20260906.md`（PR #69） | 10 `green-attr`、11 `efficient-attr` |
| `../slides/human-voice-human-line-3pages-20260906.md`（PR #68） | 15 `human-inclusive`、16 `human-health`、17 `human-culture` |

主链里原来的 `green-line` 由 PR #69 的两页替换，原来的 `human-day` 由 PR #68 的三页替换，**不并存**。18 + 2 + 3 = 23 页。

> 三个文案包分别在 PR #67 / #68 / #69 的分支上，尚未并入 `main`。本分支只放 HTML，不重复搬运 md；上表的相对路径是三包合并后的落点。

落版时只动了这几处，都是点名要的：

- **02 页标题**按锁定口径落成「总部基地建设本质上是一项战略能力建设」，该页导语、正文、页脚仍逐字取自主链 md。
- **10、11 两页**的对照表加表脚「内部测算，待基线书面核验」，「可提升方向」一列每个数字挂「参照」角标——这是 PR #69 文案包写明的整页要求。
- 文案包开头的「统一口径」「落版说明」「配图提示」是给落版看的，不上页面；配图提示已按画面要求转成 SVG。

## 页序（锁定）

```
01 cover                      封面
02 strategic-alignment-chain  ┐
03 constraints                ├ 战略 · 约束 · 目标      靛
04 target-portrait            ┘
05 three-sites                ┐
06 two-consultancies          ├ 调研                   青
07 research-standards         ┘
08 six-dimension-map          ┐ 框架 · 方案            紫
09 research-to-scheme         ┘
10 green-attr                 ┐ 绿色主线               绿
11 efficient-attr             ┘
12 mpark-three-ends           ┐
13 digital-base               ├ 智慧主线               蓝
14 green-smart-building       ┘
15 human-inclusive            ┐
16 human-health               ├ 人文主线               橙
17 human-culture              ┘
18 six-proofs                 ┐
19 indicator-tree             ├ 闭环 · 指标 · 增益      玫
20 four-scenes                ┘
21 four-steps                 ┐
22 replicable-pack            ├ 推进 · 复制 · 决策      琥珀
23 three-decisions            ┘
```

`clean-white` 是白底 + 深色字 + 彩色点缀，「点缀」按上面八组各锁一种颜色，一页只出现一种，翻到哪一组一眼能认出来。三条主线自己的绿 / 蓝 / 橙在封面、08 六边形、19 指标、23 决策四处同时出现，用于表达三线关系。

## 口径纪律（本轮守住的几条）

- 奖项与认证名称一个都没写。
- 910、1082、650 三个数一个都没上。
- 10、11 两页的数字全部落成「现状参照 → 可提升方向」，**每个数字挂「参照」角标**，包括百分比，表脚统一写「内部测算，待基线书面核验」；图上不出现任何不带角标的承诺数。
- 智慧路灯整段只在 11 `efficient-attr`，绿色页不重复同一批措施。
- 「本页边界」「待核」「不构成」这类制作口吻，全稿零命中。

## 自检脚本

```bash
python3 check_deck_against_copy.py \
  leader-deck-20260906_by小七_ppt-animation-clean-white.html \
  <三个 md 所在目录>
```

第二个参数省略时默认取 `../slides`。脚本核五件事：

1. 页序与页 id 与锁定的 23 页一一对应；
2. 每页的标题、导语、正文、表格、页脚一句都能在对应 md 里找到出处（角标插在句中时降为分句核对，会在输出里报数）；
3. 绿色 / 高效两页的对照表数字全部挂了角标，且有表脚；
4. 禁用词零命中；
5. 除 Google Fonts 外没有外部 CSS/JS/图片依赖。

当前结果：**202 条文案片段全部有出处**，其中 3 条为分句命中（都是「参照」角标插进句子造成的），其余四项全过。

## 换文案怎么改

三个文案包更新后，在 HTML 里按 `data-id` 找到对应的 `<section>`，改四处即可：`h2.t`（标题）、`p.lead`（导语）、`ol.pts` 或 `ul.plain`（正文）、`.foot .nb`（页脚一句）。页码、进度条分段、总览列表都是脚本按 DOM 顺序自动生成的，加页删页不用改脚本；改完重跑一次自检脚本。
