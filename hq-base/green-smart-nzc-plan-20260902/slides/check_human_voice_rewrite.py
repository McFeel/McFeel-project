#!/usr/bin/env python3
"""校验主链人话重写文案包：页序、页 id、固定字段、禁用词、口播时长。

用法：python3 check_human_voice_rewrite.py [markdown 路径]
"""

import re
import sys
from pathlib import Path

EXPECTED_PAGES = [
    "cover",
    "strategic-alignment-chain",
    "constraints",
    "target-portrait",
    "three-sites",
    "two-consultancies",
    "research-standards",
    "six-dimension-map",
    "research-to-scheme",
    "green-line",
    "mpark-three-ends",
    "digital-base",
    "green-smart-building",
    "human-day",
    "six-proofs",
    "indicator-tree",
    "four-scenes",
    "four-steps",
    "replicable-pack",
    "three-decisions",
]

REQUIRED_FIELDS = ["**标题：**", "**导语：**", "**正文：**", "**页脚一句：**"]

BANNED_WORDS = [
    "本页",
    "上屏",
    "不上",
    "待核",
    "不构成",
    "原独立页",
    "无假数",
    "Researchy",
    "文秘",
    "制作说明",
    "本页边界",
    "交核",
]

# 口播速率：中文念稿汇报约每秒 4.5 字；目标区间 30—60 秒，即每页 135—270 字。
CHARS_PER_SECOND = 4.5
MIN_SECONDS = 30.0
MAX_SECONDS = 60.0

PAGE_HEADING = re.compile(r"^## (\d{2}) · ([a-z0-9-]+)\s*$")
CJK = re.compile(r"[\u3400-\u9fff\u3000-\u303f\uff00-\uffef]")


def split_pages(text):
    pages, current = [], None
    for line in text.splitlines():
        m = PAGE_HEADING.match(line)
        if m:
            current = {"num": m.group(1), "slug": m.group(2), "lines": []}
            pages.append(current)
        elif current is not None:
            current["lines"].append(line)
    return pages


def spoken_chars(page):
    body = "\n".join(page["lines"])
    body = re.sub(r"\*\*|^[-|]\s*|`", "", body, flags=re.MULTILINE)
    return len(CJK.findall(body))


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name(
        "human-voice-rewrite-mainchain-20260906.md"
    )
    text = path.read_text(encoding="utf-8")
    pages = split_pages(text)
    failures = []

    print(f"校验文件：{path}")
    print(f"页数：{len(pages)}（期望 {len(EXPECTED_PAGES)}）\n")

    if len(pages) != len(EXPECTED_PAGES):
        failures.append(f"页数不符：{len(pages)} != {len(EXPECTED_PAGES)}")

    print("序号  slide-id                    字段  秒数   判定")
    print("-" * 62)
    for idx, expected in enumerate(EXPECTED_PAGES, start=1):
        if idx > len(pages):
            failures.append(f"{idx:02d} {expected} 缺页")
            continue
        page = pages[idx - 1]
        ok_order = page["num"] == f"{idx:02d}" and page["slug"] == expected
        if not ok_order:
            failures.append(f"页序或 id 不符：期望 {idx:02d} · {expected}，实际 {page['num']} · {page['slug']}")

        body = "\n".join(page["lines"])
        missing = [f for f in REQUIRED_FIELDS if f not in body]
        if missing:
            failures.append(f"{page['num']} · {page['slug']} 缺字段 {missing}")

        seconds = spoken_chars(page) / CHARS_PER_SECOND
        in_range = MIN_SECONDS <= seconds <= MAX_SECONDS
        if not in_range:
            failures.append(f"{page['num']} · {page['slug']} 口播 {seconds:.0f} 秒，超出 30—60 秒")

        verdict = "通过" if (ok_order and not missing and in_range) else "不通过"
        print(
            f"{page['num']}    {page['slug']:<26}  {4 - len(missing)}/4   {seconds:>4.0f}   {verdict}"
        )

    print("\n禁用词核查：")
    for word in BANNED_WORDS:
        hits = []
        for lineno, line in enumerate(text.splitlines(), start=1):
            if word in line:
                hits.append(lineno)
        status = "无" if not hits else f"命中 {hits}"
        print(f"  {word:<12} {status}")
        if hits:
            failures.append(f"禁用词「{word}」出现在第 {hits} 行")

    print("\n叙事顺序核查：")
    slugs = [p["slug"] for p in pages]
    order_checks = [
        ("三主线六维在调研之后", slugs.index("six-dimension-map") > slugs.index("two-consultancies")),
        ("标准归纳在框架之前", slugs.index("research-standards") < slugs.index("six-dimension-map")),
        ("闭环两页相邻", slugs.index("indicator-tree") - slugs.index("six-proofs") == 1),
        ("增益在闭环之后", slugs.index("four-scenes") > slugs.index("indicator-tree")),
        ("可复制在决策之前", slugs.index("replicable-pack") < slugs.index("three-decisions")),
    ]
    for name, ok in order_checks:
        print(f"  {name}：{'通过' if ok else '不通过'}")
        if not ok:
            failures.append(f"叙事顺序不符：{name}")

    print()
    if failures:
        print(f"校验不通过，共 {len(failures)} 项：")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("校验全部通过：20 页页序与 id 一一对应，字段齐全，禁用词为零，每页口播 30—60 秒。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
