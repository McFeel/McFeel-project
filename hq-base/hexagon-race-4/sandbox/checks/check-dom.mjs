/* 沙盘页面结构与内容校验（jsdom，不启动任何浏览器）
   用法：npm i && node check-dom.mjs                                          */
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
w.Element.prototype.scrollIntoView = function () {};

let fail = 0;
const ok = (cond, msg) => {
  console.log((cond ? '  PASS  ' : '  FAIL  ') + msg);
  if (!cond) fail++;
};
const section = (t) => console.log('\n== ' + t + ' ' + '='.repeat(Math.max(0, 60 - t.length)));
const tick = () => new Promise((r) => setTimeout(r, 0));

w.eval(data + '\n;\n' + app + '\n;globalThis.__FIRMS = FIRMS;');
const FIRMS = w.__FIRMS;

const FIRM_NAMES = ['GLM-5.2', 'Gemini 3.1', 'GPT-5.6', 'Kimi K3', 'Grok 4.6', 'Opus 4.8'];

/* ---------------------------------------------------------------- */
section('第一页 · 六家独立顶层设计');
const cards = [...d.querySelectorAll('.firm-card')];
ok(cards.length === 6, `机构卡片数量 = ${cards.length}（应为 6）`);
ok([...d.querySelectorAll('.spoke')].length === 6, '中心到六家的连接线 = 6');
ok(
  cards.map((c) => c.querySelector('.firm-full').textContent.replace(' · 独立顶层设计', '')).join(' | ') === FIRM_NAMES.join(' | '),
  '六家顺序：' + cards.map((c) => c.querySelector('.firm-name').textContent).join(' / ')
);

const hub = d.querySelector('#hub');
ok(hub.textContent.includes('既有园升级 · 六家独立顶层设计'), '中心写「既有园升级 · 六家独立顶层设计」');
ok(
  !/三层核|国家六张网|六网协同/.test(hub.textContent),
  '中心不再是三层核（不含三层核／国家六张网／六网协同字样）'
);
ok(d.querySelectorAll('#board .core-ring').length === 0, '页面已无三层同心环结构');

// 卡片上只露该家自己的核一句话 + 边的切法
let cardOK = true;
const cuts = [];
cards.forEach((c) => {
  const core = c.querySelector('.firm-core');
  const cut = c.querySelector('.firm-cut');
  const list = [...c.querySelectorAll('.firm-cutlist span')];
  if (!core || core.textContent.length < 30) cardOK = false;
  if (!cut || cut.textContent.length < 8) cardOK = false;
  if (list.length < 3) cardOK = false;
  cuts.push(cut.textContent.replace('边怎么切', '').trim() + '（' + list.length + ' 条）');
});
ok(cardOK, '每张卡片都有核一句话 + 边的切法名称 + 边名列表');
console.log('         六家切法：\n           ' + cuts.join('\n           '));
ok(new Set(cuts).size === 6, '六家切法互不相同，未被塞回统一六边');
ok(
  cards.every((c) => !/零碳|绿色|高效|智慧|人文/.test(c.querySelector('.firm-cutlist').textContent)),
  '卡片边名列表不含统一六边（零碳/绿色/高效/智慧/人文）'
);

/* ---------------------------------------------------------------- */
section('禁止项');
let allText = d.body.textContent;
for (const c of cards) {
  c.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  await tick();
  allText += d.querySelector('#modal-body').textContent;
  d.querySelector('#modal-close').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
}
ok(!/三条不做/.test(allText), '全页（含全部弹层）无「三条不做」');
ok(!/工作假设/.test(allText), '全页无用户「人人参与人人受益」工作假设小字');
{
  // 「人人参与、人人受益」只能作为某几家原文里被否掉的读法出现，不得成为任何一家的核或普惠主张
  const asCore = FIRMS.filter((f) => /人人参与|人人受益/.test(f.coreLine));
  const asClaim = FIRMS.filter((f) => /人人参与|人人受益/.test(f.puhuiClaim + f.puhuiLine));
  ok(asCore.length === 0 && asClaim.length === 0, '没有任何一家的核或普惠主张被写成「人人参与人人受益」');
  const asRejected = FIRMS.filter((f) => f.rejected.some((r) => /人人参与|人人受益/.test(r.name)));
  ok(asRejected.length >= 1, `「人人参与人人受益」仅作被否读法出现在 ${asRejected.map((f) => f.name).join('、')} 的原文里`);
}

/* ---------------------------------------------------------------- */
section('弹层 · 六家原文全文');
let modalFail = 0, srcFail = 0;
const stat = [];
for (const c of cards) {
  c.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  await tick();
  if (d.querySelector('#overlay').hasAttribute('hidden')) { modalFail++; continue; }
  const body = d.querySelector('#modal-body');
  const name = d.querySelector('#modal-title').textContent.split('　·　')[0];
  const core = body.querySelector('#sect-core');
  const edges = body.querySelector('#sect-edges');
  const puhui = body.querySelector('#sect-puhui');
  const rejected = body.querySelectorAll('#sect-puhui .rejected .blk');
  const src = body.querySelector('.mermaid-src');
  if (!src || !/^(mindmap|graph)/.test(src.textContent)) srcFail++;
  if (!body.querySelector('.srcline').textContent.includes('origin/cursor/')) srcFail++;
  stat.push({
    name,
    core: core ? core.textContent.length : 0,
    edges: edges ? edges.querySelectorAll('.edgeblk').length : 0,
    edgeLen: edges ? edges.textContent.length : 0,
    puhui: puhui ? puhui.textContent.length : 0,
    rejected: rejected.length,
  });
  d.querySelector('#modal-close').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
}
ok(modalFail === 0, `六家弹层全部打开成功（异常 ${modalFail} 处）`);
ok(srcFail === 0, `脑图 CDN 不可用时全部回退为原文 mermaid／graph 源码，且均带原文出处（异常 ${srcFail} 处）`);
ok(stat.length === 6 && stat.every((s) => s.core > 150), `每家都有核全文（最短 ${Math.min(...stat.map((s) => s.core))} 字）`);
ok(stat.every((s) => s.edges >= 1 && s.edgeLen > 200), `每家都有各边全文（最少 ${Math.min(...stat.map((s) => s.edges))} 条边、最短 ${Math.min(...stat.map((s) => s.edgeLen))} 字）`);
ok(stat.every((s) => s.puhui > 500), `每家普惠专节未被压成一句话（最短 ${Math.min(...stat.map((s) => s.puhui))} 字）`);
ok(stat.every((s) => s.rejected === 2), `每家都完整保留它否掉的另两种普惠（各 ${[...new Set(stat.map((s) => s.rejected))].join(',')} 条）`);
console.log('         各家弹层字数（核 / 边 / 普惠专节 / 否掉几种）：');
stat.forEach((s) => console.log(`           ${s.name.padEnd(11)} ${s.core} / ${s.edgeLen} / ${s.puhui} / ${s.rejected}`));

/* ---------------------------------------------------------------- */
section('第二页 · 四行 × 六家对照表');
const heads = [...d.querySelectorAll('#matrix-table thead th')];
ok(heads.length === 7, `表头列数 = ${heads.length}（行标 + 6 家）`);
ok(heads.slice(1).map((h) => h.textContent.trim()).join(' | ') === FIRM_NAMES.join(' | '), '列 = 六家：' + heads.slice(1).map((h) => h.textContent.trim()).join(' / '));
const rows = [...d.querySelectorAll('#matrix-table tbody tr')];
ok(rows.length === 4, `数据行数 = ${rows.length}（核 / 边怎么切 / 普惠主张 / 否掉了什么）`);
ok(
  rows.map((r) => r.querySelector('th').childNodes[0].textContent).join(' / ') === '核 / 边怎么切 / 普惠主张 / 否掉了什么',
  '四行行标：' + rows.map((r) => r.querySelector('th').childNodes[0].textContent).join(' / ')
);
let cellsOK = true, thin = 0, cellCount = 0;
rows.forEach((tr) => {
  const tds = [...tr.querySelectorAll('td')];
  if (tds.length !== 6) cellsOK = false;
  tds.forEach((td) => {
    cellCount++;
    const v = td.querySelector('.mx-val');
    if (!v || v.textContent.trim() === '—') cellsOK = false;
    if (v.textContent.length < 60) thin++;
  });
});
ok(cellsOK && cellCount === 24, `${cellCount} 个格子内容完整（4 行 × 6 家）`);
ok(thin === 0, `无过短格子（<60 字）：${thin} 个`);
{
  // 「否掉了什么」一行必须每家都写出两条被否读法
  const rejRow = rows[3];
  const bad = [...rejRow.querySelectorAll('.mx-val')].filter(
    (v) => (v.textContent.match(/不选|不取|否决|不作总纲/g) || []).length < 2
  );
  ok(bad.length === 0, '「否掉了什么」一行每家都写出两条被否读法');
}
// 点格子应能打开对应家的弹层
rows[2].querySelectorAll('td')[3].dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
await tick();
ok(
  !d.querySelector('#overlay').hasAttribute('hidden') && d.querySelector('#modal-title').textContent.startsWith('Kimi K3'),
  '点「普惠主张 × Kimi K3」格子打开 Kimi K3 原文弹层'
);
d.querySelector('#modal-close').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));

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
  console.log('  SKIP  未安装 canvas，跳过文本宽度估算');
}

if (measure) {
  // 卡片几何：不越界、互不重叠、不压中心圆
  const HUB_R = 160;
  let geomOK = true;
  const box = [];
  cards.forEach((c) => {
    const cx = parseFloat(c.style.left), cy = parseFloat(c.style.top);
    const b = { l: cx - 180, r: cx + 180, t: cy - 105, b: cy + 105 };
    box.push(b);
    if (b.l < 0 || b.r > 1600 || b.t < 0 || b.b > 830) geomOK = false;
    const dx = Math.max(Math.abs(cx - 800) - 180, 0);
    const dy = Math.max(Math.abs(cy - 415) - 105, 0);
    if (Math.hypot(dx, dy) < HUB_R * 0.6) geomOK = false;
  });
  for (let i = 0; i < box.length; i++)
    for (let j = i + 1; j < box.length; j++) {
      const a = box[i], c = box[j];
      if (a.l < c.r && c.l < a.r && a.t < c.b && c.t < a.b) geomOK = false;
    }
  ok(geomOK, '六张卡片均在 1600×830 画布内、互不重叠、不压中心圆');

  const INNER = 360 - 26;
  const LINE = 11.5 * 1.55;
  let worst = { room: 1e9, who: '' };
  cards.forEach((c) => {
    const coreTxt = c.querySelector('.firm-core').textContent;
    const cutTxt = c.querySelector('.firm-cut').textContent;
    const chips = [...c.querySelectorAll('.firm-cutlist span')];
    const coreLines = Math.ceil(measure(coreTxt, 11.5) / (INNER - 24));
    const cutLines = Math.ceil(measure(cutTxt, 11.5) / (INNER - 24));
    let rowW = 0, chipRows = 1;
    chips.forEach((s) => {
      const wpx = measure(s.textContent, 10.5) + 21;
      if (rowW + wpx > INNER) { chipRows++; rowW = wpx; } else rowW += wpx + 5;
    });
    const used = 11 + 20 + 7 + 1 + 8 + coreLines * LINE + 8 + cutLines * LINE + 7 + chipRows * 21 + 12;
    const room = 210 - used;
    if (room < worst.room) worst = { room, who: c.querySelector('.firm-name').textContent };
  });
  ok(worst.room > 0, `卡片内容最挤的一张（${worst.who}）仍余 ${worst.room.toFixed(0)}px 竖向余量`);

  const COL_W = (1600 - 40 - 104) / 6 - 20;
  let tableH = 42;
  rows.forEach((tr) => {
    let rowH = 0;
    [...tr.querySelectorAll('.mx-val')].forEach((v) => {
      const lines = Math.min(8, Math.ceil(measure(v.textContent, 11) / COL_W));
      rowH = Math.max(rowH, lines * 11 * 1.55 + 17);
    });
    tableH += rowH;
  });
  const avail = 830 - 46 - 14;
  console.log(`         对照表估算总高 ${tableH.toFixed(0)}px，可视区 ${avail}px（列宽 ${COL_W.toFixed(0)}px）`);
  ok(tableH <= avail, '四行一屏可见，无需滚动');
}

section('翻页');
d.querySelectorAll('.navbtn')[1].dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
ok(d.querySelector('#page-matrix').classList.contains('is-active'), '按钮切换到第二页');
d.dispatchEvent(new w.KeyboardEvent('keydown', { key: '1', bubbles: true }));
ok(d.querySelector('#page-board').classList.contains('is-active'), '快捷键 1 回到第一页');

console.log('\n' + (fail === 0 ? '结果：全部校验通过（0 项失败）' : `结果：${fail} 项失败`));
process.exit(fail === 0 ? 0 : 1);
