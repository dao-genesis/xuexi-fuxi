# -*- coding: utf-8 -*-
"""
client —— HTTP 客户端：万事归一之器

自动重试、统一头部、cookie 管理、成功判定。
"""
from __future__ import annotations
import time
from typing import Any, Dict, Optional
import requests

from .core import APIError, AuthError, is_success, log


_DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


class HTTPClient:
    """雨课堂 HTTP 客户端

    - 自动添加雨课堂特征头：xtbz, x-client, terminal-type, university-id
    - sessionid + csrftoken 双 cookie 维护
    - 自动重试网络错误
    - 自动判定 success / errcode / code
    - 401 触发 on_unauthorized 钩子（用于自动重新认证）
    """

    def __init__(self, domain: str = "www.yuketang.cn", verbose: bool = False):
        self.domain = domain
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": _DEFAULT_UA,
            "Accept": "application/json, text/plain, */*",
            "xtbz": "ykt",
            "X-Client": "web",
        })
        self.university_id: Optional[str] = None
        self._on_unauthorized = None

    # -------- 设定 --------
    def set_sessionid(self, sessionid: str, domain: str = ".yuketang.cn"):
        self.session.cookies.set("sessionid", sessionid, domain=domain)

    def set_csrftoken(self, csrftoken: str, domain: str = ".yuketang.cn"):
        self.session.cookies.set("csrftoken", csrftoken, domain=domain)
        self.session.headers["x-csrftoken"] = csrftoken

    def set_university_id(self, uid: str):
        self.university_id = str(uid)
        self.session.cookies.set("university_id", str(uid), domain=".yuketang.cn")
        self.session.headers["university-id"] = str(uid)

    @property
    def sessionid(self) -> Optional[str]:
        return self.session.cookies.get("sessionid", domain=".yuketang.cn")

    def set_xtbz(self, value: str):
        """xtbz: 标识平台。ykt = 标准雨课堂；cloud = 长江雨课堂等学校私有云"""
        self.session.headers["xtbz"] = value

    def on_unauthorized(self, callback):
        """注册 401 钩子。返回 True 表示已修复，应重试请求"""
        self._on_unauthorized = callback

    # -------- 请求底层 --------
    def url(self, path: str) -> str:
        if path.startswith("http"):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return f"https://{self.domain}{path}"

    def request(self, method: str, path: str, *,
                params=None, json=None, data=None,
                headers: Dict[str, str] = None,
                timeout: int = 20,
                retries: int = 2,
                require_success: bool = True,
                **kw) -> Dict[str, Any]:
        """统一请求接口

        require_success: True 时若响应非 success 则抛 APIError。False 时返回原 dict。
        """
        url = self.url(path)
        merged_headers = dict(headers) if headers else {}
        if "classroom-id" not in (k.lower() for k in merged_headers.keys()):
            # 部分接口需要 university-id 头，已在 session 头上
            pass

        last_exc: Optional[Exception] = None
        for attempt in range(retries + 1):
            try:
                r = self.session.request(
                    method, url,
                    params=params, json=json, data=data,
                    headers=merged_headers, timeout=timeout, **kw,
                )
            except (requests.Timeout, requests.ConnectionError) as e:
                last_exc = e
                if attempt < retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                raise APIError(f"网络异: {e}") from e

            # 401 处理
            if r.status_code == 401:
                if self._on_unauthorized and attempt == 0:
                    if self.verbose:
                        log("  ! 401，触发重新认证 ...", "warn")
                    if self._on_unauthorized():
                        continue  # 重试一次
                raise AuthError(f"401 未授权: {r.text[:200]}")

            # 其它错误
            if r.status_code >= 500 and attempt < retries:
                time.sleep(0.5 * (attempt + 1))
                continue

            if r.status_code >= 400:
                raise APIError(
                    f"HTTP {r.status_code}: {r.text[:200]}",
                    status=r.status_code, body=r.text,
                )

            # 解 JSON
            try:
                j = r.json()
            except Exception:
                if require_success:
                    raise APIError(f"非 JSON 响应: {r.text[:200]}")
                return {"_raw_text": r.text, "_status": r.status_code}

            if require_success and not is_success(j):
                raise APIError(
                    f"业务失败: {str(j)[:300]}",
                    status=r.status_code, body=j,
                )

            return j

        # 不应到达
        if last_exc:
            raise APIError(f"重试用尽: {last_exc}")
        raise APIError("未知错")

    # -------- 便捷方法 --------
    def get(self, path: str, **kw) -> Dict[str, Any]:
        return self.request("GET", path, **kw)

    def post(self, path: str, **kw) -> Dict[str, Any]:
        return self.request("POST", path, **kw)

    def put(self, path: str, **kw) -> Dict[str, Any]:
        return self.request("PUT", path, **kw)

    def delete(self, path: str, **kw) -> Dict[str, Any]:
        return self.request("DELETE", path, **kw)

    # -------- 原始请求（不解 JSON），用于下载文件 --------
    def get_raw(self, path: str, **kw) -> requests.Response:
        return self.session.get(self.url(path), **kw)

    def post_raw(self, path: str, **kw) -> requests.Response:
        return self.session.post(self.url(path), **kw)
