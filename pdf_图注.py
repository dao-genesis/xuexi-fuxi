# -*- coding: utf-8 -*-
"""
PDF 图注 (pdf_annotate)  ——  每图匹配其核心内容

道法自然：
    万物负阴而抱阳，中气以为和。
    图为阴（形），文为阳（义），图注者中气也——使图文相合。
    
    此关之事：为每页图片标注核心内容，分类整理，
    使复习时可直接按类型/关键词定位原图并插入。

道法三层：
    一、自动标注（OCR 文本 + 启发式规则）—— 快，覆盖全
    二、LLM 视觉标注（可选）—— 准，识图表/流程图等 OCR 难判者
    三、人工修正 —— 精，用户可覆写任何标注

输出：
    解析仓库/<课程>/<PDF>/_图注.json          # 每 PDF 之页级标注
    解析仓库/<课程>/_图注索引.json              # 课程级索引（可查询）
    解析仓库/<课程>/_素材/_图注索引.md           # 人读版·按章按类整理

用法：
    python pdf_图注.py                          # 全部自动标注
    python pdf_图注.py -f 环境毒理              # 仅某课
    python pdf_图注.py --export-llm             # 导出 LLM 视觉标注任务
    python pdf_图注.py --writeback-llm          # 回写 LLM 标注结果
    python pdf_图注.py --query "LD50"           # 查询含此关键词之图片
    python pdf_图注.py --gen-md                 # 生成人读图注索引
    python pdf_图注.py --force                  # 强制重标
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# 共用之器
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _yc_common import (  # noqa: E402
    log,
    header,
    read_json,
    write_json,
    parse_course_dirname,
    sanitize_filename,
    section_span_fenced,
)


# ============================================================
# 内容类型定义
# ============================================================

class ContentType:
    """页面内容类型枚举"""
    TITLE = "title"           # 章节标题页
    DEFINITION = "definition" # 概念定义
    FORMULA = "formula"       # 公式/模型
    TABLE = "table"           # 表格/对比
    FLOWCHART = "flowchart"   # 流程图/框架图
    EXAMPLE = "example"       # 例题/案例
    SUMMARY = "summary"       # 小结/要点
    LIST = "list"             # 列表/分类列举
    IMAGE = "image"           # 纯图（照片/示意图）
    MIXED = "mixed"           # 混合内容
    OTHER = "other"           # 其他/未判
    BLANK = "blank"           # 空白/封面/目录

    # 人读标签
    LABELS = {
        "title": "📌 标题页",
        "definition": "📖 概念定义",
        "formula": "📐 公式模型",
        "table": "📊 表格对比",
        "flowchart": "🔄 流程框架",
        "example": "💡 例题案例",
        "summary": "📝 小结要点",
        "list": "📋 列表分类",
        "image": "🖼️ 示意图",
        "mixed": "🔀 混合内容",
        "other": "❓ 其他",
        "blank": "⬜ 空白/封面",
    }

    # 查询优先级（复习时最关注的排前）
    PRIORITY = [
        "formula", "definition", "table", "flowchart",
        "example", "summary", "list", "mixed", "image",
        "title", "other", "blank",
    ]


# ============================================================
# 水印/碎片过滤已统一至 _ocr_clean.py
# OCR 源数据在写入 _doc.json 时已清洗，此处不再重复
# ============================================================


# ============================================================
# 自动标注·启发式规则
# ============================================================

# 定义类关键词
_DEF_PATTERNS = [
    r"是指", r"定义为?", r"称之为", r"指的是", r"所谓\s*\S+\s*是指",
    r"是指[：:]?\s*", r"即\s", r"——\s*",
    r"定义[：:]", r"概念[：:]", r"含义[：:]",
    r"^\S+[：:]\s",  # "术语：解释" 格式
]

# 公式类关键词/模式
_FORMULA_PATTERNS = [
    r"[=≈≠≤≥<>]\s*[A-Za-zα-ωΑ-Ω]",  # = 后跟变量
    r"[A-Za-z]\s*[=≈]\s*[A-Za-z\d]",  # 变量 = 表达式
    r"公式", r"方程", r"计算式", r"模型[：:]",
    r"[A-Za-zα-ω]\s*[=]\s*\(",  # f(x) = ...
    r"LD\d{2}", r"LC\d{2}", r"EC\d{2}",  # 毒理学指标
    r"[A-Z]\s*=\s*",  # 大写变量赋值
    r"[α-ω]\s*[=≈]",  # 希腊字母赋值
    r"\d+\s*[×÷\*\/]\s*\d+",  # 数值运算
]

# 表格类关键词/模式
_TABLE_PATTERNS = [
    r"比较[：:]", r"对比[：:]", r"区别[：:]", r"异同",
    r"分类[：:]", r"类型[：:]", r"特点[：:]",
    r"VS\.?", r"vs\.?",
    r"\|.*\|.*\|",  # markdown 表格行
]

# 流程图类关键词
_FLOW_PATTERNS = [
    r"流程", r"步骤[：:]", r"程序[：:]", r"路线",
    r"首先.*然后.*最后", r"第一步",
    r"→", r"⇒", r"⟶",
]

# 例题/案例类
_EXAMPLE_PATTERNS = [
    r"例[题\d]", r"案例", r"例如[：:]", r"举例",
    r"实例", r"应用[：:]", r"计算[：:]", r"求解",
]

# 小结类
_SUMMARY_PATTERNS = [
    r"小结", r"总结", r"要点", r"归纳",
    r"复习[要重]点", r"关键[要重]点",
    r"本章[要重]点",
]

# 列表类
_LIST_PATTERNS = [
    r"^\s*[①②③④⑤⑥⑦⑧⑨⑩]",  # 圈号
    r"^\s*[\d][\.\)、]\s+\S",   # 数字列表
    r"^\s*[（(]\s*\d+\s*[）)]",  # 括号数字
    r"包括[：:]", r"分为[：:]", r"包含[：:]",
]

# 标题类
_TITLE_PATTERNS = [
    r"^第[一二三四五六七八九十百]+章",
    r"^第\s*\d+\s*章",
    r"^Chapter\s*\d+",
    r"^目录$", r"^Contents$",
]

# 空白/封面
_BLANK_PATTERNS = [
    r"^谢谢", r"^Thank\s*you", r"^Q\s*&\s*A",
    r"^Questions?\s*$",
]


def _count_pattern_hits(text: str, patterns: list[str]) -> int:
    """统计文本命中某类模式之次数。"""
    hits = 0
    for pat in patterns:
        hits += len(re.findall(pat, text, re.MULTILINE | re.IGNORECASE))
    return hits


def classify_page(ocr_text: str | None, embedded_text: str | None = None) -> dict:
    """启发式分类一页内容。

    道法：OCR 源数据已由 _ocr_clean.py 清洗，此处不再重复。
    返回:...
    """
    text = (ocr_text or embedded_text or "").strip()

    if not text or len(text) < 3:
        return {
            "content_type": ContentType.BLANK,
            "confidence": 0.9,
            "core_topic": "",
            "keywords": [],
            "scores": {},
        }

    # 各类型打分
    scores = {
        ContentType.TITLE: _count_pattern_hits(text, _TITLE_PATTERNS) * 3,
        ContentType.DEFINITION: _count_pattern_hits(text, _DEF_PATTERNS) * 2,
        ContentType.FORMULA: _count_pattern_hits(text, _FORMULA_PATTERNS) * 2,
        ContentType.TABLE: _count_pattern_hits(text, _TABLE_PATTERNS) * 2,
        ContentType.FLOWCHART: _count_pattern_hits(text, _FLOW_PATTERNS) * 2,
        ContentType.EXAMPLE: _count_pattern_hits(text, _EXAMPLE_PATTERNS) * 2,
        ContentType.SUMMARY: _count_pattern_hits(text, _SUMMARY_PATTERNS) * 3,
        ContentType.LIST: _count_pattern_hits(text, _LIST_PATTERNS),
    }

    # ── 额外线索（课件结构特征）──
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    n_lines = len(lines)
    text_len = len(text)

    # 短文本 + 标题模式 → 很可能是标题页
    if n_lines <= 3 and scores[ContentType.TITLE] > 0:
        scores[ContentType.TITLE] += 10

    # 极短文本（≤2行≤20字）→ 标题或封面
    if n_lines <= 2 and text_len <= 30:
        scores[ContentType.TITLE] += 5

    # 长文本 + 多行 → 可能是混合
    if n_lines > 15:
        scores[ContentType.MIXED] = max(scores.values()) * 0.5

    # 含等号 + 含数字 → 公式倾向加分
    if "=" in text and re.search(r"\d+\.?\d*", text):
        scores[ContentType.FORMULA] += 1

    # 含冒号定义格式 + 短行 → 定义倾向
    if n_lines <= 8 and re.search(r"[：:]", text):
        scores[ContentType.DEFINITION] += 1

    # ── 课件常见模式（降低 other 比例）──
    # 节标题行（如 "1.1环境毒理学及其发展"）→ 定义/标题
    if re.match(r"^\d+\.\d+", lines[0] if lines else ""):
        # 节标题 + 正文 → 定义类
        if n_lines > 2:
            scores[ContentType.DEFINITION] += 2
        else:
            scores[ContentType.TITLE] += 2

    # 含「是指/称为/定义」→ 定义加分
    if re.search(r"是指|称为|定义为|称之为|指的是", text):
        scores[ContentType.DEFINITION] += 3

    # 含分类/包括/分为 → 列表加分
    if re.search(r"包括|分为|分类如下|有以下", text):
        scores[ContentType.LIST] += 2

    # 含数字+单位 → 公式/定义加分
    if re.search(r"\d+\.?\d*\s*(mg|kg|μg|ppm|ppb|%|mL|L|mmol|μmol)", text, re.I):
        scores[ContentType.FORMULA] += 2

    # 含实验/试验/方法 → 例题/流程加分
    if re.search(r"试验|实验|方法[：:]|步骤", text):
        scores[ContentType.EXAMPLE] += 2
        scores[ContentType.FLOWCHART] += 1

    # 含图/表引用 → 表格/流程加分
    if re.search(r"图\s*\d|表\s*\d|Fig\.?\s*\d|Tab\.?\s*\d", text, re.I):
        scores[ContentType.TABLE] += 2

    # 多行且无明显特征 → 定义（课件主体多为概念解释）
    if not any(v > 0 for v in scores.values()) and n_lines >= 3 and text_len >= 20:
        scores[ContentType.DEFINITION] = 1

    # 取最高分类型
    if not any(v > 0 for v in scores.values()):
        best_type = ContentType.OTHER
        confidence = 0.3
    else:
        best_type = max(scores, key=scores.get)
        total = sum(v for v in scores.values() if v > 0)
        confidence = min(1.0, scores[best_type] / max(total, 1))

    # 若最高分与次高分接近 → 混合
    sorted_scores = sorted(scores.values(), reverse=True)
    if len(sorted_scores) >= 2 and sorted_scores[0] > 0:
        ratio = sorted_scores[1] / sorted_scores[0] if sorted_scores[0] else 0
        if ratio > 0.7 and best_type not in (ContentType.TITLE, ContentType.BLANK):
            best_type = ContentType.MIXED
            confidence *= 0.8

    # 提取核心主题
    core_topic = _extract_core_topic(text, best_type)

    # 碎片主题检测 → 降级为blank
    if _is_garbled_topic(core_topic):
        core_topic = ""

    # 极短主题（≤3字）扩展为更完整描述
    if core_topic and len(core_topic) <= 3:
        core_topic = _expand_short_topic(core_topic, text)

    # 清理尾标点（，、。；：！？）
    if core_topic:
        core_topic = re.sub(r"[，、。；：！？\"」」]+$", "", core_topic).strip()

    # 提取关键词
    # 先将换行替换为空格，避免关键词中包含换行符
    keywords = _extract_keywords(text.replace("\n", " "))

    return {
        "content_type": best_type,
        "confidence": round(confidence, 2),
        "core_topic": core_topic,
        "keywords": keywords[:8],
        "scores": {k: v for k, v in scores.items() if v > 0},
    }


def _extract_core_topic(text: str, content_type: str) -> str:
    """从文本中提取核心主题。

    道法：
        不取首行（首行常为章节号如"1.1环境毒理学及其发展"），
        而是智能提取——优先提取定义术语、节标题核心词、冒号前概念。
        极短主题（≤3字）自动扩展为更完整的描述。
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return ""

    # ── 1. 定义类：取"XX是指"中的XX ──
    m = re.search(r"^([\u4e00-\u9fffA-Za-z\d]+)\s*(?:是指|定义为?|称之为|指的是)", text, re.MULTILINE)
    if m and len(m.group(1)) >= 2:
        return m.group(1)

    # ── 2. 冒号格式：取冒号前（但跳过章节号） ──
    for line in lines:
        # 跳过纯章节号行（如 "1.1环境毒理学及其发展"）
        if re.match(r"^\d+\.\d+", line):
            # 提取章节号后的标题部分
            m = re.match(r"^\d+(?:\.\d+)+\s*(.*)", line)
            if m and m.group(1).strip():
                return m.group(1).strip()[:60]
            continue
        m = re.search(r"^([\u4e00-\u9fffA-Za-z\d\s]{2,20})[：:]", line)
        if m:
            return m.group(1).strip()

    # ── 3. 公式类：取等号前变量名 ──
    if content_type == ContentType.FORMULA:
        m = re.search(r"([A-Za-zα-ωΑ-Ω\d\s]{2,30})\s*[=≈]", text)
        if m:
            return m.group(1).strip()

    # ── 4. 标题页：取首行 ──
    if content_type == ContentType.TITLE:
        return lines[0][:60]

    # ── 5. 兜底：取第一个非章节号行 ──
    for line in lines:
        # 跳过章节号行
        if re.match(r"^\d+\.\d+", line):
            continue
        # 跳过极短行
        if len(line) < 3:
            continue
        return line[:60]

    # 全部是章节号行 → 取首行
    return lines[0][:60]


def _expand_short_topic(topic: str, text: str) -> str:
    """极短core_topic（≤3字）扩展为更完整描述。

    道法：
        极短主题如"吸收"、"分布"、"概述"缺乏区分度，
        从OCR文本中寻找包含该主题的更完整表述。
    """
    if not topic or len(topic) > 3:
        return topic

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # 策略1：章节号行中含此主题 → 取完整章节标题
    for line in lines:
        m = re.match(r"^(\d+(?:\.\d+)+\s*.{" + str(len(topic)) + r"," + str(len(topic) + 20) + r"}" + re.escape(topic) + r")", line)
        if m:
            return m.group(1).strip()[:60]

    # 策略2：含此主题的较长行 → 取主题+上下文
    for i, line in enumerate(lines):
        if topic in line and len(line) > len(topic):
            # 冒号行：取冒号后内容补充
            m_colon = re.search(re.escape(topic) + r"\s*[：:]\s*(.{1,30})", line)
            if m_colon and m_colon.group(1).strip():
                return f"{topic}：{m_colon.group(1).strip()}"[:60]
            # 冒号在行尾（如"例子："）→ 取下一行补充
            if re.search(re.escape(topic) + r"\s*[：:]\s*$", line):
                if i + 1 < len(lines):
                    next_l = lines[i + 1].strip()
                    if len(next_l) > 2:
                        return f"{topic}：{next_l[:25]}"[:60]
            # 一般行：截取主题前后上下文
            idx = line.find(topic)
            start = max(0, idx - 4)
            end = min(len(line), idx + len(topic) + 8)
            expanded = line[start:end].strip()
            if len(expanded) > 3:
                return expanded[:60]

    # 策略3：取下一行补充
    for i, line in enumerate(lines):
        if line.strip() == topic and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if len(next_line) > 3:
                return f"{topic}·{next_line[:20]}"[:60]

    return topic


def _is_garbled_topic(topic: str) -> bool:
    """判断 core_topic 是否为OCR碎片/乱码。"""
    if not topic:
        return True
    from _ocr_clean import is_ocr_fragment
    if is_ocr_fragment(topic):
        return True
    # 纯数字+符号
    if re.match(r"^[\d,.\-~+/\\]+$", topic):
        return True
    # 含URL碎片
    if re.search(r"\.click|search-card|\.all|\.com|\.cn", topic, re.I):
        return True
    return False


def _extract_keywords(text: str) -> list[str]:
    """从文本中提取关键词（中文为主）。

    道法：
        OCR 碎片（source/from/ptag等）已在源头清洗，
        此处额外过滤无意义短词，保留学科术语。
    """
    from _ocr_clean import is_ocr_fragment

    # 去除常见停用词
    stopwords = {
        "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
        "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
        "你", "会", "着", "没有", "看", "好", "自己", "这", "他",
        "之", "与", "及", "或", "等", "可", "为", "中", "其", "从",
        "而", "但", "如", "将", "对", "于", "被", "把", "让",
        "那", "些", "则", "所", "以", "此", "该", "每", "各",
        "可以", "已经", "因为", "所以", "如果", "虽然", "但是",
        "不仅", "而且", "或者", "以及", "还是", "就是", "只是",
        "那么", "这样", "那样", "这些", "那些", "什么", "怎么",
        "如何", "为什么", "由于", "通过", "进行", "使用", "利用",
        "根据", "按照", "关于", "对于", "其中", "之间", "之后",
        "之前", "以上", "以下", "以内", "以外", "左右", "前后",
    }

    # 提取中文关键词
    # 道法：不用滑动窗口（产生无意义子串），而是基于结构提取
    # 1. 逗号/句号/冒号/顿号分隔的短语
    # 2. "的"字分隔的前后修饰词
    # 3. 高频2-4字片段

    # 按标点分割为短语
    phrases = re.split(r"[，。、；：！？,.;:!?]\s*", text)
    # 去除停用词和过短短语
    phrases = [p.strip() for p in phrases if p.strip() and len(p.strip()) >= 2]

    # 从短语中提取核心名词（"的"字前后）
    noun_candidates: list[str] = []
    for ph in phrases:
        # "XX的YY" → 取YY
        parts = re.split(r"的", ph)
        for part in parts:
            part = part.strip()
            if len(part) >= 2 and part not in stopwords:
                noun_candidates.append(part)

    # 词频统计
    noun_freq = Counter(noun_candidates)

    # 优先4字以上术语（截断≤12字）
    keywords = []
    for w, cnt in noun_freq.most_common(30):
        if w in stopwords:
            continue
        # 过滤纯数字+符号碎片（如 "00 2", "10,00"）
        if re.match(r"^[\d,.\-~+/\\ ]+$", w):
            continue
        # 过滤数字+单位（如 "25Kg", "30NM"）
        if re.match(r"^\d+[A-Za-z]+$", w):
            continue
        w = w[:12]  # 截断过长短语
        if len(w) >= 4:
            keywords.append(w)
        elif cnt >= 2 and len(w) >= 2:
            keywords.append(w)
        if len(keywords) >= 8:
            break

    # 补充：从文本中提取高频2-4字中文片段（去重）
    if len(keywords) < 4:
        cn_chunks = re.findall(r"[\u4e00-\u9fff]{2,4}", text)
        chunk_freq = Counter(cn_chunks)
        for w, cnt in chunk_freq.most_common(20):
            if w in stopwords or cnt < 2:
                continue
            if w not in keywords:
                keywords.append(w)
            if len(keywords) >= 8:
                break

    # 提取英文术语（2+字母，过滤碎片）
    # 常见化学单位/符号（不应作为关键词）
    _CHEM_SYMBOLS = frozenset({
        "mg", "kg", "g", "ml", "l", "mm", "cm", "nm", "MN", "OH",
        "cd", "pb", "hg", "as", "cr", "zn", "cu", "fe", "mn",
        "pa", "kb", "mb", "gb", "ppm", "ppb",
    })
    en_raw = re.findall(r"[A-Za-z][A-Za-z\d]{1,}(?:\s+[A-Za-z]+){0,2}", text)
    for w in en_raw[:8]:
        # 过滤 OCR 碎片
        if is_ocr_fragment(w):
            continue
        # 过滤纯数字+符号表达式（如 "2n+2", "10,00"）
        if re.match(r"^[\d,.\-~+/\\]+$", w):
            continue
        # 过滤数字+单位（如 "25Kg", "30NM"）
        if re.match(r"^\d+[A-Za-z]+$", w):
            continue
        # 过滤极短英文词（≤2字母）和化学单位符号
        if len(w) <= 2 or w.upper() in _CHEM_SYMBOLS:
            continue
        if w.upper() not in [k.upper() for k in keywords]:
            keywords.append(w)

    return keywords


# ============================================================
# 单 PDF 标注
# ============================================================

def annotate_pdf(doc_dir: Path, *, force: bool = False) -> dict | None:
    """为一 PDF 解析目录生成 _图注.json。

    道法：
        1. 读 _doc.json 取每页之 OCR 文字
        2. 启发式分类每页内容类型
        3. 合并已有 LLM/人工标注（不覆盖）
        4. 写 _图注.json
    """
    meta_path = doc_dir / "_doc.json"
    annot_path = doc_dir / "_图注.json"

    meta = read_json(meta_path)
    if not meta or not meta.get("pages"):
        return None

    # 增量：已有图注且未强制 → 保留
    old_annot = read_json(annot_path) if annot_path.exists() else None

    pages = meta.get("pages", [])
    annotations: list[dict] = []

    # 构建旧标注索引（page → annotation）
    old_by_page = {}
    if old_annot and not force:
        for a in old_annot.get("annotations", []):
            old_by_page[a.get("page", -1)] = a

    for p in pages:
        idx = p.get("index", 0)
        img = p.get("image", "")
        ocr_text = p.get("ocr_text")
        embedded_text = p.get("embedded_text")
        figures = p.get("figures") or []

        # 检查旧标注中是否有 LLM/人工覆写
        old_a = old_by_page.get(idx)
        if old_a and not force:
            # 保留人工/LLM 标注
            if old_a.get("source") in ("llm", "manual"):
                annotations.append(old_a)
                continue
            # 保留已有且 OCR 未变之自动标注
            if old_a.get("ocr_hash") == _text_hash(ocr_text):
                annotations.append(old_a)
                continue

        # 自动标注
        cls = classify_page(ocr_text, embedded_text)

        annot = {
            "page": idx,
            "image": img,
            "content_type": cls["content_type"],
            "confidence": cls["confidence"],
            "core_topic": cls["core_topic"],
            "keywords": cls["keywords"],
            "ocr_hash": _text_hash(ocr_text),
            "source": "auto",
            "manual_note": None,
        }

        # 子图标注
        if figures:
            annot["figures"] = [
                {
                    "image": f.get("image", ""),
                    "w": f.get("w", 0),
                    "h": f.get("h", 0),
                    "content_type": ContentType.IMAGE,  # 子图默认为图
                    "core_topic": "",
                    "source": "auto",
                }
                for f in figures
            ]

        # OCR 文字摘要（前 200 字，方便查阅）
        text_summary = (ocr_text or embedded_text or "").strip()[:200]
        if text_summary:
            annot["text_summary"] = text_summary

        annotations.append(annot)

    result = {
        "pdf_name": meta.get("pdf_name", ""),
        "lesson_seq": meta.get("lesson_seq"),
        "lesson_title": meta.get("lesson_title", ""),
        "presentation_title": meta.get("presentation_title", ""),
        "chapter_num": meta.get("chapter_num"),
        "page_count": len(pages),
        "annotations": annotations,
    }

    write_json(annot_path, result)
    return result


def _text_hash(text: str | None) -> str:
    """文本简略哈希（用于增量判断 OCR 是否变化）。"""
    if not text:
        return ""
    return str(len(text)) + ":" + (text[:20].replace("\n", " "))


# ============================================================
# 课程级标注
# ============================================================

def annotate_course(course_dir: Path, *, force: bool = False) -> dict | None:
    """为一门课程下所有 PDF 生成图注，并建课程级索引。"""
    # 扫描所有 _doc.json 目录
    doc_dirs = sorted(
        d for d in course_dir.iterdir()
        if d.is_dir() and (d / "_doc.json").exists()
    )
    if not doc_dirs:
        return None

    all_annotations: list[dict] = []
    stats = {"total_pages": 0, "annotated": 0, "skipped": 0}

    for d in doc_dirs:
        annot = annotate_pdf(d, force=force)
        if annot:
            n = len(annot.get("annotations", []))
            stats["total_pages"] += annot.get("page_count", 0)
            stats["annotated"] += n

            # 过滤非课程PDF（无章节号且PDF名不含课程关键字）
            ch_num = annot.get("chapter_num")
            pdf_name = annot.get("pdf_name", "")
            if not ch_num and not any(kw in pdf_name for kw in ["章", "Chapter", "环境毒理"]):
                stats["skipped"] += 1
                continue

            # 汇入课程索引
            rel_dir = d.name
            for a in annot.get("annotations", []):
                all_annotations.append({
                    **a,
                    "rel_dir": rel_dir,
                    "pdf_name": annot.get("pdf_name", ""),
                    "lesson_seq": annot.get("lesson_seq"),
                    "chapter_num": annot.get("chapter_num"),
                })
        else:
            stats["skipped"] += 1

    # 课程级索引
    index = {
        "course_dir": course_dir.name,
        "stats": stats,
        "type_distribution": _type_distribution(all_annotations),
        "annotations": all_annotations,
    }

    write_json(course_dir / "_图注索引.json", index)
    return index


def _type_distribution(annotations: list[dict]) -> dict[str, int]:
    """统计各内容类型之页数。"""
    dist: dict[str, int] = Counter(
        a.get("content_type", ContentType.OTHER) for a in annotations
    )
    return dict(dist)


# ============================================================
# 图注索引 → 人读 Markdown
# ============================================================

def generate_图注_md(course_dir: Path) -> str | None:
    """生成课程级图注索引 Markdown（按章按类整理）。

    道法：
        按章分组，每章内按内容类型排序，
        每条含：页码、核心主题、关键词、图片链接。
        复习时可直接定位并插入原图。
    """
    index_path = course_dir / "_图注索引.json"
    chart_path = course_dir / "_章节图谱.json"

    index = read_json(index_path)
    if not index or not index.get("annotations"):
        return None

    chart = read_json(chart_path) if chart_path.exists() else {}
    course_name = chart.get("course_name", course_dir.name)
    teacher = chart.get("teacher", "")
    semester = chart.get("semester", "")

    annotations = index["annotations"]

    # 按章节分组
    by_chapter: dict[int, list[dict]] = defaultdict(list)
    no_chapter: list[dict] = []
    for a in annotations:
        ch = a.get("chapter_num")
        if ch is not None:
            by_chapter[ch].append(a)
        else:
            no_chapter.append(a)

    lines: list[str] = []
    lines.append(f"# {course_name} · 图注索引")
    lines.append("")
    lines.append(f"> 教师: {teacher} · 学期: {semester}")
    lines.append(f"> 共 {len(annotations)} 页图片已标注")
    lines.append("")

    # 类型分布总览
    dist = index.get("type_distribution", {})
    lines.append("## 内容类型分布")
    lines.append("")
    lines.append("| 类型 | 页数 | 占比 |")
    lines.append("| ---- | ---: | ---: |")
    total = sum(dist.values()) or 1
    for t in ContentType.PRIORITY:
        n = dist.get(t, 0)
        if n > 0:
            label = ContentType.LABELS.get(t, t)
            pct = f"{n / total * 100:.0f}%"
            lines.append(f"| {label} | {n} | {pct} |")
    lines.append("")

    # 按章详细
    chapters = chart.get("chapters", [])
    chapter_titles = {ch["chapter_num"]: ch.get("chapter_title", "") for ch in chapters}

    for ch_num in sorted(by_chapter.keys()):
        ch_label = "绪论 · 第 0 章" if ch_num == 0 else f"第 {ch_num} 章"
        ch_title = chapter_titles.get(ch_num, "")
        ch_annots = by_chapter[ch_num]

        lines.append(f"## {ch_label}" + (f" · {ch_title}" if ch_title else ""))
        lines.append("")

        # 按类型分组
        by_type: dict[str, list[dict]] = defaultdict(list)
        for a in ch_annots:
            by_type[a.get("content_type", ContentType.OTHER)].append(a)

        for t in ContentType.PRIORITY:
            type_annots = by_type.get(t, [])
            if not type_annots:
                continue

            label = ContentType.LABELS.get(t, t)
            lines.append(f"### {label}")
            lines.append("")
            lines.append("| 页 | 核心内容 | 关键词 | 图片 |")
            lines.append("| --: | -------- | ------ | ---- |")

            for a in sorted(type_annots, key=lambda x: x.get("page", 0)):
                pg = a.get("page", 0)
                topic = a.get("core_topic", "") or "—"
                kws = "、".join(a.get("keywords", [])[:4]) or "—"
                rel = a.get("rel_dir", "")
                img = a.get("image", "")
                img_link = f"![p{pg:03d}](../{rel}/{img})" if rel and img else "—"
                # 用缩略图标记代替完整嵌入（避免 md 过大）
                thumb = f"[📷p{pg:03d}](../{rel}/{img})" if rel and img else "—"
                lines.append(f"| {pg} | {topic} | {kws} | {thumb} |")

            lines.append("")

        # 子图汇总（若有）
        all_figs = []
        for a in ch_annots:
            for fig in (a.get("figures") or []):
                all_figs.append({**fig, "page": a.get("page", 0), "rel_dir": a.get("rel_dir", "")})
        if all_figs:
            lines.append(f"### 🖼️ 嵌入子图（{len(all_figs)} 张）")
            lines.append("")
            lines.append("| 来源页 | 子图 | 尺寸 | 链接 |")
            lines.append("| ------ | ---- | ---- | ---- |")
            for fig in all_figs:
                pg = fig.get("page", 0)
                fname = fig.get("image", "")
                w, h = fig.get("w", 0), fig.get("h", 0)
                size_str = f"{w}×{h}" if w and h else "—"
                rel = fig.get("rel_dir", "")
                link = f"[📷](../{rel}/{fname})" if rel and fname else "—"
                lines.append(f"| p{pg:03d} | {fname} | {size_str} | {link} |")
            lines.append("")

    # 未归类
    if no_chapter:
        lines.append("## 未归类课件")
        lines.append("")
        for a in no_chapter:
            pg = a.get("page", 0)
            topic = a.get("core_topic", "") or "—"
            t = a.get("content_type", "other")
            label = ContentType.LABELS.get(t, t)
            rel = a.get("rel_dir", "")
            img = a.get("image", "")
            lines.append(f"- {label} · p{pg:03d} · {topic} · [📷](../{rel}/{img})")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("> 图注由自动启发式规则生成，可运行 `--export-llm` 导出 LLM 视觉标注任务以提升准确度。")
    lines.append("> 人工修正：直接编辑 `_图注.json` 中对应页之 `content_type` / `core_topic` / `manual_note`，设 `source: \"manual\"` 即可持久保留。")
    lines.append("")

    return "\n".join(lines)


# ============================================================
# 查询
# ============================================================

def query_images(
    repo: Path,
    *,
    keyword: str | None = None,
    content_type: str | None = None,
    chapter: int | None = None,
    course_filter: str | None = None,
) -> list[dict]:
    """在仓库中查询符合条件的图片标注。

    参数：
        keyword: 关键词（匹配 core_topic / keywords / text_summary）
        content_type: 内容类型过滤
        chapter: 章节号过滤
        course_filter: 课程名关键字过滤
    """
    results: list[dict] = []

    courses = sorted(
        d for d in repo.iterdir()
        if d.is_dir() and (d / "_图注索引.json").exists()
    )
    if course_filter:
        courses = [c for c in courses if course_filter in c.name]

    for course_dir in courses:
        index = read_json(course_dir / "_图注索引.json")
        if not index:
            continue

        for a in index.get("annotations", []):
            # 章节过滤
            if chapter is not None and a.get("chapter_num") != chapter:
                continue
            # 类型过滤
            if content_type and a.get("content_type") != content_type:
                continue
            # 关键词过滤
            if keyword:
                kw_lower = keyword.lower()
                searchable = " ".join([
                    a.get("core_topic", ""),
                    " ".join(a.get("keywords", [])),
                    a.get("text_summary", ""),
                    a.get("pdf_name", ""),
                ]).lower()
                if kw_lower not in searchable:
                    continue

            results.append({
                **a,
                "course_dir": course_dir.name,
            })

    return results


def format_query_results(results: list[dict]) -> str:
    """格式化查询结果为 Markdown。"""
    if not results:
        return "∅ 无匹配结果"

    lines: list[str] = []
    lines.append(f"# 图片查询结果（{len(results)} 条）")
    lines.append("")
    lines.append("| 课程 | 章 | 页 | 类型 | 核心内容 | 关键词 | 图片 |")
    lines.append("| ---- | --: | --: | ---- | -------- | ------ | ---- |")

    for a in results[:50]:  # 限制显示数量
        course = a.get("course_dir", "")
        ch = a.get("chapter_num", "—")
        pg = a.get("page", 0)
        t = a.get("content_type", "other")
        label = ContentType.LABELS.get(t, t)
        topic = a.get("core_topic", "—")
        kws = "、".join(a.get("keywords", [])[:3]) or "—"
        rel = a.get("rel_dir", "")
        img = a.get("image", "")
        link = f"[📷](../{course}/{rel}/{img})" if rel and img else "—"
        lines.append(f"| {course[:20]} | {ch} | {pg} | {label} | {topic} | {kws} | {link} |")

    if len(results) > 50:
        lines.append(f"| ... | | | | | | （共 {len(results)} 条，仅显示前 50） |")

    lines.append("")
    return "\n".join(lines)


# ============================================================
# LLM 视觉标注·导出/回写
# ============================================================

def export_llm_tasks(course_dir: Path, output_dir: Path | None = None) -> int:
    """导出 LLM 视觉标注任务（JSON 格式，供离线处理）。

    道法：
        对每页图片生成一个标注任务，
        LLM 看图后返回 content_type / core_topic / keywords。
        仅导出自动标注置信度 < 0.7 或类型为 other/mixed 之页。
    """
    index = read_json(course_dir / "_图注索引.json")
    if not index:
        return 0

    out = output_dir or course_dir / "_图注_LLM任务"
    out = Path(out)
    out.mkdir(exist_ok=True)

    tasks: list[dict] = []
    for a in index.get("annotations", []):
        # 仅导出低置信度或待确认之页
        if a.get("source") in ("llm", "manual"):
            continue
        if a.get("confidence", 1.0) >= 0.7 and a.get("content_type") not in (
            ContentType.OTHER, ContentType.MIXED, ContentType.IMAGE,
        ):
            continue

        rel_dir = a.get("rel_dir", "")
        img = a.get("image", "")
        pg = a.get("page", 0)

        tasks.append({
            "course_dir": course_dir.name,
            "rel_dir": rel_dir,
            "page": pg,
            "image_path": f"{course_dir.name}/{rel_dir}/{img}",
            "current_type": a.get("content_type"),
            "current_topic": a.get("core_topic"),
            "current_keywords": a.get("keywords", []),
            "text_summary": a.get("text_summary", ""),
            "prompt": (
                "请分析这张课件截图，返回 JSON：\n"
                '{"content_type": "title|definition|formula|table|flowchart|example|summary|list|image|mixed|other|blank", '
                '"core_topic": "此页核心主题（≤20字）", '
                '"keywords": ["关键词1", "关键词2", "关键词3"], '
                '"manual_note": "补充说明（可选）"}'
            ),
        })

    if tasks:
        task_file = out / f"_图注任务_{course_dir.name[:20]}.json"
        write_json(task_file, {"task_count": len(tasks), "tasks": tasks})
        log(f"  ↳ 导出 {len(tasks)} 个 LLM 标注任务 → {task_file}", "ok")

    return len(tasks)


def writeback_llm_annotations(course_dir: Path, resp_dir: Path | None = None) -> int:
    """回写 LLM 视觉标注结果。

    道法：
        从 _图注_LLM回写/ 目录读取 LLM 返回之 JSON，
        更新对应 _图注.json 中之标注，标记 source: "llm"。
    """
    resp_path = resp_dir or course_dir / "_图注_LLM回写"
    resp_path = Path(resp_path)

    if not resp_path.exists():
        log(f"  ∅ 无 LLM 回写目录: {resp_path}", "warn")
        return 0

    resp_files = list(resp_path.glob("*.json"))
    if not resp_files:
        return 0

    updated = 0
    for rf in resp_files:
        resp = read_json(rf)
        if not resp:
            continue

        tasks = resp.get("tasks") or resp.get("results") or []
        for task in tasks:
            rel_dir = task.get("rel_dir", "")
            pg = task.get("page", 0)
            llm_result = task.get("result") or task.get("annotation") or {}

            if not rel_dir or not llm_result:
                continue

            # 更新 _图注.json
            annot_path = course_dir / rel_dir / "_图注.json"
            annot = read_json(annot_path)
            if not annot:
                continue

            for a in annot.get("annotations", []):
                if a.get("page") == pg:
                    a["content_type"] = llm_result.get("content_type", a.get("content_type"))
                    a["core_topic"] = llm_result.get("core_topic", a.get("core_topic"))
                    a["keywords"] = llm_result.get("keywords", a.get("keywords"))
                    a["source"] = "llm"
                    if llm_result.get("manual_note"):
                        a["manual_note"] = llm_result["manual_note"]
                    updated += 1
                    break

            write_json(annot_path, annot)

    if updated > 0:
        # 重建课程索引
        annotate_course(course_dir, force=False)
        log(f"  ✓ 回写 {updated} 条 LLM 标注", "ok")

    return updated


# ============================================================
# 章节素材增强·图注插入
# ============================================================

def enhance_chapter_md(course_dir: Path) -> int:
    """将图注信息插入章节素材 md 之主版课件部分。

    道法：
        在现有「展开 N 页图链」之后，追加「图注速览」表，
        按内容类型分类列出每页之核心内容，方便快速定位。
    """
    chart_path = course_dir / "_章节图谱.json"
    chart = read_json(chart_path)
    if not chart:
        return 0

    index_path = course_dir / "_图注索引.json"
    index = read_json(index_path)
    if not index:
        return 0

    # 构建图注查询索引: (rel_dir, page) → annotation
    annot_lookup: dict[tuple[str, int], dict] = {}
    for a in index.get("annotations", []):
        key = (a.get("rel_dir", ""), a.get("page", 0))
        annot_lookup[key] = a

    enhanced = 0
    素材_dir = course_dir / "_素材"

    for ch in chart.get("chapters", []):
        ch_num = ch["chapter_num"]
        ch_title = ch.get("chapter_title", "")
        md_name = _chap_md_name(ch_num, ch_title)
        md_path = 素材_dir / md_name

        if not md_path.exists():
            continue

        text = md_path.read_text(encoding="utf-8")

        # 若已有旧图注速览/图文对照 → 先移除再重建
        if "图注速览" in text or "图文1:1对照" in text:
            text = re.sub(
                r"\n*### 图注速览 · 按内容类型.*?(?=\n---|\n## |\Z)",
                "",
                text,
                flags=re.DOTALL,
            )

        # 收集主版之图注
        primary = ch.get("primary", {})
        rel_dir = primary.get("rel_dir", "")
        if not rel_dir:
            continue

        page_annots = []
        for a in index.get("annotations", []):
            if a.get("rel_dir") == rel_dir:
                page_annots.append(a)

        if not page_annots:
            continue

        # 生成图注速览表 + 图文1:1对照
        table_lines: list[str] = []
        table_lines.append("")
        table_lines.append("### 图注速览 · 按内容类型")
        table_lines.append("")
        table_lines.append("| 页 | 类型 | 核心内容 | 关键词 |")
        table_lines.append("| --: | ---- | -------- | ------ |")

        for a in sorted(page_annots, key=lambda x: x.get("page", 0)):
            pg = a.get("page", 0)
            t = a.get("content_type", "other")
            label = ContentType.LABELS.get(t, t)
            topic = a.get("core_topic", "") or "—"
            kws = "、".join(a.get("keywords", [])[:3]) or "—"
            table_lines.append(f"| {pg} | {label} | {topic} | {kws} |")

        table_lines.append("")

        # ── 图文1:1对照：每页图配其OCR文本 ──
        # 道法：真正的图文匹配，每图对应其完整文本内容
        table_lines.append("### 图文1:1对照 · 每图配其识别文本")
        table_lines.append("")

        # 读取_doc.json获取OCR文本
        doc_meta = read_json(course_dir / rel_dir / "_doc.json")
        pages_meta = {}
        if doc_meta:
            for p in doc_meta.get("pages", []):
                pages_meta[p.get("index", 0)] = p

        for a in sorted(page_annots, key=lambda x: x.get("page", 0)):
            pg = a.get("page", 0)
            t = a.get("content_type", "other")
            label = ContentType.LABELS.get(t, t)
            topic = a.get("core_topic", "") or ""
            img_file = a.get("image", "") or f"page_{pg:03d}.jpg"

            # 取OCR文本
            p_meta = pages_meta.get(pg, {})
            ocr = (p_meta.get("ocr_text") or "").strip()
            emb = (p_meta.get("embedded_text") or "").strip()
            page_text = ocr or emb

            # 图片链接
            table_lines.append(f"#### p{pg:03d} {label}")
            table_lines.append("")
            table_lines.append(f"![p{pg}](../{rel_dir}/{img_file})")
            table_lines.append("")

            # OCR文本（折叠，避免太长）
            if page_text:
                # 截取前200字作摘要
                text_preview = page_text[:200]
                if len(page_text) > 200:
                    text_preview += "..."
                table_lines.append(f"> **核心**: {topic}")
                table_lines.append("")
                table_lines.append(f"<details><summary>识别文本（{len(page_text)}字）</summary>")
                table_lines.append("")
                table_lines.append(page_text)
                table_lines.append("")
                table_lines.append("</details>")
                table_lines.append("")

        table_lines.append("")

        # 插入到主版课件 section 之后
        insert_text = "\n".join(table_lines)

        # 找到「展开 N 页图链」的 </details> 后插入
        pattern = r"(</details>\s*\n)"
        m = re.search(pattern, text)
        if m:
            text = text[:m.end()] + insert_text + text[m.end():]
            md_path.write_text(text, encoding="utf-8")
            enhanced += 1

    return enhanced


def _chap_md_name(n: int, title: str) -> str:
    """与 课件_知识素材.py 之 chapter_filename 一致"""
    t = sanitize_filename(title or "无题", max_len=40).strip()
    if n == 0:
        return f"_第00章_{t}.md".replace(" ", "_")
    return f"_第{n:02d}章_{t}.md".replace(" ", "_")


# ============================================================
# 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="PDF 图注 —— 每图匹配其核心内容",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--repo", "-r", default="解析仓库",
                        help="解析仓库目录（默 ./解析仓库）")
    parser.add_argument("--filter", "-f", action="append", default=None,
                        help="课程名关键字过滤")
    parser.add_argument("--force", action="store_true",
                        help="强制重标（覆盖已有自动标注）")

    # 功能模式
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--export-llm", action="store_true",
                       help="导出 LLM 视觉标注任务")
    group.add_argument("--writeback-llm", action="store_true",
                       help="回写 LLM 标注结果")
    group.add_argument("--query", metavar="KEYWORD",
                       help="查询含此关键词之图片")
    group.add_argument("--query-type", metavar="TYPE",
                       help="查询指定内容类型之图片")
    group.add_argument("--gen-md", action="store_true",
                       help="生成人读图注索引 Markdown")
    group.add_argument("--enhance", action="store_true",
                       help="将图注插入章节素材 md")

    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    repo = Path(args.repo)
    if not repo.is_absolute():
        repo = script_dir / repo

    header("PDF 图注 —— 每图匹配其核心内容", width=58)

    if not repo.exists():
        log(f"× 仓库不存: {repo}", "err")
        sys.exit(1)

    # ── 查询模式 ──
    if args.query or args.query_type:
        results = query_images(
            repo,
            keyword=args.query,
            content_type=args.query_type,
            course_filter=args.filter[0] if args.filter else None,
        )
        output = format_query_results(results)
        print(output)
        return

    # ── 扫描课程 ──
    courses = sorted([
        d for d in repo.iterdir()
        if d.is_dir() and (d / "_course.json").exists()
    ])
    if args.filter:
        courses = [c for c in courses if any(kw in c.name for kw in args.filter)]

    if not courses:
        log("∅ 无可处理之课程", "warn")
        return

    log(f"\n共 {len(courses)} 门课程", "info")

    # ── LLM 导出模式 ──
    if args.export_llm:
        total_tasks = 0
        for course_dir in courses:
            # 先确保图注已生成
            annotate_course(course_dir, force=args.force)
            n = export_llm_tasks(course_dir)
            total_tasks += n
        header(f"LLM 任务导出毕  ——  {total_tasks} 个标注任务", width=58)
        return

    # ── LLM 回写模式 ──
    if args.writeback_llm:
        total_updated = 0
        for course_dir in courses:
            n = writeback_llm_annotations(course_dir)
            total_updated += n
        header(f"LLM 回写毕  ——  {total_updated} 条标注已更新", width=58)
        return

    # ── 生成 Markdown 模式 ──
    if args.gen_md:
        for course_dir in courses:
            # 先确保图注已生成
            annotate_course(course_dir, force=args.force)
            md = generate_图注_md(course_dir)
            if md:
                out_path = course_dir / "_素材" / "_图注索引.md"
                out_path.parent.mkdir(exist_ok=True)
                out_path.write_text(md, encoding="utf-8")
                info = parse_course_dirname(course_dir.name)
                log(f"  ✓ {info['course_name']:<24s} → _图注索引.md", "ok")
        header("图注索引 Markdown 生成毕", width=58)
        return

    # ── 增强素材模式 ──
    if args.enhance:
        for course_dir in courses:
            annotate_course(course_dir, force=args.force)
            n = enhance_chapter_md(course_dir)
            info = parse_course_dirname(course_dir.name)
            log(f"  ✓ {info['course_name']:<24s} · 增强 {n} 章", "ok")
        header("素材增强毕", width=58)
        return

    # ── 默认：自动标注 ──
    for course_dir in courses:
        info = parse_course_dirname(course_dir.name)
        index = annotate_course(course_dir, force=args.force)
        if index:
            stats = index.get("stats", {})
            dist = index.get("type_distribution", {})
            top_types = sorted(dist.items(), key=lambda x: -x[1])[:3]
            type_str = "、".join(
                f"{ContentType.LABELS.get(t, t)}({n})" for t, n in top_types
            )
            log(
                f"  ✓ {info['course_name']:<24s} "
                f"({stats.get('annotated', 0)} 页标注 · {type_str})",
                "ok",
            )
        else:
            log(f"  ∅ {info['course_name']:<24s} (无可标注之页)", "dim")

    header("图注毕  ——  每图已匹配其核心内容", width=58)


if __name__ == "__main__":
    main()
