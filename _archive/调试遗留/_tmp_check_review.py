import sys; sys.path.insert(0, '.')
from pathlib import Path
from _yc_common import read_json

courses = {
    '环境毒理学': '03_解析成果',
    '环境规划与管理': '02_解析成果',
    '环境法学': '02_解析成果',
    '流体力学': '02_解析成果',
    '地理信息系统': '02_解析成果',
}

for c, sub in courses.items():
    sucai = Path(c) / sub / '_素材'
    if not sucai.exists():
        print(f'{c}: _素材/ 不存在')
        continue
    md_files = sorted(sucai.glob('_第*章_*.md'))
    print(f'\n=== {c} ({len(md_files)} 章) ===')
    for f in md_files:
        text = f.read_text(encoding='utf-8')
        has_review = '复习要点' in text and '## 复习要点' in text
        # check if review section has actual content (not just placeholder)
        lines = text.split('\n')
        in_review = False
        review_content_lines = 0
        for line in lines:
            if '## 复习要点' in line:
                in_review = True
                continue
            if in_review and line.startswith('## '):
                break
            if in_review and line.strip() and not line.startswith('<!--') and not line.startswith('> '):
                review_content_lines += 1
        
        status = '✓已填' if review_content_lines > 3 else '✗待填'
        print(f'  {f.name[:55]:55s} {status} (复习要点行数: {review_content_lines})')
