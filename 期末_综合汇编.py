# -*- coding: utf-8 -*-
"""
期末 综合汇编 (final_review_compiler)  ——  执大象，天下往

道法：
    章节素材已散布于各课各章。
    此关之事：每课造一"期末骨架"——目录、速查表、复习路径、
    LLM 提示语模板，串各章素材为一炉，作期末冲刺之主图。

输出（追加于 _素材/ 下）：
    _素材/_期末骨架.md     课程级总览 + 各章速记卡 + 路径
    _素材/_期末速查.md     紧凑一张表（每章一行）+ 章际对照
    _素材/_LLM_提示语.md   推荐喂给 LLM 之复习提示语模板

用法:
    python 期末_综合汇编.py                 # 全部
    python 期末_综合汇编.py -f 环境毒理     # 仅一课
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
    read_json,
    parse_course_dirname,
    sanitize_filename,
    section_span_fenced,
)


def _chap_label(n: int) -> str:
    return "绪论" if n == 0 else f"第 {n} 章"


def _chap_md_name(n: int, title: str) -> str:
    """与 课件_知识素材.py 之 chapter_filename 一致"""
    t = sanitize_filename(title or "无题", max_len=40).strip()
    if n == 0:
        return f"_第00章_{t}.md".replace(" ", "_")
    return f"_第{n:02d}章_{t}.md".replace(" ", "_")


def _chap_material_path(course_dir: Path, chapter: dict) -> Path:
    """一章对应素材 md 路径。"""
    return course_dir / "_素材" / _chap_md_name(
        chapter["chapter_num"],
        chapter.get("chapter_title", ""),
    )


# ============================================================
# 已填章材之抽取
# ============================================================

_REVIEW_H2 = re.compile(r"^##\s+复习要点.*?$", re.MULTILINE)
_NEXT_H2 = re.compile(r"^##\s+", re.MULTILINE)
_H3_RE = re.compile(r"^###\s+.*?$", re.MULTILINE)


def _section_span(text: str, heading_re: re.Pattern[str]) -> tuple[int, int] | None:
    """取某 H2 区段 [start, end)，对代码块内的 ## 免疫。"""
    return section_span_fenced(text, heading_re)


def extract_review_section(text: str) -> str:
    """抽取章 md 中“## 复习要点”区段；未填则返空。"""
    span = _section_span(text, _REVIEW_H2)
    if not span:
        return ""
    start, end = span
    section = text[start:end].strip()
    if "LLM 未填" in section and len(section) < 240:
        return ""
    return section


def _extract_h3(review: str, keyword: str) -> str:
    """从复习要点区中抽一段 H3。"""
    matches = list(_H3_RE.finditer(review))
    for i, m in enumerate(matches):
        if keyword not in m.group(0):
            continue
        end = matches[i + 1].start() if i + 1 < len(matches) else len(review)
        return review[m.end():end].strip()
    return ""


def _strip_md(s: str) -> str:
    s = re.sub(r"\*\*(.*?)\*\*", r"\1", s)
    s = s.replace("`", "")
    s = re.sub(r"^\s*[-*]\s+", "", s)
    s = re.sub(r"^\s*\d+[.)、]\s*", "", s)
    s = s.replace("[ ]", "").strip()
    return s


def _first_items(block: str, n: int = 3) -> list[str]:
    items: list[str] = []
    for raw in block.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("|"):
            if "---" in line or "公式" in line and "含义" in line:
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells:
                line = cells[0]
        if line.startswith(("-", "*")) or re.match(r"^\d+[.)、]\s+", line) or line.startswith("|"):
            item = _strip_md(line)
            if item:
                items.append(item)
        if len(items) >= n:
            break
    return items


def read_chapter_review(course_dir: Path, chapter: dict) -> dict:
    """读一章素材，并抽出可用于最终汇编之摘要。"""
    md_path = _chap_material_path(course_dir, chapter)
    text = md_path.read_text(encoding="utf-8") if md_path.exists() else ""
    review = extract_review_section(text)
    filled = bool(review)
    concepts = _first_items(_extract_h3(review, "核心概念"), 3) if filled else []
    formulas = _first_items(_extract_h3(review, "关键公式"), 3) if filled else []
    exam_points = _first_items(_extract_h3(review, "高频考点"), 3) if filled else []
    return {
        "path": md_path,
        "exists": md_path.exists(),
        "text": text,
        "review": review,
        "filled": filled,
        "concepts": concepts,
        "formulas": formulas,
        "exam_points": exam_points,
    }


def _demote_headings(md: str, by: int = 2) -> str:
    """将嵌入内容之标题降级，免冲突。"""
    def repl(m: re.Match[str]) -> str:
        marks = m.group(1)
        return "#" * min(6, len(marks) + by) + m.group(2)

    return re.sub(r"^(#{1,6})(\s+)", repl, md, flags=re.MULTILINE)


def _cell(s: str) -> str:
    """Markdown 表格单元清洗。"""
    return (s or "").replace("|", " / ").replace("\n", "<br>").strip()


def _join_short(items: list[str], empty: str = "待填") -> str:
    return "；".join(_cell(x) for x in items if x) or empty


# ============================================================
# 期末骨架·课程级总览
# ============================================================

def generate_skeleton_md(chart: dict, course_dir: Path | None = None) -> str:
    course_name = chart.get("course_name", "")
    teacher = chart.get("teacher", "")
    semester = chart.get("semester", "")
    chapters = chart.get("chapters", [])
    reviews = {
        ch["chapter_num"]: read_chapter_review(course_dir, ch)
        for ch in chapters
    } if course_dir else {}
    filled_count = sum(1 for r in reviews.values() if r.get("filled"))

    lines: list[str] = []
    lines.append(f"# {course_name} · 期末复习骨架")
    lines.append("")
    lines.append(f"> 教师: {teacher} · 学期: {semester}")
    lines.append(
        f"> 共 {chart.get('pdf_total', 0)} PDF · {chart.get('page_total', 0)} 页 · "
        f"{len(chapters)} 章节"
    )
    if course_dir:
        lines.append(f"> 已填复习要点：{filled_count}/{len(chapters)} 章")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 一·目录
    lines.append("## 一 · 目录与素材链")
    lines.append("")
    lines.append("| 章节 | 标题 | 主版页数 | 素材文件 |")
    lines.append("| ---- | ---- | -------: | -------- |")
    for ch in chapters:
        n = ch["chapter_num"]
        t = ch.get("chapter_title", "")
        fname = _chap_md_name(n, t)
        pp = ch["primary"].get("page_count", 0)
        lines.append(f"| {_chap_label(n)} | {t} | {pp} | [{fname}](./{fname}) |")
    lines.append("")

    # 二·复习路径建议
    lines.append("## 二 · 复习路径")
    lines.append("")
    total_pages = sum(ch["primary"].get("page_count", 0) for ch in chapters)
    if total_pages <= 200:
        density = "薄"
        days_est = "2-3 日"
    elif total_pages <= 500:
        density = "中"
        days_est = "5-7 日"
    else:
        density = "厚"
        days_est = "10-14 日"
    lines.append(
        f"- 课件主版总页数 {total_pages}，密度 **{density}**，建议复习期 {days_est}"
    )
    lines.append("- 推荐三轮法：")
    lines.append("  1. **通览**（约 30%）：逐章浏览主版，知大略，标疑点")
    lines.append("  2. **填表**（约 50%）：每章节素材 md 之占位由 LLM 协填，自校")
    lines.append("  3. **速记**（约 20%）：本骨架之速查表 + 易错点反复")
    lines.append("")

    # 三·各章速记卡
    lines.append("## 三 · 各章速记卡")
    lines.append("")
    for ch in chapters:
        n = ch["chapter_num"]
        t = ch.get("chapter_title", "")
        fname = _chap_md_name(n, t)
        primary = ch["primary"]
        r = reviews.get(n, {})
        lines.append(f"### {_chap_label(n)} · {t}")
        lines.append("")
        lines.append(
            f"> 主版 {primary.get('page_count')} 页 · 第 {primary.get('lesson_seq')} 节 · "
            f"[详细素材](./{fname})"
        )
        lines.append("")
        lines.append("**核心三问**：")
        lines.append("")
        lines.append(f"- **是什么** ── {_join_short(r.get('concepts', []), '待填：见详细素材')}")
        lines.append(f"- **怎么算** ── {_join_short(r.get('formulas', []), '待填：见详细素材')}")
        lines.append(f"- **考什么** ── {_join_short(r.get('exam_points', []), '待填：见详细素材')}")
        lines.append("")
        lines.append("**易错 / 易混**：")
        lines.append("- 待复核课件原图与教师强调处")
        lines.append("")

    # 跨章节交叉
    cross_pairs: list[tuple[int, int]] = []
    for ch in chapters:
        n = ch["chapter_num"]
        for d in ch.get("all_docs", []):
            chs = d.get("all_chapter_nums", []) or []
            for c2 in chs:
                if c2 > n:
                    cross_pairs.append((n, c2))
    cross_pairs = sorted(set(cross_pairs))
    if cross_pairs:
        lines.append("## 四 · 章际交叉（同一课件涉两章）")
        lines.append("")
        for a, b in cross_pairs:
            lines.append(f"- {_chap_label(a)}  ⇄  {_chap_label(b)}")
        lines.append("")

    # 非教学性
    if chart.get("non_lecture"):
        lines.append("## 五 · 非教学性内容（仅记，期末不考）")
        lines.append("")
        for d in chart["non_lecture"]:
            lines.append(
                f"- {d.get('lesson_title')} ({d.get('page_count')} 页)"
            )
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 自评清单（复习完打勾）")
    lines.append("")
    for ch in chapters:
        n = ch["chapter_num"]
        t = ch.get("chapter_title", "")
        lines.append(f"- [ ] {_chap_label(n)} · {t}")
    lines.append("- [ ] 跨章交叉点皆通")
    lines.append("- [ ] 期末速查表已成")
    lines.append("- [ ] 三套真题/模拟题已练")
    lines.append("")

    return "\n".join(lines)


# ============================================================
# 期末速查表
# ============================================================

def generate_cheatsheet_md(chart: dict, course_dir: Path | None = None) -> str:
    course_name = chart.get("course_name", "")
    chapters = chart.get("chapters", [])
    reviews = {
        ch["chapter_num"]: read_chapter_review(course_dir, ch)
        for ch in chapters
    } if course_dir else {}
    filled_count = sum(1 for r in reviews.values() if r.get("filled"))

    lines: list[str] = []
    lines.append(f"# {course_name} · 期末速查表")
    lines.append("")
    if course_dir:
        lines.append(f"> 一页之表，含各章关键概念、公式、考点。已吸纳 {filled_count}/{len(chapters)} 章复习要点。")
    else:
        lines.append("> 一页之表，含各章关键概念、公式、考点。**待人/LLM 填**。")
    lines.append("")

    # 紧凑表：章 | 核心概念 | 关键公式 | 高频考点
    lines.append("| 章 | 标题 | 核心概念（≤3） | 关键公式 / 模型 | 高频考点 |")
    lines.append("| ---: | ---- | -------------- | ---------------- | -------- |")
    for ch in chapters:
        n = ch["chapter_num"]
        t = ch.get("chapter_title", "")
        r = reviews.get(n, {})
        lines.append(
            f"| {n} | {_cell(t)} | "
            f"{_join_short(r.get('concepts', []), '')} | "
            f"{_join_short(r.get('formulas', []), '')} | "
            f"{_join_short(r.get('exam_points', []), '')} |"
        )
    lines.append("")

    lines.append("## 易错速记（错过即列）")
    lines.append("")
    lines.append("| # | 易错点 | 正确表述 | 出处（章·页） |")
    lines.append("| --: | ------ | -------- | ------------ |")
    for i in range(1, 11):
        lines.append(f"| {i} |  |  |  |")
    lines.append("")

    lines.append("## 名词速对（≤30）")
    lines.append("")
    lines.append("| 术语 | 释义 | 章 |")
    lines.append("| ---- | ---- | ---: |")
    terms: list[tuple[str, str, int]] = []
    for ch in chapters:
        n = ch["chapter_num"]
        for item in reviews.get(n, {}).get("concepts", []):
            if "：" in item:
                name, desc = item.split("：", 1)
            elif ":" in item:
                name, desc = item.split(":", 1)
            else:
                name, desc = item, ""
            name = _cell(name)
            desc = _cell(desc)
            if name:
                terms.append((name, desc, n))
    for name, desc, n in terms[:30]:
        lines.append(f"| {name} | {desc} | {n} |")
    for _ in range(max(0, 15 - len(terms[:30]))):
        lines.append("|  |  |  |")
    lines.append("")

    return "\n".join(lines)


_MINDMAP_FILLED_H2 = re.compile(r"^##\s+思维导图\s*·\s*LLM.*?$", re.MULTILINE)
_NEXT_H2_IN_FINAL = re.compile(r"^##\s+", re.MULTILINE)


def _extract_mindmap_section(text: str) -> str:
    """从章 md 中抽取已生成的「思维导图 · LLM 生成」区段。"""
    m = _MINDMAP_FILLED_H2.search(text)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = _NEXT_H2_IN_FINAL.search(rest)
    end = m.end() + nxt.start() if nxt else len(text)
    section = text[m.start():end].strip()
    # 占位不要
    if "（待填）" in section and len(section) < 200:
        return ""
    return section


def _read_chapter_figures(course_dir: Path, chapter: dict) -> list[dict]:
    """从章节主版 _doc.json 中收集所有子图（figures）信息。"""
    primary = chapter.get("primary", {})
    rel_dir = primary.get("rel_dir", "")
    if not rel_dir:
        return []
    doc_path = course_dir / rel_dir / "_doc.json"
    meta = read_json(doc_path)
    if not meta:
        return []
    result: list[dict] = []
    for p in meta.get("pages", []):
        for fig in (p.get("figures") or []):
            result.append({
                "page": p.get("index", 0),
                "image": fig.get("image", ""),
                "w": fig.get("w", 0),
                "h": fig.get("h", 0),
                "rel_dir": rel_dir,
            })
    return result


def generate_final_review_md(chart: dict, course_dir: Path) -> str:
    """生成课程级综合复习资料：全章要点 + 嵌入子图 + 思维导图 + 全文汇总。

    道法：
        「最终底层复习资料」不止文字，亦含原图与思维导图。
        图文并茂，方为真·底层·复习资料。
        链路：PDF → 图集 + 子图 → LLM 协填 → 思维导图 → 本资料
    """
    course_name = chart.get("course_name", "")
    teacher = chart.get("teacher", "")
    semester = chart.get("semester", "")
    chapters = chart.get("chapters", [])
    reviews = {ch["chapter_num"]: read_chapter_review(course_dir, ch) for ch in chapters}
    filled_count = sum(1 for r in reviews.values() if r.get("filled"))

    # 计算子图总数
    all_figs_count = sum(
        len(_read_chapter_figures(course_dir, ch)) for ch in chapters
    )
    # 计算思维导图完成数
    mindmap_count = 0
    for ch in chapters:
        r = reviews.get(ch["chapter_num"], {})
        if r.get("text") and _extract_mindmap_section(r.get("text", "")):
            mindmap_count += 1

    lines: list[str] = []
    lines.append(f"# {course_name} · 综合复习资料")
    lines.append("")
    lines.append(f"> 教师: {teacher} · 学期: {semester}")
    lines.append(
        f"> 链路：原始 PDF → 页图集（多图提取）→ 章节图谱 → LLM 协填要点 → 思维导图 → **本资料**"
    )
    lines.append(
        f"> 完成度：复习要点 **{filled_count}/{len(chapters)}** 章 · "
        f"嵌入子图 **{all_figs_count}** 张 · 思维导图 **{mindmap_count}/{len(chapters)}** 章"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── 一·章级入口 ──
    lines.append("## 一 · 章级入口")
    lines.append("")
    lines.append("| 章 | 标题 | 主版页 | 子图 | 要点 | 图谱 | 素材 |")
    lines.append("| ---: | ---- | -----: | ---: | :--: | :--: | ---- |")
    for ch in chapters:
        n = ch["chapter_num"]
        t = ch.get("chapter_title", "")
        pp = ch.get("primary", {}).get("page_count", 0)
        fname = _chap_md_name(n, t)
        figs = _read_chapter_figures(course_dir, ch)
        fig_n = len(figs)
        filled = "✓" if reviews.get(n, {}).get("filled") else "·"
        r_text = reviews.get(n, {}).get("text", "")
        has_map = "✓" if _extract_mindmap_section(r_text) else "·"
        lines.append(
            f"| {n} | {_cell(t)} | {pp} | {fig_n} | {filled} | {has_map} | [{fname}](./{fname}) |"
        )
    lines.append("")

    # ── 二·全章汇编（要点 + 子图 + 思维导图） ──
    lines.append("## 二 · 全章综合汇编")
    lines.append("")

    for ch in chapters:
        n = ch["chapter_num"]
        t = ch.get("chapter_title", "")
        fname = _chap_md_name(n, t)
        r = reviews.get(n, {})
        primary = ch.get("primary", {})
        rel_dir = primary.get("rel_dir", "")

        lines.append(f"### {_chap_label(n)} · {t}")
        lines.append("")
        lines.append(
            f"> 素材：[{fname}](./{fname}) · 主版 {primary.get('page_count', 0)} 页"
        )
        lines.append("")

        # ① 复习要点
        if r.get("filled"):
            review = r.get("review", "")
            review_body = re.sub(
                r"^##\s+复习要点.*?\n+", "", review, count=1, flags=re.MULTILINE
            )
            lines.append(_demote_headings(review_body, by=1).strip())
        else:
            lines.append("> ⚠ 复习要点尚未填充。可运行：")
            lines.append("")
            lines.append("```bash")
            lines.append(
                f"python 课件_道喂.py --课 {course_name[:8]} --章 {n} --在线 --拼网格"
            )
            lines.append("```")
        lines.append("")

        # ② 图注速览 + 图文1:1对照（按类型定位原图，每图配其OCR文本）
        annot_index = read_json(course_dir / "_图注索引.json")
        if annot_index and rel_dir:
            from pdf_图注 import ContentType
            page_annots = [
                a for a in annot_index.get("annotations", [])
                if a.get("rel_dir") == rel_dir
            ]
            if page_annots:
                # 按类型分组
                by_type: dict[str, list] = {}
                for a in page_annots:
                    t = a.get("content_type", "other")
                    by_type.setdefault(t, []).append(a)
                lines.append(
                    "<details><summary>🏷️ 图注速览 · 按类型定位原图"
                    f"（{len(page_annots)} 页）</summary>"
                )
                lines.append("")
                for t in ContentType.PRIORITY:
                    type_annots = by_type.get(t, [])
                    if not type_annots:
                        continue
                    label = ContentType.LABELS.get(t, t)
                    lines.append(f"**{label}** ({len(type_annots)} 页)")
                    lines.append("")
                    for a in sorted(type_annots, key=lambda x: x.get("page", 0)):
                        pg = a.get("page", 0)
                        topic = a.get("core_topic", "") or "—"
                        img = a.get("image", "")
                        kws = "、".join(a.get("keywords", [])[:3]) or ""
                        kw_str = f" · {kws}" if kws else ""
                        lines.append(
                            f"- p{pg:03d} {topic}{kw_str} "
                            f"[📷](../{rel_dir}/{img})"
                        )
                    lines.append("")
                lines.append("</details>")
                lines.append("")

                # ── 图文1:1对照 ──
                # 读取OCR文本
                doc_meta = read_json(course_dir / rel_dir / "_doc.json")
                pages_meta = {}
                if doc_meta:
                    for p in doc_meta.get("pages", []):
                        pages_meta[p.get("index", 0)] = p

                lines.append(
                    f"<details><summary>🔍 图文1:1对照 · "
                    f"每图配其识别文本（{len(page_annots)} 页）</summary>"
                )
                lines.append("")
                for a in sorted(page_annots, key=lambda x: x.get("page", 0)):
                    pg = a.get("page", 0)
                    t = a.get("content_type", "other")
                    label = ContentType.LABELS.get(t, t)
                    topic = a.get("core_topic", "") or ""
                    img_file = a.get("image", "") or f"page_{pg:03d}.jpg"

                    p_meta = pages_meta.get(pg, {})
                    ocr = (p_meta.get("ocr_text") or "").strip()
                    emb = (p_meta.get("embedded_text") or "").strip()
                    page_text = ocr or emb

                    lines.append(f"**p{pg:03d} {label}** · {topic}")
                    lines.append("")
                    lines.append(f"![p{pg}](../{rel_dir}/{img_file})")
                    lines.append("")
                    if page_text:
                        lines.append(f"<details><summary>识别文本（{len(page_text)}字）</summary>")
                        lines.append("")
                        lines.append(page_text)
                        lines.append("")
                        lines.append("</details>")
                        lines.append("")
                    lines.append("---")
                    lines.append("")
                lines.append("</details>")
                lines.append("")

        # ③ 嵌入子图（若有）
        figs = _read_chapter_figures(course_dir, ch)
        if figs and rel_dir:
            lines.append(
                f"<details><summary>📷 嵌入子图（{len(figs)} 张·PDF 页内图表）</summary>"
            )
            lines.append("")
            for fig in figs:
                fname_fig = fig["image"]
                pg = fig["page"]
                fw, fh = fig.get("w", 0), fig.get("h", 0)
                size_str = f" *{fw}×{fh}*" if fw and fh else ""
                # 路径：从 _素材/_最终复习资料.md → ../<rel_dir>/page_xxx_fig_xx.jpg
                lines.append(
                    f"![p{pg:03d}-fig](../{rel_dir}/{fname_fig}){size_str}"
                )
                lines.append("")
            lines.append("</details>")
            lines.append("")

        # ④ 思维导图（若已生成）
        mindmap_section = _extract_mindmap_section(r.get("text", ""))
        if mindmap_section:
            # 降级标题（避免与全文 H2 冲突）
            mindmap_body = re.sub(
                r"^##\s+思维导图.*?\n+", "", mindmap_section, count=1, flags=re.MULTILINE
            )
            lines.append(
                "<details><summary>🧠 思维导图（markmap / mermaid）</summary>"
            )
            lines.append("")
            lines.append(mindmap_body.strip())
            lines.append("")
            lines.append("</details>")
        else:
            lines.append(
                "> 🧠 思维导图尚未生成。可运行：`python 课件_图谱.py -f "
                f"{course_name[:8]} --在线`"
            )
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append("")
    lines.append("> **正言若反**：最终资料不离底层图像；凡疑处，复归章节素材与原始 PDF。")
    lines.append("> 每章之链：原始 PDF → `02_解析成果/<PDF_stem>/page_*.jpg` → 章节素材 md → 本资料。")
    lines.append("")
    return "\n".join(lines)


# ============================================================
# LLM 提示语模板
# ============================================================

def generate_llm_prompts_md(chart: dict) -> str:
    course_name = chart.get("course_name", "")
    teacher = chart.get("teacher", "")
    chapters = chart.get("chapters", [])

    lines: list[str] = []
    lines.append(f"# {course_name} · LLM 喂入提示语")
    lines.append("")
    lines.append(
        "> 复习占位（核心概念/公式/考点等）可由具备视觉能力的 LLM 协填。"
        "下列提示语可直接复制使用。"
    )
    lines.append("")

    # 1. 按章填充
    lines.append("## 提示语 一 · 按章填充素材")
    lines.append("")
    lines.append("```")
    lines.append(f"你将以图文方式阅读《{course_name}》（{teacher} 教）某章之课件主版。")
    lines.append("请按下列结构整理：")
    lines.append("")
    lines.append("1. 核心概念（名词解释，每条 1-3 句，标出页码）")
    lines.append("2. 关键公式 / 模型（含适用条件与典型例题）")
    lines.append("3. 重要案例 / 实验（含原理、步骤、结论）")
    lines.append("4. 高频考点（按 必考/常考/可能考 三档分级）")
    lines.append("5. 易错 / 易混点（成对列出）")
    lines.append("6. 三道思考题 + 参考答案")
    lines.append("7. 与前后章之关联（一句话）")
    lines.append("")
    lines.append("要求：")
    lines.append("- 用 markdown，与素材 md 占位结构对齐")
    lines.append("- 每条不超 5 行，必要时分点")
    lines.append("- 保留原图序号引用（如 参 p012）")
    lines.append("```")
    lines.append("")

    # 2. 速查表
    lines.append("## 提示语 二 · 生成速查表")
    lines.append("")
    lines.append("```")
    lines.append(f"已读《{course_name}》全部 {len(chapters)} 章。")
    lines.append("请生成一份紧凑速查表（一页，markdown 表格），每章一行：")
    lines.append("")
    lines.append("| 章 | 标题 | 核心概念≤3 | 关键公式 | 高频考点 |")
    lines.append("")
    lines.append("再补：")
    lines.append("- 易错点 10 条（错过即列，标章·页）")
    lines.append("- 名词速对 20 条（术语→释义→章）")
    lines.append("- 章际关联图（mermaid 图，节点为章，边为概念衔接）")
    lines.append("```")
    lines.append("")

    # 3. 真题模拟
    lines.append("## 提示语 三 · 期末模拟卷")
    lines.append("")
    lines.append("```")
    lines.append(f"以《{course_name}》全部章节为蓝本，出一份期末模拟卷：")
    lines.append("")
    lines.append("- 名词解释 5（覆盖不同章）")
    lines.append("- 简答题 5（综合 2-3 章之联系）")
    lines.append("- 论述题 2（深考主线）")
    lines.append("- 计算 / 应用题 2（含步骤）")
    lines.append("- 全卷 100 分，2 小时")
    lines.append("- 附详细答案与评分标准")
    lines.append("")
    lines.append("出题原则：")
    lines.append("- 不偏不怪，覆盖主版课件之高频内容")
    lines.append("- 体现各章之相对权重（页数 / 题量 大致正比）")
    lines.append("```")
    lines.append("")

    # 4. 提供本课各章基本元信息
    lines.append("## 附：本课章节元信息（供 LLM 上下文）")
    lines.append("")
    lines.append("```")
    for ch in chapters:
        n = ch["chapter_num"]
        t = ch.get("chapter_title", "")
        pp = ch["primary"].get("page_count", 0)
        lines.append(f"{_chap_label(n)}：{t}（主版 {pp} 页）")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


# ============================================================
# 一课程汇编
# ============================================================

def compile_course(course_dir: Path) -> dict:
    chart_path = course_dir / "_章节图谱.json"
    chart = read_json(chart_path)
    if not chart:
        return {"course_dir": course_dir.name, "skipped": True}
    if not chart.get("chapters"):
        return {"course_dir": course_dir.name, "skipped": True, "reason": "无章节"}

    out_dir = course_dir / "_素材"
    out_dir.mkdir(exist_ok=True)

    (out_dir / "_期末骨架.md").write_text(generate_skeleton_md(chart, course_dir), encoding="utf-8")
    (out_dir / "_期末速查.md").write_text(generate_cheatsheet_md(chart, course_dir), encoding="utf-8")
    (out_dir / "_LLM_提示语.md").write_text(generate_llm_prompts_md(chart), encoding="utf-8")
    # 综合复习资料（图文+思维导图·升级版）
    comprehensive = generate_final_review_md(chart, course_dir)
    (out_dir / "_综合复习资料.md").write_text(comprehensive, encoding="utf-8")
    # 同时保留旧名以向后兼容（内容相同）
    (out_dir / "_最终复习资料.md").write_text(comprehensive, encoding="utf-8")

    return {
        "course_dir": course_dir.name,
        "course_name": chart.get("course_name"),
        "chapters": len(chart.get("chapters", [])),
        "files": 5,
    }


# ============================================================
# 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="期末 综合汇编 —— 执大象，天下往",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--repo", "-r", default="解析仓库")
    parser.add_argument("--filter", "-f", action="append", default=None)
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    repo = Path(args.repo)
    if not repo.is_absolute():
        repo = script_dir / repo

    header("期末 综合汇编 —— 执大象，天下往", width=58)
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
        log("∅ 无可汇编之课程", "warn")
        return

    log(f"\n共 {len(courses)} 门课程", "info")

    compiled = 0
    for course_dir in courses:
        info = parse_course_dirname(course_dir.name)
        result = compile_course(course_dir)
        if result.get("skipped"):
            log(
                f"  ∅ {info['course_name']:<24s} (跳: {result.get('reason', '无图谱')})",
                "dim",
            )
            continue
        log(
            f"  ✓ {info['course_name']:<24s} "
            f"({result.get('chapters', 0)} 章 · {result.get('files', 0)} 个汇编文件)",
            "ok",
        )
        compiled += 1

    header(f"汇编毕  ——  {compiled} 门课已成期末骨架", width=58)


if __name__ == "__main__":
    main()
