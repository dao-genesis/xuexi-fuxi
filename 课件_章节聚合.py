# -*- coding: utf-8 -*-
"""
课件 章节聚合 (chapter_aggregator)  ——  其未兆也，易谋也

道法：
    雨课堂之 PPT 多有重复——同章多版本、跨章合一节，散乱难寻。
    此关之事：以 _doc.json 之章节信号为线，按章节归一，
    辨主辅版本，识跨章节、识杂项，
    成 _章节图谱.json (机读) 与 _章节图谱.md (人读)。

依赖:
    pip install pymupdf pillow

用法:
    python 课件_章节聚合.py                     # 处理全部解析仓库
    python 课件_章节聚合.py -f 环境毒理         # 仅某课
    python 课件_章节聚合.py --repo 解析仓库     # 自定输入

输出:
    解析仓库/<课程>/_章节图谱.json
    解析仓库/<课程>/_章节图谱.md
    解析仓库/_全局图谱.md (各课总览)
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# 共用之器
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _yc_common import (  # noqa: E402
    log,
    header,
    write_json,
    read_json,
    parse_course_dirname,
)


# ============================================================
# 非教学性课件识别（开学第一课、思政、培训等）
# ============================================================

# 标题含此关键字 + 无章节信号 → 视为"非教学/装饰"
_NON_LECTURE_KEYWORDS = (
    "青春逐梦", "开学第一课", "国之重器", "新征程",
    "课程介绍", "课程说明", "教学内容说明", "教学大纲",
    "学习指南", "思政", "培训", "考试说明",
)


def is_non_lecture(doc: dict) -> bool:
    """是否为非教学性内容（开学第一课/思政/培训说明等）。"""
    if doc.get("all_chapter_nums"):
        return False
    title = (doc.get("lesson_title", "") + " " + doc.get("presentation_title", ""))
    return any(kw in title for kw in _NON_LECTURE_KEYWORDS)


# ============================================================
# 章节标题清洗 / 推断
# ============================================================

# 去除"第X章" "X-第X章" 等前缀
_CH_PREFIX_PAT = re.compile(
    r"^[\s\d\-_]*第\s*[一二三四五六七八九十百零〇○0-9]{1,4}\s*[章编篇单元部分讲节]\s*[:：．\.\-_]*"
)
_CHN_PREFIX_PAT = re.compile(
    r"^[\s\d\-_]*(?:Chapter|Unit|Part|Lecture)\s*\d{1,3}\s*[:：．\.\-_]*",
    re.IGNORECASE,
)


_VERSION_TAIL_PAT = re.compile(r"[（(]\s*\d+\s*[）)]\s*$")
_HAN_PAT = re.compile(r"[\u4e00-\u9fa5]{2,}")


def strip_chapter_prefix(title: str) -> str:
    """去除标题前的章节编号前缀，留下纯章名。"""
    if not title:
        return ""
    s = title.strip()
    s = _CH_PREFIX_PAT.sub("", s).strip()
    s = _CHN_PREFIX_PAT.sub("", s).strip()
    # 节号·句点格式（如 "2.环境保护法..."、"3. 环境利用..." → 去 "2." / "3. "）
    s = re.sub(r"^\d{1,2}\s*[.．、]\s*", "", s).strip()
    # 再去前置数字 + 横线（如 "3环境毒理学" 中的 "3"）
    s = re.sub(r"^\d{1,2}[\-_\s]*", "", s).strip()
    # 去掉尾部"（2）"这种版本编号
    s = _VERSION_TAIL_PAT.sub("", s).strip()
    # 再去残余之 ". "（章名以点起者）
    s = re.sub(r"^[.．、]\s*", "", s).strip()
    return s


def _is_meaningful_title(s: str) -> bool:
    """判断标题是否有意义（至少含 2 个连续汉字 或 长度 ≥ 4 含字母）。"""
    if not s or len(s) > 80:
        return False
    if _HAN_PAT.search(s):
        return True
    if len(s) >= 4 and re.search(r"[A-Za-z]{3,}", s):
        return True
    return False


def infer_chapter_title(docs: list[dict], chap_num: int) -> str:
    """从该章下所有文档中，推断章节标题（众数 / 最长有效）。"""
    candidates: list[str] = []
    for d in docs:
        for src in (d.get("presentation_title", ""), d.get("lesson_title", "")):
            # 只从含本章号的文本中取（避免跨章污染）
            for pat in [
                rf"第\s*{chap_num}\s*[章编篇单元部分讲节]",
                rf"第\s*{_int_to_cn(chap_num)}\s*[章编篇单元部分讲节]",
                rf"\bChapter\s*{chap_num}\b",
                rf"\bUnit\s*{chap_num}\b",
                # 节号·句点格式（兜底）：'2.环境保护法...'
                rf"^\s*{chap_num}\s*[.．、]\s*",
            ]:
                m = re.search(pat, src, re.IGNORECASE)
                if not m:
                    continue
                tail = src[m.end():].strip(" :：—-_·.")
                # 截到下一个章节信号前
                next_m = re.search(
                    r"第\s*[一二三四五六七八九十百零〇○0-9]{1,4}\s*[章编篇单元部分讲节]",
                    tail,
                )
                if next_m:
                    tail = tail[:next_m.start()].strip(" :：—-_·")
                # 去尾部版本编号 "（2）"
                tail = _VERSION_TAIL_PAT.sub("", tail).strip(" :：—-_·")
                if _is_meaningful_title(tail):
                    candidates.append(tail)
                break
    if candidates:
        return Counter(candidates).most_common(1)[0][0]
    # 兜底：从清洗后之 presentation_title / lesson_title 找有意义者
    cleaned = []
    for d in docs:
        for src in (d.get("presentation_title", ""), d.get("lesson_title", "")):
            c = strip_chapter_prefix(src)
            if _is_meaningful_title(c):
                cleaned.append(c)
    if cleaned:
        return Counter(cleaned).most_common(1)[0][0]
    return ""


_CN_DIGITS_REV = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]


def _int_to_cn(n: int) -> str:
    """阿拉伯数字 → 中文（仅章节用，<=99）"""
    if n < 0 or n > 99:
        return str(n)
    if n < 10:
        return _CN_DIGITS_REV[n]
    if n == 10:
        return "十"
    if n < 20:
        return "十" + _CN_DIGITS_REV[n - 10]
    tens, ones = divmod(n, 10)
    return _CN_DIGITS_REV[tens] + "十" + (_CN_DIGITS_REV[ones] if ones else "")


# ============================================================
# 章节聚合主逻辑
# ============================================================

def aggregate_course(course_dir_path: Path) -> dict | None:
    """聚合一门课程之章节图谱。"""
    course_json = course_dir_path / "_course.json"
    if not course_json.exists():
        return None

    cm = read_json(course_json)
    if not cm:
        return None

    documents = cm.get("documents", [])
    if not documents:
        return {
            "course_dir": cm.get("course_dir"),
            "course_name": cm.get("course_name"),
            "semester": cm.get("semester"),
            "teacher": cm.get("teacher"),
            "chapter_count": 0,
            "chapters": [],
            "non_lecture": [],
            "uncategorized": [],
        }

    # 分组：每文档可归多章
    chapter_to_docs: dict[int, list[dict]] = defaultdict(list)
    non_lecture: list[dict] = []
    uncategorized: list[dict] = []

    for doc in documents:
        all_chs = doc.get("all_chapter_nums") or []
        if not all_chs:
            if is_non_lecture(doc):
                non_lecture.append(doc)
            else:
                uncategorized.append(doc)
            continue
        for ch in all_chs:
            chapter_to_docs[ch].append(doc)

    # 每章内：选主版（页数最多者），其余为辅版
    chapters: list[dict] = []
    for ch_num in sorted(chapter_to_docs.keys()):
        ch_docs = chapter_to_docs[ch_num]
        # 排序：先按 lesson_seq，再按 page_count 倒序（页多者为主）
        ch_docs_sorted = sorted(
            ch_docs,
            key=lambda d: (d.get("lesson_seq") or 999, -(d.get("page_count") or 0)),
        )
        # 选主版：page_count 最大者；并列时取 lesson_seq 最大（即最新一节课）
        primary = max(
            ch_docs,
            key=lambda d: (d.get("page_count") or 0, d.get("lesson_seq") or 0),
        )
        # 推断章名
        title = infer_chapter_title(ch_docs, ch_num)

        chapters.append({
            "chapter_num": ch_num,
            "chapter_title": title,
            "doc_count": len(ch_docs),
            "total_pages": sum(d.get("page_count") or 0 for d in ch_docs),
            "primary": {
                "rel_dir": primary.get("rel_dir"),
                "pdf_name": primary.get("pdf_name"),
                "lesson_seq": primary.get("lesson_seq"),
                "page_count": primary.get("page_count"),
                "lesson_title": primary.get("lesson_title"),
                "presentation_title": primary.get("presentation_title"),
            },
            "all_docs": [
                {
                    "rel_dir": d.get("rel_dir"),
                    "pdf_name": d.get("pdf_name"),
                    "lesson_seq": d.get("lesson_seq"),
                    "page_count": d.get("page_count"),
                    "all_chapter_nums": d.get("all_chapter_nums") or [],
                    "is_primary": (d is primary),
                    "is_cross_chapter": len(d.get("all_chapter_nums") or []) > 1,
                }
                for d in ch_docs_sorted
            ],
        })

    chart = {
        "course_dir": cm.get("course_dir"),
        "course_name": cm.get("course_name"),
        "semester": cm.get("semester"),
        "teacher": cm.get("teacher"),
        "pdf_total": cm.get("pdf_count", 0),
        "page_total": sum(d.get("page_count") or 0 for d in documents),
        "chapter_count": len(chapters),
        "chapter_nums": [c["chapter_num"] for c in chapters],
        "chapters": chapters,
        "non_lecture": [
            {
                "rel_dir": d.get("rel_dir"),
                "pdf_name": d.get("pdf_name"),
                "lesson_seq": d.get("lesson_seq"),
                "page_count": d.get("page_count"),
                "lesson_title": d.get("lesson_title"),
            }
            for d in non_lecture
        ],
        "uncategorized": [
            {
                "rel_dir": d.get("rel_dir"),
                "pdf_name": d.get("pdf_name"),
                "lesson_seq": d.get("lesson_seq"),
                "page_count": d.get("page_count"),
                "lesson_title": d.get("lesson_title"),
                "presentation_title": d.get("presentation_title"),
            }
            for d in uncategorized
        ],
    }

    write_json(course_dir_path / "_章节图谱.json", chart)
    return chart


# ============================================================
# 章节图谱 → markdown
# ============================================================

def chart_to_markdown(chart: dict) -> str:
    lines: list[str] = []
    title = chart.get("course_name", "")
    teacher = chart.get("teacher", "")
    semester = chart.get("semester", "")

    lines.append(f"# {title} · 章节图谱")
    lines.append("")
    lines.append(f"> 教师: {teacher} · 学期: {semester}  ")
    lines.append(
        f"> PDF: {chart.get('pdf_total', 0)}, 页: {chart.get('page_total', 0)}, "
        f"识别章节: {len(chart.get('chapters', []))} 个"
    )
    chap_nums = chart.get("chapter_nums") or []
    if chap_nums:
        lines.append(f"> 章节号: {', '.join(map(str, chap_nums))}")
    lines.append("")

    # 总览表
    lines.append("## 总览")
    lines.append("")
    lines.append("| 章节 | 标题 | 主版页数 | PDF 数 |")
    lines.append("|------|------|---------:|------:|")
    for ch in chart.get("chapters", []):
        ch_n = ch["chapter_num"]
        ch_label = "绪论" if ch_n == 0 else f"第 {ch_n} 章"
        lines.append(
            f"| {ch_label} | {ch.get('chapter_title', '')} | "
            f"{ch['primary'].get('page_count', 0)} | {ch.get('doc_count', 0)} |"
        )
    if chart.get("non_lecture"):
        lines.append(f"| — | （非教学）{len(chart['non_lecture'])} 个 | — | — |")
    if chart.get("uncategorized"):
        lines.append(f"| — | （未归类）{len(chart['uncategorized'])} 个 | — | — |")
    lines.append("")

    # 各章详细
    lines.append("## 各章节详细")
    lines.append("")
    for ch in chart.get("chapters", []):
        ch_n = ch["chapter_num"]
        ch_label = "绪论 · 第 0 章" if ch_n == 0 else f"第 {ch_n} 章"
        ch_title = ch.get("chapter_title", "")
        lines.append(f"### {ch_label}" + (f" · {ch_title}" if ch_title else ""))
        lines.append("")
        for d in ch.get("all_docs", []):
            mark = "**主**" if d.get("is_primary") else "辅"
            cross = " · 跨章" if d.get("is_cross_chapter") else ""
            seq = d.get("lesson_seq")
            pages = d.get("page_count")
            rel = d.get("rel_dir") or ""
            pdf = d.get("pdf_name") or ""
            lines.append(
                f"- [{mark}] 第 {seq} 节 · {pages} 页{cross}  "
                f"`{rel}`"
            )
        lines.append("")

    # 非教学
    if chart.get("non_lecture"):
        lines.append("## 非教学性课件")
        lines.append("")
        for d in chart["non_lecture"]:
            lines.append(
                f"- 第 {d.get('lesson_seq')} 节 · {d.get('page_count')} 页 · "
                f"{d.get('lesson_title', '')}"
            )
        lines.append("")

    # 未归类
    if chart.get("uncategorized"):
        lines.append("## 未归类课件")
        lines.append("")
        for d in chart["uncategorized"]:
            lines.append(
                f"- 第 {d.get('lesson_seq')} 节 · {d.get('page_count')} 页 · "
                f"{d.get('lesson_title', '')} | {d.get('presentation_title', '')}"
            )
        lines.append("")

    return "\n".join(lines)


# ============================================================
# 全局图谱（多课总览）
# ============================================================

def global_overview_md(charts: list[dict]) -> str:
    lines: list[str] = []
    lines.append("# 解析仓库 · 全局图谱")
    lines.append("")
    lines.append(
        f"> 共 {len(charts)} 门有课件之课程，"
        f"PDF {sum(c.get('pdf_total', 0) for c in charts)}, "
        f"页 {sum(c.get('page_total', 0) for c in charts)}"
    )
    lines.append("")

    # 按页数倒序排
    charts_sorted = sorted(charts, key=lambda c: -(c.get("page_total") or 0))

    lines.append("| 课程 | 教师 | 学期 | PDF | 页 | 章节 |")
    lines.append("|------|------|------|----:|----:|------|")
    for c in charts_sorted:
        ch_nums = c.get("chapter_nums", []) or []
        ch_str = ",".join(map(str, ch_nums)) if ch_nums else "—"
        lines.append(
            f"| **{c.get('course_name', '')}** | {c.get('teacher', '')} | "
            f"{c.get('semester', '')} | {c.get('pdf_total', 0)} | "
            f"{c.get('page_total', 0)} | {ch_str} |"
        )
    lines.append("")

    # 各课图谱链接
    lines.append("## 各课图谱链接")
    lines.append("")
    for c in charts_sorted:
        cd = c.get("course_dir", "")
        nm = c.get("course_name", cd)
        lines.append(f"- [{nm}（{c.get('teacher', '')}）](./{cd}/_章节图谱.md)")
    lines.append("")

    return "\n".join(lines)


# ============================================================
# 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="课件 章节聚合 —— 按章节归一",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--repo", "-r", default="解析仓库",
        help="解析仓库目录（pdf_提文.py 之输出，默 ./解析仓库）",
    )
    parser.add_argument(
        "--filter", "-f", action="append", default=None,
        help="课程名关键字过滤",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    repo = Path(args.repo)
    if not repo.is_absolute():
        repo = script_dir / repo

    header("课件 章节聚合 —— 其未兆也，易谋也", width=58)
    log(f"  仓库: {repo}", "dim")

    if not repo.exists():
        log(f"× 仓库不存: {repo}", "err")
        sys.exit(1)

    # 收集所有课程
    courses = sorted([
        d for d in repo.iterdir()
        if d.is_dir() and (d / "_course.json").exists()
    ])
    if args.filter:
        courses = [c for c in courses if any(kw in c.name for kw in args.filter)]

    if not courses:
        log("∅ 无可处理之课程", "warn")
        return

    log(f"\n共 {len(courses)} 门课程", "info")

    charts = []
    for course in courses:
        info = parse_course_dirname(course.name)
        chart = aggregate_course(course)
        if not chart:
            log(f"  × 跳: {info['course_name']} (无 _course.json)", "warn")
            continue
        # 写 markdown
        md = chart_to_markdown(chart)
        (course / "_章节图谱.md").write_text(md, encoding="utf-8")
        # 仅当有内容才纳入全局
        if chart.get("pdf_total", 0) > 0:
            charts.append(chart)

        ch_n = chart.get("chapter_count", 0)
        nl = len(chart.get("non_lecture", []))
        un = len(chart.get("uncategorized", []))
        log(
            f"  ✓ {info['course_name']:<24s} "
            f"({chart.get('pdf_total', 0)} PDF, {ch_n} 章节, "
            f"非教 {nl}, 未归 {un})",
            "ok",
        )

    # 全局图谱
    if charts:
        gmd = global_overview_md(charts)
        (repo / "_全局图谱.md").write_text(gmd, encoding="utf-8")
        log(f"\n  全局图谱: {repo / '_全局图谱.md'}", "ok")

    header(f"聚合毕  ——  {len(charts)} 门课已成图谱", width=58)


if __name__ == "__main__":
    main()
