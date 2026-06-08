# -*- coding: utf-8 -*-
"""
core —— 道生一之根基

异常、日志、判定、域名、文件名安全化——百用所共。
"""
from __future__ import annotations
import re
import sys
from typing import Any, Optional


# ============================================================
# 异常族
# ============================================================
class YuketangError(Exception):
    """雨课堂错误之基"""


class AuthError(YuketangError):
    """认证之失"""


class APIError(YuketangError):
    """API 之异"""

    def __init__(self, message: str, *, status: int = None, body: Any = None):
        super().__init__(message)
        self.status = status
        self.body = body


class DomainError(YuketangError):
    """域名之失"""


# ============================================================
# 日志：道之述也
# ============================================================
_LEVEL_COLORS = {
    "info": "\033[36m",
    "ok": "\033[32m",
    "warn": "\033[33m",
    "err": "\033[31m",
    "dim": "\033[90m",
    "title": "\033[1;35m",
}
_RESET = "\033[0m"


def log(msg: str, level: str = "info", file=None):
    """统一日志输出"""
    out = file or sys.stdout
    if level == "raw":
        print(msg, flush=True, file=out)
        return
    prefix = _LEVEL_COLORS.get(level, "")
    print(f"{prefix}{msg}{_RESET}", flush=True, file=out)


# ============================================================
# 响应判定与解包：万道归一
# ============================================================
def is_success(j: Any) -> bool:
    """判雨课堂任意 API 之响应是否成功

    雨课堂诸 API 之成功标志多端：
        - errcode == 0   (v2/api/web 风)
        - success: True  (部分 v3)
        - code == 0      (mooc-api 风)
        - status == "OK"
    """
    if not isinstance(j, dict):
        return False
    if j.get("success") is True:
        return True
    if j.get("errcode") == 0:
        return True
    if j.get("code") == 0:
        return True
    if str(j.get("status", "")).upper() == "OK":
        return True
    return False


def unwrap_data(j: Any) -> Any:
    """从响应中取 data 字段——data 或为 dict 或为 list 或为 string"""
    if not isinstance(j, dict):
        return None
    return j.get("data")


def unwrap_user(j: Any) -> dict:
    """专取用户信息——data 可能为 list 内含一 dict"""
    data = unwrap_data(j)
    if isinstance(data, list):
        return data[0] if data else {}
    if isinstance(data, dict):
        # 可能套一层 user_info
        if "user_info" in data and isinstance(data["user_info"], dict):
            return data["user_info"]
        return data
    return {}


# ============================================================
# 文件名净化：可以为长治久安之器
# ============================================================
_INVALID_CHARS = re.compile(r'[\\/:*?"<>|\r\n\t]')


def sanitize_filename(name: str, max_len: int = 120, default: str = "无名") -> str:
    """净化作文件名：去除非法字符、控制长度"""
    if not name:
        return default
    name = _INVALID_CHARS.sub("_", str(name)).strip()
    name = re.sub(r"\s+", " ", name).strip(". ")
    if not name:
        return default
    return name[:max_len]


# ============================================================
# 域名探查：上善若水，居众之所恶
# ============================================================
POSSIBLE_DOMAINS = [
    "www.yuketang.cn",
    "pro.yuketang.cn",
    "changjiang.yuketang.cn",
]


def detect_domain(sessionid: Optional[str] = None,
                  candidates: Optional[list] = None,
                  timeout: int = 8) -> str:
    """探得可用之雨课堂子域。给 sessionid 则验证，无则只测连通"""
    import requests
    candidates = candidates or POSSIBLE_DOMAINS
    for d in candidates:
        try:
            s = requests.Session()
            if sessionid:
                s.cookies.set("sessionid", sessionid, domain=".yuketang.cn")
            s.headers["User-Agent"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )
            r = s.get(f"https://{d}/v2/api/web/userinfo", timeout=timeout)
            if r.status_code == 200:
                try:
                    j = r.json()
                    if is_success(j):
                        return d
                except Exception:
                    pass
            elif r.status_code == 401:
                # 域名通但未登录——仍是有效域名
                return d
        except Exception:
            continue
    return candidates[0]
