# -*- coding: utf-8 -*-
"""
extractors —— 多面提取器：PDF / 视频 / 习题

PDF：幻灯图 → 合成 PDF
Video：取真实 URL + 字幕 → 下载
Exam：取问题 + 答案（含字体反混淆，未来可加）
"""
from __future__ import annotations
import io
import os
import re
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Callable, Dict
import requests

from .core import sanitize_filename, log


# ============================================================
# PDF 提取
# ============================================================
class PDFExtractor:
    """幻灯片 → PDF

    流程：
        course → lessons → presentations → slides (cover urls) → 下载 → 合成 PDF
    支持：跳过已存、并发下载、统一索引。
    """

    def __init__(self, client, output_root: Optional[str] = None,
                 workers: int = 8, verbose: bool = True):
        from . import YuketangClient  # type: ignore
        self.client = client  # YuketangClient
        self.output_root = Path(output_root or "雨课堂PDF").resolve()
        self.workers = workers
        self.verbose = verbose
        self.output_root.mkdir(parents=True, exist_ok=True)

    def _slide_image_url(self, slide: dict) -> Optional[str]:
        """从一 slide 字典中取图片 URL"""
        for k in ("cover", "Thumbnail", "thumbnail", "ThumbnailUrl",
                  "image", "Image", "src", "Src"):
            v = slide.get(k)
            if v and isinstance(v, str) and v.startswith("http"):
                return v
        return None

    def _download_image(self, url: str, retries: int = 3) -> Optional[bytes]:
        for _ in range(retries):
            try:
                r = requests.get(url, timeout=30)
                if r.status_code == 200 and r.content:
                    return r.content
            except Exception:
                pass
            time.sleep(0.5)
        return None

    def _images_to_pdf(self, images: List[bytes], out_path: Path) -> bool:
        """图列 → PDF 文件"""
        if not images:
            return False
        try:
            from PIL import Image
        except ImportError:
            log("  请装 pillow: pip install pillow", "warn")
            return False

        pil_images = []
        for img_bytes in images:
            try:
                img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                pil_images.append(img)
            except Exception:
                pass
        if not pil_images:
            return False

        try:
            pil_images[0].save(
                str(out_path),
                save_all=True,
                append_images=pil_images[1:],
                format="PDF",
            )
            return True
        except Exception as e:
            log(f"    PDF 合成异: {e}", "warn")
            return False

    def download_lesson(self, course_folder: Path, lesson: dict,
                        classroom_id: int) -> int:
        """下载一 lesson 之全部 PDF（每个 presentation 一个 PDF）

        返回成功生成之 PDF 数。

        重要：activities 之实 lesson_id 在 'courseware_id' 字段，非 'id'!
        """
        # 优先 courseware_id（v2 activity 之真 lesson_id），后试他名
        lesson_id = (lesson.get("courseware_id")
                     or lesson.get("lesson_id")
                     or lesson.get("id"))
        lesson_name = (lesson.get("title")
                       or lesson.get("name")
                       or f"lesson_{lesson_id}")
        lesson_type = lesson.get("type")

        if not lesson_id:
            return 0

        # 跳过无 PPT 类型（MOOC 课时、通知等）
        if lesson_type in (15, 17, 6, 9):
            return 0

        # 取课件
        slides_groups = self.client.slides_api.get_slides_for_lesson(
            lesson_id, classroom_id
        )
        if not slides_groups:
            return 0

        # 编号前缀（让排序更直观）
        order = lesson.get("order")
        prefix = f"{order:03d}" if isinstance(order, int) else f"{lesson_id}"

        count = 0
        for group in slides_groups:
            pname = sanitize_filename(group.get("presentation_name", ""), max_len=60)
            slides = group.get("slides", [])
            if not slides:
                continue

            out_name = f"{prefix}-{sanitize_filename(lesson_name, 40)}-{pname}.pdf"
            out_name = sanitize_filename(out_name, max_len=180)
            out_path = course_folder / out_name

            if out_path.exists() and out_path.stat().st_size > 1024:
                if self.verbose:
                    log(f"    ✓ 已存，跳: {out_name}", "dim")
                count += 1
                continue

            if self.verbose:
                log(f"    → 取: {lesson_name} - {pname}", "info")
                log(f"      下载 {len(slides)} 张幻灯片...", "dim")

            # 并发下图
            urls = [self._slide_image_url(s) for s in slides]
            urls = [u for u in urls if u]
            if not urls:
                continue

            images = [None] * len(urls)
            with ThreadPoolExecutor(max_workers=self.workers) as ex:
                futs = {ex.submit(self._download_image, u): i for i, u in enumerate(urls)}
                for f in as_completed(futs):
                    idx = futs[f]
                    images[idx] = f.result()

            valid = [b for b in images if b]
            if not valid:
                if self.verbose:
                    log(f"      × 全部图失", "warn")
                continue

            if self._images_to_pdf(valid, out_path):
                count += 1
                if self.verbose:
                    log(f"    ✓ 生: {out_name} ({len(valid)} 页)", "ok")
            else:
                if self.verbose:
                    log(f"    × PDF 合成失: {out_name}", "warn")

        return count

    def download_course(self, course: dict) -> Dict[str, int]:
        """下载一 course 之全部 PDF。返回统计。"""
        cn = sanitize_filename(course.get("course", {}).get("name", "")
                               or course.get("course_name", "无名"))
        cls = sanitize_filename(course.get("name", ""))
        tea = sanitize_filename(course.get("teacher", {}).get("name", "")
                                or course.get("teacher_name", ""))
        folder_name = sanitize_filename(f"{cn}-{cls}-{tea}".strip("-"), max_len=140)
        course_folder = self.output_root / folder_name
        course_folder.mkdir(parents=True, exist_ok=True)

        classroom_id = course.get("classroom_id")
        if not classroom_id:
            return {"pdfs": 0, "lessons": 0}

        if self.verbose:
            log(f"\n┌── 课: {cn} [{cls}] ({tea})", "title")
            log(f"└── 目录: {course_folder}", "dim")

        # 取 lessons
        try:
            lessons = self.client.lessons_api.list_lessons(classroom_id)
        except Exception as e:
            log(f"  取 lesson 异: {e}", "warn")
            lessons = []

        if self.verbose:
            log(f"  共 {len(lessons)} 个 lesson", "dim")

        # 给每 lesson 标 order
        for i, l in enumerate(lessons):
            l["order"] = i + 1

        total_pdfs = 0
        for lesson in lessons:
            try:
                total_pdfs += self.download_lesson(course_folder, lesson, classroom_id)
            except Exception as e:
                log(f"    lesson {lesson.get('name','?')} 异: {e}", "warn")

        if self.verbose:
            log(f"┕ 本课共得 {total_pdfs} 个 PDF", "ok")

        return {"pdfs": total_pdfs, "lessons": len(lessons)}

    def download_all(self, courses: Optional[List[dict]] = None,
                     filter_func: Optional[Callable[[dict], bool]] = None) -> Dict:
        """下载所有课程之 PDF

        courses: None 则自动获取
        filter_func: 给 (course) → bool 过滤
        """
        if courses is None:
            courses = self.client.courses_api.list()

        if filter_func:
            courses = [c for c in courses if filter_func(c)]

        if self.verbose:
            log(f"\n共 {len(courses)} 门课程将处理", "info")

        stats = {"total_courses": len(courses), "total_pdfs": 0, "courses": []}
        for c in courses:
            try:
                r = self.download_course(c)
                stats["total_pdfs"] += r.get("pdfs", 0)
                stats["courses"].append({
                    "name": c.get("course", {}).get("name", "无名"),
                    "classroom_id": c.get("classroom_id"),
                    **r,
                })
            except Exception as e:
                log(f"  课 {c.get('classroom_id','?')} 异: {e}", "warn")

        return stats


# ============================================================
# 视频提取
# ============================================================
class VideoExtractor:
    """视频 + 字幕下载"""

    def __init__(self, client, output_root: Optional[str] = None,
                 verbose: bool = True):
        self.client = client
        self.output_root = Path(output_root or "雨课堂Videos").resolve()
        self.verbose = verbose
        self.output_root.mkdir(parents=True, exist_ok=True)

    def _download_file(self, url: str, out_path: Path,
                       chunk_size: int = 8192,
                       on_progress: Optional[Callable] = None) -> bool:
        try:
            with requests.get(url, stream=True, timeout=60) as r:
                r.raise_for_status()
                total = int(r.headers.get("Content-Length", 0))
                done = 0
                with open(out_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            done += len(chunk)
                            if on_progress and total:
                                on_progress(done, total)
            return True
        except Exception as e:
            log(f"    下载异: {e}", "warn")
            if out_path.exists():
                try:
                    out_path.unlink()
                except Exception:
                    pass
            return False

    def download_video(self, classroom_id: int, leaf_id: int,
                       video_name: str = "video",
                       course_folder: Optional[Path] = None,
                       course_sign: str = "",
                       with_subtitle: bool = True) -> Optional[Path]:
        """下载一视频 + 字幕"""
        # 取真实 ID
        video_id = self.client.videos_api.get_real_id(
            classroom_id, leaf_id, course_sign=course_sign
        )
        if not video_id:
            log(f"    × 取 video_id 失: leaf={leaf_id}", "warn")
            return None

        # 取播放 URL
        url = self.client.videos_api.get_best_quality_url(video_id)
        if not url:
            log(f"    × 取播放 URL 失: video={video_id}", "warn")
            return None

        out_dir = course_folder or self.output_root
        out_dir.mkdir(parents=True, exist_ok=True)

        safe_name = sanitize_filename(video_name, max_len=120)
        video_path = out_dir / f"{safe_name}.mp4"
        if video_path.exists() and video_path.stat().st_size > 10240:
            if self.verbose:
                log(f"    ✓ 已存，跳: {video_path.name}", "dim")
        else:
            if self.verbose:
                log(f"    → 下: {safe_name}.mp4", "info")
            if not self._download_file(url, video_path):
                return None

        # 字幕
        if with_subtitle:
            sub_url = self.client.videos_api.get_subtitle_url(video_id)
            if sub_url:
                srt_path = out_dir / f"{safe_name}.srt"
                if not srt_path.exists():
                    self._download_file(sub_url, srt_path)
                    if self.verbose:
                        log(f"    ✓ 字幕: {srt_path.name}", "dim")

        return video_path

    def download_course_videos(self, course: dict) -> Dict[str, int]:
        """下载一课程之全部视频"""
        cn = sanitize_filename(course.get("course", {}).get("name", "")
                               or course.get("course_name", "无名"))
        cls = sanitize_filename(course.get("name", ""))
        tea = sanitize_filename(course.get("teacher", {}).get("name", ""))
        folder = self.output_root / sanitize_filename(f"{cn}-{cls}-{tea}".strip("-"), 140)
        folder.mkdir(parents=True, exist_ok=True)

        classroom_id = course.get("classroom_id")
        course_sign = course.get("course_sign", "")

        # 用 mooc-api 风：取 chapter，过滤 leaf_type=0 (video)
        chapters = self.client.lessons_api.list_chapters(classroom_id, course_sign)
        videos = self.client.lessons_api.flatten_leaves(chapters, leaf_types=[0])

        if self.verbose:
            log(f"\n┌── 视频课: {cn}", "title")
            log(f"  共 {len(videos)} 个视频", "dim")

        count = 0
        for v in videos:
            leaf_id = v.get("id")
            name = v.get("name") or f"video_{leaf_id}"
            try:
                p = self.download_video(
                    classroom_id, leaf_id, name, folder, course_sign,
                )
                if p:
                    count += 1
            except Exception as e:
                log(f"    {name} 异: {e}", "warn")

        return {"videos": count, "total": len(videos)}
