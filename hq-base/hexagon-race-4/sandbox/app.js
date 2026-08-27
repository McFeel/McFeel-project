/* ============================================================
   南网总部基地既有园 · 六边形沙盘 · 交互层
   纯浏览器端，无构建、无框架；双击 index.html 即可运行。
   ============================================================ */

(function () {
  'use strict';

  var VER = { glm: '5.2', gemini: '3.1', gpt: '5.6', kimi: 'K3', grok: '4.6', opus: '4.8' };
  var CENTER = { x: 800, y: 415, rx: 545, ry: 292, coreR: 152 };

  var $ = function (sel) { return document.querySelector(sel); };
  var modelById = {};
  MODELS.forEach(function (m) { modelById[m.id] = m; });
  var edgeById = {};
  EDGES.forEach(function (e) { edgeById[e.id] = e; });

  /* ------------------------------ 舞台缩放 ------------------------------ */

  function fitStage() {
    var stage = $('#stage');
    var s = Math.min(window.innerWidth / 1600, window.innerHeight / 900);
    stage.style.transform = 'scale(' + s + ')';
  }

  /* ------------------------------ 首页沙盘 ------------------------------ */

  function buildBoard() {
    var board = $('#board');
    $('#mantra').textContent = CORE.mantra;
    $('#hypothesis').textContent = CORE.hypothesis;
    $('#hexnote').textContent = CORE.hexNote;

    var pendingTip = CORE.layers[1].pending;
    Array.prototype.forEach.call(document.querySelectorAll('sup.pending'), function (el) {
      el.setAttribute('title', pendingTip);
      el.setAttribute('data-tip', pendingTip);
    });

    EDGES.forEach(function (edge, i) {
      var rad = (edge.angle * Math.PI) / 180;
      var px = CENTER.x + CENTER.rx * Math.cos(rad);
      var py = CENTER.y + CENTER.ry * Math.sin(rad);

      var spoke = document.createElement('div');
      spoke.className = 'spoke';
      var len = Math.sqrt(Math.pow(px - CENTER.x, 2) + Math.pow(py - CENTER.y, 2));
      var deg = (Math.atan2(py - CENTER.y, px - CENTER.x) * 180) / Math.PI;
      spoke.style.left = CENTER.x + 'px';
      spoke.style.top = CENTER.y + 'px';
      spoke.style.width = Math.max(0, len - CENTER.coreR - 96) + 'px';
      spoke.style.transform = 'rotate(' + deg + 'deg) translateX(' + CENTER.coreR + 'px)';
      board.appendChild(spoke);

      var panel = document.createElement('div');
      panel.className = 'edge-panel';
      panel.style.left = px + 'px';
      panel.style.top = py + 'px';

      var head = document.createElement('div');
      head.className = 'edge-panel-head';
      if (edge.revised) panel.classList.add('is-revised');
      head.innerHTML =
        '<div class="edge-panel-title">' +
        '<span class="edge-idx">' + (i + 1) + '</span>' +
        '<span class="edge-name">' + edge.name + '</span>' +
        '<span class="edge-en">' + edge.en + '</span>' +
        (edge.revised ? '<span class="edge-revised">重跑</span>' : '') +
        '</div>' +
        '<div class="edge-tag">' + edge.tag + '</div>';
      panel.appendChild(head);

      var chips = document.createElement('div');
      chips.className = 'chips';
      MODELS.forEach(function (m) {
        var b = document.createElement('button');
        b.className = 'chip t-' + m.theme;
        b.type = 'button';
        b.title = m.name + ' · ' + edge.name + '　（原文脑图 + 该边完整方案）';
        b.innerHTML =
          '<span class="chip-name">' + m.short + '</span>' +
          '<span class="chip-sub">' + VER[m.id] + '</span>';
        b.addEventListener('click', function () { openEdgeModal(m.id, edge.id); });
        chips.appendChild(b);
      });
      panel.appendChild(chips);
      board.appendChild(panel);
    });

    var legend = $('#legend-chips');
    MODELS.forEach(function (m) {
      var d = document.createElement('div');
      d.className = 'legend-chip t-' + m.theme;
      d.textContent = m.name;
      legend.appendChild(d);
    });

    var core = $('#core');
    core.addEventListener('click', openCoreModal);
    core.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openCoreModal(); }
    });
  }

  /* ------------------------------ 对照表 ------------------------------ */

  function buildMatrix() {
    var rows = [{ id: 'core', name: '核', sub: '三层口径' }].concat(
      EDGES.map(function (e) { return { id: e.id, name: e.name, sub: e.en }; })
    );

    var thead = document.createElement('thead');
    var htr = document.createElement('tr');
    var corner = document.createElement('th');
    corner.innerHTML = '<div class="mx-modelhead">行 ＼ 列</div>';
    htr.appendChild(corner);
    MODELS.forEach(function (m) {
      var th = document.createElement('th');
      th.innerHTML =
        '<div class="mx-modelhead"><span class="dot t-' + m.theme + '"></span>' + m.name + '</div>';
      htr.appendChild(th);
    });
    thead.appendChild(htr);

    var tbody = document.createElement('tbody');
    rows.forEach(function (row) {
      var tr = document.createElement('tr');
      if (row.id === 'core') tr.className = 'row-core';
      var th = document.createElement('th');
      th.innerHTML = row.name + '<small>' + row.sub + '</small>';
      tr.appendChild(th);

      MODELS.forEach(function (m) {
        var cell = (MATRIX[row.id] || {})[m.id] || { path: '—', pack: '—' };
        var pathKey = row.id === 'inclusive' ? '主张' : '路径';
        var packKey = row.id === 'inclusive' ? '否掉' : '厂商·园区';
        var td = document.createElement('td');
        td.innerHTML =
          '<div class="mx-line"><span class="mx-key">' + pathKey + '</span><span class="mx-val">' + cell.path + '</span></div>' +
          '<div class="mx-line is-pack"><span class="mx-key">' + packKey + '</span><span class="mx-val">' + cell.pack + '</span></div>';
        td.title = m.name + ' · ' + row.name + '（点击展开原文）';
        td.addEventListener('click', function () {
          if (row.id === 'core') openCoreModal(m.id);
          else openEdgeModal(m.id, row.id);
        });
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

  function showMermaidSource(box, model, reason) {
    var pre = document.createElement('pre');
    pre.className = 'mermaid-src';
    pre.textContent = model.mermaid;
    box.innerHTML = '';
    box.style.alignItems = 'flex-start';
    box.appendChild(pre);
    var note = box.parentNode.querySelector('.mermaid-note');
    if (note && reason) note.firstChild.textContent = '脑图渲染未完成（' + reason + '），已显示原文 mermaid 源码。';
  }

  function renderMermaid(box, model) {
    if (svgCache[model.id]) { box.innerHTML = svgCache[model.id]; return; }
    box.innerHTML = '<div class="corner-note">脑图渲染中……</div>';
    ensureMermaid()
      .then(function (m) {
        return m.render('mmd-' + model.id + '-' + (++renderSeq), model.mermaid.trim());
      })
      .then(function (res) {
        svgCache[model.id] = res.svg;
        box.innerHTML = res.svg;
      })
      .catch(function (err) {
        showMermaidSource(box, model, err && err.message ? err.message : '渲染失败');
      });
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

  function mermaidPane(model, note) {
    var left = document.createElement('div');
    left.className = 'm-left';
    left.innerHTML =
      '<div class="m-secttl">原文思维导图<span class="thin">· ' + model.file + ' 内 mermaid 原文</span></div>' +
      '<div class="mermaid-box"></div>' +
      '<div class="mermaid-note">' + (note || '脑图取自该路第四轮六边形一揽子，语法仅作渲染必要的最小修正。') +
      '<button type="button">查看／收起源码</button></div>';
    var box = left.querySelector('.mermaid-box');
    renderMermaid(box, model);
    left.querySelector('.mermaid-note button').addEventListener('click', function () {
      if (box.querySelector('pre')) {
        box.style.alignItems = 'center';
        box.innerHTML = '';
        renderMermaid(box, model);
      } else {
        showMermaidSource(box, model, null);
      }
    });
    return left;
  }

  function badge(model) {
    return '<span class="badge t-' + model.theme + '">' + model.name + '</span>';
  }

  function openEdgeModal(modelId, edgeId) {
    var model = modelById[modelId];
    var edge = edgeById[edgeId];
    var section = model.edges[edgeId];

    var isPuhui = edgeId === 'inclusive';
    var mermaidNote = isPuhui
      ? '脑图取自该路第四轮六边形一揽子（一核六边未改）；右侧为该路重跑后的普惠专节原文。'
      : null;

    var body = document.createElement('div');
    body.className = 'm-body-row';
    body.appendChild(mermaidPane(model, mermaidNote));

    var right = document.createElement('div');
    right.className = 'm-right';
    var html = '<h4>' + section.title + '</h4>';
    if (isPuhui && model.puhuiClaim) {
      html += '<div class="claim-box">主张：' + model.puhuiClaim + '</div>';
    }
    section.blocks.forEach(function (b) {
      html +=
        '<div class="blk"><div class="blk-label">' + b.label + '</div>' +
        '<div class="blk-text">' + b.text + '</div></div>';
    });
    if (section.rejectedBlocks && section.rejectedBlocks.length) {
      html +=
        '<div class="rejected"><div class="rejected-ttl">' + (section.rejectedTitle || '否掉了什么') + '</div>';
      section.rejectedBlocks.forEach(function (b) {
        html +=
          '<div class="blk"><div class="blk-label">' + b.label + '</div>' +
          '<div class="blk-text">' + b.text + '</div></div>';
      });
      html += '</div>';
    }
    if (model.sources && model.sources.length && !isPuhui) {
      html +=
        '<details class="srcpack"><summary>该路原文所附公开案例与依据（' + model.sources.length + ' 条）</summary><ul class="srcs">' +
        model.sources
          .map(function (s) {
            return '<li>' + (s.url ? '<a href="' + s.url + '" target="_blank" rel="noreferrer">' + s.text + '</a>' : s.text) + '</li>';
          })
          .join('') +
        '</ul></details>';
    }
    if (isPuhui) {
      html +=
        '<div class="srcline">普惠重跑出处：<code>' + model.puhuiBranch + '</code> ： <code>hq-base/hexagon-race-4/' +
        model.puhuiFile + '</code><br />' + model.puhuiDocTitle +
        '<br />脑图仍取自第四轮一揽子：<code>' + model.branch + '</code> ： <code>hq-base/hexagon-race-4/' +
        model.file + '</code></div>';
    } else {
      html +=
        '<div class="srcline">原文出处：<code>' + model.branch + '</code> ： <code>hq-base/hexagon-race-4/' +
        model.file + '</code><br />' + model.docTitle + '</div>';
    }
    right.innerHTML = html;
    body.appendChild(right);

    openModal(
      badge(model) + '<span>' + edge.name + '　' + edge.en + '</span><span>· ' +
        (isPuhui ? '该路重跑后的普惠专节' : '该路原文完整方案') + '</span>',
      model.name + '　·　' + edge.name + (isPuhui && model.puhuiClaim ? '　·　' + model.puhuiClaim : ''),
      body
    );
  }

  function openCoreModal(focusModelId) {
    var body = document.createElement('div');
    body.className = 'm-body-row';

    var left = document.createElement('div');
    left.className = 'm-left is-scroll';
    var lh = '<div class="mantra-box">' + CORE.mantra + '</div>';
    CORE.layers.forEach(function (l) {
      lh += '<div class="core-tier"><div class="tier">' + l.tier + '</div>' +
        '<div class="headline">' + l.headline +
        (l.pending ? '<sup class="pending" title="' + l.pending + '">待核</sup>' : '') + '</div>' +
        '<div class="body">' + l.body + '</div><ul class="items">' +
        l.items.map(function (it) { return '<li>' + it + '</li>'; }).join('') +
        '</ul></div>';
    });
    lh += '<div class="note-inline">' + CORE.hexNote + '</div>';
    left.innerHTML = lh;
    body.appendChild(left);

    var right = document.createElement('div');
    right.className = 'm-right';
    var rh = '<h4>六路模型对「核」的提法（原文摘录，口径以左侧三层核为准）</h4>';
    var list = MODELS.slice();
    if (focusModelId) {
      list.sort(function (a, b) {
        return (a.id === focusModelId ? -1 : 0) - (b.id === focusModelId ? -1 : 0);
      });
    }
    list.forEach(function (m) {
      rh += '<div class="take"><div class="take-head">' + badge(m) +
        '<span class="file">' + m.file + '</span></div>';
      m.coreTake.forEach(function (p) { rh += '<p>' + p + '</p>'; });
      rh += '</div>';
    });
    rh += '<div class="srcline">六路原文出处（<code>git show &lt;分支&gt;:&lt;文件&gt;</code> 可取全文）：<ul class="srcs">';
    SOURCE_BRANCHES.forEach(function (s) {
      rh += '<li>' + s.model + '：<code>' + s.branch + '</code> ： <code>' + s.file + '</code></li>';
    });
    rh += '</ul></div>';
    right.innerHTML = rh;
    body.appendChild(right);

    openModal(
      '<span class="badge" style="background:#e3b562;color:#06131f">核</span>' +
        '<span>三层口径 · 国家 → 南网响应 → 南网自身</span>',
      '三层核',
      body
    );
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
