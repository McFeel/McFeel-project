# 南网总部基地中旬领导汇报 · 完整歸藏瑞士风单文件 HTML（23 页）

- **主文件**：`leader-deck-20260906_by小七.html`
- **落版**：小七（Grok Bot 总管）
- **文案**：文秘·Claude Opus 5.0，来自三个定稿包 **#67 / #68 / #69**（正文措辞一字未改）
- **壳**：完整 [guizang-ppt-skill](https://github.com/op7418/guizang-ppt-skill) **瑞士风** `assets/template-swiss.html`（Swiss Style · IKB 克莱因蓝）
- **日期**：2026-09-06 · 内部讨论稿

这一版是**完整壳**，不是只有 `#deck` 缩放的简化仿壳，也不是 `ppt-animation / clean-white` 白底试版（PR #71 那一路已弃用）。

---

## 怎么打开

```bash
open "hq-base/leader-deck-20260906-guizang/leader-deck-20260906_by小七.html"
```

双击即可，**不需要起本地服务器**。整份是单文件 HTML：CSS、JS、Motion One 动效引擎全部内联，只有 `images/` 是相对路径外链。断网也能完整放映（网络字体取不到时自动落到 PingFang SC / 微软雅黑）。

### 现场操作

| 键 | 行为 |
|---|---|
| `←` `→` / `空格` / 滚轮 / 触屏滑动 | 翻页 |
| `ESC` | 全片总览（点缩略图跳页） |
| `P` | **演讲者模式**：当前页 + 下一页 16:9 预览、演讲备注、计时、排练、宫格、激光笔、圈选、观众屏黑屏/白屏/冻结 |
| `B` | 静态 / 动态切换（低功耗，关掉所有入场动效，投屏卡顿时用） |

演讲备注 23 页全部写好（提词卡，不是逐字稿），合计建议 **25.8 分钟**。备注可以在浏览器里直接改，按 `data-slide-id` 存 `localStorage`。

---

## 页清单（23 页 · 页序已锁）

| # | slide-id | 页面标题 | 版式 | 图 |
|---:|---|---|---|---|
| 01 | `cover` | 建设世界一流智慧零碳园区 | SWISS-COVER-ASCII | 航拍位（可选） |
| 02 | `strategic-alignment-chain` | 总部基地建设本质上是一项战略能力建设 | S18 | **逻辑图** |
| 03 | `constraints` | 现实约束决定了零碳要靠系统能力 | S19 | — |
| 04 | `target-portrait` | 打造世界一流智慧零碳园区 | S03 | — |
| 05 | `three-sites` | 三个现场：先进园区是怎么运行的 | S16 | 实拍 ×3 |
| 06 | `two-consultancies` | 两次专题交流：把方法校准 | S08 | — |
| 07 | `research-standards` | 调研归纳：世界一流的三把尺子 | S13 | — |
| 08 | `six-dimension-map` | 三条主线统领六项属性 | S04 | **逻辑图** |
| 09 | `research-to-scheme` | 一揽子方案：调研成果怎么进方案 | S05 | **逻辑图** |
| 10 | `green-attr` | 绿色属性：把排放结构调优，把账做成可核证的 | S15 | 实拍 ×4 |
| 11 | `efficient-attr` | 高效属性：少用一点能，用好每一度电 | S22 | 实拍 ×1（整幅） |
| 12 | `mpark-three-ends` | 智慧主线（一）：三端协同，先看别人怎么做 | S05 | **逻辑图** |
| 13 | `digital-base` | 智慧主线（二）：统一数字底座，南网怎么落 | S17 | **逻辑图** |
| 14 | `green-smart-building` | 智慧主线（三）：绿智楼宇的诊断—监测—控制闭环 | S11 | **逻辑图** |
| 15 | `human-inclusive` | 普惠：一个规则，人人可及 | S16 | 实拍 ×1 |
| 16 | `human-health` | 健康：空气、光、声、温湿度可测可调可公示 | S15 | 实拍 ×1 |
| 17 | `human-culture` | 人文：一次预约联动末端，一次参观看见运行 | S16 | 实拍 ×1 |
| 18 | `six-proofs` | 六项属性互相证明 | S14 | **逻辑图** |
| 19 | `indicator-tree` | 指标结构：世界一流用什么来验 | S17 | **逻辑图** |
| 20 | `four-scenes` | 增益：对企业、对员工 | S08 | — |
| 21 | `four-steps` | 四步推进 | S19 | **逻辑图** |
| 22 | `replicable-pack` | 可复制的方案包 | S12 | — |
| 23 | `three-decisions` | 请本次明确三项决策 | SWISS-CLOSING-ASCII | — |

版式编号取自 guizang 瑞士风 `swiss-layout-lock.md` 登记的 S01–S22，共用到 **15 个不同版式**，没有自创正文结构。

---

## 九张逻辑图（可直接投屏）

这九页是信息图页，都做了**双轨**：

- `images/logic/` 下有同名 PNG → 用 PNG，铺满整块图区（`object-fit:contain`，不裁切）；
- 没有 PNG → 自动回落到页面内联的**瑞士风 SVG 逻辑图**（细线网格、IKB 强调、几何只画线、标签全走 HTML）。

**换图只要覆盖同名文件，HTML 一个字都不用改。**

| 页 | 逻辑图内容 | 文件名（Imagine 交付名） |
|---|---|---|
| 02 | 战略三栏递进：国家 → 公司 → 园区 | `images/logic/p02-strategic-chain.png` |
| 08 | 三主线 × 六属性关系图（分叉连线） | `images/logic/p08-six-dimension-map.png` |
| 09 | 调研 → 方案映射（三路汇入一揽子） | `images/logic/p09-research-to-scheme.png` |
| 12 | 三端协同（中心端 / 管理端 / 员工端 + 联动回路） | `images/logic/p12-three-ends.png` |
| 13 | 数字底座分层（四层 + 南网增量三件） | `images/logic/p13-digital-base.png` |
| 14 | 诊断—监测—控制闭环（四步 + 回到诊断的闭环弧） | `images/logic/p14-building-loop.png` |
| 18 | 六属性互证闭环（六边形 + 两两互连） | `images/logic/p18-six-proofs.png` |
| 19 | 指标树（目标 → 五类指标 → 条目） | `images/logic/p19-indicator-tree.png` |
| 21 | 四步推进阶段图（三道过关闸口） | `images/logic/p21-four-steps.png` |

**图文件不入库**：云端 VM 读不到小七 Mac 上的交付夹，`images/logic/` 在本 PR 里是空的。落 Mac 时一条命令拷进来即可：

```bash
cp /workspace/content/nanwang-hq-base/assets/logic/*.png \
   hq-base/leader-deck-20260906-guizang/images/logic/
```

**写错名也能挂上**：每个图位除主名外还挂了一条候选链（例如 14 页主名 `p14-building-loop.png`，取不到会依次再试 `p14-green-smart-building.png`、`p14-diagnose-monitor-control.png`），全部取不到才回落 SVG。完整候选表见 [`LOGIC-IMAGE-MAP-20260906.md`](LOGIC-IMAGE-MAP-20260906.md)。

**导出建议**：宽 ≥ 2400 px，甜点比例约 **3:1**（图区实测 2.92:1 ～ 3.72:1，`object-fit:contain` 不裁切，比例不一致只留边）；**透明底最稳**——14 页是暗底页，白底 PNG 挂上去会出现一块白板。图内不要画页眉页脚、页码、标题、边框、署名，也不要出现新的数字或新口径。

---

## 待补实拍清单

以下图位目前是**瑞士风网格占位框**（框里印着它等的文件名），不是假图、也没有拿示意图冒充实拍。把文件按下表路径拷进来，刷新页面就出图。

| 路径 | 落在哪一页 | 画面 |
|---|---|---|
| `images/00-cover-aerial.jpg` | 01 封面 | 园区航拍／全景。到位后自动铺成整幅底图并压一层 IKB 蒙版；不到位就保持纯 IKB + ASCII 呼吸场。 |
| `images/sites/05-boao.jpg` | 05 三个现场 | 博鳌零碳示范区建成区绿色更新现场 |
| `images/sites/05-sgcc-xiongan.jpg` | 05 三个现场 | 国网雄安创新中心运行现场 |
| `images/sites/05-huaneng-xiongan.jpg` | 05 三个现场 | 华能雄安总部运行现场 |
| `images/green/datacenter-cold-aisle.jpg` | 10 绿色属性 | 绿色机房冷通道封闭 |
| `images/green/waste-heat-flow.jpg` | 10 绿色属性 | 机房排热经热泵变成生活热水（三环节一条线） |
| `images/green/pv-rooftop-carport.jpg` | 10 绿色属性 | 屋顶与车棚光伏普查，外立面留白不标 |
| `images/green/carbon-ledger.jpg` | 10 绿色属性 | 一本总账在中间，办公与机房两个子账在两侧 |
| `images/efficient/chiller-plant.jpg` | 11 高效属性 | 冷站机房实拍（**整幅主视觉**，21:9，主体放中央安全区） |
| `images/human/parking-reserve.jpg` | 15 普惠 | 车位和充电桩按同一队列排，先约先用 |
| `images/human/env-dashboard.jpg` | 16 健康 | 楼层环境公示牌：实时数值 + 当日达标时长 |
| `images/human/meeting-endpoint-auto.jpg` | 17 人文 | 预约即末端开关，人到灯亮风起 |

补图要求：横图，短边不低于 1600 px（05 / 10 / 15 / 16 / 17 的框是 21:9，11 是整幅 21:9）；照片按 `object-fit:cover` 居中裁切，主体别贴边；奖项、认证标识、可识别人脸不要入镜。扩展名统一 `.jpg`，换成 `.png` 要同步改 HTML 里的 `src`。

> 云端拿不到 Box 和 Mac 本地盘，上表全部要在本地由小七拷入。

### 汇报当天不想露出文件路径

占位框默认会把它等的那个文件名印在框里（补图时照着拷就行）。如果当天还有图没补上、又不想让领导看见 `images/...` 这种路径，把 HTML 第一行 `<body>` 上的 `show-slot-filenames` 去掉即可：

```html
<body class="canvas-mode show-slot-filenames">   <!-- 改成 -->
<body class="canvas-mode">
```

改完占位框只剩「待补实拍」和框下那句中文说明，网格底纹照旧，页面其余部分不受影响。

---

## 文案与口径底线

正文只用已定稿文案，落版**只允许拆行、不允许改字**。三处 Researchy 已定措辞原样保留：

1. 华能：**绿色低碳、健康人文、智慧运营协同运行**
2. **博鳌零碳示范区**
3. 绿色：**存量改造合理量级**

绿色 / 高效两页表脚固定写 **「内部测算，待基线书面核验」**；PUE、EER、百分比这类参照量级数字一律挂「参照」角标，不当已实现承诺。页面上不出现「本页 / 不上 / 待核 / 不构成」这类制作口吻，也没有发明新的领导口径。

`copy-source/` 是三个定稿包的只读镜像（内容与 #67 / #68 / #69 完全一致），仅供校验脚本比对，改文案请改原 PR。

---

## 自检脚本

```bash
# 1. 落版校验：页序 + 逐句比对 + 锁定措辞 + 禁用词 + 参照角标
python3 hq-base/leader-deck-20260906-guizang/check_deck_copy.py

# 2. guizang 瑞士风版式校验（需要 playwright，会用 1600×900 实测溢出）
node <guizang-skill>/scripts/validate-swiss-deck.mjs \
     "hq-base/leader-deck-20260906-guizang/leader-deck-20260906_by小七.html"

# 3. 演讲者模式与备注契约校验
node <guizang-skill>/scripts/validate-presenter-mode.mjs \
     "hq-base/leader-deck-20260906-guizang/leader-deck-20260906_by小七.html"
```

当前状态：落版校验 **23 页页序一致、291 条定稿句逐句命中**；瑞士风校验 **0 error**；演讲者模式校验 **0 error / 0 warning，23 页备注，25.8 分钟**。
