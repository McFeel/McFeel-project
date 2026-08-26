#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_annex_docx.py —— 把《第三篇附-新产品发布融合.md》生成出版版式的 Word 文件。

用法：
    python3 build_annex_docx.py --output 第三篇附-新产品发布融合.docx
    python3 build_annex_docx.py --annex 第三篇附-新产品发布融合.md --output out.docx [--force]

说明：
    * 版式与 build_merged_book.py 完全一致（A4；正文宋体 12pt；标题黑体
      18/14/12pt；图注楷体 10.5pt），样式引擎直接复用自该脚本；
    * 本板块为书稿第三篇附，不单设封面、不加宣传册元素；
    * 输出文件已存在时拒绝覆盖，除非显式 --force；
    * 仅依赖 python-docx 与 Python 标准库。
"""

import argparse
import sys
from pathlib import Path

from docx import Document

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_merged_book import (  # noqa: E402
    KIND_TO_STYLE,
    parse_annex_markdown,
    setup_page_and_styles,
)


def log(msg):
    print(f"【build_annex_docx】{msg}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="把第三篇附 annex markdown 生成出版版式的 Word 文件"
    )
    parser.add_argument(
        "--annex",
        default=str(Path(__file__).resolve().parent / "第三篇附-新产品发布融合.md"),
        help="annex markdown 路径（默认取本脚本同目录的融合稿）",
    )
    parser.add_argument("--output", required=True, help="输出 docx 路径")
    parser.add_argument("--force", action="store_true", help="允许覆盖已存在的输出文件")
    args = parser.parse_args(argv)

    annex_path = Path(args.annex).resolve()
    if not annex_path.is_file():
        log(f"错误：annex 文件不存在：{annex_path}")
        return 2
    out = Path(args.output).resolve()
    if out == annex_path:
        log("错误：输出路径与 annex 输入相同，已拒绝执行")
        return 2
    if out.exists() and not args.force:
        log(f"错误：输出文件已存在：{out}（如需覆盖请显式加 --force）")
        return 2

    blocks = parse_annex_markdown(annex_path.read_text(encoding="utf-8"))
    log(f"annex 解析完成：{len(blocks)} 个段落（来源：{annex_path.name}）")

    doc = Document()
    setup_page_and_styles(doc)
    log("页面与样式设置完成：A4；正文宋体 12pt；标题黑体 18/14/12pt；图注楷体 10.5pt")

    for kind, text in blocks:
        style_name = KIND_TO_STYLE.get(kind, "Normal")
        doc.add_paragraph(text, style=style_name)

    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    log(f"已写出新文件：{out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
