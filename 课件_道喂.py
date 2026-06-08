# -*- coding: utf-8 -*-
"""
课件 道喂 (chapter_feed)  ——  道恒无为，而无不为

第七关。双路径：
  · 离线：导出 .道喂任务/<课>/<章>.json（含提示 + 图路径），人喂任意 LLM
  · 在线：调 LLMClient，自动填占位 → 回写章 md 之"复习要点"区

用法:
    python 课件_道喂.py --课 环境毒理 --章 3              # 默：离线导出
    python 课件_道喂.py --课 环境毒理 --章 3 --在线        # 在线填写
    python 课件_道喂.py --课 环境毒理 --在线 --拼网格      # 全章·拼图省 token
    python 课件_道喂.py --列 环境毒理                     # 列状

回写策略：
    定位章 md 中之"## 复习占位 · 待人/LLM 填充"区段，
    以"## 复习要点 · LLM 协填"替之；其余区段（主版/辅版/章际备注）原封不动。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _yc_common import log, header, read_json  # noqa: E402

_REPO = Path(__file__).resolve().parent
_仓库 = _REPO / "解析仓库"
_导出根 = _REPO / ".道喂任务"


# ─────────────────────────────────────────────
# 一、扫描可填之章
# ─────────────────────────────────────────────

def scan_chapters(course_filter: list[str] | None = None) -> list[dict]:
    """扫所有有章节图谱之课程之章节，返可填任务列表。"""
    tasks: list[dict] = []
    for course_dir in sorted(_仓库.iterdir()):
        if not course_dir.is_dir():
            continue
        if course_filter and not any(kw in course_dir.name for kw in course_filter):
            continue
        chart_path = course_dir / "_章节图谱.json"
        if not chart_path.exists():
            continue
        chart = read_json(chart_path)
        if not chart:
            continue
        material_dir = course_dir / "_素材"
        for ch in chart.get("chapters", []):
            n = ch.get("chapter_num")
            title = ch.get("chapter_title", "")
            # 章 md 文件名（与 课件_知识素材.py 之 chapter_filename 同规）
            t_clean = title or "无题"
            for bad in '\\/:*?"<>|':
                t_clean = t_clean.replace(bad, "_")
            t_clean = t_clean.strip()[:40]
            if n == 0:
                fname = f"_第00章_{t_clean}.md".replace(" ", "_")
            else:
                fname = f"_第{n:02d}章_{t_clean}.md".replace(" ", "_")
            md_path = material_dir / fname
            primary = ch.get("primary", {})
            tasks.append({
                "course_dir": str(course_dir),
                "course_name": chart.get("course_name", ""),
                "teacher": chart.get("teacher", ""),
                "semester": chart.get("semester", ""),
                "chap_num": n,
                "chap_title": title,
                "md_path": str(md_path),
                "primary_rel_dir": primary.get("rel_dir", ""),
                "primary_pages": primary.get("page_count", 0),
                "primary_lesson_seq": primary.get("lesson_seq"),
                "cross_chapters": _列跨章(ch),
            })
    return tasks


def _列跨章(chapter: dict) -> list[int]:
    """从 all_docs 抽出本章之跨章号。"""
    n = chapter.get("chapter_num")
    cross: set[int] = set()
    for d in chapter.get("all_docs", []) or []:
        for c2 in d.get("all_chapter_nums", []) or []:
            if c2 != n:
                cross.add(c2)
    return sorted(cross)


def get_primary_pages(task: dict) -> list[Path]:
    """取主版所有 page_*.jpg 路径。"""
    pdf_dir = Path(task["course_dir"]) / task["primary_rel_dir"]
    doc_json = pdf_dir / "_doc.json"
    meta = read_json(doc_json)
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


# ─────────────────────────────────────────────
# 二、回写章 md 之"复习要点"区
# ─────────────────────────────────────────────

_占位标 = re.compile(r"^## 复习占位.*?$", re.MULTILINE)
_要点标 = re.compile(r"^## 复习要点.*?$", re.MULTILINE)
_次章标 = re.compile(r"^## ", re.MULTILINE)


def 回写章md(md_path: Path, 新要点md: str) -> bool:
    """以新内容替换章 md 中之"复习占位..."或"复习要点..."区段。"""
    if not md_path.exists():
        log(f"  × 章 md 不存: {md_path.name}", "err")
        return False
    text = md_path.read_text(encoding="utf-8")
    # 找区段起
    m = _占位标.search(text) or _要点标.search(text)
    if not m:
        # 无占位区，追加
        new_text = text.rstrip() + "\n\n---\n\n" + 新要点md + "\n"
    else:
        # 找区段终（下一个 "## " 或 EOF）
        start = m.start()
        rest = text[m.end():]
        next_m = _次章标.search(rest)
        end = m.end() + next_m.start() if next_m else len(text)
        new_text = text[:start] + 新要点md + "\n" + text[end:]

    md_path.write_text(new_text, encoding="utf-8")
    return True


# ─────────────────────────────────────────────
# 三、离线导出
# ─────────────────────────────────────────────

def 离线导出(task: dict, *, 拼网格: bool = False) -> Path:
    """生成 .道喂任务/<课>/<章>.json + 配套 grid.jpg（若拼）"""
    from _道说_提示库 import 章占位填充任务

    course_dir = _导出根 / task["course_name"]
    course_dir.mkdir(parents=True, exist_ok=True)
    out_json = course_dir / f"第{task['chap_num']:02d}章_{task['chap_title'][:30]}.json"

    # 读已有人填笔记（若 md 有内容）
    existing = ""
    md = Path(task["md_path"])
    if md.exists():
        existing = md.read_text(encoding="utf-8")

    prompt_task = 章占位填充任务.build(
        course=task["course_name"],
        chap_label=f"第 {task['chap_num']} 章" if task["chap_num"] else "绪论",
        chap_title=task["chap_title"],
        page_count=task["primary_pages"],
        teacher=task["teacher"],
        semester=task["semester"],
        cross_chapters=task["cross_chapters"],
    )

    pages = get_primary_pages(task)
    page_paths_rel = [str(p.relative_to(_REPO)) for p in pages]

    # _doc.json 之路径——便于回填时知文该入哪
    doc_json_rel = None
    if pages:
        doc_json = pages[0].parent / "_doc.json"
        if doc_json.exists():
            try:
                doc_json_rel = str(doc_json.relative_to(_REPO))
            except ValueError:
                doc_json_rel = str(doc_json)

    # 拼网格
    grid_path = None
    if 拼网格 and pages:
        try:
            from _图_道 import 拼网格 as 拼
            import math
            cols = min(4, max(2, math.ceil(math.sqrt(len(pages)))))
            grid_out = course_dir / f"第{task['chap_num']:02d}章_grid.jpg"
            拼(pages, cols=cols, cell=400, out=grid_out)
            grid_path = str(grid_out.relative_to(_REPO))
        except Exception as e:
            log(f"  ⚠ 拼图失: {e}", "warn")

    payload = {
        "task": prompt_task.meta,
        "system": prompt_task.system,
        "user": prompt_task.user,
        "schema": prompt_task.schema,
        "page_count": len(pages),
        "page_paths": page_paths_rel,
        "grid_path": grid_path,
        "md_path_to_write_back": str(md.relative_to(_REPO)) if md.exists() else None,
        "doc_json_path_rel": doc_json_rel,  # 回填页文之据
        "已有笔记长": len(existing),
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_json


# ─────────────────────────────────────────────
# 四、在线调 LLM
# ─────────────────────────────────────────────

def 在线协填(
    task: dict,
    *,
    拼网格: bool = False,
    max_pages: int = 40,
    dry_run: bool = False,
) -> tuple[bool, str]:
    """调 LLM 填一章。返 (成败, 信息)"""
    from _道说_提示库 import 章占位填充任务
    from _llm_道 import LLMClient
    from _图_道 import 缩图, 拼网格 as 拼

    cli = LLMClient.from_env(profile="vision")
    if not cli.config.is_ready():
        cli = LLMClient.from_env(profile="default")
    if not cli.config.is_ready():
        return False, "未配 LLM（.env 缺 API key）"

    pages = get_primary_pages(task)
    if not pages:
        return False, "无主版图像"

    # 限页数
    if max_pages and len(pages) > max_pages:
        # 等距抽样
        step = len(pages) / max_pages
        pages = [pages[int(i * step)] for i in range(max_pages)]

    # 拼图或缩图
    if 拼网格:
        import math
        cols = min(4, max(2, math.ceil(math.sqrt(len(pages)))))
        grid_bytes = 拼(pages, cols=cols, cell=400)
        images_payload: list = [grid_bytes]
    else:
        # 单图缩
        images_payload = [缩图(p, max_dim=1568) for p in pages]

    prompt_task = 章占位填充任务.build(
        course=task["course_name"],
        chap_label=f"第 {task['chap_num']} 章" if task["chap_num"] else "绪论",
        chap_title=task["chap_title"],
        page_count=task["primary_pages"],
        teacher=task["teacher"],
        semester=task["semester"],
        cross_chapters=task["cross_chapters"],
    )

    if dry_run:
        return True, f"DRY: 将喂 {len(images_payload)} 张图, system+user={len(prompt_task.system)+len(prompt_task.user)} 字"

    log(f"  → 调 LLM ({cli.config.model}, {len(images_payload)} 图)...", "dim")
    t0 = time.time()
    try:
        raw = cli.chat_json(
            prompt_task.user,
            system=prompt_task.system,
            schema_hint=prompt_task.schema,
            images=images_payload,
            strict=False,
        )
        dt = time.time() - t0
    except Exception as e:
        return False, f"LLM 调用败: {e}"

    if not isinstance(raw, dict):
        return False, f"返非 JSON ({dt:.1f}s): {str(raw)[:200]}"

    result = 章占位填充任务.parse(raw)
    new_md = 章占位填充任务.render_md(result)

    # 回填 _doc.json 之 embedded_text（一关二事：要点入 md + 页文入 doc）
    doc_text_msg = ""
    if result.页文转录:
        try:
            pdf_dir = Path(task["course_dir"]) / task["primary_rel_dir"]
            doc_json = pdf_dir / "_doc.json"
            if doc_json.exists():
                upd, tot = 章占位填充任务.apply_page_texts(doc_json, result.页文转录)
                if upd:
                    doc_text_msg = f" +文{upd}/{tot}页"
        except Exception as e:
            doc_text_msg = f" +文异({e})"

    md_path = Path(task["md_path"])
    if 回写章md(md_path, new_md):
        return True, (
            f"✓ {dt:.1f}s 概念{len(result.核心概念)}+公式{len(result.关键公式)}"
            f"+考点{len(result.高频考点)}{doc_text_msg}"
        )
    return False, "回写失败"


# ─────────────────────────────────────────────
# 五、CLI
# ─────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="课件 道喂 —— 第七关")
    p.add_argument("--课", "-c", action="append", help="课程名关键字（可多次）")
    p.add_argument("--章", "-n", type=int, action="append", help="章节号（可多次，不指定则全章）")
    p.add_argument("--在线", action="store_true", help="调 LLM 在线填（默：离线导出）")
    p.add_argument("--拼网格", action="store_true", help="多图拼成一张大图（省 token，但损细节）")
    p.add_argument("--max-pages", type=int, default=40, help="单章最多喂图数（默 40，超则等距抽样）")
    p.add_argument("--dry", action="store_true", help="预估，不真调")
    p.add_argument("--列", "-l", nargs="?", const="", help="列可填章节（不实做）")
    args = p.parse_args()

    header("课件 道喂 —— 道恒无为，而无不为", width=58)

    course_filter = args.课 or ([args.列] if args.列 else None)
    tasks = scan_chapters(course_filter)
    if args.章:
        tasks = [t for t in tasks if t["chap_num"] in args.章]

    log(f"  找到 {len(tasks)} 章", "info")

    if args.列 is not None:
        log("", "info")
        for t in tasks:
            md_size = Path(t["md_path"]).stat().st_size if Path(t["md_path"]).exists() else 0
            log(f"  · {t['course_name']:18s} 第{t['chap_num']:>2}章 · {t['chap_title']:30s} "
                f"({t['primary_pages']}页, md {md_size//1024}KiB)", "dim")
        return

    if not tasks:
        log("× 无可填章节。先配 -c <课程>", "warn")
        return

    if args.在线:
        from _llm_道 import LLMClient
        cli = LLMClient.from_env(profile="vision")
        if not cli.config.is_ready():
            cli = LLMClient.from_env(profile="default")
        if not cli.config.is_ready():
            log("× 未配 LLM。请编辑 .env（参 .env.example）", "err")
            return
        log(f"  LLM: {cli.config.describe()}", "info")

    成 = 失 = 0
    for i, t in enumerate(tasks, 1):
        log(f"\n[{i}/{len(tasks)}] {t['course_name']} · 第{t['chap_num']}章 · {t['chap_title']}", "title")
        try:
            if args.在线:
                ok, msg = 在线协填(t, 拼网格=args.拼网格, max_pages=args.max_pages, dry_run=args.dry)
                log(f"  {msg}", "ok" if ok else "err")
                成 += int(ok)
                失 += int(not ok)
            else:
                out = 离线导出(t, 拼网格=args.拼网格)
                log(f"  ✓ 导出: {out.relative_to(_REPO)}", "ok")
                成 += 1
        except Exception as e:
            log(f"  × 异: {e}", "err")
            失 += 1

    header(f"道喂毕 —— 成 {成} · 败 {失}", width=58)
    if not args.在线 and 成:
        log(f"  导出根: {_导出根}", "dim")
        log("  下一步：把 json + 图喂给任意 LLM（playground / API / 手工）", "dim")


if __name__ == "__main__":
    main()
