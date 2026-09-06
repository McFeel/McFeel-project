#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""落版校验：HTML 里的正文必须与文秘·Opus 三个定稿文案包逐句一致。

校验四件事：
  1. 页序与 slide-id —— 23 页，顺序锁死；
  2. 逐句比对 —— copy-source/ 三个 md 里的标题、导语、正文、页脚一句，
     每一句都必须能在 HTML 的可见文本里原样找到（落版只允许拆行，不允许改字）；
  3. Researchy 已定三处措辞 + 绿色/高效表脚，必须在场；
  4. 禁止项 —— 制作口吻词不得进入页面，参照量级数字必须带「参照」角标。

用法：python3 check_deck_copy.py
"""
from __future__ import annotations

import html as htmllib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECK = HERE / "leader-deck-20260906_by小七.html"
SRC = HERE / "copy-source"

# 页序锁：md 小节 slug -> 页面 slide-id。None = 该小节已被拆页文案包取代，不参与比对。
MAIN = "human-voice-rewrite-mainchain-20260906.md"
GREEN = "human-voice-green-efficient-2pages-20260906.md"
HUMAN = "human-voice-human-line-3pages-20260906.md"

SECTION_MAP = {
    MAIN: {
        "cover": "cover",
        "strategic-alignment-chain": "strategic-alignment-chain",
        "constraints": "constraints",
        "target-portrait": "target-portrait",
        "three-sites": "three-sites",
        "two-consultancies": "two-consultancies",
        "research-standards": "research-standards",
        "six-dimension-map": "six-dimension-map",
        "research-to-scheme": "research-to-scheme",
        "green-line": None,          # 由 #69 拆成 green-attr / efficient-attr
        "mpark-three-ends": "mpark-three-ends",
        "digital-base": "digital-base",
        "green-smart-building": "green-smart-building",
        "human-day": None,           # 由 #68 拆成 human-inclusive / health / culture
        "six-proofs": "six-proofs",
        "indicator-tree": "indicator-tree",
        "four-scenes": "four-scenes",
        "four-steps": "four-steps",
        "replicable-pack": "replicable-pack",
        "three-decisions": "three-decisions",
    },
    GREEN: {"green-attr": "green-attr", "efficient-attr": "efficient-attr"},
    HUMAN: {
        "human-inclusive": "human-inclusive",
        "human-health": "human-health",
        "human-culture": "human-culture",
    },
}

EXPECTED_ORDER = [
    "cover", "strategic-alignment-chain", "constraints", "target-portrait",
    "three-sites", "two-consultancies", "research-standards", "six-dimension-map",
    "research-to-scheme", "green-attr", "efficient-attr", "mpark-three-ends",
    "digital-base", "green-smart-building", "human-inclusive", "human-health",
    "human-culture", "six-proofs", "indicator-tree", "four-scenes", "four-steps",
    "replicable-pack", "three-decisions",
]

# 标题以用户锁定的 23 页页序为准，与 md 原标题不同的在此登记（措辞同样不可再改）。
# 这一条来自 PR #70 已认可的落版：02 页标题用「总部基地建设本质上是一项战略能力建设」。
TITLE_OVERRIDES = {
    "国家怎么要求，公司怎么走，园区怎么落": "总部基地建设本质上是一项战略能力建设",
}

# Researchy 已定措辞 + 口径底线，一个字都不能动
LOCKED = [
    "绿色低碳、健康人文、智慧运营协同运行",
    "博鳌零碳示范区",
    "存量改造合理量级",
    "内部测算，待基线书面核验",
]

# 制作口吻不得进入页面
FORBIDDEN = ["本页", "不上", "待核", "不构成"]

# 参照量级数字：出现即必须在其后 80 字内挂「参照」角标
NEEDS_REF_TAG = ["约 1.4", "约 3.2%", "约 4.5", "约 4.8", "约 128"]

errors: list[str] = []
checked = 0


def norm(s: str) -> str:
    """去掉换行/多余空白，统一为可比对的一行。"""
    return re.sub(r"\s+", "", s)


# ---------------------------------------------------------------- HTML 可见文本
raw = DECK.read_text(encoding="utf-8")

slide_ids = re.findall(r'data-slide-id="([^"]+)"', raw)
# section 上和 SPEAKER_NOTES 上都可能出现，只取 section 的
slide_ids = re.findall(r'<section\b[^>]*data-slide-id="([^"]+)"', raw)

body = raw
# 去掉 style / script / 注释 / alt 属性，只留页面上真正念得出来的字
body = re.sub(r"<style\b[^>]*>.*?</style>", " ", body, flags=re.S)
body = re.sub(r"<script\b[^>]*>.*?</script>", " ", body, flags=re.S)
body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
body = re.sub(r"<[^>]+>", "\n", body)
visible = norm(htmllib.unescape(body))


# ---------------------------------------------------------------- 1. 页序
if slide_ids != EXPECTED_ORDER:
    errors.append(
        "页序/slide-id 与锁定顺序不一致：\n  实际 %s\n  期望 %s" % (slide_ids, EXPECTED_ORDER)
    )


# ---------------------------------------------------------------- md 取句
LABEL_RE = re.compile(r"^([^：。，；]{2,12})：(.+)$")
ORDINAL_RE = re.compile(r"^([一二三四五六七八九十]+)、(.+)$")


def phrases_from_line(line: str) -> list[str]:
    """一条 md 行拆成需要逐句校验的片段。

    落版允许「拆」不允许「改」，所以下面这几种重排都视为等价：
      · `标签：正文`      → 小标题 + 段落两个节点
      · `一、决策名`      → 序号 + 标题两个节点
      · `第一步 基线诊断` → 步骤号 + 步骤名两个节点
      · 表格行            → 逐单元格
    """
    line = line.strip()
    line = re.sub(r"\*\*(.+?)\*\*", r"\1", line)          # 去粗体
    line = re.sub(r"^[-*]\s+", "", line)                   # 去列表符号
    line = line.rstrip("：")                                # 分组小标题的收尾冒号
    if not line:
        return []
    if line.startswith("|"):                               # 表格行
        cells = [c.strip() for c in line.strip("|").split("|")]
        return [c for c in cells if c and c != "—" and not set(c) <= set("- ")]

    m = ORDINAL_RE.match(line)
    if m:
        return [m.group(1)] + phrases_from_line(m.group(2))

    m = LABEL_RE.match(line)
    if m:
        return phrases_from_line(m.group(1)) + [m.group(2)]

    if " " in line and len(line) <= 24:                    # 「第一步 基线诊断」
        return [p for p in line.split() if p]
    return [line]


def parse_sections(path: Path) -> dict[str, list[str]]:
    """按 `## N · slug` 切小节，抽出标题 / 导语 / 正文 / 页脚一句。"""
    out: dict[str, list[str]] = {}
    slug = None
    field = None
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        h = re.match(r"^##\s+(?:\d+\s*[·.]\s*)?(.+?)\s*$", s)
        if h:
            slug = h.group(1).strip()
            field = None
            out.setdefault(slug, [])
            continue
        if slug is None:
            continue
        if re.match(r"^\*\*配图提示[:：]?\*\*", s) or s.startswith("配图提示"):
            field = "skip"
            continue
        for name in ("标题", "导语", "页脚一句"):
            m = re.match(r"^\*\*%s[:：]\*\*\s*(.*)$" % name, s)
            if m:
                field = name
                if m.group(1).strip():
                    out[slug].extend(phrases_from_line(m.group(1)))
                break
        else:
            if re.match(r"^\*\*正文[:：]\*\*", s):
                field = "正文"
                continue
            if field in ("正文",) and s and not s.startswith("**"):
                out[slug].extend(phrases_from_line(s))
            elif field in ("正文",) and s.startswith("**") and s.endswith("**"):
                out[slug].extend(phrases_from_line(s))
    return out


for fname, mapping in SECTION_MAP.items():
    parsed = parse_sections(SRC / fname)
    unknown = set(mapping) - set(parsed)
    if unknown:
        errors.append("%s 缺少小节：%s（文案包结构变了？）" % (fname, sorted(unknown)))
    for slug, slide_id in mapping.items():
        if slide_id is None or slug not in parsed:
            continue
        for phrase in parsed[slug]:
            phrase = TITLE_OVERRIDES.get(phrase, phrase)
            n = norm(phrase)
            if len(n) < 3:
                continue
            checked += 1
            if n in visible:
                continue
            # 顿号枚举允许拆成并列 chip：每一项都在场即算命中
            items = [p for p in norm(phrase).rstrip("。").split("、") if p]
            if len(items) >= 2 and all(i in visible for i in items):
                continue
            errors.append("[%s → %s] 定稿句未在页面中原样出现：%s" % (fname, slide_id, phrase))


# ---------------------------------------------------------------- 3. 锁定措辞
for phrase in LOCKED:
    checked += 1
    if norm(phrase) not in visible:
        errors.append("锁定措辞缺失：%s" % phrase)


# ---------------------------------------------------------------- 4. 禁止项
for bad in FORBIDDEN:
    if bad in visible:
        ctx = visible[max(0, visible.find(bad) - 24): visible.find(bad) + 24]
        errors.append("出现制作口吻/禁用词「%s」，上下文：…%s…" % (bad, ctx))

for num in NEEDS_REF_TAG:
    n = norm(num)
    idx = visible.find(n)
    if idx == -1:
        errors.append("参照量级数字缺失：%s" % num)
        continue
    while idx != -1:
        if "参照" not in visible[idx: idx + 80]:
            errors.append("参照量级数字「%s」附近没有「参照」角标/说明，可能被读成已实现承诺" % num)
            break
        idx = visible.find(n, idx + 1)


# ---------------------------------------------------------------- 结果
if errors:
    print("落版校验未通过：")
    for e in errors:
        print(" -", e)
    sys.exit(1)

print("落版校验通过：%d 页页序一致，%d 条定稿句/口径逐句命中。" % (len(slide_ids), checked))
