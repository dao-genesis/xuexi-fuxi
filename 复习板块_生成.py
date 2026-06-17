# -*- coding: utf-8 -*-
"""复习板块 · 通用复习站点生成器  ·  道法自然 · 无为而无不为

为每一门课程生成 **一个独立网址(单页)**，把该课的一切复习内容汇于一页：
  - 综合复习资料（图文 + 思维导图）
  - 各章素材（页索引 + 复习要点 + 思维导图）
  - 学习系统（备考总纲 / 自测题库 / 速记卡）
  - 期末冲刺（骨架 / 速查 / 模拟卷）
  - 知识图谱（章节图谱）
  - 原始课件 · PDF 原文（逐页 OCR 文字转录）

输出至 `docs/`（可直接部署为静态站点，公网任意环境浏览器内查看）：
  docs/index.html            课程总览
  docs/<slug>.html           每课一页（内容内嵌，自包含）
  docs/assets/...            共享样式 / 脚本 / 离线 JS 库（marked / mermaid / KaTeX）

用法：
  python 复习板块_生成.py            # 生成全部已识别课程
  python 复习板块_生成.py 流体力学    # 仅生成指定课程
"""
import os
import re
import io
import sys
import json
import glob
import hashlib

ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, "docs")

# 解析成果目录候选（新旧名兼容）
PARSE_DIR_CANDIDATES = ["02_解析成果", "03_解析成果", "04_解析成果"]
REVIEW_RESULT_DIRS = ["01_复习成果"]

# 课程登记：folder -> (slug, 显示名, emoji)
COURSE_REGISTRY = {
    "流体力学": ("fluid-mechanics", "流体力学", "💧"),
    "环境法学": ("environmental-law", "环境法学", "⚖️"),
    "环境监测学": ("environmental-monitoring", "环境监测学", "📡"),
    "环境毒理学": ("environmental-toxicology", "环境毒理学", "🧪"),
    "地理信息系统": ("gis", "地理信息系统 GIS", "🗺️"),
    "环境规划与管理": ("environmental-planning", "环境规划与管理", "🏙️"),
    "近代史纲要": ("modern-history", "中国近现代史纲要", "📜"),
    "环境科学概论": ("environmental-science", "环境科学概论", "🌍"),
    "有机化学": ("organic-chemistry", "有机化学", "⚗️"),
}


def read_text(path):
    with io.open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def write_text(path, text):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(text)


def slug_for(folder):
    if folder in COURSE_REGISTRY:
        return COURSE_REGISTRY[folder][0]
    return "c-" + hashlib.md5(folder.encode("utf-8")).hexdigest()[:8]


def title_for(folder):
    if folder in COURSE_REGISTRY:
        return COURSE_REGISTRY[folder][1]
    return folder


def emoji_for(folder):
    if folder in COURSE_REGISTRY:
        return COURSE_REGISTRY[folder][2]
    return "📘"


def find_parse_dir(course_path):
    for c in PARSE_DIR_CANDIDATES:
        p = os.path.join(course_path, c)
        if os.path.isdir(p):
            return p
    return None


def _chapter_num(name):
    m = re.search(r"第\s*0*(\d+)\s*章", name)
    return int(m.group(1)) if m else 999


def _clean_title(stem):
    t = stem.lstrip("_")
    t = t.replace("_", " ")
    return t.strip()


def collect_sections(course_path):
    """返回 (sections, meta)。sections: [{id, group, title, md}]"""
    sections = []
    meta = {"teacher": "", "term": "", "pdf": 0, "chapters": 0}

    def add(group, title, md, sid):
        if md and md.strip():
            sections.append({"id": sid, "group": group, "title": title, "md": md})

    # 1) 闭环总览
    overview = os.path.join(course_path, "00_闭环总览.md")
    if os.path.isfile(overview):
        add("导览", "闭环总览", read_text(overview), "overview")

    parse = find_parse_dir(course_path)

    # course meta
    if parse:
        cj = os.path.join(parse, "_course.json")
        if os.path.isfile(cj):
            try:
                d = json.loads(read_text(cj))
                meta["teacher"] = d.get("teacher", "") or meta["teacher"]
                meta["term"] = d.get("semester", "") or meta["term"]
                meta["pdf"] = d.get("pdf_count", 0) or len(d.get("documents", []) or [])
            except Exception:
                pass

    # 2) 复习资料：综合 / 最终 / 复习成果
    su = os.path.join(parse, "_素材") if parse else None
    added_comprehensive = False
    if su and os.path.isdir(su):
        for fn, title in [("_综合复习资料.md", "综合复习资料（图文 + 思维导图）"),
                          ("_最终复习资料.md", "最终复习资料")]:
            p = os.path.join(su, fn)
            if os.path.isfile(p):
                if fn == "_最终复习资料.md" and added_comprehensive:
                    continue
                md = read_text(p)
                add("复习资料", title, md, "review-" + fn.strip("_").replace(".md", ""))
                added_comprehensive = True
                # meta: teacher/term from header
                mt = re.search(r"教师?[:：]\s*([^\s·]+)", md)
                if mt and not meta["teacher"]:
                    meta["teacher"] = mt.group(1)
                mte = re.search(r"学期[:：]\s*([^\s·]+)", md)
                if mte and not meta["term"]:
                    meta["term"] = mte.group(1)
    # 复习成果目录（额外成品）
    for rd in REVIEW_RESULT_DIRS:
        rp = os.path.join(course_path, rd)
        if os.path.isdir(rp):
            for p in sorted(glob.glob(os.path.join(rp, "*.md"))):
                stem = os.path.splitext(os.path.basename(p))[0]
                add("复习资料", _clean_title(stem), read_text(p), "rr-" + slug_safe(stem))

    # 2.5) 例题精解 · 深化（手工深化层：核心例题/案例+详解+图示）
    # 兼容各课不同布局：优先 _素材，其次 解析成果根、复习成果目录、课程根
    deep_candidates = []
    if su:
        deep_candidates.append(su)
    if parse:
        deep_candidates.append(parse)
    for rd in REVIEW_RESULT_DIRS:
        deep_candidates.append(os.path.join(course_path, rd))
    deep_candidates.append(course_path)
    for base in deep_candidates:
        dd = os.path.join(base, "_例题精解.md")
        if os.path.isfile(dd):
            add("例题精解 · 深化", "核心例题 · 详解 · 图示", read_text(dd), "deepdive")
            break

    # 3) 章节素材
    if su and os.path.isdir(su):
        chap_files = [p for p in glob.glob(os.path.join(su, "_第*.md"))]
        chap_files.sort(key=lambda p: (_chapter_num(os.path.basename(p)), os.path.basename(p)))
        meta["chapters"] = len(chap_files)
        for p in chap_files:
            stem = os.path.splitext(os.path.basename(p))[0]
            add("章节素材", _clean_title(stem), read_text(p), "ch-" + slug_safe(stem))

    # 4) 期末冲刺
    if su and os.path.isdir(su):
        for fn, title in [("_期末骨架.md", "期末骨架"),
                          ("_期末速查.md", "期末速查"),
                          ("_期末模拟卷.md", "期末模拟卷")]:
            p = os.path.join(su, fn)
            if os.path.isfile(p):
                add("期末冲刺", title, read_text(p), "exam-" + fn.strip("_").replace(".md", ""))

    # 5) 学习系统
    if parse:
        ls = os.path.join(parse, "_学习系统")
        if os.path.isdir(ls):
            order = {"00_备考总纲": 0, "自测题库": 1, "速记卡": 2}
            files = sorted(glob.glob(os.path.join(ls, "*.md")),
                           key=lambda p: order.get(os.path.splitext(os.path.basename(p))[0], 9))
            for p in files:
                stem = os.path.splitext(os.path.basename(p))[0]
                add("学习系统", _clean_title(stem), read_text(p), "study-" + slug_safe(stem))

    # 6) 知识图谱
    if parse:
        g = os.path.join(parse, "_章节图谱.md")
        if os.path.isfile(g):
            add("知识图谱", "章节图谱", read_text(g), "graph")

    # 7) 原始课件 · PDF 原文
    if parse:
        full_texts = sorted(glob.glob(os.path.join(parse, "*", "_全文.md")))
        for p in full_texts:
            folder = os.path.basename(os.path.dirname(p))
            add("原始课件 · PDF原文", folder, read_text(p), "pdf-" + slug_safe(folder))

    # 8) 原始课件 · 页图（真实 PDF 页面渲染，按讲次折叠 + 懒加载）
    cfolder = os.path.basename(course_path.rstrip("/\\"))
    cslug = slug_for(cfolder)
    man = os.path.join(DOCS, "assets", "pdf", cslug, "manifest.json")
    if os.path.isfile(man):
        try:
            mf = json.loads(read_text(man))
        except Exception:
            mf = None
        if mf and mf.get("lessons"):
            add("原始课件 · 页图", "课件原文 · 逐页（真实截图）",
                build_gallery_md(cslug, mf), "pages")

    # 修复失效的 PDF 页图路径（旧 page_NNN.jpg → assets 下真实 Lxx_pPPP.jpg）。
    # 仅限「流体力学」：该课存在两套抽取（旧 page_NNN.jpg 与新 Lxx_pPPP.jpg）的编号错配，
    # 需按讲次重映射；其它课程素材已用正确路径，不可改写（否则会把多页折叠到同一页图）。
    if cslug in _REMAP_PDF_SLUGS:
        lesson_map = build_lesson_map(parse, cslug)
        if lesson_map:
            for s in sections:
                self_folder = s["title"] if s["group"] == u"原始课件 · PDF原文" else None
                s["md"] = fix_pdf_img_paths(s["md"], cslug, lesson_map, self_folder)

    # default section: 例题精解 > 综合复习资料 > 首节
    default = None
    for pref in ("deepdive", "review-"):
        for s in sections:
            if s["id"].startswith(pref):
                default = s["id"]
                break
        if default:
            break
    if not default and sections:
        default = sections[0]["id"]

    return sections, meta, default


def slug_safe(s):
    return re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-")[:40] or hashlib.md5(s.encode("utf-8")).hexdigest()[:8]


# 仅这些课程的素材存在旧/新两套 PDF 抽取编号错配，需在生成时重映射页图路径。
# 切勿对其它课程启用——它们素材已是正确的 assets 路径，重映射会破坏页图对应关系。
_REMAP_PDF_SLUGS = {u"fluid-mechanics"}

_CN_NUM = {u"一": 1, u"二": 2, u"三": 3, u"四": 4, u"五": 5,
           u"六": 6, u"七": 7, u"八": 8, u"九": 9, u"十": 10}


def _cn_chap(s):
    m = re.search(u"第\\s*([一二三四五六七八九十])\\s*章", s)
    return _CN_NUM.get(m.group(1)) if m else None


def _inst_num(s):
    m = re.search(u"（(\\d)）|\\((\\d)\\)", s)
    return int(m.group(1) or m.group(2)) if m else 1


def _norm_cn(s):
    return re.sub(u"[^\u4e00-\u9fff]", u"", s or u"")


def build_lesson_map(parse_dir, slug):
    """把「解析成果」各 PDF 子目录（旧编号 page_NNN.jpg）映射到 manifest 中的讲次资源
    （新编号 Lxx_pPPP.jpg）。按 章号 + 实例序号 + 页数 贪心唯一匹配，返回 {folder: pages_list}。
    无 manifest 或无匹配时返回 {}（对其它课程为无操作）。"""
    if not parse_dir:
        return {}
    man_path = os.path.join(DOCS, "assets", "pdf", slug, "manifest.json")
    if not os.path.isfile(man_path):
        return {}
    try:
        mf = json.loads(read_text(man_path))
    except Exception:
        return {}
    lessons = []
    for ls in mf.get("lessons", []):
        pages = ls.get("pages", [])
        if not pages:
            continue
        title = ls.get("title", "")
        lessons.append({"id": pages[0].split("_")[0], "pages": pages,
                        "cnt": len(pages), "chap": _cn_chap(title),
                        "inst": _inst_num(title), "norm": _norm_cn(title)})
    if not lessons:
        return {}
    folders = []
    for d in sorted(os.listdir(parse_dir)):
        ft = os.path.join(parse_dir, d, "_全文.md")
        if not os.path.isfile(ft):
            continue
        nums = [int(x) for x in re.findall(r"page_(\d+)\.jpg", read_text(ft))]
        folders.append({"d": d, "mx": max(nums) if nums else 0,
                        "chap": _cn_chap(d), "inst": _inst_num(d), "norm": _norm_cn(d)})
    used = set()
    fmap = {}
    for f in sorted(folders, key=lambda x: -x["mx"]):
        cands = [L for L in lessons if L["chap"] == f["chap"]]
        if not cands:
            cands = [L for L in lessons
                     if f["norm"] and (f["norm"] in L["norm"] or L["norm"] in f["norm"])] or list(lessons)
        cands = sorted(cands, key=lambda L: (L["id"] in used, abs(L["cnt"] - f["mx"]), L["inst"] != f["inst"]))
        if cands:
            pick = cands[0]
            used.add(pick["id"])
            fmap[f["d"]] = pick["pages"]
    return fmap


def fix_pdf_img_paths(md, slug, fmap, self_folder=None):
    """把 md 内失效的 PDF 页图路径改写为 assets 下真实存在的页图。
    - `](../<folder>/page_NNN.jpg)`  → `](assets/pdf/<slug>/<Lxx>_pPPP.jpg)`
    - 仅当 self_folder 给定时，改写裸 `](page_NNN.jpg)`（原始课件·PDF原文分组）。
    页号按「位置」对齐并 clamp 到讲次页数，保证目标文件必然存在。"""
    if not md or not fmap:
        return md

    def _resolve(folder, n):
        pages = fmap.get(folder)
        if not pages:
            return None
        idx = min(max(n, 1), len(pages)) - 1
        return u"](assets/pdf/%s/%s)" % (slug, pages[idx])

    def _rel(m):
        r = _resolve(m.group(1), int(m.group(2)))
        return r if r else m.group(0)

    md = re.sub(r"\]\(\.\./([^/)]+)/page_(\d+)\.jpg\)", _rel, md)
    if self_folder and self_folder in fmap:
        def _bare(m):
            r = _resolve(self_folder, int(m.group(1)))
            return r if r else m.group(0)
        md = re.sub(r"\]\(page_(\d+)\.jpg\)", _bare, md)
    return md


def build_gallery_md(slug, mf):
    """由 manifest.json 生成「原始课件·页图」分组：按讲次折叠 + 懒加载缩略 + 点击看大图。"""
    out = [u"# 原始课件 · 页图（真实 PDF 页面）\n",
           u"> 下列为雨课堂课件原始页面渲染；大讲已均匀采样关键页。点击讲次标题展开，单击图片可看大图。\n"]
    for i, ls in enumerate(mf.get("lessons", []), 1):
        title = ls.get("title", u"讲次 %d" % i)
        pages = ls.get("pages", [])
        if not pages:
            continue
        out.append(u'<details class="pdf-lesson"%s>' % (u" open" if i == 1 else u""))
        out.append(u'<summary>%s · %d 页</summary>' % (esc_attr(title), len(pages)))
        out.append(u'<div class="pdf-gallery">')
        for fn in pages:
            src = u"assets/pdf/%s/%s" % (slug, fn)
            out.append(u'<a href="%s" target="_blank" rel="noopener"><img loading="lazy" src="%s" alt=""></a>' % (src, src))
        out.append(u'</div></details>')
    return u"\n".join(out)


COURSE_HTML = u"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · 全方位复习</title>
<link rel="stylesheet" href="assets/vendor/katex/katex.min.css">
<link rel="stylesheet" href="assets/styles.css">
</head>
<body>
<header class="topbar">
  <button class="btn menu-toggle" id="btn-menu" title="目录">☰</button>
  <div class="brand">
    <span class="title">{emoji} {title}</span>
    <span class="meta">{meta}</span>
  </div>
  <span class="spacer"></span>
  <div class="search">
    <span>🔍</span>
    <input id="search-input" type="search" placeholder="过滤目录 / 回车全文检索" autocomplete="off">
  </div>
  <button class="btn" id="btn-print" title="展开全部并打印 / 导出 PDF">导出</button>
  <button class="btn" id="btn-theme" title="切换暗色 / 亮色">◐</button>
  <a class="btn" href="index.html" title="返回全部课程">全部课程</a>
</header>
<div class="layout">
  <nav class="sidebar" id="sidebar"></nav>
  <main class="content" id="content"></main>
</div>
<div id="print-root"></div>
<script id="course-data" type="application/json">{data}</script>
<script src="assets/vendor/marked.min.js"></script>
<script src="assets/vendor/mermaid.min.js"></script>
<script src="assets/vendor/katex/katex.min.js"></script>
<script src="assets/app.js"></script>
</body>
</html>
"""

INDEX_HTML = u"""<!DOCTYPE html>
<html lang="zh-CN" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>复习板块 · 全方位复习站</title>
<link rel="stylesheet" href="assets/styles.css">
</head>
<body>
<header class="topbar">
  <div class="brand"><span class="title">📚 复习板块</span><span class="meta">通用 · 全方位复习 · 公网任意环境可查</span></div>
  <span class="spacer"></span>
  <button class="btn" id="btn-theme" title="切换暗色 / 亮色">◐</button>
</header>
<section class="hero">
  <h1>全方位复习站</h1>
  <p>每门课程一个网址 · 综合复习资料 / 各章素材 / 学习系统 / 期末冲刺 / 知识图谱 / 原始课件PDF原文，皆汇于一页。</p>
</section>
<section class="cards">
{cards}
</section>
<script>
(function(){{
  var t="light"; try{{t=localStorage.getItem("fuxi-theme")||"light";}}catch(e){{}}
  document.documentElement.setAttribute("data-theme",t);
  var b=document.getElementById("btn-theme");
  if(b)b.addEventListener("click",function(){{
    var c=document.documentElement.getAttribute("data-theme")==="dark"?"dark":"light";
    var n=c==="dark"?"light":"dark";
    document.documentElement.setAttribute("data-theme",n);
    try{{localStorage.setItem("fuxi-theme",n);}}catch(e){{}}
  }});
}})();
</script>
</body>
</html>
"""


def build_course(folder):
    course_path = os.path.join(ROOT, folder)
    if not os.path.isdir(course_path):
        return None
    sections, meta, default = collect_sections(course_path)
    if not sections:
        return None
    slug = slug_for(folder)
    title = title_for(folder)
    data = {
        "slug": slug, "title": title, "folder": folder,
        "meta": meta, "defaultSection": default, "sections": sections,
    }
    meta_str = " · ".join([x for x in [
        ("教师 " + meta["teacher"]) if meta.get("teacher") else "",
        meta.get("term", ""),
        ("%d 章" % meta["chapters"]) if meta.get("chapters") else "",
        ("%d 份课件" % meta["pdf"]) if meta.get("pdf") else "",
    ] if x])
    html = COURSE_HTML.format(
        title=esc_attr(title), emoji=emoji_for(folder), meta=esc_attr(meta_str),
        data=json.dumps(data, ensure_ascii=False).replace("</", "<\\/"),
    )
    write_text(os.path.join(DOCS, slug + ".html"), html)
    counts = {}
    for s in sections:
        counts[s["group"]] = counts.get(s["group"], 0) + 1
    return {"folder": folder, "slug": slug, "title": title, "emoji": emoji_for(folder),
            "meta": meta_str, "counts": counts, "n": len(sections)}


def esc_attr(s):
    return (s or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def build_index(built):
    cards = []
    order = ["导览", "复习资料", "例题精解 · 深化", "章节素材", "学习系统", "期末冲刺", "知识图谱", "原始课件 · 页图", "原始课件 · PDF原文"]
    for b in built:
        badges = "".join(
            '<span class="badge">%s·%d</span>' % (esc_attr(g), b["counts"][g])
            for g in order if g in b["counts"]
        )
        cards.append(
            '<a class="card" href="{slug}.html">'
            '<div class="emoji">{emoji}</div>'
            '<div class="ct">{title}</div>'
            '<div class="cm">{meta}</div>'
            '<div class="badges">{badges}</div>'
            '</a>'.format(slug=b["slug"], emoji=b["emoji"], title=esc_attr(b["title"]),
                          meta=esc_attr(b["meta"] or "全方位复习"), badges=badges)
        )
    write_text(os.path.join(DOCS, "index.html"), INDEX_HTML.format(cards="\n".join(cards)))


def discover_courses():
    found = []
    for name in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, name)
        if not os.path.isdir(p):
            continue
        if name.startswith(".") or name.startswith("_") or name in ("docs", "yuketang", "解析仓库"):
            continue
        if find_parse_dir(p) or os.path.isfile(os.path.join(p, "00_闭环总览.md")):
            found.append(name)
    return found


def main():
    args = sys.argv[1:]
    courses = args if args else discover_courses()
    built = []
    for c in courses:
        info = build_course(c)
        if info:
            built.append(info)
            print(u"[成] %-12s -> docs/%s.html  (%d 篇)" % (c, info["slug"], info["n"]))
        else:
            print(u"[空] %-12s  无可用内容，跳过" % c)
    # index 按内容篇数排序
    built.sort(key=lambda b: -b["n"])
    build_index(built)
    print(u"[索] docs/index.html  (%d 门课程)" % len(built))


if __name__ == "__main__":
    main()
