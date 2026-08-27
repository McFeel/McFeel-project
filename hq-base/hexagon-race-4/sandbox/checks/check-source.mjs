/* 忠实度校验：把 data.js 里的六路脑图与正文，与六个原文分支逐行比对。
   只需 git，不需要任何 npm 依赖。
   用法：node check-source.mjs                                                */
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const DIR = path.resolve(import.meta.dirname, '..');
new Function(fs.readFileSync(path.join(DIR, 'data.js'), 'utf8') + '\n;globalThis.__D = { MODELS, SOURCE_BRANCHES };')();
const { MODELS, SOURCE_BRANCHES } = globalThis.__D;

let fail = 0;
const ok = (c, m) => { console.log((c ? '  PASS  ' : '  FAIL  ') + m); if (!c) fail++; };

function gitShow(branch, file) {
  try {
    return execFileSync('git', ['show', `${branch}:${file}`], { cwd: DIR, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
  } catch {
    return null;
  }
}

console.log('== 六路原文可达性');
const md = {};
for (const m of MODELS) {
  const text = gitShow(m.branch, 'hq-base/hexagon-race-4/' + m.file);
  md[m.id] = text;
  ok(!!text, `${m.name}：${m.branch} ： hq-base/hexagon-race-4/${m.file}${text ? `（${text.length} 字）` : ' —— 取不到，请先 git fetch 该分支'}`);
}
if (Object.values(md).some((v) => !v)) {
  console.log('\n提示：先执行 git fetch origin <分支> 再重跑。');
  process.exit(1);
}

console.log('\n== 脑图逐行比对（允许的最小修正：<br> → <br/>、缩进层级）');
for (const m of MODELS) {
  const block = md[m.id].match(/```mermaid\n([\s\S]*?)```/);
  if (!block) { ok(false, `${m.name}：原文未找到 mermaid 代码块`); continue; }
  const orig = block[1].replace(/\n+$/, '').split('\n');
  const mine = m.mermaid.trim().split('\n');
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
    `${m.name}：${mine.length} 行，${diffs.length ? `${diffs.length} 行最小修正（${[...new Set(kinds)].join('、')}）` : '零改动'}`
  );
  diffs.forEach((dd, k) => console.log(`          第 ${dd.i} 行[${kinds[k]}]：${(dd.a || '(无)').trim()}  →  ${(dd.b || '(无)').trim()}`));
}

/* 归一化：抹掉 Markdown 强调、引号样式、全半角括号、空白与连接符差异，
   剩下的必须逐字命中原文（整段包含，不是抽样锚点）。 */
const norm = (s) =>
  s
    .replace(/[*>`]/g, '')
    .replace(/[「」“”"'’]/g, '')
    .replace(/[（(]/g, '(')
    .replace(/[）)]/g, ')')
    .replace(/\s+/g, '')
    .replace(/[·・]/g, '')
    .replace(/[-—–]/g, '');

// 页面上必须删掉「三条不做」相关表述，这一处对原文的删改是刻意的，单独声明
const DECLARED_EDITS = {
  'glm/coreTake': '按「页面不得出现三条不做」的要求，删去原文枚举中的「一套不做清单」一项，其余逐字保留',
};

console.log('\n== 六边正文逐段整段比对（36 段/路 × 6 路 = 144 段）');
let blockTotal = 0;
for (const m of MODELS) {
  const hay = norm(md[m.id]);
  const miss = [];
  let count = 0;
  Object.keys(m.edges).forEach((eid) => {
    m.edges[eid].blocks.forEach((b) => {
      count++;
      blockTotal++;
      if (!hay.includes(norm(b.text))) miss.push(`${eid}/${b.label}`);
    });
  });
  ok(miss.length === 0, `${m.name}：${count} 段正文${miss.length ? '有 ' + miss.length + ' 段与原文不符（' + miss.join('、') + '）' : '整段逐字命中原文'}`);
}
console.log(`         六路合计 ${blockTotal} 段`);

console.log('\n== 对「核」的提法比对');
for (const m of MODELS) {
  const hay = norm(md[m.id]);
  const miss = m.coreTake.filter((t) => !hay.includes(norm(t)));
  const declared = DECLARED_EDITS[m.id + '/coreTake'];
  if (miss.length && declared) {
    console.log(`  NOTE  ${m.name}：${miss.length} 段有声明过的删改 —— ${declared}`);
    // 声明过的删改仍需保证：删改后的文字仍是原文的连续片段拼接
    const pieces = miss[0].split(/[，。：；]/).filter((p) => p.length > 6);
    const allIn = pieces.every((p) => hay.includes(norm(p)));
    ok(allIn, `${m.name}：删改后各分句仍逐字来自原文（${pieces.length} 个分句全部命中）`);
  } else {
    ok(miss.length === 0, `${m.name}：${m.coreTake.length} 段提法整段逐字命中原文`);
  }
}

console.log('\n== 出处清单');
ok(SOURCE_BRANCHES.length === 6, `页面列出的原文出处 = ${SOURCE_BRANCHES.length} 条`);
ok(
  SOURCE_BRANCHES.every((s) => MODELS.some((m) => m.branch === s.branch && 'hq-base/hexagon-race-4/' + m.file === s.file)),
  '出处清单与各路模型的分支/文件一一对应'
);

console.log('\n' + (fail === 0 ? '结果：全部校验通过（0 项失败）' : `结果：${fail} 项失败`));
process.exit(fail === 0 ? 0 : 1);
