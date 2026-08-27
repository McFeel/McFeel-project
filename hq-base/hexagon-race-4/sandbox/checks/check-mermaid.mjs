/* 脑图校验：用 CDN 实际下发的那个 UMD 文件（mermaid@10.9.1/dist/mermaid.min.js）
   在 jsdom 中挂载、解析并真正渲染成 SVG，不启动任何浏览器。
   用法：npm i jsdom mermaid@10.9.1 canvas && node check-mermaid.mjs           */
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { JSDOM } from 'jsdom';

const HERE = import.meta.dirname;
const DIR = path.resolve(HERE, '..');
const OUT = process.env.SVG_OUT || '';

const require = createRequire(import.meta.url);
let UMD, ver;
try {
  UMD = require.resolve('mermaid/dist/mermaid.min.js');
  ver = require('mermaid/package.json').version;
} catch {
  console.error('缺少 mermaid：请先在本目录执行 npm i');
  process.exit(2);
}
if (!ver.startsWith('10.')) {
  console.error(`已安装 mermaid ${ver}，但页面固定使用 10.x 的 UMD 包（11.x 的 dist 不再挂载 window.mermaid）。请执行 npm i mermaid@10.9.1`);
  process.exit(2);
}

const dom = new JSDOM('<!doctype html><html><body></body></html>', {
  runScripts: 'dangerously',
  pretendToBeVisual: true,
});
const W = dom.window;

// 补齐 jsdom 未实现、而真实浏览器自带的 API 与 SVG 排版能力
W.structuredClone = (v) => globalThis.structuredClone(v);
if (!W.matchMedia) W.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {} });
const svgProto = W.SVGElement.prototype;
svgProto.getBBox = function () {
  const n = (this.textContent || '').length;
  return { x: 0, y: 0, width: Math.max(24, n * 14), height: 22 };
};
svgProto.getComputedTextLength = function () { return Math.max(24, (this.textContent || '').length * 14); };
svgProto.getScreenCTM = function () {
  const ctm = { a: 1, b: 0, c: 0, d: 1, e: 0, f: 0, inverse: () => ctm };
  return ctm;
};
W.SVGSVGElement.prototype.createSVGPoint = function () {
  return { x: 0, y: 0, matrixTransform: () => ({ x: 0, y: 0 }) };
};
W.HTMLElement.prototype.getBoundingClientRect = function () {
  const n = (this.textContent || '').length;
  return { x: 0, y: 0, top: 0, left: 0, right: n * 14, bottom: 22, width: Math.max(24, n * 14), height: 22 };
};

const tag = W.document.createElement('script');
tag.textContent = fs.readFileSync(UMD, 'utf8');
W.document.head.appendChild(tag);

let fail = 0;
const ok = (c, m) => { console.log((c ? '  PASS  ' : '  FAIL  ') + m); if (!c) fail++; };

console.log(`== 浏览器加载路径模拟：mermaid@${ver}/dist/mermaid.min.js（${(fs.statSync(UMD).size / 1048576).toFixed(2)} MB，UMD）`);
ok(typeof W.mermaid === 'object' && W.mermaid !== null, '普通 <script> 标签即挂载 window.mermaid（无需 ES module，file:// 双击可用）');
ok(typeof W.mermaid.initialize === 'function' && typeof W.mermaid.render === 'function', 'mermaid.initialize / mermaid.render 均可用');
W.mermaid.initialize({ startOnLoad: false, securityLevel: 'loose', theme: 'dark' });

new Function(fs.readFileSync(path.join(DIR, 'data.js'), 'utf8') + '\n;globalThis.__M = MODELS;')();
const MODELS = globalThis.__M;

console.log('\n== 六路 mindmap 语法解析');
for (const m of MODELS) {
  let msg = '', good = true;
  try { await W.mermaid.parse(m.mermaid.trim()); } catch (e) { good = false; msg = ' —— ' + (e.message || e).toString().split('\n')[0]; }
  ok(good, `${m.name}（${m.mermaid.trim().split('\n').length} 行）解析通过${msg}`);
}

console.log('\n== 六路 mindmap 渲染产物');
for (const m of MODELS) {
  try {
    const { svg } = await W.mermaid.render('mmd-' + m.id, m.mermaid.trim());
    const doc = new W.DOMParser().parseFromString(svg, 'image/svg+xml');
    const nodes = doc.querySelectorAll('g.mindmap-node, .mindmap-node').length;
    const texts = [...doc.querySelectorAll('text, span')].map((e) => e.textContent).join('');
    const root = m.mermaid.match(/root\(\((.*?)\)\)/);
    const rootOK = !root || root[1].split(/<br\/?>/).every((p) => texts.includes(p));
    ok(
      svg.startsWith('<svg') && nodes > 0 && rootOK,
      `${m.name}：SVG ${(svg.length / 1024).toFixed(1)} KB，mindmap 节点 ${nodes} 个，根节点文字${rootOK ? '已渲染' : '缺失'}`
    );
    if (OUT) {
      fs.mkdirSync(OUT, { recursive: true });
      fs.writeFileSync(path.join(OUT, `mindmap-${m.id}.svg`), svg);
    }
  } catch (e) {
    ok(false, `${m.name}：渲染失败（${(e.message || e).toString().split('\n')[0]}）`);
  }
}
if (OUT) console.log('         SVG 已导出至 ' + OUT);

console.log('\n' + (fail === 0 ? '结果：全部校验通过（0 项失败）' : `结果：${fail} 项失败`));
process.exit(fail === 0 ? 0 : 1);
