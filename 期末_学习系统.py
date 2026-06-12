# -*- coding: utf-8 -*-
"""
期末 学习系统 (final_study_system)  ——  以提取与间隔，固已得之知

道法：
    骨已立（章节素材），肉已生（复习要点）。
    然"读懂"非"记牢"——固知之效，在 **提取练习** 与 **间隔重复**。
    此关之事：不调 LLM，纯由已有素材 + OCR，为每课造一套可执行之"备考系统"：

        <课>/0X_解析成果/_学习系统/
        ├── 00_备考总纲.md   学习科学原则 + 三段备考 + 间隔重复日历 + 交错刷题序 + 每日清单 + 元认知自查
        ├── 自测题库.md       闭卷提取题（答案默藏·<details>）—— 效用最高之法
        └── 速记卡.md         填空卡（cloze）—— 间隔重复之载体

    已填要点之章 → 题与卡皆实；未填之章 → 出"回忆点"脚手架（待 LLM 填实后自动转实）。

用法:
    python 期末_学习系统.py                      # 全部在修课夹
    python 期末_学习系统.py -f 流体              # 仅含"流体"之课
    python 期末_学习系统.py --考试日 2026-06-25  # 指定考试日（默：今日+21）
    python 期末_学习系统.py --repo 解析仓库       # 改扫描根（默：仓库根之课夹）
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _yc_common import log, header, read_json  # noqa: E402
import 期末_综合汇编 as 汇编  # noqa: E402
import 学习科学 as 科  # noqa: E402


# ============================================================
# 章材内容抽取（复用汇编之器·取全量条目）
# ============================================================

def _chap_label(n: int) -> str:
    return "绪论" if n == 0 else f"第 {n} 章"


_CHECKBOX = re.compile(r"^\s*\[[ xX]\]\s*")


def _clean_item(s: str) -> str:
    """去任务列表勾选框等残留装饰（_strip_md 未尽者）。"""
    return _CHECKBOX.sub("", (s or "").strip()).strip()


def _items_of(review: str, keyword: str, n: int = 50) -> list[str]:
    """从复习要点区取某 H3 下之全部条目（去 markdown 装饰）。"""
    block = 汇编._extract_h3(review, keyword)
    if not block:
        return []
    return [it for it in (_clean_item(x) for x in 汇编._first_items(block, n=n)) if it]


def 读章要点(course_dir: Path, chapter: dict) -> dict:
    """读一章素材，抽出造题/造卡所需之结构化条目。"""
    r = 汇编.read_chapter_review(course_dir, chapter)
    review = r.get("review", "")
    out = {
        "num": chapter.get("chapter_num", 0),
        "title": chapter.get("chapter_title", ""),
        "filled": r.get("filled", False),
        "概念": [],
        "考点": [],
        "易错": [],
        "思考题块": "",
    }
    if review:
        out["概念"] = _items_of(review, "核心概念")
        out["考点"] = _items_of(review, "高频考点")
        out["易错"] = _items_of(review, "易错")
        块 = 汇编._extract_h3(review, "思考")
        # 去已勾选框标记（- [x] / - [ ]），还原为普通列表，免视觉杂讯
        out["思考题块"] = re.sub(r"(?m)^(\s*[-*]\s*)\[[ xX]\]\s*", r"\1", 块)
    return out


# ============================================================
# 一、备考总纲
# ============================================================

def 生成备考总纲(chart: dict, 章信息: list[dict], 今日: date, 考试日: date) -> str:
    course = chart.get("course_name", "")
    teacher = chart.get("teacher", "")
    semester = chart.get("semester", "")
    标签 = [f"{_chap_label(c['num'])}" + (f" {c['title']}" if c["title"] else "") for c in 章信息]

    L: list[str] = []
    L.append(f"# {course} · 期末备考总纲")
    L.append("")
    L.append(f"> 教师：{teacher} · 学期：{semester}")
    L.append(f"> 生成于 {今日.isoformat()} · 目标考试日 **{考试日.isoformat()}**（共 {(考试日-今日).days} 天）")
    L.append(f"> 章数：{len(章信息)} · 已填要点：{sum(1 for c in 章信息 if c['filled'])} 章")
    L.append("")
    L.append("> *为学者日益，闻道者日损。* —— 复习非求多读，而求记牢；记牢之法，已有实证。")
    L.append("")
    L.append("---")
    L.append("")
    # 学习科学原则
    L.append("## 一 · 复习之道（实证为据）")
    L.append("")
    L.append("> 据 Dunlosky et al. 2013（《Psychological Science in the Public Interest》）"
             "与 Carpenter, Pan & Butler 2022（《Nature Reviews Psychology》）：")
    L.append("")
    L.append("| 技法 | 效用 | 怎么做 |")
    L.append("|---|---|---|")
    L.append("| **提取练习**（自测/默写） | **高** | 合上书，先答 `自测题库.md`，再对照——别只重读 |")
    L.append("| **间隔重复**（分散练习） | **高** | 按下方日历，隔日/隔周回提取，别考前突击一次 |")
    L.append("| 交错练习 | 中 | 按下方“交错刷题序”混章做题，别一章刷到底 |")
    L.append("| 自我解释 / 追问“为什么” | 中 | 每个考点问自己“为什么成立、与上一章何关” |")
    L.append("| 双重编码（图像） | 中 | 看/画每章思维导图，文字配图记 |")
    L.append("| 高亮 · 重读 · 摘抄 | **低** | 感觉努力实则低效，不作为主手段 |")
    L.append("")
    # 三段备考
    段 = 科.备考阶段(今日, 考试日)
    L.append("## 二 · 三段备考（先懂 → 后测 → 终模考）")
    L.append("")
    for s in 段:
        L.append(f"- **{s.名}**（{s.始.isoformat()} → {s.末.isoformat()} · {s.天数} 天）：{s.要旨}")
    L.append("")
    # 间隔重复日历
    程 = 科.间隔重排程(标签, 今日, 考试日)
    L.append("## 三 · 间隔重复日历（首学 + 1/3/7/14 天回提取）")
    L.append("")
    if not 程:
        L.append("> （无章节或窗口为零）")
    else:
        L.append("| 日期 | 当日任务 |")
        L.append("|---|---|")
        for it in 程:
            L.append(f"| {it.日期.isoformat()} | " + "<br>".join(it.任务) + " |")
    L.append("")
    L.append("> 📖 = 首次学习（求懂）；🔁 = 闭卷提取复习（求牢）。错过某日，顺延即可，勿弃。")
    L.append("")
    # 交错刷题序
    轮 = 科.交错复习序(标签, 轮数=3)
    L.append("## 四 · 交错刷题序（三轮 · 混章不连刷）")
    L.append("")
    for i, r in enumerate(轮, 1):
        L.append(f"{i}. " + " → ".join(r))
    L.append("")
    # 每日清单
    L.append("## 五 · 每日提取清单（贴在桌前）")
    L.append("")
    L.append("- [ ] 今日“首学”章：通读图文 + 看思维导图（求懂）")
    L.append("- [ ] 今日“回提取”章：**闭卷**做 `自测题库.md` 对应题，再对照订正")
    L.append("- [ ] 过一遍 `速记卡.md`（答不出的标记，明日优先）")
    L.append("- [ ] 把每个考点用“一句话”向自己解释“为什么”（自我解释）")
    L.append("")
    # 元认知
    L.append("## 六 · 元认知自查（别被“熟悉感”骗了）")
    L.append("")
    L.append("> *知不知，尚矣；不知不知，病矣。*")
    L.append("")
    L.append("- “读过了”≠“答得出”。判断标准只有一个：**合上书能否复述/默写**。")
    L.append("- 越是“看着眼熟”的内容越危险——优先去**自测**它，而非重读它。")
    L.append("- 每轮自测后，把答错/卡壳的章节，提前到下一日的“回提取”。")
    L.append("")
    # 索引
    L.append("## 七 · 配套材料")
    L.append("")
    L.append("- `自测题库.md` —— 闭卷提取题（按章 · 答案默藏）")
    L.append("- `速记卡.md` —— 填空卡（适合碎片时间 + 间隔重复）")
    L.append("- `../_素材/_综合复习资料.md` —— 图文 + 思维导图全本")
    L.append("- `../_素材/_期末速查.md` —— 一页速查表")
    L.append("")
    未填 = [c for c in 章信息 if not c["filled"]]
    if 未填:
        names = "、".join(f"{_chap_label(c['num'])}" for c in 未填)
        L.append(f"> ⚠ 待 LLM 填实之章：{names}。填实后重跑本脚本，题与卡自动转为实题。")
        L.append("")
    return "\n".join(L)


# ============================================================
# 二、自测题库（提取练习）
# ============================================================

def 生成自测题库(chart: dict, 章信息: list[dict]) -> str:
    course = chart.get("course_name", "")
    L: list[str] = []
    L.append(f"# {course} · 自测题库（闭卷提取）")
    L.append("")
    L.append("> **用法**：先合上书答，再展开“参考答案”对照。**提取**比重读有效得多。")
    L.append("> 答错/卡壳处，回 `_综合复习资料.md` 对应章精看，并标入次日复习。")
    L.append("")
    L.append("---")
    L.append("")
    总题 = 0
    for c in 章信息:
        lab = _chap_label(c["num"]) + (f" · {c['title']}" if c["title"] else "")
        L.append(f"## {lab}")
        L.append("")
        if not c["filled"]:
            L.append("> （本章要点待 LLM 填实）暂以“回忆脚手架”代之：")
            L.append("")
            L.append(f"1. 合上书，用 3–5 句话复述「{c['title'] or lab}」的核心内容，再对照 `_综合复习资料.md`。")
            L.append("2. 本章最可能考的 3 个点是什么？为什么？")
            L.append("")
            continue
        q = 0
        # 概念 → 名词解释
        for item in c["概念"]:
            名, _, 释 = item.partition("：")
            if not 释:
                名, _, 释 = item.partition(":")
            名 = (名 or item).strip()
            释 = 释.strip()
            if not 释:
                continue
            q += 1
            总题 += 1
            L.append(f"**Q{q}（名词解释）** {名}？")
            L.append("")
            L.append("<details><summary>参考答案</summary>")
            L.append("")
            L.append(释)
            L.append("")
            L.append("</details>")
            L.append("")
        # 考点 → 解释/默写
        for pt in c["考点"]:
            pt = pt.strip()
            if not pt:
                continue
            q += 1
            总题 += 1
            L.append(f"**Q{q}（考点·闭卷默写）** 请展开论述：{pt}")
            L.append("")
            L.append("<details><summary>提示 / 要点</summary>")
            L.append("")
            L.append(f"对照本章“高频考点 / 核心概念”作答；要点：{pt}")
            L.append("")
            L.append("</details>")
            L.append("")
        # 思考题（已含答案）
        if c["思考题块"]:
            L.append("**思考题（综合应用）**")
            L.append("")
            L.append("<details><summary>题与参考答案</summary>")
            L.append("")
            L.append(c["思考题块"])
            L.append("")
            L.append("</details>")
            L.append("")
        if q == 0 and not c["思考题块"]:
            L.append("> （本章已填，但未抽到结构化条目，请直接看 `_综合复习资料.md`）")
            L.append("")
    L.insert(2, f"> 共 {总题} 道结构化提取题（不含思考题与脚手架）。\n")
    return "\n".join(L)


# ============================================================
# 三、速记卡（cloze · 间隔重复）
# ============================================================

def 生成速记卡(chart: dict, 章信息: list[dict]) -> str:
    course = chart.get("course_name", "")
    L: list[str] = []
    L.append(f"# {course} · 速记卡（填空 · 间隔重复）")
    L.append("")
    L.append("> 碎片时间用：看正面回忆背面，答不出的打 ✗，按间隔重复优先复习。")
    L.append("")
    L.append("---")
    L.append("")
    总卡 = 0
    for c in 章信息:
        if not c["概念"]:
            continue
        卡 = 科.生成填空卡(c["概念"])
        if not 卡:
            continue
        lab = _chap_label(c["num"]) + (f" · {c['title']}" if c["title"] else "")
        L.append(f"## {lab}")
        L.append("")
        for k in 卡:
            总卡 += 1
            L.append(f"- {k['正面']}")
            L.append(f"  - <details><summary>答案</summary> {k['背面']} </details>")
        L.append("")
    if 总卡 == 0:
        L.append("> （暂无可生成填空卡之结构化概念——待相关章节 LLM 填实后重跑）")
        L.append("")
    else:
        L.insert(2, f"> 共 {总卡} 张卡。\n")
    return "\n".join(L)


# ============================================================
# 课级处理
# ============================================================

def 处理一课(parse_dir: Path, 今日: date, 考试日: date) -> dict:
    chart = read_json(parse_dir / "_章节图谱.json")
    if not chart or not chart.get("chapters"):
        return {"dir": parse_dir.as_posix(), "skipped": True}
    章信息 = [读章要点(parse_dir, ch) for ch in chart["chapters"]]
    out_dir = parse_dir / "_学习系统"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "00_备考总纲.md").write_text(
        生成备考总纲(chart, 章信息, 今日, 考试日), encoding="utf-8")
    (out_dir / "自测题库.md").write_text(
        生成自测题库(chart, 章信息), encoding="utf-8")
    (out_dir / "速记卡.md").write_text(
        生成速记卡(chart, 章信息), encoding="utf-8")
    return {
        "dir": parse_dir.as_posix(),
        "course": chart.get("course_name"),
        "chapters": len(章信息),
        "filled": sum(1 for c in 章信息 if c["filled"]),
    }


# ============================================================
# 发现课夹
# ============================================================

def 发现解析目录(root: Path, repo: str | None) -> list[Path]:
    dirs: list[Path] = []
    if repo:
        base = Path(repo)
        if not base.is_absolute():
            base = root / repo
        dirs = [d for d in sorted(base.iterdir())
                if d.is_dir() and (d / "_章节图谱.json").exists()] if base.exists() else []
    else:
        # 仓库根之课夹：<课>/0X_解析成果/_章节图谱.json（排除 解析仓库 冗余镜像）
        for p in sorted(root.glob("*/0*_解析成果/_章节图谱.json")):
            dirs.append(p.parent)
    return dirs


def main() -> None:
    parser = argparse.ArgumentParser(
        description="期末 学习系统 —— 以提取与间隔，固已得之知",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--filter", "-f", action="append", default=None,
                        help="仅处理名含此关键字之课（可多次）")
    parser.add_argument("--考试日", "--exam", dest="exam", default=None,
                        help="目标考试日 YYYY-MM-DD（默：今日+21）")
    parser.add_argument("--repo", "-r", default=None,
                        help="改扫描根目录（默：仓库根之课夹）")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    今日 = date.today()
    if args.exam:
        try:
            考试日 = datetime.strptime(args.exam, "%Y-%m-%d").date()
        except ValueError:
            log(f"× 考试日格式错（需 YYYY-MM-DD）：{args.exam}", "err")
            sys.exit(1)
    else:
        考试日 = 今日 + timedelta(days=21)

    header("期末 学习系统 —— 提取练习 · 间隔重复", width=58)
    log(f"  今日 {今日} · 考试日 {考试日}（{(考试日-今日).days} 天）", "dim")

    dirs = 发现解析目录(root, args.repo)
    if args.filter:
        dirs = [d for d in dirs if any(kw in d.parent.name or kw in d.as_posix()
                                       for kw in args.filter)]
    if not dirs:
        log("∅ 未发现可处理之解析目录", "warn")
        return

    log(f"\n共 {len(dirs)} 个解析目录", "info")
    done = 0
    for d in dirs:
        info = 处理一课(d, 今日, 考试日)
        if info.get("skipped"):
            log(f"  ∅ {d.parent.name:<16s}（无图谱/无章）", "dim")
            continue
        log(f"  ✓ {str(info.get('course','')):<16s} "
            f"{info['filled']}/{info['chapters']} 章已填 → _学习系统/（3 件）", "ok")
        done += 1

    header(f"学习系统毕  ——  {done} 门课已出备考总纲", width=58)


if __name__ == "__main__":
    main()
