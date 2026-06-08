# -*- coding: utf-8 -*-
"""
雨课堂全链路 · 共用之器 (yc_common)

道之共器，万法所宗。
此模块为"PDF→章节聚合→素材汇→综合汇编"全链共用之基石。
"""

from __future__ import annotations

import re
import sys
import json
from pathlib import Path
from typing import Optional, Tuple, Any


# ============================================================
# 一、文件名清洗
# ============================================================

INVALID_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|\r\n\t]')


def sanitize_filename(name: str, max_len: int = 100) -> str:
    """除恶字之于文件名。"""
    if not name:
        return "无名"
    name = INVALID_FILENAME_CHARS.sub("_", str(name)).strip()
    name = re.sub(r"\s+", " ", name).strip(". ")
    return (name or "无名")[:max_len]


# ============================================================
# 二、彩色日志
# ============================================================

_COLORS = {
    "info":  "\033[36m",    # cyan
    "ok":    "\033[32m",    # green
    "warn":  "\033[33m",    # yellow
    "err":   "\033[31m",    # red
    "dim":   "\033[90m",    # gray
    "title": "\033[1;35m",  # bold magenta
}


def log(msg: str, level: str = "info") -> None:
    """彩色之教。"""
    prefix = _COLORS.get(level, "")
    reset = "\033[0m" if prefix else ""
    print(f"{prefix}{msg}{reset}", flush=True)


def header(title: str, char: str = "─", width: int = 64) -> None:
    """标题盒。"""
    log("\n╭" + char * width + "╮", "title")
    log(f"│  {title.ljust(width - 2)}│", "title")
    log("╰" + char * width + "╯", "title")


# ============================================================
# 二·五、Markdown 区段提取（代码块免疫）
# ============================================================

_FENCE_RE = re.compile(r"^[ \t]*(`{3,}|~{3,})", re.MULTILINE)
_H2_STRICT = re.compile(r"^##\s+", re.MULTILINE)


def section_span_fenced(
    text: str,
    heading_re: "re.Pattern[str]",
) -> "tuple[int, int] | None":
    """定位 Markdown 中某 H2 区段 [start, end)，对代码块内的 ## 免疫。

    道法：markmap/mermaid 代码块内含 ## 标题行，朴素 regex 会误判区段边界。
          此函数逐行跟踪代码块开关状态，仅在块外之 ##  才算作区段终点。

    Args:
        text:       完整 Markdown 文本
        heading_re: 定位目标 H2 的正则（如 re.compile(r'^##\\s+思维导图.*?$', ...)）

    Returns:
        (start, end) 左闭右开的字节范围，或 None（未找到目标 H2）。
    """
    m = heading_re.search(text)
    if not m:
        return None

    rest = text[m.end():]
    in_fence = False
    end_offset = len(rest)

    for lm in re.finditer(r"^(.*?)$", rest, re.MULTILINE):
        line = lm.group(1)
        if _FENCE_RE.match(line):
            in_fence = not in_fence
        elif not in_fence and _H2_STRICT.match(line):
            end_offset = lm.start()
            break

    return m.start(), m.end() + end_offset


# ============================================================
# 三、章节信号识别
# ============================================================

# 中文数字 → 阿拉伯数字
_CN_DIGIT = {
    "零": 0, "〇": 0, "○": 0,
    "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
    "六": 6, "七": 7, "八": 8, "九": 9,
}


def cn_to_int(s: str) -> Optional[int]:
    """中文数字字符串 → int。失败返回 None。

    合法格式：
      纯阿拉伯：123
      单字：一-九/十/百
      含十：十一/二十/二十一/...
      含百：一百/一百零八/二百二十一/...
    非法（返 None）："五六"、"一二三" 这类无单位连写
    """
    s = (s or "").strip()
    if not s:
        return None
    if s.isdigit():
        return int(s)
    if s == "十":
        return 10
    if s == "百":
        return 100
    # 含百
    if "百" in s:
        a, _, rest = s.partition("百")
        hundreds = _CN_DIGIT.get(a, 1) * 100
        if not rest or rest == "零":
            return hundreds
        sub = cn_to_int(rest.lstrip("零"))
        if sub is None:
            return None
        if rest.startswith("零") and sub < 10:
            return hundreds + sub
        return hundreds + sub
    # 含十
    if "十" in s:
        a, _, b = s.partition("十")
        if a and a not in _CN_DIGIT:
            return None
        if b and b not in _CN_DIGIT:
            return None
        tens = _CN_DIGIT.get(a, 1) * 10 if a else 10
        ones = _CN_DIGIT.get(b, 0) if b else 0
        return tens + ones
    # 单字
    if len(s) == 1:
        return _CN_DIGIT.get(s)
    # 多字无单位 → 拒（"五六" / "一二三" 都不应识为章节）
    return None


# 章节匹配模式（按优先级排）
_CHAPTER_PATTERNS = [
    # 中文：第X章/篇/单元/部分/讲/编
    (re.compile(r"第\s*([一二三四五六七八九十百零〇○0-9]{1,4})\s*章"), "章"),
    (re.compile(r"第\s*([一二三四五六七八九十百零〇○0-9]{1,4})\s*编"), "编"),
    (re.compile(r"第\s*([一二三四五六七八九十百零〇○0-9]{1,4})\s*篇"), "篇"),
    (re.compile(r"第\s*([一二三四五六七八九十百零〇○0-9]{1,4})\s*单元"), "单元"),
    (re.compile(r"第\s*([一二三四五六七八九十百零〇○0-9]{1,4})\s*部分"), "部分"),
    (re.compile(r"第\s*([一二三四五六七八九十百零〇○0-9]{1,4})\s*讲"), "讲"),
    (re.compile(r"第\s*([一二三四五六七八九十百零〇○0-9]{1,4})\s*节"), "节"),
    # 英文
    (re.compile(r"\bChapter\s*(\d{1,3})\b", re.IGNORECASE), "Chapter"),
    (re.compile(r"\bUnit\s*(\d{1,3})\b", re.IGNORECASE), "Unit"),
    (re.compile(r"\bPart\s*(\d{1,3})\b", re.IGNORECASE), "Part"),
    (re.compile(r"\bLecture\s*(\d{1,3})\b", re.IGNORECASE), "Lecture"),
]


# 绪论 / 总论 / 概论 / 引言 → 第 0 章
_INTRO_KEYWORDS = ("绪论", "总论", "概论", "引言", "导论", "前言", "Introduction")


# 节号·句点格式（次优先：仅当无"章/编/篇..."等显式信号时回落）
# 例："2.环境保护法的基本原则"、"3. 环境利用行为的主体..."、"5. 第N节 ..."
# 严守：开头(允前导空白)、N 取 1-30、点后须接一个非数字字符
_SECTION_DOT_PAT = re.compile(r"^\s*(\d{1,2})\s*[.．、]\s*(?=\D)")


def _try_section_dot(text: str) -> Optional[int]:
    """尝试以句点节号识章号。仅当无显式章信号时调。"""
    if not text:
        return None
    m = _SECTION_DOT_PAT.match(text.lstrip())
    if not m:
        return None
    n = int(m.group(1))
    if 1 <= n <= 30:
        return n
    return None


def detect_chapter(text: str) -> Tuple[Optional[int], Optional[str]]:
    """从文本（多为文件名/标题）中识别**首个**章节信号。

    返回: (章号 int, 原始片段 str) 或 (None, None)。
    "绪论/导论"等返回 (0, "绪论")。
    若无"章/编..."等信号，回落到"N. 标题"之节号识别。
    """
    if not text:
        return None, None

    # 先识别"绪论/导论"——但仅当无显式章号时才优先（绪论可能是"第一章 绪论"）
    has_explicit = any(p.search(text) for p, _ in _CHAPTER_PATTERNS)
    if not has_explicit:
        for kw in _INTRO_KEYWORDS:
            if kw in text:
                return 0, kw

    for pat, kind in _CHAPTER_PATTERNS:
        m = pat.search(text)
        if not m:
            continue
        num_str = m.group(1)
        n = cn_to_int(num_str) if not num_str.isdigit() else int(num_str)
        if n is not None and 0 <= n <= 200:
            return n, m.group(0)

    # 无显式章号但有绪论关键字
    for kw in _INTRO_KEYWORDS:
        if kw in text:
            return 0, kw

    # 末路：句点节号回落
    n = _try_section_dot(text)
    if n is not None:
        m = _SECTION_DOT_PAT.match(text.lstrip())
        raw = m.group(0).strip() if m else f"{n}."
        return n, raw

    return None, None


def detect_all_chapters(text: str) -> list[Tuple[int, str]]:
    """识别文本中**所有**章节信号（去重保序）。

    用于聚合阶段：一节课件可能跨多章（如"第五章...第六章..."）。
    返回 [(章号, 原始片段), ...]
    """
    if not text:
        return []
    found: list[Tuple[int, str]] = []
    seen: set[int] = set()

    # 显式章号
    for pat, _ in _CHAPTER_PATTERNS:
        for m in pat.finditer(text):
            num_str = m.group(1)
            n = cn_to_int(num_str) if not num_str.isdigit() else int(num_str)
            if n is None or not (0 <= n <= 200):
                continue
            if n in seen:
                continue
            seen.add(n)
            found.append((n, m.group(0)))

    # 绪论 —— 仅当完全无显式章号时，方独立成章
    if not seen:
        for kw in _INTRO_KEYWORDS:
            if kw in text:
                found.append((0, kw))
                seen.add(0)
                break

    # 句点节号 —— 末路回落，仅当完全无显式章号时
    if not seen:
        n = _try_section_dot(text)
        if n is not None:
            m = _SECTION_DOT_PAT.match(text.lstrip())
            raw = m.group(0).strip() if m else f"{n}."
            found.append((n, raw))
            seen.add(n)

    found.sort(key=lambda x: x[0])
    return found


# ============================================================
# 四、JSON 读写（UTF-8，缩进，sort 不开以保插序）
# ============================================================

def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


# ============================================================
# 五、雨课堂 PDF 文件名解析
# ============================================================

# 形如 "004-3环境毒理学 第三章-3环境毒理学 第三章.pdf"
#   → seq=4, lesson_title="3环境毒理学 第三章", pres_title="3环境毒理学 第三章"
_PDF_NAME_PAT = re.compile(
    r"^(?P<seq>\d{1,4})[-_](?P<lesson>.+?)[-_](?P<pres>.+)\.pdf$",
    re.IGNORECASE,
)


def parse_pdf_filename(filename: str) -> dict:
    """解析雨课堂下载之 PDF 文件名。

    返回 dict: {seq, lesson_title, presentation_title} 或 {} 若不匹配。
    """
    base = Path(filename).name
    m = _PDF_NAME_PAT.match(base)
    if not m:
        return {"seq": None, "lesson_title": Path(base).stem, "presentation_title": ""}
    return {
        "seq": int(m.group("seq")),
        "lesson_title": m.group("lesson").strip(),
        "presentation_title": m.group("pres").strip(),
    }


# ============================================================
# 六、课程目录解析
# ============================================================

# 形如 "环境毒理学-2026春-090963-001-森巴提·叶尔肯"
def parse_course_dirname(dirname: str) -> dict:
    """解析课程目录名。

    雨课堂归档格式：<课程名>-<学期>-<班级编号>-<教师>
    返回 dict: {course_name, semester, class_code, teacher}
    """
    parts = dirname.split("-")
    if len(parts) >= 4:
        return {
            "course_name": parts[0],
            "semester": parts[1],
            "class_code": "-".join(parts[2:-1]),
            "teacher": parts[-1],
        }
    return {
        "course_name": parts[0] if parts else dirname,
        "semester": "",
        "class_code": "",
        "teacher": parts[-1] if len(parts) > 1 else "",
    }


# ============================================================
# 七、自测
# ============================================================

if __name__ == "__main__":
    log("== 章节·首个识别 ==", "title")
    cases = [
        ("第三章 污染物的生物转运", 3),
        ("3环境毒理学 第三章", 3),
        ("Chapter 5 - Hydraulics", 5),
        ("第十二章 综合规划", 12),
        ("第二十一章 大端", 21),
        ("绪论", 0),
        ("第一章 绪论", 1),  # 显式章号优先于"绪论"关键字
        ("导论与背景", 0),
        ("第五六章习题", None),     # "五六"应被拒
        ("第二编 污染控制法", 2),    # "编"也算
        ("无章节信号文本", None),
        # 节号·句点格式（仅当无章/编时回落）
        ("2.环境保护法的基本原则", 2),
        ("3. 环境利用行为的主体及其权利义务", 3),
        ("5. 环境基本法与综合性环境法律制度", 5),
        ("2.5 不应识为 2", None),  # 点后是数字 → 拒
        ("2.0 同理", None),
        ("第二章 1.基本原则", 2),  # 有显式章号优先于节号
    ]
    ok = 0
    for text, expected in cases:
        n, raw = detect_chapter(text)
        mark = "✓" if n == expected else "✗"
        if n == expected:
            ok += 1
        log(f"  {mark} {text!r:36s} → 第 {n} 章 (期望 {expected}, 匹配 {raw!r})",
            "ok" if n == expected else "err")
    log(f"  {ok}/{len(cases)} 通过", "info")

    log("\n== 章节·全部识别 ==", "title")
    multi_cases = [
        "第五章 环境毒理学常用实验方法 → 第六章环境化学物的安全性",
        "第五六章习题",
        "第三章 污染物的生物转运",
    ]
    for c in multi_cases:
        chs = detect_all_chapters(c)
        log(f"  {c!r:50s} → {chs}", "info")

    log("\n== 文件名解析 ==", "title")
    for n in [
        "004-3环境毒理学 第三章-3环境毒理学 第三章.pdf",
        "001-青春逐梦，共赴改革新征程-青春逐梦，共赴改革新征程.pdf",
    ]:
        log(f"  {n} → {parse_pdf_filename(n)}", "info")

    log("\n== 课程目录解析 ==", "title")
    log(f"  {parse_course_dirname('环境毒理学-2026春-090963-001-森巴提·叶尔肯')}", "info")
