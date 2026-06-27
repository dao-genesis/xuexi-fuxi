/* 复习板块 · 通用复习站点 · 客户端渲染
 * 读取页面内嵌的 course-data(JSON)，左侧分组导航，主区渲染 Markdown，
 * 支持：KaTeX 公式 / Mermaid 思维导图 / markmap 大纲 / 全文检索 / 暗色主题 / 一键打印导出。
 */
(function () {
  "use strict";

  var dataEl = document.getElementById("course-data");
  if (!dataEl) return;
  var COURSE = JSON.parse(dataEl.textContent);

  // ---------- math protect (LaTeX 不被 markdown 破坏) ----------
  var MATH_OPEN = "\u0001MATH", MATH_CLOSE = "\u0001";
  function protectMath(md) {
    var store = [];
    md = md.replace(/\$\$([\s\S]+?)\$\$/g, function (m, tex) {
      store.push({ display: true, tex: tex });
      return MATH_OPEN + (store.length - 1) + MATH_CLOSE;
    });
    md = md.replace(/(^|[^\\$])\$([^\$\n]+?)\$/g, function (m, pre, tex) {
      store.push({ display: false, tex: tex });
      return pre + MATH_OPEN + (store.length - 1) + MATH_CLOSE;
    });
    return { md: md, store: store };
  }
  // 裸百分号会被 KaTeX 当作注释（吞掉行尾含右花括号），转义为 \%；已转义的保持不变。
  function sanitizeTex(tex) {
    return tex.replace(/\\%/g, "\u0001PCT\u0001")
              .replace(/%/g, "\\%")
              .replace(/\u0001PCT\u0001/g, "\\%");
  }
  function restoreMath(html, store) {
    return html.replace(new RegExp(MATH_OPEN + "(\\d+)" + MATH_CLOSE, "g"), function (m, i) {
      var item = store[+i];
      if (!item) return m;
      try {
        return window.katex.renderToString(sanitizeTex(item.tex), {
          displayMode: item.display, throwOnError: false, strict: false, output: "html"
        });
      } catch (e) {
        return '<code>' + escapeHtml(item.tex) + '</code>';
      }
    });
  }
  function escapeHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  // ---------- markmap 代码块 -> 大纲 HTML ----------
  function markmapToHtml(src) {
    var lines = src.split("\n"), out = ['<div class="markmap-outline">'];
    var listOpen = false;
    lines.forEach(function (ln) {
      var hm = ln.match(/^(#{1,6})\s+(.*)$/);
      if (hm) {
        if (listOpen) { out.push("</ul>"); listOpen = false; }
        out.push('<div class="mm-h" style="margin-left:' + (hm[1].length - 1) * 14 + 'px">' + escapeHtml(hm[2]) + "</div>");
        return;
      }
      var lm = ln.match(/^(\s*)[-*+]\s+(.*)$/);
      if (lm) {
        if (!listOpen) { out.push("<ul>"); listOpen = true; }
        out.push('<li style="margin-left:' + lm[1].length * 6 + 'px">' + escapeHtml(lm[2]) + "</li>");
        return;
      }
      if (ln.trim() && !listOpen) out.push("<div>" + escapeHtml(ln) + "</div>");
    });
    if (listOpen) out.push("</ul>");
    out.push("</div>");
    return out.join("\n");
  }

  // ---------- marked renderer ----------
  var mermaidSeq = 0;
  function buildRenderer() {
    var r = new marked.Renderer();
    r.code = function (code, infostring) {
      var lang = (infostring || "").trim().split(/\s+/)[0];
      if (lang === "mermaid") {
        return '<div class="mermaid">' + escapeHtml(code) + "</div>";
      }
      if (lang === "markmap") {
        return markmapToHtml(code);
      }
      return "<pre><code>" + escapeHtml(code) + "</code></pre>";
    };
    r.image = function (href, title, text) {
      // 课件页图(page_*.jpg)未随仓库提交：给出占位，若图存在则正常显示
      var alt = text || "";
      return '<img src="' + href + '" alt="' + escapeHtml(alt) + '" loading="lazy" ' +
        'onerror="this.outerHTML=&quot;<span class=\\&quot;img-missing\\&quot;>\u25a4 ' + escapeHtml(alt || href) + '</span>&quot;">';
    };
    return r;
  }
  var RENDERER = buildRenderer();
  marked.setOptions({ gfm: true, breaks: false, headerIds: false, mangle: false });

  // 正文里的比较号与区间号本是数学符号，却会被 Markdown 误解析：
  //  ① 孤立 ~（如 1~3 / 100~1000）被 GFM 当成删除线（仅 ~~ 才应是删除线）；
  //  ② 裸 <（如 K<1 / <之和）被当成 HTML 标签起始，吞掉其后的 **加粗** 等行内语法。
  // 故在「代码块/行内代码之外」先占位保护 ~、转义比较号 <（标签 <a 等不动），解析后再还原。
  var TILDE_HOLD = "\u0001TLD\u0001";
  function protectInline(md) {
    var parts = md.split(/(```[\s\S]*?```|`[^`\n]*`)/g);
    for (var i = 0; i < parts.length; i += 2) {
      parts[i] = parts[i]
        .replace(/(^|[^~])~(?!~)/g, "$1" + TILDE_HOLD)
        .replace(/<(?![A-Za-z\/!?])/g, "&lt;");
    }
    return parts.join("");
  }
  function renderMarkdown(md) {
    var p = protectMath(md);
    var html = marked.parse(protectInline(p.md), { renderer: RENDERER });
    html = html.split(TILDE_HOLD).join("~");
    return restoreMath(html, p.store);
  }

  function runDynamic(container) {
    // mermaid
    var nodes = container.querySelectorAll(".mermaid");
    if (nodes.length && window.mermaid) {
      nodes.forEach(function (n, i) { n.id = "mmd-" + (mermaidSeq++) + "-" + i; });
      try { window.mermaid.run({ nodes: nodes }); } catch (e) { /* 单图失败不阻断 */ }
    }
  }

  // ---------- DOM refs ----------
  var elSidebar = document.getElementById("sidebar");
  var elContent = document.getElementById("content");
  var elSearch = document.getElementById("search-input");

  // ---------- build nav ----------
  var GROUP_ORDER = ["章节精讲", "实验精讲 · 上机", "考前综合", "考前精华", "总览资料", "真题与网络资源", "期末冲刺", "原始课件", "导览", "复习资料", "例题精解 · 深化", "章节素材", "学习系统", "知识图谱", "原始课件 · 页图", "原始课件 · PDF原文"];
  var sectionsById = {};
  COURSE.sections.forEach(function (s) { sectionsById[s.id] = s; });

  function buildNav() {
    var groups = {};
    COURSE.sections.forEach(function (s) {
      (groups[s.group] = groups[s.group] || []).push(s);
    });
    var order = GROUP_ORDER.filter(function (g) { return groups[g]; });
    Object.keys(groups).forEach(function (g) { if (order.indexOf(g) < 0) order.push(g); });

    elSidebar.innerHTML = "";
    order.forEach(function (g) {
      var gdiv = document.createElement("div");
      gdiv.className = "group";
      var gt = document.createElement("div");
      gt.className = "group-title";
      gt.textContent = g + " · " + groups[g].length;
      gdiv.appendChild(gt);
      groups[g].forEach(function (s) {
        var b = document.createElement("button");
        b.className = "nav-item";
        b.textContent = s.title;
        b.dataset.id = s.id;
        b.title = s.title;
        b.addEventListener("click", function () { selectSection(s.id); closeSidebarMobile(); });
        gdiv.appendChild(b);
      });
      elSidebar.appendChild(gdiv);
    });
  }

  var currentId = null;
  function selectSection(id, scrollToText) {
    var s = sectionsById[id];
    if (!s) return;
    currentId = id;
    Array.prototype.forEach.call(elSidebar.querySelectorAll(".nav-item"), function (b) {
      b.classList.toggle("active", b.dataset.id === id);
    });
    var active = elSidebar.querySelector(".nav-item.active");
    if (active) active.scrollIntoView({ block: "nearest" });

    elContent.innerHTML =
      '<div class="crumbs">' + escapeHtml(COURSE.title) + " / " + escapeHtml(s.group) + "</div>" +
      '<article class="doc" id="doc"></article>';
    var doc = document.getElementById("doc");
    doc.innerHTML = renderMarkdown(s.md);
    runDynamic(doc);
    window.scrollTo(0, 0);
    if (scrollToText) highlightAndScroll(doc, scrollToText);
    if (history.replaceState) history.replaceState(null, "", "#" + encodeURIComponent(id));
  }

  function highlightAndScroll(root, q) {
    var lower = q.toLowerCase();
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var node;
    while ((node = walker.nextNode())) {
      var idx = node.nodeValue.toLowerCase().indexOf(lower);
      if (idx >= 0) {
        var range = document.createRange();
        range.setStart(node, idx); range.setEnd(node, idx + q.length);
        var mk = document.createElement("mark"); mk.className = "hit";
        try { range.surroundContents(mk); mk.scrollIntoView({ block: "center" }); } catch (e) {}
        return;
      }
    }
  }

  // ---------- search ----------
  function navFilter(q) {
    var lower = q.toLowerCase();
    Array.prototype.forEach.call(elSidebar.querySelectorAll(".group"), function (g) {
      var any = false;
      Array.prototype.forEach.call(g.querySelectorAll(".nav-item"), function (b) {
        var hit = !q || b.textContent.toLowerCase().indexOf(lower) >= 0;
        b.classList.toggle("hidden", !hit);
        if (hit) any = true;
      });
      g.classList.toggle("hidden", !any);
    });
  }

  function cleanSnippet(text) {
    return text
      .replace(/```[\s\S]*?```/g, " ")
      .replace(/<\/?[a-zA-Z][^>]*>/g, " ")
      .replace(/&lt;\/?[a-zA-Z][^&]*?&gt;/g, " ")
      .replace(/&[a-z]+;/g, " ")
      .replace(/!?\[([^\]]*)\]\([^)]*\)/g, "$1")
      .replace(/\[[ xX]?\]/g, " ")
      .replace(/^[\s>#*\-+|]+/gm, " ")
      .replace(/[|#`*_~]/g, " ")
      .replace(/[-:]{2,}/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function fullTextSearch(q) {
    var lower = q.toLowerCase(), results = [];
    COURSE.sections.forEach(function (s) {
      var hay = s.md.toLowerCase(), idx = hay.indexOf(lower), count = 0, from = 0;
      while (idx >= 0) { count++; from = idx + lower.length; idx = hay.indexOf(lower, from); if (count > 99) break; }
      if (count > 0) {
        var first = hay.indexOf(lower);
        var snip = cleanSnippet(s.md.substring(Math.max(0, first - 40), first + 80));
        results.push({ id: s.id, title: s.title, group: s.group, count: count, snip: snip });
      }
    });
    results.sort(function (a, b) { return b.count - a.count; });

    elContent.innerHTML = '<div class="crumbs">检索 “' + escapeHtml(q) + '” · 命中 ' + results.length + ' 篇</div>' +
      '<div class="search-results" id="sr"></div>';
    var sr = document.getElementById("sr");
    if (!results.length) { sr.innerHTML = '<div class="empty">未找到相关内容</div>'; return; }
    results.forEach(function (r) {
      var b = document.createElement("button");
      b.className = "sr-item";
      b.innerHTML = '<div class="sr-title">' + escapeHtml(r.title) + ' · <small>' + escapeHtml(r.group) + ' · ' + r.count + ' 处</small></div>' +
        '<div class="sr-snip">…' + escapeHtml(r.snip) + '…</div>';
      b.addEventListener("click", function () { selectSection(r.id, q); });
      sr.appendChild(b);
    });
  }

  var searchTimer = null;
  if (elSearch) {
    elSearch.addEventListener("input", function () {
      var q = elSearch.value.trim();
      navFilter(q);
      clearTimeout(searchTimer);
    });
    elSearch.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        var q = elSearch.value.trim();
        if (q) fullTextSearch(q);
      }
    });
  }

  // ---------- print / export all ----------
  var btnPrint = document.getElementById("btn-print");
  if (btnPrint) {
    btnPrint.addEventListener("click", function () {
      var root = document.getElementById("print-root");
      if (!root.dataset.built) {
        var html = '<h1>' + escapeHtml(COURSE.title) + ' · 全方位复习</h1>';
        COURSE.sections.forEach(function (s) {
          html += '<article class="doc"><h1>' + escapeHtml(s.title) + '</h1>' + renderMarkdown(s.md) + '</article>';
        });
        root.innerHTML = html;
        runDynamic(root);
        root.dataset.built = "1";
        setTimeout(function () { window.print(); }, 600);
      } else {
        window.print();
      }
    });
  }

  // ---------- theme ----------
  var btnTheme = document.getElementById("btn-theme");
  function applyTheme(t) {
    document.documentElement.setAttribute("data-theme", t);
    try { localStorage.setItem("fuxi-theme", t); } catch (e) {}
    if (window.mermaid) {
      try { window.mermaid.initialize({ startOnLoad: false, theme: t === "dark" ? "dark" : "default", securityLevel: "loose" }); } catch (e) {}
    }
  }
  if (btnTheme) {
    btnTheme.addEventListener("click", function () {
      var cur = document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "light";
      applyTheme(cur === "dark" ? "light" : "dark");
      // 主题切换后重渲当前页(mermaid 颜色)
      if (currentId) selectSection(currentId);
    });
  }

  // ---------- mobile sidebar ----------
  var btnMenu = document.getElementById("btn-menu");
  var scrim = document.createElement("div");
  scrim.className = "scrim";
  document.body.appendChild(scrim);
  function closeSidebarMobile() { elSidebar.classList.remove("open"); scrim.classList.remove("show"); }
  if (btnMenu) btnMenu.addEventListener("click", function () {
    var open = elSidebar.classList.toggle("open");
    scrim.classList.toggle("show", open);
  });
  scrim.addEventListener("click", closeSidebarMobile);

  // ---------- init ----------
  var initTheme = "light";
  try { initTheme = localStorage.getItem("fuxi-theme") || "light"; } catch (e) {}
  if (window.mermaid) window.mermaid.initialize({ startOnLoad: false, theme: initTheme === "dark" ? "dark" : "default", securityLevel: "loose" });
  applyTheme(initTheme);

  buildNav();
  var hashId = decodeURIComponent((location.hash || "").replace(/^#/, ""));
  var startId = sectionsById[hashId] ? hashId : (COURSE.defaultSection || (COURSE.sections[0] && COURSE.sections[0].id));
  if (startId) selectSection(startId);
})();
