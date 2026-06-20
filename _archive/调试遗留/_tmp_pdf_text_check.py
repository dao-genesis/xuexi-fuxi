# -*- coding: utf-8 -*-
"""临时脚本：检测所有PDF是否有内嵌文字层"""
import fitz, os
from collections import Counter

results = []

# 1. 雨课堂PDF
yk_base = '雨课堂PDF'
if os.path.isdir(yk_base):
    for root, dirs, files in os.walk(yk_base):
        for f in files:
            if f.endswith('.pdf'):
                p = os.path.join(root, f)
                try:
                    doc = fitz.open(p)
                    total = sum(len(page.get_text().strip()) for page in doc)
                    results.append(('雨课堂', os.path.basename(f)[:50], len(doc), total))
                    doc.close()
                except:
                    pass

# 2. 五课课件PDF
for course in ['环境毒理学', '环境规划与管理', '环境法学', '流体力学', '地理信息系统']:
    for sub in ['01_原始PDF', '02_原始课件PDF']:
        base = os.path.join(course, sub)
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            for f in files:
                if f.endswith('.pdf'):
                    p = os.path.join(root, f)
                    try:
                        doc = fitz.open(p)
                        total = sum(len(page.get_text().strip()) for page in doc)
                        results.append((course, os.path.basename(f)[:50], len(doc), total))
                        doc.close()
                    except:
                        pass

# 汇总
has_text = [r for r in results if r[3] > 100]
no_text = [r for r in results if r[3] <= 100]

print(f'=== PDF文字层检测 ===')
print(f'总计: {len(results)} 个PDF')
print(f'有内嵌文字 (>100字符): {len(has_text)}')
print(f'纯图片 (需OCR): {len(no_text)}')
print()

if has_text:
    print('--- 有文字层的PDF ---')
    for course, name, pages, chars in has_text[:20]:
        print(f'  [{course}] {name}: {pages}页, {chars}字符')
    if len(has_text) > 20:
        print(f'  ... 还有 {len(has_text)-20} 个')
else:
    print('--- 所有PDF都是纯图片型，无内嵌文字层 ---')

print()
print('--- 各课统计 ---')
course_stats = Counter()
for course, name, pages, chars in results:
    has = '有文字' if chars > 100 else '纯图片'
    course_stats[(course, has)] += 1
for (course, has), cnt in sorted(course_stats.items()):
    print(f'  {course}: {has} {cnt}个')
