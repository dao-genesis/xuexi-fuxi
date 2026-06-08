# -*- coding: utf-8 -*-
"""
课件 知识素材 (chapter_material)  ——  其脆也，易判也

道法：
    章节图谱已立，万图归位。
    此关之事：以章节为单位，造一可读、可填、可喂 LLM 之素材文档。
    含：主版课件每页之图像引用、辅版概要、跨章节备注、
       复习占位（核心概念/公式/案例/考点/思考题）。

输出布局：
    解析仓库/<课程>/_素材/
    ├── _index.md
    ├── _第00章_绪论.md
    ├── _第01章_xxxx.md
    └── _第N章_xxxx.md

用法:
    python 课件_知识素材.py                    # 处理全部
    python 课件_知识素材.py -f 环境毒理        # 仅某课
    python 课件_知识素材.py --inline-images    # 内联展示图像（默仅图链）
    python 课件_知识素材.py --skip-non-lecture # 跳非教学（默生成简短摘要）
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _yc_common import (  # noqa: E402
    log,
    header,
    sanitize_filename,
    read_json,
    parse_course_dirname,
    section_span_fenced,
)


# ============================================================
# 路径与命名
# ============================================================

def chapter_filename(chap_num: int, chap_title: str) -> str:
    """章节素材 md 之文件名。"""
    title_part = sanitize_filename(chap_title or "无题", max_len=40).strip()
    if chap_num == 0:
        return f"_第00章_{title_part}.md".replace(" ", "_")
    return f"_第{chap_num:02d}章_{title_part}.md".replace(" ", "_")


# ============================================================
# 已填复习要点之保全
# ============================================================

_REVIEW_H2 = re.compile(r"^##\s+复习(?:要点|占位).*?$", re.MULTILINE)
_FILLED_REVIEW_H2 = re.compile(r"^##\s+复习要点.*?$", re.MULTILINE)
_MINDMAP_PLACEHOLDER_H2 = re.compile(r"^##\s+思维导图占位.*?$", re.MULTILINE)
_FILLED_MINDMAP_H2 = re.compile(r"^##\s+思维导图\s*·\s*LLM.*?$", re.MULTILINE)
_ANY_MINDMAP_H2 = re.compile(r"^##\s+思维导图.*?$", re.MULTILINE)
_NEXT_H2 = re.compile(r"^##\s+", re.MULTILINE)


def _section_span(text: str, heading_re: re.Pattern[str]) -> tuple[int, int] | None:
    """取某 H2 区段 [start, end)，对代码块内的 ## 免疫。"""
    return section_span_fenced(text, heading_re)


def _extract_filled_review(text: str) -> str | None:
    """抽取已填之“复习要点”区。未填占位不取。"""
    span = _section_span(text, _FILLED_REVIEW_H2)
    if not span:
        return None
    start, end = span
    section = text[start:end].strip()
    # 空壳不保
    if "LLM 未填" in section and len(section) < 200:
        return None
    return section


def _extract_filled_mindmap(text: str) -> str | None:
    """抽取已填之「思维导图 · LLM 生成」区；未填占位不取。"""
    span = _section_span(text, _FILLED_MINDMAP_H2)
    if not span:
        return None
    start, end = span
    section = text[start:end].strip()
    if "（待填）" in section and len(section) < 200:
        return None
    return section


def preserve_filled_review(new_md: str, old_md: str) -> str:
    """素材重生时，保全旧 md 中已由人/LLM 填好的复习要点 + 思维导图。

    道法：下层图链可重造，上层心得不可轻失。
    """
    # 1. 保全复习要点
    old_review = _extract_filled_review(old_md)
    if old_review:
        span = _section_span(new_md, _REVIEW_H2)
        if not span:
            new_md = new_md.rstrip() + "\n\n---\n\n" + old_review + "\n"
        else:
            start, end = span
            new_md = new_md[:start] + old_review + "\n" + new_md[end:]

    # 2. 保全思维导图（已 LLM 生成者）
    old_mindmap = _extract_filled_mindmap(old_md)
    if old_mindmap:
        span = _section_span(new_md, _ANY_MINDMAP_H2)
        if not span:
            new_md = new_md.rstrip() + "\n\n" + old_mindmap + "\n"
        else:
            start, end = span
            new_md = new_md[:start] + old_mindmap + "\n" + new_md[end:]

    return new_md


# ============================================================
# 一章素材生成
# ============================================================

def generate_chapter_md(
    chart: dict,
    chapter: dict,
    course_dir: Path,
    *,
    inline_images: bool = False,
    max_pages_per_aux: int = 3,
) -> str:
    """生成一章之 markdown 素材。"""
    course_name = chart.get("course_name", "")
    teacher = chart.get("teacher", "")
    semester = chart.get("semester", "")

    chap_num = chapter["chapter_num"]
    chap_title = chapter.get("chapter_title", "")
    chap_label = "绪论" if chap_num == 0 else f"第 {chap_num} 章"
    full_chap = f"{chap_label}" + (f" · {chap_title}" if chap_title else "")

    primary = chapter["primary"]
    all_docs = chapter.get("all_docs", [])
    aux_docs = [d for d in all_docs if not d.get("is_primary")]

    lines: list[str] = []
    lines.append(f"# {course_name} · {full_chap} · 素材")
    lines.append("")
    lines.append(f"> 教师: {teacher} · 学期: {semester}")
    lines.append(f"> 章下 PDF: {chapter.get('doc_count', 0)} 个 · 总页: {chapter.get('total_pages', 0)}")
    lines.append(
        f"> 主版: 第 {primary.get('lesson_seq')} 节 · "
        f"{primary.get('page_count')} 页"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # === 主版课件 · 图文1:1对照 ===
    # 道法：每图配其OCR文本，构建真正的图文对照文档
    # 雨课堂PDF：每页=一张全页图，ocr_text是唯一文本来源
    lines.append(f"## 主版课件 · 第 {primary.get('lesson_seq')} 节")
    lines.append("")
    lines.append(f"> `{primary.get('pdf_name')}`")
    lines.append("")
    primary_dir = course_dir / primary.get("rel_dir", "")
    primary_meta = read_json(primary_dir / "_doc.json")
    if primary_meta:
        pages = primary_meta.get("pages", [])
        rel_dir = primary.get("rel_dir", "")

        # 收集全部子图（含页号）
        all_figures: list[dict] = []
        for p in pages:
            for fig in (p.get("figures") or []):
                all_figures.append({
                    "page": p.get("index", 0),
                    "image": fig.get("image", ""),
                    "w": fig.get("w", 0),
                    "h": fig.get("h", 0),
                })

        # ── 图文1:1对照 ──
        # 优先使用 ocr_text（雨课堂PDF唯一文本源），fallback embedded_text
        def _page_text(p: dict) -> str:
            """取页面文本：ocr_text 优先，embedded_text 兜底。"""
            ocr = (p.get("ocr_text") or "").strip()
            if ocr:
                return ocr
            return (p.get("embedded_text") or "").strip()

        if inline_images:
            # ── 内联模式：每页 图+文 直接展示 ──
            for p in pages:
                idx = p.get("index", 0)
                img = p.get("image", "")
                text = _page_text(p)
                page_figs = p.get("figures") or []
                lines.append(f"### 第 {idx} 页")
                lines.append("")
                # 图片
                lines.append(f"![p{idx}](../{rel_dir}/{img})")
                lines.append("")
                # 页内子图（若有）
                if page_figs:
                    lines.append(
                        f"**本页嵌入子图（{len(page_figs)} 张）：**"
                    )
                    lines.append("")
                    for fig in page_figs:
                        fname = fig.get("image", "")
                        fw, fh = fig.get("w", 0), fig.get("h", 0)
                        lines.append(f"![fig-{fig.get('index',0)}](../{rel_dir}/{fname})")
                        if fw and fh:
                            lines.append(f"*{fw}×{fh}*")
                        lines.append("")
                # OCR文本（直接展示，非折叠）
                if text:
                    lines.append("**识别文本：**")
                    lines.append("")
                    lines.append(text)
                    lines.append("")
                lines.append("---")
                lines.append("")
        else:
            # ── 索引模式：图链 + OCR文本折叠 ──
            # 快速图链索引（可点击跳转）
            lines.append(f"<details><summary>展开 {len(pages)} 页图链</summary>")
            lines.append("")
            for p in pages:
                idx = p.get("index", 0)
                img = p.get("image", "")
                text = _page_text(p)
                # 首行作为预览
                preview = text.split("\n")[0][:50] if text else ""
                line = f"- [p{idx:03d}](../{rel_dir}/{img})"
                if preview:
                    line += f"  · {preview}"
                lines.append(line)
            lines.append("")
            lines.append("</details>")
            lines.append("")

            # 嵌入子图（折叠·若有）
            if all_figures:
                lines.append(
                    f"<details><summary>展开 {len(all_figures)} 个嵌入子图（PDF 页内图表·已单独提取）</summary>"
                )
                lines.append("")
                for fig in all_figures:
                    fname = fig["image"]
                    pg = fig["page"]
                    fw, fh = fig.get("w", 0), fig.get("h", 0)
                    size_str = f" · {fw}×{fh}" if fw and fh else ""
                    lines.append(
                        f"- [p{pg:03d}↳{fname}](../{rel_dir}/{fname}){size_str}"
                    )
                lines.append("")
                lines.append("</details>")
                lines.append("")

            # ── 图文1:1对照：每页图配其OCR文本 ──
            # 道法：真正的图文匹配，每图对应其完整文本内容
            ocr_pages = [p for p in pages if _page_text(p)]
            if ocr_pages:
                lines.append(
                    f"<details><summary>展开 {len(ocr_pages)} 页图文对照（每图配其识别文本）</summary>"
                )
                lines.append("")
                for p in ocr_pages:
                    idx = p.get("index", 0)
                    img = p.get("image", "")
                    text = _page_text(p)
                    # 图片链接
                    lines.append(f"**p{idx:03d}** ![](../{rel_dir}/{img})")
                    lines.append("")
                    # OCR文本
                    lines.append(text)
                    lines.append("")
                    lines.append("---")
                    lines.append("")
                lines.append("</details>")
                lines.append("")

    # === 辅版课件 ===
    if aux_docs:
        lines.append("## 辅版课件")
        lines.append("")
        lines.append(
            f"> 共 {len(aux_docs)} 个辅版（同章不同次/不同侧重）。"
            f"每辅版仅列前 {max_pages_per_aux} 页之链，余者参 主版 即可。"
        )
        lines.append("")
        for i, d in enumerate(aux_docs, 1):
            cross = "（跨章）" if d.get("is_cross_chapter") else ""
            lines.append(
                f"### 辅 {i} · 第 {d.get('lesson_seq')} 节 · "
                f"{d.get('page_count')} 页{cross}"
            )
            lines.append("")
            lines.append(f"> `{d.get('pdf_name')}` · 涉章 {d.get('all_chapter_nums', [])}")
            lines.append("")
            d_dir = course_dir / d.get("rel_dir", "")
            d_meta = read_json(d_dir / "_doc.json")
            if d_meta:
                pages = d_meta.get("pages", [])[:max_pages_per_aux]
                for p in pages:
                    idx = p.get("index", 0)
                    img = p.get("image", "")
                    # OCR文本预览
                    ocr = (p.get("ocr_text") or "").strip()
                    emb = (p.get("embedded_text") or "").strip()
                    text_preview = (ocr or emb).split("\n")[0][:50]
                    line = f"- [p{idx:03d}](../{d.get('rel_dir')}/{img})"
                    if text_preview:
                        line += f"  · {text_preview}"
                    lines.append(line)
                if len(d_meta.get("pages", [])) > max_pages_per_aux:
                    lines.append(
                        f"- ...余 {len(d_meta['pages']) - max_pages_per_aux} 页, "
                        f"参 [`{d.get('rel_dir')}/`](../{d.get('rel_dir')}/)"
                    )
                lines.append("")

    # === 跨章节备注 ===
    cross_chs = sorted({
        ch
        for d in all_docs
        for ch in (d.get("all_chapter_nums") or [])
        if ch != chap_num
    })
    if cross_chs:
        lines.append("## 跨章节备注")
        lines.append("")
        lines.append(
            f"此章之课件亦覆盖 {', '.join(f'第 {c} 章' for c in cross_chs)}, "
            f"复习时宜与彼章互参。"
        )
        lines.append("")

    # === 思维导图占位 ===
    try:
        from _道说_提示库 import 思维导图任务 as _MindmapTask
        lines.append("---")
        lines.append("")
        lines.append(
            _MindmapTask.render_placeholder(
                chap_label,
                chap_title or "（无题）",
            )
        )
    except ImportError:
        lines.append("---")
        lines.append("")
        lines.append("## 思维导图占位 · 待 LLM 生成")
        lines.append("")
        lines.append("```markmap")
        lines.append(f"# {chap_label}")
        lines.append("## （待填）")
        lines.append("```")
        lines.append("")

    # === 复习占位 ===
    lines.append("---")
    lines.append("")
    lines.append("## 复习占位 · 待人/LLM 填充")
    lines.append("")
    lines.append("> 阅读上方主版图链所指 page_001..page_NNN，整理为下：")
    lines.append("")
    lines.append("### 一、核心概念（名词解释）")
    lines.append("")
    lines.append("- [ ] 概念 1：")
    lines.append("- [ ] 概念 2：")
    lines.append("- [ ] 概念 3：")
    lines.append("")
    lines.append("### 二、关键公式 / 模型")
    lines.append("")
    lines.append("- [ ] 公式：")
    lines.append("- [ ] 模型：")
    lines.append("")
    lines.append("### 三、重要案例 / 实验 / 例题")
    lines.append("")
    lines.append("- [ ] 案例：")
    lines.append("")
    lines.append("### 四、高频考点（速记）")
    lines.append("")
    lines.append("1. ")
    lines.append("2. ")
    lines.append("3. ")
    lines.append("")
    lines.append("### 五、思考题 / 自测")
    lines.append("")
    lines.append("- [ ] 题：")
    lines.append("- [ ] 答：")
    lines.append("")
    lines.append("### 六、与前后章之关联")
    lines.append("")
    lines.append("- 承前章：")
    lines.append("- 启后章：")
    lines.append("")

    return "\n".join(lines)


# ============================================================
# 索引 markdown
# ============================================================

def generate_index_md(chart: dict, chapter_files: list[tuple[int, str, str]]) -> str:
    """生成 _index.md（章节素材入口）"""
    lines: list[str] = []
    course_name = chart.get("course_name", "")
    teacher = chart.get("teacher", "")
    semester = chart.get("semester", "")

    lines.append(f"# {course_name} · 知识素材索引")
    lines.append("")
    lines.append(f"> 教师: {teacher} · 学期: {semester}")
    lines.append(
        f"> PDF: {chart.get('pdf_total', 0)} · 页: {chart.get('page_total', 0)} · "
        f"章节: {chart.get('chapter_count', 0)}"
    )
    lines.append("")
    lines.append("## 各章节素材文件")
    lines.append("")
    lines.append("| 章节 | 标题 | 主版页数 | 文件 |")
    lines.append("|------|------|---------:|------|")
    for ch_num, ch_title, fname in chapter_files:
        ch_label = "绪论" if ch_num == 0 else f"第 {ch_num} 章"
        # 主版页数从 chart 中找
        primary_pages = next(
            (
                ch["primary"].get("page_count", 0)
                for ch in chart.get("chapters", [])
                if ch["chapter_num"] == ch_num
            ),
            0,
        )
        lines.append(f"| {ch_label} | {ch_title} | {primary_pages} | [{fname}](./{fname}) |")
    lines.append("")
    if chart.get("non_lecture"):
        lines.append("## 非教学性内容（仅列）")
        lines.append("")
        for d in chart["non_lecture"]:
            lines.append(
                f"- 第 {d.get('lesson_seq')} 节 · {d.get('page_count')} 页 · "
                f"{d.get('lesson_title', '')}  "
                f"`{d.get('rel_dir')}`"
            )
        lines.append("")
    if chart.get("uncategorized"):
        lines.append("## 未归类课件（无明确章号）")
        lines.append("")
        for d in chart["uncategorized"]:
            lines.append(
                f"- 第 {d.get('lesson_seq')} 节 · {d.get('page_count')} 页 · "
                f"{d.get('lesson_title', '')} | {d.get('presentation_title', '')}  "
                f"`{d.get('rel_dir')}`"
            )
        lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("> 道之教：")
    lines.append("> 1. 每章节 md 提供主版图链（按页排），辅版仅前几页之链")
    lines.append("> 2. 复习占位部分由人/LLM 阅图填充")
    lines.append("> 3. 跨章节标记便于交叉复习")
    lines.append("")
    return "\n".join(lines)


# ============================================================
# 一课程素材生成
# ============================================================

def generate_course_materials(
    course_dir: Path,
    *,
    inline_images: bool = False,
    skip_non_lecture: bool = False,
    max_pages_per_aux: int = 3,
) -> dict:
    """生成一课程之全部章节素材。"""
    chart_path = course_dir / "_章节图谱.json"
    chart = read_json(chart_path)
    if not chart:
        return {"course_dir": course_dir.name, "generated": 0, "skipped": True}

    out_dir = course_dir / "_素材"
    out_dir.mkdir(exist_ok=True)

    chapter_files: list[tuple[int, str, str]] = []
    generated = 0
    for ch in chart.get("chapters", []):
        ch_num = ch["chapter_num"]
        ch_title = ch.get("chapter_title", "")
        fname = chapter_filename(ch_num, ch_title)
        md_path = out_dir / fname
        md = generate_chapter_md(
            chart, ch, course_dir,
            inline_images=inline_images,
            max_pages_per_aux=max_pages_per_aux,
        )
        if md_path.exists():
            try:
                md = preserve_filled_review(md, md_path.read_text(encoding="utf-8"))
            except Exception:
                # 保全失败不阻断素材重生
                pass
        md_path.write_text(md, encoding="utf-8")
        chapter_files.append((ch_num, ch_title, fname))
        generated += 1

    # 索引
    idx_md = generate_index_md(chart, chapter_files)
    (out_dir / "_index.md").write_text(idx_md, encoding="utf-8")

    return {
        "course_dir": course_dir.name,
        "course_name": chart.get("course_name"),
        "generated": generated,
        "out_dir": str(out_dir),
    }


# ============================================================
# 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="课件 知识素材 —— 按章生 markdown 素材索引",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--repo", "-r", default="解析仓库",
        help="解析仓库目录（默 ./解析仓库）",
    )
    parser.add_argument(
        "--filter", "-f", action="append", default=None,
        help="课程名关键字过滤",
    )
    parser.add_argument(
        "--inline-images", action="store_true",
        help="主版每页内联图像（生成 md 较大但直观）",
    )
    parser.add_argument(
        "--skip-non-lecture", action="store_true",
        help="跳过非教学性内容",
    )
    parser.add_argument(
        "--max-aux-pages", type=int, default=3,
        help="每个辅版最多列出之页数（默 3）",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    repo = Path(args.repo)
    if not repo.is_absolute():
        repo = script_dir / repo

    header("课件 知识素材 —— 其脆也，易判也", width=58)
    log(f"  仓库: {repo}", "dim")

    if not repo.exists():
        log(f"× 仓库不存: {repo}", "err")
        sys.exit(1)

    courses = sorted([
        d for d in repo.iterdir()
        if d.is_dir() and (d / "_章节图谱.json").exists()
    ])
    if args.filter:
        courses = [c for c in courses if any(kw in c.name for kw in args.filter)]

    if not courses:
        log("∅ 无可处理之课程（_章节图谱.json 不存）", "warn")
        return

    log(f"\n共 {len(courses)} 门课程之素材待生成", "info")

    for course_dir in courses:
        info = parse_course_dirname(course_dir.name)
        result = generate_course_materials(
            course_dir,
            inline_images=args.inline_images,
            skip_non_lecture=args.skip_non_lecture,
            max_pages_per_aux=args.max_aux_pages,
        )
        log(
            f"  ✓ {info['course_name']:<24s} "
            f"({result['generated']} 章 → {course_dir.name}/_素材/)",
            "ok",
        )

    header(f"素材毕  ——  {len(courses)} 门课已成素材", width=58)


if __name__ == "__main__":
    main()
