#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""落版校验 · 领导汇报 HTML

钉死四条口径，改完文案或补完图跑一遍，退出码 0 才算过：

  A 页面上每一段可见文字，要么逐字来自 #67/#68/#69 三包 md，要么属于落版构件白名单
  B 绿色／高效两页对照表的表脚必须是原句「内部测算，待基线书面核验」
  C PUE、501 万千瓦时、4171 吨、新能源占比这些数字只能待在对照表里、且带「参照」角标，
    全稿不得出现「已实现／已达到」这类承诺腔
  D 图内角标百分比（节能率 60%、40%+）不得进正文，只能出现在那句免责里

另外核页序、标题、导语、正文点、页脚是否与三包 md 逐字一致，以及图位是否登记进清单。

用法：
    python3 check_deck.py                          # md 默认找 ../slides/
    python3 check_deck.py --slides /path/to/slides # 指定三包 md 所在目录

三包 md 分别来自 PR #67 / #68 / #69，合并后就在 ../slides/ 下。
找不到 md 时只跑 B/C/D 与图位登记，A 与逐字比对会跳过并提示。
"""
import io
import os
import re
import sys
import html as htmlmod

HERE = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.join(HERE, 'leader-deck-20260906_by小七.html')
MANIFEST = os.path.join(HERE, 'images', 'IMAGE-MANIFEST.md')

MD_FILES = {
    'main': 'human-voice-rewrite-mainchain-20260906.md',
    'green': 'human-voice-green-efficient-2pages-20260906.md',
    'human': 'human-voice-human-line-3pages-20260906.md',
}

ORDER = ['cover', 'strategic-alignment-chain', 'constraints', 'target-portrait', 'three-sites',
         'two-consultancies', 'research-standards', 'six-dimension-map', 'research-to-scheme',
         'green-attr', 'efficient-attr', 'mpark-three-ends', 'digital-base', 'green-smart-building',
         'human-inclusive', 'human-health', 'human-culture', 'six-proofs', 'indicator-tree',
         'four-scenes', 'four-steps', 'replicable-pack', 'three-decisions']

# 主链原 green-line / human-day 已被 #69 / #68 拆页替换，不得并存
DROPPED = {'green-line', 'human-day'}

# 群里锁定的口径，不来自 md，单独登记
LOCKED_TITLES = {'strategic-alignment-chain': '总部基地建设本质上是一项战略能力建设'}

TABLE_FOOT = '内部测算，待基线书面核验'
TABLE_FOOT_PAGES = ['green-attr', 'efficient-attr']
GUARDED_NUMS = ['1.66', '1.4', '2.3%', '3.2%', '501', '4171']
COMMIT_WORDS = r'已实现|已达到|已达成|已建成|已经实现|已经达到|已经达成|实现了|达到了|达标了|建成了|已完成|已经完成'
BADGE_PCT = r'节能率\s*60%|40%\+'

PUNCT = set('、，。：；！？（）()「」『』《》——…·,.;:!?\'"“”‘’-—－/|＋+%※→←　')


def bare(s):
    return ''.join(c for c in (s or '') if c not in PUNCT and not c.isspace())


def strip_tags(h):
    h = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', h, flags=re.S)
    return htmlmod.unescape(re.sub(r'<[^>]+>', ' ', h))


# ---- 落版构件白名单：版面零件，加一条要过一次脑子 ----
CHROME = {bare(x) for x in [
    '南方电网总部基地 · 领导汇报', '战略 · 约束 · 目标', '调研', '框架 · 方案',
    '绿色主线', '智慧主线', '人文主线', '闭环 · 指标 · 增益', '推进 · 复制 · 决策', '封面',
    '建设世界一流智慧零碳园区', '战略对齐', '四道约束', '总体目标', '三个现场',
    '两次专题交流', '三把尺子', '三条主线 · 六项属性', '调研 → 方案', '属性一 · 绿色',
    '属性二 · 高效', '智慧主线（一）', '智慧主线（二）', '智慧主线（三）',
    '属性三 · 普惠', '属性四 · 健康', '属性五 · 人文', '互证闭环', '指标结构',
    '建成之后', '推进节奏', '带得走的东西', '请本次明确',
    '导语', '汇报对象', '汇报路线', '版本',
    '现场 01', '现场 02', '现场 03', '尺子 01', '尺子 02', '尺子 03',
    '主线 01', '主线 02', '主线 03', '端 01', '端 02', '端 03',
    '类别 01', '类别 02', '类别 03', '类别 04', '类别 05',
    'STEP 01', 'STEP 02', 'STEP 03', 'STEP 04',
    '第一步', '第二步', '第三步', '第四步', '一', '二', '三',
    '对企业', '对员工',
    '来源', '吸收什么', '进入方案哪里', '参照项', '现状参照', '可提升方向',
    '参照', TABLE_FOOT,
    '内部讨论稿 · 2026.09', '小七落版 · 文案 文秘·Opus', '← → 翻页 · ESC 总览',
    '← → 翻页', 'ESC 总览', '页面总览 · 23 页', 'ESC 返回', 'IMG · 待补', '—',
]}

CAPTIONS = {bare(x) for x in [
    'Fig-1 · 园区系统结构（复用仓库 figures/fig-1.png）',
    '办公楼群区、能源中心区、数据机房区与电网之间的供冷、余热、光伏、柔性资源关系；园中园试点区先行验证。',
    'Fig-2 · 统一数字底座平台架构（复用仓库 figures/fig-2.png）',
    '配图角标（节能率 60%、40%+）是素材自带示意，不是本方案口径；照明数字以正文与对照表为准。',
]}

FILE_RE = re.compile(r'^(green|efficient|human)/[a-z0-9-]+\.png$')
CHROME_RE = re.compile(r'^[A-Za-z][A-Za-z ]*·\s*\d{2}\s*/\s*23$')
COVER_RE = re.compile(r'^小七落版 · 文案 文秘·OPUS · \d{2} / 23$')


def parse_md(path):
    txt = io.open(path, encoding='utf-8').read()
    out = {}
    for b in re.split(r'^## ', txt, flags=re.M)[1:]:
        head = b.split('\n', 1)[0].strip()
        m = re.match(r'^\d+\s*·\s*(\S+)', head)
        if not m:
            continue

        def field(name, body=b):
            mm = re.search(r'\*\*' + name + r'：\*\*\s*(.+?)\s*(?=\n\n|\n\*\*|\Z)', body, re.S)
            return mm.group(1).strip() if mm else None

        main = b.split('**配图提示：**')[0]
        out[m.group(1)] = {
            'title': field('标题'), 'lead': field('导语'), 'foot': field('页脚一句'),
            'bullets': [re.sub(r'\*\*(.+?)\*\*', r'\1', x) for x in re.findall(r'^- (.+)$', main, flags=re.M)],
            'art': field('配图提示'),
        }
    return out


def main():
    slides_dir = os.path.join(HERE, '..', 'slides')
    if '--slides' in sys.argv:
        slides_dir = sys.argv[sys.argv.index('--slides') + 1]

    deck = io.open(DECK, encoding='utf-8').read()
    manifest = io.open(MANIFEST, encoding='utf-8').read() if os.path.exists(MANIFEST) else ''
    sections = re.findall(r'<section class="slide[^"]*" data-id="([^"]+)"[^>]*>(.*?)</section>', deck, re.S)
    body_html = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', deck, flags=re.S)
    visible = strip_tags(deck)
    fails = []

    md = {}
    have_md = True
    for key, name in MD_FILES.items():
        p = os.path.join(slides_dir, name)
        if not os.path.exists(p):
            have_md = False
            continue
        md.update(parse_md(p))

    print('=' * 68)
    print('落版校验 · 领导汇报 HTML')
    print('=' * 68)

    # ---------- 页序 ----------
    got = [s for s, _ in sections]
    print(f'\n页数：{len(got)} / 期望 {len(ORDER)}')
    if got != ORDER:
        fails.append('页序不符：' + ' → '.join(got))
        print('页序：FAIL')
    else:
        print('页序：与锁定页序逐页一致 ok')
    for sid in DROPPED:
        if f'data-id="{sid}"' in deck:
            fails.append(f'被拆页替换的 {sid} 仍在 HTML 里')

    # ---------- 逐字比对 ----------
    if not have_md:
        print(f'\n三包 md 未找到（找的是 {os.path.normpath(slides_dir)}），逐字比对与反向覆盖跳过。')
        print('三包 md 来自 PR #67 / #68 / #69，合并后重跑，或用 --slides 指定目录。')
    else:
        print('\n逐字比对（标题 / 导语 / 正文点 / 页脚 对三包 md）：')
        for n, (sid, frag) in enumerate(sections, 1):
            src = md.get(sid)
            if not src:
                fails.append(f'{n:02d} {sid}：md 里找不到对应页')
                print(f'  {n:02d} {sid:<26} FAIL 无对应 md 页')
                continue
            flags = []
            want_title = LOCKED_TITLES.get(sid, src['title'])
            hm = re.search(r'<h1 class="hero">(.*?)</h1>|<h2 class="t[^"]*"[^>]*>(.*?)</h2>', frag, re.S)
            got_title = strip_tags(hm.group(1) or hm.group(2)) if hm else ''
            if bare(got_title) != bare(want_title):
                flags.append(f'标题：md《{want_title}》 html《{got_title.strip()}》')
            fm = re.search(r'<div class="nb">(.*?)</div>', frag, re.S)
            got_foot = strip_tags(fm.group(1)) if fm else ''
            if bare(got_foot) != bare(src['foot']):
                flags.append(f'页脚：md《{src["foot"]}》 html《{got_foot.strip()}》')
            lm = re.search(r'<p class="lead"[^>]*>(.*?)</p>', frag, re.S)
            got_lead = strip_tags(lm.group(1)) if lm else strip_tags(frag)
            if bare(src['lead']) not in bare(got_lead):
                flags.append(f'导语：md《{src["lead"]}》')
            page_text = bare(strip_tags(frag))
            miss = [b for b in src['bullets'] if bare(b) and bare(b) not in page_text]
            if miss:
                flags.append('正文缺条：' + ' ／ '.join(m[:32] for m in miss))
            print(f'  {n:02d} {sid:<26} {"ok" if not flags else "FAIL"}')
            for f in flags:
                print('     - ' + f)
                fails.append(f'{n:02d} {sid}: {f}')

        # ---------- A · 反向覆盖 ----------
        corpus = ''
        for name in MD_FILES.values():
            t = io.open(os.path.join(slides_dir, name), encoding='utf-8').read()
            corpus += bare(re.sub(r'\*\*(.+?)\*\*', r'\1', t))
        locked = {bare(v) for v in LOCKED_TITLES.values()}
        tally = {'md': 0, 'chrome': 0, 'locked': 0, 'caption': 0, 'file': 0}
        unknown = []
        for n, (sid, frag) in enumerate(sections, 1):
            for seg in [x.strip() for x in re.sub(r'<[^>]+>', '\n', frag).split('\n')]:
                seg = htmlmod.unescape(seg).strip()
                b = bare(seg)
                if not b:
                    continue
                if FILE_RE.match(seg):
                    tally['file'] += 1
                elif b in CHROME or CHROME_RE.match(seg) or COVER_RE.match(seg):
                    tally['chrome'] += 1
                elif b in locked:
                    tally['locked'] += 1
                elif b in CAPTIONS:
                    tally['caption'] += 1
                elif b in corpus:
                    tally['md'] += 1
                else:
                    unknown.append((n, sid, seg))
        print('\nA · 反向覆盖：页面上每一段可见文字的出处')
        print(f'    逐字来自三包 md        {tally["md"]} 段')
        print(f'    落版版面构件（白名单）  {tally["chrome"]} 段')
        print(f'    群内锁定口径（02 标题） {tally["locked"]} 段')
        print(f'    插图 / 图位说明        {tally["caption"]} 段')
        print(f'    图位占位文件名          {tally["file"]} 段')
        print(f'    出处不明                {len(unknown)} 段')
        for n, sid, seg in unknown:
            print(f'      !! {n:02d} {sid}: {seg[:88]}')
            fails.append(f'{n:02d} {sid} 出处不明：{seg[:60]}')

        missing_art = [sid for sid, v in md.items()
                       if v.get('art') and not v['art'].lstrip().startswith('-')
                       and bare(v['art']) not in bare(manifest)]
        print(f'    三包配图提示已收进清单  {"ok" if not missing_art else "缺 " + ", ".join(missing_art)}')
        if missing_art:
            fails.append('IMAGE-MANIFEST.md 缺配图提示：' + ', '.join(missing_art))

    # ---------- B · 表脚原句 ----------
    foots = re.findall(r'<div class="tb-foot">([^<]*)</div>', deck)
    foot_pages = [sid for sid, frag in sections if 'tb-foot' in frag]
    ok_foot = foots == [TABLE_FOOT] * 2 and foot_pages == TABLE_FOOT_PAGES
    print(f'\nB · 表脚原句「{TABLE_FOOT}」')
    print(f'    {"ok（green-attr / efficient-attr 各一处，原句一字不差）" if ok_foot else "FAIL " + str(foots) + " " + str(foot_pages)}')
    if not ok_foot:
        fails.append(f'表脚原句不符：{foots} {foot_pages}')

    # ---------- C · 敏感数字与承诺腔 ----------
    print('\nC · 敏感数字与承诺腔')
    hits = re.findall(COMMIT_WORDS, visible)
    print(f'    承诺腔用词（已实现 / 已达到 …）  {"命中 " + str(hits) if hits else "0"}')
    if hits:
        fails.append(f'承诺腔用词命中：{hits}')
    rows = re.findall(r'<tr>(?!\s*<th)(.*?)</tr>', body_html, re.S)
    outside_txt = strip_tags(re.sub(r'<table.*?</table>', '', body_html, flags=re.S))
    bad = []
    for num in GUARDED_NUMS:
        if num in outside_txt:
            bad.append(f'{num} 出现在对照表之外')
        for r in rows:
            cell = re.search(r'<td class="[^"]*\bto\b[^"]*">(.*?)</td>', r, re.S)
            c = cell.group(1) if cell else ''
            if num in c and 'class="ref"' not in c:
                bad.append(f'{num} 所在的可提升方向单元格缺「参照」角标')
    print(f'    PUE / 501 万 / 4171 吨 / 占比   {"命中 " + str(bad) if bad else "0（全部在对照表内，且带参照角标）"}')
    if bad:
        fails.append(f'敏感数字口径不符：{bad}')

    # ---------- D · 图内角标百分比 ----------
    no_note = re.sub(r'<div class="slot-note">.*?</div>', '', body_html, flags=re.S)
    badge = re.findall(BADGE_PCT, strip_tags(no_note))
    print(f'\nD · 图内角标百分比进正文            {"命中 " + str(badge) if badge else "0（只出现在免责一句里）"}')
    if badge:
        fails.append(f'图内角标百分比进了正文：{badge}')

    # ---------- 图位登记 ----------
    slots = re.findall(r'<figure class="slot[^"]*"[^>]*>(.*?)</figure>', deck, re.S)
    print(f'\n图位：{len(slots)} 个')
    for sl in slots:
        src = re.search(r'<img src="images/([^"]+)"', sl)
        lbl = re.search(r'<span class="f">([^<]+)</span>', sl)
        if not src or not lbl:
            fails.append('图位缺 img 或占位文件名')
            continue
        if src.group(1) != lbl.group(1):
            fails.append(f'图位 src 与占位框文件名不一致：{src.group(1)} vs {lbl.group(1)}')
        if src.group(1) not in manifest:
            fails.append(f'图位 {src.group(1)} 未登记进 IMAGE-MANIFEST.md')
    print(f'    src 与占位文件名一致、且全部登记进清单  {"ok" if not [f for f in fails if "图位" in f] else "FAIL"}')

    # ---------- 其他制作口吻 ----------
    print('\n其他红线')
    for name, pat in [('PUE 1.4 称行业优秀', r'1\.4[^。\n]{0,12}行业优秀'),
                      ('910 / 1082 / 650', r'\b(910|1082|650)\b'),
                      ('制作口吻 Researchy', r'Researchy'),
                      ('制作口吻 本页边界', r'本页边界'),
                      ('制作口吻 不上本页', r'不上本页'),
                      ('制作口吻 【待核】', r'【待核】'),
                      ('落版说明串页', r'落版说明|统一口径（')]:
        h = re.findall(pat, visible, re.I)
        print(f'    {name:<22} {"命中 " + str(h) if h else "0"}')
        if h:
            fails.append(f'{name} 命中：{h}')

    print('\n' + '=' * 68)
    if fails:
        print(f'不通过：{len(fails)} 项')
        for f in fails:
            print('  - ' + f)
        return 1
    print('全部通过')
    if have_md:
        print('  页面文字只来自 #67/#68/#69 与落版构件（02 页标题为群内锁定口径）')
    print('  表脚原句在位；PUE / 501 万千瓦时 / 4171 吨等未写成已实现；角标百分比未进正文')
    if not have_md:
        print('  注意：三包 md 不在位，逐字比对与反向覆盖本次没跑，只过了 B/C/D 与图位登记')
    return 0


if __name__ == '__main__':
    sys.exit(main())
