# -*- coding: utf-8 -*-
"""复习站 · 清单生成器（道法自然·加法不破底层）

为某一门课扫描其解析成果，生成一份 JSON 清单，供 index.html 单页阅览站按需加载。
不改任何底层器；纯读文件、出清单。

用法：
    python 复习站_构建.py 流体力学
    python 复习站_构建.py            # 不带参数 → 扫描全部课程

产物：
    site_data/<课程>.json    # 单课清单
    site_data/_courses.json  # 课程索引（供站点首页列出所有课程）
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE_DATA = ROOT / "site_data"

# 课程目录之共同标志：含 02_解析成果
_PARSE_DIR = "02_解析成果"


def _rel(p: Path) -> str:
    """相对仓库根之 POSIX 路径（供网页 fetch）。"""
    return p.relative_to(ROOT).as_posix()


def _chapter_key(name: str) -> tuple:
    m = re.search(r"_第(\d+)章", name)
    return (int(m.group(1)) if m else 999, name)


def _lecture_key(name: str) -> tuple:
    m = re.match(r"\s*(\d+)", name)
    return (int(m.group(1)) if m else 999, name)


def _lecture_title(dirname: str) -> str:
    """讲次目录名形如 `001-开学第一课-XXX`，取末段为题，前缀序号保留。"""
    parts = dirname.split("-", 1)
    seq = parts[0].strip()
    rest = parts[1] if len(parts) > 1 else dirname
    # 末段常重复，取 `-` 后最末一段去重
    tail = rest.split("-")[-1].strip()
    return f"{seq} · {tail}"


def build_course(course_dir: Path) -> dict | None:
    parse = course_dir / _PARSE_DIR
    if not parse.is_dir():
        return None

    material = parse / "_素材"
    learn = parse / "_学习系统"

    groups: list[dict] = []

    # 一 · 临考总览
    overview = []
    for fname, label in [
        ("_最终复习资料.md", "期末复习全集（整合一炉·首选）"),
        ("_综合复习资料.md", "综合复习资料（图文溯源全本）"),
        ("_期末速查.md", "期末速查（考前一张表）"),
        ("_期末骨架.md", "期末骨架（知识结构）"),
    ]:
        f = material / fname
        if f.exists():
            overview.append({"label": label, "path": _rel(f)})
    bg = learn / "00_备考总纲.md"
    if bg.exists():
        overview.insert(1, {"label": "备考总纲（节律与路径）", "path": _rel(bg)})
    if overview:
        groups.append({"title": "临考总览", "items": overview})

    # 二 · 分章精要（要点 + 思维导图）
    chapters = []
    if material.exists():
        chs = sorted(
            (p for p in material.iterdir() if re.match(r"_第\d+章", p.name)),
            key=lambda p: _chapter_key(p.name),
        )
        for p in chs:
            label = p.stem.lstrip("_")
            chapters.append({"label": label, "path": _rel(p)})
    if chapters:
        groups.append({"title": "分章精要（要点 + 思维导图）", "items": chapters})

    # 三 · 自测与练习
    practice = []
    for base, fname, label in [
        (learn, "自测题库.md", "自测题库（闭卷·提取练习）"),
        (learn, "速记卡.md", "速记卡（间隔重复·填空）"),
        (material, "_期末模拟卷.md", "期末模拟卷（限时·闭卷）"),
    ]:
        f = base / fname
        if f.exists():
            practice.append({"label": label, "path": _rel(f)})
    if practice:
        groups.append({"title": "自测与练习", "items": practice})

    # 四 · 原始讲义（OCR 全文，溯底层）
    lectures = []
    lec_dirs = sorted(
        (p for p in parse.iterdir() if p.is_dir() and re.match(r"\s*\d", p.name)),
        key=lambda p: _lecture_key(p.name),
    )
    for d in lec_dirs:
        full = d / "_全文.md"
        if full.exists():
            lectures.append({"label": _lecture_title(d.name), "path": _rel(full)})
    if lectures:
        groups.append({"title": "原始讲义（OCR 全文）", "items": lectures})

    # 元信息：教师/学期（自 _course.json）
    teacher = semester = ""
    cj = parse / "_course.json"
    if cj.exists():
        try:
            meta = json.loads(cj.read_text(encoding="utf-8"))
            teacher = meta.get("teacher", "") or meta.get("教师", "")
            semester = meta.get("semester", "") or meta.get("学期", "")
        except Exception:
            pass

    total_items = sum(len(g["items"]) for g in groups)
    return {
        "course": course_dir.name,
        "teacher": teacher,
        "semester": semester,
        "groups": groups,
        "count": total_items,
    }


def discover_courses() -> list[Path]:
    out = []
    for p in sorted(ROOT.iterdir()):
        if p.is_dir() and (p / _PARSE_DIR).is_dir():
            out.append(p)
    return out


def main(argv: list[str]) -> int:
    SITE_DATA.mkdir(exist_ok=True)
    if len(argv) > 1:
        targets = [ROOT / argv[1]]
    else:
        targets = discover_courses()

    index = []
    for course_dir in targets:
        data = build_course(course_dir)
        if not data:
            print(f"[skip] {course_dir.name}: 无 {_PARSE_DIR}")
            continue
        out = SITE_DATA / f"{course_dir.name}.json"
        out.write_text(
            json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print(f"[ok] {course_dir.name}: {data['count']} 篇 → {_rel(out)}")
        index.append(
            {
                "course": data["course"],
                "teacher": data["teacher"],
                "count": data["count"],
            }
        )

    # 若扫描了全部课程，更新课程索引
    if len(argv) <= 1:
        (SITE_DATA / "_courses.json").write_text(
            json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print(f"[ok] 课程索引 → site_data/_courses.json（{len(index)} 门）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
