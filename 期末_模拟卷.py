# -*- coding: utf-8 -*-
"""
期末 模拟卷 (final_mockexam)  ——  善始且善成

第八关 (兼容旧"第九关")。链路之末：以课程之已填要点（最终复习资料）为蓝本，
让 LLM 出一份期末模拟卷；并存为 markdown 供随时复用。

双源（反者道之动）：
  · **课夹自治**（主）：<workspace>/<课>/02_解析成果/_章节图谱.json （或 03_）
  · **解析仓库**（兜底）：<workspace>/解析仓库/<课>-<学期>-...
  → 同名课程仅采课夹版（去重）

双路径（同道喂之器）：
  · 离线：导出 .模拟卷任务/<课>_期末模拟卷.json + 提示语，可任喂 LLM
  · 在线：调 LLM → 自动生卷 → 写 <课>/0X_解析成果/_素材/_期末模拟卷.md

用法:
    python 期末_模拟卷.py                            # 默：离线导出（全课）
    python 期末_模拟卷.py -c 环境法学                 # 单课离线
    python 期末_模拟卷.py -c 环境法学 --在线          # 单课在线
    python 期末_模拟卷.py --在线 --max-chap-chars 4000 # 全课在线，章摘要限长
    python 期末_模拟卷.py --列                        # 列状（标 [课夹]/[仓库]）

道：
    "信言不美，美言不信。"
    出题不依虚言，唯据章谱与已填要点。无凭则不出。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _yc_common import log, header, read_json, parse_course_dirname  # noqa: E402

_REPO = Path(__file__).resolve().parent
_仓库 = _REPO / "解析仓库"
_导出根 = _REPO / ".模拟卷任务"

# 课夹自治 · 解析夹候选名（与 课程_闭环.py 之 PARSE_DIR_CANDIDATES 同）
_PARSE_DIR_CANDIDATES = ["02_解析成果", "03_解析成果"]
# 不视为课夹之目录（与 课程_闭环.py 之 EXCLUDE_NAMES 同）
_EXCLUDE_COURSE_NAMES = {
    "yuketang", "雨课堂PDF", "解析仓库", "__pycache__",
    ".llm_cache", ".yuketang", ".图道_测试", ".道喂任务",
    ".模拟卷任务", "_archive",
}

_REVIEW_H2 = re.compile(r"^##\s+复习要点.*?$", re.MULTILINE)
_NEXT_H2 = re.compile(r"^##\s+", re.MULTILINE)


# ─────────────────────────────────────────────
# 一、扫课程，凑章摘要
# ─────────────────────────────────────────────

def _chap_md_name(n: int, title: str) -> str:
    """与 课件_知识素材.py 一致之章 md 命名。"""
    t = (title or "无题")
    for bad in '\\/:*?"<>|':
        t = t.replace(bad, "_")
    t = t.strip()[:40]
    if n == 0:
        return f"_第00章_{t}.md".replace(" ", "_")
    return f"_第{n:02d}章_{t}.md".replace(" ", "_")


def _extract_review_section(text: str) -> str:
    """从章 md 抽"复习要点"区段全文；未填返空串。"""
    m = _REVIEW_H2.search(text)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = _NEXT_H2.search(rest)
    end = m.end() + nxt.start() if nxt else len(text)
    section = text[m.start():end].strip()
    if "LLM 未填" in section and len(section) < 240:
        return ""
    return section


def _build_chap_summary(course_dir: Path, chart: dict, max_chap_chars: int = 6000) -> tuple[str, dict]:
    """以章为单位，凑出可喂之课程素材摘要。

    返 (摘要全文, 统计 dict)
    """
    parts: list[str] = []
    filled = 0
    unfilled = 0
    for ch in chart.get("chapters", []):
        n = ch.get("chapter_num")
        title = ch.get("chapter_title", "")
        label = "绪论" if n == 0 else f"第 {n} 章"
        pp = ch.get("primary", {}).get("page_count", 0)
        head = f"### {label} · {title}（主版 {pp} 页）"
        md_path = course_dir / "_素材" / _chap_md_name(n, title)
        if md_path.exists():
            text = md_path.read_text(encoding="utf-8")
            review = _extract_review_section(text)
            if review:
                filled += 1
                # 删 H2 标头
                body = re.sub(r"^##\s+复习要点.*?\n+", "", review, count=1, flags=re.MULTILINE)
                # 控长
                if len(body) > max_chap_chars:
                    body = body[:max_chap_chars] + "\n\n…（已截，余略）"
                parts.append(head + "\n\n" + body.strip())
                continue
        unfilled += 1
        parts.append(head + "\n\n> 复习要点尚未填充，仅以章题为引。")
    return "\n\n".join(parts), {"filled": filled, "unfilled": unfilled}


# ─────────────────────────────────────────────
# 二、扫一课，凑任务材料
# ─────────────────────────────────────────────

def _find_parse_dir(course_root: Path) -> Path | None:
    """于课夹下找解析夹（02_解析成果/ 或 03_解析成果/）。"""
    for cand in _PARSE_DIR_CANDIDATES:
        d = course_root / cand
        if d.is_dir():
            return d
    return None


def _scan_courses(course_filter: list[str] | None) -> list[dict]:
    """双源扫描：先采课夹自治模式（<workspace>/<课>/0X_解析成果/），
    再采旧 解析仓库/<课>/（向后兼容）；据 course_name 去重，课夹优先。

    反者道之动：闭环主居课夹，仓库为兜底。
    """
    tasks: list[dict] = []
    seen: set[str] = set()

    def _matches(d: Path, cn: str) -> bool:
        if not course_filter:
            return True
        return any(kw in d.name or kw in cn for kw in course_filter)

    # 一·课夹自治模式
    for d in sorted(_REPO.iterdir()):
        if (
            not d.is_dir()
            or d.name.startswith(".")
            or d.name.startswith("_")
            or d.name in _EXCLUDE_COURSE_NAMES
        ):
            continue
        parse_dir = _find_parse_dir(d)
        if not parse_dir:
            continue
        chart = read_json(parse_dir / "_章节图谱.json")
        if not chart or not chart.get("chapters"):
            continue
        cn = chart.get("course_name") or d.name
        if not _matches(d, cn):
            continue
        if cn in seen:
            continue
        seen.add(cn)
        tasks.append({
            "course_dir": parse_dir,
            "course_name": cn,
            "teacher": chart.get("teacher", ""),
            "semester": chart.get("semester", ""),
            "chart": chart,
            "source": "课夹",
            "course_root": d,
        })

    # 二·解析仓库（向后兼容；同名者跳）
    if _仓库.exists():
        for d in sorted(_仓库.iterdir()):
            if not d.is_dir():
                continue
            chart = read_json(d / "_章节图谱.json")
            if not chart or not chart.get("chapters"):
                continue
            cn = chart.get("course_name") or d.name
            if not _matches(d, cn):
                continue
            if cn in seen:
                continue
            seen.add(cn)
            tasks.append({
                "course_dir": d,
                "course_name": cn,
                "teacher": chart.get("teacher", ""),
                "semester": chart.get("semester", ""),
                "chart": chart,
                "source": "仓库",
                "course_root": d,
            })

    return tasks


# ─────────────────────────────────────────────
# 三、出卷之提示
# ─────────────────────────────────────────────

def _build_mock_task(task: dict, *, max_chap_chars: int = 6000, 题型: dict | None = None):
    from _道说_提示库 import 模拟卷任务
    summary, stat = _build_chap_summary(task["course_dir"], task["chart"], max_chap_chars=max_chap_chars)
    pt = 模拟卷任务.build(course=task["course_name"], chap_summary=summary, 题型分布=题型)
    pt.meta["filled_chapters"] = stat["filled"]
    pt.meta["unfilled_chapters"] = stat["unfilled"]
    pt.meta["chap_summary_len"] = len(summary)
    return pt, summary


# ─────────────────────────────────────────────
# 四、回写：模拟卷 markdown
# ─────────────────────────────────────────────

def _mock_to_md(course_name: str, teacher: str, semester: str, result) -> str:
    """模拟卷结果 → 完整试卷 markdown。"""
    lines: list[str] = []
    lines.append(f"# {course_name} · 期末模拟卷")
    lines.append("")
    lines.append(f"> 教师: {teacher} · 学期: {semester}")
    lines.append(f"> 自《最终复习资料》自举而生，仅作复习自测。")
    lines.append(f"> 出题时刻：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # 一、选择
    if result.选择题:
        lines.append(f"## 一、单项选择题（共 {len(result.选择题)} 题）")
        lines.append("")
        for i, q in enumerate(result.选择题, 1):
            if not isinstance(q, dict):
                continue
            lines.append(f"**{i}.** {q.get('q', '').strip()}")
            for opt in q.get("options", []) or []:
                lines.append(f"  - {opt}")
            ans = q.get("answer", "")
            exp = q.get("explain", "")
            lines.append("")
            lines.append("<details><summary>📝 参考答案（先闭卷作答，再展开对照）</summary>")
            lines.append("")
            lines.append(f"答：**{ans}**" + (f"  　解析：{exp}" if exp else ""))
            lines.append("")
            lines.append("</details>")
            lines.append("")
    # 二、填空
    if result.填空题:
        lines.append(f"## 二、填空题（共 {len(result.填空题)} 题）")
        lines.append("")
        for i, q in enumerate(result.填空题, 1):
            if not isinstance(q, dict):
                continue
            lines.append(f"**{i}.** {q.get('q', '').strip()}")
            lines.append("")
            lines.append("<details><summary>📝 参考答案</summary>")
            lines.append("")
            lines.append(f"答：**{q.get('answer', '')}**")
            lines.append("")
            lines.append("</details>")
            lines.append("")
    # 三、名解
    if result.名词解释:
        lines.append(f"## 三、名词解释（共 {len(result.名词解释)} 题）")
        lines.append("")
        for i, q in enumerate(result.名词解释, 1):
            if not isinstance(q, dict):
                continue
            lines.append(f"**{i}.** {q.get('q', '')}")
            lines.append("")
            lines.append("<details><summary>📝 参考答案</summary>")
            lines.append("")
            lines.append(f"答：{q.get('answer', '')}")
            lines.append("")
            lines.append("</details>")
            lines.append("")
    # 四、简答
    if result.简答题:
        lines.append(f"## 四、简答题（共 {len(result.简答题)} 题）")
        lines.append("")
        for i, q in enumerate(result.简答题, 1):
            if not isinstance(q, dict):
                continue
            lines.append(f"**{i}.** {q.get('q', '').strip()}")
            lines.append("")
            lines.append("<details><summary>📝 参考答案（答要点）</summary>")
            lines.append("")
            lines.append(f"答要点：{q.get('answer', '')}")
            lines.append("")
            lines.append("</details>")
            lines.append("")
    # 五、论述
    if result.论述题:
        lines.append(f"## 五、论述题（共 {len(result.论述题)} 题）")
        lines.append("")
        for i, q in enumerate(result.论述题, 1):
            if not isinstance(q, dict):
                continue
            lines.append(f"**{i}.** {q.get('q', '').strip()}")
            lines.append("")
            lines.append("<details><summary>📝 参考答案（答框架）</summary>")
            lines.append("")
            lines.append(f"答框架：{q.get('answer', '')}")
            lines.append("")
            lines.append("</details>")
            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("> 正言若反：模拟卷宜与原图、章 md 互参，方知所考之实。")
    return "\n".join(lines)


# ─────────────────────────────────────────────
# 五、离线/在线
# ─────────────────────────────────────────────

def _offline_export(task: dict, *, max_chap_chars: int, 题型: dict | None) -> Path:
    pt, summary = _build_mock_task(task, max_chap_chars=max_chap_chars, 题型=题型)
    _导出根.mkdir(parents=True, exist_ok=True)
    out = _导出根 / f"{task['course_name']}_期末模拟卷.json"
    payload = {
        "task": pt.meta,
        "system": pt.system,
        "user": pt.user,
        "schema": pt.schema,
        "chap_summary_excerpt": summary[:2000],
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    # 配套人读版（含 system + user 之提示文）
    md = _导出根 / f"{task['course_name']}_期末模拟卷_提示.md"
    md.write_text(
        f"# {task['course_name']} · 期末模拟卷·LLM 提示\n\n"
        f"> 喂下文给任意 LLM（ChatGPT/Claude/Kimi/通义...），取 JSON 回，存为 `{task['course_name']}_答.json`，\n"
        f"> 再以 `python 期末_模拟卷.py -c {task['course_name'][:6]} --纳入 <答 json>` 入卷。\n\n"
        f"## system\n\n```\n{pt.system}\n```\n\n"
        f"## user\n\n```\n{pt.user}\n```\n\n"
        f"## schema 提示\n\n```json\n{json.dumps(pt.schema, ensure_ascii=False, indent=2)}\n```\n",
        encoding="utf-8",
    )
    return out


def _online_generate(task: dict, *, max_chap_chars: int, 题型: dict | None, dry_run: bool = False) -> tuple[bool, str]:
    from _道说_提示库 import 模拟卷任务
    from _llm_道 import LLMClient
    cli = LLMClient.from_env(profile="long")
    if not cli.config.is_ready():
        cli = LLMClient.from_env(profile="default")
    if not cli.config.is_ready():
        return False, "未配 LLM（.env 缺 API key）"
    pt, summary = _build_mock_task(task, max_chap_chars=max_chap_chars, 题型=题型)
    if dry_run:
        return True, f"DRY: system+user={len(pt.system)+len(pt.user)} 字, summary={len(summary)} 字"

    log(f"  → 调 LLM ({cli.config.model})...", "dim")
    t0 = time.time()
    try:
        raw = cli.chat_json(pt.user, system=pt.system, schema_hint=pt.schema, strict=False)
    except Exception as e:
        return False, f"LLM 调用败: {e}"
    dt = time.time() - t0
    if not isinstance(raw, dict):
        return False, f"返非 JSON ({dt:.1f}s): {str(raw)[:200]}"
    result = 模拟卷任务.parse(raw)
    md = _mock_to_md(task["course_name"], task["teacher"], task["semester"], result)
    out = task["course_dir"] / "_素材" / "_期末模拟卷.md"
    out.write_text(md, encoding="utf-8")
    return True, (
        f"✓ {dt:.1f}s 选{len(result.选择题)} 填{len(result.填空题)} "
        f"名{len(result.名词解释)} 简{len(result.简答题)} 论{len(result.论述题)} → {out.relative_to(_REPO)}"
    )


def _intake_answer(task: dict, answer_path: Path) -> tuple[bool, str]:
    """将离线喂 LLM 之答（JSON）纳入为本课模拟卷 md。"""
    from _道说_提示库 import 模拟卷任务
    if not answer_path.exists():
        return False, f"答文件不存: {answer_path}"
    try:
        raw = json.loads(answer_path.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"读 JSON 败: {e}"
    if not isinstance(raw, dict):
        return False, "答非 JSON 对象"
    result = 模拟卷任务.parse(raw)
    md = _mock_to_md(task["course_name"], task["teacher"], task["semester"], result)
    out = task["course_dir"] / "_素材" / "_期末模拟卷.md"
    out.write_text(md, encoding="utf-8")
    return True, (
        f"✓ 选{len(result.选择题)} 填{len(result.填空题)} "
        f"名{len(result.名词解释)} 简{len(result.简答题)} 论{len(result.论述题)} → {out.relative_to(_REPO)}"
    )


# ─────────────────────────────────────────────
# 六、CLI
# ─────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="期末 模拟卷 —— 第八关 · 双源扫描")
    p.add_argument("--课", "-c", action="append", help="课程名关键字（可多次）")
    p.add_argument("--在线", action="store_true", help="调 LLM 在线生卷（默：离线导出）")
    p.add_argument("--列", "-l", action="store_true", help="仅列可生卷之课")
    p.add_argument("--dry", action="store_true", help="预估，不真调")
    p.add_argument("--max-chap-chars", type=int, default=6000, help="单章摘要长上限（防爆窗）")
    p.add_argument(
        "--纳入", default=None,
        help="纳入 LLM 离线答 JSON 文件路径（须配 -c <课>）",
    )
    p.add_argument("--题型", default=None,
                   help="题型分布 JSON 形如 '{\"选择题\":10,\"简答题\":5,...}'")
    args = p.parse_args()

    header("期末 模拟卷 —— 第八关", width=58)

    课型 = None
    if args.题型:
        try:
            课型 = json.loads(args.题型)
        except Exception as e:
            log(f"  × 题型 JSON 解析败: {e}", "err")
            return

    tasks = _scan_courses(args.课)
    log(f"  扫得 {len(tasks)} 门有图谱之课", "info")

    if args.列:
        for t in tasks:
            ch = t["chart"]
            n = len(ch.get("chapters", []))
            src = t.get("source", "?")
            log(
                f"  · [{src}] {t['course_name']:<18s} {n} 章 · {t['teacher']}",
                "dim",
            )
        return

    if not tasks:
        log("× 无可生卷之课。检查 -c <课>。", "warn")
        return

    if args.纳入:
        if len(tasks) != 1:
            log("× 纳入须指明唯一课。请加 -c <课名关键字>。", "err")
            return
        ok, msg = _intake_answer(tasks[0], Path(args.纳入))
        log(f"  {msg}", "ok" if ok else "err")
        return

    成 = 失 = 0
    for i, t in enumerate(tasks, 1):
        log(f"\n[{i}/{len(tasks)}] {t['course_name']} · {t['teacher']}", "title")
        try:
            if args.在线:
                ok, msg = _online_generate(t, max_chap_chars=args.max_chap_chars, 题型=课型, dry_run=args.dry)
                log(f"  {msg}", "ok" if ok else "err")
                成 += int(ok); 失 += int(not ok)
            else:
                out = _offline_export(t, max_chap_chars=args.max_chap_chars, 题型=课型)
                log(f"  ✓ 离线导出: {out.relative_to(_REPO)}", "ok")
                log(f"      配套提示文: {out.with_name(out.stem.replace('期末模拟卷','期末模拟卷_提示')+'.md').name}", "dim")
                成 += 1
        except Exception as e:
            log(f"  × 异: {e}", "err")
            失 += 1

    header(f"模拟卷毕 —— 成 {成} · 败 {失}", width=58)


# ─────────────────────────────────────────────
# 七、与 课程_闭环.py 之协议（薄包装供其调用）
# ─────────────────────────────────────────────
# 课程_闭环.关_模拟卷 直接调 _offline_export / _online_generate；
# task["course_dir"] 须就课夹自治模式（指向 0X_解析成果/）。
# 见 课程_闭环.关_模拟卷 实现。


if __name__ == "__main__":
    main()
