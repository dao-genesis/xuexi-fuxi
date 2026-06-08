# -*- coding: utf-8 -*-
"""
章号归 · 地理信息系统课
====================
PDF 内无"第N章"字样，自动识别失。按主题手工归四章：
  001 + 002 → 第一章 GIS 概论
  003 + 004 → 第二章 空间数据基础
  005      → 第三章 空间数据的转换与处理
  006      → 第四章 空间数据的可视化表达

跑此脚本后跑：
  python 课程_闭环.py 地理信息系统 --only 聚合,素材,汇编,总览

道：「为之者败之，执之者失之」——故仅改 chapter_num/chapter_raw 之元，
图像与 pages 等本源不动。
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent / "02_解析成果"

MAPPING: dict[str, tuple[int, str]] = {
    "001-地理信息系统 Geographic Information System, GIS-地理信息系统 Geographic Information System, GIS": (1, "第一章"),
    "002-地理信息系统 Geographic Information System, GIS（2）-地理信息系统 Geographic Information System, GIS": (1, "第一章"),
    "003-GIS-空间数据-知识点回顾": (2, "第二章"),
    "004-空间数据-知识点回顾": (2, "第二章"),
    "005-空间数据的转换与处理-空间数据的转换与处理": (3, "第三章"),
    "006-空间数据的可视化表达-空间数据的可视化表达": (4, "第四章"),
}


def main() -> int:
    if not ROOT.exists():
        print(f"× 解析根不存在: {ROOT}", file=sys.stderr)
        return 1

    # ── 一改：每个 _doc.json ──
    print("  ── [改 _doc.json] ──")
    ok_doc = 0
    miss = 0
    for stem, (n, raw) in MAPPING.items():
        p = ROOT / stem / "_doc.json"
        if not p.exists():
            print(f"  × 缺: {stem[:60]}... → {p}", file=sys.stderr)
            miss += 1
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        d["chapter_num"] = n
        d["chapter_raw"] = raw
        d["all_chapter_nums"] = [n]
        d["all_chapter_raws"] = [raw]
        p.write_text(
            json.dumps(d, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        short = stem[:50] + ("..." if len(stem) > 50 else "")
        print(f"  ✓ {short:55s} → {raw} (chap={n})")
        ok_doc += 1

    # ── 二改：_course.json 之 documents ──（聚合关之实读处）
    print("\n  ── [改 _course.json.documents] ──")
    course_json = ROOT / "_course.json"
    if not course_json.exists():
        print(f"  × 缺 _course.json: {course_json}", file=sys.stderr)
        return 3
    cj = json.loads(course_json.read_text(encoding="utf-8"))
    documents = cj.get("documents") or []
    ok_cj = 0
    for doc in documents:
        rel_dir = doc.get("rel_dir") or ""
        # rel_dir 与 MAPPING 之 key 同
        if rel_dir in MAPPING:
            n, raw = MAPPING[rel_dir]
            doc["chapter_num"] = n
            doc["chapter_raw"] = raw
            doc["all_chapter_nums"] = [n]
            doc["all_chapter_raws"] = [raw]
            ok_cj += 1
            print(f"  ✓ {rel_dir[:50]:55s} → chap={n}")
        else:
            print(f"  ? 未匹: {rel_dir[:60]}", file=sys.stderr)
    course_json.write_text(
        json.dumps(cj, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"\n  共改 _doc.json {ok_doc} 件 · _course.json.documents {ok_cj} 项 · 缺 {miss}")
    return 0 if (miss == 0 and ok_cj == len(MAPPING)) else 2


if __name__ == "__main__":
    sys.exit(main())
