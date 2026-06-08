# -*- coding: utf-8 -*-
"""
OCR 文本清洗管道  ——  涤除垢尘，复归其明

道法：
    OCR 之原始文本含水印、碎片、噪声。
    本模块为唯一清洗入口——所有 OCR 引擎输出经此管道后，
    方写入 _doc.json 之 ocr_text 字段。
    下游（图注、全文md）不再需重复清洗。

    清洗顺序（道之序）：
    1. 水印行移除（整行匹配）
    2. 行尾水印清理（"1.1XX 新蓬大学" → "1.1XX"）
    3. OCR碎片过滤（source/from/ptag等HTML残留）
    4. 极短低质行移除（≤2字符非中文）
    5. 空行压缩
"""

from __future__ import annotations

import re

# ── 水印模式 ──────────────────────────────────────────────

# 雨课堂课件常见校名水印（OCR 误识变体）
_WATERMARK_LINE_RE = re.compile(
    r"^(新[蓬雄建疆]?大学|Xinj?iang\s*Un?iver?si?t[ys]"
    r"|ngUnn?versit[ys]|Unn?versiry|Unn?versity"
    r"|Uenversity|Unvensi[n]?|Unnver|Uevenn\d*|Uavers(?:ity)?\d*"
    r"|ang\s*Uenversity|Uenvers"
    r"|Uenversity|Unversity|Unversit[ys]"
    r"|Univ[ea]rs[ia]t[ey]|Univ\.?$"
    r")$",
    re.IGNORECASE,
)

# 行尾水印（如 "1.1环境毒理学及其发展 新建大学"）
_TRAILING_WATERMARK_RE = re.compile(
    r"\s+(新[蓬雄建疆]?大学|Xinj?iang\s*Un?iver?si?t[ys]"
    r"|ngUnn?versit[ys]|Unn?versiry|Unn?versity"
    r"|Uenversity|Unvensi[n]?|Unnver|Uevenn\d*|Uavers(?:ity)?\d*"
    r"|ang\s*Uenversity|Uenvers"
    r"|Uenversity|Unversity|Unversit[ys]"
    r"|Univ[ea]rs[ia]t[ey]|Univ\.?"
    r")\s*$",
    re.IGNORECASE,
)

# 行内水印碎片（如 "Uenversity3", "Unnver", "Unvensin1.", "Uevenn1.", "Uaversity3." 等）
# 道法：OCR误识校名水印的核心特征是含 "nivers/vers/versi/versity/vens" 等子串
# 用更宽松的模式：U + 0-4个字母 + (vers|vens) + 0-4个字母 + 可选数字+点
# 保护：排除正常英文词（divers/converse/universal/overs/inverse等）
_INLINE_WATERMARK_RE = re.compile(
    r"\s*(ang\s*)?[Uu][a-z]{0,4}v(?:ers|ens)[a-z]{0,4}\d*\.?\s*"
    r"|\s*(ang\s*)?[Uu]even[n]?\d*\.?\s*",
    re.IGNORECASE,
)

# 安全检查：正常英文词不应被误删
_SAFE_EN_WORDS = frozenset({
    "divers", "diverse", "converse", "universal", "universe",
    "universally", "inverse", "inversely", "overs", "convers",
    "adversary", "adverse", "controversy", "traverse",
})

# ── OCR 碎片模式 ──────────────────────────────────────────

# HTML/代码残留碎片（RapidOCR 误识课件中的代码/URL片段）
_FRAGMENT_LINE_RE = re.compile(
    r"^(source|from|ptag|href|src|alt|class|id|div|span|img|http|https|www|com|org|net|html|css|js|base64|data|image|png|jpg|jpeg|gif|svg|script|style|link|meta|head|body|font|color|align|width|height|border|padding|margin|display|block|inline|none|auto|center|left|right|top|bottom|position|relative|absolute|fixed|overflow|hidden|visible|scroll|text|content|url|background|opacity|filter|transform|transition|animation|keyframes|media|import|export|default|return|function|const|let|var|type|interface|class|extends|implements|public|private|protected|static|final|abstract|virtual|override|super|this|new|delete|null|undefined|true|false|NaN|Infinity|async|await|yield|generator|iterator|promise|resolve|reject|then|catch|finally|try|throw|error|exception|debugger|console|log|warn|error|info|debug|trace|assert|dir|table|group|groupEnd|time|timeEnd|profile|profileEnd|count|clear|indent|unindent|show|create|destroy)$",
    re.IGNORECASE,
)

# URL 碎片行（OCR 误识课件中的超链接）
_URL_FRAGMENT_RE = re.compile(
    r"^(https?://|//|www\.|\.com|\.cn|\.org|\.net|\.edu|sohu|sina|baidu|zhihu|weibo|bilibili|douyin|toutiao)",
    re.IGNORECASE,
)

# 含URL碎片之行（行内含 https:// 或 //xxx.com 等）
_INLINE_URL_RE = re.compile(
    r"https?://\S+|//\w+\.\w{2,4}",
    re.IGNORECASE,
)

# 视频嵌入碎片（雨课堂课件中的视频占位符OCR误识）
_VIDEO_FRAGMENT_RE = re.compile(
    r"(网络视频|视频框|search-card|\.click|此视频|可被拖动|修改大小|上传手机课件|手机进行观看|温馨提示)",
    re.IGNORECASE,
)

# Base64 编码片段（OCR 误识嵌入对象）
_BASE64_LINE_RE = re.compile(
    r"^[A-Za-z0-9+/=]{16,}$"  # 纯base64字符，≥16字符
)

# 极短英文碎片（≤4字符纯ASCII，非有意义的化学式/缩写）
_SHORT_FRAGMENT_RE = re.compile(
    r"^[a-zA-Z0-9_/\\]{1,4}$"
)

# 有意义的短英文术语（不应被过滤）
_MEANINGFUL_SHORT = {
    "LD50", "LC50", "NOAEL", "LOAEL", "ADI", "RfD", "SF", "BMD", "BMDL",
    "TD50", "TI", "MOE", "HQ", "HI", "CR", "Vd", "Ke", "Ka", "CL", "V",
    "t½", "Cmax", "Tmax", "AUC", "F", "Db", "Dd", "Ds", "Dm",
    "DNA", "RNA", "ATP", "ADP", "AMP", "GTP", "cAMP", "cGMP",
    "pH", "POPs", "VOC", "SVOC", "PM2.5", "PM10", "SO2", "NO2", "O3",
    "PAH", "PCB", "Dioxin", "BPA", "DEHP", "DDT", "HCH",
    "Ames", "TA98", "TA100", "TA97", "TA102", "TA1535", "TA1537",
    "His", "G8", "R8", "M2", "M3", "S9", "CYP", "GST", "SOD", "CAT", "GPx",
    "MDA", "ROS", "GSH", "NADH", "NADPH", "CO2", "H2O2", "OH",
    "IgG", "IgM", "IgA", "IgE", "IL-1", "IL-6", "TNF", "IFN",
    "NO", "NOS", "COX", "LOX", "PG", "LT", "TX",
    "EPA", "FDA", "WHO", "IARC", "OECD", "ISO",
    "Pb", "Hg", "Cd", "Cr", "As", "Ni", "Zn", "Cu", "Mn", "Fe", "Al",
    "mg", "kg", "ug", "ng", "pg", "ml", "L", "mM", "uM", "nM", "pM",
    "iv", "ip", "im", "sc", "po", "ig", "inh",
}


def clean_ocr_text(raw_text: str) -> str:
    """OCR 文本清洗管道——唯一入口。

    道法：
        此函数为所有 OCR 输出之必经之路。
        清洗后之文本方写入 _doc.json，下游不再重复清洗。
    """
    if not raw_text or not raw_text.strip():
        return ""

    lines_raw = raw_text.split("\n")
    lines_clean: list[str] = []

    for line in lines_raw:
        stripped = line.strip()
        if not stripped:
            continue

        # 1. 整行水印 → 跳过
        if _WATERMARK_LINE_RE.match(stripped):
            continue

        # 2. 行尾水印清理
        stripped = _TRAILING_WATERMARK_RE.sub("", stripped).strip()
        if not stripped:
            continue

        # 2.5 行内水印碎片清理（如 "ang Uenversity3", "Unvensin1."）
        # 安全检查：若行含正常英文词则跳过行内清理
        if not any(w in stripped.lower() for w in _SAFE_EN_WORDS):
            stripped = _INLINE_WATERMARK_RE.sub(" ", stripped).strip()
            if not stripped:
                continue

        # 3. OCR碎片行 → 跳过
        if _FRAGMENT_LINE_RE.match(stripped):
            continue

        # 3.5 URL碎片行 → 跳过
        if _URL_FRAGMENT_RE.match(stripped):
            continue

        # 3.6 行内URL碎片 → 清除
        stripped = _INLINE_URL_RE.sub("", stripped).strip()
        if not stripped:
            continue

        # 3.7 视频嵌入碎片 → 清除含碎片的行
        stripped = _VIDEO_FRAGMENT_RE.sub("", stripped).strip()
        if not stripped:
            continue

        # 3.8 Base64编码片段 → 跳过
        if _BASE64_LINE_RE.match(stripped):
            continue

        # 4. 极短低质行（≤2字符非中文，非有意义术语）
        if len(stripped) <= 4 and stripped.isascii():
            if stripped.upper() not in {w.upper() for w in _MEANINGFUL_SHORT}:
                # 检查是否为化学式/数字（如 "3.5", "1/2"）
                if not re.match(r"^[\d./]+$", stripped):
                    continue

        lines_clean.append(stripped)

    # 5. 空行压缩
    result = "\n".join(lines_clean)

    # 6. 跨行碎片合并（如 "LD\n2" → "LD2"，"00\n2" → "002"）
    # 道法：OCR 常将一个词拆成多行，需合并
    result = re.sub(r"([A-Za-z])\n(\d+)", r"\1\2", result)  # LD\n50 → LD50
    result = re.sub(r"(\d)\n(\d)", r"\1\2", result)          # 0\n2 → 02
    result = re.sub(r"([A-Za-z])\n([A-Za-z])", r"\1\2", result)  # co\nm → com

    # 7. 残留碎片行过滤（合并后可能产生新的碎片行）
    final_lines = []
    for line in result.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        # 纯数字+符号碎片（如 "10,00", "12~0"）
        if re.match(r"^[\d,.\-~+/\\]+$", stripped) and len(stripped) <= 8:
            continue
        # 极短英文碎片
        if len(stripped) <= 3 and stripped.isascii():
            if stripped.upper() not in {w.upper() for w in _MEANINGFUL_SHORT}:
                continue
        final_lines.append(stripped)

    return "\n".join(final_lines)


def is_ocr_fragment(text: str) -> bool:
    """判文本是否为OCR碎片（用于关键词/主题过滤）。"""
    if not text:
        return True
    if _FRAGMENT_LINE_RE.match(text.strip()):
        return True
    if len(text) <= 4 and text.isascii():
        if text.upper() not in {w.upper() for w in _MEANINGFUL_SHORT}:
            return True
    return False
