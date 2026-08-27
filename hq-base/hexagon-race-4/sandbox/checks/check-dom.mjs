/* 沙盘页面结构与内容校验（jsdom，不启动任何浏览器）
   用法：npm i jsdom && node check-dom.mjs                                     */
import fs from 'node:fs';
import path from 'node:path';
import { JSDOM } from 'jsdom';

const DIR = path.resolve(import.meta.dirname, '..');
const html = fs.readFileSync(path.join(DIR, 'index.html'), 'utf8');
const data = fs.readFileSync(path.join(DIR, 'data.js'), 'utf8');
const app = fs.readFileSync(path.join(DIR, 'app.js'), 'utf8');

const dom = new JSDOM(html, { runScripts: 'outside-only', pretendToBeVisual: true });
const w = dom.window;
const d = w.document;

// 模拟脑图 CDN 不可达：验证回退到原文源码后页面仍完整
w.__mermaidFailed = true;

let fail = 0;
const ok = (cond, msg) => {
  console.log((cond ? '  PASS  ' : '  FAIL  ') + msg);
  if (!cond) fail++;
};
const section = (t) => console.log('\n== ' + t + ' ' + '='.repeat(Math.max(0, 60 - t.length)));
const tick = () => new Promise((r) => setTimeout(r, 0));

w.eval(data + '\n;\n' + app);

/* ---------------------------------------------------------------- */
section('第一页 · 沙盘骨架');
const panels = [...d.querySelectorAll('.edge-panel')];
ok(panels.length === 6, `六边面板数量 = ${panels.length}（应为 6）`);
const chips = [...d.querySelectorAll('.chip')];
ok(chips.length === 36, `模型字标数量 = ${chips.length}（6 边 × 6 模型 = 36）`);
ok([...d.querySelectorAll('.spoke')].length === 6, '中心到六边的连接线 = 6');
ok(d.querySelectorAll('#core .core-ring').length === 3, '中心核为三层同心环 = 3');

const names = panels.map((p) => p.querySelector('.edge-name').textContent);
ok(
  JSON.stringify(names) === JSON.stringify(['零碳', '绿色', '高效', '智慧', '人文（含健康）', '普惠']),
  '六边顺序与命名：' + names.join(' / ')
);

// 面板与中心核几何：不越界、互不重叠、不压中心核
const CORE_R = 152;
let geomOK = true;
const box = [];
panels.forEach((p) => {
  const cx = parseFloat(p.style.left);
  const cy = parseFloat(p.style.top);
  const l = cx - 170, r = cx + 170, t = cy - 108, b = cy + 108;
  box.push({ l, r, t, b });
  if (l < 0 || r > 1600 || t < 0 || b > 830) geomOK = false;
  const dx = Math.max(Math.abs(cx - 800) - 170, 0);
  const dy = Math.max(Math.abs(cy - 415) - 108, 0);
  if (Math.hypot(dx, dy) < CORE_R * 0.6) geomOK = false;
});
for (let i = 0; i < box.length; i++)
  for (let j = i + 1; j < box.length; j++) {
    const a = box[i], c = box[j];
    if (a.l < c.r && c.l < a.r && a.t < c.b && c.t < a.b) geomOK = false;
  }
ok(geomOK, '六面板均在 1600×830 画布内、互不重叠、不压中心核');

const coreText = d.querySelector('#core').textContent;
ok(
  ['六张网', '水网', '新型电网', '算力网', '新一代通信网', '城市地下管网', '物流网', '六网协同', '算电协同', '战略资产', '第二增长曲线'].every(
    (k) => coreText.includes(k)
  ),
  '中心核显示锁定的三层口径关键词（六张网 / 六网协同 / 算电协同 / 战略资产）'
);
ok(d.querySelector('#mantra').textContent.includes('国家建六张网，南网做协同'), '顶栏口头禅已就位：' + d.querySelector('#mantra').textContent);
ok(d.querySelector('#hexnote').textContent.includes('不与六边一对一拆分对应'), '六边与六张网不一对一的说明已就位');
ok(
  d.querySelectorAll('sup.pending').length > 0 && d.querySelector('sup.pending').getAttribute('title').length > 10,
  '「待核」角标带说明性 tooltip'
);

/* ---------------------------------------------------------------- */
section('第二页 · 核＋六边 × 六模型对照表');
const heads = [...d.querySelectorAll('#matrix-table thead th')];
ok(heads.length === 7, `表头列数 = ${heads.length}（行标 + 6 模型）`);
ok(
  heads.slice(1).map((h) => h.textContent.trim()).join(' | ') ===
    'GLM-5.2 | Gemini 3.1 | GPT-5.6 | Kimi K3 | Grok 4.6 | Opus 4.8',
  '列 = 六路模型：' + heads.slice(1).map((h) => h.textContent.trim()).join(' / ')
);
const rows = [...d.querySelectorAll('#matrix-table tbody tr')];
ok(rows.length === 7, `数据行数 = ${rows.length}（核 + 六边）`);
ok(rows[0].querySelector('th').textContent.startsWith('核'), '第一行为「核」');
let cellsOK = true, thinCells = 0, cellCount = 0;
rows.forEach((tr) => {
  const tds = [...tr.querySelectorAll('td')];
  if (tds.length !== 6) cellsOK = false;
  tds.forEach((td) => {
    cellCount++;
    const keys = [...td.querySelectorAll('.mx-key')].map((k) => k.textContent);
    const vals = [...td.querySelectorAll('.mx-val')].map((v) => v.textContent.trim());
    if (keys.join('/') !== '路径/厂商·园区') cellsOK = false;
    if (vals.length !== 2 || vals.some((v) => v.length < 15)) cellsOK = false;
    if (td.textContent.length < 60) thinCells++;
  });
});
ok(cellsOK && cellCount === 42, `${cellCount} 个格子均含「路径」与「厂商·园区」两栏且内容完整`);
ok(thinCells === 0, `无过短格子（<60 字）：${thinCells} 个`);

/* ---------------------------------------------------------------- */
section('弹层 · 36 个「模型 × 边」详情');
const overlay = d.querySelector('#overlay');
let modalFail = 0, srcFail = 0, minBlock = 1e9, minBlockWhere = '';
let minEdge = 1e9, minEdgeWhere = '', blockCounts = new Set();
const labelSets = {};
for (const chip of chips) {
  chip.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  await tick(); // 等 mermaid 的异步回退分支落地
  if (overlay.hasAttribute('hidden')) { modalFail++; continue; }
  const blocks = [...d.querySelectorAll('#modal-body .blk')];
  blockCounts.add(blocks.length);
  const title = d.querySelector('#modal-title').textContent;
  const model = title.split('　·　')[0];
  labelSets[model] = labelSets[model] || new Set();
  let edgeLen = 0;
  blocks.forEach((b) => {
    const label = b.querySelector('.blk-label').textContent;
    const text = b.querySelector('.blk-text').textContent;
    labelSets[model].add(label);
    edgeLen += text.length;
    if (text.length < minBlock) { minBlock = text.length; minBlockWhere = title + ' / ' + label; }
  });
  if (edgeLen < minEdge) { minEdge = edgeLen; minEdgeWhere = title; }
  const src = d.querySelector('#modal-body .mermaid-src');
  if (!src || !src.textContent.startsWith('mindmap')) srcFail++;
  if (!d.querySelector('#modal-body .srcline').textContent.includes('origin/cursor/')) srcFail++;
  d.querySelector('#modal-close').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
}
ok(modalFail === 0, `36 个「模型 × 边」弹层全部打开成功（异常 ${modalFail} 处）`);
ok(srcFail === 0, `脑图 CDN 不可用时全部回退为原文 mermaid 源码，且均带原文出处（异常 ${srcFail} 处）`);
ok([...blockCounts].join(',') === '4', `每个弹层均为 4 段（是什么/为什么/怎么做/一揽子 等价分段）：${[...blockCounts].join(',')}`);
ok(minEdge >= 200, `单边详情最短 ${minEdge} 字（未压成一句话），最短处：${minEdgeWhere}`);
ok(minBlock >= 20, `最短段落 ${minBlock} 字，位于：${minBlockWhere}`);
// 只有 GPT-5.6 与 Grok 4.6 两路原文自带来源清单，弹层里应当以折叠块呈现
const srcPacks = {};
for (const chip of chips.slice(0, 6)) {
  chip.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  await tick();
  const model = d.querySelector('#modal-title').textContent.split('　·　')[0];
  srcPacks[model] = d.querySelectorAll('#modal-body .srcpack .srcs li').length;
  d.querySelector('#modal-close').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
}
ok(
  srcPacks['GPT-5.6'] === 9 && srcPacks['Grok 4.6'] === 14 && srcPacks['Kimi K3'] === 0,
  `自带来源清单的两路已折叠呈现：GPT-5.6 ${srcPacks['GPT-5.6']} 条、Grok 4.6 ${srcPacks['Grok 4.6']} 条；其余四路无此块`
);

console.log('         各路分段标签：');
Object.keys(labelSets).forEach((k) => console.log('           ' + k + '：' + [...labelSets[k]].join(' / ')));

/* ---------------------------------------------------------------- */
section('弹层 · 中心核');
d.querySelector('#core').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
ok(!overlay.hasAttribute('hidden'), '点击中心核可打开弹层');
const tiers = [...d.querySelectorAll('#modal-body .core-tier')];
ok(tiers.length === 3, `三层口径卡片 = ${tiers.length}`);
ok(
  tiers[0].textContent.includes('物流网') && tiers[1].textContent.includes('算电协同') && tiers[2].textContent.includes('名片和验证场'),
  '三层内容依次为：国家六张网 / 南网六网协同 / 南网自身战略资产'
);
ok(tiers[2].textContent.includes('能源公司只起草方案') && tiers[2].textContent.includes('再其他央国企'), '第三层含「能源公司只起草方案」与复制次序');
ok([...d.querySelectorAll('#modal-body .take')].length === 6, `各模型对核的提法 = ${d.querySelectorAll('#modal-body .take').length} 条`);
ok(d.querySelector('#modal-body .mantra-box').textContent.includes('可复制的战略资产'), '口头禅在核弹层内呈现');
ok([...d.querySelectorAll('#modal-body .srcs li')].length === 6, '列出六路原文分支与文件路径');

/* ---------------------------------------------------------------- */
section('禁止项与整页文本审查');
d.querySelector('#modal-close').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
let allText = d.body.textContent;
for (const chip of chips) {
  chip.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  await tick();
  allText += d.querySelector('#modal-body').textContent;
  d.querySelector('#modal-close').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
}
d.querySelector('#core').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
allText += d.querySelector('#modal-body').textContent;
d.querySelector('#modal-close').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));

ok(!/三条不做/.test(allText), '全页（含全部弹层）无「三条不做」');
ok(!/不做清单/.test(allText), '全页无「不做清单」');
ok(!/2030/.test(allText), '未出现「2030 覆盖重点园区」一类未经核实的时间表');
ok(!/印发/.test(allText.replace(/以正式印发文件为准|不作公司印发件口径引用/g, '')), '未把待核口径写成公司印发件');
console.log(`         全页可见文本共 ${allText.length} 字`);

/* ---------------------------------------------------------------- */
section('排版余量估算（node-canvas 按真实字体测量文本宽度）');
let measure = null;
try {
  const { createCanvas } = await import('canvas');
  const ctx = createCanvas(8, 8).getContext('2d');
  measure = (t, px, bold) => {
    ctx.font = `${bold ? 'bold ' : ''}${px}px "WenQuanYi Micro Hei", "Droid Sans Fallback", sans-serif`;
    return ctx.measureText(t || '').width;
  };
} catch {
  console.log('  SKIP  未安装 canvas，跳过文本宽度估算（npm i canvas 后可启用）');
}

if (measure) {
  const PANEL_INNER = 340 - 24; // 面板宽 340，左右内边距各 12
  let worst = { room: 1e9, who: '' };
  panels.forEach((p) => {
    const name = p.querySelector('.edge-name').textContent;
    const en = p.querySelector('.edge-en').textContent;
    const w = 20 + 8 + measure(name, 18, true) + 8 + measure(en, 10.5);
    const room = PANEL_INNER - w;
    if (room < worst.room) worst = { room, who: `${name} ${en}` };
  });
  ok(worst.room > 0, `六边面板标题行最紧的一条仍余 ${worst.room.toFixed(0)}px（${worst.who}）`);

  let tagWorst = { room: 1e9, who: '' };
  panels.forEach((p) => {
    const tag = p.querySelector('.edge-tag').textContent;
    const room = PANEL_INNER - measure(tag, 10.5);
    if (room < tagWorst.room) tagWorst = { room, who: tag };
  });
  ok(tagWorst.room > 0, `面板副标题最紧的一条仍余 ${tagWorst.room.toFixed(0)}px（${tagWorst.who}）`);

  const CHIP_W = (PANEL_INNER - 16) / 3;
  let chipWorst = { room: 1e9, who: '' };
  [...d.querySelectorAll('.chip')].forEach((c) => {
    const t = c.querySelector('.chip-name').textContent;
    const room = CHIP_W - measure(t, 14, true) - 8;
    if (room < chipWorst.room) chipWorst = { room, who: t };
  });
  ok(chipWorst.room > 0, `模型字标最宽的一个（${chipWorst.who}）在 ${CHIP_W.toFixed(0)}px 格内仍余 ${chipWorst.room.toFixed(0)}px`);

  // 对照表：按 3 行收起后估算行高，看七行能否基本一屏放下
  const COL_W = (1600 - 40 - 108) / 6 - 18;
  const LINE = 11 * 1.52;
  let tableH = 42;
  rows.forEach((tr) => {
    let rowH = 0;
    [...tr.querySelectorAll('td')].forEach((td) => {
      const h = [...td.querySelectorAll('.mx-val')].reduce((acc, v) => {
        const lines = Math.min(3, Math.ceil(measure(v.textContent, 11) / COL_W));
        return acc + lines * LINE;
      }, 0);
      rowH = Math.max(rowH, h + 24);
    });
    tableH += rowH;
  });
  const avail = 830 - 46 - 14;
  console.log(`         对照表估算总高 ${tableH.toFixed(0)}px，可视区 ${avail}px（列宽 ${COL_W.toFixed(0)}px）`);
  ok(tableH < avail * 1.25, `七行基本一屏可见（超出 ${Math.max(0, tableH - avail).toFixed(0)}px，可滚动）`);
}

section('翻页');
d.querySelectorAll('.navbtn')[1].dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
ok(
  d.querySelector('#page-matrix').classList.contains('is-active') && !d.querySelector('#page-board').classList.contains('is-active'),
  '按钮切换到第二页'
);
d.dispatchEvent(new w.KeyboardEvent('keydown', { key: '1', bubbles: true }));
ok(d.querySelector('#page-board').classList.contains('is-active'), '快捷键 1 回到首页沙盘');

console.log('\n' + (fail === 0 ? '结果：全部校验通过（0 项失败）' : `结果：${fail} 项失败`));
process.exit(fail === 0 ? 0 : 1);
