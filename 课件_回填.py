# -*- coding: utf-8 -*-
"""
课件 回填 (chapter_writeback)  ——  反者道之动 · 道喂之对偶

道法：
    与「课件_道喂.py --拼网格」成对偶。
    
    流：
        ① 课件_道喂.py --拼网格        →   .道喂任务/<课>/<章>.json + grid.jpg
        ② 主公手喂任意 LLM             →   LLM 返 JSON（含核心概念/公式/考点/...）
        ③ 课件_回填.py <task> <resp>   →   回写 _素材/_第NN章_xxx.md 之"复习要点"区
    
    无 .env、无网络、无 token——主公完全主之。
    一章一回填，章成则速查表自厚，期末资料自实。

用法:
    # 一章·从文件读响应
    python 课件_回填.py .道喂任务/环境毒理学/第01章_绪论.json LLM响应.json
    
    # 一章·从 stdin 读（粘贴方式）
    python 课件_回填.py .道喂任务/环境毒理学/第01章_绪论.json
    （之后粘贴 LLM 之 JSON 响应，Ctrl+Z + 回车 结束）
    
    # 批量·扫 .道喂任务/<课>/_resp/<章>.json
    python 课件_回填.py --batch
    python 课件_回填.py --batch -c 环境毒理学
    
    # 干跑·只显示将写入但不真写
    python 课件_回填.py .道喂任务/环境毒理学/第01章_绪论.json LLM响应.json --dry

道：
    "图难于其易，为大于其细"——
    分章细喂，得 JSON，回填一章；章章如此，全课乃成。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

from _yc_common import log, header  # noqa: E402
from _道说_提示库 import 章占位填充任务  # noqa: E402

_REPO = Path(__file__).resolve().parent
_道喂根 = _REPO / ".道喂任务"


# ─────────────────────────────────────────────
# 一、JSON 解析（容错）
# ─────────────────────────────────────────────

_JSON_FENCE = ("```json", "```JSON", "```")


def 去围栏(text: str) -> str:
    """去除 ```json...``` 包裹（若有）。复 _llm_道._strip_json_fence。"""
    s = text.strip()
    for pre in _JSON_FENCE:
        if s.startswith(pre):
            s = s[len(pre):].lstrip("\n").rstrip()
            if s.endswith("```"):
                s = s[:-3].rstrip()
            return s
    return s


def 提取JSON对象(text: str) -> dict | None:
    """从可能含杂文之 LLM 响应中抽出首个完整 JSON 对象。

    策略：
      1. 若整体本即合法 JSON，直接返
      2. 否则寻第一个 '{' 与匹配之 '}'，取之试解
      3. 仍败则返 None
    """
    s = 去围栏(text)
    if not s:
        return None

    # 直接试
    try:
        v = json.loads(s)
        return v if isinstance(v, dict) else None
    except json.JSONDecodeError:
        pass

    # 寻 { ... } 块（容许嵌套，简单括号配对）
    start = s.find("{")
    if start < 0:
        return None
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(s)):
        c = s[i]
        if esc:
            esc = False
            continue
        if c == "\\" and in_str:
            esc = True
            continue
        if c == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                block = s[start:i + 1]
                try:
                    v = json.loads(block)
                    return v if isinstance(v, dict) else None
                except json.JSONDecodeError:
                    return None
    return None


# ─────────────────────────────────────────────
# 二、回写章 md（与 课件_道喂.py 之 回写章md 同规）
# ─────────────────────────────────────────────

_占位标 = re.compile(r"^## 复习占位.*?$", re.MULTILINE)
_要点标 = re.compile(r"^## 复习要点.*?$", re.MULTILINE)
_次章标 = re.compile(r"^## ", re.MULTILINE)


def 回写章md(md_path: Path, 新要点md: str, *, dry: bool = False) -> tuple[bool, str]:
    """以新内容替换章 md 中之"复习占位..."或"复习要点..."区段。

    返 (成败, 信息)
    """
    if not md_path.exists():
        return False, f"章 md 不存: {md_path}"

    text = md_path.read_text(encoding="utf-8")
    m = _占位标.search(text) or _要点标.search(text)

    if not m:
        # 无占位区，追加
        new_text = text.rstrip() + "\n\n---\n\n" + 新要点md + "\n"
        action = "追加"
    else:
        start = m.start()
        rest = text[m.end():]
        next_m = _次章标.search(rest)
        end = m.end() + next_m.start() if next_m else len(text)
        new_text = text[:start] + 新要点md + "\n" + text[end:]
        action = "替换"

    delta = len(new_text.encode("utf-8")) - len(text.encode("utf-8"))
    info = f"{action}  {len(text)//1024}KiB → {len(new_text)//1024}KiB ({delta:+d} B)"

    if dry:
        return True, f"[DRY] {info}"

    md_path.write_text(new_text, encoding="utf-8")
    return True, info


# ─────────────────────────────────────────────
# 三、单章回填
# ─────────────────────────────────────────────

def 回填一章(task_path: Path, resp_text: str, *, dry: bool = False) -> tuple[bool, str]:
    """读 task.json + LLM 响应，调 章占位填充任务.parse + render_md，回写章 md。"""

    # ① 读 task.json
    if not task_path.exists():
        return False, f"task.json 不存: {task_path}"

    try:
        task_data = json.loads(task_path.read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"读 task.json 异: {e}"

    md_rel = task_data.get("md_path_to_write_back")
    if not md_rel:
        return False, "task.json 缺 md_path_to_write_back"
    md_path = _REPO / md_rel
    # 若是绝对路径或 D:\... 之 junction，直接用
    if not md_path.exists():
        md_path = Path(md_rel)

    # ② 解析 resp
    raw_dict = 提取JSON对象(resp_text)
    if not raw_dict:
        return False, f"响应中无可解之 JSON 对象（前 200 字：{resp_text[:200]!r}）"

    # ③ 任务·解析 + 渲染
    result = 章占位填充任务.parse(raw_dict)
    new_md = 章占位填充任务.render_md(result)

    # ④ 回写章 md 之要点
    ok, info = 回写章md(md_path, new_md, dry=dry)
    if not ok:
        return False, info

    # ⑤ 回填 _doc.json 之页文（一关二事：要点入 md + 页文入 doc）
    doc_text_msg = ""
    if result.页文转录:
        doc_json_rel = task_data.get("doc_json_path_rel")
        doc_json: Path | None = None
        if doc_json_rel:
            cand = _REPO / doc_json_rel
            if cand.exists():
                doc_json = cand
            else:
                p2 = Path(doc_json_rel)
                if p2.exists():
                    doc_json = p2
        # 兼容旧 task json（无 doc_json_path_rel）——从 page_paths 推
        if doc_json is None:
            pps = task_data.get("page_paths") or []
            if pps:
                first = _REPO / pps[0]
                if not first.exists():
                    first = Path(pps[0])
                if first.exists():
                    cand = first.parent / "_doc.json"
                    if cand.exists():
                        doc_json = cand

        if doc_json is not None:
            if dry:
                doc_text_msg = f" · 文 {len(result.页文转录)} 项 → {doc_json.name} [DRY]"
            else:
                upd, tot = 章占位填充任务.apply_page_texts(doc_json, result.页文转录)
                doc_text_msg = f" · 文 {upd}/{tot} 页 → _doc.json"
        else:
            doc_text_msg = " · ⚠ 无可解之 _doc.json（task 或老旧 · 可重生 task json）"

    detail = (
        f"页文{len(result.页文转录)}+"
        f"概念{len(result.核心概念)}+公式{len(result.关键公式)}+"
        f"案例{len(result.重要案例)}+考点{len(result.高频考点)}+"
        f"思考{len(result.思考题)}"
    )
    return True, f"{info} · {detail}{doc_text_msg}"


# ─────────────────────────────────────────────
# 四、CLI
# ─────────────────────────────────────────────

def cmd_one(args) -> int:
    task_path = Path(args.task)
    if not task_path.exists():
        log(f"× task.json 不存: {task_path}", "err")
        return 1

    # 读 resp：文件 / stdin
    if args.resp and args.resp != "-":
        resp_path = Path(args.resp)
        if not resp_path.exists():
            log(f"× 响应文件不存: {resp_path}", "err")
            return 1
        resp_text = resp_path.read_text(encoding="utf-8")
        log(f"  读响应自: {resp_path}  ({len(resp_text)} 字)", "dim")
    else:
        log("  请粘贴 LLM 响应 JSON，结束按 Ctrl+Z 回车 (Win) / Ctrl+D (nix)：", "warn")
        resp_text = sys.stdin.read()
        log(f"  收响应 {len(resp_text)} 字", "dim")

    if not resp_text.strip():
        log("× 响应为空", "err")
        return 1

    # 元
    try:
        meta = json.loads(task_path.read_text(encoding="utf-8")).get("task", {})
    except Exception:
        meta = {}
    course = meta.get("course", "?")
    chap = meta.get("chap", "?")
    title = meta.get("title", "?")

    log(f"\n→ 回填: {course} · {chap} · {title}", "info")
    if args.dry:
        log("  [DRY 模式]", "warn")

    ok, msg = 回填一章(task_path, resp_text, dry=args.dry)
    if ok:
        log(f"  ✓ {msg}", "ok")
        return 0
    log(f"  × {msg}", "err")
    return 1


def cmd_batch(args) -> int:
    """批量：扫 .道喂任务/<课>/_resp/<章>.json，对应回填同名章。"""
    if not _道喂根.exists():
        log(f"× 道喂根不存: {_道喂根}", "err")
        return 1

    pairs: list[tuple[Path, Path]] = []
    for course_dir in sorted(_道喂根.iterdir()):
        if not course_dir.is_dir():
            continue
        if args.课 and not any(kw in course_dir.name for kw in args.课):
            continue
        # 默：响应放 .道喂任务/<课>/_resp/<章>.json，与任务同名
        resp_dir = course_dir / "_resp"
        if not resp_dir.exists():
            log(f"  ⊝ {course_dir.name}: 无 _resp/ 目录", "dim")
            continue
        for resp_file in sorted(resp_dir.glob("*.json")):
            task_file = course_dir / resp_file.name
            if not task_file.exists():
                log(f"  ⚠ {course_dir.name}/{resp_file.name}: 无对应 task", "warn")
                continue
            pairs.append((task_file, resp_file))

    if not pairs:
        log("× 无可回填之对（应放 .道喂任务/<课>/_resp/<章>.json，名同任务）", "warn")
        return 1

    header(f"批量回填 · {len(pairs)} 章", width=58)

    成 = 失 = 0
    for i, (task_path, resp_path) in enumerate(pairs, 1):
        try:
            meta = json.loads(task_path.read_text(encoding="utf-8")).get("task", {})
        except Exception:
            meta = {}
        course = meta.get("course", "?")
        chap = meta.get("chap", "?")
        title = meta.get("title", "?")

        log(f"\n[{i}/{len(pairs)}] {course} · {chap} · {title}", "title")
        log(f"  task: {task_path.relative_to(_REPO)}", "dim")
        log(f"  resp: {resp_path.relative_to(_REPO)}", "dim")

        try:
            resp_text = resp_path.read_text(encoding="utf-8")
            ok, msg = 回填一章(task_path, resp_text, dry=args.dry)
            log(f"  {'✓' if ok else '×'} {msg}", "ok" if ok else "err")
            成 += int(ok)
            失 += int(not ok)
        except Exception as e:
            log(f"  × 异: {e}", "err")
            失 += 1

    header(f"批量回填毕 —— 成 {成} · 败 {失}", width=58)
    if 成 and not args.dry:
        log("  下一步：跑 `python 期末_综合汇编.py` 重生骨架，纳新填要点", "dim")
        log("        或 `python 期末_全图.py` 重生学期总图，更新进度", "dim")
    return 0 if 失 == 0 else 1


def main() -> int:
    p = argparse.ArgumentParser(
        prog="课件_回填",
        description="课件 回填 —— 反者道之动 · 道喂之对偶",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    p.add_argument("task", nargs="?", help="task.json 路径（从道喂导出）")
    p.add_argument("resp", nargs="?", help="LLM 响应 JSON 文件路径（- 或省略则读 stdin）")

    p.add_argument("--batch", action="store_true",
                   help="批量模式：扫 .道喂任务/<课>/_resp/<章>.json")
    p.add_argument("--课", "-c", action="append", default=None,
                   help="批量·课程名关键字（可多次）")
    p.add_argument("--dry", action="store_true", help="干跑：只显示将写入但不真写")

    args = p.parse_args()

    if args.batch:
        return cmd_batch(args)

    if not args.task:
        p.print_help()
        return 1
    return cmd_one(args)


if __name__ == "__main__":
    sys.exit(main())
