#!/usr/bin/env python3
"""复核本目录三份意见中引用的全部算术结果。

原则：只用报送稿披露的数字做四则运算，不引入外部假设，不为未披露项赋值。
用法：python3 verify_numbers.py
"""


def show(label, value, note=""):
    if isinstance(value, float):
        text = f"{value:,.4f}".rstrip("0").rstrip(".")
    else:
        text = f"{value:,}"
    print(f"{label:<52}{text:>20}  {note}")


def rule(title):
    print()
    print("=" * 96)
    print(title)
    print("=" * 96)


# ---------------------------------------------------------------- 政策分档口径
rule("一、发改高技〔2025〕320号 附件1 规模分档（原件第8页，已核）")
STD_RACK_KW = 2.5
show("3000 标准机架折合设计功率 (kW)", 3000 * STD_RACK_KW, "与原件“7500KW”一致")
show("1000 标准机架折合设计功率 (kW)", 1000 * STD_RACK_KW, "与原件“2500KW”一致")
print("大型及以上判定阈值：≥3000标准架 或 >7500kW 或 当量≥10000tce 或 等价≥24000tce 或 服务器采购≥10亿元")

# ---------------------------------------------------------------- 电信里水 36MW
rule("二、中国电信佛山数据中心（南海里水）36MW")

TEL_IT_KW = 36000.0
TEL_STD_RACK = 14400
TEL_INVEST_WAN = 94638.0
show("14400 标准机架 × 2.5kW (kW)", TEL_STD_RACK * STD_RACK_KW, "＝36MW，与稿内自洽")
show("单位投资 (万元/MW)", TEL_INVEST_WAN / (TEL_IT_KW / 1000))
show("单位投资 (万元/标准架)", TEL_INVEST_WAN / TEL_STD_RACK)

# 实物机柜（两高终稿口径）
racks = [(100.0, 328), (24.0, 82), (15.0, 82)]
tel_rack_kw = sum(kw * n for kw, n in racks)
tel_rack_n = sum(n for _, n in racks)
show("实物机柜台数合计 (台)", tel_rack_n)
show("实物机柜功率合计 (kW)", tel_rack_kw, "≈36MW")
show("平均单柜功率 (kW/台)", tel_rack_kw / tel_rack_n)
show("标准架 14400 对 3000 架阈值倍数", TEL_STD_RACK / 3000)
show("申报值 36000kW 对 7500kW 阈值倍数", TEL_IT_KW / 7500)
show("实物侧 35998kW 对 7500kW 阈值倍数", tel_rack_kw / 7500)

HOURS = 8760
tel_it_wan_kwh = sum(kw * n * HOURS for kw, n in racks) / 10000
show("IT 电量（满载8760h，万kWh）", tel_it_wan_kwh)
show("其中 100kW×328 台 (万kWh)", 100.0 * 328 * HOURS / 10000)

TEL_TOTAL_WAN_KWH = 37818.35
tel_aux = TEL_TOTAL_WAN_KWH - tel_it_wan_kwh
show("年总电量（稿内，万kWh）", TEL_TOTAL_WAN_KWH)
show("反算辅助电量 (万kWh)", tel_aux)
show("PUE ＝ 总电量 ÷ IT 电量", TEL_TOTAL_WAN_KWH / tel_it_wan_kwh, "稿内设计 1.199")

COEF_EQ = 1.229      # 当量值 tce/万kWh
COEF_PRICE = 2.8534  # 等价值 tce/万kWh（电信稿内口径）
tel_eq = TEL_TOTAL_WAN_KWH * COEF_EQ
tel_pr = TEL_TOTAL_WAN_KWH * COEF_PRICE
show("电力折当量值 (tce)", tel_eq, "稿内 46478.76")
show("电力折等价值 (tce)", tel_pr, "稿内 107910.89")

DIESEL_T = 68.64
DIESEL_TCE = 100.02
show("柴油折标隐含系数 (tce/吨)", DIESEL_TCE / DIESEL_T)
show("合计当量值 (tce)", tel_eq + DIESEL_TCE, "稿内 46578.77")
show("合计等价值 (tce)", tel_pr + DIESEL_TCE, "稿内 108010.90")
show("当量值/大型阈值 10000tce 倍数", (tel_eq + DIESEL_TCE) / 10000)
show("等价值/大型阈值 24000tce 倍数", (tel_pr + DIESEL_TCE) / 24000)

show("80% 绿电对应物理电量 (万kWh)", TEL_TOTAL_WAN_KWH * 0.8)
show("年平均运行功率 (kW)", TEL_TOTAL_WAN_KWH * 10000 / HOURS)
show("对 100000kVA 的占比 (%)", TEL_TOTAL_WAN_KWH * 10000 / HOURS / 100000 * 100,
     "稿载负荷率 40.95%")
show("100000kVA × 40.95% (kVA)", 100000 * 0.4095)

DG_N, DG_KW, DG_H = 26, 2200, 6
show("柴发装机合计 (kW)", DG_N * DG_KW)
show("26台×2200kW×6h 发电量 (kWh)", DG_N * DG_KW * DG_H)
show("隐含油耗率 (kg/kWh)", DIESEL_T * 1000 / (DG_N * DG_KW * DG_H))

# 申请书财务口径
show("财务口径 IT 电量（85%，万kWh）", TEL_IT_KW * 0.85 * HOURS / 10000)
show("财务口径电费 (万元)", TEL_IT_KW * 0.85 * HOURS / 10000 * 0.75, "稿内约 20104 万元")
show("能效章与财务章电量差 (万kWh)", TEL_TOTAL_WAN_KWH - TEL_IT_KW * 0.85 * HOURS / 10000)
show("IT电量(负荷1.0)−财务IT电量(85%) (万kWh)",
     tel_it_wan_kwh - TEL_IT_KW * 0.85 * HOURS / 10000)

PFLOPS = 11483.0
show("其他收入 11483P×3.3万/P/月×85% (万元)", PFLOPS * 3.3 * 0.85, "稿内 32210 万元")
show("同式乘 12 个月 (万元)", PFLOPS * 3.3 * 0.85 * 12, "若确为年收入应为此量级")
rev = [7344.0, 3600.0, 184.0, 32210.0]
show("收入四项合计 (万元)", sum(rev), "稿内 43338 万元")
show("收入 − 成本 (万元)", sum(rev) - 20788.4)
show("与稿载利润总额 29561 万元之差 (万元)", 29561 - (sum(rev) - 20788.4))
show("该差额占收入比 (%)", (29561 - (sum(rev) - 20788.4)) / sum(rev) * 100)

show("按上架率 85.10% 的 IT 电量 (万kWh)", TEL_IT_KW * 0.8510 * HOURS / 10000)
show("与财务章 85% 口径之差 (万kWh)", TEL_IT_KW * (0.8510 - 0.85) * HOURS / 10000)
show("“其他收入”×12 ÷ 项目投资 (倍)", PFLOPS * 3.3 * 0.85 * 12 / TEL_INVEST_WAN)
show("“其他收入”占收入合计比 (%)", 32210 / 43338 * 100)
show("现状支撑 80000 架 × 2.5kW (kW)", 80000 * STD_RACK_KW, "＝200MW，支撑文件内部自洽")
show("现状支撑用地 ÷ 里水用地 (倍)", 244.3 / 46.55)
show("11483 PFLOPS ÷ 20992 张 (TFLOPS/张)", PFLOPS / 20992 * 1000)
show("11483 PFLOPS ÷ 17100 张 (TFLOPS/张)", PFLOPS / 17100 * 1000)
show("两套芯片方案单卡算力之差 (TFLOPS/张)", PFLOPS / 17100 * 1000 - PFLOPS / 20992 * 1000)
show("20992 张 ÷ 492 台 (张/台)", 20992 / 492)
show("邦程7MW＋唯颐55MW (MW)", 7 + 55)
show("已签约36MW 占 62MW 需求比 (%)", 36 / 62 * 100)

# ---------------------------------------------------------------- 腾龙湾区
rule("三、腾龙湾区数据中心项目")

air = (480, 14.4)
liq = (7056, 27.78)
tl_air_kw = air[0] * air[1]
tl_liq_kw = liq[0] * liq[1]
tl_kw = tl_air_kw + tl_liq_kw
show("风冷 480×14.4kW (kW)", tl_air_kw)
show("液冷 7056×27.78kW (kW)", tl_liq_kw)
show("机柜逐项合计 (kW)", tl_kw, "＝202.92768MW，稿称“约202.9MW”")
show("液冷占 IT 功率比 (%)", tl_liq_kw / tl_kw * 100)
show("折合 2.5kW 标准机架 (个)", tl_kw / STD_RACK_KW, "稿称约 8.12 万个")
show("标准架对 3000 架阈值倍数", tl_kw / STD_RACK_KW / 3000)
show("大型阈值 7500kW 的倍数", tl_kw / 7500)
show("一期 136MW 对 7500kW 阈值倍数", 136000 / 7500, "分期亦属大型及以上")

TL_TOTAL_YI = 20.8589   # 亿kWh
TL_IT_YI = 17.7765      # 亿kWh
show("PUE ＝ 20.8589 ÷ 17.7765", TL_TOTAL_YI / TL_IT_YI, "稿内设计 1.173")
show("IT 电量 ÷ 8760h (kW)", TL_IT_YI * 1e8 / HOURS, "＝满载202.93MW，负荷率1.0")
show("总电量 ÷ 8760h (kW)", TL_TOTAL_YI * 1e8 / HOURS)

TL_EQ, TL_PR = 256355.86, 591746.09
tl_wan_kwh = TL_TOTAL_YI * 1e8 / 1e4
show("反算当量折标系数 (tce/万kWh)", TL_EQ / tl_wan_kwh, "与电信 1.229 一致")
show("反算等价折标系数 (tce/万kWh)", TL_PR / tl_wan_kwh, "电信用 2.8534，两稿不一致")
show("等价系数两稿之差 (tce/万kWh)", COEF_PRICE - TL_PR / tl_wan_kwh)
show("当量值/大型阈值 10000tce 倍数", TL_EQ / 10000)
show("等价值/大型阈值 24000tce 倍数", TL_PR / 24000)
show("年总电量 × 1.229 (tce)", tl_wan_kwh * COEF_EQ, "稿载当量 256355.86")
show("与稿载当量值之差 (tce)", tl_wan_kwh * COEF_EQ - TL_EQ, "≈0：当量值仅由电量折算")
show("辅助电量＝总电量−IT电量 (亿kWh)", TL_TOTAL_YI - TL_IT_YI)
show("一期 136MW 占整体 IT 功率比 (%)", 136 / (tl_kw / 1000) * 100)
show("一期投资 31.52 占整体 41.81 比 (%)", 31.52 / 41.81 * 100)

show("一期 136MW 满载年电量 (亿kWh)", 136000 * HOURS / 1e8)
show("与稿载总电量 20.8589 亿kWh 之差 (亿kWh)", TL_TOTAL_YI - 136000 * HOURS / 1e8)

show("整体单位投资 (万元/MW)", 418100 / (tl_kw / 1000))
show("一期单位投资 (万元/MW)", 315200 / 136)
show("整体减一期 投资 (亿元)", 41.81 - 31.52)
show("整体减一期 IT 功率 (MW)", tl_kw / 1000 - 136)
show("差额段单位投资 (万元/MW)", (418100 - 315200) / (tl_kw / 1000 - 136))

show("1# 每模块功率 (MW/模块)", 48 / 120)
show("2# 每模块功率 (MW/模块)", 48 / 96)
show("1#＋2# 合计 (MW)", 48 + 48)
show("与机柜算术 202.92768MW 缺口 (MW)", tl_kw / 1000 - 96)

show("结论章 100% 绿电对应电量 (亿kWh)", TL_TOTAL_YI * 1.0)
show("背景章 20% 绿电对应电量 (亿kWh)", TL_TOTAL_YI * 0.2)
show("两者相差 (亿kWh)", TL_TOTAL_YI * 0.8)
show("公司介绍 20000×6kW (kW)", 20000 * 6)
show("与项目明细之差 (kW)", tl_kw - 20000 * 6)
show("单位工业增加值能耗 4.569 ÷ 2.42 (倍)", 4.569 / 2.42)

# ---------------------------------------------------------------- 并场
rule("四、两项目并场核对")
show("腾龙整体＋电信里水 (MW)", tl_kw / 1000 + TEL_IT_KW / 1000)
show("腾龙一期＋电信里水 (MW)", 136 + TEL_IT_KW / 1000)
show("两项目当量值合计 (tce)", TL_EQ + tel_eq + DIESEL_TCE)
show("两项目等价值合计 (tce)", TL_PR + tel_pr + DIESEL_TCE)
print()
print("说明：以上均为对报送稿披露数字的四则运算复核，未替报送稿补齐任何未披露项。")
