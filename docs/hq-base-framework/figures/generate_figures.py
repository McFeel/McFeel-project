#!/usr/bin/env python3
"""Generate F01–F12 figures for the headquarters-base framework document.

All facts and numbers in these figures come only from:
  docs/hq-base-framework/01-技术与案例清单.md

Outputs are white-background SVG sources plus 300 dpi PNG files.  The SVG
files retain text and vector shapes for direct editing in vector software.
"""

from __future__ import annotations

import math
import textwrap
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle


OUT = Path(__file__).resolve().parent

# Southern Power Grid-inspired blue/green palette, with grayscale-safe borders.
BLUE = "#0068B7"
BLUE_D = "#174A72"
BLUE_L = "#E8F3FA"
GREEN = "#00A86B"
GREEN_D = "#087A58"
GREEN_L = "#E6F6EF"
TEAL = "#13A7A0"
TEAL_L = "#E7F7F6"
INK = "#20303C"
MID = "#5F6F7A"
LINE = "#9AAAB4"
PALE = "#F5F8FA"
WHITE = "#FFFFFF"
AMBER = "#E59B22"
AMBER_L = "#FFF4DD"
RED = "#C94B52"
RED_L = "#FCECEE"

mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Noto Sans CJK SC", "Droid Sans Fallback", "WenQuanYi Micro Hei"],
        "axes.unicode_minus": False,
        "svg.fonttype": "none",
        "figure.facecolor": WHITE,
        "savefig.facecolor": WHITE,
    }
)


def canvas(width: float, height: float):
    """Create a normalized, borderless drawing canvas."""
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def wrap(text: str, width: int) -> str:
    """Wrap Chinese-friendly text while preserving explicit line breaks."""
    parts = []
    for line in text.split("\n"):
        parts.append("\n".join(textwrap.wrap(line, width=width, break_long_words=True) or [""]))
    return "\n".join(parts)


def box(
    ax,
    x,
    y,
    w,
    h,
    *,
    fc=WHITE,
    ec=LINE,
    lw=1.2,
    radius=0.012,
    z=1,
):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.006,rounding_size={radius}",
        facecolor=fc,
        edgecolor=ec,
        linewidth=lw,
        zorder=z,
    )
    ax.add_patch(patch)
    return patch


def txt(
    ax,
    x,
    y,
    text,
    *,
    size=11,
    color=INK,
    weight="normal",
    ha="center",
    va="center",
    linespacing=1.25,
    z=5,
):
    return ax.text(
        x,
        y,
        text,
        fontsize=size,
        color=color,
        fontweight=weight,
        ha=ha,
        va=va,
        linespacing=linespacing,
        zorder=z,
    )


def title(ax, code: str, heading: str, claim: str | None = None):
    txt(ax, 0.03, 0.965, code, size=10, color=WHITE, weight="bold", ha="left")
    box(ax, 0.022, 0.942, 0.055, 0.045, fc=BLUE, ec=BLUE, radius=0.008, z=2)
    txt(ax, 0.095, 0.967, heading, size=17, weight="bold", ha="left")
    ax.plot([0.025, 0.975], [0.925, 0.925], color=GREEN, linewidth=2.4)
    if claim:
        txt(ax, 0.975, 0.9, claim, size=9.2, color=GREEN_D, weight="bold", ha="right")


def arrow(ax, start, end, *, color=BLUE, lw=1.8, style="-|>", rad=0, z=3):
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle=style,
        mutation_scale=12,
        linewidth=lw,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
        zorder=z,
    )
    ax.add_patch(patch)
    return patch


def footer(ax, text: str):
    txt(ax, 0.025, 0.02, text, size=7.6, color=MID, ha="left", va="bottom")


def save(fig, slug: str):
    png = OUT / f"{slug}.png"
    svg = OUT / f"{slug}.svg"
    fig.savefig(png, dpi=300, bbox_inches=None, pad_inches=0)
    fig.savefig(svg, bbox_inches=None, pad_inches=0)
    plt.close(fig)


def draw_f01():
    fig, ax = canvas(7.2, 5.6)
    title(ax, "F01", "政策束与三层战略收拢")

    policy = [
        ("国家方向", "六张网 · 节能降碳 · 人工智能赋能能源", BLUE),
        ("行业与电网", "新型电力系统 · 数字电网 · 算电协同", TEAL),
        ("园区与建筑", "既有建筑提效 · 分项计量 · 碳核算", GREEN),
        ("南网自身", "协同发展 · 战略资产 · 第二增长曲线", BLUE_D),
    ]
    for i, (head, body, color) in enumerate(policy):
        y = 0.79 - i * 0.145
        box(ax, 0.03, y, 0.39, 0.105, fc=WHITE, ec=color, lw=1.7)
        box(ax, 0.03, y, 0.12, 0.105, fc=color, ec=color, radius=0.01)
        txt(ax, 0.09, y + 0.052, wrap(head, 6), size=9.2, color=WHITE, weight="bold")
        txt(ax, 0.16, y + 0.052, wrap(body, 13), size=8.2, ha="left")

    txt(ax, 0.225, 0.2, "政策束", size=10, weight="bold", color=BLUE_D)
    arrow(ax, (0.43, 0.55), (0.49, 0.55), color=GREEN, lw=2.5)

    stages = [
        (0.5, 0.73, 0.45, 0.16, BLUE_L, BLUE, "国家建“六张网”",
         "水网｜新型电网｜算力网\n新一代通信网｜城市地下管网｜物流网"),
        (0.55, 0.48, 0.35, 0.145, TEAL_L, TEAL, "南网做协同",
         "以新型电网为枢纽\n算电协同为突破口"),
        (0.61, 0.25, 0.23, 0.15, GREEN_L, GREEN, "加快积累战略资产",
         "驱动第二增长曲线"),
    ]
    for x, y, w, h, fc, ec, head, body in stages:
        box(ax, x, y, w, h, fc=fc, ec=ec, lw=2)
        txt(ax, x + w / 2, y + h * 0.68, head, size=11.2, weight="bold", color=ec)
        txt(ax, x + w / 2, y + h * 0.28, body, size=8.2)
    arrow(ax, (0.725, 0.72), (0.725, 0.64), color=BLUE_D)
    arrow(ax, (0.725, 0.47), (0.725, 0.40), color=BLUE_D)
    arrow(ax, (0.725, 0.25), (0.725, 0.16), color=GREEN, lw=2.5)
    ax.add_patch(Circle((0.725, 0.105), 0.06, facecolor=GREEN, edgecolor=GREEN_D, lw=2))
    txt(ax, 0.725, 0.125, "总部基地", size=9.5, color=WHITE, weight="bold")
    txt(ax, 0.725, 0.087, "第一验证场", size=7.8, color=WHITE, weight="bold")
    footer(ax, "国家层及“2+3+N”协调机制采用【公开报道】口径；不将国家任务写成本项目资格。")
    save(fig, "F01-政策束与三层战略收拢")


def draw_f02():
    fig, ax = canvas(7.2, 7.0)
    title(ax, "F02", "一核六边：总体架构", "边向核沉淀资产 · 核为边定方向")
    cx, cy, r = 0.5, 0.51, 0.245
    pts = [(cx + r * math.cos(math.radians(90 - i * 60)),
            cy + r * math.sin(math.radians(90 - i * 60))) for i in range(6)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=PALE, edgecolor=BLUE, lw=2.5))
    ax.add_patch(Circle((cx, cy), 0.145, facecolor=BLUE_D, edgecolor=GREEN, lw=4))
    txt(ax, cx, cy + 0.055, "一  核", size=12, color="#BDEBDA", weight="bold")
    txt(ax, cx, cy, "加快积累战略资产", size=12.5, color=WHITE, weight="bold")
    txt(ax, cx, cy - 0.045, "驱动第二增长曲线", size=12.5, color=WHITE, weight="bold")
    txt(ax, cx, cy - 0.098, "算电协同落在核上", size=9.5, color="#CFE8F6", weight="bold")

    nodes = [
        ("绿色", "碳账·绿电\n光伏与负荷", 0.5, 0.835, GREEN),
        ("高效", "冷站诊断·AI群控\n蓄冷对接电价", 0.82, 0.68, BLUE),
        ("智慧", "一个平台两类功能\n数字孪生", 0.82, 0.34, TEAL),
        ("普惠", "人人参与\n人人受益", 0.5, 0.15, GREEN_D),
        ("健康", "可检测\n可验收", 0.18, 0.34, BLUE_D),
        ("人文", "风貌·场所\n获得感", 0.18, 0.68, AMBER),
    ]
    for head, body, x, y, color in nodes:
        box(ax, x - 0.115, y - 0.064, 0.23, 0.128, fc=WHITE, ec=color, lw=2)
        box(ax, x - 0.115, y - 0.064, 0.065, 0.128, fc=color, ec=color)
        txt(ax, x - 0.082, y, head, size=11, color=WHITE, weight="bold")
        txt(ax, x - 0.035, y, body, size=9.2, ha="left", weight="bold")

    for i in range(6):
        ang = math.radians(90 - i * 60)
        p1 = (cx + 0.155 * math.cos(ang), cy + 0.155 * math.sin(ang))
        p2 = (cx + 0.225 * math.cos(ang), cy + 0.225 * math.sin(ang))
        arrow(ax, p1, p2, color=LINE, lw=1.2, style="<|-|>")
    footer(ax, "战略是核，不占边；六边独立落实、分开验收。基地是验证场与明牌，不是第二增长曲线本身。")
    save(fig, "F02-一核六边总体架构")


def draw_f03():
    fig, ax = canvas(8.0, 5.2)
    title(ax, "F03", "战略资产四件套与复制路径", "资产带走 · 园区留下")
    box(ax, 0.03, 0.13, 0.43, 0.73, fc=BLUE_L, ec=BLUE, lw=2)
    txt(ax, 0.245, 0.815, "总部基地｜内部验证场", size=13, color=BLUE_D, weight="bold")
    cards = [
        ("碳账与核算口径", "园区碳账本\n机房进出账规则", GREEN),
        ("调控与交易模型", "柔性资源\n电价与交易控制", BLUE),
        ("数字底座与数据资产", "平台架构\n数据与训练模型", TEAL),
        ("改造与运营方法论", "不停机·分区试点\n先测后改", AMBER),
    ]
    for i, (head, body, color) in enumerate(cards):
        x = 0.06 + (i % 2) * 0.195
        y = 0.53 - (i // 2) * 0.29
        box(ax, x, y, 0.17, 0.22, fc=WHITE, ec=color, lw=1.7)
        txt(ax, x + 0.085, y + 0.153, wrap(head, 9), size=10.2, color=color, weight="bold")
        txt(ax, x + 0.085, y + 0.065, body, size=8.7)

    arrow(ax, (0.46, 0.5), (0.57, 0.5), color=GREEN, lw=3)
    txt(ax, 0.515, 0.56, "形成可带走资产", size=9, color=GREEN_D, weight="bold")
    box(ax, 0.57, 0.13, 0.40, 0.73, fc=WHITE, ec=GREEN, lw=2)
    txt(ax, 0.77, 0.815, "内部验证 → 行业复制", size=13, color=GREEN_D, weight="bold")
    path = [(0.61, 0.30), (0.69, 0.38), (0.77, 0.50), (0.87, 0.66), (0.94, 0.74)]
    ax.plot([p[0] for p in path], [p[1] for p in path], color=BLUE, lw=4)
    for x, y in path:
        ax.add_patch(Circle((x, y), 0.012, facecolor=WHITE, edgecolor=BLUE, lw=2))
    milestones = [
        (0.61, 0.245, "基地验证\n运行数据可核验"),
        (0.77, 0.42, "南网内复制\n验证多园区架构"),
        (0.93, 0.65, "行业复制\n输出能碳一体化能力"),
    ]
    for x, y, label in milestones:
        txt(ax, x, y, label, size=9, weight="bold")
    txt(ax, 0.77, 0.18, "基地＝明牌，不是曲线本身", size=11, color=BLUE_D, weight="bold")
    footer(ax, "验收不是“园区多好看”，而是“跑通后能否复制给下一座连续办公既有园区”。")
    save(fig, "F03-战略资产四件套与复制路径")


def draw_f04():
    fig, ax = canvas(7.2, 6.4)
    title(ax, "F04", "既有园区现状与五项硬约束", "约束反向塑造方案")
    ax.add_patch(Polygon([(0.36, 0.33), (0.65, 0.33), (0.72, 0.52), (0.61, 0.70),
                          (0.37, 0.68), (0.29, 0.49)], closed=True, facecolor=PALE,
                         edgecolor=BLUE, lw=2))
    for x, y, w, h in [(0.39, 0.51, 0.12, 0.11), (0.53, 0.46, 0.11, 0.15),
                        (0.36, 0.39, 0.15, 0.09), (0.54, 0.36, 0.09, 0.07)]:
        ax.add_patch(Rectangle((x, y), w, h, facecolor=BLUE_L, edgecolor=BLUE_D, lw=1.2))
    txt(ax, 0.5, 0.74, "广州科学城 · 持续运行的既有园区", size=12, color=BLUE_D, weight="bold")
    txt(ax, 0.5, 0.29, "不停机 · 不大拆 · 先测后改", size=11, color=GREEN_D, weight="bold")

    constraints = [
        (0.02, 0.66, 0.27, 0.14, "持续办公", "约 5000 人\n不可成片停机", BLUE),
        (0.71, 0.66, 0.27, 0.14, "设备年限", "主要设备 2016 年投运\n未到报废年限", TEAL),
        (0.01, 0.42, 0.26, 0.14, "历史风貌", "外立面不可大改\n采用针灸式更新", AMBER),
        (0.73, 0.41, 0.26, 0.14, "光伏边界", "屋顶空间有限\n现状约 2 点几 MW", GREEN),
        (0.36, 0.12, 0.29, 0.14, "用电口径", "年用电约 7000 万度\n机房是否计入待核", BLUE_D),
    ]
    for x, y, w, h, head, body, color in constraints:
        box(ax, x, y, w, h, fc=WHITE, ec=color, lw=1.8)
        txt(ax, x + 0.02, y + h * 0.7, head, size=10.5, color=color, weight="bold", ha="left")
        txt(ax, x + 0.02, y + h * 0.31, body, size=8.6, ha="left")
        arrow(ax, (x + w / 2, y if y > 0.3 else y + h),
              (0.5, 0.5), color=LINE, lw=1, style="-", z=0)

    box(ax, 0.03, 0.065, 0.94, 0.055, fc=GREEN_L, ec=GREEN, radius=0.006)
    txt(ax, 0.5, 0.093,
        "不停机 → 园中园试点　｜　风貌受限 → 针灸式更新　｜　设备未报废 → 不换主机先节能",
        size=9.3, weight="bold")
    footer(ax, "以上数字均为【交流纪要／会中口述，待核实】：未经核证，量级参照。")
    save(fig, "F04-既有园区现状与约束")


def draw_f05():
    fig, ax = canvas(7.2, 6.3)
    title(ax, "F05", "目标三档与核算边界决策")
    levels = [
        (0.06, 0.57, 0.25, 0.16, BLUE_L, BLUE, "低碳", "降碳率 ≥30%", "条件较宽｜代价较低\n示范度有限"),
        (0.32, 0.57, 0.30, 0.22, GREEN_L, GREEN, "近零碳", "降碳率 ≥60%", "节能＋绿电协同\n认证口径待核"),
        (0.63, 0.57, 0.31, 0.28, AMBER_L, AMBER, "碳中和／零碳", "总量 ≤0；抵消 ≤30%", "边界敏感｜抵消依赖高\n标准状态待核"),
    ]
    for x, y, w, h, fc, ec, head, metric, note in levels:
        box(ax, x, y, w, h, fc=fc, ec=ec, lw=2)
        txt(ax, x + w / 2, y + h * 0.71, head, size=13, color=ec, weight="bold")
        txt(ax, x + w / 2, y + h * 0.44, metric, size=10.5, weight="bold")
        txt(ax, x + w / 2, y + h * 0.16, note, size=7.8)
    arrow(ax, (0.47, 0.885), (0.47, 0.80), color=GREEN, lw=2.3)
    txt(ax, 0.47, 0.88, "项目名称“绿色近零碳”", size=9.5, color=GREEN_D, weight="bold", va="bottom")
    footer(ax, "三级台阶据【宣讲材料】；标准稿件状态待核实。宣讲数据未经核证，仅作口径参照。")

    box(ax, 0.04, 0.11, 0.92, 0.38, fc=PALE, ec=BLUE_D, lw=1.8)
    box(ax, 0.38, 0.40, 0.24, 0.065, fc=BLUE_D, ec=BLUE_D)
    txt(ax, 0.5, 0.433, "核算边界前置决策", size=11, color=WHITE, weight="bold")
    arrow(ax, (0.50, 0.40), (0.27, 0.34), color=BLUE)
    arrow(ax, (0.50, 0.40), (0.73, 0.34), color=GREEN)
    box(ax, 0.08, 0.16, 0.36, 0.17, fc=WHITE, ec=BLUE, lw=1.7)
    txt(ax, 0.26, 0.286, "数据机房入账", size=11, color=BLUE, weight="bold")
    txt(ax, 0.26, 0.22, "园区基数大｜余热收益可计\n边界统一｜达标压力更高", size=9)
    box(ax, 0.56, 0.16, 0.36, 0.17, fc=WHITE, ec=GREEN, lw=1.7)
    txt(ax, 0.74, 0.286, "机房独立核算", size=11, color=GREEN_D, weight="bold")
    txt(ax, 0.74, 0.22, "机房专题叙事更集中\n暂无全国统一专项判定标准", size=9)
    txt(ax, 0.5, 0.13, "边界选择联动目标档位、余热利用与算力普惠", size=9.3, color=INK, weight="bold")
    save(fig, "F05-目标三档与边界决策")


def draw_matrix(ax, rows, columns, *, x=0.03, y=0.06, w=0.94, h=0.82,
                col_widths=None, row_label_w=0.075, header_h=0.07,
                fontsize=7.7, highlight=None):
    """Draw a compact information matrix with row labels outside four columns."""
    col_widths = col_widths or [0.18, 0.37, 0.20, 0.25]
    data_x = x + row_label_w
    data_w = w - row_label_w
    rh = (h - header_h) / len(rows)
    colors = [BLUE_D, BLUE, TEAL, GREEN, AMBER, MID]
    ax.add_patch(Rectangle((data_x, y + h - header_h), data_w, header_h,
                           facecolor=BLUE_D, edgecolor=WHITE, lw=1))
    xx = data_x
    for i, col in enumerate(columns):
        cw = data_w * col_widths[i]
        txt(ax, xx + cw / 2, y + h - header_h / 2, col, size=9, color=WHITE, weight="bold")
        xx += cw
    for r, row in enumerate(rows):
        yy = y + h - header_h - (r + 1) * rh
        fc = GREEN_L if highlight == r else (WHITE if r % 2 == 0 else PALE)
        ax.add_patch(Rectangle((x, yy), w, rh, facecolor=fc, edgecolor=LINE, lw=0.8))
        ax.add_patch(Rectangle((x, yy), row_label_w, rh, facecolor=colors[r],
                               edgecolor=WHITE, lw=1))
        txt(ax, x + row_label_w / 2, yy + rh / 2, row[0], size=10, color=WHITE, weight="bold")
        xx = data_x
        for i, cell in enumerate(row[1:]):
            cw = data_w * col_widths[i]
            txt(ax, xx + 0.008, yy + rh / 2, cell, size=fontsize,
                ha="left", linespacing=1.22)
            xx += cw


def draw_f06():
    fig, ax = canvas(8.0, 7.8)
    title(ax, "F06", "六边 × 技术族：第五章行动导览")
    rows = [
        ("绿色", "能碳算清、管住\n形成可交易闭环",
         "G1 碳账台阶　G2 核算边界\nG3 绿电抵消　G4 光伏普查\nG5 源网荷储　G6 水与微气候",
         "碳账立账\n光伏资源普查",
         "碳账口径\n抵消结构方法"),
        ("高效", "以实测诊断\n提升运行效率",
         "E1 冷站水系统诊断　E2 AI 群控\nE3 蓄冷电价　E4 行为联动\nE5 余热回收　E6 楼宇分档",
         "冷站诊断进场\n蓄冷策略专题",
         "实测基线\n诊断与调控模型"),
        ("智慧", "统一数字底座\n连接园内园外",
         "智慧① 一个平台两类功能\n② 四级计量　③ 孪生/AIOC\n④ 预测与 AI 调优　⑤ 数据主权",
         "平台总体设计\n会议室联动轻改",
         "平台架构·数据目录\n接口标准·训练模型"),
        ("普惠", "人人参与\n人人受益",
         "P1 碳普惠　P2 算力普惠\nP3 园区资源普惠\nP4 无障碍与适老化",
         "碳账规则设计\n资源统一预约",
         "全员参与机制\n行为核算方法"),
        ("健康", "环境可检测\n改善可验收",
         "H1 环境连续监测\nH2 新风与净化　H3 健康照明\nH4 健身休憩与心理健康",
         "楼层环境监测\n风系统同步诊断",
         "健康环境验收规则\n隐私边界"),
        ("人文", "风貌延续\n场所可感",
         "C1 针灸式更新\nC2 半开放空间与微气候\nC3 电网文化科普　C4 获得感运营",
         "公共节点试点\n真实系统动线",
         "连续办公园区\n以人为本改造方法"),
    ]
    draw_matrix(
        ax, rows, ["边的定义", "硬技术族", "首批动作", "沉淀资产"],
        x=0.025, y=0.055, w=0.95, h=0.83,
        col_widths=[0.18, 0.39, 0.19, 0.24],
        fontsize=9.0, highlight=2,
    )
    box(ax, 0.78, 0.885, 0.18, 0.035, fc=GREEN, ec=GREEN, radius=0.005)
    txt(ax, 0.87, 0.903, "5.3 偏重展开", size=8.3, color=WHITE, weight="bold")
    footer(ax, "技术族编号与内容均取《01-技术与案例清单》；矩阵用于导航，不替代各节技术说明。")
    save(fig, "F06-六边技术族行动矩阵")


def draw_f07():
    fig, ax = canvas(8.0, 7.2)
    title(ax, "F07", "一个平台、两类功能：智慧架构", "一次规划 · 避免二次集成")

    # Top wings
    box(ax, 0.035, 0.64, 0.41, 0.235, fc=BLUE_L, ec=BLUE, lw=2)
    box(ax, 0.555, 0.64, 0.41, 0.235, fc=GREEN_L, ec=GREEN, lw=2)
    txt(ax, 0.24, 0.835, "园内侧｜让运行更高效、更可感", size=11.5, color=BLUE, weight="bold")
    txt(ax, 0.76, 0.835, "园外侧｜连接电网、交易与碳", size=11.5, color=GREEN_D, weight="bold")
    left = ["办公行为联动", "设备工单闭环", "碳普惠记账", "资源预约"]
    right = ["电网互动", "实时电价与交易接口", "碳核算与绿电"]
    for i, item in enumerate(left):
        x = 0.06 + (i % 2) * 0.19
        y = 0.735 - (i // 2) * 0.085
        box(ax, x, y, 0.165, 0.055, fc=WHITE, ec=BLUE, radius=0.008)
        txt(ax, x + 0.0825, y + 0.028, item, size=9, weight="bold")
    for i, item in enumerate(right):
        y = 0.752 - i * 0.07
        box(ax, 0.585, y, 0.25, 0.05, fc=WHITE, ec=GREEN, radius=0.008)
        txt(ax, 0.71, y + 0.025, item, size=8.9, weight="bold")

    box(ax, 0.85, 0.715, 0.125, 0.105, fc=WHITE, ec=GREEN_D, lw=1.8)
    txt(ax, 0.9125, 0.772, "南网数字电网\n／交易系统", size=8.5, color=GREEN_D, weight="bold")
    txt(ax, 0.9125, 0.689, "南网独有增量", size=8.2, color=RED, weight="bold")
    arrow(ax, (0.835, 0.765), (0.85, 0.765), color=GREEN_D, lw=2.2)

    # Platform foundation
    arrow(ax, (0.24, 0.64), (0.39, 0.56), color=BLUE, lw=2.3)
    arrow(ax, (0.76, 0.64), (0.61, 0.56), color=GREEN, lw=2.3)
    box(ax, 0.075, 0.37, 0.85, 0.195, fc=TEAL_L, ec=TEAL, lw=2.4)
    txt(ax, 0.11, 0.527, "平台底座｜一个平台", size=12.5, color=TEAL, weight="bold", ha="left")
    platform = [
        ("数字孪生", "真实运行映射"),
        ("AIOC", "运营指挥与工单"),
        ("负荷预测与 AI 调优", "接电价／需求响应"),
        ("数据资产", "目录·语义·证据链"),
    ]
    for i, (head, sub) in enumerate(platform):
        x = 0.105 + i * 0.202
        box(ax, x, 0.405, 0.18, 0.088, fc=WHITE, ec=TEAL, radius=0.009)
        txt(ax, x + 0.09, 0.461, head, size=9.3, color=TEAL, weight="bold")
        txt(ax, x + 0.09, 0.425, sub, size=7.7, color=MID)
    box(ax, 0.625, 0.335, 0.30, 0.05, fc=BLUE_D, ec=BLUE_D, radius=0.012)
    txt(ax, 0.775, 0.36, "▣  数据主权自持 · 本地化部署", size=9, color=WHITE, weight="bold")

    # Sensing layer
    arrow(ax, (0.5, 0.37), (0.5, 0.31), color=TEAL, style="<|-|>", lw=2)
    box(ax, 0.075, 0.11, 0.85, 0.19, fc=PALE, ec=BLUE_D, lw=2)
    txt(ax, 0.11, 0.263, "感知与计量层｜真实数据入口", size=11.5, color=BLUE_D, weight="bold", ha="left")
    sensors = [
        ("四级用能监测", "地块—楼宇—区域—楼层"),
        ("环境监测", "空气·温湿度·噪声·照度"),
        ("设备物联", "冷站·末端·蓄冷·光伏等"),
    ]
    for i, (head, sub) in enumerate(sensors):
        x = 0.11 + i * 0.275
        box(ax, x, 0.145, 0.245, 0.075, fc=WHITE, ec=BLUE_D, radius=0.009)
        txt(ax, x + 0.1225, 0.192, head, size=9.2, color=BLUE_D, weight="bold")
        txt(ax, x + 0.1225, 0.16, sub, size=7.7, color=MID)
    footer(ax, "架构原则：真实运行数据向上形成应用、向外连接电网；平台、接口与数据主权一次规划。")
    save(fig, "F07-一个平台两类功能智慧架构")


def draw_f08():
    fig, ax = canvas(8.0, 9.2)
    title(ax, "F08", "信息港做法 → 总部基地落点", "逐条映射 · 每行都说明差异化")

    box(ax, 0.03, 0.765, 0.455, 0.11, fc=BLUE_L, ec=BLUE, lw=1.8)
    box(ax, 0.515, 0.765, 0.455, 0.11, fc=GREEN_L, ec=GREEN, lw=1.8)
    txt(ax, 0.05, 0.848, "信息港｜办公＋数据中心复合园区", size=10.5, color=BLUE, weight="bold", ha="left")
    txt(ax, 0.05, 0.802, "602 亩｜约 77 万㎡｜约 2.4 万机架\n日均约 5200 人【公开报道】",
        size=9.0, ha="left")
    txt(ax, 0.535, 0.848, "总部基地｜持续运行的既有园区", size=10.5, color=GREEN_D, weight="bold", ha="left")
    txt(ax, 0.535, 0.802, "既有园区｜约 5000 人持续办公\n【交流纪要】", size=9.3, ha="left")

    cols = [0.30, 0.31, 0.39]
    x0, y0, tw, th = 0.025, 0.055, 0.95, 0.69
    header_h = 0.055
    rh = (th - header_h) / 7
    headers = ["信息港做法（证据等级）", "总部基地落点", "差异化（服务一核）"]
    xx = x0
    for i, head in enumerate(headers):
        cw = tw * cols[i]
        ax.add_patch(Rectangle((xx, y0 + th - header_h), cw, header_h,
                               facecolor=BLUE_D if i < 2 else GREEN_D, edgecolor=WHITE, lw=1))
        txt(ax, xx + cw / 2, y0 + th - header_h / 2, head, size=10.5, color=WHITE, weight="bold")
        xx += cw
    rows = [
        ("会议预约联动\n照明／空调（A）",
         "会议室与公共区首批轻改造\n接入统一平台",
         "联动数据进入园区碳账本\n支撑碳普惠个人记账"),
        ("四级用能监测＋\n智慧用电（A／B）",
         "补齐全园分项计量\n建设能碳数字底座",
         "计量口径同时服务\n碳核算与电力交易结算"),
        ("数字孪生＋AI 管控\n分钟级自检（A）",
         "AIOC 智能运营中心\n以真实运行数据为展项",
         "不做大屏秀；叠加电网侧\n负荷／电价／绿电数据"),
        ("楼宇 64 项\n诊断分档（B）",
         "全园楼宇摸底排序\n形成分期改造计划",
         "诊断结论回到国家标准口径\n校核认证达标"),
        ("机房余热经热泵\n供办公（A）",
         "机房余热—生活热水／\n除湿再热试点",
         "广州气候下先摸需求侧\n与机房核算边界专题绑定"),
        ("算力中心与园区\n同地共生（A）",
         "绿电就近供算力；算力负荷\n参与需求响应／交易",
         "信息港无此公开叙事\n南网独有增量，落在核上"),
        ("本地化部署需\n按设备重训（C）",
         "评估数据归属、合规、\n模型重训与退出成本",
         "数据主权自持为前置条件\n必要时自建底座、外购模块"),
    ]
    for r, row in enumerate(rows):
        yy = y0 + th - header_h - (r + 1) * rh
        fc = GREEN_L if r in (2, 5, 6) else (WHITE if r % 2 == 0 else PALE)
        xx = x0
        for i, cell in enumerate(row):
            cw = tw * cols[i]
            ax.add_patch(Rectangle((xx, yy), cw, rh, facecolor=fc, edgecolor=LINE, lw=0.8))
            txt(ax, xx + 0.008, yy + rh / 2, cell, size=9.5 if i != 2 else 9.3,
                ha="left", linespacing=1.2, weight="bold" if (i == 2 and r in (2, 5, 6)) else "normal")
            xx += cw
    footer(ax, "信息港底数与 A/B 级做法未经本次调研核证；数字仅作量级参照，不进入总部基地指标。")
    save(fig, "F08-信息港做法到总部基地落点")


def draw_f09():
    fig, ax = canvas(8.0, 5.5)
    title(ax, "F09", "柔性资源—实时电价对接路线", "从固定时段控制走向约 15 分钟级调度")
    box(ax, 0.035, 0.23, 0.28, 0.56, fc=BLUE_L, ec=BLUE, lw=2)
    box(ax, 0.685, 0.23, 0.28, 0.56, fc=GREEN_L, ec=GREEN, lw=2)
    txt(ax, 0.175, 0.735, "现状｜固定低谷逻辑", size=12, color=BLUE, weight="bold")
    txt(ax, 0.175, 0.61, "冰蓄冷主机", size=12, weight="bold")
    txt(ax, 0.175, 0.53, "按固定低谷时段蓄冷", size=9.5)
    box(ax, 0.075, 0.36, 0.20, 0.09, fc=WHITE, ec=BLUE)
    txt(ax, 0.175, 0.405, "经济性依赖固定低谷", size=9, weight="bold")
    txt(ax, 0.175, 0.29, "控制目标：\n守住舒适与存量经济性", size=9, color=BLUE_D, weight="bold")

    box(ax, 0.35, 0.29, 0.30, 0.44, fc=AMBER_L, ec=AMBER, lw=2)
    txt(ax, 0.5, 0.675, "机制过渡带", size=12, color=AMBER, weight="bold")
    txt(ax, 0.5, 0.59, "固定低谷时段取消方向", size=9.5, weight="bold")
    txt(ax, 0.5, 0.515, "广东细则预计 1–2 年落地", size=9.5, weight="bold")
    txt(ax, 0.5, 0.44, "跟踪官方文件\n同步改造控制与交易接口", size=9)
    box(ax, 0.38, 0.325, 0.24, 0.065, fc=WHITE, ec=AMBER)
    txt(ax, 0.5, 0.357, "风险也是南网主场", size=9.5, color=AMBER, weight="bold")
    arrow(ax, (0.315, 0.51), (0.35, 0.51), color=AMBER, lw=2.4)
    arrow(ax, (0.65, 0.51), (0.685, 0.51), color=GREEN, lw=2.4)

    txt(ax, 0.825, 0.735, "稳态｜柔性资源池", size=12, color=GREEN_D, weight="bold")
    for i, item in enumerate(["蓄冷", "光伏", "储能", "充电桩"]):
        x = 0.72 + (i % 2) * 0.11
        y = 0.59 - (i // 2) * 0.08
        box(ax, x, y, 0.09, 0.055, fc=WHITE, ec=GREEN)
        txt(ax, x + 0.045, y + 0.028, item, size=8.7, weight="bold")
    txt(ax, 0.825, 0.43, "AI 负荷预测", size=10, color=GREEN_D, weight="bold")
    arrow(ax, (0.825, 0.405), (0.825, 0.36), color=GREEN)
    txt(ax, 0.825, 0.32, "实时电价／需求响应／交易", size=9.2, weight="bold")
    txt(ax, 0.825, 0.26, "控制目标：约 15 分钟级\n经济性＋电网友好协同", size=8.7, color=GREEN_D, weight="bold")
    footer(ax, "时间尺度与落地进度据【交流纪要】，未经核证；需持续跟踪广东官方细则。")
    save(fig, "F09-柔性资源与实时电价路线")


def draw_f10():
    fig, ax = canvas(7.2, 6.2)
    title(ax, "F10", "普惠三环：人人参与、人人受益", "参与聚合为园区碳账资产")
    circles = [
        (0.36, 0.58, 0.20, BLUE_L, BLUE, "碳普惠",
         "个人／团队碳账\n园区总账人人可见"),
        (0.64, 0.58, 0.20, GREEN_L, GREEN, "算力普惠",
         "全员 AI 工具\n算力可用、门槛低"),
        (0.50, 0.36, 0.20, TEAL_L, TEAL, "资源普惠",
         "充电／会议／文体／空间\n规则透明、公平可及"),
    ]
    for x, y, r, fc, ec, head, body in circles:
        ax.add_patch(Circle((x, y), r, facecolor=fc, edgecolor=ec, lw=2, alpha=0.82))
        oy = 0.09 if y > 0.4 else -0.07
        txt(ax, x, y + oy, head, size=12, color=ec, weight="bold")
        txt(ax, x, y + oy - 0.07, body, size=8.2)
    box(ax, 0.37, 0.43, 0.26, 0.08, fc=BLUE_D, ec=WHITE, radius=0.02, z=7)
    txt(ax, 0.5, 0.47, "人人参与 · 人人受益", size=11.5, color=WHITE, weight="bold", z=8)
    box(ax, 0.08, 0.08, 0.84, 0.075, fc=PALE, ec=BLUE_D, lw=1.8)
    txt(ax, 0.5, 0.118, "无障碍与适老化＝标配（地板）", size=11, color=BLUE_D, weight="bold")
    arrow(ax, (0.72, 0.27), (0.88, 0.21), color=GREEN, lw=2)
    txt(ax, 0.86, 0.27, "个人参与聚合\n→ 园区碳账本", size=9, color=GREEN_D, weight="bold")
    footer(ax, "普惠不是投资收益；经营复制叙事归核管理，不进入普惠边。")
    save(fig, "F10-普惠人人参与人人受益")


def draw_f11():
    fig, ax = canvas(8.2, 5.3)
    title(ax, "F11", "实施路线：三件先行与决策节点", "园中园分区试点 · 用运行数据回灌")
    lanes = [
        ("冷站与水系统深度诊断", BLUE, "取得实测基线"),
        ("园区碳账本与核算边界", GREEN, "支撑目标比较"),
        ("平台总体设计", TEAL, "数据主权先定"),
    ]
    for i, (name, color, note) in enumerate(lanes):
        y = 0.79 - i * 0.1
        box(ax, 0.05, y, 0.89, 0.065, fc=WHITE, ec=color, radius=0.008)
        box(ax, 0.05, y, 0.27, 0.065, fc=color, ec=color, radius=0.008)
        txt(ax, 0.185, y + 0.033, name, size=9.5, color=WHITE, weight="bold")
        ax.plot([0.34, 0.72], [y + 0.033, y + 0.033], color=color, lw=3)
        box(ax, 0.74, y + 0.006, 0.18, 0.052, fc=WHITE, ec=WHITE, radius=0.004)
        txt(ax, 0.83, y + 0.033, note, size=8.5, color=color, weight="bold")
    txt(ax, 0.05, 0.89, "三件先行｜当前即启动", size=11, color=BLUE_D, weight="bold", ha="left")

    y = 0.34
    ax.plot([0.09, 0.92], [y, y], color=BLUE_D, lw=3)
    steps = [
        (0.12, "9 月中旬", "方向性汇报\n向两位主任"),
        (0.38, "10 月前", "预可行性方案\n争取立项"),
        (0.64, "框架审议通过后", "网公司分阶段\n安排预算机制"),
        (0.88, "试点实施", "园中园分区试点\n数据回灌"),
    ]
    for x, date, body in steps:
        ax.add_patch(Circle((x, y), 0.018, facecolor=WHITE, edgecolor=BLUE_D, lw=2.5))
        txt(ax, x, y - 0.06, date, size=9.2, color=BLUE_D, weight="bold")
        box(ax, x - 0.09, 0.12, 0.18, 0.105, fc=PALE, ec=LINE)
        txt(ax, x, 0.172, body, size=8.5)
    for x, label in [(0.27, "目标档位决策"), (0.52, "核算边界决策")]:
        diamond = Polygon([(x, 0.43), (x + 0.022, 0.455), (x, 0.48), (x - 0.022, 0.455)],
                          closed=True, facecolor=AMBER_L, edgecolor=AMBER, lw=1.8)
        ax.add_patch(diamond)
        txt(ax, x, 0.505, label, size=8.5, color=AMBER, weight="bold")
    footer(ax, "本图只表达节奏与机制，不包含投资额。具体指标、工程量与预算留待预可研。")
    save(fig, "F11-实施路线与三件先行")


def draw_f12():
    fig, ax = canvas(8.0, 8.8)
    title(ax, "F12", "证据等级与预可研待核清单", "弱证据不升级 · 未核事项不进入指标")
    txt(ax, 0.035, 0.88, "上表｜五级证据使用规则", size=11, color=BLUE_D, weight="bold", ha="left")
    levels = [
        ("A", "公开报道", "可作事实背景；注明未经本次调研核证"),
        ("B", "宣讲材料／产品资料宣称", "只作量级参照，不进入方案指标"),
        ("C", "交流纪要／会中口述估算", "只作背景与约束；数字标待核实"),
        ("D", "交流判断", "明确为本方判断；书面确认后定稿"),
        ("E", "待核实", "不进入正文结论，只进入待核清单"),
    ]
    y0, rh = 0.61, 0.05
    for i, (grade, source, rule) in enumerate(levels):
        y = y0 + (4 - i) * rh
        fc = WHITE if i % 2 == 0 else PALE
        ax.add_patch(Rectangle((0.035, y), 0.93, rh, facecolor=fc, edgecolor=LINE, lw=0.8))
        ax.add_patch(Rectangle((0.035, y), 0.07, rh, facecolor=BLUE_D if i < 3 else MID, edgecolor=WHITE))
        txt(ax, 0.07, y + rh / 2, grade, size=10, color=WHITE, weight="bold")
        txt(ax, 0.12, y + rh / 2, source, size=8.8, ha="left", weight="bold")
        txt(ax, 0.47, y + rh / 2, rule, size=8.5, ha="left")

    txt(ax, 0.035, 0.58, "下表｜进入预可研前必须核掉的八项", size=11, color=GREEN_D, weight="bold", ha="left")
    items = [
        ("园区年用电量口径", "约 7000 万度；机房是否计入", "园区平台数据核验"),
        ("现状光伏装机", "约 2 点几 MW", "并网资料核验"),
        ("标准稿件状态", "报批稿／征求意见稿两说", "向建科院书面确认"),
        ("中移产品用语", "“引导值”待确认", "向中移书面确认"),
        ("信息港运行绩效", "公开材料未见核证", "实地调研重点了解"),
        ("信息港 6 号地信息", "弱来源，核实前不引用", "实地环节核实"),
        ("广东实时电价细则", "进度与约 15 分钟尺度", "跟踪官方文件"),
        ("机房余热需求侧", "广州热需求量级未知", "园区踏勘摸底"),
    ]
    headers = ["事项", "当前口径", "核验方式"]
    widths = [0.26, 0.44, 0.30]
    x0, y0, tw, th = 0.035, 0.065, 0.93, 0.475
    hh = 0.05
    xx = x0
    for i, head in enumerate(headers):
        cw = tw * widths[i]
        ax.add_patch(Rectangle((xx, y0 + th - hh), cw, hh, facecolor=GREEN_D, edgecolor=WHITE))
        txt(ax, xx + cw / 2, y0 + th - hh / 2, head, size=9.2, color=WHITE, weight="bold")
        xx += cw
    row_h = (th - hh) / len(items)
    for r, row in enumerate(items):
        yy = y0 + th - hh - (r + 1) * row_h
        xx = x0
        for i, cell in enumerate(row):
            cw = tw * widths[i]
            ax.add_patch(Rectangle((xx, yy), cw, row_h,
                                   facecolor=WHITE if r % 2 == 0 else PALE,
                                   edgecolor=LINE, lw=0.8))
            txt(ax, xx + 0.008, yy + row_h / 2, cell, size=8.1, ha="left")
            xx += cw
    footer(ax, "数字口径均源自《01-技术与案例清单》；口述／宣称数字未经核证，仅作量级参照。")
    save(fig, "F12-证据等级与待核清单")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for draw in [
        draw_f01,
        draw_f02,
        draw_f03,
        draw_f04,
        draw_f05,
        draw_f06,
        draw_f07,
        draw_f08,
        draw_f09,
        draw_f10,
        draw_f11,
        draw_f12,
    ]:
        draw()
    print(f"Generated 12 SVG and 12 PNG figures in {OUT}")


if __name__ == "__main__":
    main()
