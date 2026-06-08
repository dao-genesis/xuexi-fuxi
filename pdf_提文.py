# -*- coding: utf-8 -*-
"""
PDF 提文 (pdf_extract)  ——  其安也，易持也

道法自然：
    雨课堂之 PDF 本由 JPEG 图像合成——纯图无字。
    故须二步：先取其内嵌原图（page_NNN.jpg），再以 OCR 识其文字。
    辅以 _doc.json 之元数据（章节信号、课时序号、标题、每页 OCR 文字），
    则后续聚合、汇编皆有所凭。
    OCR 既成，更生 _全文.md——一 PDF 之全文 Markdown，
    章节标题自 OCR 结果中识别，结构自现。

依赖：
    pip install pymupdf pillow rapidocr-onnxruntime

用法：
    python pdf_提文.py                       # 处理 ./雨课堂PDF（仅取图）
    python pdf_提文.py --ocr                  # 取图 + OCR 识文 + 生 MD
    python pdf_提文.py --ocr-only             # 仅 OCR（图已取，补识文）
    python pdf_提文.py --input <目录>        # 自定输入
    python pdf_提文.py --output <目录>       # 自定输出（默 ./解析仓库）
    python pdf_提文.py --filter "环境毒理"   # 仅处理含此关键字之课程
    python pdf_提文.py --force               # 重处已存在
    python pdf_提文.py --dpi 200             # 渲染兜底之 dpi（默 150）

输出布局：
    解析仓库/
    ├── _index.json                              # 全局索引
    └── 环境毒理学-2026春-.../
        ├── _course.json                         # 课程级索引
        └── 004-3环境毒理学 第三章-3环境毒理学 第三章/
            ├── _doc.json                        # 含 ocr_text 字段
            ├── _全文.md                          # OCR 全文 Markdown
            ├── page_001.jpg
            ├── page_002.jpg
            └── ...
"""

from __future__ import annotations

import argparse
import re
import sys
import time
import traceback
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("缺 PyMuPDF。请运行: pip install pymupdf", file=sys.stderr)
    sys.exit(1)

try:
    from rapidocr_onnxruntime import RapidOCR
    _OCR_ENGINE = RapidOCR()
except ImportError:
    _OCR_ENGINE = None
except Exception:
    _OCR_ENGINE = None

# 统一引擎（增强版 OCR + 智能路由）
try:
    from pdf2md_引擎 import ocr_doc_dir as _ocr_doc_dir_v2, pdf2md as _pdf2md_v2  # noqa: E402
    _HAS_V2_ENGINE = True
except ImportError:
    _HAS_V2_ENGINE = False

# 共用之器
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _yc_common import (  # noqa: E402
    log,
    header,
    sanitize_filename,
    detect_chapter,
    detect_all_chapters,
    parse_pdf_filename,
    parse_course_dirname,
    write_json,
    read_json,
)
from _ocr_clean import clean_ocr_text  # noqa: E402


# ============================================================
# 章节信号·从 PDF 名/标题计算
# ============================================================

def compute_chapter_signals(name_info: dict) -> dict:
    """从 lesson_title / presentation_title 算章节信号。

    规则：
      - 主章号：优先 presentation_title 之首章；若无，再用 lesson_title 之首章
      - 全部章号：lesson_title ∪ presentation_title 中所有章号去重
    """
    lesson = name_info.get("lesson_title", "") or ""
    pres = name_info.get("presentation_title", "") or ""

    chap_num, chap_raw = detect_chapter(pres)
    if chap_num is None:
        chap_num, chap_raw = detect_chapter(lesson)

    all_chs: list[tuple[int, str]] = []
    seen: set[int] = set()
    for src in (pres, lesson):
        for n, raw in detect_all_chapters(src):
            if n not in seen:
                seen.add(n)
                all_chs.append((n, raw))
    all_chs.sort(key=lambda x: x[0])

    return {
        "chapter_num": chap_num,
        "chapter_raw": chap_raw,
        "all_chapter_nums": [n for n, _ in all_chs],
        "all_chapter_raws": [r for _, r in all_chs],
    }


# ============================================================
# PDF → 图像 + 元数据
# ============================================================

def extract_pdf_pages(
    pdf_path: Path,
    out_dir: Path,
    *,
    dpi_fallback: int = 150,
    force: bool = False,
) -> dict:
    """提一 PDF 之所有页为 jpg/png，并写 _doc.json。

    返回该 PDF 之元数据 dict（已写入磁盘）。
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    meta_path = out_dir / "_doc.json"

    # 增量：若 _doc.json 已存且未强制，复用之
    if meta_path.exists() and not force:
        old = read_json(meta_path)
        if old and old.get("page_count", 0) > 0:
            # 检查主图 + 子图是否都还在
            pages = old.get("pages", [])
            all_present = all(
                (out_dir / p["image"]).exists() for p in pages if p.get("image")
            )
            if all_present:
                figs_ok = all(
                    (out_dir / f["image"]).exists()
                    for p in pages
                    for f in (p.get("figures") or [])
                    if f.get("image")
                )
                if figs_ok:
                    return old

    # 文件名信号
    name_info = parse_pdf_filename(pdf_path.name)
    lesson_title = name_info.get("lesson_title", "")
    pres_title = name_info.get("presentation_title", "")
    # 章节信号
    chap_sig = compute_chapter_signals(name_info)

    pages: list[dict] = []

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        log(f"  × 不可开: {pdf_path.name}: {e}", "err")
        return {
            "pdf_path": str(pdf_path),
            "pdf_name": pdf_path.name,
            "error": str(e),
            "page_count": 0,
            "pages": [],
        }

    page_count = len(doc)

    for i, page in enumerate(doc, start=1):
        # 策略 A：直取嵌入原图
        saved_path: Path | None = None
        ext = "jpg"
        page_figures: list[dict] = []   # 本页内嵌子图（多图时提取）

        try:
            imgs = page.get_images(full=False)

            if len(imgs) == 1:
                # 单图：整页即此图（原有逻辑·最常见情形）
                xref = imgs[0][0]
                pix_info = doc.extract_image(xref)
                if pix_info and pix_info.get("image"):
                    raw_ext = pix_info.get("ext", "jpeg")
                    ext = "jpg" if raw_ext in ("jpeg", "jpg") else raw_ext
                    saved_path = out_dir / f"page_{i:03d}.{ext}"
                    if not saved_path.exists() or force:
                        saved_path.write_bytes(pix_info["image"])

            elif len(imgs) > 1:
                # 多图：此页含嵌入图表/图片 → 提取各子图 + 渲染整页主图
                # 道法：先渲染整页作主图（Strategy B 先触发）
                # 然后逐一提取每张子图，存为 page_NNN_fig_MM.ext
                for fig_idx, img_info in enumerate(imgs, 1):
                    xref = img_info[0]
                    try:
                        pix_info = doc.extract_image(xref)
                        if pix_info and pix_info.get("image"):
                            raw_ext = pix_info.get("ext", "jpeg")
                            fig_ext = "jpg" if raw_ext in ("jpeg", "jpg") else raw_ext
                            fig_name = f"page_{i:03d}_fig_{fig_idx:02d}.{fig_ext}"
                            fig_path = out_dir / fig_name
                            if not fig_path.exists() or force:
                                fig_path.write_bytes(pix_info["image"])
                            # 图像尺寸（img_info tuple: xref,smask,w,h,bpc,...）
                            img_w = img_info[2] if len(img_info) > 2 else 0
                            img_h = img_info[3] if len(img_info) > 3 else 0
                            # 过滤极微图（< 64×64，多为装饰/图标）
                            if img_w * img_h >= 64 * 64:
                                page_figures.append({
                                    "index": fig_idx,
                                    "image": fig_name,
                                    "w": img_w,
                                    "h": img_h,
                                })
                    except Exception:
                        pass

        except Exception:
            saved_path = None

        # 策略 B：渲染兜底（单图提取失败 或 多图页作主图）
        if not saved_path or not saved_path.exists():
            try:
                pix = page.get_pixmap(dpi=dpi_fallback)
                ext = "png"
                saved_path = out_dir / f"page_{i:03d}.{ext}"
                if not saved_path.exists() or force:
                    pix.save(str(saved_path))
            except Exception as e:
                log(f"    × 第 {i} 页渲染败: {e}", "warn")
                continue

        # 嵌入文本（如有；雨课堂 PDF 多为 null，后由 LLM 道喂协填）
        try:
            embedded_text = page.get_text("text") or ""
        except Exception:
            embedded_text = ""

        page_record: dict = {
            "index": i,
            "image": saved_path.name,
            "embedded_text": embedded_text.strip() or None,
        }
        if page_figures:
            page_record["figures"] = page_figures
            log(
                f"    ↳ 第 {i} 页提取 {len(page_figures)} 子图",
                "dim",
            )
        pages.append(page_record)

    doc.close()

    meta = {
        "pdf_path": str(pdf_path),
        "pdf_name": pdf_path.name,
        "lesson_seq": name_info.get("seq"),
        "lesson_title": lesson_title,
        "presentation_title": pres_title,
        **chap_sig,  # chapter_num, chapter_raw, all_chapter_nums, all_chapter_raws
        "page_count": page_count,
        "pages": pages,
    }
    write_json(meta_path, meta)
    return meta


# ============================================================
# OCR · 以图识文
# ============================================================

def _ocr_image(image_path: Path) -> list[dict]:
    """OCR 单图，返 [{"bbox": [...], "text": str, "score": float}, ...]

    按 y 坐标排序（上→下），同行按 x 排序（左→右）。
    """
    global _OCR_ENGINE
    if _OCR_ENGINE is None:
        return []
    try:
        result, _elapse = _OCR_ENGINE(str(image_path))
    except Exception as e:
        log(f"    × OCR 败: {image_path.name}: {e}", "warn")
        # 重初始化引擎（onnxruntime 偶发内部错误后需重建）
        try:
            from rapidocr_onnxruntime import RapidOCR
            _OCR_ENGINE = RapidOCR()
        except Exception:
            pass
        return []
    if not result:
        return []
    # result: [[bbox, text, score], ...]
    lines: list[dict] = []
    for bbox, text, score in result:
        # bbox: [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
        y_top = bbox[0][1] if bbox else 0
        x_left = bbox[0][0] if bbox else 0
        lines.append({
            "bbox": bbox,
            "text": text,
            "score": score,
            "y_top": y_top,
            "x_left": x_left,
        })
    # 按 y 排序（上→下）；y 近者按 x（左→右）
    lines.sort(key=lambda l: (round(l["y_top"] / 10), l["x_left"]))
    return lines


# 水印关键词（雨课堂课件常见校名水印）
_WATERMARK_RE = re.compile(
    r"^(新[蓬雄建疆]?大学|Xinj?iang\s*University|ngUnn?versit[ys]|Unn?versiry|Unn?versity)$",
    re.IGNORECASE,
)


def _is_watermark(text: str) -> bool:
    """判 OCR 行是否为水印（校名、重复装饰文字）。"""
    t = text.strip()
    if not t:
        return False
    if _WATERMARK_RE.match(t):
        return True
    # 极短低置信行（<4字、含乱码）
    if len(t) <= 3 and not re.match(r"^[\u4e00-\u9fff]+$", t):
        return True
    return False


# 行尾水印清理（如 "1.1环境毒理学及其发展 新建大学"）
_TRAILING_WATERMARK_RE = re.compile(
    r"\s+(新[蓬雄建疆]?大学|Xinj?iang\s*University|ngUnn?versit[ys]|Unn?versiry|Unn?versity)\s*$",
    re.IGNORECASE,
)


def _strip_trailing_watermark(text: str) -> str:
    """清理行尾水印片段。"""
    return _TRAILING_WATERMARK_RE.sub("", text).strip()


def _ocr_lines_to_text(lines: list[dict]) -> str:
    """OCR 行列表 → 纯文本。合并 y 近者为一行。过滤水印。"""
    if not lines:
        return ""
    # 分组：y 差 < 15 视为同行
    row_groups: list[list[dict]] = []
    current_row: list[dict] = [lines[0]]
    for ln in lines[1:]:
        if abs(ln["y_top"] - current_row[0]["y_top"]) < 15:
            current_row.append(ln)
        else:
            row_groups.append(current_row)
            current_row = [ln]
    row_groups.append(current_row)

    text_lines: list[str] = []
    for row in row_groups:
        row.sort(key=lambda l: l["x_left"])
        # 过滤水印行
        parts = [l["text"] for l in row if not _is_watermark(l["text"])]
        if not parts:
            continue
        text_lines.append(_strip_trailing_watermark(" ".join(parts)))
    return "\n".join(text_lines)


def _is_heading(text: str, score: float) -> str | None:
    """判 OCR 行是否为标题。返标题级别（'##' / '###' / '####'）或 None。
    
    道法：
      - 章标题："第X章..." 或 "第一章..."
      - 节标题："1.1 ..." / "1.2.3 ..." 等编号开头
      - 短高置信行（≤20字、score≥0.95）亦可为小标题
    """
    t = text.strip()
    if not t:
        return None
    # 章标题
    if re.match(r"^(第[一二三四五六七八九十百]+章|第\d+章)", t):
        return "##"
    # 节标题：数字编号（1.1 / 1.2.3 等，编号后可无空格）
    if re.match(r"^(\d+\.\d+(\.\d+)?)[\s\.．]", t) or re.match(r"^(\d+\.\d+(\.\d+)?)[\u4e00-\u9fff]", t):
        return "###"
    # 短高置信行 → 小标题
    if len(t) <= 20 and score >= 0.95 and not t.endswith(("。", "，", "；", "：", "、", ",", ".", ";")):
        return "####"
    return None


def _ocr_lines_to_markdown(lines: list[dict]) -> str:
    """OCR 行列表 → 结构化 Markdown。"""
    if not lines:
        return ""
    row_groups: list[list[dict]] = []
    current_row: list[dict] = [lines[0]]
    for ln in lines[1:]:
        if abs(ln["y_top"] - current_row[0]["y_top"]) < 15:
            current_row.append(ln)
        else:
            row_groups.append(current_row)
            current_row = [ln]
    row_groups.append(current_row)

    md_lines: list[str] = []
    for row in row_groups:
        row.sort(key=lambda l: l["x_left"])
        text = " ".join(l["text"] for l in row).strip()
        if not text:
            continue
        avg_score = sum(l["score"] for l in row) / len(row)
        heading = _is_heading(text, avg_score)
        if heading:
            md_lines.append("")  # 标题前空行
            md_lines.append(f"{heading} {text}")
        else:
            md_lines.append(text)
    return "\n".join(md_lines)


def ocr_document(
    doc_dir: Path,
    *,
    force: bool = False,
    use_v2: bool = True,
) -> dict | None:
    """对一 PDF 解析目录下所有页图执行 OCR，更新 _doc.json 并生 _全文.md。
    
    增量：已有 ocr_text 之页跳过（除非 force）。
    use_v2: 若 True 且 pdf2md_引擎 可用，则用增强引擎（噪声过滤+结构优化）。
    返更新后之 meta dict，或 None（无页可 OCR）。
    """
    # 优先使用 V2 引擎（噪声过滤 + 结构化更优）
    if use_v2 and _HAS_V2_ENGINE:
        return _ocr_doc_dir_v2(doc_dir, force=force)
    
    if _OCR_ENGINE is None:
        log("  × 无 OCR 引擎（需 rapidocr-onnxruntime）", "err")
        return None

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
        lines = _ocr_image(img_path)
        raw_text = _ocr_lines_to_text(lines) if lines else ""
        p["ocr_text"] = clean_ocr_text(raw_text) or None
        p["ocr_lines_count"] = len(lines)
        ocr_count += 1

    dt = time.time() - t0
    if ocr_count == 0 and skip_count == 0:
        return meta

    # 写回 _doc.json
    write_json(meta_path, meta)

    # 生成 _全文.md
    md_path = doc_dir / "_全文.md"
    md = _build_full_markdown(meta)
    md_path.write_text(md, encoding="utf-8")

    log(
        f"    OCR: {ocr_count} 页识, {skip_count} 页跳, "
        f"全文 → {md_path.name} ({dt:.1f}s)",
        "ok" if ocr_count > 0 else "dim",
    )
    return meta


def _build_full_markdown(meta: dict) -> str:
    """从 _doc.json 之 pages 构建 _全文.md。"""
    pdf_name = meta.get("pdf_name", "?")
    lesson_title = meta.get("lesson_title", "")
    pres_title = meta.get("presentation_title", "")
    title = pres_title or lesson_title or pdf_name

    L: list[str] = []
    L.append(f"# {title}")
    L.append("")
    L.append(f"> 来源: {pdf_name}")
    if lesson_title and lesson_title != title:
        L.append(f"> 课时: {lesson_title}")
    L.append("")

    for p in meta.get("pages", []):
        idx = p.get("index", 0)
        img = p.get("image", "")
        ocr = p.get("ocr_text") or p.get("embedded_text") or ""

        # 页分隔
        L.append(f"---")
        L.append("")
        L.append(f"<!-- page {idx} -->")
        L.append("")

        if ocr and ocr.strip():
            md_text = _simple_text_to_md(ocr.strip())
            L.append(md_text)
        else:
            L.append(f"![page {idx}]({img})")
            L.append("")
            L.append("> *此页无文字*")
        L.append("")

    return "\n".join(L)


def _simple_text_to_md(text: str) -> str:
    """纯 OCR 文本 → 简单 Markdown（识别章节/节标题）。
    
    道法：ocr_text 已由 _ocr_clean.py 清洗，此处不再重复过滤水印。
    """
    lines = text.split("\n")
    md_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            md_lines.append("")
            continue
        # 章标题
        if re.match(r"^(第[一二三四五六七八九十百]+章|第\d+章)", stripped):
            md_lines.append("")
            md_lines.append(f"## {stripped}")
            continue
        # 节标题
        if re.match(r"^(\d+\.\d+(\.\d+)?)[\s\.．]", stripped) or re.match(r"^(\d+\.\d+(\.\d+)?)[\u4e00-\u9fff]", stripped):
            md_lines.append("")
            md_lines.append(f"### {stripped}")
            continue
        md_lines.append(stripped)
    return "\n".join(md_lines)


def ocr_course(
    course_out_dir: Path,
    *,
    force: bool = False,
    use_v2: bool = True,
) -> dict:
    """对一门课程下所有已解析 PDF 目录执行 OCR。"""
    doc_dirs = sorted(
        d for d in course_out_dir.iterdir()
        if d.is_dir() and (d / "_doc.json").exists()
    )
    if not doc_dirs:
        log(f"  ∅ 无可 OCR 之解析目录", "dim")
        return {"ocr_count": 0, "skip_count": 0, "fail_count": 0}

    total_ocr = 0
    total_skip = 0
    total_fail = 0
    for d in doc_dirs:
        try:
            result = ocr_document(d, force=force, use_v2=use_v2)
            if result:
                pages = result.get("pages", [])
                total_ocr += sum(1 for p in pages if p.get("ocr_text"))
                total_skip += sum(1 for p in pages if not p.get("ocr_text") and p.get("image"))
            else:
                total_fail += 1
        except Exception as e:
            log(f"  × OCR 败: {d.name}: {e}", "err")
            total_fail += 1

    return {
        "ocr_count": total_ocr,
        "skip_count": total_skip,
        "fail_count": total_fail,
    }


# ============================================================
# 课程批处理
# ============================================================

def rescan_doc_chapters(meta_path: Path) -> dict | None:
    """仅重新计算 _doc.json 中之章节信号字段（不动图像）。"""
    old = read_json(meta_path)
    if not old:
        return None
    name_info = parse_pdf_filename(old.get("pdf_name", ""))
    # 用元数据已存的标题（更稳）
    name_info["lesson_title"] = old.get("lesson_title") or name_info.get("lesson_title", "")
    name_info["presentation_title"] = (
        old.get("presentation_title") or name_info.get("presentation_title", "")
    )
    chap_sig = compute_chapter_signals(name_info)
    old.update(chap_sig)
    write_json(meta_path, old)
    return old


def process_course(
    course_dir: Path,
    out_root: Path,
    *,
    dpi_fallback: int = 150,
    force: bool = False,
    rescan_only: bool = False,
    do_ocr: bool = False,
    ocr_only: bool = False,
    use_v2: bool = True,
) -> dict:
    """处理一门课程目录之下所有 PDF。"""
    course_info = parse_course_dirname(course_dir.name)
    out_course = out_root / course_dir.name
    out_course.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(course_dir.glob("*.pdf"))
    if not pdf_files:
        log(f"  ∅ 空: {course_dir.name}", "dim")
        return {
            "course_dir": course_dir.name,
            **course_info,
            "pdf_count": 0,
            "documents": [],
        }

    mode_desc = "OCR补识" if ocr_only else ("取图+OCR" if do_ocr else "取图")
    log(f"\n┌── 课程: {course_info['course_name']} ({course_info['teacher']}) [{mode_desc}]", "title")
    log(f"│   {len(pdf_files)} 个 PDF", "info")
    log(f"└── → {out_course}", "dim")

    docs = []
    skipped = 0
    processed = 0
    rescanned = 0
    failed = 0

    # OCR-only 模式：不取图，仅对已有解析目录补 OCR
    if ocr_only:
        ocr_stat = ocr_course(out_course, force=force, use_v2=use_v2)
        log(f"  └ OCR: {ocr_stat['ocr_count']} 页识, {ocr_stat['skip_count']} 跳, {ocr_stat['fail_count']} 败", "info")
        return {
            "course_dir": course_dir.name,
            **course_info,
            "pdf_count": len(pdf_files),
            "processed": 0,
            "rescanned": 0,
            "skipped": 0,
            "failed": 0,
            "ocr_pages": ocr_stat["ocr_count"],
        }

    for pdf in pdf_files:
        out_dir = out_course / sanitize_filename(pdf.stem, max_len=120)
        meta_path = out_dir / "_doc.json"

        # 仅重扫章节
        if rescan_only:
            if meta_path.exists():
                meta = rescan_doc_chapters(meta_path)
                if meta:
                    docs.append(meta)
                    rescanned += 1
                    continue
            # 否则正常处理
        # 增量判断
        elif meta_path.exists() and not force:
            old = read_json(meta_path)
            if old and old.get("page_count", 0) > 0:
                pages = old.get("pages", [])
                if all((out_dir / p["image"]).exists() for p in pages if p.get("image")):
                    skipped += 1
                    docs.append(old)
                    continue

        try:
            t0 = time.time()
            meta = extract_pdf_pages(
                pdf, out_dir,
                dpi_fallback=dpi_fallback, force=force,
            )
            dt = time.time() - t0
            chap = (
                f"第{meta['chapter_num']}章" if meta.get('chapter_num') is not None
                else "无章号"
            )
            log(
                f"  ✓ {pdf.name[:60]:60s} "
                f"({meta['page_count']:3d}页, {chap}, {dt:.1f}s)",
                "ok",
            )
            docs.append(meta)
            processed += 1

            # 取图后即 OCR（若启）
            if do_ocr and _OCR_ENGINE is not None:
                ocr_document(out_dir, force=force, use_v2=use_v2)
        except Exception as e:
            log(f"  × {pdf.name}: {e}", "err")
            traceback.print_exc()
            failed += 1

    course_meta = {
        "course_dir": course_dir.name,
        **course_info,
        "pdf_count": len(pdf_files),
        "processed": processed,
        "rescanned": rescanned,
        "skipped": skipped,
        "failed": failed,
        "documents": [
            {
                "pdf_name": d.get("pdf_name"),
                "lesson_seq": d.get("lesson_seq"),
                "lesson_title": d.get("lesson_title"),
                "presentation_title": d.get("presentation_title"),
                "chapter_num": d.get("chapter_num"),
                "chapter_raw": d.get("chapter_raw"),
                "all_chapter_nums": d.get("all_chapter_nums", []),
                "all_chapter_raws": d.get("all_chapter_raws", []),
                "page_count": d.get("page_count"),
                "rel_dir": sanitize_filename(Path(d.get("pdf_name", "")).stem, max_len=120),
            }
            for d in docs
        ],
    }
    write_json(out_course / "_course.json", course_meta)

    if rescan_only:
        log(f"  └ 重扫 {rescanned}, 失 {failed}", "info")
    else:
        log(f"  └ 处 {processed}, 跳 {skipped}, 失 {failed}", "info")
    return course_meta


# ============================================================
# 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="PDF 提文 —— 直取雨课堂 PDF 内嵌原图",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--input", "-i", default="雨课堂PDF",
        help="输入根目录（雨课堂下载目录，默 ./雨课堂PDF）",
    )
    parser.add_argument(
        "--output", "-o", default="解析仓库",
        help="输出根目录（默 ./解析仓库）",
    )
    parser.add_argument(
        "--filter", "-f", action="append", default=None,
        help="课程名关键字过滤（可多次）",
    )
    parser.add_argument(
        "--dpi", type=int, default=150,
        help="渲染兜底 DPI（默 150；嵌入原图不受此影响）",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="忽略已有结果，强制重处理",
    )
    parser.add_argument(
        "--rescan", action="store_true",
        help="仅重扫章节信号字段（不动图像，速极快）",
    )
    parser.add_argument(
        "--list-only", "-l", action="store_true",
        help="仅列出课程，不处理",
    )
    parser.add_argument(
        "--ocr", action="store_true",
        help="取图后执行 OCR 识文 + 生成 _全文.md",
    )
    parser.add_argument(
        "--ocr-only", action="store_true",
        help="仅 OCR（图已取，补识文），不重取图",
    )
    parser.add_argument(
        "--engine", default="v2",
        choices=["v2", "v1"],
        help="OCR 引擎版本：v2=统一引擎(默), v1=旧RapidOCR",
    )
    args = parser.parse_args()

    # 路径解析
    script_dir = Path(__file__).resolve().parent
    in_root = Path(args.input)
    if not in_root.is_absolute():
        in_root = script_dir / in_root
    out_root = Path(args.output)
    if not out_root.is_absolute():
        out_root = script_dir / out_root

    header("PDF 提文  ——  其安也，易持也", width=58)
    log(f"  输入: {in_root}", "dim")
    log(f"  输出: {out_root}", "dim")
    use_v2 = args.engine == "v2" and _HAS_V2_ENGINE
    if use_v2:
        log(f"  引擎: V2 统一引擎（噪声过滤+结构优化）", "ok")
    else:
        log(f"  引擎: V1 原始 RapidOCR", "dim")

    if not in_root.exists():
        log(f"× 输入目录不存: {in_root}", "err")
        sys.exit(1)

    courses = sorted([d for d in in_root.iterdir() if d.is_dir()])
    if args.filter:
        courses = [
            c for c in courses
            if any(kw in c.name for kw in args.filter)
        ]

    if not courses:
        log("∅ 无可处理之课程目录", "warn")
        sys.exit(0)

    log(f"\n共 {len(courses)} 门课程目录", "info")
    for i, c in enumerate(courses, 1):
        info = parse_course_dirname(c.name)
        log(f"  [{i:2d}] {info['course_name']} | {info['semester']} | {info['teacher']}", "dim")

    if args.list_only:
        return

    out_root.mkdir(parents=True, exist_ok=True)

    # 处理
    all_courses_meta = []
    grand_pdfs = 0
    grand_pages = 0

    for course_dir in courses:
        try:
            meta = process_course(
                course_dir, out_root,
                dpi_fallback=args.dpi, force=args.force,
                rescan_only=args.rescan,
                do_ocr=args.ocr,
                ocr_only=args.ocr_only,
                use_v2=use_v2,
            )
            all_courses_meta.append(meta)
            grand_pdfs += meta.get("pdf_count", 0)
            grand_pages += sum(
                d.get("page_count", 0) for d in meta.get("documents", [])
            )
        except KeyboardInterrupt:
            log("\n中止矣。", "warn")
            break
        except Exception as e:
            log(f"× 课程失: {course_dir.name}: {e}", "err")
            traceback.print_exc()

    # 全局索引
    index = {
        "input_root": str(in_root),
        "output_root": str(out_root),
        "course_count": len(all_courses_meta),
        "pdf_total": grand_pdfs,
        "page_total": grand_pages,
        "courses": [
            {
                "course_dir": m["course_dir"],
                "course_name": m.get("course_name"),
                "semester": m.get("semester"),
                "teacher": m.get("teacher"),
                "pdf_count": m.get("pdf_count", 0),
                "page_count": sum(
                    d.get("page_count", 0) for d in m.get("documents", [])
                ),
                # 章节摘要：set of detected chapters
                "chapters_detected": sorted(set(
                    d["chapter_num"] for d in m.get("documents", [])
                    if d.get("chapter_num") is not None
                )),
            }
            for m in all_courses_meta
        ],
    }
    write_json(out_root / "_index.json", index)

    header(f"提文毕  ——  课 {len(all_courses_meta)}, PDF {grand_pdfs}, 页 {grand_pages}", width=58)
    log(f"  全局索引: {out_root / '_index.json'}", "ok")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n知止所以不殆。退也。", "warn")
        sys.exit(130)
