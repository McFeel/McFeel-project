/* ============================================================
   既有园升级 · 六家独立顶层设计 · 交互层
   纯浏览器端，无构建、无框架；双击 index.html 即可运行。
   ============================================================ */

(function () {
  'use strict';

  var CENTER = { x: 800, y: 415, rx: 545, ry: 292, hubR: 160 };

  var $ = function (sel) { return document.querySelector(sel); };
  var firmById = {};
  FIRMS.forEach(function (f) { firmById[f.id] = f; });

  /* ------------------------------ 舞台缩放 ------------------------------ */

  function fitStage() {
    var s = Math.min(window.innerWidth / 1600, window.innerHeight / 900);
    $('#stage').style.transform = 'scale(' + s + ')';
  }

  /* --------------------------- 第一页：六家卡片 --------------------------- */

  function buildBoard() {
    var board = $('#board');
    $('#brand-title').textContent = STAGE.title;
    $('#brand-sub').textContent = STAGE.sub;
    $('#topnote').textContent = STAGE.note;
    $('#hub-title').textContent = STAGE.title;
    $('#hub-sub').textContent = STAGE.sub;
    $('#hub-hint').textContent = STAGE.hint;

    FIRMS.forEach(function (firm) {
      var rad = (firm.angle * Math.PI) / 180;
      var px = CENTER.x + CENTER.rx * Math.cos(rad);
      var py = CENTER.y + CENTER.ry * Math.sin(rad);

      var spoke = document.createElement('div');
      spoke.className = 'spoke';
      var len = Math.sqrt(Math.pow(px - CENTER.x, 2) + Math.pow(py - CENTER.y, 2));
      var deg = (Math.atan2(py - CENTER.y, px - CENTER.x) * 180) / Math.PI;
      spoke.style.left = CENTER.x + 'px';
      spoke.style.top = CENTER.y + 'px';
      spoke.style.width = Math.max(0, len - CENTER.hubR - 100) + 'px';
      spoke.style.transform = 'rotate(' + deg + 'deg) translateX(' + CENTER.hubR + 'px)';
      board.appendChild(spoke);

      var card = document.createElement('button');
      card.type = 'button';
      card.className = 'firm-card t-' + firm.theme;
      card.style.left = px + 'px';
      card.style.top = py + 'px';
      card.title = firm.name + '：原文脑图 + 核全文 + 各边 + 普惠专节';
      card.innerHTML =
        '<div class="firm-head">' +
        '<span class="firm-mark"><span class="firm-name">' + firm.short + '</span>' +
        '<span class="firm-ver">' + firm.ver + '</span></span>' +
        '<span class="firm-full">' + firm.name + ' · 独立顶层设计</span>' +
        '</div>' +
        '<div class="firm-core"><span class="k">核</span>' + firm.coreLine + '</div>' +
        '<div class="firm-cut"><span class="k">边怎么切</span>' + firm.cutName + '</div>' +
        '<div class="firm-cutlist">' +
        firm.cutList.map(function (c) { return '<span>' + c + '</span>'; }).join('') +
        '</div>';
      card.addEventListener('click', function () { openFirmModal(firm.id); });
      board.appendChild(card);
    });

    var legend = $('#legend-chips');
    FIRMS.forEach(function (f) {
      var d = document.createElement('div');
      d.className = 'legend-chip t-' + f.theme;
      d.textContent = f.name;
      legend.appendChild(d);
    });
  }

  /* --------------------------- 第二页：对照表 --------------------------- */

  function buildMatrix() {
    var thead = document.createElement('thead');
    var htr = document.createElement('tr');
    var corner = document.createElement('th');
    corner.innerHTML = '<div class="mx-modelhead">行 ＼ 列</div>';
    htr.appendChild(corner);
    FIRMS.forEach(function (f) {
      var th = document.createElement('th');
      th.innerHTML = '<div class="mx-modelhead"><span class="dot t-' + f.theme + '"></span>' + f.name + '</div>';
      htr.appendChild(th);
    });
    thead.appendChild(htr);

    var tbody = document.createElement('tbody');
    MATRIX_ROWS.forEach(function (row) {
      var tr = document.createElement('tr');
      tr.className = 'row-' + row.id;
      var th = document.createElement('th');
      th.innerHTML = row.name + '<small>' + row.sub + '</small>';
      tr.appendChild(th);

      FIRMS.forEach(function (f) {
        var td = document.createElement('td');
        var txt = (MATRIX[row.id] || {})[f.id] || '—';
        td.innerHTML = '<div class="mx-val">' + txt + '</div>';
        td.title = f.name + ' · ' + row.name + '（点击展开原文）';
        td.addEventListener('click', function () { openFirmModal(f.id, row.id); });
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });

    var table = $('#matrix-table');
    table.appendChild(thead);
    table.appendChild(tbody);
  }

  /* ------------------------------ mermaid ------------------------------ */

  var mermaidReady = null;
  var svgCache = {};
  var renderSeq = 0;

  function ensureMermaid() {
    if (mermaidReady) return mermaidReady;
    mermaidReady = new Promise(function (resolve, reject) {
      var t0 = Date.now();
      (function poll() {
        if (window.mermaid) {
          try {
            window.mermaid.initialize({
              startOnLoad: false,
              securityLevel: 'loose',
              theme: 'dark',
              themeVariables: {
                fontFamily: '"PingFang SC","Microsoft YaHei","Noto Sans SC",sans-serif',
                fontSize: '15px',
              },
            });
          } catch (e) { /* 用默认配置继续 */ }
          return resolve(window.mermaid);
        }
        if (window.__mermaidFailed) return reject(new Error('mermaid CDN 不可达'));
        if (Date.now() - t0 > 9000) return reject(new Error('mermaid 加载超时'));
        setTimeout(poll, 100);
      })();
    });
    return mermaidReady;
  }

  function showMermaidSource(box, firm, reason) {
    var pre = document.createElement('pre');
    pre.className = 'mermaid-src';
    pre.textContent = firm.mermaid;
    box.innerHTML = '';
    box.style.alignItems = 'flex-start';
    box.appendChild(pre);
    var note = box.parentNode.querySelector('.mermaid-note');
    if (note && reason) note.firstChild.textContent = '脑图渲染未完成（' + reason + '），已显示原文 mermaid 源码。';
  }

  function renderMermaid(box, firm) {
    if (svgCache[firm.id]) { box.innerHTML = svgCache[firm.id]; return; }
    box.innerHTML = '<div class="corner-note">脑图渲染中……</div>';
    ensureMermaid()
      .then(function (m) { return m.render('mmd-' + firm.id + '-' + (++renderSeq), firm.mermaid.trim()); })
      .then(function (res) { svgCache[firm.id] = res.svg; box.innerHTML = res.svg; })
      .catch(function (err) { showMermaidSource(box, firm, err && err.message ? err.message : '渲染失败'); });
  }

  /* ------------------------------ 弹层 ------------------------------ */

  var overlay = $('#overlay');
  var lastFocus = null;

  function openModal(eyebrowHTML, title, bodyNode) {
    $('#modal-eyebrow').innerHTML = eyebrowHTML;
    $('#modal-title').textContent = title;
    var body = $('#modal-body');
    body.innerHTML = '';
    body.appendChild(bodyNode);
    lastFocus = document.activeElement;
    overlay.hidden = false;
    $('#modal-close').focus();
  }

  function closeModal() {
    overlay.hidden = true;
    $('#modal-body').innerHTML = '';
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  function mermaidPane(firm) {
    var left = document.createElement('div');
    left.className = 'm-left';
    left.innerHTML =
      '<div class="m-secttl">原文脑图<span class="thin">· ' + firm.file + ' 内 mermaid 原文</span></div>' +
      '<div class="mermaid-box"></div>' +
      '<div class="mermaid-note">脑图取自该家原文，语法仅作渲染必要的最小修正。<button type="button">查看／收起源码</button></div>';
    var box = left.querySelector('.mermaid-box');
    renderMermaid(box, firm);
    left.querySelector('.mermaid-note button').addEventListener('click', function () {
      if (box.querySelector('pre')) {
        box.style.alignItems = 'center';
        box.innerHTML = '';
        renderMermaid(box, firm);
      } else {
        showMermaidSource(box, firm, null);
      }
    });
    return left;
  }

  function badge(firm) {
    return '<span class="badge t-' + firm.theme + '">' + firm.name + '</span>';
  }

  function blocksHTML(blocks) {
    return blocks
      .map(function (b) {
        return (
          '<div class="blk">' +
          (b.label ? '<div class="blk-label">' + b.label + '</div>' : '') +
          '<div class="blk-text">' + b.text + '</div></div>'
        );
      })
      .join('');
  }

  function openFirmModal(firmId, focusSection) {
    var firm = firmById[firmId];

    var body = document.createElement('div');
    body.className = 'm-body-row';
    body.appendChild(mermaidPane(firm));

    var right = document.createElement('div');
    right.className = 'm-right';

    var jump = '<div class="jumpbar">';
    firm.sections.forEach(function (s) {
      jump += '<button type="button" data-jump="' + s.id + '">' + s.title.replace(/^[一二三四五、\d.\s]+/, '') + '</button>';
    });
    jump += '</div>';

    var html = jump;
    firm.sections.forEach(function (s) {
      html += '<section class="sect" id="sect-' + s.id + '"><h4>' + s.title + '</h4>';
      if (s.lead) html += '<p class="sect-lead">' + s.lead + '</p>';
      if (s.nav) html += '<p class="sect-nav">本页编排：' + s.nav + '</p>';
      if (s.blocks) html += blocksHTML(s.blocks);
      if (s.edges) {
        s.edges.forEach(function (e) {
          html += '<div class="edgeblk"><div class="edgeblk-name">' + e.name + '</div>' + blocksHTML(e.blocks) + '</div>';
        });
      }
      if (s.rejectedBlocks) {
        html +=
          '<div class="rejected"><div class="rejected-ttl">' + (s.rejectedTitle || '否掉了什么') + '</div>' +
          blocksHTML(s.rejectedBlocks) + '</div>';
      }
      html += '</section>';
    });

    html +=
      '<div class="srcline">原文出处：<code>' + firm.branch + '</code> ： <code>hq-base/hexagon-race-4/' +
      firm.file + '</code><br />' + firm.docTitle + '</div>';

    right.innerHTML = html;
    body.appendChild(right);

    openModal(
      badge(firm) +
        '<span>独立顶层设计 · 原文全文</span>' +
        '<span>· 核 ' + firm.cutName + ' · 普惠：' + firm.puhuiClaim + '</span>',
      firm.name + '　·　' + firm.docTitle,
      body
    );

    Array.prototype.forEach.call(right.querySelectorAll('.jumpbar button'), function (b) {
      b.addEventListener('click', function () {
        var t = right.querySelector('#sect-' + b.dataset.jump);
        if (t) t.scrollIntoView({ block: 'start' });
      });
    });

    if (focusSection) {
      var map = { core: 'core', cut: 'edges', puhui: 'puhui', rejected: 'puhui' };
      var target = right.querySelector('#sect-' + (map[focusSection] || focusSection));
      if (target) target.scrollIntoView({ block: 'start' });
    }
  }

  /* ------------------------------ 翻页与快捷键 ------------------------------ */

  function showPage(name) {
    Array.prototype.forEach.call(document.querySelectorAll('.page'), function (p) {
      p.classList.toggle('is-active', p.id === 'page-' + name);
    });
    Array.prototype.forEach.call(document.querySelectorAll('.navbtn'), function (b) {
      b.classList.toggle('is-active', b.dataset.page === name);
    });
  }

  function bindGlobal() {
    Array.prototype.forEach.call(document.querySelectorAll('.navbtn'), function (b) {
      b.addEventListener('click', function () { showPage(b.dataset.page); });
    });
    $('#modal-close').addEventListener('click', closeModal);
    overlay.addEventListener('click', function (e) { if (e.target === overlay) closeModal(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !overlay.hidden) { closeModal(); return; }
      if (!overlay.hidden) return;
      if (e.key === '1') showPage('board');
      if (e.key === '2') showPage('matrix');
      if (e.key === 'ArrowRight') showPage('matrix');
      if (e.key === 'ArrowLeft') showPage('board');
    });
    window.addEventListener('resize', fitStage);
  }

  /* ------------------------------ 启动 ------------------------------ */

  buildBoard();
  buildMatrix();
  bindGlobal();
  fitStage();
})();
