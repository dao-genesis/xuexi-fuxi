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

# GitHub Pages 部署根地址（用于 README 首页在线网址一览）。
PAGES_BASE = "https://zhouyoukang1234-spec.github.io/xuexi-fuxi"

# 实验上机分组名（实验课与理论课融为一体：同一课页内，章节精讲之后即为上机实验精讲）。
LAB_GROUP = u"实验精讲 · 上机"
_LAB_CN = {0: u"导览", 1: u"一", 2: u"二", 3: u"三", 4: u"四", 5: u"五",
           6: u"六", 7: u"七", 8: u"八", 9: u"九", 10: u"十"}


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


def _lab_title(stem):
    """由 `_实验_NN_标题` 文件名派生显示标题：实验_03_矢量数据编辑与处理 → 实验三 · 矢量数据编辑与处理。"""
    s = stem.lstrip(u"_")
    m = re.match(u"实验_0*(\\d+)_(.+)$", s)
    if m:
        n = int(m.group(1))
        rest = m.group(2).replace(u"_", u" ").strip()
        if n == 0:
            return u"实验导览 · " + rest
        return u"实验%s · %s" % (_LAB_CN.get(n, str(n)), rest)
    return _clean_title(stem)


def _web_res_title(stem):
    """由 `_网络资源_NN_标题` 文件名派生显示标题：去前缀与序号，下划线转空格。"""
    t = stem.lstrip("_")
    t = re.sub(r"^网络资源[_\-]?\d*[_\-]?", "", t)
    t = t.replace("_", " ").strip()
    return t or stem.lstrip("_")


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

    # 2.6) 网络资源 · 真题/考点专集（联网调研汇编：真题题型、高频考点、名词解释速查、院校专集）
    # 文件命名 `_素材/_网络资源_NN_*.md`；为全部课程通用，离线汇编、与生成器同源、可查可搜。
    if su and os.path.isdir(su):
        for p in sorted(glob.glob(os.path.join(su, "_网络资源_*.md"))):
            stem = os.path.splitext(os.path.basename(p))[0]
            add("真题与网络资源", _web_res_title(stem), read_text(p), "web-" + slug_safe(stem))

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

    # 3.5) 实验上机素材（实验课 ↔ 理论课融为一体）：`_素材/_实验_NN_*.md`，按序号排序。
    # 仅 GIS 等含实验的课程存在此类文件；其它课程无此文件，自动跳过（无操作）。
    if su and os.path.isdir(su):
        lab_files = sorted(glob.glob(os.path.join(su, "_实验_*.md")),
                           key=lambda p: os.path.basename(p))
        for p in lab_files:
            stem = os.path.splitext(os.path.basename(p))[0]
            add(LAB_GROUP, _lab_title(stem), read_text(p), "lab-" + slug_safe(stem))

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

    # 章节为主线重组（仅启用课程）：把分散小节合并为「每章一节」+ 少量总览。
    if cslug in _CHAPTER_CENTRIC_SLUGS:
        new_sections, ch_default, ch_count = chapterize(sections, cslug)
        if new_sections:
            sections = new_sections
            if ch_count:
                meta["chapters"] = ch_count
            return sections, meta, ch_default

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


# ============================================================================
# 章节为主线（chapter-centric）重组 —— 仅对 _CHAPTER_CENTRIC_SLUGS 内课程启用。
# 把原本分散在「章节素材 / 例题精解 / 自测题库 / 速记卡 / 页图」里的同章内容，
# 合并为「每章一节」：知识精讲（图文）→ 核心PDF原页+例题详解 → 自测练习 → 速记知识点
# → 本章课件原页全图。其余内容收敛为少量「总览」板块。导航由此从数十项精简到十余项。
# ============================================================================
_CHAPTER_CENTRIC_SLUGS = {u"fluid-mechanics", u"gis", u"environmental-toxicology",
                         u"environmental-law", u"environmental-planning"}

# 流体力学章名为人工校订版（素材 H1 已规范，此处作为权威覆盖）；
# 其余课程章名在 chapterize 内由素材 H1 / 文件名自动派生（_name_from_material）。
CHAPTER_NAMES_BY_SLUG = {
    u"fluid-mechanics": {
        1: u"流体及其主要物性",
        2: u"流体静力学",
        3: u"流体运动基础",
        4: u"流体动力学基础",
        5: u"层流、紊流及其能量损失",
        6: u"孔口、管嘴流动与有压管流",
        7: u"明渠流动",
    },
    u"gis": {
        1: u"地理信息系统概论",
        2: u"空间数据（模型与结构）",
        3: u"空间数据的转换与处理",
        4: u"空间数据的可视化表达",
    },
    u"environmental-toxicology": {
        1: u"绪论与基本概念",
        2: u"污染物在环境（机体）中的迁移与转化",
        3: u"毒作用及其机制",
        4: u"毒作用的影响因素",
        5: u"环境毒理学常用实验方法",
        6: u"环境化学物的安全性与健康危险度评价",
        7: u"常见化学致癌物的环境毒理学",
    },
    u"environmental-law": {
        1: u"环境法学概述",
        2: u"环境保护法的基本原则",
        3: u"环境权利、义务的主体及其权利义务",
        4: u"国家的环境保护职责",
        5: u"环境基本法与综合性环境法律制度",
        6: u"污染控制法",
    },
    u"environmental-planning": {
        2: u"绪论 · 环境规划与管理",
        4: u"环境规划与管理的综合分析方法",
        5: u"环境规划的基本内容和程序",
        6: u"环境规划（要素规划）",
        7: u"环境管理模式",
    },
}

# 讲次→章 的「关键词映射」：用于课件标题不含「第N章」、但含章名/主题词的课程
# （如环境法学标题为章名、环境规划绪论无章号、GIS 为主题录播）。
# _lesson_chap 先按「第N章」识别，再回退到此关键词表，实现各章课件原页的可靠归并。
_LESSON_CHAP_KW = {
    u"environmental-law": {
        1: [u"开学第一课", u"绪论", u"概述"],
        2: [u"基本原则"],
        3: [u"环境利用行为的主体", u"权利义务"],
        4: [u"国家的环境保护义务", u"国家的环境保护职责"],
        5: [u"环境基本法", u"综合性环境法律"],
        6: [u"污染控制法", u"环境损害救济"],
    },
    u"environmental-planning": {
        2: [u"绪论", u"政策方针法律法规", u"第二三章"],
    },
    u"gis": {
        1: [u"地理信息系统 Geographic", u"概论"],
        2: [u"空间数据"],
    },
}


# 按讲次 ID 直接指定所属章（一讲可归多章）：用于源录播按主题而非按教材章节录制的课程。
# GIS 录播仅「概论 / 空间数据」两主题，而教材第2~4章均为「空间数据」子主题，故拆分归并。
_LESSON_ID_CHAP = {
    u"gis": {u"L03": [1], u"L04": [1], u"L01": [2, 3], u"L02": [2, 4]},
}


def _lesson_chap(slug, title):
    """识别课件讲次所属章：先按「第N章」，再回退按章名关键词匹配。"""
    c = _cn_chap(title)
    if c:
        return c
    for n, kws in _LESSON_CHAP_KW.get(slug, {}).items():
        for kw in kws:
            if kw in title:
                return n
    return None


def _lesson_in_chap(slug, ls, chap):
    idmap = _LESSON_ID_CHAP.get(slug)
    if idmap is not None:
        lid = ls.get("pages", [u"_"])[0].split(u"_")[0]
        return chap in idmap.get(lid, [])
    return _lesson_chap(slug, ls.get("title", "")) == chap


def _chapter_pages(slug, mf, chap, k=6):
    """取该章对应讲次的页图文件名，等距抽取至多 k 张作为「核心原页」内嵌图文。"""
    allp = []
    for ls in mf.get("lessons", []):
        if _lesson_in_chap(slug, ls, chap):
            allp.extend(ls.get("pages", []))
    if not allp:
        return []
    if len(allp) <= k:
        return allp
    step = len(allp) / float(k)
    return [allp[int(i * step)] for i in range(k)]


def _inline_pages_md(slug, pages):
    """把若干核心原页渲染为可点击放大的横向图文条（内嵌于「图文精讲」块顶部）。"""
    if not pages:
        return u""
    cells = []
    for fn in pages:
        src = u"assets/pdf/%s/%s" % (slug, fn)
        cells.append(u'<a href="%s" target="_blank" rel="noopener">'
                     u'<img loading="lazy" src="%s" alt=""></a>' % (src, src))
    return (u"### 本章核心课件原页（点击看大图）\n\n"
            u'<div class="pdf-gallery">\n%s\n</div>\n' % u"\n".join(cells))


def _safe_mindmap_label(name):
    """清洗章名用于 mermaid mindmap 根节点（去除会破坏语法的括号/斜杠等）。"""
    return re.sub(u"[()（）/\\\\\\[\\]]", u" ", name).strip()


def _name_from_material(md, fname):
    """从素材 H1（形如「课名 · 第N章 · 章名 · 素材」）或文件名派生章名。"""
    for ln in md.splitlines():
        if ln.startswith(u"#"):
            m = re.search(u"第\\s*0*\\d+\\s*章\\s*[·:：．.\\-—]*\\s*(.+)$", ln)
            if m:
                nm = re.split(u"[·|]", m.group(1))[0]
                nm = nm.replace(u"素材", u"").strip(u" ·-—|\u3000")
                if nm:
                    return nm
            break
    stem = os.path.splitext(os.path.basename(fname))[0].lstrip(u"_")
    stem = re.sub(u"^第\\s*0*\\d+\\s*章", u"", stem)
    stem = re.sub(u"[_\\s]+", u" ", stem).strip()
    return stem or None


def _strip_broken_imgs(md):
    """删除指向非 assets/、非 http 的失效图片引用（如 ../课夹/page_NNN.jpg、图全副本）。
    仅删图片标记，正文保留；assets 下真实页图与外链图片不受影响。"""
    def rep(m):
        tgt = m.group(1).strip()
        if tgt.startswith(u"assets/") or tgt.startswith(u"http") or tgt.startswith(u"data:"):
            return m.group(0)
        return u""
    return re.sub(r"!\[[^\]]*\]\(([^)]*)\)", rep, md)


def _strip_details_markmap(md):
    """去掉 <details>…</details> 折叠块（页索引 / 逐页OCR文字对照）与 markmap 代码块，
    保留正文（思维导图 mermaid 与「复习要点」等 LLM 文本）。"""
    md = re.sub(r"<details[\s\S]*?</details>", u"", md, flags=re.I)
    md = re.sub(r"```markmap[\s\S]*?```", u"", md)
    return md


def _first_mermaid(md):
    m = re.search(r"```mermaid[\s\S]*?```", md)
    return m.group(0) if m else u""


def _section_body(md, head_kw):
    """截取「标题行含 head_kw」起、到下一个同级或更高级标题前的正文（含该标题）。"""
    lines = md.splitlines()
    start = None
    level = 0
    for i, ln in enumerate(lines):
        hm = re.match(r"(#{1,6})\s+(.*)$", ln)
        if hm and head_kw in hm.group(2):
            start = i
            level = len(hm.group(1))
            break
    if start is None:
        return u""
    out = [lines[start]]
    for ln in lines[start + 1:]:
        hm = re.match(r"(#{1,6})\s+", ln)
        if hm and len(hm.group(1)) <= level:
            break
        out.append(ln)
    return u"\n".join(out)


def _demote(md, by=1):
    """ATX 标题整体降级 by 级（# → ##），封顶 ######，使其嵌入到上层小节之下。"""
    def rep(m):
        return u"#" * min(len(m.group(1)) + by, 6) + u" "
    return re.sub(r"(?m)^(#{1,6})\s+", rep, md)


def _split_h2_chapters(md):
    """按 `## 第N章 …` 切分单文件，返回 {章号: 该章正文(不含标题行)}。"""
    out = {}
    parts = re.split(r"(?m)^##\s+第\s*0*(\d+)\s*章[^\n]*\n", md or u"")
    for i in range(1, len(parts), 2):
        try:
            n = int(parts[i])
        except (ValueError, IndexError):
            continue
        out[n] = parts[i + 1] if i + 1 < len(parts) else u""
    return out


def _chapter_gallery(slug, mf, chap):
    """该章对应讲次的课件原页（仅图片、无 OCR 文字），折叠展示。"""
    rows = []
    for ls in mf.get("lessons", []):
        if not _lesson_in_chap(slug, ls, chap):
            continue
        for fn in ls.get("pages", []):
            src = u"assets/pdf/%s/%s" % (slug, fn)
            rows.append(u'<a href="%s" target="_blank" rel="noopener">'
                        u'<img loading="lazy" src="%s" alt=""></a>' % (src, src))
    if not rows:
        return u""
    return (u'<details class="pdf-lesson">\n'
            u'<summary>本章课件原页 · 共 %d 页（点击展开）</summary>\n'
            u'<div class="pdf-gallery">\n%s\n</div></details>' % (len(rows), u"\n".join(rows)))


def chapterize(sections, slug):
    """把分散小节重组为「章节为主线」。返回 (new_sections, default_id, chapter_count)。"""
    man = os.path.join(DOCS, "assets", "pdf", slug, "manifest.json")
    mf = {}
    if os.path.isfile(man):
        try:
            mf = json.loads(read_text(man))
        except Exception:
            mf = {}

    by_group = {}
    for s in sections:
        by_group.setdefault(s["group"], []).append(s)

    materials = {}
    mat_names = {}
    _mscore = {}
    for s in by_group.get(u"章节素材", []):
        n = _chapter_num(s["title"])
        if n == 999:
            continue
        md = s["md"]
        # 同一章多份素材时：优先含「复习要点」者，其次取更长者；
        # 如此可跳过「_图全 / _核心复习」等纯图或精简副本，取到带知识精讲的主素材。
        score = (1 if u"复习要点" in md else 0, len(md))
        if score > _mscore.get(n, (-1, -1)):
            _mscore[n] = score
            materials[n] = md
            mat_names[n] = _name_from_material(md, s["title"])
    deepdive = next((s["md"] for s in sections if s["id"] == "deepdive"), u"")
    dd_ch = _split_h2_chapters(deepdive)
    quiz = cards = u""
    for s in by_group.get(u"学习系统", []):
        if u"自测" in s["title"]:
            quiz = s["md"]
        elif u"速记" in s["title"]:
            cards = s["md"]
    quiz_ch = _split_h2_chapters(quiz)
    card_ch = _split_h2_chapters(cards)

    _CN = u"〇一二三四五六七八九十"
    fluid_names = CHAPTER_NAMES_BY_SLUG.get(slug, {})
    chaps = sorted(set(list(materials.keys()) + list(dd_ch.keys())))
    new = []
    for n in chaps:
        name = fluid_names.get(n) or mat_names.get(n) or (u"第%d章" % n)
        P = [u"# 第%d章 · %s" % (n, name), u"",
             u"> 一章打通 ▸ 知识精讲（图文）· 例题详解 · 自测练习 · 速记知识点 · 课件原页全图", u""]
        # 收集本章各组成部分，最后按存在者顺序编号（避免出现 二→五 的跳号）。
        blocks = []
        if n in materials:
            mat = _strip_details_markmap(materials[n])
            rp = _section_body(mat, u"复习要点")
            body = _strip_broken_imgs(_demote(rp if rp else mat, 1))
            mer = _first_mermaid(mat)
            if mer:
                if slug != u"fluid-mechanics":
                    mer = re.sub(r"root\(\(.*?\)\)",
                                 u"root((第%d章<br/>%s))" % (n, _safe_mindmap_label(name)),
                                 mer, count=1, flags=re.S)
                body += u"\n\n### 本章知识结构图\n\n" + mer
            blocks.append((u"知识精讲 · 核心概念 / 公式 / 考点", body))
        # 流体力学已人工图文精解（原页内嵌于解析旁），不再叠加自动原页条，保持原样。
        inline = (_inline_pages_md(slug, _chapter_pages(slug, mf, n))
                  if (mf and slug != u"fluid-mechanics") else u"")
        if n in dd_ch:
            dd = _strip_broken_imgs(_demote(dd_ch[n], 1))
            blocks.append((u"核心 PDF 原页 · 图文精讲 + 例题详解", (inline + u"\n" + dd) if inline else dd))
        elif inline:
            blocks.append((u"核心 PDF 原页 · 图文精讲", inline))
        if n in quiz_ch:
            blocks.append((u"自测题 · 练习", _strip_broken_imgs(_demote(quiz_ch[n], 1))))
        if n in card_ch:
            blocks.append((u"速记卡 · 知识点速查", _strip_broken_imgs(_demote(card_ch[n], 1))))
        gal = _chapter_gallery(slug, mf, n) if mf else u""
        if gal:
            blocks.append((u"本章课件原页 · 全图", gal))
        for idx, (label, body) in enumerate(blocks, 1):
            P.append(u"## %s、%s" % (_CN[idx] if idx < len(_CN) else str(idx), label))
            P.append(body)
        new.append({"id": "chap-%d" % n, "group": u"章节精讲",
                    "title": u"第%d章 · %s" % (n, name), "md": u"\n\n".join(P)})

    # 实验上机精讲：紧随章节精讲之后，实验课与理论课融为一体（内容已为成稿，原样保留）。
    for s in by_group.get(LAB_GROUP, []):
        new.append({"id": s["id"], "group": LAB_GROUP, "title": s["title"], "md": s["md"]})

    # 总览板块（少量）：综合复习资料 / 知识图谱 / 备考总纲 → 总览资料；期末冲刺；全部课件原页
    for s in by_group.get(u"复习资料", []):
        new.append({"id": s["id"], "group": u"总览资料", "title": s["title"], "md": s["md"]})
    for s in by_group.get(u"知识图谱", []):
        new.append({"id": s["id"], "group": u"总览资料", "title": u"知识图谱 · " + s["title"], "md": s["md"]})
    for s in by_group.get(u"学习系统", []):
        if u"备考" in s["title"]:
            new.append({"id": s["id"], "group": u"总览资料", "title": s["title"], "md": s["md"]})
    for s in by_group.get(u"真题与网络资源", []):
        new.append({"id": s["id"], "group": u"真题与网络资源", "title": s["title"], "md": s["md"]})
    for s in by_group.get(u"期末冲刺", []):
        new.append({"id": s["id"], "group": u"期末冲刺", "title": s["title"], "md": s["md"]})
    for s in by_group.get(u"原始课件 · 页图", []):
        new.append({"id": s["id"], "group": u"原始课件", "title": u"全部课件原页 · 逐讲", "md": s["md"]})
    # 丢弃：导览（闭环总览）、原始课件·PDF原文（逐页OCR乱码，已被页图/各章原页取代）

    default = ("chap-%d" % chaps[0]) if chaps else (new[0]["id"] if new else None)
    return new, default, len(chaps)


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
    order = ["章节精讲", "总览资料", "真题与网络资源", "期末冲刺", "原始课件", "导览", "复习资料", "例题精解 · 深化", "章节素材", "学习系统", "知识图谱", "原始课件 · 页图", "原始课件 · PDF原文"]
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


_README_ORDER = ["章节精讲", "总览资料", "真题与网络资源", "期末冲刺", "原始课件", "导览", "复习资料", "例题精解 · 深化", "章节素材", "学习系统", "知识图谱", "原始课件 · 页图", "原始课件 · PDF原文"]


def build_readme(built):
    """生成仓库主页 README.md：首页一览所有学科的在线复习网址。
    由本生成器产出，与 docs/index.html 同源、自动同步。"""
    L = []
    L.append(u"# 📚 复习板块 · 全方位复习站")
    L.append(u"")
    L.append(u"> 道生一，一生二，二生三，三生万物。")
    L.append(u"> 从课程原始 PDF 出发，经「抽取 → 聚合 → 素材 → LLM 精炼 → 编译 → 思维导图 → 期末资料」流水线，")
    L.append(u"> 生成可在**公网任意浏览器**直接查看的复习页：综合复习资料 / 章节素材 / 学习系统 / 期末冲刺 / 知识图谱 / 原始课件 PDF 原文，皆汇于一页。")
    L.append(u"")
    L.append(u"## 🌐 在线复习网址（一览）")
    L.append(u"")
    L.append(u"**📖 总览首页**：%s/" % PAGES_BASE)
    L.append(u"")
    L.append(u"| 学科 | 任课 / 进度 | 在线复习页 |")
    L.append(u"| --- | --- | --- |")
    for b in built:
        url = u"%s/%s.html" % (PAGES_BASE, b["slug"])
        L.append(u"| %s **%s** | %s | [📖 打开复习页](%s) |"
                 % (b["emoji"], b["title"], b["meta"] or u"全方位复习", url))
    L.append(u"")
    L.append(u"## 🧩 各科内容模块")
    L.append(u"")
    for b in built:
        mods = u" ｜ ".join(u"%s×%d" % (g, b["counts"][g]) for g in _README_ORDER if g in b["counts"])
        L.append(u"- %s **%s** — %s" % (b["emoji"], b["title"], mods))
    L.append(u"")
    L.append(u"## 🛠️ 生成 / 更新")
    L.append(u"")
    L.append(u"```bash")
    L.append(u"python 复习板块_生成.py            # 生成全部课程 → docs/")
    L.append(u"python 复习板块_生成.py 流体力学   # 仅生成指定课程")
    L.append(u"```")
    L.append(u"")
    L.append(u"产物输出至 `docs/`（`index.html` 总览 + `<slug>.html` 每课一页，自包含、可直接部署为 GitHub Pages 静态站点）。")
    L.append(u"工程约定与流水线细节见 [`AGENTS.md`](AGENTS.md)。")
    L.append(u"")
    L.append(u"---")
    L.append(u"> 本文件由 `复习板块_生成.py` 自动生成（与 `docs/index.html` 同源），请勿手改；如需调整请改生成器后重新生成。")
    L.append(u"")
    write_text(os.path.join(ROOT, "README.md"), u"\n".join(L))


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
    build_readme(built)
    print(u"[页] README.md  (%d 门课程在线网址一览)" % len(built))


if __name__ == "__main__":
    main()
