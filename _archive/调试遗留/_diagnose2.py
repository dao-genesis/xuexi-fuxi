# -*- coding: utf-8 -*-
"""深度诊断：OCR质量 + 标注质量 + 速度瓶颈"""
import json, re, time
from pathlib import Path
from collections import Counter

repo = Path("解析仓库/环境毒理学-2026春-090963-001-森巴提·叶尔肯")

# 1. OCR 碎片分析
print("=== 一、OCR 碎片/噪声分析 ===")
ocr_fragments = Counter()  # 短英文token
wm_lines = 0
total_lines = 0
total_chars = 0
pages_with_ocr = 0

for dd in sorted(repo.iterdir()):
    if not dd.is_dir() or not (dd / "_doc.json").exists():
        continue
    meta = json.loads((dd / "_doc.json").read_text("utf-8"))
    for p in meta["pages"]:
        ocr = p.get("ocr_text", "")
        if not ocr:
            continue
        pages_with_ocr += 1
        total_chars += len(ocr)
        for line in ocr.split("\n"):
            total_lines += 1
            stripped = line.strip()
            if not stripped:
                continue
            # 水印行
            if re.match(r"^(新[蓬雄建疆]?大学|Un?n?ver?si?t[ys]|ngUnn?versit[ys])", stripped, re.I):
                wm_lines += 1
            # 短英文碎片
            for w in stripped.split():
                if len(w) <= 6 and w.isascii() and re.match(r'^[a-zA-Z0-9_/\\]+$', w):
                    ocr_fragments[w] += 1

print(f"总页: {pages_with_ocr}, 总字符: {total_chars}, 总行: {total_lines}")
print(f"水印行: {wm_lines} ({wm_lines*100//max(total_lines,1)}%)")
print(f"\nTop 30 OCR碎片token:")
for frag, cnt in ocr_fragments.most_common(30):
    print(f"  {frag:20s} × {cnt}")

# 2. 标注质量分析
print("\n=== 二、标注质量分析 ===")
annot_index = json.loads((repo / "_图注索引.json").read_text("utf-8"))
type_dist = Counter()
bad_topics = []
bad_keywords = []
for a in annot_index["annotations"]:
    t = a.get("content_type", "other")
    type_dist[t] += 1
    topic = a.get("core_topic", "")
    kws = a.get("keywords", [])
    # 坏主题：纯英文碎片、含OCR噪声
    if topic and len(topic) <= 6 and topic.isascii():
        bad_topics.append((a.get("rel_dir",""), a.get("page",0), topic))
    # 坏关键词
    for kw in kws:
        if len(kw) <= 3 and kw.isascii():
            bad_keywords.append(kw)

print("类型分布:")
for t, n in type_dist.most_common():
    print(f"  {t:15s}: {n}")
print(f"\n坏主题（纯英文碎片）: {len(bad_topics)} 个")
for rd, pg, tp in bad_topics[:20]:
    print(f"  {rd[:40]}/p{pg}: '{tp}'")
print(f"\n坏关键词（≤3字符英文）: {len(bad_keywords)} 个")
bk_counter = Counter(bad_keywords)
for kw, cnt in bk_counter.most_common(20):
    print(f"  '{kw}' × {cnt}")

# 3. 速度瓶颈分析
print("\n=== 三、速度瓶颈 ===")
# 检查 OCR 耗时记录
total_pages = sum(len(json.loads((dd/"_doc.json").read_text("utf-8"))["pages"]) 
                  for dd in sorted(repo.iterdir()) 
                  if dd.is_dir() and (dd/"_doc.json").exists())
print(f"总页数: {total_pages}")
print(f"实测 OCR 速度: ~8s/页 (RapidOCR CPU)")
print(f"全课 OCR 耗时: ~{total_pages * 8 // 60} 分钟")
print(f"瓶颈: RapidOCR 逐页串行处理，无并行")

# 4. 根本问题汇总
print("\n=== 四、根本问题诊断 ===")
print("1. OCR是唯一文本源（embedded_text=0），质量决定一切下游")
print("2. OCR碎片（source/from/ptag等）→ 污染core_topic和keywords")
print("3. 水印虽已过滤但仍残留在ocr_text原始数据中（仅标注时过滤）")
print("4. 49% 'other' 分类 → 启发式规则太弱，无法覆盖课件常见模式")
print("5. OCR速度 ~8s/页 → 767页需~100分钟，不可接受")
print("6. core_topic提取取首行 → 经常是章节号而非核心主题")
print("7. 无并行处理 → 单线程瓶颈")
