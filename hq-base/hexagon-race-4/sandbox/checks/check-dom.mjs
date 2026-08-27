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

w.__mermaidFailed = true;
w.Element.prototype.scrollIntoView = function () {};

let fail = 0;
const ok = (cond, msg) => {
  console.log((cond ? '  PASS  ' : '  FAIL  ') + msg);
  if (!cond) fail++;
};
const section = (t) => console.log('\n== ' + t + ' ' + '='.repeat(Math.max(0, 60 - t.length)));
const tick = () => new Promise((r) => setTimeout(r, 0));

w.eval(data + '\n;\n' + app + '\n;globalThis.__D = { CORE, EDGES, MODELS, MATRIX };');
const { CORE, EDGES, MODELS, MATRIX } = w.__D;

const EDGE_NAMES = ['零碳', '绿色', '高效', '智慧', '人文（含健康）', '普惠'];
const FIRM_NAMES = ['GLM-5.2', 'Gemini 3.1', 'GPT-5.6', 'Kimi K3', 'Grok 4.6', 'Opus 4.8'];

/* ---------------------------------------------------------------- */
section('第一页 · 一核六边');
ok(d.querySelectorAll('#board .core-ring').length === 3, '中心是三层同心环');
ok(d.querySelector('#hub') === null, '页面已无「六家独立顶层设计」中心圆');
ok(d.querySelectorAll('.firm-card').length === 0, '页面已无六家独立机构卡片');
ok(!/六家独立顶层设计/.test(d.body.textContent), '首页正文不含「六家独立顶层设计」');

const rings = [...d.querySelectorAll('.core-ring-label')].map((el) => el.textContent);
ok(rings.some((t) => /国家/.test(t)), '第一环写国家');
ok(rings.some((t) => /南网/.test(t) && /协同/.test(d.querySelector('#core').textContent)), '第二环写南网六网协同');
ok(/第二增长曲线/.test(d.querySelector('#core').textContent), '第三环写第二增长曲线');
ok(/六张网/.test(d.querySelector('#core').textContent), '核上可见「六张网」');

const panels = [...d.querySelectorAll('.edge-panel')];
ok(panels.length === 6, `六边面板数量 = ${panels.length}（应为 6）`);
ok(
  panels.map((p) => p.querySelector('.edge-name').textContent).join(' / ') === EDGE_NAMES.join(' / '),
  '六边顺序：' + panels.map((p) => p.querySelector('.edge-name').textContent).join(' / ')
);
ok([...d.querySelectorAll('.spoke')].length === 6, '中心到六边的连接线 = 6');

panels.forEach((p, i) => {
  const chips = [...p.querySelectorAll('.chip')];
  ok(chips.length === 6, `${EDGE_NAMES[i]} 面板有六家字标`);
});

const puhui = panels.find((p) => p.querySelector('.edge-name').textContent === '普惠');
ok(puhui && puhui.classList.contains('is-revised'), '普惠面板带「重跑」标记');
ok(
  panels.filter((p) => p.classList.contains('is-revised')).length === 1,
  '只有普惠一边带重跑标记，其余五边不另起炉灶'
);

ok(/工作假设/.test(d.querySelector('#hypothesis').textContent), '顶栏有且仅有一处工作假设');
ok(
  (d.body.textContent.match(/工作假设/g) || []).length === 1,
  '「工作假设」只出现一次，不写进任何一家主张'
);

/* ---------------------------------------------------------------- */
section('禁止项');
let allText = d.body.textContent + data;
const core = d.querySelector('#core');
core.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
await tick();
allText += d.querySelector('#modal-body').textContent;
d.querySelector('#modal-close').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
for (const p of panels) {
  for (const chip of p.querySelectorAll('.chip')) {
    chip.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
    await tick();
    allText += d.querySelector('#modal-body').textContent;
    d.querySelector('#modal-close').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  }
}
ok(!/三条不做/.test(allText), '全页（含全部弹层与数据）无「三条不做」');
ok(!/全国首个零碳机房/.test(allText), '全页无「全国首个零碳机房」');
ok(
  MODELS.every((m) => !/人人参与|人人受益/.test(m.puhuiClaim || '')),
  '没有任何一家的普惠主张被写成「人人参与人人受益」'
);

/* ---------------------------------------------------------------- */
section('弹层 · 核与六边');
core.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
await tick();
ok(
  !d.querySelector('#overlay').hasAttribute('hidden') &&
    /三层核/.test(d.querySelector('#modal-title').textContent),
  '点击中心打开三层核弹层'
);
ok(d.querySelectorAll('.core-tier').length === 3, '核弹层列出三层口径');
d.querySelector('#modal-close').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));

let modalFail = 0;
const puhuiStats = [];
for (let i = 0; i < panels.length; i++) {
  const chips = [...panels[i].querySelectorAll('.chip')];
  chips[0].dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  await tick();
  if (d.querySelector('#overlay').hasAttribute('hidden')) modalFail++;
  const body = d.querySelector('#modal-body');
  const src = body.querySelector('.mermaid-src');
  ok(src && /^mindmap/.test(src.textContent.trim()), `${EDGE_NAMES[i]} × GLM 脑图回退为 mindmap 源码`);
  if (EDGE_NAMES[i] === '普惠') {
    ok(body.querySelector('.rejected'), '普惠弹层含「否掉了什么」');
    ok(body.querySelector('.claim-box'), '普惠弹层露出主张句');
    ok(/puhui-revise/.test(body.querySelector('.srcline').textContent), '普惠弹层出处指向重跑分支');
  }
  d.querySelector('#modal-close').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
}
ok(modalFail === 0, '六边弹层均可打开');

for (const p of panels) {
  if (p.querySelector('.edge-name').textContent !== '普惠') continue;
  for (const chip of p.querySelectorAll('.chip')) {
    chip.dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
    await tick();
    const body = d.querySelector('#modal-body');
    puhuiStats.push({
      title: d.querySelector('#modal-title').textContent,
      claim: (body.querySelector('.claim-box') || {}).textContent || '',
      rejected: body.querySelectorAll('.rejected .blk').length,
      text: body.textContent.length,
    });
    d.querySelector('#modal-close').dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
  }
}
ok(puhuiStats.length === 6, '普惠六家弹层全部打开');
ok(puhuiStats.every((s) => s.rejected === 2), '每家普惠都保留两条被否读法');
ok(puhuiStats.every((s) => s.text > 400), `普惠弹层未被压成一句话（最短 ${Math.min(...puhuiStats.map((s) => s.text))} 字）`);
console.log('         普惠六家主张：');
puhuiStats.forEach((s) => console.log('           ' + s.title + ' / ' + s.claim));

/* ---------------------------------------------------------------- */
section('第二页 · 核 + 六边 × 六模型');
const heads = [...d.querySelectorAll('#matrix-table thead th')];
ok(heads.length === 7, `表头列数 = ${heads.length}（行标 + 6 家）`);
ok(
  heads.slice(1).map((h) => h.textContent.trim()).join(' | ') === FIRM_NAMES.join(' | '),
  '列 = 六家：' + heads.slice(1).map((h) => h.textContent.trim()).join(' / ')
);
const rows = [...d.querySelectorAll('#matrix-table tbody tr')];
ok(rows.length === 7, `数据行数 = ${rows.length}（核 + 六边）`);
ok(
  rows.map((r) => r.querySelector('th').childNodes[0].textContent).join(' / ') ===
    ['核', ...EDGE_NAMES].join(' / '),
  '七行行标：' + rows.map((r) => r.querySelector('th').childNodes[0].textContent).join(' / ')
);
let cellsOK = true, cellCount = 0;
rows.forEach((tr) => {
  const tds = [...tr.querySelectorAll('td')];
  if (tds.length !== 6) cellsOK = false;
  tds.forEach((td) => {
    cellCount++;
    const vals = [...td.querySelectorAll('.mx-val')];
    if (vals.length !== 2 || vals.some((v) => !v.textContent.trim() || v.textContent.trim() === '—')) cellsOK = false;
  });
});
ok(cellsOK && cellCount === 42, `${cellCount} 个格子内容完整（7 行 × 6 家）`);

const puhuiRow = rows[6];
ok(
  [...puhuiRow.querySelectorAll('.mx-key')].slice(0, 2).map((k) => k.textContent).join('/') === '主张/否掉',
  '普惠行格子标签为「主张 / 否掉」'
);

rows[6].querySelectorAll('td')[3].dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
await tick();
ok(
  !d.querySelector('#overlay').hasAttribute('hidden') &&
    d.querySelector('#modal-title').textContent.startsWith('Kimi K3') &&
    /普惠/.test(d.querySelector('#modal-title').textContent),
  '点「普惠 × Kimi K3」格子打开 Kimi 普惠弹层'
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
  let geomOK = true;
  const box = [];
  panels.forEach((p) => {
    const cx = parseFloat(p.style.left), cy = parseFloat(p.style.top);
    const b = { l: cx - 170, r: cx + 170, t: cy - 108, b: cy + 108 };
    box.push(b);
    if (b.l < 0 || b.r > 1600 || b.t < 0 || b.b > 830) geomOK = false;
  });
  for (let i = 0; i < box.length; i++)
    for (let j = i + 1; j < box.length; j++) {
      const a = box[i], c = box[j];
      if (a.l < c.r && c.l < a.r && a.t < c.b && c.t < a.b) geomOK = false;
    }
  ok(geomOK, '六边面板均在 1600×900 画布内、互不重叠');
}

section('翻页');
d.querySelectorAll('.navbtn')[1].dispatchEvent(new w.MouseEvent('click', { bubbles: true }));
ok(d.querySelector('#page-matrix').classList.contains('is-active'), '按钮切换到第二页');
d.dispatchEvent(new w.KeyboardEvent('keydown', { key: '1', bubbles: true }));
ok(d.querySelector('#page-board').classList.contains('is-active'), '快捷键 1 回到第一页');

ok(CORE.layers.length === 3, '数据层锁定三层核');
ok(EDGES.length === 6 && EDGES[5].id === 'inclusive', '数据层六边以普惠收尾');
ok(Object.keys(MATRIX).length === 7, '对照表覆盖核 + 六边');

console.log('\n' + (fail === 0 ? '结果：全部校验通过（0 项失败）' : `结果：${fail} 项失败`));
process.exit(fail === 0 ? 0 : 1);
