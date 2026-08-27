#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给《关于进一步深化广东电网办公节能业务合作的工作汇报》加 Word 批注。

设计原则：只加批注、不改正文。已审的 20 条问题逐条写成一条 Word 批注，
钉在正文对应句上（author=文秘）。批注正文统一写“严重程度＋问题＋改法”，
与已审结论一致；不另出清单体审查意见。

实现方式：直接操作 docx 包（zip）内的部件，用 lxml/python-docx 的 oxml 助手拼装：
  1. 在 word/document.xml 里，把每条问题对应的锚定文字用
     w:commentRangeStart / w:commentRangeEnd 包起来，并追加一个带
     w:commentReference 的引用 run；
  2. 新增 word/comments.xml，写入 20 条批注（w:comment，author=文秘）；
  3. 在 [Content_Types].xml 里登记 comments 部件的内容类型；
  4. 在 word/_rels/document.xml.rels 里加 comments 关系。
正文文字本身一个字都不改，只是把已有的 run 按锚点边界切开以便精确钉句。

用法：
    python3 docs/reviews/add_gd_report_comments.py 原稿.docx 批注稿.docx

原稿云端可能没有，可先用配套的 test_add_gd_report_comments.py 造夹具测 comments 部件。
"""

from __future__ import annotations

import copy
import sys
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from lxml import etree

# 复用 python-docx 的命名空间与 oxml 助手，符合 python-docx/lxml 技术栈。
from docx.oxml import OxmlElement
from docx.oxml.ns import nsmap, qn

W = nsmap["w"]
CT = "[Content_Types].xml"
DOCUMENT = "word/document.xml"
DOCUMENT_RELS = "word/_rels/document.xml.rels"
COMMENTS = "word/comments.xml"

CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
COMMENTS_CT = (
    "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml"
)
COMMENTS_REL = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments"
)

AUTHOR = "文秘"
INITIALS = "WM"

# 特殊锚点：钉在正文首个非空段落（用于“开篇无主送”这类针对缺失/开篇的问题）。
FIRST_PARAGRAPH = "\x00FIRST_PARAGRAPH\x00"


@dataclass
class CommentSpec:
    """一条已审问题：钉句锚点 + 批注正文。"""

    cid: int
    severity: str  # 高 / 中 / 低
    # 候选锚点，按顺序取第一个在正文中命中的；FIRST_PARAGRAPH 表示钉首段。
    anchors: list[str]
    body: str
    first_only: bool = True  # 只钉首次命中处
    matched_anchor: str = field(default="", init=False)


def _sev(tag: str, problem: str, fix: str) -> str:
    return f"【{tag}】{problem}改法：{fix}"


# 已审 20 条。body = 严重程度 + 问题 + 改法，与已审结论一致。
COMMENT_SPECS: list[CommentSpec] = [
    CommentSpec(
        1, "高", ["由南网能源公司承接"],
        _sev("高",
             "把相关业务直接表述为“由南网能源公司承接”，属于未经采购程序即预设承接主体与结果，与招投标、框架采购合规相冲突。",
             "删去指定承接主体的定论表述，改为“依程序参与框架采购、争取承接”，承接结果以采购程序确定为准。"),
    ),
    CommentSpec(
        2, "高", ["严格按照贵司制度流程参与框架采购", "贵司"],
        _sev("高",
             "本件为对内工作汇报，却出现“贵司”这类对外敬语，主送对象与文种错位，且把参与主体表述含混。",
             "对内汇报不用“贵司”，明确主体为我方（南网能源公司），改为“严格按照广东电网相关制度流程参与框架采购”。"),
    ),
    CommentSpec(
        3, "高", ["特此汇报", "工作汇报"],
        _sev("高",
             "标题用“工作汇报”、结语“特此汇报”，但正文含“恳请”等请求上级批准的事项，文种与事由不符。",
             "凡需上级批准事项，改为“请示”（一文一事，标题“……的请示”，结语“妥否，请批示”）；若仅汇报则删去恳请类请求。"),
    ),
    CommentSpec(
        4, "高", ["恳请"],
        _sev("高",
             "汇报文种不应含“恳请……”的请求语气，与文种相矛盾（首处标注，全文同类照改）。",
             "改为陈述性表述；确需上级批准的，整件转为请示。"),
    ),
    CommentSpec(
        5, "高", [FIRST_PARAGRAPH],
        _sev("高",
             "开篇无主送机关，未写明呈报对象，公文要素不全。",
             "按行文关系补主送机关（抬头顶格），明确报送对象后再述事由。"),
    ),
    CommentSpec(
        6, "高", ["无缝续签"],
        _sev("高",
             "“无缝续签”属绝对化、不严谨表述，且续签须走采购程序，不能预设必然续签。",
             "删除“无缝”，据实改为“依程序做好到期后接续”，不承诺必然续签。"),
    ),
    CommentSpec(
        7, "高", ["清城供电局", "粤电大厦"],
        _sev("高",
             "单位、物业指称需核实与规范：如“清城供电局”是否应为“清远供电局清城分局/清城供电局”全称，“粤电大厦”是否为本项目相关物业、有无涉密或指称错误。",
             "逐一核实并使用规范全称，剔除无关或错误指称。"),
    ),
    CommentSpec(
        8, "高", ["2027-2028年度办公节能框架采购"],
        _sev("高",
             "开篇即直陈具体采购年度与事项而无背景铺垫，且采购名称须全文一致。",
             "开篇先交代背景与缘由，采购名称全文统一为“2027—2028年度办公节能框架采购”。"),
    ),
    CommentSpec(
        9, "中", ["2028年集中到期", "集中到期"],
        _sev("中",
             "“2028年集中到期”缺依据、易生歧义，未说明所指合同。",
             "列明到期合同的名称、数量与时间，避免笼统表述。"),
    ),
    CommentSpec(
        10, "中", ["无法续签"],
        _sev("中",
             "“无法续签”表述绝对且未说明原因。",
             "说明具体制约（合同期满须重新采购），改为“到期须按程序重新采购”。"),
    ),
    CommentSpec(
        11, "中", ["减少多供应商协调管理成本", "多供应商协调"],
        _sev("中",
             "“减少多供应商协调管理成本”论据含混，缺现状与数据支撑。",
             "补充多供应商现状与协调成本的具体说明或量化对比。"),
    ),
    CommentSpec(
        12, "中", ["严格落实"],
        _sev("中",
             "“严格落实”为口号式表述，缺可核指标。",
             "明确落实的具体制度、责任主体与时限。"),
    ),
    CommentSpec(
        13, "中", ["保障改造质量", "运维响应时效"],
        _sev("中",
             "“保障改造质量、运维响应时效”为承诺性表述，缺量化标准。",
             "给出质量验收标准与运维响应/到场时限等可核指标。"),
    ),
    CommentSpec(
        14, "中", ["大楼供冷系统", "供冷系统"],
        _sev("中",
             "“大楼供冷系统”指称不清，未界定楼宇与系统边界。",
             "写明具体楼宇名称与系统范围。"),
    ),
    CommentSpec(
        15, "中", ["基层单位"],
        _sev("中",
             "“基层单位”指代笼统。",
             "明确所指基层单位范围或予以列举。"),
    ),
    CommentSpec(
        16, "中", ["设备运维"],
        _sev("中",
             "“设备运维”范围不清，与前述业务边界存在重叠。",
             "界定设备运维的对象与内容边界。"),
    ),
    CommentSpec(
        17, "低", ["办公节能各细分业务"],
        _sev("低",
             "小标题“（一）办公节能各细分业务”表述冗余、不够规范。",
             "精简为规范小标题，如“（一）办公节能细分业务”。"),
    ),
    CommentSpec(
        18, "低", ["2027-2028办公节能框架采购体系", "办公节能框架采购体系"],
        _sev("低",
             "采购名称漏“年度”，与其他处口径不一致。",
             "补“年度”，全文统一为“2027—2028年度办公节能框架采购”。"),
    ),
    CommentSpec(
        19, "低", ["BOO"],
        _sev("低",
             "专有名词“BOO”首次出现未注全称。",
             "首次出现注明“BOO（建设—拥有—运营）”，后文再用简称。"),
    ),
    CommentSpec(
        20, "低", ["增量拓展空间较大", "首先衷心感谢"],
        _sev("低",
             "“增量拓展空间较大”表述空泛无支撑；如取开篇“首先衷心感谢”，则对内汇报致谢客套冗余。",
             "删空泛表述并据实说明潜力；对内汇报删去致谢客套。"),
    ),
]


# --------------------------- run 级文字处理 --------------------------- #

def _run_text(run: etree._Element) -> str:
    """一个 run 的文字＝其 w:t 子节点文字之和（忽略 tab/break 等特殊内容）。"""
    return "".join(t.text or "" for t in run.findall(qn("w:t")))


def _set_run_text(run: etree._Element, text: str) -> None:
    """把 run 的文字重置为单个 w:t（保留 space=preserve）。"""
    for t in run.findall(qn("w:t")):
        run.remove(t)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    rpr = run.find(qn("w:rPr"))
    if rpr is not None:
        rpr.addnext(t)
    else:
        run.insert(0, t)


def _split_run_at(paragraph: etree._Element, offset: int) -> None:
    """确保段落在字符 offset 处正好有一个 run 边界（必要时切开某个 run，保留其 rPr）。"""
    if offset <= 0:
        return
    pos = 0
    for run in list(paragraph.findall(qn("w:r"))):
        text = _run_text(run)
        length = len(text)
        if length == 0:
            continue
        if pos < offset < pos + length:
            rel = offset - pos
            right = copy.deepcopy(run)
            _set_run_text(run, text[:rel])
            _set_run_text(right, text[rel:])
            run.addnext(right)
            return
        pos += length


def _paragraph_text(paragraph: etree._Element) -> str:
    return "".join(_run_text(r) for r in paragraph.findall(qn("w:r")))


def _wrap_range(paragraph: etree._Element, start: int, end: int, cid: int) -> None:
    """在段落 [start, end) 字符区间外插入 commentRangeStart/End 及引用 run。"""
    _split_run_at(paragraph, end)
    _split_run_at(paragraph, start)

    first = last = None
    pos = 0
    for run in paragraph.findall(qn("w:r")):
        length = len(_run_text(run))
        if length == 0:
            continue
        if start <= pos < end:
            if first is None:
                first = run
            last = run
        pos += length
    if first is None or last is None:
        raise RuntimeError("锚点区间未匹配到任何 run，无法钉批注。")

    crs = OxmlElement("w:commentRangeStart")
    crs.set(qn("w:id"), str(cid))
    first.addprevious(crs)

    cre = OxmlElement("w:commentRangeEnd")
    cre.set(qn("w:id"), str(cid))
    last.addnext(cre)

    ref_run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    rstyle = OxmlElement("w:rStyle")
    rstyle.set(qn("w:val"), "CommentReference")
    rpr.append(rstyle)
    ref_run.append(rpr)
    ref = OxmlElement("w:commentReference")
    ref.set(qn("w:id"), str(cid))
    ref_run.append(ref)
    cre.addnext(ref_run)


def _anchor_paragraph(
    body: etree._Element, spec: CommentSpec
) -> tuple[etree._Element, int, int, str]:
    """在正文里为一条问题找到钉句位置，返回(段落, start, end, 命中锚点)。"""
    paragraphs = body.findall(qn("w:p"))

    for anchor in spec.anchors:
        if anchor == FIRST_PARAGRAPH:
            for para in paragraphs:
                text = _paragraph_text(para)
                if text.strip():
                    return para, 0, len(text), anchor
            continue
        for para in paragraphs:
            text = _paragraph_text(para)
            idx = text.find(anchor)
            if idx != -1:
                return para, idx, idx + len(anchor), anchor
    raise LookupError(
        f"第 {spec.cid} 条：正文中找不到锚点 {spec.anchors!r}，无法钉句。"
    )


# --------------------------- 部件拼装 --------------------------- #

def build_comments_part(specs: list[CommentSpec]) -> bytes:
    """生成 word/comments.xml。"""
    root = etree.Element(qn("w:comments"), nsmap={"w": W})
    date = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
    for spec in specs:
        comment = etree.SubElement(root, qn("w:comment"))
        comment.set(qn("w:id"), str(spec.cid))
        comment.set(qn("w:author"), AUTHOR)
        comment.set(qn("w:date"), date)
        comment.set(qn("w:initials"), INITIALS)

        para = etree.SubElement(comment, qn("w:p"))
        ppr = etree.SubElement(para, qn("w:pPr"))
        pstyle = etree.SubElement(ppr, qn("w:pStyle"))
        pstyle.set(qn("w:val"), "CommentText")

        ann_run = etree.SubElement(para, qn("w:r"))
        ann_rpr = etree.SubElement(ann_run, qn("w:rPr"))
        ann_style = etree.SubElement(ann_rpr, qn("w:rStyle"))
        ann_style.set(qn("w:val"), "CommentReference")
        etree.SubElement(ann_run, qn("w:annotationRef"))

        text_run = etree.SubElement(para, qn("w:r"))
        t = etree.SubElement(text_run, qn("w:t"))
        t.set(qn("xml:space"), "preserve")
        t.text = spec.body

    return etree.tostring(
        root, xml_declaration=True, encoding="UTF-8", standalone=True
    )


def _register_content_type(raw: bytes) -> bytes:
    root = etree.fromstring(raw)
    for override in root.findall(f"{{{CT_NS}}}Override"):
        if override.get("PartName") == "/word/comments.xml":
            return raw  # 已登记
    override = etree.SubElement(root, f"{{{CT_NS}}}Override")
    override.set("PartName", "/word/comments.xml")
    override.set("ContentType", COMMENTS_CT)
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def _register_relationship(raw: bytes) -> bytes:
    root = etree.fromstring(raw)
    for rel in root.findall(f"{{{REL_NS}}}Relationship"):
        if rel.get("Target") in ("comments.xml", "/word/comments.xml"):
            return raw  # 已登记
    used = {rel.get("Id") for rel in root.findall(f"{{{REL_NS}}}Relationship")}
    n = 1
    while f"rId{n}" in used:
        n += 1
    rel = etree.SubElement(root, f"{{{REL_NS}}}Relationship")
    rel.set("Id", f"rId{n}")
    rel.set("Type", COMMENTS_REL)
    rel.set("Target", "comments.xml")
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def add_comments(src: Path, dst: Path, specs: list[CommentSpec] | None = None) -> list[CommentSpec]:
    """读入原稿 docx，钉上 20 条批注，写出批注稿。返回带命中锚点的 specs。"""
    specs = specs if specs is not None else COMMENT_SPECS

    with zipfile.ZipFile(src) as zf:
        names = zf.namelist()
        parts = {name: zf.read(name) for name in names}

    if DOCUMENT not in parts:
        raise ValueError("这不是有效的 Word 文档：缺少 word/document.xml。")

    doc_root = etree.fromstring(parts[DOCUMENT])
    body = doc_root.find(qn("w:body"))
    if body is None:
        raise ValueError("word/document.xml 缺少 w:body。")

    for spec in specs:
        para, start, end, anchor = _anchor_paragraph(body, spec)
        _wrap_range(para, start, end, spec.cid)
        spec.matched_anchor = anchor

    parts[DOCUMENT] = etree.tostring(
        doc_root, xml_declaration=True, encoding="UTF-8", standalone=True
    )
    parts[COMMENTS] = build_comments_part(specs)
    parts[CT] = _register_content_type(parts[CT])
    if DOCUMENT_RELS in parts:
        parts[DOCUMENT_RELS] = _register_relationship(parts[DOCUMENT_RELS])
    else:
        parts[DOCUMENT_RELS] = _new_document_rels()

    ordered = list(names)
    if COMMENTS not in ordered:
        ordered.append(COMMENTS)
    if DOCUMENT_RELS not in ordered:
        ordered.append(DOCUMENT_RELS)

    dst.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in ordered:
            zf.writestr(name, parts[name])
    return specs


def _new_document_rels() -> bytes:
    root = etree.Element(f"{{{REL_NS}}}Relationships")
    rel = etree.SubElement(root, f"{{{REL_NS}}}Relationship")
    rel.set("Id", "rId1")
    rel.set("Type", COMMENTS_REL)
    rel.set("Target", "comments.xml")
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        print("参数错误。用法：python3 add_gd_report_comments.py 原稿.docx 批注稿.docx")
        return 2
    src, dst = Path(argv[1]), Path(argv[2])
    if not src.exists():
        print(f"原稿不存在：{src}")
        return 1
    specs = add_comments(src, dst)
    print(f"已写出批注稿：{dst}")
    for spec in specs:
        shown = "开篇首段" if spec.matched_anchor == FIRST_PARAGRAPH else spec.matched_anchor
        print(f"  [{spec.severity}] 第{spec.cid:>2}条 → 钉“{shown}”")
    print(f"共 {len(specs)} 条批注，author={AUTHOR}。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
