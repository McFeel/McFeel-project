#!/usr/bin/env python3
"""核对 clean-white 单文件 HTML 幻灯与三个 Markdown 文案包是否逐句一致。

检查五件事：
  1. 页序与页 id 与锁定的 23 页一一对应；
  2. 每页的标题、导语、正文、页脚一句都能在对应 md 里找到出处；
  3. 绿色／高效两页的对照表数字全部挂了「参照」角标，且有表脚；
  4. 禁用词（奖项认证名、被点名不上版的数字、制作口吻）零命中；
  5. 单文件：除 Google Fonts 外没有任何外部 CSS/JS/图片依赖。

用法：python3 check_deck_against_copy.py [HTML 路径] [三个 md 所在目录]
"""

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_HTML = HERE / "leader-deck-20260906_by小七_ppt-animation-clean-white.html"
DEFAULT_MD_DIR = HERE.parent / "slides"

MAINCHAIN = "human-voice-rewrite-mainchain-20260906.md"
HUMAN_LINE = "human-voice-human-line-3pages-20260906.md"
GREEN_EFF = "human-voice-green-efficient-2pages-20260906.md"

# 锁定页序：main = 主链 md 的页 id，其余两包按 slide-id 供页
LOCKED_ORDER = [
    ("cover", MAINCHAIN, "cover"),
    ("strategic-alignment-chain", MAINCHAIN, "strategic-alignment-chain"),
    ("constraints", MAINCHAIN, "constraints"),
    ("target-portrait", MAINCHAIN, "target-portrait"),
    ("three-sites", MAINCHAIN, "three-sites"),
    ("two-consultancies", MAINCHAIN, "two-consultancies"),
    ("research-standards", MAINCHAIN, "research-standards"),
    ("six-dimension-map", MAINCHAIN, "six-dimension-map"),
    ("research-to-scheme", MAINCHAIN, "research-to-scheme"),
    ("green-attr", GREEN_EFF, "green-attr"),
    ("efficient-attr", GREEN_EFF, "efficient-attr"),
    ("mpark-three-ends", MAINCHAIN, "mpark-three-ends"),
    ("digital-base", MAINCHAIN, "digital-base"),
    ("green-smart-building", MAINCHAIN, "green-smart-building"),
    ("human-inclusive", HUMAN_LINE, "human-inclusive"),
    ("human-health", HUMAN_LINE, "human-health"),
    ("human-culture", HUMAN_LINE, "human-culture"),
    ("six-proofs", MAINCHAIN, "six-proofs"),
    ("indicator-tree", MAINCHAIN, "indicator-tree"),
    ("four-scenes", MAINCHAIN, "four-scenes"),
    ("four-steps", MAINCHAIN, "four-steps"),
    ("replicable-pack", MAINCHAIN, "replicable-pack"),
    ("three-decisions", MAINCHAIN, "three-decisions"),
]

# 用户点名锁定的标题（正文、导语、页脚仍逐字取自主链 md）
TITLE_OVERRIDES = {
    "strategic-alignment-chain": "总部基地建设本质上是一项战略能力建设",
}

# 用户点名要求的表脚，两张对照表都要有
TABLE_FOOTNOTE = "内部测算，待基线书面核验"

BANNED = [
    "LEED", "WELL", "BREEAM", "DGNB", "绿色建筑三星", "三星级标识",
    "近零碳示范", "示范项目奖", "获奖", "认证证书",
    "910", "1082", "650",
    "本页边界", "待核", "不构成", "Researchy", "制作说明", "上屏", "文秘",
]

STRIP = "：:，。、；！？（）()「」【】·—－ \t\r\n\u3000/｜|"
CLAUSE_SPLIT = re.compile(r"[，。；：、！？\n]")


def norm(s):
    return "".join(ch for ch in s if ch not in STRIP)


# --------------------------------------------------------------------------- md


def parse_md(path):
    """把一个文案包切成 {slide-id: {title, lead, body[], foot, table[]}}。"""
    text = path.read_text(encoding="utf-8")
    pages = {}
    chunks = re.split(r"^## +\S+ +· +([a-z0-9-]+)\s*$", text, flags=re.M)
    # chunks = [前言, id1, body1, id2, body2, ...]
    for i in range(1, len(chunks), 2):
        pid, body = chunks[i], chunks[i + 1]
        page = {"title": "", "lead": "", "body": [], "foot": "", "table": []}
        m = re.search(r"\*\*标题：\*\*\s*(.+)", body)
        if m:
            page["title"] = m.group(1).strip()
        m = re.search(r"\*\*导语：\*\*\s*(.+)", body)
        if m:
            page["lead"] = m.group(1).strip()
        m = re.search(r"\*\*页脚一句：\*\*\s*(.+)", body)
        if m:
            page["foot"] = m.group(1).strip()
        seg = body
        m = re.search(r"\*\*正文：\*\*(.*?)(?=\*\*页脚一句：\*\*)", body, flags=re.S)
        if m:
            seg = m.group(1)
        for line in seg.splitlines():
            line = line.strip()
            if line.startswith("- "):
                page["body"].append(line[2:].strip())
            elif line.startswith("|") and line.endswith("|"):
                cells = [c.strip() for c in line.strip("|").split("|")]
                if all(set(c) <= set("- ") for c in cells):
                    continue
                page["table"].append(cells)
            elif line.endswith("：") and 2 <= len(line) <= 8:
                page["body"].append(line)
        pages[pid] = page
    return pages


def parse_md_numbered(path):
    """人文三页 / 绿色高效两页用「## 1 · slide-id」编号，走同一套解析。"""
    return parse_md(path)


# ------------------------------------------------------------------------- html


class SlideParser(HTMLParser):
    """按 <section class="slide" data-id=...> 收集可见文本。"""

    SKIP = {"script", "style"}
    VOID = {"br", "hr", "img", "input", "meta", "link", "source", "use", "col", "area"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.slides = []          # [(data_id, data_name, text)]
        self.order = []
        self._depth = 0
        self._buf = []
        self._id = None
        self._name = None
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.SKIP:
            self._skip += 1
            return
        if tag == "section" and "slide" in a.get("class", ""):
            self._depth = 1
            self._buf = []
            self._id = a.get("data-id")
            self._name = a.get("data-name", "")
            self.order.append(self._id)
            return
        if tag in self.VOID:
            if tag == "br" and self._depth:
                self._buf.append("\n")
            return
        if self._depth:
            self._depth += 1

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self._skip = max(0, self._skip - 1)
            return
        if self._depth:
            self._depth -= 1
            if self._depth == 0:
                self.slides.append((self._id, self._name, "".join(self._buf)))
                self._id = None

    def handle_data(self, data):
        if self._skip or not self._depth:
            return
        self._buf.append(data)


# ------------------------------------------------------------------------ check


def contains(haystack, needle):
    """整句命中返回 'full'，分句全命中返回 'clause'，否则返回缺失的分句。"""
    if norm(needle) and norm(needle) in haystack:
        return "full", []
    missing = [
        c for c in (x.strip() for x in CLAUSE_SPLIT.split(needle))
        if len(norm(c)) >= 2 and norm(c) not in haystack
    ]
    return ("clause", []) if not missing else ("miss", missing)


def main():
    html_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_HTML
    md_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_MD_DIR

    raw = html_path.read_text(encoding="utf-8")
    packs = {
        MAINCHAIN: parse_md(md_dir / MAINCHAIN),
        HUMAN_LINE: parse_md_numbered(md_dir / HUMAN_LINE),
        GREEN_EFF: parse_md_numbered(md_dir / GREEN_EFF),
    }

    p = SlideParser()
    p.feed(raw)
    slides = {sid: (name, norm(txt)) for sid, name, txt in p.slides}

    errors, warnings, clause_hits, checked = [], [], 0, 0

    # 1 页序
    want = [x[0] for x in LOCKED_ORDER]
    if p.order != want:
        errors.append("页序不符：\n  期望 %s\n  实际 %s" % (want, p.order))

    # 2 逐句核对
    for idx, (sid, pack, mid) in enumerate(LOCKED_ORDER, start=1):
        if sid not in slides:
            errors.append("缺页：%s" % sid)
            continue
        name, text = slides[sid]
        page = packs[pack].get(mid)
        if page is None:
            errors.append("%s 在 %s 里找不到 md 页 %s" % (sid, pack, mid))
            continue

        fields = [("标题", TITLE_OVERRIDES.get(sid, page["title"])),
                  ("导语", page["lead"]),
                  ("页脚一句", page["foot"])]
        fields += [("正文", b) for b in page["body"]]
        for cells in page["table"]:
            fields += [("表格", c) for c in cells if c and c != "—"]

        for label, value in fields:
            if not value:
                continue
            checked += 1
            kind, missing = contains(text, value)
            if kind == "miss":
                errors.append("%02d %s · %s 未落版：%s\n      缺：%s"
                              % (idx, sid, label, value, "／".join(missing)))
            elif kind == "clause":
                clause_hits += 1

        # 锁定标题必须原样出现
        if sid in TITLE_OVERRIDES and norm(TITLE_OVERRIDES[sid]) not in text:
            errors.append("%02d %s 锁定标题缺失" % (idx, sid))

        if name and norm(name) not in text:
            warnings.append("%02d %s 的 data-name 与页面标题不一致" % (idx, sid))

    # 3 对照表：数字挂角标 + 表脚
    for sid in ("green-attr", "efficient-attr"):
        block = re.search(r'data-id="%s".*?(?=<section|<div id="ov")' % sid, raw, flags=re.S)
        body = block.group(0) if block else ""
        rows = re.findall(r'<span class="c(?:now|to)">(.*?)</span>\s*(?=<span|</div>)', body, flags=re.S)
        for cell in rows:
            plain = re.sub(r"<[^>]+>", "", cell).strip()
            if plain in ("—", ""):
                continue
            if 'class="rt"' not in cell:
                errors.append("%s 对照表数字未挂参照角标：%s" % (sid, plain))
        if TABLE_FOOTNOTE not in body:
            errors.append("%s 缺表脚「%s」" % (sid, TABLE_FOOTNOTE))

    # 4 禁用词
    flat = re.sub(r"<[^>]+>", " ", raw)
    for w in BANNED:
        if re.search(r"(?<![0-9])%s(?![0-9])" % re.escape(w), flat):
            errors.append("命中禁用词：%s" % w)

    # 5 单文件
    for m in re.findall(r'<(?:script|link|img)\b[^>]*>', raw):
        src = re.search(r'(?:src|href)="([^"]+)"', m)
        if not src:
            continue
        url = src.group(1)
        if url.startswith(("https://fonts.googleapis.com", "https://fonts.gstatic.com")):
            continue
        errors.append("存在外部依赖：%s" % url)

    # ------------------------------------------------------------------ report
    print("HTML  : %s" % html_path)
    print("文案包: %s" % md_dir)
    print("页数  : %d（锁定 %d）" % (len(p.order), len(LOCKED_ORDER)))
    print("核对  : %d 条文案片段，其中 %d 条为分句命中（落版时插入了角标或分栏）"
          % (checked, clause_hits))
    for w in warnings:
        print("  提示 %s" % w)
    if errors:
        print("\n不通过，%d 处：" % len(errors))
        for e in errors:
            print("  × %s" % e)
        return 1
    print("\n全部通过：页序锁定、逐句有出处、角标与表脚齐、禁用词零命中、无外部依赖。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
