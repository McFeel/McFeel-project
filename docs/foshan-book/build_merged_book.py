#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_merged_book.py —— 新产品发布系列融合进佛山书稿并套用产品报告版式。

用法：
    python3 build_merged_book.py 源书稿.docx --output 融合后书稿.docx
    python3 build_merged_book.py 源书稿.docx --output 融合后书稿.docx --annex 第三篇附-新产品发布融合.md
    python3 build_merged_book.py 源书稿.docx --dry-run        # 仅打印将替换的块，不写文件

行为：
    1. 只读打开源书稿 docx（命令行第一个参数）；
    2. 定位"第三篇附／南网能源公司产品介绍板块／新产品发布系列"薄占位块
       （自块标题起，至下一个同级或更高级标题、或"第×篇／附录×"止）；
    3. 以 annex markdown（默认取本脚本同目录《第三篇附-新产品发布融合.md》）
       的全文替换该薄块；
    4. 按产品报告版式统一全书样式：A4 页面；正文宋体 12pt；
       一级标题黑体 18pt、二级黑体 14pt、三级黑体 12pt；图注楷体 10.5pt
       （规定范围 9—11pt 内取五号）；封面题字楷体 12pt、主标题黑体 24pt
       （规定范围 22—26pt 内取值）、副标题微软雅黑 13pt；
    5. 写入 --output 指定的新文件。

安全保证：
    * 绝不修改或覆盖输入文件；运行前后校验源文件 SHA-256 一致；
    * --output 与输入路径相同时拒绝执行；
    * --output 已存在时拒绝覆盖，除非显式传入 --force；
    * 仅依赖 python-docx 与 Python 标准库。
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

# ---------------------------------------------------------------- 版式常量

PAGE_W_CM, PAGE_H_CM = 21.0, 29.7          # A4
BODY_FONT, BODY_SIZE_PT = "宋体", 12
H1_FONT, H1_SIZE_PT = "黑体", 18
H2_FONT, H2_SIZE_PT = "黑体", 14
H3_FONT, H3_SIZE_PT = "黑体", 12
CAPTION_FONT, CAPTION_SIZE_PT = "楷体", 10.5   # 规定 9—11pt，取五号
KICKER_FONT, KICKER_SIZE_PT = "楷体", 12
COVER_TITLE_FONT, COVER_TITLE_SIZE_PT = "黑体", 24   # 规定 22—26pt
COVER_SUB_FONT, COVER_SUB_SIZE_PT = "微软雅黑", 13

CAPTION_STYLE_NAME = "图注"
KICKER_STYLE_NAME = "封面题字"

# ------------------------------------------------------- 占位块定位特征

ANNEX_START_RES = [
    re.compile(r"第三篇附.*产品介绍"),
    re.compile(r"产品介绍板块"),
    re.compile(r"新产品发布系列"),
]
BLOCK_END_RE = re.compile(r"^(附录\s*[A-DＡ-Ｄ]|第[一二三四五六七八九十百零]+[篇部])")
CAPTION_LINE_RE = re.compile(r"^[图表][　 \t]*[0-9０-９一二三四五六七八九十]+")
TOC_STYLE_RE = re.compile(r"^(TOC|Contents|目录)\s*\d*$", re.IGNORECASE)


def log(msg):
    print(f"【build_merged_book】{msg}")


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def heading_level(paragraph):
    """返回段落的标题级别（Title 视为 0）；非标题段落返回 None。"""
    name = paragraph.style.name or ""
    if name == "Title":
        return 0
    m = re.match(r"^Heading (\d+)$", name)
    if m:
        return int(m.group(1))
    return None


def is_toc_paragraph(p):
    """目录条目段落（Word 自动目录样式 TOC 1—9／目录 1—9）不参与占位块定位。"""
    return bool(TOC_STYLE_RE.match((p.style.name or "").strip()))


def find_annex_block(doc):
    """定位薄占位块，返回 (start_idx, end_idx)，end_idx 为块后第一段（可为 len）。

    两遍查找：先在标题样式段落中找（正式书稿的板块标题一般为标题样式），
    找不到再退而在非目录段落中找，避免误命中卷首目录中的同名条目。
    """
    paras = doc.paragraphs
    start = None
    for want_heading in (True, False):
        for i, p in enumerate(paras):
            if is_toc_paragraph(p):
                continue
            text = p.text.strip()
            if not text:
                continue
            if want_heading and heading_level(p) is None:
                continue
            if any(rx.search(text) for rx in ANNEX_START_RES):
                start = i
                break
        if start is not None:
            break
    if start is None:
        return None
    start_level = heading_level(paras[start])
    end = len(paras)
    for j in range(start + 1, len(paras)):
        p = paras[j]
        text = p.text.strip()
        level = heading_level(p)
        if level is not None and (start_level is None or level <= start_level):
            end = j
            break
        if BLOCK_END_RE.match(text):
            end = j
            break
    return start, end


# ------------------------------------------------------- 样式工具

def ensure_paragraph_style(doc, name, outline_level=None):
    """取得段落样式，不存在则新建；新建标题样式时补 outlineLvl 以保留大纲级别。"""
    try:
        return doc.styles[name]
    except KeyError:
        style = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = doc.styles["Normal"]
        if outline_level is not None:
            ppr = style.element.get_or_add_pPr()
            ol = ppr.find(qn("w:outlineLvl"))
            if ol is None:
                ol = OxmlElement("w:outlineLvl")
                ppr.append(ol)
            ol.set(qn("w:val"), str(outline_level))
        return style


def set_style_font(style, ascii_font, ea_font, size_pt, bold=None, black=False):
    style.font.name = ascii_font
    style.font.size = Pt(size_pt)
    if bold is not None:
        style.font.bold = bold
    if black:
        style.font.color.rgb = RGBColor(0, 0, 0)
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:ascii"), ascii_font)
    rfonts.set(qn("w:hAnsi"), ascii_font)
    rfonts.set(qn("w:eastAsia"), ea_font)


def setup_page_and_styles(doc):
    for section in doc.sections:
        section.page_width = Cm(PAGE_W_CM)
        section.page_height = Cm(PAGE_H_CM)

    set_style_font(doc.styles["Normal"], BODY_FONT, BODY_FONT, BODY_SIZE_PT)
    set_style_font(ensure_paragraph_style(doc, "Heading 1", outline_level=0), H1_FONT, H1_FONT, H1_SIZE_PT, black=True)
    set_style_font(ensure_paragraph_style(doc, "Heading 2", outline_level=1), H2_FONT, H2_FONT, H2_SIZE_PT, black=True)
    set_style_font(ensure_paragraph_style(doc, "Heading 3", outline_level=2), H3_FONT, H3_FONT, H3_SIZE_PT, black=True)
    set_style_font(ensure_paragraph_style(doc, CAPTION_STYLE_NAME), CAPTION_FONT, CAPTION_FONT, CAPTION_SIZE_PT)
    set_style_font(ensure_paragraph_style(doc, KICKER_STYLE_NAME), KICKER_FONT, KICKER_FONT, KICKER_SIZE_PT)
    set_style_font(ensure_paragraph_style(doc, "List Bullet"), BODY_FONT, BODY_FONT, BODY_SIZE_PT)

    # 封面：仅当书稿使用 Word 内置 Title/Subtitle 样式时套用，否则跳过不改动
    try:
        set_style_font(doc.styles["Title"], COVER_TITLE_FONT, COVER_TITLE_FONT, COVER_TITLE_SIZE_PT, black=True)
        log("已套用封面主标题样式：黑体 24pt（规定范围 22—26pt）")
    except KeyError:
        log("未检测到 Title 样式，跳过封面主标题样式")
    try:
        set_style_font(doc.styles["Subtitle"], COVER_SUB_FONT, COVER_SUB_FONT, COVER_SUB_SIZE_PT)
        log("已套用封面副标题样式：微软雅黑 13pt")
    except KeyError:
        log("未检测到 Subtitle 样式，跳过封面副标题样式")

    # 封面题字（kicker）：Title 段之前紧邻的非空短段落
    paras = doc.paragraphs
    title_idx = next((i for i, p in enumerate(paras) if (p.style.name or "") == "Title"), None)
    if title_idx is not None:
        for k in range(title_idx - 1, -1, -1):
            text = paras[k].text.strip()
            if not text:
                continue
            if len(text) <= 30:
                paras[k].style = doc.styles[KICKER_STYLE_NAME]
                log(f"已套用封面题字样式：楷体 12pt → 「{text}」")
            break


def restyle_captions(doc):
    """将全书中"图　×／表　×"题注段落统一为图注样式（楷体 10.5pt）。"""
    caption_style = doc.styles[CAPTION_STYLE_NAME]
    count = 0
    for p in doc.paragraphs:
        if (p.style.name or "") == CAPTION_STYLE_NAME:
            continue
        if CAPTION_LINE_RE.match(p.text.strip()):
            p.style = caption_style
            count += 1
    log(f"图注样式套用完成，共处理 {count} 个既有题注段落")


# ------------------------------------------------------- annex 解析

def parse_annex_markdown(md_text):
    """把 annex markdown 解析为 (kind, text) 序列。

    kind ∈ {h1, h2, h3, caption, bullet, body}；去除 ** 与 ` 标记。
    """
    blocks = []
    for raw in md_text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if line.startswith("### "):
            kind, text = "h3", line[4:]
        elif line.startswith("## "):
            kind, text = "h2", line[3:]
        elif line.startswith("# "):
            kind, text = "h1", line[2:]
        elif line.startswith("> "):
            kind, text = "body", line[2:]
        elif re.match(r"^[-*]\s+", line):
            kind, text = "bullet", re.sub(r"^[-*]\s+", "", line)
        elif CAPTION_LINE_RE.match(line.strip()):
            kind, text = "caption", line.strip()
        else:
            kind, text = "body", line
        text = text.replace("**", "").replace("`", "").strip()
        if text:
            blocks.append((kind, text))
    return blocks


KIND_TO_STYLE = {
    "h1": "Heading 1",
    "h2": "Heading 2",
    "h3": "Heading 3",
    "caption": CAPTION_STYLE_NAME,
    "bullet": "List Bullet",
    "body": "Normal",
}


def replace_block(doc, start, end, blocks):
    paras = doc.paragraphs
    anchor = paras[end] if end < len(paras) else None
    for p in paras[start:end]:
        p._element.getparent().remove(p._element)
    for kind, text in blocks:
        style_name = KIND_TO_STYLE.get(kind, "Normal")
        if anchor is not None:
            new_p = anchor.insert_paragraph_before(text, style=style_name)
        else:
            new_p = doc.add_paragraph(text)
            new_p.style = doc.styles[style_name]
    return len(blocks)


# ------------------------------------------------------- 主流程

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="将新产品发布系列融合进佛山书稿并套用产品报告版式（绝不覆盖输入文件）"
    )
    parser.add_argument("source", help="源书稿 docx 路径（只读，绝不修改）")
    parser.add_argument("--output", help="融合后新文件路径（必需，除非 --dry-run）")
    parser.add_argument(
        "--annex",
        default=str(Path(__file__).resolve().parent / "第三篇附-新产品发布融合.md"),
        help="annex markdown 路径（默认取本脚本同目录的融合稿）",
    )
    parser.add_argument("--dry-run", action="store_true", help="仅打印将替换的块，不写文件")
    parser.add_argument("--force", action="store_true", help="允许覆盖已存在的输出文件")
    args = parser.parse_args(argv)

    src = Path(args.source).resolve()
    if not src.is_file():
        log(f"错误：源文件不存在：{src}")
        return 2

    annex_path = Path(args.annex).resolve()
    if not annex_path.is_file():
        log(f"错误：annex 文件不存在：{annex_path}")
        return 2

    out = None
    if not args.dry_run:
        if not args.output:
            log("错误：缺少 --output（或使用 --dry-run）")
            return 2
        out = Path(args.output).resolve()
        if out == src:
            log("错误：输出路径与输入相同，已拒绝执行（绝不覆盖原件）")
            return 2
        if out.exists() and not args.force:
            log(f"错误：输出文件已存在：{out}（如需覆盖请显式加 --force）")
            return 2

    src_hash_before = sha256_of(src)
    doc = Document(str(src))

    found = find_annex_block(doc)
    if found is None:
        log("错误：未找到'第三篇附／产品介绍板块／新产品发布系列'占位块。已检索特征：")
        for rx in ANNEX_START_RES:
            log(f"    - {rx.pattern}")
        return 3
    start, end = found
    paras = doc.paragraphs
    log(f"定位到占位块：第 {start + 1} 段至第 {end} 段（共 {end - start} 段）")
    log(f"块首：「{paras[start].text.strip()[:60]}」")
    if end < len(paras):
        log(f"块后首段（保留）：「{paras[end].text.strip()[:60]}」")
    else:
        log("块后无内容（占位块位于文档末尾）")

    if args.dry_run:
        log("dry-run，将替换的块内容如下：")
        for p in paras[start:end]:
            print(f"    {p.text}")
        log("dry-run 结束，未写出任何文件")
        return 0

    blocks = parse_annex_markdown(annex_path.read_text(encoding="utf-8"))
    log(f"annex 解析完成：{len(blocks)} 个段落（来源：{annex_path.name}）")

    setup_page_and_styles(doc)
    log("页面与样式设置完成：A4；正文宋体 12pt；标题黑体 18/14/12pt")

    inserted = replace_block(doc, start, end, blocks)
    log(f"替换完成：删除原薄块 {end - start} 段，插入 annex {inserted} 段")

    restyle_captions(doc)

    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))

    src_hash_after = sha256_of(src)
    if src_hash_after != src_hash_before:
        log("严重错误：源文件校验值发生变化，已中止")
        return 4
    log(f"源文件校验未变（SHA-256 一致）：{src.name}")
    log(f"已写出新文件：{out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
