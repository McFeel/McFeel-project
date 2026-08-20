#!/usr/bin/env python3
"""稿件红线自查。

对本目录下的调研报告成稿做机械校验，覆盖六类约束：

1. “零碳区域”只允许出现在转述住建部认证体系之处，且不得用于指称本项目；
2. “全国首个”“国内首个”一类表述必须带出处或争取方向的限定语；
3. 清华大学一站尚未开展，不得写成已调研、已座谈、已形成结论；
4. 既成事实用语（已立项、已签约等）只允许出现在否定语境；
5. 含量化数据的段落必须同段标注出处；
6. 正文使用全角标点，并校验公文 Word 与 Markdown 正文同步。

用法：python3 docs/survey-reports/check_writing_constraints.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

DOC_DIR = Path(__file__).resolve().parent
REPORT = DOC_DIR / "2026-08-南网总部基地绿色近零碳智慧园区项目调研报告.md"
DOCX = DOC_DIR / "2026-08-南网总部基地绿色近零碳智慧园区项目调研报告.docx"

# “零碳区域”系建科院宣讲材料转述住建部体系时的原词，只能在有出处的语境下使用。
ZERO_CARBON_AREA = "零碳区域"
AREA_SOURCE_MARKERS = ("宣讲材料", "住建部", "建科院")
PROJECT_MARKERS = ("南网", "总部基地", "本项目")

# “首个”类表述必须说明是谁的口径。
FIRST_CLAIMS = ("全国首个", "国内首个")
FIRST_MARKERS = ("宣讲材料", "争取", "会内", "意向", "据")

# 清华一站尚未开展。
TSINGHUA = "清华"
TSINGHUA_FORBIDDEN = ("已调研", "已座谈", "已参观", "已形成结论", "已开展", "调研结论")

FAIT_ACCOMPLI = ("已立项", "已落地", "已签约", "已申报", "已批复", "已中标")
NEGATION_MARKERS = ("不", "未", "没有", "无", "非", "禁", "尚")

# 量化数据必须与出处同段出现。
QUANTITY_RE = re.compile(
    r"\d+(?:\.\d+)?(?:%|％|万平方米|平方米|万千瓦|兆瓦|千瓦|千瓦时|万度|度|吨|"
    r"万立方米|亩|万块|块|栋|次每小时)"
)
SOURCE_MARKERS = (
    "据",
    "宣讲材料",
    "新华网",
    "中国网",
    "新能源网",
    "报道",
    "纪要",
    "会上",
    "调研计划",
    "计算",
    "稿中未见",
    "标准",
    "台阶",
    "要求",
)

# 文号样式一律不得出现。GB 55015-2021 是宣讲材料给出的标准号，
# 仿宋_GB2312、楷体_GB2312 是公文体例的字体名，均属允许项。
ALLOWED_STANDARD_NUMBERS = ("GB 55015-2021", "仿宋_GB2312", "楷体_GB2312")
DOC_NUMBER_RE = re.compile(r"〔\d{4}〕|\d{4}〕\d+号|第?\d+号文|GB ?/ ?T ?\d|GB ?\d{4,}")

HALFWIDTH_PUNCT = re.compile(r"[,;:!?()]")
SENTENCE_SPLIT = re.compile(r"[。；！？\n]")
# 术语与英文缩写中的半角字符属正常排版，校验时先行剔除。
TECH_TOKENS = re.compile(
    r"GB 55015-2021|SEER|STP|V2G|AI|Wp|PUE|G\d+|5\.5至5\.6|check_writing_constraints\.py"
)


def sentences(text: str):
    for chunk in SENTENCE_SPLIT.split(text):
        chunk = chunk.strip()
        if chunk:
            yield chunk


def body_lines(text: str):
    """产出正文行，跳过 Markdown 结构行，并剥离行内代码与链接目标。"""
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith(("#", "<!--", "|")) or set(line) <= {"-"}:
            continue
        stripped = re.sub(r"`[^`]*`", "", line)
        stripped = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", stripped)
        yield lineno, stripped.replace("**", "")


def paragraphs(text: str):
    for lineno, line in body_lines(text):
        yield lineno, line


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

    texts = {doc: doc.read_text(encoding="utf-8") for doc in docs}

    # 一、“零碳区域”的使用语境。
    # 出处要求只针对正文；审查说明是对该词本身的说明文字，不适用此项。
    problems = []
    for sentence in sentences(texts[REPORT]):
        if ZERO_CARBON_AREA in sentence and not any(
            m in sentence for m in AREA_SOURCE_MARKERS
        ):
            problems.append(f"{REPORT.name}「零碳区域」缺出处：{sentence}")
    for doc, text in texts.items():
        for sentence in sentences(text):
            if (
                ZERO_CARBON_AREA in sentence
                and any(m in sentence for m in PROJECT_MARKERS)
                and not any(n in sentence for n in NEGATION_MARKERS)
            ):
                problems.append(f"{doc.name}「零碳区域」被用于本项目：{sentence}")
    check("「零碳区域」仅用于转述认证体系", problems)

    # 二、“首个”类表述的限定语
    problems = []
    for doc, text in texts.items():
        for sentence in sentences(text):
            for claim in FIRST_CLAIMS:
                if claim in sentence and not any(m in sentence for m in FIRST_MARKERS):
                    problems.append(f"{doc.name}「{claim}」缺限定语：{sentence}")
    check("「首个」类表述须带出处或争取方向", problems)

    # 三、清华一站尚未开展
    problems = []
    for doc, text in texts.items():
        for sentence in sentences(text):
            if TSINGHUA not in sentence:
                continue
            for word in TSINGHUA_FORBIDDEN:
                if word in sentence and not any(
                    n in sentence for n in NEGATION_MARKERS
                ):
                    problems.append(f"{doc.name}清华被写成「{word}」：{sentence}")
    check("清华大学一站不得写成已开展", problems)

    # 四、既成事实用语限于否定语境
    problems = []
    for doc, text in texts.items():
        for sentence in sentences(text):
            for term in FAIT_ACCOMPLI:
                if term in sentence and not any(
                    n in sentence for n in NEGATION_MARKERS
                ):
                    problems.append(f"{doc.name}「{term}」非否定语境：{sentence}")
    check("既成事实用语限于否定语境", problems)

    # 五、量化数据必须同段标注出处
    problems = []
    for doc, text in texts.items():
        for lineno, line in paragraphs(text):
            if QUANTITY_RE.search(line) and not any(m in line for m in SOURCE_MARKERS):
                problems.append(f"{doc.name} 第 {lineno} 行数据缺出处：{line[:70]}")
    check("量化数据同段标注出处", problems)

    # 六、文号样式
    problems = []
    for doc, text in texts.items():
        masked = text
        for allowed in ALLOWED_STANDARD_NUMBERS:
            masked = masked.replace(allowed, "○")
        for match in DOC_NUMBER_RE.finditer(masked):
            problems.append(f"{doc.name} 疑似文号：「{match.group()}」")
    check("未出现编造文号", problems)

    # 七、正文全角标点
    problems = []
    for doc, text in texts.items():
        for lineno, line in body_lines(text):
            if HALFWIDTH_PUNCT.search(TECH_TOKENS.sub("", line)):
                problems.append(f"{doc.name} 第 {lineno} 行含半角标点：{line[:70]}")
    check("正文全角标点", problems)

    # 八、公文 Word 与 Markdown 正文同步
    print("\n=== 公文 Word 与 Markdown 同步 ===")
    if not DOCX.exists():
        print("FAIL  未找到公文 Word，请先执行 build_docx.py")
        failures.append("缺少公文 Word")
    else:
        try:
            from docx import Document
        except ImportError:
            print("SKIP  未安装 python-docx，跳过同步校验")
        else:
            doc_text = "".join(
                p.text for p in Document(DOCX).paragraphs
            ) + "".join(
                c.text for t in Document(DOCX).tables for r in t.rows for c in r.cells
            )
            md_text = REPORT.read_text(encoding="utf-8")
            missing = [
                line
                for _, line in body_lines(md_text)
                if len(line) > 30 and line[:28] not in doc_text
            ]
            if missing:
                print(f"FAIL  Word 缺少 {len(missing)} 段正文，需重新生成")
                for line in missing[:3]:
                    print(f"      {line[:60]}")
                failures.append("Word 与 Markdown 不同步")
            else:
                print("PASS")

    print("\n=== 结果 ===")
    if failures:
        print(f"共 {len(failures)} 项未通过，需修改稿件。")
        return 1
    print("全部检查项通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
