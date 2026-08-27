# 南网总部基地既有园 · 六边形沙盘（一核六边）

可投屏的双页沙盘。首页是**一个战略核 + 六条属性边**；普惠只是六边之一，按六家重跑口径对照。六家没有各自另立顶层设计，也不占掉六边。

## 怎么打开

**双击 `index.html`**，用系统默认浏览器打开（Chrome / Edge / Safari / Firefox 均可）。

- 无需 npm、无需构建、无需本地服务器；`index.html`、`style.css`、`app.js`、`data.js` 四个文件放在同一目录即可。
- 打开后按 `F11`（macOS 为 `⌃⌘F`）全屏，画面按 16:9 等比缩放铺满投屏。
- 脑图用 mermaid CDN 10.9.1 渲染，联网时显示图形；断网时自动退化为该路原文的 mermaid 源码，页面其余部分不受影响。

## 两页

**第一页 · 首页沙盘**

- 中心是三层战略核，点击展开全文：
  1. 国家：六张网（水网、新型电网、算力网、新一代通信网、城市地下管网、物流网）
  2. 南网：以新型电网为枢纽做六网协同；算电协同是突破口（待核）
  3. 南网自身：加快积累战略资产，驱动「第二增长曲线」。基地是验证场／明牌，不是曲线本身。
- 周围六边：零碳、绿色、高效、智慧、人文（含健康）、普惠。战略不占边。
- 每边面板露出该边短句 + 六家字标。点字标：该路第四轮六边形脑图 + 该边全文。
- 普惠一侧带「重跑」标记；点开后右侧是该家重跑后的普惠主张、定义与否掉了什么，不把该家另起的核或另切的边搬上首页。

**第二页 · 核 + 六边 × 六模型**

- 行 = 核 + 六边，列 = 六家。点格子打开对应原文。
- 普惠行的格子写「主张 / 否掉」，其余行仍写「路径 / 厂商·园区」。

## 操作

| 操作 | 效果 |
| --- | --- |
| 点击顶栏页签 / 按 `1` `2` / 左右方向键 | 切换两页 |
| 点击中心三层核 | 打开三层口径 + 六路对「核」的原文摘录 |
| 点击边上的模型字标或表格格子 | 打开该路脑图 + 该边全文 |
| `Esc` 或点击遮罩 | 关闭弹层 |

## 口径

顶栏有一条**工作假设**（只出现一次，不改写任何一家原文）：普惠 = 人人参与、人人受益（碳普惠、算力普惠、园区资源普惠）。

六家重跑后的普惠主张（摘自主张句，全文见弹层）：

| 家 | 普惠主张 |
| --- | --- |
| GLM-5.2 | 园城共生 / 溢出公共品 |
| Gemini 3.1 | 能力平权（赋能型普惠） |
| GPT-5.6 | 基础能力可及 |
| Kimi K3 | 机制普惠（红利向下、减碳向上聚资产） |
| Grok 4.6 | 外溢（可被借、可被感、可被学会） |
| Opus 4.8 | 绿色能力普惠（以碳普惠为锚） |

零碳、绿色、高效、智慧、人文与三层核仍用第四轮赛马一揽子原文。未核验数字标「待核」。

## 数据来源

核与其余五边取自第四轮赛马：

```
git show origin/cursor/hq-base-hexagon-race4-glm-5-2-f636:hq-base/hexagon-race-4/glm-5-2.md
git show origin/cursor/gemini-hexagon-64df:hq-base/hexagon-race-4/gemini-3-1.md
git show origin/cursor/hq-hexagon-race-4-14f7:hq-base/hexagon-race-4/gpt-5-6.md
git show origin/cursor/hexagon-race-4-kimi-k3-4d3f:hq-base/hexagon-race-4/kimi-k3.md
git show origin/cursor/hq-base-hexagon-race-4-b2b3:hq-base/hexagon-race-4/grok-4-6.md
git show origin/cursor/hexagon-race-4-opus-4-8-26a4:hq-base/hexagon-race-4/opus-4-8.md
```

普惠一侧只取各家重跑专节中的主张、定义与否掉了什么：

```
git show origin/cursor/hq-base-puhui-revise-glm52-956b:hq-base/hexagon-race-4/puhui-revise/glm-5-2.md
git show origin/cursor/puhui-revise-3f73:hq-base/hexagon-race-4/puhui-revise/gemini-3-1.md
git show origin/cursor/rewrite-puhui-framework-3725:hq-base/hexagon-race-4/puhui-revise/gpt-5-6.md
git show origin/cursor/puhui-revise-4557:hq-base/hexagon-race-4/puhui-revise/kimi-k3.md
git show origin/cursor/puhui-revise-interface-4649:hq-base/hexagon-race-4/puhui-revise/grok-4-6.md
git show origin/cursor/hq-base-puhui-revise-091a:hq-base/hexagon-race-4/puhui-revise/opus-4-8.md
```

## 上一轮存档

普惠重跑之前的统一「一核六边」六路一揽子，整份保留在 `archive/`。双击 `archive/index.html` 可单独打开。

## 可选：重跑校验脚本

`checks/` 下三个脚本用于在无浏览器环境校验页面结构、原文忠实度与脑图渲染，属开发期工具，与页面运行无关（页面本身不依赖任何 npm 包）。

```bash
cd checks
npm i
node check-dom.mjs        # 三层核、六边面板、42 格对照表、禁止项、排版余量
node check-source.mjs     # 五边对照 archive 原文；普惠对照六家重跑分支
node check-mermaid.mjs    # 六路脑图语法解析 + 实际渲染成 SVG
```
