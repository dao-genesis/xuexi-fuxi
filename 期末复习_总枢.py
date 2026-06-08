# -*- coding: utf-8 -*-
"""
期末复习 总枢 (final_review_pipeline)  ——  道生一，一生二

道法：
    全链路一键驱动。从雨课堂/本地 PDF 至最终底层复习资料，诸关依次而成。
    增量友好：默认仅做新增 / 重扫，已成者跳。

诸关：
    [一] yk.py pdf             雨课堂 → 初始 PDF（可选）
    [二] pdf_提文.py          PDF → 图像 + 元数据
    [三] 课件_章节聚合.py     按章归一、识跨章
    [四] 课件_知识素材.py     生章节素材 md
    [五] 课件_道喂.py         人/LLM 填章要点（可选：离线/在线/dry）
    [六] 期末_综合汇编.py     生期末骨架/速查/LLM提示/最终复习资料
    [七] 期末_全图.py         学期总图 + 进度 + 待办

用法:
    python 期末复习_总枢.py                    # 全链路·增量
    python 期末复习_总枢.py --fetch-pdf -f 环境毒理
    python 期末复习_总枢.py --rescan           # 仅重扫章节(快)
    python 期末复习_总枢.py -f 环境毒理        # 仅一课
    python 期末复习_总枢.py -f 环境毒理 --feed offline --feed-grid
    python 期末复习_总枢.py -f 环境毒理 --feed online --feed-grid
    python 期末复习_总枢.py -f 环境毒理 --self-boot       # 不取 PDF，仅用本地雨课堂PDF/
    python 期末复习_总枢.py -f 环境毒理 --self-boot --fetch-pdf
    python 期末复习_总枢.py --inline-images    # 第四关用内联图
    python 期末复习_总枢.py --skip 提文        # 跳过某关
    python 期末复习_总枢.py --only 聚合,素材   # 仅跑某几关

全链路图：
    雨课堂 / 已有本地 PDF
        ↓ [一] yk.py pdf（可选）
    雨课堂PDF/<课>/*.pdf
        ↓ [二] pdf_提文
    解析仓库/<课>/<PDF>/page_NNN.jpg + _doc.json
                      <课>/_course.json + _index.json
        ↓ [三] 课件_章节聚合
    解析仓库/<课>/_章节图谱.json + _章节图谱.md  +  _全局图谱.md
        ↓ [四] 课件_知识素材
    解析仓库/<课>/_素材/_第N章_xxx.md + _index.md
        ↓ [五] 课件_道喂（可选）
    解析仓库/<课>/_素材/_第N章_xxx.md（复习要点）
        ↓ [六] 期末_综合汇编
    解析仓库/<课>/_素材/_期末骨架.md + _期末速查.md + _LLM_提示语.md + _最终复习资料.md
        ↓ [七] 期末_全图
    解析仓库/_学期总图.md + _学期总图.json
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _yc_common import log, header  # noqa: E402


def _has_llm_credentials() -> bool:
    """轻量检测 .env / 环境变量中是否有 LLM 凭据；
    本地 ollama / lm-studio 也算（base_url 含 localhost/127）。"""
    try:
        from _llm_道 import LLMConfig
    except Exception:
        return False
    for prof in ("vision", "default", "long"):
        try:
            if LLMConfig.from_env(prof).is_ready():
                return True
        except Exception:
            continue
    return False


def _print_final_artifacts(cwd: Path, course_filter: list[str] | None) -> None:
    """全链路毕后，列出关键产物之路。"""
    repo = cwd / "解析仓库"
    if not repo.exists():
        return
    artifacts: list[tuple[str, Path]] = [
        ("学期总图", repo / "_学期总图.md"),
        ("全局图谱", repo / "_全局图谱.md"),
    ]
    for p in repo.iterdir():
        if not p.is_dir():
            continue
        if course_filter and not any(kw in p.name for kw in course_filter):
            continue
        finals = [
            ("最终复习资料", p / "_素材" / "_最终复习资料.md"),
            ("期末骨架",     p / "_素材" / "_期末骨架.md"),
            ("期末速查",     p / "_素材" / "_期末速查.md"),
            ("章节图谱",     p / "_章节图谱.md"),
        ]
        for label, fp in finals:
            if fp.exists():
                artifacts.append((f"{p.name} · {label}", fp))

    log("\n  关键产物：", "title")
    for label, fp in artifacts:
        if fp.exists():
            sz = fp.stat().st_size
            log(f"    · {label}  ({sz//1024} KiB)\n        {fp}", "dim")


# 关名 → 脚本
STAGES = [
    ("取PDF", "yk.py", "雨课堂 → 初始 PDF"),
    ("提文", "pdf_提文.py", "PDF → 图像 + 元数据"),
    ("聚合", "课件_章节聚合.py", "按章归一、识跨章"),
    ("素材", "课件_知识素材.py", "章节素材 markdown"),
    ("道喂", "课件_道喂.py", "LLM/离线任务 → 章复习要点"),
    ("汇编", "期末_综合汇编.py", "期末骨架 + 速查 + LLM 提示 + 最终复习资料"),
    ("全图", "期末_全图.py", "学期总图 + 进度 + 道喂待办"),
    ("模卷", "期末_模拟卷.py", "据最终复习资料 → 模拟卷（离线/在线）"),
]


def run_stage(name: str, script: str, args: list[str], cwd: Path) -> tuple[bool, float]:
    """执某关。返 (成败, 耗时秒)"""
    script_path = cwd / script
    if not script_path.exists():
        log(f"  × 缺脚本: {script}", "err")
        return False, 0.0

    cmd = [sys.executable, str(script_path), *args]
    log(f"\n┌── [{name}] {script}", "title")
    log(f"│   {' '.join(args) if args else '(无参)'}", "dim")

    t0 = time.time()
    try:
        # 直通子进程之 stdout/stderr，方便实时见输出
        result = subprocess.run(cmd, cwd=str(cwd))
        dt = time.time() - t0
        ok = result.returncode == 0
        if ok:
            log(f"└── [{name}] ✓ ({dt:.1f}s)", "ok")
        else:
            log(f"└── [{name}] × 退码 {result.returncode} ({dt:.1f}s)", "err")
        return ok, dt
    except Exception as e:
        dt = time.time() - t0
        log(f"└── [{name}] × 异: {e} ({dt:.1f}s)", "err")
        return False, dt


def main():
    parser = argparse.ArgumentParser(
        description="期末复习 总枢 —— 道生一，一生二",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    # 流程控制
    parser.add_argument(
        "--only", default=None,
        help="仅跑指定关（逗号分），如 --only 聚合,素材",
    )
    parser.add_argument(
        "--skip", default=None,
        help="跳过指定关（逗号分），如 --skip 提文",
    )
    parser.add_argument(
        "--self-boot", "--闭环", action="store_true",
        help="自举闭环：从本地雨课堂PDF全跑，并在线道喂拼网格，最后汇编/全图；不默认触网取PDF",
    )
    parser.add_argument(
        "--fetch-pdf", action="store_true",
        help="先调用 yk.py pdf 下载雨课堂 PDF（默认不触网）",
    )
    parser.add_argument(
        "--course-id", action="append", default=None,
        help="取PDF阶段指定 classroom_id（可多次；须配 --fetch-pdf）",
    )
    parser.add_argument(
        "--workers", type=int, default=8,
        help="取PDF阶段并发数（默认 8）",
    )
    # 透传给提文
    parser.add_argument(
        "--rescan", action="store_true",
        help="提文阶段仅重扫章节（不动图像）",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="强制重处理（提文阶段）",
    )
    parser.add_argument(
        "--dpi", type=int, default=150,
        help="提文渲染兜底 DPI（默 150）",
    )
    # 透传给素材
    parser.add_argument(
        "--inline-images", action="store_true",
        help="素材阶段·主版每页内联图像",
    )
    parser.add_argument(
        "--max-aux-pages", type=int, default=3,
        help="素材阶段·辅版最多列页数",
    )
    # 透传给道喂
    parser.add_argument(
        "--feed", choices=["none", "offline", "online", "dry"], default="none",
        help="道喂阶段：none 不跑；offline 导出任务；online 在线回写；dry 在线预估",
    )
    parser.add_argument(
        "--feed-grid", "--拼网格", action="store_true",
        help="道喂阶段拼网格图，省 token",
    )
    parser.add_argument(
        "--feed-max-pages", type=int, default=40,
        help="道喂阶段每章最多喂图页数（默认 40）",
    )
    # 模拟卷
    parser.add_argument(
        "--mock", "--模卷", action="store_true",
        help="末关：生模拟卷（默关；--self-boot 自动启）",
    )
    parser.add_argument(
        "--mock-online", action="store_true",
        help="模拟卷阶段在线生（须 .env）。否则离线导出",
    )
    parser.add_argument(
        "--mock-max-chap-chars", type=int, default=6000,
        help="模拟卷阶段单章摘要长上限（默 6000）",
    )
    # 共用
    parser.add_argument(
        "--filter", "-f", action="append", default=None,
        help="课程名关键字过滤（透传至各关）",
    )
    args = parser.parse_args()

    if args.self_boot:
        # 闭环自举：默 online + 拼网格 + 模拟卷；若 .env 无 key 则自动转 offline（不损一物）
        args.feed_grid = True
        args.mock = True
        if _has_llm_credentials():
            args.feed = "online"
            args.mock_online = True
            log("  自举：检得 .env 凭据，在线道喂回写 + 在线模拟卷", "ok")
        else:
            args.feed = "offline"
            args.mock_online = False
            log("  自举：.env 无 LLM 凭据，回落为离线（道喂任务 + 模拟卷提示包）", "warn")
            log("       后续可任喂 LLM playground，再 --only 汇编,全图 纳新填", "dim")

    # 解析 only/skip
    only = {s.strip() for s in args.only.split(",")} if args.only else None
    skip = {s.strip() for s in args.skip.split(",")} if args.skip else set()

    script_dir = Path(__file__).resolve().parent

    header("期末复习 总枢 —— 道生一，一生二", width=58)
    log(f"  根: {script_dir}", "dim")
    if only:
        log(f"  仅跑: {', '.join(only)}", "info")
    if skip:
        log(f"  跳过: {', '.join(skip)}", "info")

    # 各关参数构造
    filter_args = []
    for f in (args.filter or []):
        filter_args.extend(["--filter", f])
    course_filter_args = []
    for f in (args.filter or []):
        course_filter_args.extend(["--课", f])

    # yk.py pdf 只支持单 --filter/--course-id；此处取第一项，精细多课可分次跑
    fetch_args = ["pdf", "--workers", str(args.workers)]
    if args.filter:
        fetch_args.extend(["--filter", args.filter[0]])
    if args.course_id:
        fetch_args.extend(["--course-id", args.course_id[0]])

    feed_args = [
        *course_filter_args,
        *(["--在线"] if args.feed in ("online", "dry") else []),
        *(["--dry"] if args.feed == "dry" else []),
        *(["--拼网格"] if args.feed_grid else []),
        "--max-pages", str(args.feed_max_pages),
    ]

    mock_args = [
        *course_filter_args,
        *(["--在线"] if args.mock_online else []),
        "--max-chap-chars", str(args.mock_max_chap_chars),
    ]

    stage_args = {
        "取PDF": fetch_args,
        "提文": [
            *(["--rescan"] if args.rescan else []),
            *(["--force"] if args.force else []),
            "--dpi", str(args.dpi),
            *filter_args,
        ],
        "聚合": [*filter_args],
        "素材": [
            *(["--inline-images"] if args.inline_images else []),
            "--max-aux-pages", str(args.max_aux_pages),
            *filter_args,
        ],
        "道喂": feed_args,
        "全图": [],  # 全图不限单课
        "汇编": [*filter_args],
        "模卷": mock_args,
    }

    # 依次执行
    total_t = 0.0
    success_count = 0
    skipped_count = 0
    fail_count = 0
    for name, script, desc in STAGES:
        if name == "取PDF" and not args.fetch_pdf:
            log(f"\n  ⊝ [{name}] {desc} (跳：默认不触网，需 --fetch-pdf)", "dim")
            skipped_count += 1
            continue
        if name == "道喂" and args.feed == "none":
            log(f"\n  ⊝ [{name}] {desc} (跳：需 --feed offline/online/dry)", "dim")
            skipped_count += 1
            continue
        if name == "模卷" and not args.mock:
            log(f"\n  ⊝ [{name}] {desc} (跳：需 --mock 或 --self-boot)", "dim")
            skipped_count += 1
            continue
        if only and name not in only:
            log(f"\n  ⊝ [{name}] {desc} (跳：未在 --only 之列)", "dim")
            skipped_count += 1
            continue
        if name in skip:
            log(f"\n  ⊝ [{name}] {desc} (跳：在 --skip 之列)", "dim")
            skipped_count += 1
            continue

        ok, dt = run_stage(name, script, stage_args.get(name, []), script_dir)
        total_t += dt
        if ok:
            success_count += 1
        else:
            fail_count += 1
            log("\n× 此关失败，是否继续？", "warn")
            # 失败即止，避免错上加错
            break

    header(
        f"总枢毕  —— 成 {success_count} · 跳 {skipped_count} · "
        f"败 {fail_count} · 用时 {total_t:.1f}s",
        width=58,
    )

    if fail_count == 0:
        log("\n  道之教：", "title")
        log("    1. 看 _学期总图.md          - 复习总入口", "info")
        log("    2. 看 _全局图谱.md          - 各课总览", "info")
        log("    3. 看 <课>/_素材/_期末骨架.md - 单课入口", "info")
        log("    4. 看 <课>/_素材/_最终复习资料.md - PDF 自举终端", "info")
        if args.feed == "offline":
            log("    5. 已生离线道喂任务包：见 .道喂任务/<课>/<章>.json + grid.jpg", "info")
            log("       将其拖到任意 LLM 网页(ChatGPT/Claude/Kimi/通义...) 喂之", "dim")
            log("       获章 md 后，重跑：python 期末复习_总枢.py -f <课名> --only 汇编,全图", "dim")
        elif args.feed == "online":
            log("    5. 在线道喂已完，复习要点已回写", "info")
        else:
            log("    5. 一键自举（在线/离线自动选）：", "info")
            log("       python 期末复习_总枢.py -f <课名> --self-boot", "dim")
        log("", "info")
        try:
            _print_final_artifacts(script_dir, args.filter)
        except Exception:
            pass


if __name__ == "__main__":
    main()
