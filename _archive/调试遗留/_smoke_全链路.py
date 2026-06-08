# -*- coding: utf-8 -*-
"""
全链路 烟雾测试 (smoke test)  ——  慎终若始，则无败事矣

道法：
    一令查全链：底层之器、关之脚本、产物之态。
    凡有一伤，立显之；万事通则知道隐。

用:
    python _smoke_全链路.py
"""
from __future__ import annotations

import importlib
import sys
import time
from pathlib import Path

_REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(_REPO))


def _绿(s: str) -> str: return f"\033[32m{s}\033[0m"
def _红(s: str) -> str: return f"\033[31m{s}\033[0m"
def _黄(s: str) -> str: return f"\033[33m{s}\033[0m"
def _淡(s: str) -> str: return f"\033[90m{s}\033[0m"


成 = []
败 = []
警 = []


def 验(描述: str, 行: callable) -> None:
    try:
        result = 行()
        if result is False:
            print(f"  {_红('×')} {描述}")
            败.append(描述)
        elif result is None or result is True:
            print(f"  {_绿('✓')} {描述}")
            成.append(描述)
        else:
            print(f"  {_绿('✓')} {描述}  {_淡(str(result))}")
            成.append(描述)
    except Exception as e:
        print(f"  {_红('×')} {描述}  {_淡(f'{type(e).__name__}: {e}')}")
        败.append(描述)


def 注(描述: str, 行: callable) -> None:
    try:
        result = 行()
        if result:
            print(f"  {_淡('·')} {描述}  {_淡(str(result))}")
        else:
            print(f"  {_黄('⚠')} {描述}  {_黄('(空 / 不在)')}")
            警.append(描述)
    except Exception as e:
        print(f"  {_黄('⚠')} {描述}  {_淡(f'{type(e).__name__}: {e}')}")
        警.append(描述)


# ============================================================
# 一、底层之器
# ============================================================

print("\n=== 一 · 底层之器 ===\n")

验("import _yc_common", lambda: importlib.import_module("_yc_common"))
验("import _llm_道", lambda: importlib.import_module("_llm_道"))
验("import _图_道", lambda: importlib.import_module("_图_道"))
验("import _道说_提示库", lambda: importlib.import_module("_道说_提示库"))


def _测_yc_common():
    m = importlib.import_module("_yc_common")
    assert m.cn_to_int("十二") == 12
    assert m.cn_to_int("二十一") == 21
    assert m.detect_chapter("第三章 污染物")[0] == 3
    assert m.detect_chapter("绪论")[0] == 0
    assert m.sanitize_filename("a/b:c?d") == "a_b_c_d"
    return "cn_to_int / detect_chapter / sanitize_filename 皆通"


验("_yc_common 关键函数", _测_yc_common)


def _测_llm_道():
    m = importlib.import_module("_llm_道")
    cfg = m.LLMConfig.from_env()
    assert hasattr(cfg, "api_key")
    assert hasattr(cfg, "base_url")
    assert hasattr(cfg, "model")
    cli = m.LLMClient(cfg)
    msg = m.build_user_message("hi")
    assert msg["role"] == "user"
    msg2 = m.build_user_message("hi", images=[b"fakebytes"])
    assert isinstance(msg2["content"], list)
    return f"client + msg builder 通; ready={cli.config.is_ready()}"


验("_llm_道 client + msg", _测_llm_道)


def _测_llm_缓存():
    m = importlib.import_module("_llm_道")
    cache = m.LLMCache(_REPO / ".llm_cache_test")
    payload = {"model": "test", "messages": [{"role": "user", "content": "hi"}]}
    cache.set(payload, {"content": "hello"})
    hit = cache.get(payload)
    assert hit and hit.get("value", {}).get("content") == "hello"
    # 清理
    import shutil
    shutil.rmtree(cache.root, ignore_errors=True)
    return "set/get 命中"


验("_llm_道 缓存 set/get", _测_llm_缓存)


def _测_图_道():
    m = importlib.import_module("_图_道")
    # 用 PIL 直造一张测图
    from PIL import Image
    import io
    img = Image.new("RGB", (1024, 768), (200, 200, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    src_bytes = buf.getvalue()

    # 缩
    out = m.缩图(src_bytes, max_dim=512)
    assert isinstance(out, bytes) and len(out) > 0

    # 拼网格
    grid = m.拼网格([src_bytes] * 4, cols=2, cell=256, label=False)
    assert len(grid) > 0

    # 估 token
    est = m.估_图_tokens(src_bytes, detail="high")
    assert est > 0

    # 分批
    batches = list(m.分批喂图(["a"] * 25, max_per_batch=10))
    assert len(batches) == 3
    return f"缩/拼/分/估 通 (估={est}tk)"


验("_图_道 全函数", _测_图_道)


def _测_提示库():
    m = importlib.import_module("_道说_提示库")
    t = m.章占位填充任务.build(
        course="测试课", chap_label="第 1 章", chap_title="测试", page_count=10,
    )
    assert t.system and t.user and t.schema
    fake = {"核心概念": [{"name": "x", "def_": "y"}], "高频考点": ["a", "b"]}
    res = m.章占位填充任务.parse(fake)
    assert len(res.核心概念) == 1 and len(res.高频考点) == 2
    md = m.章占位填充任务.render_md(res)
    assert "## 复习要点" in md
    return f"章占位 + 速查行 + 模拟卷 = {len(m.任务注册)} 任务"


验("_道说_提示库 任务全套", _测_提示库)


# ============================================================
# 二、关之脚本（语法 + 帮助文）
# ============================================================

print("\n=== 二 · 关之脚本 ===\n")

import subprocess

关脚本 = [
    "pdf_提文.py",
    "课件_章节聚合.py",
    "课件_知识素材.py",
    "期末_综合汇编.py",
    "课件_道喂.py",
    "期末_全图.py",
    "期末复习_总枢.py",
    "课程_闭环.py",
]

for s in 关脚本:
    p = _REPO / s
    if not p.exists():
        print(f"  {_红('×')} {s} 缺")
        败.append(f"缺脚本 {s}")
        continue
    # 仅编译检查，不执行（避免重跑）
    try:
        compile(p.read_text(encoding="utf-8"), str(p), "exec")
        print(f"  {_绿('✓')} {s}  {_淡(f'{p.stat().st_size//1024} KiB')}")
        成.append(f"compile {s}")
    except SyntaxError as e:
        print(f"  {_红('×')} {s}  {_红(f'SyntaxError: {e}')}")
        败.append(f"语法错 {s}")


# ============================================================
# 三、配置 / 凭据
# ============================================================

print("\n=== 三 · 配置 ===\n")

注(".env.example 在", lambda: (_REPO / ".env.example").stat().st_size)
注(".gitignore 在", lambda: (_REPO / ".gitignore").stat().st_size)
注(".env 配（凭据）", lambda: (_REPO / ".env").stat().st_size if (_REPO / ".env").exists() else None)


def _llm配状():
    m = importlib.import_module("_llm_道")
    states = {}
    for prof in ("default", "vision", "long"):
        cfg = m.LLMConfig.from_env(prof)
        states[prof] = "ready" if cfg.is_ready() else "无 key"
    return states


print(f"  {_淡('·')} LLM profile 状: {_llm配状()}")


# ============================================================
# 四、产物之态
# ============================================================

print("\n=== 四 · 产物之态 ===\n")

仓库 = _REPO / "解析仓库"
雨课堂 = _REPO / "雨课堂PDF"

注("雨课堂PDF/", lambda: f"{len(list(雨课堂.iterdir()))} 课程" if 雨课堂.exists() else None)
注("解析仓库/_index.json", lambda: (仓库 / "_index.json").stat().st_size if (仓库 / "_index.json").exists() else None)
注("解析仓库/_全局图谱.md", lambda: (仓库 / "_全局图谱.md").stat().st_size if (仓库 / "_全局图谱.md").exists() else None)
注("解析仓库/_学期总图.md", lambda: (仓库 / "_学期总图.md").stat().st_size if (仓库 / "_学期总图.md").exists() else None)


def _统_课():
    if not 仓库.exists():
        return None
    all_dirs = [d for d in 仓库.iterdir() if d.is_dir()]
    real = [d for d in all_dirs if (d / "_course.json").exists()]
    empty = len(all_dirs) - len(real)
    chap = sum(1 for c in real if (c / "_章节图谱.json").exists())
    skel = sum(1 for c in real if (c / "_素材" / "_期末骨架.md").exists())
    return f"{len(real)} 实课 + {empty} 空占位, {chap} 章谱, {skel} 骨架"


print(f"  {_淡('·')} 课程汇总: {_统_课()}")


def _道喂态():
    d = _REPO / ".道喂任务"
    if not d.exists():
        return "未生"
    files = list(d.rglob("*.json"))
    grids = list(d.rglob("*_grid.jpg"))
    return f"{len(files)} 任务包, {len(grids)} 拼图"


print(f"  {_淡('·')} 道喂离线产: {_道喂态()}")


def _闭环课夹态():
    """列可闭环之课夹（含 01_原始PDF/ 或 02_原始课件PDF/ 之课夹）"""
    PDF_CANDS = ["01_原始PDF", "02_原始课件PDF", "01_原始pdf"]
    out = []
    for d in sorted(_REPO.iterdir()):
        if not d.is_dir() or d.name.startswith(".") or d.name in {"yuketang", "雨课堂PDF", "解析仓库"}:
            continue
        for c in PDF_CANDS:
            sub = d / c
            if sub.is_dir() and list(sub.glob("*.pdf")):
                # 看有无最终复习资料
                final = None
                for pc in ("02_解析成果", "03_解析成果"):
                    p = d / pc / "_素材" / "_最终复习资料.md"
                    if p.exists():
                        final = "✓"
                        break
                out.append(f"{d.name}({c}, 终{final or '·'})")
                break
    return f"{len(out)} 课: " + ", ".join(out) if out else "0 课"


print(f"  {_淡('·')} 闭环课夹: {_闭环课夹态()}")


def _缓存态():
    d = _REPO / ".llm_cache"
    if not d.exists():
        return "未生（无在线调）"
    files = list(d.rglob("*.json"))
    return f"{len(files)} 条"


print(f"  {_淡('·')} LLM 缓存: {_缓存态()}")


# ============================================================
# 五、文档之态
# ============================================================

print("\n=== 五 · 文档 ===\n")

文档 = ["全链路_道说.md", "雨课堂使用说明.md", "雨课堂PDF索引.md", "YUKETANG_SDK.md"]
for d in 文档:
    p = _REPO / d
    if p.exists():
        size = p.stat().st_size
        print(f"  {_绿('✓')} {d}  {_淡(f'{size//1024} KiB')}")
    else:
        print(f"  {_黄('⚠')} {d} 缺")


# ============================================================
# 六、收口
# ============================================================

print("\n" + "=" * 58)
print(f"  成 {_绿(str(len(成)))} · 警 {_黄(str(len(警)))} · 败 {_红(str(len(败)))}")
print("=" * 58)

if 败:
    print(f"\n{_红('败者:')}")
    for d in 败:
        print(f"  · {d}")
    sys.exit(1)
else:
    print(f"\n  {_绿('道恒无为，而无不为。全链路通。')}")
    sys.exit(0)
