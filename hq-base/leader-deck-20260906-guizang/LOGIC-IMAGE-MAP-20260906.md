# 逻辑图挂载对照表 · 2026-09-06

Imagine 已交 9 张瑞士风逻辑图。本文件登记**页 → 文件名 → 挂载状态**，是补图和换图时的唯一对照表。

- 交付夹（小七 Mac）：`/workspace/content/nanwang-hq-base/assets/logic/*.png`
- 落位目录（本仓库）：`hq-base/leader-deck-20260906-guizang/images/logic/`
- 云端 VM 读不到 Mac 本地盘，**图文件不入库**，由小七落 Mac 时一并拷进交付夹。

---

## 一条命令拷进来

```bash
cd <仓库根>
cp /workspace/content/nanwang-hq-base/assets/logic/*.png \
   hq-base/leader-deck-20260906-guizang/images/logic/
```

拷完刷新浏览器即可，**HTML 一个字都不用改**。

---

## 对照表

| 页 | slide-id | 主文件名（Imagine 交付名） | 图应该说清什么 |
|---:|---|---|---|
| 02 | `strategic-alignment-chain` | `images/logic/p02-strategic-chain.png` | 战略三栏递进：国家 → 公司 → 园区，落点在园区能力 |
| 08 | `six-dimension-map` | `images/logic/p08-six-dimension-map.png` | 三主线 × 六属性：绿色主线辖绿色+高效，智慧主线辖智慧，人文主线辖普惠+健康+人文 |
| 09 | `research-to-scheme` | `images/logic/p09-research-to-scheme.png` | 三路调研来源 → 各自吸收什么 → 进入方案哪一块 |
| 12 | `mpark-three-ends` | `images/logic/p12-three-ends.png` | 中心端 / 管理端 / 员工端 + 一次预约联动末端的回路 |
| 13 | `digital-base` | `images/logic/p13-digital-base.png` | 统一接入 / 数据 / 管理 / 联动 四层 + 南网增量三件 |
| 14 | `green-smart-building` | `images/logic/p14-building-loop.png` | 诊断起点 → 分区改造 → 四级监测 → 控制闭环，末端回到诊断 |
| 18 | `six-proofs` | `images/logic/p18-six-proofs.png` | 六项属性两两互连的闭环 |
| 19 | `indicator-tree` | `images/logic/p19-indicator-tree.png` | 目标 → 绿色/高效/智慧/人文/协同 五类 → 各自条目 |
| 21 | `four-steps` | `images/logic/p21-four-steps.png` | 四步阶段轴 + 三道「数据合格才进下一步」过关闸口 |

> **P18**：如果当前这张箭头旁还带「IKB」字样，先挂上不影响放映；Imagine 的干净版出来后**覆盖同名文件**即可，不用改 HTML、不用改本表。

---

## 候选文件名（写错名也能挂上）

每个图位除主文件名外还挂了一条候选链，主名取不到会按顺序逐个再试，全部取不到才回落到页面内联的瑞士风 SVG 逻辑图。所以历史命名、少一位页码这些写法都能兜住。

| 页 | 主文件名 | 候选 1 | 候选 2 | 候选 3 |
|---:|---|---|---|---|
| 02 | `p02-strategic-chain.png` | `p02-strategic-alignment-chain.png` | `p2-strategic-chain.png` | `p2-strategic-alignment-chain.png` |
| 08 | `p08-six-dimension-map.png` | `p8-six-dimension-map.png` | — | — |
| 09 | `p09-research-to-scheme.png` | `p9-research-to-scheme.png` | — | — |
| 12 | `p12-three-ends.png` | `p12-mpark-three-ends.png` | — | — |
| 13 | `p13-digital-base.png` | `p13-unified-digital-base.png` | — | — |
| 14 | `p14-building-loop.png` | `p14-green-smart-building.png` | `p14-diagnose-monitor-control.png` | — |
| 18 | `p18-six-proofs.png` | `p18-six-proofs-clean.png` | — | — |
| 19 | `p19-indicator-tree.png` | `p19-indicators.png` | — | — |
| 21 | `p21-four-steps.png` | `p21-rollout.png` | — | — |

---

## 图区实测尺寸与导出建议

1600 × 900 投屏下，九个图区的实测像素（宽固定 1440，高由该页标题行数决定）：

| 页 | 图区 | 比例 | 页底色 |
|---:|---|---|---|
| 02 | 1440 × 396 | 3.64 : 1 | 纸白 |
| 08 | 1440 × 445 | 3.24 : 1 | 纸白 |
| 09 | 1440 × 443 | 3.25 : 1 | 浅灰 |
| 12 | 1440 × 387 | 3.72 : 1 | 浅灰 |
| 13 | 1440 × 443 | 3.25 : 1 | 纸白 |
| 14 | 1440 × 466 | 3.09 : 1 | **暗底（ink）** |
| 18 | 1440 × 493 | 2.92 : 1 | 纸白 |
| 19 | 1440 × 443 | 3.25 : 1 | 浅灰 |
| 21 | 1440 × 483 | 2.98 : 1 | 纸白 |

**导出建议**

- 图区按 `object-fit:contain` 显示，**不会裁切**，比例不一致只会左右或上下留边。
- 甜点比例约 **3 : 1**（例如 2400 × 800）；宽建议 ≥ 2400 px。
- 底色：透明底最稳。**14 页是暗底页**，白底 PNG 挂上去会出现一块白板，务必用透明底。09 / 12 / 19 是浅灰底页，透明或 `#f0f0ee` 都行，纸白 `#fafaf8` 会有极轻的色差。
- 图内**不要**画页眉、页脚、页码、标题、导语、边框、署名、Logo —— 这些页面自己已经有了，画进去会重影。
- 图内**不要**出现新的数字或新口径；标签只用页面上已有的措辞。百分比、PUE、EER 这类参照量级如果出现在图内，必须同样带「参照」字样，不能读成已实现承诺。

---

## 落位后怎么自检

```bash
python3 hq-base/leader-deck-20260906-guizang/check_deck_copy.py
```

打开 HTML 逐页看这 9 页：图挂上了就是整幅 PNG 铺在标题下方、页脚之上；没挂上会自动显示页面内联的瑞士风 SVG 逻辑图（也能直接投屏，不会开天窗）。两种状态都已实测通过。
