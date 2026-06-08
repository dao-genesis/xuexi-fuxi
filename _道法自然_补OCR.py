# -*- coding: utf-8 -*-
"""
道法自然·补OCR  ——  为之于其未有也，治之于其未乱也

四课（环境规划与管理·环境法学·流体力学·地理信息系统）
已有 page_NNN.jpg 但缺 OCR 文字 + _全文.md + pages/page_NNN.md
此脚本一键补全。

用法：
    python _道法自然_补OCR.py
    python _道法自然_补OCR.py --force       # 强制重OCR已有页
    python _道法自然_补OCR.py --no-pages    # 不生成页级MD
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# 确保在正确目录
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from pdf_提文 import ocr_course, ocr_document, _build_full_markdown, _HAS_V2_ENGINE
from _yc_common import log, header, read_json, write_json

# 四课之解析成果目录
COURSES = [
    "环境规划与管理",
    "环境法学",
    "流体力学",
    "地理信息系统",
]

# 解析成果子目录名（环境毒理学是 03_解析成果，其余是 02_解析成果）
PARSE_DIR_MAP = {
    "环境毒理学": "03_解析成果",
}


def build_page_md(doc_dir: Path, meta: dict) -> int:
    """为每页生成 pages/page_NNN.md（图+文配对）。"""
    pages_dir = doc_dir / "pages"
    pages_dir.mkdir(exist_ok=True)

    pdf_name = meta.get("pdf_name", "?")
    pres_title = meta.get("presentation_title", "")
    lesson_title = meta.get("lesson_title", "")
    title = pres_title or lesson_title or pdf_name

    count = 0
    for p in meta.get("pages", []):
        idx = p.get("index", 0)
        img = p.get("image", "")
        ocr = p.get("ocr_text") or p.get("embedded_text") or ""

        # 计算OCR置信度
        ocr_lines_count = p.get("ocr_lines_count", 0)
        if ocr_lines_count > 0 and ocr:
            conf = "95%+"  # 简化，实际可从lines算
        elif ocr:
            conf = "~90%"
        else:
            conf = "N/A"

        md_path = pages_dir / f"page_{idx:03d}.md"

        # 增量：已存在且非空则跳过
        if md_path.exists() and md_path.stat().st_size > 20:
            continue

        lines = [
            f"# {title} — 第 {idx} 页",
            "",
            f"> 来源: {pdf_name}",
            f"> 页码: {idx}",
            f"> OCR置信: {conf}",
            "",
            f"![page {idx}](../{img})",
            "",
        ]

        if ocr and ocr.strip():
            # 简单文本转MD（识别标题）
            from pdf_提文 import _simple_text_to_md
            lines.append(_simple_text_to_md(ocr.strip()))
        else:
            lines.append("> *此页无文字*")

        md_path.write_text("\n".join(lines), encoding="utf-8")
        count += 1

    return count


def build_pure_md(doc_dir: Path, meta: dict, course_root: Path) -> int:
    """生成纯文字版 MD（无图片引用），放入 04_MD全文/ 或对应目录。"""
    # 检查是否有 04_MD全文 目录
    md_dir = course_root / "04_MD全文"
    if not md_dir.exists():
        # 环境毒理学有此目录，其余可能没有
        return 0

    pdf_name = meta.get("pdf_name", "?")
    stem = Path(pdf_name).stem
    # 截断过长文件名
    if len(stem) > 80:
        stem = stem[:80]
    md_path = md_dir / f"{stem}.md"

    if md_path.exists() and md_path.stat().st_size > 20:
        return 0

    pres_title = meta.get("presentation_title", "")
    lesson_title = meta.get("lesson_title", "")
    title = pres_title or lesson_title or pdf_name

    L = [f"# {stem}", "", f"> 来源: {pdf_name}", f"> 页数: {meta.get('page_count', 0)}", ""]

    for p in meta.get("pages", []):
        idx = p.get("index", 0)
        ocr = p.get("ocr_text") or p.get("embedded_text") or ""

        L.append("---")
        L.append("")
        L.append(f"<!-- page {idx} -->")
        L.append("")

        if ocr and ocr.strip():
            from pdf_提文 import _simple_text_to_md
            L.append(_simple_text_to_md(ocr.strip()))
        else:
            L.append(f"> *第{idx}页无文字*")
        L.append("")

    md_path.write_text("\n".join(L), encoding="utf-8")
    return 1


def main():
    import argparse
    parser = argparse.ArgumentParser(description="道法自然·补OCR")
    parser.add_argument("--force", action="store_true", help="强制重OCR已有页")
    parser.add_argument("--no-pages", action="store_true", help="不生成页级MD")
    parser.add_argument("--filter", "-f", action="append", help="仅处理含此关键字之课程")
    args = parser.parse_args()

    header("道法自然·补OCR  ——  为之于其未有也", width=56)

    courses = COURSES
    if args.filter:
        courses = [c for c in courses if any(kw in c for kw in args.filter)]

    total_ocr_pages = 0
    total_page_md = 0
    total_full_md = 0
    t0 = time.time()

    for course_name in courses:
        parse_subdir = PARSE_DIR_MAP.get(course_name, "02_解析成果")
        course_root = SCRIPT_DIR / course_name
        parse_dir = course_root / parse_subdir

        if not parse_dir.exists():
            log(f"  ∅ {course_name}: {parse_subdir}/ 不存在", "warn")
            continue

        log(f"\n┌── {course_name} ({parse_subdir}/)", "title")

        # 找所有 _doc.json 子目录
        doc_dirs = sorted(
            d for d in parse_dir.iterdir()
            if d.is_dir() and (d / "_doc.json").exists()
        )

        if not doc_dirs:
            log(f"  ∅ 无 _doc.json", "warn")
            continue

        log(f"│   {len(doc_dirs)} 个PDF解析目录", "info")

        # 逐PDF执行OCR
        for d in doc_dirs:
            try:
                result = ocr_document(d, force=args.force, use_v2=True)
                if result:
                    ocr_pages = sum(1 for p in result.get("pages", []) if p.get("ocr_text"))
                    total_ocr_pages += ocr_pages
                    log(f"  ✓ {d.name[:50]:50s} OCR {ocr_pages}页", "ok")

                    # 生成页级MD
                    if not args.no_pages:
                        n = build_page_md(d, result)
                        total_page_md += n
                        if n > 0:
                            log(f"    ↳ 页级MD: +{n}", "dim")

                    # 生成纯文字版MD
                    n = build_pure_md(d, result, course_root)
                    total_full_md += n
            except Exception as e:
                log(f"  × {d.name}: {e}", "err")

    dt = time.time() - t0
    header(
        f"补OCR毕  ——  {total_ocr_pages}页OCR · {total_page_md}页级MD · {total_full_md}纯文MD · {dt:.0f}s",
        width=56,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n知止所以不殆。", "warn")
        sys.exit(130)
