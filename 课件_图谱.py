# -*- coding: utf-8 -*-
"""
课件 图谱 (chapter_mindmap)  ——  知常曰明，知明曰归根

道法：
    章节素材已立，复习要点已填（或待填）。
    此关之事：据章节知识内容，以 LLM 生成
    层次清晰之思维导图（markmap + mermaid 双格式），
    回写至章 md 之「思维导图」区。

两路径：
  · 离线：导出 .道喂任务/<课夹名>/图谱/<章>.json（含提示+已有要点），
          人喂任意 LLM → 得 JSON → 置 _resp/ → 由回填关纳入
  · 在线：调 LLMClient，自动填「思维导图」区 → 回写章 md

回写策略：
    定位章 md 中之「## 思维导图占位」或「## 思维导图 · LLM 生成」区段，
    以「## 思维导图 · LLM 生成」（含 markmap + mermaid）替之；
    其余区段（主版/辅版/复习要点）原封不动。

用法:
    python 课件_图谱.py --列 环境毒理         # 列可生成章节
    python 课件_图谱.py --课 环境毒理 --章 3  # 默：离线导出
    python 课件_图谱.py --课 环境毒理 --在线  # 全章在线生成
    python 课件_图谱.py --全 --在线           # 所有可闭环课程在线生成
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from _yc_common import log, header, read_json, write_json, section_span_fenced  # noqa: E402

_仓库 = ROOT / "解析仓库"
_导出根 = ROOT / ".道喂任务"

# 定位章 md 之思维导图区（含占位 & 已填两种标题）
_MINDMAP_ANY_H2 = re.compile(r"^##\s+思维导图.*?$", re.MULTILINE)
_REVIEW_FENCE_H2 = re.compile(r"^##\s+(?:复习|---)", re.MULTILINE)
_NEXT_H2 = re.compile(r"^##\s+", re.MULTILINE)


# ─────────────────────────────────────────────
# 一、扫描可生成之章
# ─────────────────────────────────────────────

def scan_chapters(
    course_filter: list[str] | None = None,
    course_root: Path | None = None,
) -> list[dict]:
    """扫所有有章节图谱之课程，返可生成思维导图之任务列表。"""
    root = course_root or _仓库
    tasks: list[dict] = []
    for course_dir in sorted(root.iterdir()):
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
            t_clean = (title or "无题").strip()
            for bad in '\\/:*?"<>|':
                t_clean = t_clean.replace(bad, "_")
            t_clean = t_clean[:40]
            fname = (
                f"_第00章_{t_clean}.md".replace(" ", "_")
                if n == 0
                else f"_第{n:02d}章_{t_clean}.md".replace(" ", "_")
            )
            md_path = material_dir / fname
            tasks.append({
                "course_dir": str(course_dir),
                "course_name": chart.get("course_name", ""),
                "teacher": chart.get("teacher", ""),
                "semester": chart.get("semester", ""),
                "chap_num": n,
                "chap_title": title,
                "md_path": str(md_path),
            })
    return tasks


def _read_review_content(md_path: Path) -> str:
    """从章 md 中抽取「复习要点」区作为上下文喂入 LLM。"""
    if not md_path.exists():
        return ""
    text = md_path.read_text(encoding="utf-8")
    m = re.search(r"^##\s+复习要点.*?$", text, re.MULTILINE)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = _NEXT_H2.search(rest)
    end = m.end() + nxt.start() if nxt else len(text)
    return text[m.start():end].strip()


# ─────────────────────────────────────────────
# 二、回写章 md（思维导图区）
# ─────────────────────────────────────────────

def _section_span(text: str, heading_re: re.Pattern) -> tuple[int, int] | None:
    """取某 H2 区段 [start, end)，对代码块内的 ## 免疫。"""
    return section_span_fenced(text, heading_re)


def writeback_mindmap(md_path: Path, mindmap_md: str, *, dry: bool = False) -> bool:
    """把思维导图 markdown 回写到章 md 之「思维导图」区段。

    若该区已存则替换，否则插入于「复习占位」前（或文末）。
    返 True 表成功写入，False 表跳过（无变化）。
    """
    if not md_path.exists():
        log(f"    × 章 md 不存: {md_path.name}", "err")
        return False

    text = md_path.read_text(encoding="utf-8")
    span = _section_span(text, _MINDMAP_ANY_H2)

    if span:
        start, end = span
        new_text = text[:start] + mindmap_md + "\n" + text[end:]
    else:
        # 找「复习占位」前插入；找不到则文末
        m = re.search(r"^##\s+复习占位.*?$", text, re.MULTILINE)
        if m:
            insert_at = m.start()
            new_text = text[:insert_at] + "---\n\n" + mindmap_md + "\n" + text[insert_at:]
        else:
            new_text = text.rstrip() + "\n\n---\n\n" + mindmap_md + "\n"

    if new_text == text:
        return False

    if not dry:
        md_path.write_text(new_text, encoding="utf-8")
    return True


# ─────────────────────────────────────────────
# 三、离线导出
# ─────────────────────────────────────────────

def export_offline(
    tasks: list[dict],
    feed_dir: Path,
    *,
    chap_filter: set[int] | None = None,
) -> int:
    """导出思维导图任务包至 feed_dir/图谱/。返导出数。"""
    from _道说_提示库 import 思维导图任务

    out_root = feed_dir / "图谱"
    out_root.mkdir(parents=True, exist_ok=True)
    exported = 0

    for t in tasks:
        n = t["chap_num"]
        if chap_filter and n not in chap_filter:
            continue

        review = _read_review_content(Path(t["md_path"]))
        chap_label = f"第 {n} 章" if n else "绪论"
        prompt_task = 思维导图任务.build(
            course=t["course_name"],
            chap_label=chap_label,
            chap_title=t["chap_title"],
            review_content=review,
            teacher=t["teacher"],
            semester=t["semester"],
        )

        title_part = (t["chap_title"] or "无题")[:30]
        chap_key = f"第{n:02d}章" if n else "第00章"
        out_json = out_root / f"{chap_key}_{title_part}_图谱.json"

        payload = {
            "task": prompt_task.meta,
            "system": prompt_task.system,
            "user": prompt_task.user,
            "schema": prompt_task.schema,
            "md_path_to_write_back": t["md_path"],
            "review_chars": len(review),
        }
        write_json(out_json, payload)
        log(
            f"  ✓ 离线导出: {out_json.relative_to(ROOT) if str(out_json).startswith(str(ROOT)) else out_json.name}",
            "ok",
        )
        exported += 1

    return exported


# ─────────────────────────────────────────────
# 四、在线生成
# ─────────────────────────────────────────────

def generate_online(
    tasks: list[dict],
    *,
    chap_filter: set[int] | None = None,
    dry: bool = False,
) -> dict:
    """调 LLMClient，在线生成思维导图并回写章 md。"""
    try:
        from _llm_道 import LLMClient
    except ImportError:
        log("  × _llm_道 不可导，在线模式不可用", "err")
        return {"ok": 0, "fail": 1, "skipped": 0}

    from _道说_提示库 import 思维导图任务

    cli = LLMClient()
    ok_n = fail_n = skip_n = 0

    for t in tasks:
        n = t["chap_num"]
        if chap_filter and n not in chap_filter:
            skip_n += 1
            continue

        chap_label = f"第 {n} 章" if n else "绪论"
        log(f"\n  ┌ [{chap_label} · {t['chap_title']}]", "title")

        review = _read_review_content(Path(t["md_path"]))
        if not review:
            log("    ⊝ 无复习要点（建议先道喂·回填），仅凭章标题生成", "warn")

        prompt_task = 思维导图任务.build(
            course=t["course_name"],
            chap_label=chap_label,
            chap_title=t["chap_title"],
            review_content=review,
            teacher=t["teacher"],
            semester=t["semester"],
        )

        try:
            t0 = time.time()
            raw = cli.chat_json(
                prompt_task.user,
                system=prompt_task.system,
                schema_hint=prompt_task.schema,
            )
            dt = time.time() - t0
            result = 思维导图任务.parse(raw)
            mindmap_md = 思维导图任务.render_md(result)
            written = writeback_mindmap(Path(t["md_path"]), mindmap_md, dry=dry)
            status = "✓" if written else "⊝(无变化)"
            log(
                f"  └ {status} {chap_label} · {t['chap_title'][:20]}  "
                f"({dt:.1f}s · markmap {len(result.markmap)}字 · mermaid {len(result.mermaid)}字)",
                "ok" if written else "dim",
            )
            ok_n += 1
        except Exception as e:
            log(f"  └ × {chap_label}: {e}", "err")
            fail_n += 1

    return {"ok": ok_n, "fail": fail_n, "skipped": skip_n}


# ─────────────────────────────────────────────
# 五、回填（从 _resp/ 中的 JSON 回写）
# ─────────────────────────────────────────────

def writeback_from_resp(feed_dir: Path, *, dry: bool = False) -> dict:
    """从 feed_dir/图谱/_resp/*.json 读 LLM 返回，回写对应章 md。

    约定：JSON 文件名与导出时同名（或含 task.md_path_to_write_back 字段）。
    """
    from _道说_提示库 import 思维导图任务

    resp_dir = feed_dir / "图谱" / "_resp"
    if not resp_dir.exists():
        log(f"  ∅ 无 resp 目录: {resp_dir}", "dim")
        return {"ok": 0, "fail": 0, "skipped": 0}

    ok_n = fail_n = 0
    for jf in sorted(resp_dir.glob("*.json")):
        try:
            data = read_json(jf)
            if not data:
                continue
            # 找对应 md 路径
            md_path_str = data.get("md_path_to_write_back") or data.get("md_path")
            if not md_path_str:
                log(f"  ⚠ {jf.name}: 无 md_path_to_write_back，跳", "warn")
                continue
            md_path = Path(md_path_str)
            if not md_path.is_absolute():
                md_path = ROOT / md_path

            # parse 结果
            resp_raw = data.get("response") or data.get("result") or data
            result = 思维导图任务.parse(resp_raw)
            if not result.markmap and not result.mermaid:
                log(f"  ⚠ {jf.name}: markmap/mermaid 均空，跳", "warn")
                continue

            mindmap_md = 思维导图任务.render_md(result)
            written = writeback_mindmap(md_path, mindmap_md, dry=dry)
            log(
                f"  {'✓' if written else '⊝'} {jf.name} → {md_path.name}",
                "ok" if written else "dim",
            )
            ok_n += 1
        except Exception as e:
            log(f"  × {jf.name}: {e}", "err")
            fail_n += 1

    return {"ok": ok_n, "fail": fail_n, "skipped": 0}


# ─────────────────────────────────────────────
# 六、「列」模式
# ─────────────────────────────────────────────

def list_chapters(tasks: list[dict]) -> None:
    if not tasks:
        log("∅ 无可生成图谱之章节", "warn")
        return
    log(f"\n共 {len(tasks)} 章节可生成思维导图：\n", "info")
    for t in tasks:
        n = t["chap_num"]
        md_exists = Path(t["md_path"]).exists()
        review_len = len(_read_review_content(Path(t["md_path"])))
        label = "绪论" if n == 0 else f"第{n:02d}章"
        has_review = f"{review_len}字" if review_len else "无复习要点"
        md_mark = "✓" if md_exists else "·"
        log(
            f"  {md_mark} {t['course_name'][:10]:<10s}  {label}  {t['chap_title'][:24]:<24s}  {has_review}",
            "dim",
        )


# ─────────────────────────────────────────────
# 七、单课入口（供 课程_闭环.py 调用）
# ─────────────────────────────────────────────

def 生成图谱(
    parse_dir: Path,
    feed_dir: Path,
    *,
    mode: str = "offline",   # none | offline | online | writeback
    chap_filter: set[int] | None = None,
    dry: bool = False,
) -> dict:
    """课程闭环第七关·思维导图生成。

    mode:
      none       — 跳
      offline    — 离线导出 .道喂任务/<课>/图谱/*.json
      online     — 在线 LLM 生成 → 回写章 md
      writeback  — 从 .道喂任务/<课>/图谱/_resp/*.json 回填
    """
    if mode == "none":
        return {"skipped": True}

    chart_path = parse_dir / "_章节图谱.json"
    chart = read_json(chart_path)
    if not chart or not chart.get("chapters"):
        log("  ⊝ 无章节图谱，跳", "dim")
        return {"skipped": True, "reason": "no_chart"}

    # 构 tasks（以 parse_dir 为课目录）
    tasks: list[dict] = []
    material_dir = parse_dir / "_素材"
    course_name = chart.get("course_name", parse_dir.name)
    teacher = chart.get("teacher", "")
    semester = chart.get("semester", "")
    for ch in chart.get("chapters", []):
        n = ch.get("chapter_num")
        title = ch.get("chapter_title", "")
        t_clean = (title or "无题").strip()
        for bad in '\\/:*?"<>|':
            t_clean = t_clean.replace(bad, "_")
        t_clean = t_clean[:40]
        fname = (
            f"_第00章_{t_clean}.md".replace(" ", "_")
            if n == 0
            else f"_第{n:02d}章_{t_clean}.md".replace(" ", "_")
        )
        tasks.append({
            "course_dir": str(parse_dir),
            "course_name": course_name,
            "teacher": teacher,
            "semester": semester,
            "chap_num": n,
            "chap_title": title,
            "md_path": str(material_dir / fname),
        })

    if mode == "offline":
        n_exp = export_offline(tasks, feed_dir, chap_filter=chap_filter)
        log(f"  ✓ 离线导出 {n_exp} 章图谱任务 → {feed_dir.relative_to(ROOT) if str(feed_dir).startswith(str(ROOT)) else feed_dir}/图谱/", "ok")
        return {"mode": "offline", "exported": n_exp}

    if mode == "online":
        result = generate_online(tasks, chap_filter=chap_filter, dry=dry)
        log(f"  ✓ 在线生成: {result['ok']} 章 · {result['fail']} 败", "ok")
        return {"mode": "online", **result}

    if mode == "writeback":
        result = writeback_from_resp(feed_dir, dry=dry)
        log(f"  ✓ 回填: {result['ok']} 章 · {result['fail']} 败", "ok")
        return {"mode": "writeback", **result}

    log(f"  × 未知 mode: {mode}", "err")
    return {"error": f"unknown mode: {mode}"}


# ─────────────────────────────────────────────
# 八、CLI 入口
# ─────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="课件 图谱 —— 知常曰明，知明曰归根",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--课", "-c", dest="course", action="append", default=None,
        metavar="关键字", help="课程名关键字过滤（可多次）",
    )
    parser.add_argument(
        "--全", action="store_true", help="对所有可用课程生成",
    )
    parser.add_argument(
        "--章", type=int, action="append", default=None,
        dest="chap", metavar="N", help="仅指定章（可多次）",
    )
    parser.add_argument(
        "--在线", action="store_true", help="在线 LLM 生成（默离线导出）",
    )
    parser.add_argument(
        "--回填", action="store_true",
        help="从 .道喂任务/<课>/图谱/_resp/ 回填（人工喂 LLM 后）",
    )
    parser.add_argument(
        "--列", action="store_true", help="列可生成之章节",
    )
    parser.add_argument(
        "--干跑", "--dry", action="store_true",
        help="干跑（不真写盘，仅显示将写内容）",
    )
    parser.add_argument(
        "--repo", default="解析仓库",
        help="解析仓库目录（默 ./解析仓库）",
    )
    args = parser.parse_args()

    script_dir = ROOT
    repo = Path(args.repo)
    if not repo.is_absolute():
        repo = script_dir / repo

    header("课件 图谱 —— 知常曰明，知明曰归根", width=58)

    course_filter = args.course if not args.全 else None
    tasks = scan_chapters(course_filter=course_filter, course_root=repo)

    if args.列:
        list_chapters(tasks)
        return 0

    if not tasks:
        log("∅ 无任务（检查 --课 关键字或解析仓库是否有 _章节图谱.json）", "warn")
        return 0

    chap_filter = set(args.chap) if args.chap else None

    if args.回填:
        # 按课分组回填
        course_dirs: set[str] = {t["course_dir"] for t in tasks}
        total_ok = total_fail = 0
        for cd in sorted(course_dirs):
            cd_path = Path(cd)
            # 找对应 feed_dir
            feed_dir = ROOT / ".道喂任务" / cd_path.name
            r = writeback_from_resp(feed_dir, dry=args.干跑)
            total_ok += r["ok"]
            total_fail += r["fail"]
        log(f"\n回填毕：✓ {total_ok} 章  × {total_fail} 败", "info")
        return 0 if total_fail == 0 else 1

    if args.在线:
        result = generate_online(tasks, chap_filter=chap_filter, dry=args.干跑)
        log(
            f"\n在线生成毕：✓ {result['ok']} 章  × {result['fail']} 败  ⊝ {result['skipped']} 跳",
            "info",
        )
        return 0 if result["fail"] == 0 else 1

    # 默：离线导出（按课分组）
    course_dirs_map: dict[str, list[dict]] = {}
    for t in tasks:
        course_dirs_map.setdefault(t["course_dir"], []).append(t)

    total_exp = 0
    for cd, cd_tasks in sorted(course_dirs_map.items()):
        cd_path = Path(cd)
        feed_dir = ROOT / ".道喂任务" / cd_path.name
        n_exp = export_offline(cd_tasks, feed_dir, chap_filter=chap_filter)
        total_exp += n_exp

    log(f"\n离线导出毕：共 {total_exp} 章图谱任务", "info")
    log("→ 将 .道喂任务/<课>/图谱/*.json 中的 system+user 喂给 LLM，", "dim")
    log("  将返回 JSON 存为同名文件于 .道喂任务/<课>/图谱/_resp/<同名>.json，", "dim")
    log("  然后运行：python 课件_图谱.py --课 <名> --回填", "dim")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("\n知止所以不殆。退也。", "warn")
        sys.exit(130)
