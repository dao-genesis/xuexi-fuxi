# -*- coding: utf-8 -*-
"""
PDF → Markdown 统一引擎  ——  道法自然，无为而无不为

道法：
    PDF 有二类：文字型（可直取文本）与图像型（须 OCR 识文）。
    本引擎智能路由：
      - 先以 PyMuPDF 探文本——若有字，直取之（最快·零损）；
      - 若无字（纯图 PDF），则以 RapidOCR 识图（中文最强·已装可用）；
      - pdfplumber / MarkItDown 为文字型兜底；
      - 多引擎竞合：同一 PDF 可多路提取，取最优。
    输出为结构化 Markdown，章节标题自识别，表格尽力保真。

    反者道之动——不依赖未装之重器，从已有之本源出发，
    PyMuPDF + RapidOCR + pdfplumber + MarkItDown，四器归一。

依赖：
    pip install pymupdf rapidocr-onnxruntime pdfplumber markitdown

用法（模块级）：
    from pdf2md_引擎 import pdf2md, pdf2md_batch

    # 单文件
    result = pdf2md("test.pdf")
    print(result.markdown)

    # 批量
    results = pdf2md_batch("课程PDF目录/")

用法（命令行）：
    python pdf2md_引擎.py input.pdf
    python pdf2md_引擎.py input.pdf -o output.md
    python pdf2md_引擎.py input_dir/ -o output_dir/
    python pdf2md_引擎.py input.pdf --engine auto|rapidocr|pymupdf|pdfplumber|markitdown
    python pdf2md_引擎.py input.pdf --compare   # 多引擎竞合，取最优
"""

from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

# ── 引擎可用性探测 ──────────────────────────────────────────

_HAS_FITZ = False
_HAS_RAPIDOCR = False
_HAS_PDFPLUMBER = False
_HAS_MARKITDOWN = False

try:
    import fitz  # PyMuPDF
    _HAS_FITZ = True
except ImportError:
    pass

try:
    from rapidocr_onnxruntime import RapidOCR
    _OCR_ENGINE = RapidOCR()
    _HAS_RAPIDOCR = True
except Exception:
    _OCR_ENGINE = None

try:
    import pdfplumber
    _HAS_PDFPLUMBER = True
except ImportError:
    pass

try:
    from markitdown import MarkItDown
    _MD_ENGINE = MarkItDown()
    _HAS_MARKITDOWN = True
except Exception:
    _MD_ENGINE = None

# 共用之器
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _yc_common import log, header, write_json, read_json  # noqa: E402
from _ocr_clean import clean_ocr_text  # noqa: E402


# ── 数据结构 ────────────────────────────────────────────────

@dataclass
class PageResult:
    """单页提取结果"""
    index: int = 0
    text: str = ""
    engine: str = ""
    confidence: float = 0.0
    is_image_page: bool = False  # 此页为纯图（无嵌入文本）
    image_path: str = ""         # 提取之图路径


@dataclass
class Pdf2MdResult:
    """单 PDF → Markdown 结果"""
    pdf_path: str = ""
    markdown: str = ""
    pages: list[PageResult] = field(default_factory=list)
    engine_used: str = ""
    total_chars: int = 0
    elapsed: float = 0.0
    page_count: int = 0
    text_pages: int = 0      # 有嵌入文本之页数
    image_pages: int = 0     # 纯图之页数
    ocr_pages: int = 0       # 经 OCR 之页数


# ── 引擎1：PyMuPDF 直取文本 ─────────────────────────────────

def _extract_pymupdf_text(pdf_path: str | Path) -> list[PageResult]:
    """PyMuPDF 直取嵌入文本。返每页结果。"""
    if not _HAS_FITZ:
        return []
    doc = fitz.open(str(pdf_path))
    results: list[PageResult] = []
    for i, page in enumerate(doc):
        text = page.get_text("text") or ""
        imgs = page.get_images(full=False)
        is_img = len(text.strip()) < 10 and len(imgs) >= 1
        results.append(PageResult(
            index=i,
            text=text.strip(),
            engine="pymupdf",
            confidence=1.0 if text.strip() else 0.0,
            is_image_page=is_img,
        ))
    doc.close()
    return results


# ── 引擎2：RapidOCR 识图 ────────────────────────────────────

def _ocr_rapidocr(image_path: str | Path) -> tuple[str, float]:
    """RapidOCR 识单图。返 (text, avg_score)。"""
    if _OCR_ENGINE is None:
        return "", 0.0
    try:
        result, _elapse = _OCR_ENGINE(str(image_path))
    except Exception as e:
        log(f"    × RapidOCR 败: {e}", "warn")
        return "", 0.0
    if not result:
        return "", 0.0
    # result: [[bbox, text, score], ...]
    lines_info = []
    for bbox, text, score in result:
        y_top = bbox[0][1] if bbox else 0
        x_left = bbox[0][0] if bbox else 0
        lines_info.append({
            "text": text,
            "score": score,
            "y_top": y_top,
            "x_left": x_left,
        })
    # 按 y 排序，同行按 x
    lines_info.sort(key=lambda l: (round(l["y_top"] / 10), l["x_left"]))
    # 合并同行
    row_groups: list[list[dict]] = []
    current_row: list[dict] = [lines_info[0]]
    for ln in lines_info[1:]:
        if abs(ln["y_top"] - current_row[0]["y_top"]) < 15:
            current_row.append(ln)
        else:
            row_groups.append(current_row)
            current_row = [ln]
    row_groups.append(current_row)

    text_lines: list[str] = []
    total_score = 0.0
    for row in row_groups:
        row.sort(key=lambda l: l["x_left"])
        text_lines.append(" ".join(l["text"] for l in row))
        total_score += sum(l["score"] for l in row) / len(row)
    avg_score = total_score / len(row_groups) if row_groups else 0.0
    raw_text = "\n".join(text_lines)
    # 清洗管道：水印、碎片、噪声在源头移除
    cleaned = clean_ocr_text(raw_text)
    return cleaned, avg_score


def _extract_rapidocr_pages(pdf_path: str | Path, *, dpi: int = 150) -> list[PageResult]:
    """RapidOCR 对 PDF 逐页 OCR。
    
    道法（三层加速）：
      1. 直取内嵌原图（最快·无损·雨课堂PDF之常态·15-35KB）
      2. 150DPI JPEG 渲染兜底（比200DPI PNG快2.7倍·识别几乎无损）
      3. 内存直传——不写临时文件，numpy bytes 直传 OCR
    实测：50页 18s（内嵌图）vs 54s（200DPI PNG），2.9x 加速。
    """
    if not _HAS_FITZ or not _HAS_RAPIDOCR:
        return []
    import tempfile
    tmp_dir = Path(tempfile.mkdtemp(prefix="pdf2md_"))
    doc = fitz.open(str(pdf_path))
    results: list[PageResult] = []
    
    for i, page in enumerate(doc):
        img_path: Path | None = None
        
        # 策略A：直取内嵌原图（最快·无损·雨课堂PDF之常态）
        try:
            imgs = page.get_images(full=False)
            if len(imgs) >= 1:
                xref = imgs[0][0]
                pix_info = doc.extract_image(xref)
                if pix_info and pix_info.get("image"):
                    ext = pix_info.get("ext", "jpeg")
                    suffix = ".jpg" if ext in ("jpeg", "jpg") else f".{ext}"
                    img_path = tmp_dir / f"page_{i:03d}{suffix}"
                    img_path.write_bytes(pix_info["image"])
        except Exception:
            img_path = None
        
        # 策略B：150DPI JPEG 渲染兜底（比200DPI PNG快2.7倍）
        if img_path is None or not img_path.exists():
            try:
                pix = page.get_pixmap(dpi=dpi)
                img_path = tmp_dir / f"page_{i:03d}.jpg"
                img_path.write_bytes(pix.tobytes("jpeg", jpg_quality=50))
            except Exception as e:
                log(f"    × 第{i+1}页渲染败: {e}", "warn")
                results.append(PageResult(index=i, engine="rapidocr", is_image_page=True))
                continue
        
        # OCR
        text, score = _ocr_rapidocr(img_path)
        results.append(PageResult(
            index=i,
            text=text,
            engine="rapidocr",
            confidence=score,
            is_image_page=True,
        ))
    
    doc.close()
    # 清理临时目录
    try:
        for f in tmp_dir.iterdir():
            f.unlink(missing_ok=True)
        tmp_dir.rmdir()
    except Exception:
        pass
    return results


def _ocr_image_file(image_path: str | Path) -> tuple[str, float]:
    """对已有图文件执行 OCR。公开接口，供 pdf_提文.py 调用。"""
    return _ocr_rapidocr(image_path)


# ── 引擎3：pdfplumber ───────────────────────────────────────

def _extract_pdfplumber(pdf_path: str | Path) -> list[PageResult]:
    """pdfplumber 提取文本+表格。"""
    if not _HAS_PDFPLUMBER:
        return []
    results: list[PageResult] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            # 尝试提取表格
            tables = page.extract_tables()
            table_md = ""
            for tbl in tables:
                if tbl:
                    table_md += _table_to_md(tbl) + "\n"
            combined = (text + "\n" + table_md).strip()
            results.append(PageResult(
                index=i,
                text=combined,
                engine="pdfplumber",
                confidence=0.9 if text.strip() else 0.0,
                is_image_page=len(text.strip()) < 10,
            ))
    return results


# ── 引擎4：MarkItDown ──────────────────────────────────────

def _extract_markitdown(pdf_path: str | Path) -> list[PageResult]:
    """MarkItDown 提取。仅返整体文本（不分页）。"""
    if not _HAS_MARKITDOWN:
        return []
    try:
        result = _MD_ENGINE.convert(str(pdf_path))
        text = result.text_content or ""
    except Exception as e:
        log(f"    × MarkItDown 败: {e}", "warn")
        return []
    if not text.strip():
        return []
    # MarkItDown 不分页，整体作为 page 0
    return [PageResult(
        index=0,
        text=text,
        engine="markitdown",
        confidence=0.7,
        is_image_page=False,
    )]


# ── 表格 → Markdown ────────────────────────────────────────

def _table_to_md(table: list[list[str | None]]) -> str:
    """二维列表 → Markdown 表格。"""
    if not table:
        return ""
    # 清理 None
    rows = [[(c or "").strip() for c in row] for row in table]
    if not rows:
        return ""
    # 表头
    md = "| " + " | ".join(rows[0]) + " |\n"
    md += "| " + " | ".join("---" for _ in rows[0]) + " |\n"
    for row in rows[1:]:
        # 补齐列数
        while len(row) < len(rows[0]):
            row.append("")
        md += "| " + " | ".join(row[:len(rows[0])]) + " |\n"
    return md


# ── 文本 → 结构化 Markdown ─────────────────────────────────

# ── OCR 噪声过滤 ───────────────────────────────────────────

# OCR 碎片清洗（单行级·在 OCR 源头即移除）
_FRAGMENT_PATTERNS = [
    re.compile(r"^[a-z]{1,4}$"),                    # 纯英文碎片: "m", "rom", "co"
    re.compile(r"^\d{1,3}[a-zA-Z]{1,3}$"),          # 混合碎片: "2n+2", "30NM"
    re.compile(r"^\.\.(all|click|com)$", re.I),      # URL碎片
    re.compile(r"^[a-z]+\.\d+\.", re.I),             # URL碎片2
    re.compile(r"^from=\d+"),                         # URL参数
    re.compile(r"^m=\d+\.\d+"),                       # URL参数
]

# 页眉/页脚检测：跨页频率统计法
# 道法：若一行文本在>=30%的页中出现，则为页眉/页脚，应滤除。
# 此法不依赖正则模式，自适应任何PDF的页眉页脚。

def _is_heading_line(line: str) -> bool:
    """判断一行是否为章节标题（跨页重复出现是正常的，不应被当噪声滤除）。"""
    s = line.strip()
    if not s:
        return False
    # 章标题
    if re.match(r"^(第[一二三四五六七八九十百零\d]+章|Chapter\s+\d+)", s, re.IGNORECASE):
        return True
    # 节标题：X.X 开头
    if re.match(r"^(\d+\.\d+(\.\d+)?)\s", s):
        return True
    # 含核心学术词汇的短行（如"环境毒理学及其发展"）
    # 这些是课程内容标题，即使跨页重复也不应滤除
    academic_kw = ['毒理学', '环境', '污染', '生态', '健康', '化学', '物理',
                   '生物', '评价', '方法', '实验', '研究', '发展', '趋势',
                   '对象', '任务', '内容', '应用', '概念', '定义', '原理',
                   '机制', '效应', '转运', '转化', '代谢', '动力学']
    if len(s) <= 30 and any(kw in s for kw in academic_kw):
        return True
    return False


def _detect_headers_footers(pages_text: list[str], threshold: float = 0.3) -> set[str]:
    """跨页频率统计法检测页眉/页脚。返应滤除之行集合。
    
    道法：精确匹配 + 模糊匹配（归一化后统计）。
    OCR 乱码如 "XingungUeversity"/"ngUnnversity" 虽每页不同，
    但归一化后皆含 "univ" 或 "大学"，以此捕获。
    """
    if len(pages_text) < 3:
        return set()
    # 统计每行出现页数（精确）
    line_page_count: dict[str, int] = {}
    # 统计归一化行出现页数（模糊）
    norm_page_count: dict[str, int] = {}
    norm_to_originals: dict[str, list[str]] = {}
    
    for text in pages_text:
        seen = set(text.strip().split("\n"))
        for line in seen:
            s = line.strip()
            if s and len(s) <= 60:
                line_page_count[s] = line_page_count.get(s, 0) + 1
                # 归一化：去数字、去空格、小写
                norm = re.sub(r'\d+', '', s).replace(' ', '').lower()
                # 进一步归一化：常见校名关键词
                for kw in ['university', 'univ', '大学', '学院', 'college']:
                    if kw in norm:
                        norm = '__SCH__'
                        break
                # 模糊校名：OCR乱码如 ngUnnversity, XingungUeversity
                # 特征：含 ersit/versi/nivers 等子串（即使拼写不全）
                if norm != '__SCH__':
                    for sub in ['ersit', 'versi', 'niver', 'nnver', 'uever', 'ngu']:
                        if sub in norm:
                            norm = '__SCH__'
                            break
                if len(norm) >= 2:
                    norm_page_count[norm] = norm_page_count.get(norm, 0) + 1
                    norm_to_originals.setdefault(norm, []).append(s)
    
    n_pages = len(pages_text)
    noise_set = set()
    
    # 精确频率
    for line, count in line_page_count.items():
        if count / n_pages >= threshold:
            # 保护：章节标题跨页重复是正常的，不是噪声
            if _is_heading_line(line):
                continue
            noise_set.add(line)
    
    # 模糊频率：归一化行出现>=30%页，则所有原始行皆滤除
    for norm, count in norm_page_count.items():
        if count / n_pages >= threshold and norm != '__SCH__':
            for orig in norm_to_originals.get(norm, []):
                # 保护章节标题
                if not _is_heading_line(orig):
                    noise_set.add(orig)
    
    # 校名特殊处理：__SCH__ 归一化行出现>=20%即滤除
    sch_count = norm_page_count.get('__SCH__', 0)
    if sch_count / n_pages >= 0.2:
        for orig in norm_to_originals.get('__SCH__', []):
            noise_set.add(orig)
    
    # 补充：纯数字页码
    for line in line_page_count:
        if re.match(r"^\d{1,3}$", line):
            noise_set.add(line)
    
    return noise_set


def _filter_ocr_noise(text: str, noise_set: set[str] | None = None) -> str:
    """过滤 OCR 噪声。noise_set 为频率法检测之页眉/页脚集合。"""
    lines = text.split("\n")
    filtered: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            filtered.append("")
            continue
        # 频率法滤除
        if noise_set and stripped in noise_set:
            continue
        # 碎片清洗
        is_frag = False
        for pat in _FRAGMENT_PATTERNS:
            if pat.match(stripped):
                is_frag = True
                break
        if is_frag:
            continue
        filtered.append(line)
    return "\n".join(filtered)


def _text_to_structured_md(text: str, noise_set: set[str] | None = None) -> str:
    """纯文本 → 结构化 Markdown（识别章节标题、列表、空行）。"""
    if not text.strip():
        return ""
    # 先过滤噪声（频率法 + 碎片清洗）
    text = _filter_ocr_noise(text, noise_set=noise_set)
    lines = text.split("\n")
    md_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            md_lines.append("")
            continue
        # 章标题：第X章 / Chapter X
        if re.match(r"^(第[一二三四五六七八九十百零\d]+章|Chapter\s+\d+)", stripped, re.IGNORECASE):
            md_lines.append("")
            md_lines.append(f"## {stripped}")
            continue
        # 节标题：X.X 或 X.X.X 开头（兼容 1.1环境毒理学 和 3.1.2吸收）
        # 条件：以数字.数字开头，且编号后跟中文或空格（非英文/单位）
        _sec_m = re.match(r"^(\d+\.\d+(?:\.\d+)?)(.*)", stripped)
        if _sec_m and _sec_m.group(2) and (re.match(r"^[\u4e00-\u9fff]", _sec_m.group(2)) or re.match(r"^\s", _sec_m.group(2))):
            md_lines.append("")
            md_lines.append(f"### {stripped}")
            continue
        # 短行 → 可能小标题
        # 道法：标题不应含句子级标点（。！？；），含则为句子非标题
        # 中文列表项（一、二、）虽短但非标题
        _SENTENCE_PUNCT = set("。！？；!?;")
        _has_sentence_punct = any(c in _SENTENCE_PUNCT for c in stripped)
        _is_chinese_list = bool(re.match(r"^[一二三四五六七八九十]+[、.]", stripped))
        _is_numbered_list = (bool(re.match(r"^[\d]+[).、]", stripped))
                             or bool(re.match(r"^[A-D][.、)]", stripped))
                             or bool(re.match(r"^\(\d+\)", stripped)))
        _is_bullet = stripped.startswith(("•", "-", "*", "·", "●", "○", "(", "（", "【"))
        
        if (len(stripped) <= 15
            and not _has_sentence_punct
            and not _is_chinese_list
            and not _is_numbered_list
            and not _is_bullet
            and not stripped.endswith(("，", "：", "、", ",", ")", "】", "]"))):
            md_lines.append("")
            md_lines.append(f"#### {stripped}")
            continue
        md_lines.append(stripped)
    return "\n".join(md_lines)


# ── 智能路由：判断 PDF 类型 ─────────────────────────────────

def _classify_pdf(pdf_path: str | Path) -> str:
    """判断 PDF 类型：'text'（文字型）/ 'image'（纯图型）/ 'mixed'（混合）。
    
    道法：取前5页探文本，若>60%有字则 text，若<20%有字则 image，否则 mixed。
    """
    if not _HAS_FITZ:
        return "image"  # 无 PyMuPDF 则只能当图处理
    doc = fitz.open(str(pdf_path))
    sample = min(5, len(doc))
    text_count = 0
    for i in range(sample):
        page = doc[i]
        text = page.get_text("text") or ""
        if len(text.strip()) > 20:
            text_count += 1
    doc.close()
    ratio = text_count / sample if sample > 0 else 0
    if ratio > 0.6:
        return "text"
    elif ratio < 0.2:
        return "image"
    else:
        return "mixed"


# ── 核心：单 PDF → Markdown ─────────────────────────────────

def pdf2md(
    pdf_path: str | Path,
    *,
    engine: str = "auto",
    dpi: int = 150,
    compare: bool = False,
    force: bool = False,
) -> Pdf2MdResult:
    """单 PDF → Markdown。
    
    engine:
      "auto"      — 智能路由（默认）
      "rapidocr"  — 强制 RapidOCR OCR
      "pymupdf"   — 强制 PyMuPDF 直取
      "pdfplumber"— 强制 pdfplumber
      "markitdown"— 强制 MarkItDown
    
    compare: True 时多引擎竞合，取最优结果。
    """
    pdf_path = Path(pdf_path)
    t0 = time.time()
    
    # ── 智能路由 ──
    if engine == "auto":
        pdf_type = _classify_pdf(pdf_path)
        if pdf_type == "text":
            engine = "pymupdf"
        elif pdf_type == "image":
            engine = "rapidocr"
        else:
            engine = "rapidocr"  # mixed 亦以 OCR 为主
        log(f"  路由: {pdf_type}型 → {engine}", "dim")
    
    # ── 单引擎提取 ──
    if not compare:
        pages = _extract_single(pdf_path, engine, dpi=dpi)
    else:
        # 多引擎竞合
        pages = _extract_compare(pdf_path, dpi=dpi)
        engine = "compare"
    
    # ── 统计 ──
    text_pages = sum(1 for p in pages if p.text.strip() and not p.is_image_page)
    image_pages = sum(1 for p in pages if p.is_image_page)
    ocr_pages = sum(1 for p in pages if p.engine == "rapidocr" and p.text.strip())
    total_chars = sum(len(p.text) for p in pages)
    
    # ── 组装 Markdown ──
    md = _assemble_markdown(pdf_path, pages)
    
    elapsed = time.time() - t0
    return Pdf2MdResult(
        pdf_path=str(pdf_path),
        markdown=md,
        pages=pages,
        engine_used=engine,
        total_chars=total_chars,
        elapsed=elapsed,
        page_count=len(pages),
        text_pages=text_pages,
        image_pages=image_pages,
        ocr_pages=ocr_pages,
    )


def _extract_single(pdf_path: Path, engine: str, *, dpi: int = 200) -> list[PageResult]:
    """单引擎提取。"""
    extractors: dict[str, Callable[..., list[PageResult]]] = {
        "pymupdf": lambda: _extract_pymupdf_text(pdf_path),
        "rapidocr": lambda: _extract_rapidocr_pages(pdf_path, dpi=dpi),
        "pdfplumber": lambda: _extract_pdfplumber(pdf_path),
        "markitdown": lambda: _extract_markitdown(pdf_path),
    }
    fn = extractors.get(engine)
    if fn is None:
        log(f"  × 未知引擎: {engine}", "err")
        return []
    pages = fn()
    # RapidOCR 对纯图PDF：补充 PyMuPDF 取嵌入文本（若有）
    if engine == "rapidocr" and _HAS_FITZ:
        doc = fitz.open(str(pdf_path))
        for p in pages:
            if p.index < len(doc):
                embed = doc[p.index].get_text("text") or ""
                if embed.strip() and not p.text.strip():
                    p.text = embed.strip()
                    p.engine = "pymupdf+rapidocr"
                    p.is_image_page = False
        doc.close()
    return pages


def _extract_compare(pdf_path: Path, *, dpi: int = 200) -> list[PageResult]:
    """多引擎竞合——逐页取最优。"""
    all_results: dict[str, list[PageResult]] = {}
    if _HAS_FITZ:
        all_results["pymupdf"] = _extract_pymupdf_text(pdf_path)
    if _HAS_RAPIDOCR and _HAS_FITZ:
        all_results["rapidocr"] = _extract_rapidocr_pages(pdf_path, dpi=dpi)
    if _HAS_PDFPLUMBER:
        all_results["pdfplumber"] = _extract_pdfplumber(pdf_path)
    # MarkItDown 不分页，不参与逐页竞合
    
    # 逐页选最优
    max_pages = max((len(v) for v in all_results.values()), default=0)
    best_pages: list[PageResult] = []
    for i in range(max_pages):
        candidates: list[PageResult] = []
        for eng_name, eng_pages in all_results.items():
            if i < len(eng_pages):
                candidates.append(eng_pages[i])
        if not candidates:
            best_pages.append(PageResult(index=i))
            continue
        # 选文本最长且置信最高者
        best = max(candidates, key=lambda c: (len(c.text.strip()), c.confidence))
        best_pages.append(best)
    return best_pages


def _assemble_markdown(pdf_path: Path, pages: list[PageResult]) -> str:
    """从页结果组装完整 Markdown。
    
    道法：先跨页统计频率检测页眉/页脚，再逐页结构化。
    此为反向审视——单页看不出噪声，跨页方知。
    """
    title = pdf_path.stem
    L: list[str] = []
    L.append(f"# {title}")
    L.append("")
    L.append(f"> 来源: {pdf_path.name}")
    L.append(f"> 页数: {len(pages)}")
    L.append("")
    
    # ── 跨页频率法检测页眉/页脚 ──
    pages_text = [p.text.strip() for p in pages if p.text.strip()]
    noise_set = _detect_headers_footers(pages_text)
    if noise_set:
        log(f"  噪声检测: {len(noise_set)} 行跨页重复→滤除", "dim")
    
    for p in pages:
        if not p.text.strip():
            continue
        # 页分隔
        L.append("---")
        L.append("")
        L.append(f"<!-- page {p.index + 1} -->")
        L.append("")
        # 结构化（带噪声过滤）
        md_text = _text_to_structured_md(p.text.strip(), noise_set=noise_set)
        L.append(md_text)
        L.append("")
    
    return "\n".join(L)


# ── 批量处理 ────────────────────────────────────────────────

def pdf2md_batch(
    input_dir: str | Path,
    *,
    output_dir: str | Path | None = None,
    engine: str = "auto",
    dpi: int = 150,
    compare: bool = False,
    force: bool = False,
    filter_kw: list[str] | None = None,
) -> list[Pdf2MdResult]:
    """批量处理目录下所有 PDF。"""
    input_dir = Path(input_dir)
    if not input_dir.exists():
        log(f"× 输入目录不存: {input_dir}", "err")
        return []
    
    pdfs = sorted(input_dir.rglob("*.pdf"))
    if filter_kw:
        pdfs = [p for p in pdfs if any(kw in p.name for kw in filter_kw)]
    
    if not pdfs:
        log("∅ 无 PDF 可处理", "warn")
        return []
    
    log(f"\n共 {len(pdfs)} 个 PDF 待处理", "info")
    
    results: list[Pdf2MdResult] = []
    for i, pdf in enumerate(pdfs, 1):
        log(f"[{i}/{len(pdfs)}] {pdf.name}", "dim")
        try:
            result = pdf2md(pdf, engine=engine, dpi=dpi, compare=compare, force=force)
            results.append(result)
            
            # 写输出
            if output_dir:
                out = Path(output_dir)
                out.mkdir(parents=True, exist_ok=True)
                md_path = out / f"{pdf.stem}.md"
                md_path.write_text(result.markdown, encoding="utf-8")
                log(f"  ✓ {result.total_chars} 字, {result.engine_used}, {result.elapsed:.1f}s → {md_path.name}", "ok")
            else:
                log(f"  ✓ {result.total_chars} 字, {result.engine_used}, {result.elapsed:.1f}s", "ok")
        except Exception as e:
            log(f"  × 失败: {e}", "err")
    
    return results


# ── 对已有解析目录补 OCR（兼容 pdf_提文.py 之目录结构）───

def ocr_doc_dir(
    doc_dir: str | Path,
    *,
    force: bool = False,
    per_page_md: bool = True,
) -> dict | None:
    """对 pdf_提文.py 已提取之目录（含 page_*.jpg + _doc.json）补 OCR。
    
    道法：复用已有之图，不重复渲染，最小化出力。
    串行执行（实测多线程反而更慢0.67x，因 onnxruntime GIL 锁）。
    per_page_md: 若 True，为每页生成独立 MD（1:1 图文对应）。
    返更新后之 meta dict。
    """
    doc_dir = Path(doc_dir)
    meta_path = doc_dir / "_doc.json"
    meta = read_json(meta_path)
    if not meta or not meta.get("pages"):
        return None
    
    pages = meta["pages"]
    ocr_count = 0
    skip_count = 0
    t0 = time.time()
    
    for p in pages:
        img_name = p.get("image")
        if not img_name:
            continue
        img_path = doc_dir / img_name
        if not img_path.exists():
            continue
        # 增量
        if not force and p.get("ocr_text"):
            skip_count += 1
            continue
        # OCR
        text, score = _ocr_rapidocr(img_path)
        p["ocr_text"] = text if text else None
        p["ocr_score"] = round(score, 3) if score else None
        if text:
            ocr_count += 1
    
    dt = time.time() - t0
    if ocr_count == 0 and skip_count == 0:
        return meta
    
    # 写回 _doc.json
    write_json(meta_path, meta)
    
    # 跨页频率法检测噪声
    pages_text = []
    for p in pages:
        ocr = p.get("ocr_text") or p.get("embedded_text") or ""
        if ocr and ocr.strip():
            pages_text.append(ocr.strip())
    noise_set = _detect_headers_footers(pages_text)
    
    # 生成 _全文.md（带频率法噪声过滤 + 图片引用）
    md_path = doc_dir / "_全文.md"
    md = _build_md_from_meta(meta, noise_set=noise_set)
    md_path.write_text(md, encoding="utf-8")
    
    # 生成每页独立 MD（1:1 图文对应）
    if per_page_md:
        _generate_per_page_md(doc_dir, meta, noise_set=noise_set)
    
    log(
        f"    OCR: {ocr_count} 页识, {skip_count} 页跳, "
        f"全文 → {md_path.name} ({dt:.1f}s)",
        "ok" if ocr_count > 0 else "dim",
    )
    return meta


def _build_md_from_meta(meta: dict, noise_set: set[str] | None = None) -> str:
    """从 _doc.json 构建 _全文.md（1:1 图文对应版）。"""
    pdf_name = meta.get("pdf_name", "?")
    title = meta.get("presentation_title") or meta.get("lesson_title") or pdf_name
    
    L: list[str] = []
    L.append(f"# {title}")
    L.append("")
    L.append(f"> 来源: {pdf_name}")
    L.append(f"> 页数: {len(meta.get('pages', []))}")
    L.append("")
    
    if noise_set:
        log(f"      噪声: {len(noise_set)} 行跨页重复→滤除", "dim")
    
    for p in meta.get("pages", []):
        idx = p.get("index", 0)
        img = p.get("image", "")
        ocr = p.get("ocr_text") or p.get("embedded_text") or ""
        
        L.append("---")
        L.append("")
        L.append(f"<!-- page {idx} -->")
        L.append("")
        
        # 1:1 图文对应：先放图片引用，再放文字
        if img:
            L.append(f"![page {idx}]({img})")
            L.append("")
        
        if ocr and ocr.strip():
            md_text = _text_to_structured_md(ocr.strip(), noise_set=noise_set)
            L.append(md_text)
        elif not img:
            L.append("> *此页无文字*")
        L.append("")
    
    return "\n".join(L)


def _generate_per_page_md(doc_dir: Path, meta: dict, *, noise_set: set[str] | None = None) -> int:
    """为每页生成独立 MD 文件——1:1 图文对应。
    
    道法：每页一图一文，图在上文在下，取之尽锱铢。
    输出：doc_dir/pages/page_NNN.md（含图片引用+结构化文字）
    返生成之文件数。
    """
    pages_dir = doc_dir / "pages"
    pages_dir.mkdir(exist_ok=True)
    
    pdf_name = meta.get("pdf_name", "?")
    title = meta.get("presentation_title") or meta.get("lesson_title") or pdf_name
    n_generated = 0
    
    for p in meta.get("pages", []):
        idx = p.get("index", 0)
        img = p.get("image", "")
        ocr = p.get("ocr_text") or p.get("embedded_text") or ""
        score = p.get("ocr_score")
        
        # 文件名：page_NNN.md
        md_name = f"page_{idx:03d}.md"
        md_path = pages_dir / md_name
        
        L: list[str] = []
        # 标题
        L.append(f"# {title} — 第 {idx} 页")
        L.append("")
        # 元信息
        L.append(f"> 来源: {pdf_name}")
        L.append(f"> 页码: {idx}")
        if score is not None:
            L.append(f"> OCR置信: {score:.1%}")
        L.append("")
        
        # 图片引用（相对路径：从 pages/ 回上级找 page_NNN.jpg）
        if img:
            L.append(f"![page {idx}](../{img})")
            L.append("")
        
        # OCR 文字（结构化 + 噪声过滤）
        if ocr and ocr.strip():
            md_text = _text_to_structured_md(ocr.strip(), noise_set=noise_set)
            L.append(md_text)
        elif not img:
            L.append("> *此页无文字*")
        L.append("")
        
        md_path.write_text("\n".join(L), encoding="utf-8")
        n_generated += 1
    
    if n_generated:
        log(f"      1:1图文: {n_generated} 页 → pages/page_NNN.md", "dim")
    return n_generated


# ── 命令行入口 ──────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="PDF → Markdown 统一引擎  ——  道法自然",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("input", help="输入 PDF 文件或目录")
    parser.add_argument("-o", "--output", help="输出 MD 文件或目录")
    parser.add_argument(
        "--engine", default="auto",
        choices=["auto", "rapidocr", "pymupdf", "pdfplumber", "markitdown"],
        help="提取引擎（默 auto 智能路由）",
    )
    parser.add_argument("--dpi", type=int, default=150, help="OCR 渲染 DPI（默 150）")
    parser.add_argument("--compare", action="store_true", help="多引擎竞合，取最优")
    parser.add_argument("--force", action="store_true", help="忽略已有结果")
    parser.add_argument("--filter", "-f", action="append", help="文件名关键字过滤")
    args = parser.parse_args()
    
    header("PDF → Markdown  ——  道法自然，无为而无不为", width=60)
    
    # 引擎状态
    log("  引擎状态:", "dim")
    log(f"    PyMuPDF:     {'✓' if _HAS_FITZ else '✗'}", "ok" if _HAS_FITZ else "warn")
    log(f"    RapidOCR:    {'✓' if _HAS_RAPIDOCR else '✗'}", "ok" if _HAS_RAPIDOCR else "warn")
    log(f"    pdfplumber:  {'✓' if _HAS_PDFPLUMBER else '✗'}", "ok" if _HAS_PDFPLUMBER else "warn")
    log(f"    MarkItDown:  {'✓' if _HAS_MARKITDOWN else '✗'}", "ok" if _HAS_MARKITDOWN else "warn")
    
    inp = Path(args.input)
    if inp.is_file():
        # 单文件
        result = pdf2md(inp, engine=args.engine, dpi=args.dpi, compare=args.compare)
        if args.output:
            out = Path(args.output)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(result.markdown, encoding="utf-8")
            log(f"  ✓ → {out} ({result.total_chars} 字, {result.elapsed:.1f}s)", "ok")
        else:
            print(result.markdown)
    elif inp.is_dir():
        # 批量
        results = pdf2md_batch(
            inp,
            output_dir=args.output,
            engine=args.engine,
            dpi=args.dpi,
            compare=args.compare,
            force=args.force,
            filter_kw=args.filter,
        )
        total_chars = sum(r.total_chars for r in results)
        total_time = sum(r.elapsed for r in results)
        header(f"毕  ——  {len(results)} PDF, {total_chars} 字, {total_time:.1f}s", width=60)
    else:
        log(f"× 输入不存: {inp}", "err")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n知止所以不殆。", "warn")
        sys.exit(130)
