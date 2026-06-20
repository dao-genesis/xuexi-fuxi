import os

for course in ['环境规划与管理', '环境法学', '流体力学']:
    sub = '02_解析成果'
    base = os.path.join(course, sub)
    if not os.path.isdir(base): continue
    dirs = sorted([d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))])
    print(f'\n=== {course} ({len(dirs)} dirs) ===')
    for d in dirs:
        dp = os.path.join(base, d)
        has_doc = os.path.exists(os.path.join(dp, '_doc.json'))
        full_path = os.path.join(dp, '_全文.md')
        has_full = os.path.exists(full_path) and os.path.getsize(full_path) > 100
        jpgs = [f for f in os.listdir(dp) if f.startswith('page_') and f.endswith('.jpg')]
        status = 'done' if has_full else ('hasdoc' if has_doc else 'nodoc')
        print(f'  {status:6s} {d[:55]}  jpgs={len(jpgs)}')
