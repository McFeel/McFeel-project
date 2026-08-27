/* 忠实度校验：把 data.js 里六家的脑图与正文，与六个原文分支逐段比对。
   只需 git，不需要任何 npm 依赖。
   用法：node check-source.mjs                                                */
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const DIR = path.resolve(import.meta.dirname, '..');
new Function(fs.readFileSync(path.join(DIR, 'data.js'), 'utf8') + '\n;globalThis.__D = { FIRMS, SOURCE_BRANCHES, MATRIX };')();
const { FIRMS, SOURCE_BRANCHES, MATRIX } = globalThis.__D;

let fail = 0;
const ok = (c, m) => { console.log((c ? '  PASS  ' : '  FAIL  ') + m); if (!c) fail++; };

function gitShow(branch, file) {
  try {
    return execFileSync('git', ['show', `${branch}:${file}`], { cwd: DIR, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
  } catch {
    return null;
  }
}

console.log('== 六家原文可达性');
const md = {};
for (const f of FIRMS) {
  const text = gitShow(f.branch, 'hq-base/hexagon-race-4/' + f.file);
  md[f.id] = text;
  ok(!!text, `${f.name}：${f.branch} ： hq-base/hexagon-race-4/${f.file}${text ? `（${text.length} 字）` : ' —— 取不到，请先 git fetch 该分支'}`);
}
if (Object.values(md).some((v) => !v)) {
  console.log('\n提示：先执行 git fetch origin <分支> 再重跑。');
  process.exit(1);
}

console.log('\n== 脑图逐行比对（允许的最小修正：<br> → <br/>、缩进层级）');
for (const f of FIRMS) {
  const block = md[f.id].match(/```mermaid\n([\s\S]*?)```/);
  if (!block) { ok(false, `${f.name}：原文未找到 mermaid 代码块`); continue; }
  const orig = block[1].replace(/\n+$/, '').split('\n');
  const mine = f.mermaid.trim().split('\n');
  const diffs = [];
  for (let i = 0; i < Math.max(orig.length, mine.length); i++)
    if (orig[i] !== mine[i]) diffs.push({ i: i + 1, a: orig[i], b: mine[i] });
  const kinds = diffs.map((dd) => {
    if (dd.a === undefined || dd.b === undefined) return 'ADD/DEL';
    if (dd.a.trim().replace(/<br>/g, '<br/>') !== dd.b.trim()) return '正文改动';
    return dd.a.trim() === dd.b.trim() ? '缩进' : '<br/>';
  });
  const bad = kinds.filter((k) => k === '正文改动' || k === 'ADD/DEL').length;
  ok(
    orig.length === mine.length && bad === 0,
    `${f.name}：${mine.length} 行（${mine[0].trim()}），${diffs.length ? `${diffs.length} 行最小修正（${[...new Set(kinds)].join('、')}）` : '零改动'}`
  );
  diffs.forEach((dd, k) => console.log(`          第 ${dd.i} 行[${kinds[k]}]：${(dd.a || '(无)').trim()}  →  ${(dd.b || '(无)').trim()}`));
}

/* 归一化：抹掉 Markdown 强调、引号样式、全半角括号、空白与连接符差异，
   剩下的必须逐字命中原文（整段包含，不是抽样锚点）。 */
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

console.log('\n== 正文逐段整段比对（核 / 各边 / 普惠专节 / 被否读法 / 附节）');
let total = 0;
for (const f of FIRMS) {
  const hay = norm(md[f.id]);
  const miss = [];
  let count = 0;
  const push = (where, text) => {
    count++;
    total++;
    if (!hay.includes(norm(text))) miss.push(where);
  };
  f.sections.forEach((s) => {
    (s.blocks || []).forEach((b, i) => push(`${s.id}/${b.label || '#' + (i + 1)}`, b.text));
    (s.edges || []).forEach((e) => e.blocks.forEach((b, i) => push(`${s.id}/${e.name}/${b.label || '#' + (i + 1)}`, b.text)));
    (s.rejectedBlocks || []).forEach((b) => push(`${s.id}/否/${b.label}`, b.text));
    if (s.lead) push(`${s.id}/lead`, s.lead);
  });
  ok(miss.length === 0, `${f.name}：${count} 段${miss.length ? `有 ${miss.length} 段与原文不符（${miss.join('、')}）` : '整段逐字命中原文'}`);
}
console.log(`         六家合计 ${total} 段`);

console.log('\n== 卡片与对照表的摘要句必须来自原文');
for (const f of FIRMS) {
  const hay = norm(md[f.id]);
  // 摘要句允许改写语序，但其中的关键短语必须逐字来自原文
  const phrases = f.coreLine.split(/[，。；：]/).filter((p) => p.length >= 8);
  const missed = phrases.filter((p) => !hay.includes(norm(p)));
  ok(missed.length === 0, `${f.name}：核一句话的 ${phrases.length} 个关键短语全部逐字来自原文${missed.length ? '（缺：' + missed.join(' / ') + '）' : ''}`);
}

console.log('\n== 用户提法不得写成任何一家的核或普惠主张');
{
  const bad = FIRMS.filter((f) => /人人参与|人人受益/.test(f.coreLine + f.puhuiClaim + f.puhuiLine));
  ok(bad.length === 0, `六家的核与普惠主张均未被写成「人人参与人人受益」${bad.length ? '（' + bad.map((f) => f.name).join('、') + '）' : ''}`);
  const rejectedBy = FIRMS.filter((f) => f.rejected.some((r) => /人人参与|人人受益/.test(r.name)));
  ok(rejectedBy.length >= 1, `该提法仅作被否读法保留在原文里：${rejectedBy.map((f) => f.name).join('、')}`);
  // 每家「否掉了什么」必须与其原文一致：两条被否读法
  const wrong = FIRMS.filter((f) => f.rejected.length !== 2);
  ok(wrong.length === 0, '六家各保留两条被否读法，未遗漏');
  const mxMissing = FIRMS.filter((f) => !MATRIX.rejected[f.id] || MATRIX.rejected[f.id].length < 60);
  ok(mxMissing.length === 0, '对照表「否掉了什么」一行六家均已写清');
}

console.log('\n== 出处清单');
ok(SOURCE_BRANCHES.length === 6, `页面列出的原文出处 = ${SOURCE_BRANCHES.length} 条`);
ok(
  SOURCE_BRANCHES.every((s) => FIRMS.some((f) => f.branch === s.branch && 'hq-base/hexagon-race-4/' + f.file === s.file)),
  '出处清单与六家的分支/文件一一对应'
);

console.log('\n' + (fail === 0 ? '结果：全部校验通过（0 项失败）' : `结果：${fail} 项失败`));
process.exit(fail === 0 ? 0 : 1);
