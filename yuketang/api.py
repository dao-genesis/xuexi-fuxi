# -*- coding: utf-8 -*-
"""
api —— 雨课堂全量端点封装

涵两套并存之 API：
    v2/v3  风：/v2/api/web/...   /api/v3/...           （标准雨课堂）
    mooc-api 风：/mooc-api/v1/lms/...                   （新版 mooc 平台）
    edu_admin 风：/edu_admin/...                         （学校管理）
    video-log 风：/video-log/...                         （视频心跳）

自动按域名/课程类型选合适之路径。
"""
from __future__ import annotations
import time
from typing import List, Dict, Any, Optional

from .core import unwrap_data, unwrap_user, log


# ============================================================
# 用户
# ============================================================
class UserAPI:
    def __init__(self, http):
        self.http = http

    def check_login(self) -> dict:
        """验证登录态并取用户信息"""
        try:
            j = self.http.get("/v2/api/web/userinfo", require_success=False)
            user = unwrap_user(j)
            if user:
                return user
        except Exception:
            pass

        # 备用：mooc-api 风
        try:
            j = self.http.get("/edu_admin/check_user_session/", require_success=False)
            data = unwrap_data(j) or {}
            if isinstance(data, dict) and "user_id" in data:
                return data
        except Exception:
            pass

        return {}

    def basic_info(self) -> dict:
        """详细用户信息"""
        try:
            j = self.http.get("/edu_admin/get_user_basic_info/")
            return unwrap_data(j) or {}
        except Exception:
            return {}


# ============================================================
# 课程列表（含归档）
# ============================================================
class CoursesAPI:
    def __init__(self, http):
        self.http = http

    def list(self, identity: int = None, include_archived: bool = True) -> List[dict]:
        """列所有课程

        identity: None=自动尝试 (2 学生 → 1 备用); 整数则只用此身份
        include_archived: 是否包含归档课程
        """
        courses: List[dict] = []
        seen_ids = set()

        # v2/api/web 风
        identities = [identity] if identity is not None else [2, 1]
        for ide in identities:
            try:
                j = self.http.get(
                    "/v2/api/web/courses/list",
                    params={"identity": ide},
                    require_success=False,
                )
                data = unwrap_data(j) or {}
                if isinstance(data, dict):
                    for c in data.get("list", []) or []:
                        cid = c.get("classroom_id") or c.get("id")
                        if cid and cid not in seen_ids:
                            c.setdefault("classroom_id", cid)
                            c["_source"] = "v2_list"
                            courses.append(c)
                            seen_ids.add(cid)
                if courses and identity is None:
                    break  # 自动模式下，得课即可
            except Exception as e:
                log(f"  v2 课程列表 identity={ide} 异: {e}", "dim")

        # 归档
        if include_archived:
            try:
                j = self.http.get("/v2/api/web/classroom_archive", require_success=False)
                data = unwrap_data(j) or {}
                if isinstance(data, dict):
                    for c in data.get("classrooms", []) or []:
                        cid = c.get("classroom_id") or c.get("id")
                        if cid and cid not in seen_ids:
                            c.setdefault("classroom_id", cid)
                            c["_source"] = "archive"
                            c["_archived"] = True
                            courses.append(c)
                            seen_ids.add(cid)
            except Exception as e:
                log(f"  归档课程 异: {e}", "dim")

        # mooc-api 风（如可用）
        if self.http.university_id:
            try:
                j = self.http.get(
                    "/mooc-api/v1/lms/user/user-courses/",
                    params={
                        "status": 1, "page": 1, "no_page": 1,
                        "term": "latest",
                        "uv_id": self.http.university_id,
                    },
                    require_success=False,
                )
                data = unwrap_data(j) or {}
                if isinstance(data, dict):
                    for c in data.get("product_list", []) or []:
                        cid = c.get("classroom_id")
                        if cid and cid not in seen_ids:
                            c["_source"] = "mooc_api"
                            courses.append(c)
                            seen_ids.add(cid)
            except Exception as e:
                log(f"  mooc-api 课程列表 异: {e}", "dim")

        return courses


# ============================================================
# 课程结构 / Lessons / Chapters / Leaves
# ============================================================
class LessonsAPI:
    """课程内之单元 —— Lesson / Chapter / Leaf

    雨课堂之课程结构有两套并存：
        - 老 v2 风：classroom 下挂 lessons (即课程列表)，每 lesson 有 presentations
        - 新 mooc 风：classroom 下挂 chapters → sections → leaves
    """

    LEAF_TYPE = {
        0: "video",
        1: "slide",     # PPT/课件
        3: "recommend",
        4: "discussion",
        5: "exam",
        6: "homework",
    }

    def __init__(self, http):
        self.http = http

    # -------- v2 风 --------
    def list_lessons(self, classroom_id: int, page_size: int = 500) -> List[dict]:
        """v2/api/web 风：取一 classroom 下所有 lesson（含课件、作业、讨论等）"""
        path = f"/v2/api/web/logs/learn/{classroom_id}"
        params = {"actype": -1, "page": 0, "offset": page_size, "sort": -1}
        headers = {
            "classroom-id": str(classroom_id),
            "university-id": self.http.university_id or "0",
        }
        j = self.http.get(path, params=params, headers=headers, require_success=False)
        data = unwrap_data(j) or {}
        if isinstance(data, dict):
            return data.get("activities", []) or []
        return []

    # -------- mooc-api 风 --------
    def list_chapters(self, classroom_id: int, course_sign: str = "",
                      uv_id: str = None) -> List[dict]:
        """mooc-api 风：取课程章节结构（含全部 leaf）"""
        uv_id = uv_id or self.http.university_id or "0"
        params = {
            "cid": classroom_id,
            "term": "latest",
            "uv_id": uv_id,
        }
        if course_sign:
            params["sign"] = course_sign
        headers = {
            "classroom-id": str(classroom_id),
            "university-id": str(uv_id),
        }
        try:
            j = self.http.get(
                "/mooc-api/v1/lms/learn/course/chapter",
                params=params, headers=headers,
                require_success=False,
            )
            data = unwrap_data(j) or {}
            return data.get("course_chapter", []) if isinstance(data, dict) else []
        except Exception:
            return []

    def flatten_leaves(self, chapters: List[dict],
                       leaf_types: Optional[List[int]] = None) -> List[dict]:
        """将章节树展平为 leaf 列表"""
        leaves: List[dict] = []

        def visit(node):
            if not isinstance(node, dict):
                return
            lt = node.get("leaf_type")
            if lt is not None:
                if leaf_types is None or lt in leaf_types:
                    leaves.append(node)
            for sub in node.get("section_leaf_list", []) or []:
                visit(sub)
            for sub in node.get("leaf_list", []) or []:
                visit(sub)

        for ch in chapters or []:
            visit(ch)
        return leaves

    def get_leaf_info(self, classroom_id: int, leaf_id: int,
                      course_sign: str = "", uv_id: str = None) -> dict:
        """取一 leaf 之详情"""
        uv_id = uv_id or self.http.university_id or "0"
        params = {"term": "latest", "uv_id": uv_id}
        if course_sign:
            params["sign"] = course_sign
        headers = {
            "classroom-id": str(classroom_id),
            "university-id": str(uv_id),
        }
        try:
            j = self.http.get(
                f"/mooc-api/v1/lms/learn/leaf_info/{classroom_id}/{leaf_id}/",
                params=params, headers=headers,
                require_success=False,
            )
            return unwrap_data(j) or {}
        except Exception:
            return {}


# ============================================================
# 课件 / Slides / Presentations
# ============================================================
class SlidesAPI:
    """课件相关 API —— v3 优先，v1 备"""

    def __init__(self, http):
        self.http = http

    # -------- v3 --------
    def get_lesson_summary_v3(self, lesson_id: int, classroom_id: int) -> Optional[dict]:
        """v3：取 lesson 摘要（含 presentations 列表）"""
        headers = {
            "classroom-id": str(classroom_id),
            "university-id": self.http.university_id or "0",
        }
        try:
            j = self.http.get(
                "/api/v3/lesson-summary/student",
                params={"lesson_id": lesson_id},
                headers=headers,
                require_success=False,
            )
            return unwrap_data(j)
        except Exception:
            return None

    def get_presentation_v3(self, presentation_id, lesson_id, classroom_id) -> dict:
        """v3：取一 presentation 之全部幻灯片"""
        headers = {
            "classroom-id": str(classroom_id),
            "university-id": self.http.university_id or "0",
        }
        return self.http.get(
            "/api/v3/lesson-summary/student/presentation",
            params={"presentation_id": presentation_id, "lesson_id": lesson_id},
            headers=headers,
        )

    # -------- v1 兜底 --------
    def get_lessonafter_v1(self, lesson_id, classroom_id) -> Optional[list]:
        headers = {
            "classroom-id": str(classroom_id),
            "university-id": self.http.university_id or "0",
        }
        try:
            j = self.http.get(
                f"/v2/api/web/lessonafter/{lesson_id}/presentation",
                params={"classroom_id": classroom_id},
                headers=headers,
                require_success=False,
            )
            return unwrap_data(j) or []
        except Exception:
            return None

    def get_presentation_v1(self, presentation_id, classroom_id) -> dict:
        headers = {
            "classroom-id": str(classroom_id),
            "university-id": self.http.university_id or "0",
        }
        return self.http.get(
            f"/v2/api/web/lessonafter/presentation/{presentation_id}",
            params={"classroom_id": classroom_id},
            headers=headers,
        )

    # -------- 通用：给 lesson 取所有幻灯片 --------
    def get_slides_for_lesson(self, lesson_id: int, classroom_id: int) -> List[dict]:
        """取一 lesson 之所有 presentation 之所有 slide

        返回：[{
            'presentation_id', 'presentation_name',
            'slides': [{'index', 'cover', 'thumbnail', ...}, ...]
        }, ...]
        """
        results: List[dict] = []

        # v3 path
        summary = self.get_lesson_summary_v3(lesson_id, classroom_id)
        if summary and isinstance(summary, dict):
            presentations = summary.get("presentations", []) or []
            for p in presentations:
                pid = p.get("id") or p.get("presentation_id")
                pname = p.get("title") or p.get("name") or f"presentation_{pid}"
                if not pid:
                    continue
                try:
                    pj = self.get_presentation_v3(pid, lesson_id, classroom_id)
                    pdata = unwrap_data(pj) or {}
                    slides = (pdata.get("slides") or pdata.get("Slides")
                              or pdata.get("data", {}).get("slides", []))
                    if isinstance(slides, list) and slides:
                        results.append({
                            "presentation_id": pid,
                            "presentation_name": pname,
                            "slides": slides,
                            "_api": "v3",
                        })
                except Exception as e:
                    log(f"  v3 取 presentation {pid} 异: {e}", "dim")
            if results:
                return results

        # v1 兜底
        v1_list = self.get_lessonafter_v1(lesson_id, classroom_id)
        if v1_list:
            for p in v1_list:
                pid = p.get("id") or p.get("presentation_id")
                pname = p.get("name") or p.get("title") or f"presentation_{pid}"
                if not pid:
                    continue
                try:
                    pj = self.get_presentation_v1(pid, classroom_id)
                    pdata = unwrap_data(pj) or {}
                    slides = (pdata.get("slides") or pdata.get("Slides") or [])
                    if isinstance(slides, list) and slides:
                        results.append({
                            "presentation_id": pid,
                            "presentation_name": pname,
                            "slides": slides,
                            "_api": "v1",
                        })
                except Exception as e:
                    log(f"  v1 取 presentation {pid} 异: {e}", "dim")

        return results


# ============================================================
# 视频
# ============================================================
class VideosAPI:
    """视频相关 —— 真实 ID、播放 URL、字幕、心跳"""

    def __init__(self, http):
        self.http = http

    def get_real_id(self, classroom_id, leaf_id, course_sign: str = "",
                    uv_id: str = None) -> Optional[str]:
        """从 leaf URL 之 ID 取视频真实 ID（ccid）"""
        uv_id = uv_id or self.http.university_id or "0"
        params = {"term": "latest", "uv_id": uv_id}
        if course_sign:
            params["sign"] = course_sign
        try:
            j = self.http.get(
                f"/mooc-api/v1/lms/learn/leaf_info/{classroom_id}/{leaf_id}/",
                params=params, require_success=False,
            )
            data = unwrap_data(j) or {}
            media = data.get("content_info", {}).get("media", {})
            return media.get("ccid")
        except Exception:
            return None

    def get_play_urls(self, video_id: str, provider: str = "cc",
                      is_single: int = 0) -> Dict[str, list]:
        """取视频之播放 URL（多种清晰度）"""
        try:
            j = self.http.get(
                "/api/open/audiovideo/playurl",
                params={
                    "video_id": video_id,
                    "provider": provider,
                    "is_single": is_single,
                },
                require_success=False,
            )
            data = unwrap_data(j) or {}
            return data.get("playurl", {}).get("sources", {}) or {}
        except Exception:
            return {}

    def get_best_quality_url(self, video_id: str) -> Optional[str]:
        """选最高清晰度之 URL"""
        sources = self.get_play_urls(video_id)
        if not sources:
            return None
        best_key = None
        best_num = -1
        for k in sources.keys():
            num = int("".join(c for c in k if c.isdigit()) or "0")
            if num > best_num:
                best_num = num
                best_key = k
        if best_key and sources[best_key]:
            urls = sources[best_key]
            return urls[0] if isinstance(urls, list) else urls
        return None

    def get_subtitle_url(self, video_id: str) -> Optional[str]:
        """取视频字幕 URL"""
        try:
            j = self.http.get(
                "/api/open/yunpan/video/subtitle/list",
                params={"cc_id": video_id},
                require_success=False,
            )
            data = unwrap_data(j) or {}
            items = data.get("items", []) or []
            if items:
                return items[0].get("url")
        except Exception:
            pass
        return None

    def get_watch_progress(self, classroom_id, video_id, user_id,
                           course_id, uv_id: str = None) -> dict:
        """取观看进度"""
        uv_id = uv_id or self.http.university_id or "0"
        try:
            j = self.http.get(
                "/video-log/get_video_watch_progress/",
                params={
                    "cid": course_id,
                    "user_id": user_id,
                    "classroom_id": classroom_id,
                    "video_type": "video",
                    "vtype": "rate",
                    "video_id": video_id,
                    "snapshot": 1,
                    "term": "latest",
                    "uv_id": uv_id,
                },
                require_success=False,
            )
            return unwrap_data(j) or {}
        except Exception:
            return {}


# ============================================================
# 习题、作业、考试
# ============================================================
class ExercisesAPI:
    """习题、作业、考试相关 API"""

    def __init__(self, http):
        self.http = http

    def get_exercise_list(self, leaf_id, uv_id: str = None) -> dict:
        """取一 leaf 之习题列表"""
        uv_id = uv_id or self.http.university_id or "0"
        try:
            j = self.http.get(
                f"/mooc-api/v1/lms/exercise/get_exercise_list/{leaf_id}/",
                params={"term": "latest", "uv_id": uv_id},
                require_success=False,
            )
            return unwrap_data(j) or {}
        except Exception:
            return {}

    def submit_problem(self, payload: dict, uv_id: str = None) -> dict:
        """提交答案"""
        uv_id = uv_id or self.http.university_id or "0"
        return self.http.post(
            "/mooc-api/v1/lms/exercise/problem_apply/",
            params={"term": "latest", "uv_id": uv_id},
            json=payload,
            require_success=False,
        )
