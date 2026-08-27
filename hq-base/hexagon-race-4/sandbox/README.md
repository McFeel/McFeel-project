# 既有园升级 · 六家独立顶层设计（沙盘）

可投屏的双页沙盘，把六家（GLM-5.2 / Gemini 3.1 / GPT-5.6 / Kimi K3 / Grok 4.6 / Opus 4.8）各自独立的顶层设计并排摆在同一台面上对照。**六家各写各的核、各切各的边、各主张各的普惠，本沙盘不作统一收口。**

## 怎么打开

**双击 `index.html`**，用系统默认浏览器打开（Chrome / Edge / Safari / Firefox 均可）。

- 无需 npm、无需构建、无需本地服务器；`index.html`、`style.css`、`app.js`、`data.js` 四个文件放在同一目录即可。
- 打开后按 `F11`（macOS 为 `⌃⌘F`）全屏，画面按 16:9 等比缩放铺满投屏。
- 脑图用 mermaid CDN 渲染，联网时显示图形；断网时自动退化为该家原文的 mermaid 源码，页面其余部分不受影响。

## 两页

**第一页 · 六家独立顶层设计**

- 中心写「既有园升级 · 六家独立顶层设计」，不设统一的核。
- 周围六张机构卡片，卡片上只露该家自己的核（一句话）和边的切法名称与边名。
- 点任一机构：弹层展示该家原文脑图 + 核全文 + 各边 + 普惠专节，并完整保留它否掉的另两种普惠读法。弹层右上角有分节跳转。

**第二页 · 四行对照表**

- 行 = 核 / 边怎么切 / 普惠主张 / 否掉了什么，列 = 六家，24 格一屏可见。
- 点任一格子展开该家原文，并自动定位到对应分节。

## 六家的切法（互不统一）

| 家 | 核（一句话，摘自原文） | 边怎么切 | 普惠主张 |
| --- | --- | --- | --- |
| GLM-5.2 | 园是南网走向「算电协同生态组织者」的证地与汇聚场 | 三内向角色 + 一外向普惠 | 园城共生 / 溢出公共品 |
| Gemini 3.1 | 放弃三层嵌套核，改「内生驱动」单核：活态试验田 | 四维激活（不采用六边形） | 能力平权（赋能型普惠） |
| GPT-5.6 | 升级为南网可共同使用、可动态调度、可持续演进的能力场 | 一核五面 | 基础能力可及 |
| Kimi K3 | 从「用能大户」改写为电碳算协同在用户侧的制度试验田 | 四边一底，不设六边 | 机制普惠（双向机制） |
| Grok 4.6 | 把围墙里的好园写成南网的公共界面 | 按关系切四边 | 外溢型普惠 |
| Opus 4.8 | 既有园不是展台，是南网先在自己身上跑通的真实样本 | 三条边，不必六 | 绿色能力普惠（以碳普惠为锚） |

## 操作

| 操作 | 效果 |
| --- | --- |
| 点击顶栏页签 / 按 `1` `2` / 左右方向键 | 切换两页 |
| 点击机构卡片或表格格子 | 打开该家原文脑图 + 全文 |
| 弹层内的分节按钮 | 跳到核 / 边 / 普惠专节 |
| `Esc` 或点击遮罩 | 关闭弹层 |

## 数据来源

`data.js` 中六家的正文与脑图均逐字取自各自原文分支，脑图零改动。原文全文：

```
git show origin/cursor/hq-base-puhui-revise-glm52-956b:hq-base/hexagon-race-4/puhui-revise/glm-5-2.md
git show origin/cursor/puhui-revise-3f73:hq-base/hexagon-race-4/puhui-revise/gemini-3-1.md
git show origin/cursor/rewrite-puhui-framework-3725:hq-base/hexagon-race-4/puhui-revise/gpt-5-6.md
git show origin/cursor/puhui-revise-4557:hq-base/hexagon-race-4/puhui-revise/kimi-k3.md
git show origin/cursor/puhui-revise-interface-4649:hq-base/hexagon-race-4/puhui-revise/grok-4-6.md
git show origin/cursor/hq-base-puhui-revise-091a:hq-base/hexagon-race-4/puhui-revise/opus-4-8.md
```

弹层里带「本页编排」前缀的一句是本沙盘的导航说明，不是原文；其余正文均为原文。

## 上一轮存档

上一轮统一「一核六边」口径下的六路一揽子（第四轮赛马）整体保留在 `archive/`，双击 `archive/index.html` 可单独打开，默认首页不再展示统一六边。

## 可选：重跑校验脚本

`checks/` 下三个脚本用于在无浏览器环境校验页面结构、原文忠实度与脑图渲染，属开发期工具，与页面运行无关（页面本身不依赖任何 npm 包）。

```bash
cd checks
npm i
node check-dom.mjs        # 六家卡片、24 格对照表、六家弹层、禁止项文本审查、排版余量
node check-source.mjs     # 六家原文可达性、脑图逐行比对、113 段正文整段比对
node check-mermaid.mjs    # 六家脑图语法解析 + 实际渲染成 SVG
```
