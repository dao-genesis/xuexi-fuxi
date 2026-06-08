# -*- coding: utf-8 -*-
"""道法自然·OCR推进到底 — 无为而无不为"""
import sys, os, time, traceback
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# 强制unbuffered输出
sys.stdout.reconfigure(line_buffering=True)

from pdf_提文 import ocr_document, _build_full_markdown
from _yc_common import log, header

COURSES = [
    ("环境规划与管理", "02_解析成果"),
    ("环境法学", "02_解析成果"),
    ("流体力学", "02_解析成果"),
    ("地理信息系统", "02_解析成果"),
    ("环境毒理学", "03_解析成果"),
]

def build_page_md(doc_dir, meta):
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
        md_path = pages_dir / f"page_{idx:03d}.md"
        if md_path.exists() and md_path.stat().st_size > 20:
            continue
        lines = [f"# {title} — 第 {idx} 页", "", f"> 来源: {pdf_name}", f"> 页码: {idx}", "", f"![page {idx}](../{img})", ""]
        if ocr and ocr.strip():
            from pdf_提文 import _simple_text_to_md
            lines.append(_simple_text_to_md(ocr.strip()))
        else:
            lines.append("> *此页无文字*")
        md_path.write_text("\n".join(lines), encoding="utf-8")
        count += 1
    return count


def main():
    header("道法自然·OCR推进到底  ——  无为而无不为", width=56)
    t0 = time.time()
    total_ocr = 0
    total_err = 0

    for course_name, parse_subdir in COURSES:
        course_root = SCRIPT_DIR / course_name
        parse_dir = course_root / parse_subdir
        if not parse_dir.exists():
            print(f"  ∅ {course_name}: 目录不存在")
            continue

        doc_dirs = sorted(d for d in parse_dir.iterdir() if d.is_dir() and (d / "_doc.json").exists())
        if not doc_dirs:
            print(f"  ∅ {course_name}: 无_doc.json")
            continue

        # 统计已完成
        done = sum(1 for d in doc_dirs if (d / "_全文.md").exists() and (d / "_全文.md").stat().st_size > 100)
        print(f"\n┌── {course_name} ({done}/{len(doc_dirs)} 已完成)")

        for d in doc_dirs:
            full_md = d / "_全文.md"
            if full_md.exists() and full_md.stat().st_size > 100:
                print(f"  · {d.name[:50]:50s} 已完成")
                continue

            print(f"  → {d.name[:50]:50s} OCR中...")
            try:
                result = ocr_document(d, force=False, use_v2=True)
                if result:
                    ocr_pages = sum(1 for p in result.get("pages", []) if p.get("ocr_text"))
                    total_ocr += ocr_pages
                    print(f"  ✓ {d.name[:50]:50s} OCR {ocr_pages}页")
                    n = build_page_md(d, result)
                    if n > 0:
                        print(f"    ↳ 页级MD: +{n}")
            except KeyboardInterrupt:
                print("\n知止所以不殆。")
                sys.exit(130)
            except Exception as e:
                total_err += 1
                print(f"  × {d.name[:50]}: {e}")
                traceback.print_exc()
                continue

    dt = time.time() - t0
    header(f"OCR毕  ——  {total_ocr}页 · {total_err}错误 · {dt:.0f}s", width=56)


if __name__ == "__main__":
    main()
