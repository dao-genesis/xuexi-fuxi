# -*- coding: utf-8 -*-
"""
期末 全图 (semester_overview)  ——  执大象，天下往

第八关。跨课汇为一图，作学期复习总入口。

输出:
    解析仓库/_学期总图.md
        · 各课综览（课名/教师/学期/PDF/页/章/状态）
        · 进度跟踪（已填占位之章 / 共章）
        · 复习路径建议（按周排）
        · 速链表（各课图谱 / 素材 / 骨架）
        · 道喂任务清单（待人/LLM 填者）

道：
    "圣人执一，以为天下牧"——
    一图在手，知何已成、何将为、何以始。
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _yc_common import log, header, read_json, write_json  # noqa: E402

_REPO = Path(__file__).resolve().parent
_仓库 = _REPO / "解析仓库"

_复习要点标 = re.compile(r"^##\s+复习要点.*?$", re.MULTILINE)
_下个二级标 = re.compile(r"^##\s+", re.MULTILINE)


def _已填复习要点(content: str) -> bool:
    """判断章 md 是否已有实质“复习要点”。

    兼容 LLM 回写与人工填写；不再只认固定标题“复习要点 · LLM 协填”。
    """
    m = _复习要点标.search(content)
    if not m:
        return False
    rest = content[m.end():]
    nxt = _下个二级标.search(rest)
    section = rest[:nxt.start()] if nxt else rest
    section = section.strip()
    if not section:
        return False
    if "LLM 未填" in section and len(section) < 240:
        return False
    return True


# ─────────────────────────────────────────────
# 一、扫描
# ─────────────────────────────────────────────

def 扫_课程() -> list[dict]:
    """扫所有课程，归一为综览之 dict 列表。"""
    courses: list[dict] = []
    if not _仓库.exists():
        return []
    for d in sorted(_仓库.iterdir()):
        if not d.is_dir():
            continue
        course = _扫一课(d)
        if course:
            courses.append(course)
    return courses


def _扫一课(course_dir: Path) -> dict | None:
    """单课综览。"""
    course_json = course_dir / "_course.json"
    chart_json = course_dir / "_章节图谱.json"
    course_meta = read_json(course_json) or {}
    chart = read_json(chart_json) or {}

    if not course_meta and not chart:
        return None

    chapters = chart.get("chapters") or []
    material_dir = course_dir / "_素材"

    # 章节填写状（看每章 md 中是否含"复习要点 · LLM 协填"标志）
    chap_states: list[dict] = []
    for ch in chapters:
        md_path = _章md路径(course_dir, ch)
        filled = False
        size_kib = 0
        if md_path and md_path.exists():
            try:
                content = md_path.read_text(encoding="utf-8")
                size_kib = len(content.encode("utf-8")) // 1024
                filled = _已填复习要点(content)
            except Exception:
                pass
        chap_states.append({
            "num": ch.get("chapter_num"),
            "title": ch.get("chapter_title", ""),
            "primary_pages": ch.get("primary", {}).get("page_count", 0),
            "all_doc_count": len(ch.get("all_docs", []) or []),
            "md_path": str(md_path.relative_to(_REPO)) if md_path else "",
            "md_exists": md_path.exists() if md_path else False,
            "md_kib": size_kib,
            "filled": filled,
        })

    # 期末汇编三件
    has_skeleton = (material_dir / "_期末骨架.md").exists()
    has_quick = (material_dir / "_期末速查.md").exists()
    has_llm_prompt = (material_dir / "_LLM_提示语.md").exists()

    return {
        "name": course_meta.get("course_name") or chart.get("course_name") or course_dir.name,
        "teacher": course_meta.get("teacher") or chart.get("teacher", ""),
        "semester": course_meta.get("semester") or chart.get("semester", ""),
        "dir_name": course_dir.name,
        "rel_dir": str(course_dir.relative_to(_REPO)),
        "pdf_count": len(course_meta.get("documents", []) or []),
        "page_count": sum(d.get("page_count", 0) for d in (course_meta.get("documents", []) or [])),
        "chap_count": len(chapters),
        "chap_states": chap_states,
        "filled_count": sum(1 for c in chap_states if c["filled"]),
        "non_teaching_count": len(chart.get("non_teaching", []) or []),
        "uncategorized_count": len(chart.get("uncategorized", []) or []),
        "has_skeleton": has_skeleton,
        "has_quick": has_quick,
        "has_llm_prompt": has_llm_prompt,
    }


def _章md路径(course_dir: Path, chapter: dict) -> Path | None:
    """以 课件_知识素材.py 同规推得章 md 路径。"""
    n = chapter.get("chapter_num")
    title = chapter.get("chapter_title") or "无题"
    t_clean = title
    for bad in '\\/:*?"<>|':
        t_clean = t_clean.replace(bad, "_")
    t_clean = t_clean.strip()[:40]
    if n == 0:
        fname = f"_第00章_{t_clean}.md".replace(" ", "_")
    elif n is not None:
        fname = f"_第{n:02d}章_{t_clean}.md".replace(" ", "_")
    else:
        return None
    return course_dir / "_素材" / fname


# ─────────────────────────────────────────────
# 二、复习路径推算
# ─────────────────────────────────────────────

def 推_周次(总页数: int, 周数: int = 4) -> int:
    """以总页推每天页量。"""
    if not 总页数:
        return 0
    return max(1, 总页数 // (周数 * 7))


# ─────────────────────────────────────────────
# 三、生 markdown
# ─────────────────────────────────────────────

def 生_总图_md(courses: list[dict]) -> str:
    today = dt.date.today().isoformat()

    lines: list[str] = []
    lines.append("# 解析仓库 · 学期总图")
    lines.append("")
    lines.append(f"> 生成于 {today}")
    lines.append("> *执大象，天下往*")
    lines.append("")

    # 总数
    total_pdf = sum(c["pdf_count"] for c in courses)
    total_pages = sum(c["page_count"] for c in courses)
    total_chaps = sum(c["chap_count"] for c in courses)
    total_filled = sum(c["filled_count"] for c in courses)
    courses_with_chap = sum(1 for c in courses if c["chap_count"] > 0)
    courses_with_skel = sum(1 for c in courses if c["has_skeleton"])

    lines.append("## 一 · 总览")
    lines.append("")
    lines.append(f"- 课程总：**{len(courses)}** 门")
    lines.append(f"- 有章节者：**{courses_with_chap}** 门 / 有期末骨架：**{courses_with_skel}** 门")
    lines.append(f"- PDF 总：**{total_pdf}** 份 · 页总：**{total_pages}** 页")
    lines.append(f"- 章节总：**{total_chaps}** 章 · LLM 已填占位：**{total_filled}** 章 "
                 f"(**{(total_filled/max(1,total_chaps)*100):.0f}%**)")
    lines.append("")

    # 各课表
    lines.append("## 二 · 各课综览")
    lines.append("")
    lines.append("| 课程 | 教师 | 学期 | PDF | 页 | 章 | 已填 | 骨架 | 速查 | 提示 |")
    lines.append("|------|------|------|----:|----:|----:|:----:|:----:|:----:|:----:|")
    for c in courses:
        prog = ""
        if c["chap_count"]:
            prog = f"{c['filled_count']}/{c['chap_count']}"
        else:
            prog = "—"
        skel = "✓" if c["has_skeleton"] else "·"
        quick = "✓" if c["has_quick"] else "·"
        prompt = "✓" if c["has_llm_prompt"] else "·"
        lines.append(f"| **{c['name']}** | {c['teacher']} | {c['semester']} | "
                     f"{c['pdf_count']} | {c['page_count']} | {c['chap_count']} | "
                     f"{prog} | {skel} | {quick} | {prompt} |")
    lines.append("")

    # 复习路径
    lines.append("## 三 · 复习路径建议")
    lines.append("")
    lines.append("以**4 周**为期，按页数排各课优先级：")
    lines.append("")
    teaching_courses = [c for c in courses if c["chap_count"] > 0]
    teaching_courses_sorted = sorted(teaching_courses, key=lambda c: -c["page_count"])
    if teaching_courses_sorted:
        lines.append("| 课程 | 页 | 章 | 日均页 | 建议 |")
        lines.append("|------|---:|---:|------:|------|")
        for c in teaching_courses_sorted:
            d_pages = 推_周次(c["page_count"], 4)
            tip = ""
            if c["chap_count"] >= 6:
                tip = "重点：内容繁，分章细看"
            elif c["chap_count"] >= 3:
                tip = "中量：通览 + 要点"
            else:
                tip = "轻量：可速通"
            lines.append(f"| {c['name']} | {c['page_count']} | {c['chap_count']} | {d_pages} | {tip} |")
        lines.append("")

    # 进度细化
    lines.append("## 四 · 章节进度细化")
    lines.append("")
    for c in courses:
        if c["chap_count"] == 0:
            continue
        lines.append(f"### {c['name']}（{c['teacher']}）")
        lines.append("")
        lines.append("| 章 | 标题 | 页 | 文档 | md | 已填 |")
        lines.append("|---:|------|---:|---:|---:|:----:|")
        for ch in c["chap_states"]:
            n = ch["num"]
            chap_label = "绪" if n == 0 else f"第{n}章"
            md_state = "—"
            if ch["md_exists"]:
                md_state = f"{ch['md_kib']}KiB"
            filled = "✓" if ch["filled"] else "·"
            lines.append(f"| {chap_label} | {ch['title'][:30]} | {ch['primary_pages']} | "
                         f"{ch['all_doc_count']} | {md_state} | {filled} |")
        lines.append("")

    # 道喂待办
    lines.append("## 五 · 道喂待办（未填占位之章）")
    lines.append("")
    pending: list[tuple[str, dict]] = []
    for c in courses:
        for ch in c["chap_states"]:
            if not ch["filled"] and ch["num"] is not None:
                pending.append((c["name"], ch))
    if pending:
        lines.append(f"共 **{len(pending)}** 章待填。优先按页数：")
        lines.append("")
        lines.append("| 课程 | 章 | 标题 | 页 | 命令 |")
        lines.append("|------|---:|------|---:|------|")
        for cname, ch in sorted(pending, key=lambda x: -x[1]["primary_pages"])[:30]:
            n = ch["num"]
            cmd = f"`python 课件_道喂.py -c {cname[:6]} --章 {n} --在线 --拼网格`"
            lines.append(f"| {cname} | {n} | {ch['title'][:30]} | {ch['primary_pages']} | {cmd} |")
        if len(pending) > 30:
            lines.append("")
            lines.append(f"*余 {len(pending)-30} 条略。批量喂：`python 课件_道喂.py --在线 --拼网格`*")
        lines.append("")
    else:
        lines.append("✓ 所有章皆已填占位。")
        lines.append("")

    # 速链
    lines.append("## 六 · 速链")
    lines.append("")
    lines.append("- [全局图谱](_全局图谱.md)")
    lines.append("")
    for c in courses:
        if c["chap_count"] == 0:
            continue
        rel = c["rel_dir"].replace("\\", "/").replace("解析仓库/", "")
        lines.append(f"- **{c['name']}**：")
        lines.append(f"  - [章节图谱]({rel}/_章节图谱.md)")
        if c["has_skeleton"]:
            lines.append(f"  - [期末骨架]({rel}/_素材/_期末骨架.md)")
            lines.append(f"  - [期末速查]({rel}/_素材/_期末速查.md)")
            lines.append(f"  - [LLM 提示语]({rel}/_素材/_LLM_提示语.md)")
        lines.append("")

    # 道之教
    lines.append("---")
    lines.append("")
    lines.append("## 七 · 道之教")
    lines.append("")
    lines.append("> 图难于其易，为大于其细。")
    lines.append(">")
    lines.append("> 复习之事：先看此图明大势，再据各课骨架立专攻，")
    lines.append("> 终用 `课件_道喂.py` 调 LLM 填占位，章成则速查表自厚，")
    lines.append("> 期末模拟卷自来。")
    lines.append("")
    lines.append("**一日之计**:")
    lines.append("```bash")
    lines.append("# 1. 总枢全链路（增量）")
    lines.append("python 期末复习_总枢.py")
    lines.append("# 2. 看此学期总图（必先）")
    lines.append("# 3. 道喂未填之章（在线，须 .env 配 API key）")
    lines.append("python 课件_道喂.py --在线 --拼网格")
    lines.append("# 4. 重生汇编以纳新填之要点")
    lines.append("python 期末复习_总枢.py --only 汇编")
    lines.append("```")
    lines.append("")
    lines.append("> 知不知，尚矣。")
    lines.append("")
    return "\n".join(lines)


def 生_总图_json(courses: list[dict]) -> dict:
    """机读版（供他工具用）"""
    return {
        "generated_at": dt.datetime.now().isoformat(),
        "course_count": len(courses),
        "total_pdf": sum(c["pdf_count"] for c in courses),
        "total_pages": sum(c["page_count"] for c in courses),
        "total_chapters": sum(c["chap_count"] for c in courses),
        "total_filled": sum(c["filled_count"] for c in courses),
        "courses": courses,
    }


# ─────────────────────────────────────────────
# 四、CLI
# ─────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="期末 全图 —— 第八关")
    p.add_argument("--out", default=None, help="输出根（默：解析仓库）")
    p.add_argument("--json-only", action="store_true", help="仅输出 JSON")
    p.add_argument("--md-only", action="store_true", help="仅输出 markdown")
    args = p.parse_args()

    out_root = Path(args.out) if args.out else _仓库
    out_root.mkdir(parents=True, exist_ok=True)

    header("期末 全图 —— 执大象，天下往", width=58)

    courses = 扫_课程()
    log(f"  扫得 {len(courses)} 门课", "info")

    if not args.json_only:
        md = 生_总图_md(courses)
        out_md = out_root / "_学期总图.md"
        out_md.write_text(md, encoding="utf-8")
        log(f"  ✓ md → {out_md.relative_to(_REPO)}  ({len(md.encode('utf-8'))//1024} KiB)", "ok")

    if not args.md_only:
        data = 生_总图_json(courses)
        out_json = out_root / "_学期总图.json"
        write_json(out_json, data)
        log(f"  ✓ json → {out_json.relative_to(_REPO)}", "ok")

    # 进度速报
    total_chap = sum(c["chap_count"] for c in courses)
    total_filled = sum(c["filled_count"] for c in courses)
    if total_chap:
        pct = total_filled / total_chap * 100
        log(f"\n  进度: {total_filled}/{total_chap} 章已填占位 ({pct:.0f}%)", "info")

    header("全图毕", width=58)


if __name__ == "__main__":
    main()
