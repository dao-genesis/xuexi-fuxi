# -*- coding: utf-8 -*-
"""
课程 闭环 (course_self_bootstrap)  ——  反者，道之动也

道法：
    *反者道之动，弱者道之用。*
    雨课堂 PDF 山，一旦整理迁入 <课>/01_原始PDF/，即以课夹为本，
    单课自成闭环：不绑全局 雨课堂PDF/解析仓库，单课可独立全跑。
    从初始 PDF 至最终底层复习资料，无外赖之患。

链路（皆于课夹内）：
    <课>/01_原始PDF/*.pdf  (或 02_原始课件PDF/)
        │ [一] 提文
        ▼
    <课>/02_解析成果/<PDF_stem>/page_*.jpg + _doc.json
                       /_course.json
        │ [二] 聚合
        ▼
    <课>/02_解析成果/_章节图谱.{json,md}
        │ [三] 素材
        ▼
    <课>/02_解析成果/_素材/_第N章_*.md  +  _index.md
        │ [四] 道喂（可选：离线/在线/dry）
        ▼
    <课>/02_解析成果/_素材/_第N章_*.md  (回写复习要点)
    .道喂任务/<课>/第N章_*.json + *_grid.jpg  (若离线·全局)
        │ [五] 回填（自 _resp/<同名>.json 回写章 md）
        ▼
    <课>/02_解析成果/_素材/_第N章_*.md  (复习要点既填)
        │ [六] 汇编
        ▼
    <课>/02_解析成果/_素材/_期末骨架.md
                       /_期末速查.md
                       /_LLM_提示语.md
                       /_最终复习资料.md   ★ 终
        │ [七] 模拟卷（默离线·亦可在线）
        ▼
    .模拟卷任务/<课>_期末模拟卷.json + _提示.md  (离线·全局)
    <课>/02_解析成果/_素材/_期末模拟卷.md  (在线·须 .env 配 LLM)
        │ [八] 总览（汇集前七关之态）
        ▼
    <课>/00_闭环总览.md   ← 自动重生

用法：
    python 课程_闭环.py                        # 列可闭环课夹
    python 课程_闭环.py 环境法学               # 单课·增量
    python 课程_闭环.py 环境法学 环境毒理学    # 多课
    python 课程_闭环.py --全                   # 全部可闭环课夹依次
    python 课程_闭环.py 环境法学 --feed offline --grid
    python 课程_闭环.py 环境法学 --feed online --grid
    python 课程_闭环.py 环境法学 --rescan      # 仅重扫章节信号
    python 课程_闭环.py 环境法学 --ocr         # 提文 + OCR 识文 → _全文.md
    python 课程_闭环.py 环境法学 --only 素材,汇编,总览
    python 课程_闭环.py 环境法学 --skip 道喂

约：
    若 <课>/02_解析成果/_course.json 既存（含教师/学期等），新跑保留之；
    凡先前手填或既有之素材内"复习要点"区段，重生时自动保全（赖既有素材关之 preserve）。
    不损一物。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import time
import traceback
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from _yc_common import (  # noqa: E402
    log, header, write_json, read_json,
    sanitize_filename, parse_course_dirname,
)


# ============================================================
# 一、课夹识别
# ============================================================

# 可能的子夹名（按优先序）
PDF_DIR_CANDIDATES = ["01_原始PDF", "02_原始课件PDF", "01_原始pdf"]
PARSE_DIR_CANDIDATES = ["02_解析成果", "03_解析成果"]
# 课夹内之 legacy 道喂夹（向后兼容，只读不写）
LEGACY_FEED_DIR_CANDIDATES = ["03_道喂任务", "04_道喂任务"]
# 道喂任务之主居所——全局 .道喂任务/<课夹名>/
# 与既有 课件_道喂.py、课件_回填.py 之 _道喂根 = .道喂任务 之约定融
GLOBAL_FEED_ROOT_NAME = ".道喂任务"

# 不视为课夹的目录
EXCLUDE_NAMES = {
    "yuketang", "雨课堂PDF", "解析仓库", "__pycache__",
    ".llm_cache", ".yuketang", ".图道_测试", ".道喂任务",
    ".模拟卷任务", "_archive",
}


def _find_dir(parent: Path, candidates: list[str], must_exist: bool = False) -> Optional[Path]:
    """从候选名中找第一个存在的；不存在则返第一个（待建）。"""
    for cand in candidates:
        p = parent / cand
        if p.is_dir():
            return p
    if must_exist:
        return None
    return parent / candidates[0]


def 识别课夹(p: Path) -> Optional[dict]:
    """识别一目录是否为可闭环之课夹。

    道喂任务居于全局 .道喂任务/<课夹名>/——与既有 课件_道喂/课件_回填 之约定一。
    legacy_feed_dir 若存（课夹内旧版 03_道喂任务/），仅作回顾用。
    """
    if not p.is_dir() or p.name.startswith(".") or p.name in EXCLUDE_NAMES:
        return None
    # 必有 PDF 之原始夹
    pdf_dir = None
    for cand in PDF_DIR_CANDIDATES:
        d = p / cand
        if d.is_dir() and list(d.glob("*.pdf")):
            pdf_dir = d
            break
    if pdf_dir is None:
        return None
    parse_dir = _find_dir(p, PARSE_DIR_CANDIDATES)
    # 道喂任务·全局位置（主）
    feed_dir = ROOT / GLOBAL_FEED_ROOT_NAME / p.name
    # 课夹内之 legacy 道喂夹（若存）
    legacy_feed_dir = _find_dir(p, LEGACY_FEED_DIR_CANDIDATES, must_exist=True)
    return {
        "course_root": p,
        "pdf_dir": pdf_dir,
        "parse_dir": parse_dir,
        "feed_dir": feed_dir,
        "legacy_feed_dir": legacy_feed_dir,
        "course_name": p.name,
    }


def 列闭环课夹(workspace_root: Path) -> list[dict]:
    """扫工作区，列所有可闭环之课夹。"""
    out = []
    for d in sorted(workspace_root.iterdir()):
        info = 识别课夹(d)
        if info:
            out.append(info)
    return out


# ============================================================
# 二、提文（PDF → 图 + _doc.json + _course.json）
# ============================================================

def 关_提文(info: dict, *, force: bool = False, dpi: int = 150, rescan: bool = False, ocr: bool = False) -> Optional[dict]:
    """从 <课>/01_原始PDF/*.pdf 提文至 <课>/02_解析成果/<stem>/。

    若 <课>/02_解析成果/_course.json 既存，则保留其 teacher/semester/course_name 等。
    ocr=True 时，取图后自动 OCR 识文 + 生成 _全文.md。
    """
    from pdf_提文 import extract_pdf_pages, rescan_doc_chapters, ocr_document, _OCR_ENGINE
    from _yc_common import parse_pdf_filename

    pdf_files = sorted(info["pdf_dir"].glob("*.pdf"))
    if not pdf_files:
        log("  ∅ 无 PDF", "warn")
        return None

    info["parse_dir"].mkdir(parents=True, exist_ok=True)

    # 既有 _course.json 之元数据（保留）
    existing_course = read_json(info["parse_dir"] / "_course.json") or {}
    course_name_kept = existing_course.get("course_name") or info["course_name"]
    teacher_kept = existing_course.get("teacher", "")
    semester_kept = existing_course.get("semester", "")
    class_code_kept = existing_course.get("class_code", "")
    course_dir_kept = existing_course.get("course_dir") or info["course_name"]
    # 若 _course.json 无（首跑），则尝试从课夹名解析（多数为单名如"环境法学"）
    if not teacher_kept and not semester_kept:
        parsed = parse_course_dirname(info["course_name"])
        if parsed.get("teacher"):
            teacher_kept = parsed["teacher"]
        if parsed.get("semester"):
            semester_kept = parsed["semester"]
        if parsed.get("course_name") and parsed.get("course_name") != info["course_name"]:
            course_name_kept = parsed["course_name"]

    log(f"  共 {len(pdf_files)} PDF", "info")
    log(f"  课程: {course_name_kept} | 教师: {teacher_kept or '?'} | 学期: {semester_kept or '?'}", "dim")

    docs = []
    skipped = processed = rescanned_n = failed = 0
    for pdf in pdf_files:
        out_dir = info["parse_dir"] / sanitize_filename(pdf.stem, max_len=120)
        meta_path = out_dir / "_doc.json"

        # rescan only：仅刷章节信号
        if rescan and meta_path.exists():
            meta = rescan_doc_chapters(meta_path)
            if meta:
                docs.append(meta)
                rescanned_n += 1
                continue

        # 增量：已成且未 force 则跳
        if not force and meta_path.exists():
            old = read_json(meta_path)
            if old and old.get("page_count", 0) > 0:
                pages = old.get("pages", [])
                if all((out_dir / p["image"]).exists() for p in pages if p.get("image")):
                    docs.append(old)
                    skipped += 1
                    log(f"  ⊝ {pdf.name[:55]:55s} (跳, 已成 {old.get('page_count')}页)", "dim")
                    continue

        try:
            t0 = time.time()
            meta = extract_pdf_pages(pdf, out_dir, dpi_fallback=dpi, force=force)
            dt = time.time() - t0
            docs.append(meta)
            processed += 1
            chap = (
                f"第{meta['chapter_num']}章"
                if meta.get("chapter_num") is not None
                else "无章号"
            )
            log(f"  ✓ {pdf.name[:55]:55s} ({meta['page_count']:3d}页, {chap}, {dt:.1f}s)", "ok")

            # 取图后即 OCR（若启）
            if ocr and _OCR_ENGINE is not None:
                try:
                    ocr_document(out_dir, force=force)
                except Exception as e:
                    log(f"    × OCR 败: {e}", "warn")

        except Exception as e:
            log(f"  × {pdf.name}: {e}", "err")
            failed += 1

    course_meta = {
        "course_dir": course_dir_kept,
        "course_root_name": info["course_name"],
        "course_name": course_name_kept,
        "semester": semester_kept,
        "class_code": class_code_kept,
        "teacher": teacher_kept,
        "pdf_count": len(pdf_files),
        "processed": processed,
        "rescanned": rescanned_n,
        "skipped": skipped,
        "failed": failed,
        "documents": [
            {
                "pdf_name": d.get("pdf_name"),
                "lesson_seq": d.get("lesson_seq"),
                "lesson_title": d.get("lesson_title"),
                "presentation_title": d.get("presentation_title"),
                "chapter_num": d.get("chapter_num"),
                "chapter_raw": d.get("chapter_raw"),
                "all_chapter_nums": d.get("all_chapter_nums", []),
                "all_chapter_raws": d.get("all_chapter_raws", []),
                "page_count": d.get("page_count"),
                "rel_dir": sanitize_filename(Path(d.get("pdf_name", "")).stem, max_len=120),
            }
            for d in docs
        ],
    }
    write_json(info["parse_dir"] / "_course.json", course_meta)
    log(f"  └ 处 {processed} · 跳 {skipped} · 重 {rescanned_n} · 失 {failed}", "info")
    return course_meta


# ============================================================
# 三、聚合（按章节归一）
# ============================================================

def 关_聚合(info: dict) -> Optional[dict]:
    """以 <课>/02_解析成果/ 为虚拟"课目录"，行章节聚合。"""
    from 课件_章节聚合 import aggregate_course, chart_to_markdown

    chart = aggregate_course(info["parse_dir"])
    if not chart:
        log("  × 聚合失（缺 _course.json）", "err")
        return None
    md = chart_to_markdown(chart)
    (info["parse_dir"] / "_章节图谱.md").write_text(md, encoding="utf-8")

    nc = len(chart.get("chapters", []))
    nl = len(chart.get("non_lecture", []))
    un = len(chart.get("uncategorized", []))
    log(f"  ✓ {nc} 章节 · 非教 {nl} · 未归 {un}", "ok")
    return chart


# ============================================================
# 四、素材（按章生 markdown）
# ============================================================

def 关_素材(info: dict, *, inline_images: bool = False, max_aux_pages: int = 3) -> dict:
    """生 <课>/02_解析成果/_素材/_第N章_*.md"""
    from 课件_知识素材 import generate_course_materials

    result = generate_course_materials(
        info["parse_dir"],
        inline_images=inline_images,
        max_pages_per_aux=max_aux_pages,
    )
    log(f"  ✓ {result.get('generated', 0)} 章 md → _素材/", "ok")
    return result


# ============================================================
# 五、道喂（离线/在线/dry）
# ============================================================

def _构_道喂任务(info: dict) -> list[dict]:
    """从课夹之 _章节图谱.json 构 task 列表，与 课件_道喂.scan_chapters 同规。"""
    chart = read_json(info["parse_dir"] / "_章节图谱.json")
    if not chart:
        return []
    tasks = []
    for ch in chart.get("chapters", []):
        n = ch.get("chapter_num")
        title = ch.get("chapter_title", "")
        t_clean = sanitize_filename(title or "无题", max_len=40).strip()
        if n == 0:
            fname = f"_第00章_{t_clean}.md".replace(" ", "_")
        else:
            fname = f"_第{n:02d}章_{t_clean}.md".replace(" ", "_")
        md_path = info["parse_dir"] / "_素材" / fname
        primary = ch.get("primary", {})
        cross = set()
        for d in ch.get("all_docs", []) or []:
            for c2 in d.get("all_chapter_nums", []) or []:
                if c2 != n:
                    cross.add(c2)
        tasks.append({
            "course_dir": str(info["parse_dir"]),
            "course_name": chart.get("course_name", info["course_name"]),
            "teacher": chart.get("teacher", ""),
            "semester": chart.get("semester", ""),
            "chap_num": n,
            "chap_title": title,
            "md_path": str(md_path),
            "primary_rel_dir": primary.get("rel_dir", ""),
            "primary_pages": primary.get("page_count", 0),
            "primary_lesson_seq": primary.get("lesson_seq"),
            "cross_chapters": sorted(cross),
        })
    return tasks


def _取主版页(task: dict) -> list[Path]:
    """从 task 取主版所有 page_*.jpg 真实路径。"""
    pdf_dir = Path(task["course_dir"]) / task["primary_rel_dir"]
    meta = read_json(pdf_dir / "_doc.json")
    if not meta:
        return []
    pages = []
    for p in meta.get("pages", []):
        img = p.get("image", "")
        if img:
            ip = pdf_dir / img
            if ip.exists():
                pages.append(ip)
    return pages


def _道喂_离线(info: dict, tasks: list[dict], *, grid: bool = False) -> dict:
    """离线导出至全局 .道喂任务/<课夹名>/。

    所有路径以 ROOT 为基相对——与 课件_回填.py 之 `_REPO / md_rel` 解析一。
    """
    from _道说_提示库 import 章占位填充任务

    info["feed_dir"].mkdir(parents=True, exist_ok=True)
    成 = 失 = 0
    for t in tasks:
        try:
            prompt_task = 章占位填充任务.build(
                course=t["course_name"],
                chap_label=f"第 {t['chap_num']} 章" if t["chap_num"] else "绪论",
                chap_title=t["chap_title"],
                page_count=t["primary_pages"],
                teacher=t["teacher"],
                semester=t["semester"],
                cross_chapters=t["cross_chapters"],
            )

            pages = _取主版页(t)
            page_paths_rel = [str(p.relative_to(ROOT)) for p in pages]

            grid_path = None
            if grid and pages:
                try:
                    from _图_道 import 拼网格 as 拼
                    import math
                    cols = min(4, max(2, math.ceil(math.sqrt(len(pages)))))
                    grid_out = info["feed_dir"] / f"第{t['chap_num']:02d}章_grid.jpg"
                    拼(pages, cols=cols, cell=400, out=grid_out)
                    grid_path = str(grid_out.relative_to(ROOT))
                except Exception as e:
                    log(f"    ⚠ 拼图失: {e}", "warn")

            existing = ""
            md = Path(t["md_path"])
            if md.exists():
                existing = md.read_text(encoding="utf-8")

            title_part = (t["chap_title"] or "无题")[:30]
            chap_label = f"第{t['chap_num']:02d}章"
            out_json = info["feed_dir"] / f"{chap_label}_{title_part}.json"
            payload = {
                "task": prompt_task.meta,
                "system": prompt_task.system,
                "user": prompt_task.user,
                "schema": prompt_task.schema,
                "page_count": len(pages),
                "page_paths": page_paths_rel,
                "grid_path": grid_path,
                "md_path_to_write_back": str(md.relative_to(ROOT)) if md.exists() else None,
                "已有笔记长": len(existing),
            }
            out_json.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            log(f"  ✓ {chap_label} → {out_json.name}", "ok")
            成 += 1
        except Exception as e:
            log(f"  × 第{t['chap_num']}章: {e}", "err")
            失 += 1
    return {"success": 成, "failed": 失, "mode": "offline"}


def _道喂_在线(
    info: dict,
    tasks: list[dict],
    *,
    grid: bool = False,
    max_pages: int = 40,
    dry_run: bool = False,
) -> dict:
    """在线调 LLM，回写章 md。"""
    from 课件_道喂 import 在线协填
    from _llm_道 import LLMClient

    cli = LLMClient.from_env(profile="vision")
    if not cli.config.is_ready():
        cli = LLMClient.from_env(profile="default")
    if not cli.config.is_ready():
        log("  × 未配 LLM（.env 缺 API key）", "err")
        return {"skipped": True, "reason": "no_llm"}
    log(f"  LLM: {cli.config.describe()}", "info")

    成 = 失 = 0
    for t in tasks:
        try:
            ok, msg = 在线协填(
                t, 拼网格=grid, max_pages=max_pages, dry_run=dry_run,
            )
            mark = "✓" if ok else "×"
            log(f"  {mark} 第{t['chap_num']}章: {msg}", "ok" if ok else "err")
            成 += int(ok)
            失 += int(not ok)
        except Exception as e:
            log(f"  × 第{t['chap_num']}章: {e}", "err")
            失 += 1
    return {"success": 成, "failed": 失, "mode": "online", "dry_run": dry_run}


def 关_道喂(
    info: dict,
    *,
    mode: str = "none",
    grid: bool = False,
    max_pages: int = 40,
    chap_filter: Optional[set] = None,
) -> dict:
    """道喂分支。mode = none | offline | online | dry

    离线导出至 .道喂任务/<课夹名>/（全局）。
    """
    if mode == "none":
        log("  ⊝ 跳（未指 --feed）", "dim")
        return {"skipped": True}

    tasks = _构_道喂任务(info)
    if chap_filter:
        tasks = [t for t in tasks if t["chap_num"] in chap_filter]
    if not tasks:
        log("  ∅ 无可填章节（先成 _章节图谱.json）", "warn")
        return {"skipped": True}

    log(f"  待填 {len(tasks)} 章", "info")
    if mode == "offline":
        return _道喂_离线(info, tasks, grid=grid)
    return _道喂_在线(info, tasks, grid=grid, max_pages=max_pages, dry_run=(mode == "dry"))


# ============================================================
# 六、回填（道喂之对偶——从 _resp/ 回写章 md）
# ============================================================

def 关_回填(info: dict, *, dry: bool = False) -> dict:
    """扫 .道喂任务/<课>/_resp/<章>.json，回写对应章 md 之"复习要点"。

    与 课件_回填.py 之约定一：响应文件须与 task 同名置于 _resp/ 下。
    """
    feed_dir = info["feed_dir"]
    resp_dir = feed_dir / "_resp"
    if not resp_dir.is_dir():
        rel = resp_dir.relative_to(ROOT).as_posix()
        log(f"  ⊝ 无 _resp/ 目录（{rel}）", "dim")
        return {"skipped": True, "reason": "no_resp_dir"}

    pairs: list[tuple[Path, Path]] = []
    for resp_file in sorted(resp_dir.glob("*.json")):
        task_file = feed_dir / resp_file.name
        if not task_file.exists():
            log(f"  ⚠ {resp_file.name}: 无对应 task，跳", "warn")
            continue
        pairs.append((task_file, resp_file))

    if not pairs:
        log("  ∅ _resp/ 中无可回填", "warn")
        return {"skipped": True, "reason": "no_pairs"}

    log(f"  待回填 {len(pairs)} 章", "info")

    try:
        from 课件_回填 import 回填一章
    except Exception as e:
        log(f"  × 无法引入 课件_回填: {e}", "err")
        return {"skipped": True, "reason": f"import: {e}"}

    成 = 失 = 0
    for task_path, resp_path in pairs:
        try:
            resp_text = resp_path.read_text(encoding="utf-8")
            ok, msg = 回填一章(task_path, resp_text, dry=dry)
            mark = "✓" if ok else "×"
            log(f"  {mark} {resp_path.name}: {msg}", "ok" if ok else "err")
            if ok:
                成 += 1
            else:
                失 += 1
        except Exception as e:
            log(f"  × {resp_path.name}: {e}", "err")
            失 += 1
    return {"success": 成, "failed": 失, "total": len(pairs)}


# ============================================================
# 七、汇编（生骨架/速查/LLM提示/最终复习资料）
# ============================================================


def 关_汇编(info: dict) -> dict:
    """生 _素材/_期末骨架.md / _期末速查.md / _LLM_提示语.md / _最终复习资料.md"""
    from 期末_综合汇编 import compile_course

    result = compile_course(info["parse_dir"])
    if result.get("skipped"):
        log(f"  ⊝ 跳: {result.get('reason', '无图谱')}", "dim")
    else:
        log(
            f"  ✓ {result.get('chapters', 0)} 章 · "
            f"{result.get('files', 0)} 个汇编文件",
            "ok",
        )
    return result


# ============================================================
# 七·三、学习系统（备考总纲 · 自测题库 · 速记卡）
# ============================================================

def 关_学习系统(info: dict, *, 考试日=None) -> dict:
    """生 _学习系统/00_备考总纲.md · 自测题库.md · 速记卡.md

    道法：骨已立、肉已生，此关以"提取练习"与"间隔重复"固已得之知。
          纯离线（不调 LLM），由已有素材 + 章节图谱即出。
    """
    from datetime import date, timedelta
    from 期末_学习系统 import 处理一课

    今日 = date.today()
    考 = 考试日 or (今日 + timedelta(days=21))
    result = 处理一课(info["parse_dir"], 今日, 考)
    if result.get("skipped"):
        log("  ⊝ 跳: 无图谱/无章", "dim")
    else:
        log(
            f"  ✓ {result.get('filled', 0)}/{result.get('chapters', 0)} 章已填 "
            f"→ _学习系统/（备考总纲 · 自测题库 · 速记卡）",
            "ok",
        )
    return result


# ============================================================
# 七·五、图谱（思维导图生成关）
# ============================================================

def 关_图谱(
    info: dict,
    *,
    mode: str = "none",
    chap_filter: Optional[set] = None,
    dry: bool = False,
) -> dict:
    """思维导图生成关。mode = none | offline | online | writeback

    · none      — 跳（默认，不影响已有流程）
    · offline   — 离线导出至 .道喂任务/<课>/图谱/*.json
    · online    — 在线 LLM 生成 → 回写章 md
    · writeback — 从 .道喂任务/<课>/图谱/_resp/*.json 回填
    """
    if mode == "none":
        log("  ⊝ 跳（未指 --图谱）", "dim")
        return {"skipped": True}

    try:
        from 课件_图谱 import 生成图谱
    except Exception as e:
        log(f"  × 无法引入 课件_图谱: {e}", "err")
        return {"error": str(e)}

    return 生成图谱(
        info["parse_dir"],
        info["feed_dir"],
        mode=mode,
        chap_filter=chap_filter,
        dry=dry,
    )


# ============================================================
# 八、总览（00_闭环总览.md）
# ============================================================

_REVIEW_H2 = re.compile(r"^##\s+复习要点.*?$", re.MULTILINE)
_NEXT_H2 = re.compile(r"^##\s+", re.MULTILINE)


def _已填复习要点(content: str) -> bool:
    """同 期末_全图._已填复习要点。"""
    m = _REVIEW_H2.search(content)
    if not m:
        return False
    rest = content[m.end():]
    nxt = _NEXT_H2.search(rest)
    section = rest[: nxt.start()] if nxt else rest
    section = section.strip()
    if not section:
        return False
    if "LLM 未填" in section and len(section) < 240:
        return False
    return True


def _统计课夹(info: dict) -> dict:
    """扫课夹之各态。"""
    pdf_files = sorted(info["pdf_dir"].glob("*.pdf"))
    parse_dir = info["parse_dir"]
    course_meta = read_json(parse_dir / "_course.json") or {}
    chart = read_json(parse_dir / "_章节图谱.json") or {}
    chapters = chart.get("chapters", []) or []
    non_lecture = chart.get("non_lecture", []) or []
    uncat = chart.get("uncategorized", []) or []

    chap_states = []
    filled_count = 0
    for ch in chapters:
        n = ch.get("chapter_num")
        title = ch.get("chapter_title", "")
        t_clean = sanitize_filename(title or "无题", max_len=40).strip()
        if n == 0:
            fname = f"_第00章_{t_clean}.md".replace(" ", "_")
        else:
            fname = f"_第{n:02d}章_{t_clean}.md".replace(" ", "_")
        md_path = parse_dir / "_素材" / fname
        filled = False
        size = 0
        if md_path.exists():
            try:
                content = md_path.read_text(encoding="utf-8")
                size = len(content.encode("utf-8"))
                if _已填复习要点(content):
                    filled = True
                    filled_count += 1
            except Exception:
                pass
        chap_states.append({
            "num": n,
            "title": title,
            "fname": fname,
            "primary_pages": ch.get("primary", {}).get("page_count", 0),
            "all_doc_count": len(ch.get("all_docs", []) or []),
            "filled": filled,
            "md_size": size,
            "md_exists": md_path.exists(),
        })

    material_dir = parse_dir / "_素材"
    has_skel = (material_dir / "_期末骨架.md").exists()
    has_quick = (material_dir / "_期末速查.md").exists()
    has_prompt = (material_dir / "_LLM_提示语.md").exists()
    has_final = (material_dir / "_最终复习资料.md").exists()

    # 全局道喂任务态（.道喂任务/<课夹名>/）
    feed_dir = info["feed_dir"]
    feed_files: list[Path] = []
    if feed_dir.exists():
        feed_files = sorted(
            [p for p in feed_dir.iterdir() if p.is_file()]
        )
    # 回填响应态（.道喂任务/<课夹名>/_resp/）
    resp_dir = feed_dir / "_resp"
    resp_files: list[Path] = []
    if resp_dir.exists():
        resp_files = sorted(resp_dir.glob("*.json"))

    # legacy 课夹内道喂夹（向后兼容显示）
    legacy_feed_files: list[Path] = []
    if info.get("legacy_feed_dir") and info["legacy_feed_dir"].exists():
        legacy_feed_files = sorted(
            [p for p in info["legacy_feed_dir"].iterdir() if p.is_file()]
        )

    # 期末模拟卷之态（第八关）
    course_name_resolved = course_meta.get("course_name") or info["course_name"]
    mock_root = ROOT / ".模拟卷任务"
    mock_offline_json = mock_root / f"{course_name_resolved}_期末模拟卷.json"
    mock_offline_md = mock_root / f"{course_name_resolved}_期末模拟卷_提示.md"
    mock_online_md = material_dir / "_期末模拟卷.md"
    has_mock_offline = mock_offline_json.exists()
    has_mock_online = mock_online_md.exists()

    return {
        "course_name": course_name_resolved,
        "teacher": course_meta.get("teacher", ""),
        "semester": course_meta.get("semester", ""),
        "pdf_count": len(pdf_files),
        "pdf_files": pdf_files,
        "page_total": sum(d.get("page_count") or 0 for d in course_meta.get("documents", [])),
        "chapter_count": len(chapters),
        "chap_states": chap_states,
        "filled_count": filled_count,
        "non_lecture_count": len(non_lecture),
        "uncategorized_count": len(uncat),
        "has_skeleton": has_skel,
        "has_quick": has_quick,
        "has_prompt": has_prompt,
        "has_final": has_final,
        "feed_files": feed_files,
        "resp_files": resp_files,
        "legacy_feed_files": legacy_feed_files,
        # 模拟卷
        "mock_offline_json": mock_offline_json,
        "mock_offline_md": mock_offline_md,
        "mock_online_md": mock_online_md,
        "has_mock_offline": has_mock_offline,
        "has_mock_online": has_mock_online,
    }


def 关_总览(info: dict) -> dict:
    """生/更新 <课>/00_闭环总览.md

    道喂任务居全局 .道喂任务/<课夹名>/——从课夹视之需逾根 `../`。
    """
    import os
    stat = _统计课夹(info)
    out_path = info["course_root"] / "00_闭环总览.md"
    course_root = info["course_root"]

    # 课夹内之相对路径（用 ./...）
    rel_pdf = info["pdf_dir"].relative_to(course_root).as_posix()
    rel_parse = info["parse_dir"].relative_to(course_root).as_posix()
    # 道喂任务居根之 .道喂任务/<课>/——从 <课>/00_闭环总览.md 视之，须先 `../`
    # 但 markdown 通常 `../.道喂任务/<课>/` 即可
    rel_feed = os.path.relpath(info["feed_dir"], course_root).replace("\\", "/")
    legacy_feed_dir = info.get("legacy_feed_dir")
    rel_legacy = (
        legacy_feed_dir.relative_to(course_root).as_posix()
        if legacy_feed_dir else None
    )

    cname = info['course_name']
    L: list[str] = []
    L.append(f"# {stat['course_name']} · 闭环总览")
    L.append("")
    L.append("> *反者，道之动也；弱者，道之用也。*")
    L.append(
        f"> 此课夹自成闭环——从 `{rel_pdf}/*.pdf` 自举至 "
        f"`{rel_parse}/_素材/_最终复习资料.md`。"
    )
    L.append(f"> 更新于 {_dt.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    L.append("")
    teacher_line = " · ".join(filter(None, [
        f"教师：{stat['teacher']}" if stat['teacher'] else "",
        f"学期：{stat['semester']}" if stat['semester'] else "",
    ]))
    if teacher_line:
        L.append(teacher_line)
        L.append("")

    # 入口（最重要）
    L.append("## 一 · 入口速链")
    L.append("")
    if stat["has_final"]:
        L.append(
            f"- ★ **[最终底层复习资料](./{rel_parse}/_素材/_最终复习资料.md)**"
            "  ← 从此入门"
        )
    if stat["has_skeleton"]:
        L.append(f"- [期末骨架](./{rel_parse}/_素材/_期末骨架.md)")
    if stat["has_quick"]:
        L.append(f"- [期末速查](./{rel_parse}/_素材/_期末速查.md)")
    if stat["has_prompt"]:
        L.append(f"- [LLM 提示语](./{rel_parse}/_素材/_LLM_提示语.md)")
    if stat["has_mock_online"]:
        L.append(f"- [期末模拟卷](./{rel_parse}/_素材/_期末模拟卷.md)")
    L.append(f"- [章节图谱](./{rel_parse}/_章节图谱.md)")
    L.append(f"- [章节素材索引](./{rel_parse}/_素材/_index.md)")
    L.append("")

    # 一令贯通
    L.append("## 二 · 一令贯通")
    L.append("")
    L.append("```bash")
    L.append("# 全链路·增量（八关：提文→聚合→素材→道喂→回填→汇编→模拟卷→总览）")
    L.append(f"python 课程_闭环.py {cname}")
    L.append("")
    L.append("# 加：离线道喂任务（导出 .json+grid.jpg 至全局 .道喂任务/）")
    L.append(f"python 课程_闭环.py {cname} --feed offline --grid")
    L.append("")
    L.append("# 加：在线 LLM 协填（须 .env 配 API key）")
    L.append(f"python 课程_闭环.py {cname} --feed online --grid")
    L.append("")
    L.append("# 加：在线 LLM 出期末模拟卷（写至 _素材/_期末模拟卷.md）")
    L.append(f"python 课程_闭环.py {cname} --mock online")
    L.append("")
    L.append("# 仅重扫章节信号（速极快）")
    L.append(f"python 课程_闭环.py {cname} --rescan")
    L.append("")
    L.append("# 单章道喂 + 回填（避免一令误调多章）")
    L.append(f"python 课程_闭环.py {cname} --feed offline --grid --章 3")
    L.append("```")
    L.append("")

    # 闭环之态
    L.append("## 三 · 闭环之态")
    L.append("")
    L.append(
        f"- 原始 PDF：**{stat['pdf_count']}** 份 / "
        f"**{stat['page_total']}** 页  (`{rel_pdf}/`)"
    )
    L.append(
        f"- 解析章节：**{stat['chapter_count']}** 章 "
        f"(非教学 {stat['non_lecture_count']}, 未归 {stat['uncategorized_count']})"
    )
    pct = (stat['filled_count'] * 100 // max(1, stat['chapter_count'])) \
        if stat['chapter_count'] else 0
    L.append(
        f"- 复习要点填充：**{stat['filled_count']}/{stat['chapter_count']}** 章已填  "
        f"({pct}%)"
    )
    skel = "✓" if stat["has_skeleton"] else "·"
    quick = "✓" if stat["has_quick"] else "·"
    prompt = "✓" if stat["has_prompt"] else "·"
    final = "✓" if stat["has_final"] else "·"
    L.append(
        f"- 期末四件套：骨架 {skel} · 速查 {quick} · 提示 {prompt} · "
        f"**最终复习资料：{final}**"
    )
    # 道喂态简记
    n_feed = len([f for f in stat["feed_files"] if f.suffix == ".json"])
    n_grid = len([f for f in stat["feed_files"] if f.suffix == ".jpg"])
    n_resp = len(stat["resp_files"])
    L.append(
        f"- 全局道喂：**{n_feed}** 任务 + **{n_grid}** 网格 "
        f"(`{rel_feed}/`)；已回填 **{n_resp}** 章"
    )
    # 期末模拟卷态
    mock_off = "✓" if stat["has_mock_offline"] else "·"
    mock_on = "✓" if stat["has_mock_online"] else "·"
    L.append(
        f"- 期末模拟卷：离线任务包 {mock_off} · "
        f"**在线已生卷：{mock_on}**"
    )
    L.append("")

    # 章节进度
    if stat["chap_states"]:
        L.append("## 四 · 章节进度")
        L.append("")
        L.append("| 章 | 标题 | 主版页 | 文档 | md | 已填 | 入口 |")
        L.append("|---:|------|------:|---:|----:|:---:|------|")
        for ch in stat["chap_states"]:
            n = ch["num"]
            label = "绪" if n == 0 else f"第{n}章"
            md_state = f"{ch['md_size']//1024}KiB" if ch["md_size"] else "—"
            filled = "✓" if ch["filled"] else "·"
            t = (ch["title"] or "")[:36]
            link = (
                f"[md](./{rel_parse}/_素材/{ch['fname']})"
                if ch["md_exists"] else "·"
            )
            L.append(
                f"| {label} | {t} | {ch['primary_pages']} | "
                f"{ch['all_doc_count']} | {md_state} | {filled} | {link} |"
            )
        L.append("")

    # 道喂态详
    if stat["feed_files"] or stat["resp_files"]:
        L.append("## 五 · 道喂任务 · 全局")
        L.append("")
        L.append(f"位居：`{rel_feed}/`（全工作区 `.道喂任务/{cname}/`）")
        L.append("")
        if stat["feed_files"]:
            L.append("**任务包**：")
            L.append("")
            for f in stat["feed_files"]:
                size_kib = f.stat().st_size // 1024
                L.append(f"- [{f.name}]({rel_feed}/{f.name}) · {size_kib} KiB")
            L.append("")
        if stat["resp_files"]:
            L.append(f"**LLM 响应**（_resp/，已 {n_resp} 章）：")
            L.append("")
            for f in stat["resp_files"]:
                size_kib = f.stat().st_size // 1024
                L.append(
                    f"- [{f.name}]({rel_feed}/_resp/{f.name}) · {size_kib} KiB"
                )
            L.append("")
        else:
            L.append("**回填响应**：未有。若已手喂 LLM 得 JSON，置入：")
            L.append("")
            L.append(f"`{rel_feed}/_resp/<同任务名>.json`")
            L.append("")
            L.append(f"然后 `python 课程_闭环.py {cname} --only 回填,汇编,总览`")
            L.append("")

    # legacy 课夹内道喂夹（向后兼容）
    if stat["legacy_feed_files"] and rel_legacy:
        L.append("## 六 · 课夹内 legacy 道喂（向后兼容·只读）")
        L.append("")
        L.append(f"位居：`{rel_legacy}/`")
        L.append("")
        L.append(
            "> 此乃旧版（闭环主居全局 `.道喂任务/`）。"
            "若全局已盖，则此处仅作回顾。可删去无患。"
        )
        L.append("")
        for f in stat["legacy_feed_files"]:
            size_kib = f.stat().st_size // 1024
            L.append(f"- [{f.name}](./{rel_legacy}/{f.name}) · {size_kib} KiB")
        L.append("")

    # 期末模拟卷段（第八关）—— 节号据上方既已列之节而续
    # 上节固定：一 入口 / 二 一令 / 三 态 / 四 章节进度
    # 可选：五 道喂（若有 feed 或 resp）/ 五|六 legacy（若有 legacy）
    _CN_NUM = ("零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十")
    sec_idx_mock = 4
    if stat["feed_files"] or stat["resp_files"]:
        sec_idx_mock += 1  # 道喂
    if stat["legacy_feed_files"]:
        sec_idx_mock += 1  # legacy

    if stat["has_mock_offline"] or stat["has_mock_online"]:
        sec_idx_mock += 1  # 此节·模拟卷
        mock_sec_num = (
            _CN_NUM[sec_idx_mock] if sec_idx_mock < len(_CN_NUM)
            else str(sec_idx_mock)
        )
        L.append(f"## {mock_sec_num} · 期末模拟卷 · 第八关")
        L.append("")
        if stat["has_mock_online"]:
            mock_md = stat["mock_online_md"]
            size_kib = mock_md.stat().st_size // 1024
            L.append(
                f"- ★ **[已生卷·课夹版](./{rel_parse}/_素材/_期末模拟卷.md)** "
                f"· {size_kib} KiB（在线 LLM 自举·可即印）"
            )
        if stat["has_mock_offline"]:
            mock_json = stat["mock_offline_json"]
            mock_md_off = stat["mock_offline_md"]
            rel_mock_root = os.path.relpath(
                mock_json.parent, course_root
            ).replace("\\", "/")
            sj = mock_json.stat().st_size // 1024
            sm = (
                mock_md_off.stat().st_size // 1024
                if mock_md_off.exists() else 0
            )
            L.append(
                f"- 离线任务包：[`{mock_json.name}`]"
                f"({rel_mock_root}/{mock_json.name}) · {sj} KiB"
            )
            if mock_md_off.exists():
                L.append(
                    f"- LLM 提示文：[`{mock_md_off.name}`]"
                    f"({rel_mock_root}/{mock_md_off.name}) · {sm} KiB"
                )
            L.append("")
            L.append(
                f"  > 喂上述提示给 LLM 取 JSON 答，存为 "
                f"`{stat['course_name']}_答.json`，再："
            )
            L.append(
                f"  > `python 期末_模拟卷.py -c {cname} "
                f"--纳入 <答 json>` 入卷。"
            )
        L.append("")
    else:
        sec_idx_mock = -1  # 标记无此节，不进位

    # 原始 PDF —— 续模拟卷之后
    sec_idx = 4
    if stat["feed_files"] or stat["resp_files"]:
        sec_idx += 1  # 道喂
    if stat["legacy_feed_files"]:
        sec_idx += 1  # legacy
    if stat["has_mock_offline"] or stat["has_mock_online"]:
        sec_idx += 1  # 模拟卷
    sec_idx += 1  # 此节
    pdf_sec_num = _CN_NUM[sec_idx] if sec_idx < len(_CN_NUM) else str(sec_idx)
    L.append(f"## {pdf_sec_num} · 原始 PDF")
    L.append("")
    L.append("<details><summary>展开列表</summary>")
    L.append("")
    for f in stat["pdf_files"]:
        mb = f.stat().st_size / 1024 / 1024
        L.append(f"- [{f.name}](./{rel_pdf}/{f.name}) · {mb:.2f} MB")
    L.append("")
    L.append("</details>")
    L.append("")

    # 道之教
    L.append("---")
    L.append("")
    L.append("## 终 · 道之教")
    L.append("")
    L.append("> *道恒无为，而无不为。*")
    L.append(">")
    L.append("> 此夹自为闭环：万事可于课夹内成；")
    L.append("> 道喂任务居全局 `.道喂任务/`、模拟卷任务居全局 `.模拟卷任务/`，")
    L.append("> 与既有 课件_道喂 / 回填 / 期末_模拟卷 之约定一。")
    L.append(">")
    L.append("> 每章既填，速查自厚；闭环既毕，期末自宁；")
    L.append("> 模拟卷既出，临考自定。")
    L.append("> 见疑则归章素材 → 归原 PDF 图。")
    L.append("> 慎终若始，则无败事矣。")
    L.append("")

    out_path.write_text("\n".join(L), encoding="utf-8")
    log(
        f"  ✓ 总览 → {out_path.relative_to(course_root)} "
        f"({stat['filled_count']}/{stat['chapter_count']} 章已填, "
        f"{n_feed} 任务, {n_resp} 回填)",
        "ok",
    )
    return {
        "out_path": str(out_path),
        "filled": stat["filled_count"],
        "chap_count": stat["chapter_count"],
        "feed_count": n_feed,
        "resp_count": n_resp,
    }


# ============================================================
# 八ノ五、模拟卷（第八关·期末模拟卷）
# ============================================================


def 关_模拟卷(info: dict, *, mode: str = "offline") -> dict:
    """生 期末模拟卷之离线任务包，或调 LLM 在线生卷。

    薄包装 期末_模拟卷.py 之 _offline_export / _online_generate，
    输入 task 已就课夹自治模式（course_dir == info["parse_dir"]），
    与之约定一。

    mode = none | offline | online
        · none   ─ 跳
        · offline ─ 导出 .模拟卷任务/<课>_期末模拟卷.json + 提示 md
        · online  ─ 调 LLM 自生卷 → <课>/<解析夹>/_素材/_期末模拟卷.md
    """
    if mode == "none":
        log("  ⊝ 跳（--mock none）", "dim")
        return {"skipped": True}

    chart = read_json(info["parse_dir"] / "_章节图谱.json")
    if not chart or not chart.get("chapters"):
        log("  ⊝ 无 _章节图谱.json 或 0 章，跳", "dim")
        return {"skipped": True, "reason": "no_chart"}

    task = {
        "course_dir": info["parse_dir"],  # 课夹自治：解析夹即"课目录"
        "course_name": chart.get("course_name", info["course_name"]),
        "teacher": chart.get("teacher", ""),
        "semester": chart.get("semester", ""),
        "chart": chart,
        "source": "课夹",
        "course_root": info["course_root"],
    }

    import 期末_模拟卷 as _mock

    if mode == "online":
        ok, msg = _mock._online_generate(
            task, max_chap_chars=6000, 题型=None, dry_run=False,
        )
        log(f"  {'✓' if ok else '×'} {msg}", "ok" if ok else "err")
        return {"success": int(ok), "mode": "online"}

    # 默：离线
    out = _mock._offline_export(task, max_chap_chars=6000, 题型=None)
    rel = out.relative_to(ROOT) if str(out).startswith(str(ROOT)) else out
    log(f"  ✓ 离线导出: {rel}", "ok")
    return {"success": 1, "mode": "offline", "out": str(out)}


# ============================================================
# 九、单课驱动 / 八关链
# ============================================================

# 十关：提文 → 聚合 → 素材 → 道喂 → 回填 → 汇编 → 学习系统 → 图谱 → 模拟卷 → 总览
# 学习系统关置汇编后（要点已填则题/卡皆实）；图谱关置其后；模拟卷置总览前。
STAGES = ["提文", "聚合", "素材", "道喂", "回填", "汇编", "学习系统", "图谱", "模拟卷", "总览"]


def 闭环一课(info: dict, args) -> dict:
    """对单课夹跑全链路。返各关之状。"""
    only = set(s.strip() for s in args.only.split(",")) if args.only else None
    skip = set(s.strip() for s in args.skip.split(",")) if args.skip else set()

    summary = {"course": info["course_name"], "stages": {}}

    def 跑关(name: str, fn) -> bool:
        if only and name not in only:
            log(f"\n  ⊝ [{name}] 跳（未在 --only）", "dim")
            summary["stages"][name] = "skip"
            return True
        if name in skip:
            log(f"\n  ⊝ [{name}] 跳（在 --skip）", "dim")
            summary["stages"][name] = "skip"
            return True
        log(f"\n┌── [{name}]", "title")
        t0 = time.time()
        try:
            fn()
            dt = time.time() - t0
            log(f"└── [{name}] ✓ ({dt:.1f}s)", "ok")
            summary["stages"][name] = "ok"
            return True
        except Exception as e:
            dt = time.time() - t0
            traceback.print_exc()
            log(f"└── [{name}] × ({dt:.1f}s): {e}", "err")
            summary["stages"][name] = f"fail: {e}"
            return False

    chap_filter = set(args.chap) if args.chap else None

    # 提文 → 聚合 → 素材 是核心三关，前关失则后关亦无意义
    if not 跑关("提文", lambda: 关_提文(
        info, force=args.force, dpi=args.dpi, rescan=args.rescan, ocr=args.ocr,
    )):
        return summary
    if not 跑关("聚合", lambda: 关_聚合(info)):
        return summary
    if not 跑关("素材", lambda: 关_素材(
        info, inline_images=args.inline_images,
        max_aux_pages=args.max_aux_pages,
    )):
        return summary

    # 道喂、回填、汇编、模拟卷、总览 - 各自独立
    # （模拟卷置总览前，使总览能汇集模拟卷之态）
    跑关("道喂", lambda: 关_道喂(
        info, mode=args.feed, grid=args.grid,
        max_pages=args.max_pages, chap_filter=chap_filter,
    ))
    跑关("回填", lambda: 关_回填(info, dry=args.dry_writeback))
    跑关("汇编", lambda: 关_汇编(info))
    跑关("学习系统", lambda: 关_学习系统(info, 考试日=getattr(args, "考试日", None)))
    跑关("图谱", lambda: 关_图谱(
        info, mode=args.图谱, chap_filter=chap_filter, dry=args.dry_writeback,
    ))
    跑关("模拟卷", lambda: 关_模拟卷(info, mode=args.mock))
    跑关("总览", lambda: 关_总览(info))

    return summary


# ============================================================
# 十、CLI
# ============================================================


def 列_模式(workspace_root: Path) -> None:
    cands = 列闭环课夹(workspace_root)
    if not cands:
        log("∅ 无可闭环之课夹", "warn")
        log(
            "  课夹须含 PDF 之 01_原始PDF/ 或 02_原始课件PDF/",
            "dim",
        )
        return
    log(f"\n共 {len(cands)} 门可闭环课夹：\n", "info")
    for c in cands:
        pdfs = list(c["pdf_dir"].glob("*.pdf"))
        existing = "✓" if (c["parse_dir"] / "_章节图谱.json").exists() else "·"
        log(
            f"  · {c['course_name']:<24s}  {len(pdfs):2d} PDF  "
            f"({c['pdf_dir'].name})  章谱 {existing}",
            "dim",
        )
    log("", "info")
    log("用法：python 课程_闭环.py <课夹名>", "dim")
    log("或：  python 课程_闭环.py --全", "dim")


def main() -> int:
    p = argparse.ArgumentParser(
        description="课程 闭环 —— 反者，道之动也；以课夹为本，从 PDF 自举至最终底层复习资料",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "courses", nargs="*",
        help="课夹名（不填且无 --全 则列）",
    )
    p.add_argument("--列", "-l", action="store_true", help="列所有可闭环之课夹")
    p.add_argument("--全", action="store_true", help="对所有可闭环课夹依次跑")
    # 提文参数
    p.add_argument(
        "--force", action="store_true",
        help="强制重处提文（忽略既有 _doc.json）",
    )
    p.add_argument("--dpi", type=int, default=150, help="提文渲染兜底 DPI")
    p.add_argument(
        "--rescan", action="store_true",
        help="仅重扫章节信号（不动图像，速极快）",
    )
    p.add_argument(
        "--ocr", action="store_true",
        help="提文后自动 OCR 识文 + 生成 _全文.md",
    )
    # 素材参数
    p.add_argument(
        "--inline-images", action="store_true",
        help="素材：主版每页内联展示图像",
    )
    p.add_argument(
        "--max-aux-pages", type=int, default=3,
        help="素材：每辅版列页数（默 3）",
    )
    # 道喂参数
    p.add_argument(
        "--feed", choices=["none", "offline", "online", "dry"], default="none",
        help="道喂模式：none/offline/online/dry",
    )
    p.add_argument(
        "--grid", "--拼网格", action="store_true",
        help="道喂拼网格图（省 token）",
    )
    p.add_argument(
        "--max-pages", type=int, default=40,
        help="道喂每章最多喂图页（默 40）",
    )
    p.add_argument(
        "--chap", "--章", type=int, action="append", default=None,
        help="仅道喂指定章（可多次）",
    )
    # 回填参数
    p.add_argument(
        "--dry-writeback", action="store_true",
        help="回填关：干跑（只显示将写入但不真写）",
    )
    # 模拟卷参数
    p.add_argument(
        "--mock", choices=["none", "offline", "online"], default="offline",
        help="模拟卷模式：none/offline/online（默 offline · 离线导出 .模拟卷任务/）",
    )
    # 图谱参数
    p.add_argument(
        "--图谱", dest="图谱",
        choices=["none", "offline", "online", "writeback"],
        default="none",
        help=(
            "思维导图生成关：none(跳·默)/offline(离线导出)/online(在线LLM)/writeback(回填 _resp/)"
        ),
    )
    # 学习系统参数
    p.add_argument(
        "--考试日", "--exam", dest="考试日", default=None,
        help="学习系统关：目标考试日 YYYY-MM-DD（默：今日+21），决定间隔重复日历",
    )
    # 流程
    p.add_argument(
        "--only", default=None,
        help="仅跑指定关（逗号分: 提文,聚合,素材,道喂,回填,汇编,学习系统,图谱,模拟卷,总览）",
    )
    p.add_argument("--skip", default=None, help="跳过指定关")
    args = p.parse_args()

    header("课程 闭环 —— 反者，道之动也", width=58)
    log(f"  根: {ROOT}", "dim")

    # 列模式
    if args.列:
        列_模式(ROOT)
        return 0

    # 选课
    if args.courses:
        infos: list[dict] = []
        for n in args.courses:
            cp = ROOT / n
            info = 识别课夹(cp)
            if info is None:
                log(
                    f"× {n}: 非可闭环课夹（须含 01_原始PDF/ 或 02_原始课件PDF/ 之 PDF）",
                    "err",
                )
                continue
            infos.append(info)
        if not infos:
            return 1
    elif args.全:
        infos = 列闭环课夹(ROOT)
        if not infos:
            log("∅ 无可闭环课夹", "warn")
            return 0
    else:
        # 默认：列
        列_模式(ROOT)
        return 0

    log(f"  待闭环 {len(infos)} 门课", "info")

    summaries = []
    t_all0 = time.time()
    for i, info in enumerate(infos, 1):
        header(
            f"[{i}/{len(infos)}] 闭环：{info['course_name']}",
            width=58,
        )
        log(f"  原始: {info['pdf_dir'].relative_to(ROOT)}", "dim")
        log(f"  解析: {info['parse_dir'].relative_to(ROOT)}", "dim")
        log(f"  道喂: {info['feed_dir'].relative_to(ROOT)} (全局)", "dim")
        if info.get("legacy_feed_dir") and info["legacy_feed_dir"].exists():
            log(
                f"  legacy: {info['legacy_feed_dir'].relative_to(ROOT)}",
                "dim",
            )
        s = 闭环一课(info, args)
        summaries.append(s)

    dt_all = time.time() - t_all0
    header(f"闭环毕  用时 {dt_all:.1f}s", width=58)
    for s in summaries:
        cells = []
        for stage in STAGES:
            r = s["stages"].get(stage, "—")
            if r == "ok":
                cells.append(f"\033[32m{stage}\033[0m")
            elif r == "skip":
                cells.append(f"\033[90m{stage}\033[0m")
            elif r == "—":
                cells.append(f"\033[90m{stage}\033[0m")
            else:
                cells.append(f"\033[31m{stage}×\033[0m")
        log(f"  {s['course']:<24s}  {' → '.join(cells)}", "info")
    log("\n  道恒无为，而无不为。", "title")

    # 失败者非零退码
    any_fail = any(
        any(v.startswith("fail") for v in s["stages"].values())
        for s in summaries
    )
    return 1 if any_fail else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("\n知止所以不殆。退也。", "warn")
        sys.exit(130)
