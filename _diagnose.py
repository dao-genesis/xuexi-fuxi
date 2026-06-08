# -*- coding: utf-8 -*-
"""深度诊断：解剖 _doc.json 数据质量"""
import json
from pathlib import Path

d = Path("解析仓库/环境毒理学-2026春-090963-001-森巴提·叶尔肯/002-第一章绪论-第一章绪论")
meta = json.loads((d / "_doc.json").read_text("utf-8"))

print("=== _doc.json 结构 ===")
print(f"keys: {list(meta.keys())}")
sample = meta["pages"][0]
print(f"page keys: {list(sample.keys())}")
print()

for p in meta["pages"][:8]:
    idx = p.get("index", "?")
    ocr = p.get("ocr_text", "")
    emb = p.get("embedded_text", "") or p.get("text", "")
    print(f"--- page {idx} ---")
    print(f"  ocr ({len(ocr)}ch): {ocr[:150]}")
    print(f"  emb ({len(emb)}ch): {emb[:150]}")
    print()

# 统计：有多少页有 embedded_text
all_dirs = sorted(
    x for x in d.parent.iterdir()
    if x.is_dir() and (x / "_doc.json").exists()
)
emb_count = 0
ocr_count = 0
total = 0
for dd in all_dirs:
    m = json.loads((dd / "_doc.json").read_text("utf-8"))
    for p in m["pages"]:
        total += 1
        if p.get("ocr_text"):
            ocr_count += 1
        if p.get("embedded_text") or p.get("text"):
            emb_count += 1

print(f"\n=== 全课程统计 ===")
print(f"总页: {total}")
print(f"有 ocr_text: {ocr_count} ({ocr_count*100//total}%)")
print(f"有 embedded_text: {emb_count} ({emb_count*100//total}%)")

# 对比 OCR vs embedded 质量
print("\n=== OCR vs Embedded 质量对比（第1章前10页）===")
m = json.loads((d / "_doc.json").read_text("utf-8"))
for p in m["pages"][:10]:
    idx = p.get("index", "?")
    ocr = p.get("ocr_text", "")
    emb = p.get("embedded_text", "") or p.get("text", "")
    # 水印含量
    wm_ocr = sum(1 for line in ocr.split("\n") if "大学" in line or "University" in line)
    wm_emb = sum(1 for line in emb.split("\n") if "大学" in line or "University" in line)
    # 碎片含量（短英文token）
    frag_ocr = sum(1 for w in ocr.split() if len(w) <= 5 and w.isascii() and not w.isalpha())
    frag_emb = sum(1 for w in emb.split() if len(w) <= 5 and w.isascii() and not w.isalpha())
    print(f"  p{idx:03d}: ocr={len(ocr):4d}ch wm={wm_ocr} frag={frag_ocr} | emb={len(emb):4d}ch wm={wm_emb} frag={frag_emb}")
