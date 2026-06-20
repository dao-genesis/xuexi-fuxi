import os
for c,s in [('环境规划与管理','02_解析成果'),('环境法学','02_解析成果'),('流体力学','02_解析成果'),('地理信息系统','02_解析成果'),('环境毒理学','03_解析成果')]:
    base = os.path.join(c,s)
    if not os.path.isdir(base): continue
    dirs = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base,d)) and os.path.exists(os.path.join(base,d,'_doc.json'))]
    done = [d for d in dirs if os.path.exists(os.path.join(base,d,'_全文.md')) and os.path.getsize(os.path.join(base,d,'_全文.md'))>100]
    tag = 'OK' if len(done)==len(dirs) else '->'
    print(f'  {tag} {c}: {len(done)}/{len(dirs)}')
