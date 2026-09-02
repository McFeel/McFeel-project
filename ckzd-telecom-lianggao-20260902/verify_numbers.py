#!/usr/bin/env python3
"""复核两高专册已核数字，并检查意见稿禁用措辞。"""

from pathlib import Path
import sys
import zipfile

BASE = Path(__file__).resolve().parent
MD = BASE / "01-telecom-lishui-lianggao-opinion.md"
DOCX = BASE / "01-telecom-lishui-lianggao-opinion.docx"
README = BASE / "README.md"

errors = []


def near(actual, expected, tol, label):
    if abs(actual - expected) > tol:
        errors.append(f"{label}: {actual} != {expected} (tol {tol})")
    else:
        print(f"OK  {label}: {actual}")


# IT cabinets and power
it_kw = 100 * 328 + 24 * 82 + 15 * 82
near(it_kw, 35998, 0, "IT kW 100×328+24×82+15×82")
near(328 + 82 + 82, 492, 0, "cabinet count")
near(it_kw / 492, 73.166666, 1e-4, "avg kW/cabinet")

# IT energy
it_100 = 100 * 328 * 8760 / 10000  # 万 kWh
near(it_100, 28732.80, 1e-9, "100kW row 万kWh")
it_24 = 24 * 82 * 8760 / 10000
it_15 = 15 * 82 * 8760 / 10000
it_total = it_100 + it_24 + it_15
near(it_total, 31534.248, 1e-9, "IT total 万kWh")

elec = 37818.35
aux = elec - it_total
near(aux, 6284.102, 1e-9, "aux 万kWh")
pue = elec / it_total
near(pue, 1.199, 5e-4, "PUE elec/IT")
near(elec / 10000, 3.781835, 1e-12, "亿 kWh")

# tce
eq_power = elec * 1.229
val_power = elec * 2.8534
near(eq_power, 46478.76, 0.01, "power tce 当量")
near(val_power, 107910.89, 0.02, "power tce 等价")

diesel_t = 68.64
diesel_kwh = 26 * 2200 * 6
near(diesel_kwh, 343200, 0, "diesel test kWh")
diesel_from_rate = diesel_kwh * 0.20 / 1000
near(diesel_from_rate, diesel_t, 1e-9, "diesel t at 0.20 kg/kWh")
diesel_tce = 100.02
implied = diesel_tce / diesel_t
near(implied, 1.4571, 5e-4, "implied diesel tce/t")

near(eq_power + diesel_tce, 46578.78, 0.02, "total 当量 (rounded)")
# 稿内合计 46578.77 由未圆整中间值得到
near(elec * 1.229 + diesel_t * implied, 46578.77, 0.02, "total 当量 unrounded-ish")
near(val_power + diesel_tce, 108010.91, 0.02, "total 等价 (rounded)")
near(elec * 2.8534 + diesel_tce, 108010.90, 0.02, "total 等价 稿内")

green = elec * 0.80
near(green, 30254.68, 1e-9, "80% of annual kWh")

avg_kw = elec * 10000 / 8760
near(avg_kw, 43172, 1.0, "annual average kW")
near(avg_kw / 100000 * 100, 43.17, 0.02, "implied transformer load %")
near(100000 * 0.4095, 40950, 0, "40.95% of 100000 kVA")

inv_per_mw = 94638 / 36
near(inv_per_mw, 2628.8333, 1e-3, "万元/MW")

# text locks
text = MD.read_text(encoding="utf-8")
readme = README.read_text(encoding="utf-8")
forbidden = ["原则同意", "基本同意", "条件具备、补正后实施"]
# 意见中会点名禁止使用这些词，允许出现在“不得使用/不得表述为”句中
for phrase in forbidden:
    for fname, body in (("md", text), ("readme", readme)):
        for i, line in enumerate(body.splitlines(), 1):
            if phrase in line and ("不得" not in line) and ("无“原则同意”" not in line) and ("无\"原则同意\"" not in line):
                errors.append(f"{fname}:{i} bare forbidden phrase {phrase}: {line}")

required = [
    "不具备出具肯定性两高审查意见的条件",
    "37818.35",
    "46578.77",
    "108010.90",
    "1.199",
    "绿证",
    "其他商服用地",
    "韶关",
    "36MW",
]
for token in required:
    if token not in text:
        errors.append(f"md missing required token: {token}")

# old folders untouched marker: this script only reads new folder
if "原则同意" in text and text.count("不得") == 0:
    errors.append("原则同意 present without 不得")

# docx
if not DOCX.exists():
    errors.append("docx missing")
else:
    if not zipfile.is_zipfile(DOCX):
        errors.append("docx is not a zip/OOXML file")
    else:
        with zipfile.ZipFile(DOCX) as zf:
            names = zf.namelist()
            if "word/document.xml" not in names:
                errors.append("docx missing word/document.xml")
            xml = zf.read("word/document.xml").decode("utf-8")
            for token in ("不具备出具肯定性", "36MW", "37818.35", "108010.90"):
                if token not in xml:
                    errors.append(f"docx xml missing {token}")
            if "原则同意" in xml and "不得" not in xml:
                errors.append("docx has 原则同意 without 不得")
        print(f"OK  docx zip+xml ({DOCX.stat().st_size} bytes)")

if errors:
    print("FAIL")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("ALL CHECKS PASSED")
