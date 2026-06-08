# -*- coding: utf-8 -*-
"""道法自然·OCR推进到底 v2 — 强制重跑未完成目录"""
import sys, os, time, traceback
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.stdout.reconfigure(line_buffering=True)

from pdf2md_引擎 import ocr_doc_dir
from _yc_common import log, header, read_json

COURSES = [
    ("环境规划与管理", "02_解析成果"),
    ("环境法学", "02_解析成果"),
    ("流体力学", "02_解析成果"),
    ("地理信息系统", "02_解析成果"),
    ("环境毒理学", "03_解析成果"),
]

def main():
    header("道法自然·OCR推进到底 v2  ——  无为而无不为", width=56)
    t0 = time.time()
    total_ocr = 0
    total_err = 0
    total_done = 0

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

        # 找未完成的
        todo = []
        for d in doc_dirs:
            full_md = d / "_全文.md"
            if not full_md.exists() or full_md.stat().st_size <= 100:
                todo.append(d)

        done_count = len(doc_dirs) - len(todo)
        print(f"\n┌── {course_name} ({done_count}/{len(doc_dirs)} 已完成, {len(todo)} 待OCR)")

        if not todo:
            print(f"  ✓ 全部完成")
            continue

        for d in todo:
            print(f"  → {d.name[:55]} OCR中...", flush=True)
            try:
                result = ocr_doc_dir(d, force=False)
                if result:
                    ocr_pages = sum(1 for p in result.get("pages", []) if p.get("ocr_text"))
                    total_ocr += ocr_pages
                    total_done += 1
                    print(f"  ✓ {d.name[:55]} OCR {ocr_pages}页", flush=True)
                else:
                    print(f"  · {d.name[:55]} 无可OCR页", flush=True)
            except KeyboardInterrupt:
                print("\n知止所以不殆。")
                sys.exit(130)
            except Exception as e:
                total_err += 1
                print(f"  × {d.name[:55]}: {e}", flush=True)
                traceback.print_exc()
                continue

    dt = time.time() - t0
    header(f"OCR毕  ——  {total_done}完成 · {total_ocr}页OCR · {total_err}错误 · {dt:.0f}s", width=56)


if __name__ == "__main__":
    main()
