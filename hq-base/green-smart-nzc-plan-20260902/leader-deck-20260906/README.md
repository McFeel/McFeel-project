# 南网总部基地领导汇报 · 横向翻页 HTML（歸藏瑞士风）

小七落版 · 文案 文秘·Opus · 2026-09-06 · 共 23 页

## 怎么打开

双击 `leader-deck-20260906_by小七.html`，用 Chrome 或 Edge 打开，`F11` 全屏投屏。

不联网也能开：整份幻灯是**单个 HTML 文件**，样式和脚本都写在文件里，没有 CDN、没有外链字体、没有构建步骤。中文用系统字体（PingFang SC／微软雅黑／Noto Sans SC），西文和数字用 Helvetica／Arial 一档的无衬线，换机器不会掉版。

唯一的外部依赖是同目录的 `images/`，走相对路径。**把 HTML 和 `images/` 一起拷走**，位置随便放；只拷 HTML 的话两张图会变成空框，其余 21 页照常。

| 操作 | 键 |
| --- | --- |
| 翻页 | `←` `→`，或 `PageUp` `PageDown`，或空格 |
| 首页 / 末页 | `Home` / `End` |
| 页面总览（点标题直接跳页） | `ESC` |
| 也支持 | 鼠标滚轮、触屏左右滑、底部分页点 |

页面按 1600×900 的固定画布等比缩放，任何窗口尺寸下版式都不变形。地址栏带页面 id，例如 `...html#green-attr` 可以直接开到绿色属性页；`Ctrl+P` 可按页导出 PDF。

## 文件

| 文件 | 说明 |
| --- | --- |
| `leader-deck-20260906_by小七.html` | 幻灯主文件，单文件可投屏 |
| `images/fig-1-park-system.png` | 09 页配图，复用 `../figures/fig-1.png` |
| `images/fig-2-digital-base.png` | 13 页配图，复用 `../figures/fig-2.png` |
| `images/green/` `images/efficient/` `images/human/` | 11 个待拷入的图位，目录已建好，图放进去就出图 |
| `images/IMAGE-MANIFEST.md` | 配图清单：已复用哪几张、还缺哪几张、缺的叫什么名字、画面要什么 |

## 补图怎么补

按 `images/IMAGE-MANIFEST.md` 里的**路径和文件名**把图拷进去，刷新页面就出图，**HTML 一个字都不用改**。

图位是自动兜底的：图片在就显示图片，图片不在就退回虚线占位框，框里印的正是它等的那个文件名。所以补一张出一张，不用一次配齐，也不会因为少一张图把版面弄坏——两种状态下版式完全一样。

云端读不到 Box 和 Mac 本地盘，11 张图都要在本地由小七拷入。目录清单：

```
images/green/      datacenter-cold-aisle.png  waste-heat-flow.png
                   pv-rooftop-carport.png     carbon-ledger.png
images/efficient/  chiller-plant.png          lighting-before-after.png
                   smart-pole.png             night-lighting-path.png
images/human/      parking-reserve.png        env-dashboard.png
                   meeting-endpoint-auto.png
```

**图内自带的角标数字不是本方案口径。** `night-lighting-path.png` 的「节能率 60%」和 `lighting-before-after.png` 的「40%+」都是素材自带的示意角标，不是承诺数，也不拿去改文案；11 页照明的口径仍是 PR #69 的参照方向：参照测算一年省约 113 万千瓦时，幅度约三成。这一句已经落在页面上，就印在那一排图下面。

## 文案来自哪里

本轮只做落版、排版、挂图、页序，**一句领导话术都没有另写**。每页的标题、导语、正文、页脚都逐字取自下面三个 Markdown 文案包（文秘·Claude Opus 5.0 出品）：

| 文案包 | 供给哪些页 |
| --- | --- |
| `../slides/human-voice-rewrite-mainchain-20260906.md`（PR #67） | 主链 18 页 |
| `../slides/human-voice-green-efficient-2pages-20260906.md`（PR #69） | 10 `green-attr`、11 `efficient-attr` |
| `../slides/human-voice-human-line-3pages-20260906.md`（PR #68） | 15 `human-inclusive`、16 `human-health`、17 `human-culture` |

主链里原来的 `green-line` 由 PR #69 的两页替换，原来的 `human-day` 由 PR #68 的三页替换，**不并存**。20 页 + 1 + 2 = 23 页。

落版时只动了这几处，都是用户点名要的：

- 02 页标题按锁定口径落成「总部基地建设本质上是一项战略能力建设」，该页导语、正文、页脚仍逐字取自主链 md。
- 10、11 两页的对照表加表脚「内部测算，待基线书面核验」，可提升方向一列的每个数字挂「参照」角标——这是 PR #69 文案包里写明的整页要求。
- 11 页那排图下面加了一句「配图角标（节能率 60%、40%+）是素材自带示意，不是本方案口径；照明数字以正文与对照表为准。」
- 文案包开头的「统一口径」「落版说明」是给落版看的，不上页面。
- 10、11 两页的图位说明逐字取自文案包的「配图提示」；15—17 三页因为 Box 图的画面与原配图提示不是同一组，图位说明改取本页正文原句，原配图提示仍记在 `images/IMAGE-MANIFEST.md` 里备查。

## 页序（锁定）

```
01 cover                      封面
02 strategic-alignment-chain  ┐
03 constraints                ├ 战略 · 约束 · 目标
04 target-portrait            ┘
05 three-sites                ┐
06 two-consultancies          ├ 调研
07 research-standards         ┘
08 six-dimension-map          ┐ 框架 · 方案
09 research-to-scheme         ┘
10 green-attr                 ┐ 绿色主线
11 efficient-attr             ┘
12 mpark-three-ends           ┐
13 digital-base               ├ 智慧主线
14 green-smart-building       ┘
15 human-inclusive            ┐
16 human-health               ├ 人文主线
17 human-culture              ┘
18 six-proofs                 ┐
19 indicator-tree             ├ 闭环 · 指标 · 增益
20 four-scenes                ┘
21 four-steps                 ┐
22 replicable-pack            ├ 推进 · 复制 · 决策
23 three-decisions            ┘
```

## 校验：改完跑一遍

```bash
python3 check_deck.py                          # md 默认找 ../slides/
python3 check_deck.py --slides /path/to/slides # 指定三包 md 所在目录
```

只用标准库，不装任何依赖，退出码 0 才算过。四条钉死的口径都在里面：

| | 校验什么 |
| --- | --- |
| A | 页面上每一段可见文字，要么逐字来自 #67/#68/#69 三包 md，要么是登记在案的落版构件（页码、栏目名、表头、表脚、图位说明）。出现第三种就报「出处不明」并列出原句 |
| B | 绿色／高效两页对照表的表脚必须是原句「内部测算，待基线书面核验」，一字不差，且只在这两页 |
| C | PUE、501 万千瓦时、4171 吨、新能源占比只能待在对照表里、且带「参照」角标；全稿不得出现「已实现／已达到／已建成」这类承诺腔 |
| D | 图内角标百分比（节能率 60%、40%+）不得进正文，只能出现在那句免责里 |

外加页序、逐字比对、图位登记、以及「PUE 1.4 称行业优秀／910／1082／650／Researchy／本页边界／不上本页／【待核】」这几条老红线。

三包 md 来自 PR #67／#68／#69，还没合并时脚本会提示跳过 A 与逐字比对，只跑 B/C/D 与图位登记，并在结尾写明哪几项没跑。

## 口径纪律（本轮守住的几条）

- 绿色、高效两页对照表的表脚是原句「内部测算，待基线书面核验」，一字不差。
- PUE（约 1.66 → 约 1.4）、年新能源发电占比（约 2.3% → 约 3.2%）、约 501 万千瓦时、约 4171 吨，全部只出现在对照表的「可提升方向」一列，每个都带「参照」角标，**一处都没有写成已实现或已批准**；全稿没有「已实现／已达到／已建成」这类承诺腔。
- 配图里素材自带的角标百分比（节能率 60%、40%+）只当画面元素，没进正文、没进对照表。
- 不写「PUE 1.4 是行业优秀」；「行业优秀参照」只挂在高效页的配套冷源 EER 上，那是文案包自己的写法。
- 910、1082、650 三个数一个都没上。
- 奖项与认证名称一个都没写。
- 智慧路灯整段只在 11 `efficient-attr`，绿色页不重复。
- 10、11 两页的数字全部落成「现状参照 → 可提升方向」，每个数字挂「参照」角标，表脚统一写「内部测算，待基线书面核验」。
- 「Researchy」「本页边界」「不上本页」「【待核】」这类制作口吻，全稿零命中。

## 换文案怎么改

三个文案包更新后，在 HTML 里按 `data-id` 找到对应的 `<section>`，改四处即可：`h2.t`（标题）、`p.lead`（导语）、`ol.pts`（正文）、`.foot .nb`（页脚一句）。页序、页码、总览列表都是脚本按 DOM 顺序自动生成的，加页删页不用改脚本。

## 风格出处

歸藏 PPT skill 的**风格 B · 瑞士国际主义（Swiss Style）**，壳子参照仓库内既有的领导汇报 HTML `hq-base/world-class-nzc-hq-20260903/guizang-slides/index.html`：IKB 克莱因蓝 `#002FA7` 全场单一锚点色，纸白 `#fafaf8` 底、80 px 模块网格，全程无衬线、直角纯色、发丝分割线，字号越大字重越轻。

与那份壳子的差别只在工程取舍：本文件去掉了演讲者模式、WebGL 背景、Motion One 和 Lucide 图标这几处外部依赖，换成纯 CSS 网格和自带的翻页脚本，为的是满足「单文件、断网可开」。
