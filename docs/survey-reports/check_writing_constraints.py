#!/usr/bin/env python3
"""稿件红线自查。

对本目录下的调研报告成稿做机械校验，覆盖五类约束：
术语白名单、既成事实表述的否定语境、编造要素、半角标点、关键口径的限定语。

用法：python3 docs/survey-reports/check_writing_constraints.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

DOC_DIR = Path(__file__).resolve().parent

# 只允许「零碳」单用，以及「零碳机房」「零碳工厂」两个复合词。
ALLOWED_ZEROCARBON_TERMS = ("零碳机房", "零碳工厂")
BANNED_TERMS = ("零碳区域",)

# 这些词只允许出现在否定语境中，用于声明「不是已定事实」。
FAIT_ACCOMPLI = ("已立项", "已落地", "已签约", "已申报", "已批复", "已中标")
NEGATION_MARKERS = ("不", "未", "没有", "无", "非", "禁")

# 「全国首个」必须与限定语同句出现，避免被读成既成事实。
SCOPED_CLAIM = "全国首个"
SCOPE_MARKERS = ("争取", "会内", "不得", "未见", "一类表述")

FABRICATION_PATTERNS = {
    "文号或标准编号": r"〔\d{4}〕|\d{4}〕\d+号|GB ?/ ?T ?\d|GB ?\d{4,}|DL ?/ ?T|T ?/ ?CEC",
    "百分比": r"\d+(?:\.\d+)?[%％]",
    "量值单位": (
        r"\d+(?:\.\d+)?(?:万元|亿元|万千瓦|兆瓦|MW|kW|kWh|万度|平方米|㎡|"
        r"吨|万吨|台|个月|个季度)"
    ),
    "未见指标": r"\bPUE\b|\bCUE\b|\bWUE\b",
}

HALFWIDTH_PUNCT = re.compile(r"[,;:!?()]")
SENTENCE_SPLIT = re.compile(r"[。；！？\n]")


def body_lines(text: str):
    """产出正文行，跳过 Markdown 结构行，并剥离行内代码与链接目标。"""
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#") or set(line) <= {"-"}:
            continue
        if line.startswith("|"):  # 表格行含大量 Markdown 分隔符
            continue
        stripped = re.sub(r"`[^`]*`", "", line)
        stripped = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", stripped)
        stripped = stripped.replace("**", "")
        yield lineno, stripped


def sentences_with(text: str, needle: str):
    for chunk in SENTENCE_SPLIT.split(text):
        if needle in chunk:
            yield chunk.strip()


def main() -> int:
    docs = sorted(p for p in DOC_DIR.glob("*.md"))
    if not docs:
        print("未找到待检查的 Markdown 稿件。")
        return 1

    failures: list[str] = []

    def check(title: str, problems: list[str]) -> None:
        print(f"\n=== {title} ===")
        if not problems:
            print("PASS")
            return
        for item in problems:
            print(f"FAIL  {item}")
        failures.extend(problems)

    # 一、禁用术语
    problems = []
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        for term in BANNED_TERMS:
            if term in text:
                problems.append(f"{doc.name} 出现禁用术语「{term}」")
    check("禁用术语", problems)

    # 二、术语白名单：先移除允许的复合词，再看是否残留「零碳＋汉字」的自造搭配。
    problems = []
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        masked = text
        for term in ALLOWED_ZEROCARBON_TERMS:
            masked = masked.replace(term, "○")
        # 文件名与链接中的「零碳机房」已被掩去，此处只剩自造搭配。
        for match in re.finditer(r"零碳[\u4e00-\u9fff]+", masked):
            problems.append(f"{doc.name} 出现白名单外搭配「{match.group()}」")
    check("术语白名单（零碳／零碳机房／零碳工厂）", problems)

    # 三、既成事实表述必须处于否定语境
    problems = []
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        for term in FAIT_ACCOMPLI:
            for sentence in sentences_with(text, term):
                if not any(mark in sentence for mark in NEGATION_MARKERS):
                    problems.append(
                        f"{doc.name}「{term}」出现在非否定语境：{sentence}"
                    )
    check("既成事实表述限于否定语境", problems)

    # 四、关键口径的限定语
    problems = []
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        for sentence in sentences_with(text, SCOPED_CLAIM):
            if not any(mark in sentence for mark in SCOPE_MARKERS):
                problems.append(
                    f"{doc.name}「{SCOPED_CLAIM}」缺少限定语：{sentence}"
                )
    check("「全国首个」须带争取方向的限定语", problems)

    # 五、编造要素
    problems = []
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        for name, pattern in FABRICATION_PATTERNS.items():
            for match in re.finditer(pattern, text):
                problems.append(f"{doc.name} 疑似{name}：「{match.group()}」")
    check("编造要素（文号、百分比、量值、未见指标）", problems)

    # 六、半角标点
    problems = []
    for doc in docs:
        for lineno, line in body_lines(doc.read_text(encoding="utf-8")):
            if HALFWIDTH_PUNCT.search(line):
                problems.append(f"{doc.name} 第 {lineno} 行含半角标点：{line}")
    check("正文全角标点", problems)

    print("\n=== 结果 ===")
    if failures:
        print(f"共 {len(failures)} 项未通过，需修改稿件。")
        return 1
    print("全部检查项通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
