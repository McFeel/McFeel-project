/* 忠实度校验：
   - 核与五边：对照 archive/data-race4.js（第四轮赛马一揽子）
   - 普惠：对照六家重跑分支原文
   用法：node check-source.mjs                                                */
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const DIR = path.resolve(import.meta.dirname, '..');
new Function(fs.readFileSync(path.join(DIR, 'data.js'), 'utf8') + '\n;globalThis.__D = { MODELS, SOURCE_BRANCHES, PUHUI_SOURCES, MATRIX, CORE };')();
new Function(fs.readFileSync(path.join(DIR, 'archive/data-race4.js'), 'utf8') + '\n;globalThis.__A = { MODELS, MATRIX, CORE };')();
const { MODELS, SOURCE_BRANCHES, PUHUI_SOURCES, MATRIX } = globalThis.__D;
const ARCHIVE = globalThis.__A;

let fail = 0;
const ok = (c, m) => { console.log((c ? '  PASS  ' : '  FAIL  ') + m); if (!c) fail++; };

function gitShow(branch, file) {
  try {
    return execFileSync('git', ['show', `${branch}:${file}`], { cwd: DIR, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
  } catch {
    return null;
  }
}

const norm = (s) =>
  s
    .replace(/[*>`#]/g, '')
    .replace(/[「」“”"'’]/g, '')
    .replace(/[（(]/g, '(')
    .replace(/[）)]/g, ')')
    .replace(/[／/]/g, '/')
    .replace(/[＋+]/g, '+')
    .replace(/\s+/g, '')
    .replace(/[·・]/g, '')
    .replace(/[-—–]/g, '');

console.log('== 第四轮原文可达性（核与五边出处）');
for (const s of SOURCE_BRANCHES) {
  const text = gitShow(s.branch, s.file);
  ok(!!text, `${s.model}：${s.branch} ： ${s.file}${text ? `（${text.length} 字）` : ' —— 本机未取到，五边仍对照 archive'}`);
}

console.log('\n== 普惠重跑原文可达性');
const md = {};
for (const f of MODELS) {
  const text = gitShow(f.puhuiBranch, 'hq-base/hexagon-race-4/' + f.puhuiFile);
  md[f.id] = text;
  ok(!!text, `${f.name}：${f.puhuiBranch} ： hq-base/hexagon-race-4/${f.puhuiFile}${text ? `（${text.length} 字）` : ' —— 取不到，请先 git fetch 该分支'}`);
}
if (Object.values(md).some((v) => !v)) {
  console.log('\n提示：先执行 git fetch origin <分支> 再重跑。');
  process.exit(1);
}

console.log('\n== 脑图逐行比对第四轮一揽子（允许 <br> → <br/>、缩进）');
const archById = {};
ARCHIVE.MODELS.forEach((m) => { archById[m.id] = m; });
for (const f of MODELS) {
  const orig = archById[f.id].mermaid.trim().split('\n');
  const mine = f.mermaid.trim().split('\n');
  const diffs = [];
  for (let i = 0; i < Math.max(orig.length, mine.length); i++)
    if (orig[i] !== mine[i]) diffs.push({ i: i + 1, a: orig[i], b: mine[i] });
  ok(diffs.length === 0, `${f.name}：脑图与 archive 第四轮一揽子${diffs.length ? `有 ${diffs.length} 行差异` : '一致（未导入重跑另核）'}`);
}

console.log('\n== 核与五边正文对照 archive（普惠除外）');
const FIVE = ['zero', 'green', 'eff', 'smart', 'human'];
for (const f of MODELS) {
  const a = archById[f.id];
  const miss = [];
  FIVE.forEach((eid) => {
    const mine = f.edges[eid];
    const old = a.edges[eid];
    if (mine.title !== old.title) miss.push(eid + '/title');
    if (mine.blocks.length !== old.blocks.length) miss.push(eid + '/len');
    mine.blocks.forEach((b, i) => {
      if (!old.blocks[i] || b.label !== old.blocks[i].label || b.text !== old.blocks[i].text) miss.push(`${eid}/${b.label || i}`);
    });
  });
  f.coreTake.forEach((p, i) => {
    if (p !== a.coreTake[i]) miss.push('coreTake/' + i);
  });
  ok(miss.length === 0, `${f.name}：核摘录 + 五边与 archive 逐字一致${miss.length ? '（' + miss.join('、') + '）' : ''}`);
}

console.log('\n== 普惠专节逐段命中重跑原文');
let total = 0;
for (const f of MODELS) {
  const hay = norm(md[f.id]);
  const miss = [];
  let count = 0;
  const push = (where, text) => {
    count++;
    total++;
    if (!hay.includes(norm(text))) miss.push(where);
  };
  const sec = f.edges.inclusive;
  sec.blocks.forEach((b) => push(b.label, b.text));
  (sec.rejectedBlocks || []).forEach((b) => push('否/' + b.label, b.text));
  if (f.puhuiClaim) {
    const claimBits = f.puhuiClaim.split(/[／/·（）()]/).filter((p) => p.length >= 2);
    const missedClaim = claimBits.filter((p) => !hay.includes(norm(p)));
    if (missedClaim.length) miss.push('主张句:' + missedClaim.join('|'));
  }
  ok(miss.length === 0, `${f.name}：${count} 段${miss.length ? `有 ${miss.length} 处未命中（${miss.join('、')}）` : '主张／定义／否掉整段命中重跑原文'}`);
}
console.log(`         六家普惠合计 ${total} 段`);

console.log('\n== 首页未导入重跑另核／另切边');
{
  const home = fs.readFileSync(path.join(DIR, 'index.html'), 'utf8');
  ok(!/六家独立顶层设计/.test(home), 'index.html 不再写「六家独立顶层设计」');
  ok(!MODELS.some((m) => /活态试验田|共同能力场|制度试验田|公共界面/.test(m.edges.zero.blocks[0].text)), '零碳边未被重跑另核改写');
}

console.log('\n== 用户提法不得写成任何一家的普惠主张');
{
  const bad = MODELS.filter((f) => /人人参与|人人受益/.test(f.puhuiClaim || ''));
  ok(bad.length === 0, `六家普惠主张均未被写成「人人参与人人受益」${bad.length ? '（' + bad.map((f) => f.name).join('、') + '）' : ''}`);
  const rejectedBy = MODELS.filter((f) =>
    (f.edges.inclusive.rejectedBlocks || []).some((r) => /人人参与|人人受益/.test(r.label + r.text))
  );
  ok(rejectedBy.length >= 1, `该提法仅作被否读法保留：${rejectedBy.map((f) => f.name).join('、')}`);
  const wrong = MODELS.filter((f) => (f.edges.inclusive.rejectedBlocks || []).length !== 2);
  ok(wrong.length === 0, '六家各保留两条被否读法');
  const mxMissing = MODELS.filter((f) => !MATRIX.inclusive[f.id] || MATRIX.inclusive[f.id].path.length < 20);
  ok(mxMissing.length === 0, '对照表普惠行六家均已写清');
}

console.log('\n== 出处清单');
ok(SOURCE_BRANCHES.length === 6, `第四轮出处 = ${SOURCE_BRANCHES.length} 条`);
ok(PUHUI_SOURCES.length === 6, `普惠重跑出处 = ${PUHUI_SOURCES.length} 条`);
ok(
  PUHUI_SOURCES.every((s) => MODELS.some((f) => f.puhuiBranch === s.branch && 'hq-base/hexagon-race-4/' + f.puhuiFile === s.file)),
  '普惠出处清单与六家重跑分支/文件一一对应'
);

console.log('\n' + (fail === 0 ? '结果：全部校验通过（0 项失败）' : `结果：${fail} 项失败`));
process.exit(fail === 0 ? 0 : 1);
