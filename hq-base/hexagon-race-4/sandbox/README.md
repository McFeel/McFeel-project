# 南网总部基地既有园 · 六边形沙盘（第四轮赛马 · 六路对照）

可投屏的双页沙盘，用于把第四轮赛马六路模型（GLM-5.2 / Gemini 3.1 / GPT-5.6 / Kimi K3 / Grok 4.6 / Opus 4.8）的原文摆在同一张台面上对照。

## 怎么打开

**双击 `index.html`** 即可，用系统默认浏览器打开（Chrome / Edge / Safari / Firefox 均可）。

- 无需 npm、无需构建、无需本地服务器；`index.html`、`style.css`、`app.js`、`data.js` 四个文件放在同一目录即可。
- 打开后按 `F11`（macOS 为 `⌃⌘F`）全屏，画面按 16:9 等比缩放铺满投屏。
- 脑图用 mermaid CDN 渲染，联网时显示图形；断网时自动退化为该路原文的 mermaid 源码，页面其余部分不受影响。

## 两页

**第一页 · 首页沙盘**

- 中心是三层核（国家六张网 → 南网六网协同 → 南网自身战略资产），点击展开三层完整口径与六路模型对核的提法。
- 周围六边：零碳、绿色、高效、智慧、人文（含健康）、普惠。每边六个模型字标，点击任一字标弹出该路原文脑图与该边完整方案（四段，不压缩）。

**第二页 · 对照表**

- 行 = 核 + 六边（7 行），列 = 六路模型（6 列），格子写路径与厂商／园区。
- 点击任一格子展开该路该边的原文完整方案。

## 操作

| 操作 | 效果 |
| --- | --- |
| 点击顶栏页签 / 按 `1` `2` / 左右方向键 | 切换两页 |
| 点击模型字标或表格格子 | 打开原文脑图 + 完整方案 |
| 点击中心核 | 打开三层核口径 |
| `Esc` 或点击遮罩 | 关闭弹层 |

## 数据来源

`data.js` 中的六路正文与脑图均逐字取自各路原文，脑图仅做渲染必要的最小修正（Kimi K3 一路：`<br>` → `<br/>`，并把 `资产沉淀` 分支缩进到 root 之下，因为 mermaid mindmap 只允许单一根节点）。原文全文：

```
git show origin/cursor/hq-base-hexagon-race4-glm-5-2-f636:hq-base/hexagon-race-4/glm-5-2.md
git show origin/cursor/gemini-hexagon-64df:hq-base/hexagon-race-4/gemini-3-1.md
git show origin/cursor/hq-hexagon-race-4-14f7:hq-base/hexagon-race-4/gpt-5-6.md
git show origin/cursor/hexagon-race-4-kimi-k3-4d3f:hq-base/hexagon-race-4/kimi-k3.md
git show origin/cursor/hq-base-hexagon-race-4-b2b3:hq-base/hexagon-race-4/grok-4-6.md
git show origin/cursor/hexagon-race-4-opus-4-8-26a4:hq-base/hexagon-race-4/opus-4-8.md
```

## 可选：重跑校验脚本

`checks/` 下三个脚本用于在无浏览器环境校验页面结构、mermaid 语法与渲染产物，属开发期工具，与页面运行无关（页面本身不依赖任何 npm 包）。

```bash
cd checks
npm i jsdom mermaid@10.9.1 canvas
node check-dom.mjs        # 页面结构、42 格对照表、36 个弹层、禁止项文本审查
node check-mermaid.mjs    # 六路脑图语法解析 + 与原文逐行比对
node check-render.mjs     # 六路脑图实际渲染成 SVG
```
