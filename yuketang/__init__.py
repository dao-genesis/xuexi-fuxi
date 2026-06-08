# -*- coding: utf-8 -*-
"""
yuketang —— 雨课堂通用 SDK · 道生一

道法自然，无为而无不为。
此包逆向雨课堂之全部，归一于通用之基础。

主要导出：
    YuketangClient       —— 万事归一之客户端
    auth                 —— WebSocketQR / Sessionid / CDP 三路认证
    api                  —— User/Courses/Lessons/Slides/Videos/Exercises
    extractors           —— PDF / Video / Exam 多面提取器
"""

__version__ = "1.0.0"

from .core import (
    YuketangError,
    AuthError,
    APIError,
    DomainError,
    log,
    is_success,
    unwrap_data,
    sanitize_filename,
    detect_domain,
    POSSIBLE_DOMAINS,
)
from .storage import CredentialStore
from .client import HTTPClient
from .auth import (
    AuthManager,
    WebSocketQRAuth,
    SessionIDAuth,
    CDPAuth,
    EdgePlaywrightAuth,
)
from .api import (
    UserAPI,
    CoursesAPI,
    LessonsAPI,
    SlidesAPI,
    VideosAPI,
    ExercisesAPI,
)


class YuketangClient:
    """雨课堂万能客户端——道生一之入口

    使用：
        client = YuketangClient()
        user = client.login()              # 自动选择最佳认证方式
        courses = client.courses.list()    # 列课程
        client.pdf.download_all()          # 下载所有 PDF
    """

    def __init__(self, domain: str = None, sessionid: str = None,
                 cache_dir: str = None, verbose: bool = True):
        self.domain = domain or "www.yuketang.cn"
        self.verbose = verbose
        self.store = CredentialStore(cache_dir=cache_dir)
        self.http = HTTPClient(domain=self.domain, verbose=verbose)
        if sessionid:
            self.http.set_sessionid(sessionid)
        self._auth_manager = None
        self._user = None

        # 各类 API
        self.user_api = UserAPI(self.http)
        self.courses_api = CoursesAPI(self.http)
        self.lessons_api = LessonsAPI(self.http)
        self.slides_api = SlidesAPI(self.http)
        self.videos_api = VideosAPI(self.http)
        self.exercises_api = ExercisesAPI(self.http)

        # 提取器（懒加载，避免循环依赖）
        self._pdf_extractor = None
        self._video_extractor = None

    @property
    def pdf(self):
        if self._pdf_extractor is None:
            from .extractors import PDFExtractor
            self._pdf_extractor = PDFExtractor(self)
        return self._pdf_extractor

    @property
    def video(self):
        if self._video_extractor is None:
            from .extractors import VideoExtractor
            self._video_extractor = VideoExtractor(self)
        return self._video_extractor

    def login(self, prefer: str = None) -> dict:
        """智能登录——道法自然
        prefer: 偏好认证法 (sessionid / ws_qr / cdp)；None 则自动选最佳
        返回 user 信息字典
        """
        if self._auth_manager is None:
            self._auth_manager = AuthManager(self.http, self.store, self.domain, verbose=self.verbose)
        user = self._auth_manager.login(prefer=prefer)
        self._user = user
        return user

    def whoami(self) -> dict:
        """当前登录用户"""
        if self._user is None:
            self._user = self.user_api.check_login()
        return self._user

    def is_logged_in(self) -> bool:
        try:
            u = self.user_api.check_login()
            return bool(u and u.get("name"))
        except Exception:
            return False
