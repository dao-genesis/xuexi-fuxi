# -*- coding: utf-8 -*-
"""
storage —— 持久化之器

凭据、缓存、用户偏好——皆居于此。
"""
from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any


def _default_cache_dir() -> Path:
    """默认缓存目录：脚本同级 .yuketang/"""
    # 优先用脚本所在目录
    import sys
    if hasattr(sys, "_MEIPASS"):  # PyInstaller
        return Path.home() / ".yuketang"
    here = Path(__file__).parent.parent  # 学习复习/
    return here / ".yuketang"


class CredentialStore:
    """凭据存储：sessionid、csrftoken、university_id 等

    存于 .yuketang/credentials.json
    """

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = Path(cache_dir) if cache_dir else _default_cache_dir()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cred_file = self.cache_dir / "credentials.json"
        self.legacy_session_file = self.cache_dir.parent / ".session_cache.txt"
        self._data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.cred_file.exists():
            try:
                return json.loads(self.cred_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        # 兼容老的 .session_cache.txt
        if self.legacy_session_file.exists():
            sid = self.legacy_session_file.read_text(encoding="utf-8").strip()
            if sid:
                return {"sessionid": sid, "_migrated_from_legacy": True}
        return {}

    def save(self):
        """落盘"""
        self.cred_file.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        # 同时更新老的 .session_cache.txt 以保兼容
        sid = self._data.get("sessionid", "")
        if sid:
            try:
                self.legacy_session_file.write_text(sid, encoding="utf-8")
            except Exception:
                pass

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value):
        self._data[key] = value
        self._data["_updated_at"] = int(time.time())

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if v is not None:
                self._data[k] = v
        self._data["_updated_at"] = int(time.time())

    def clear(self):
        self._data = {}
        if self.cred_file.exists():
            self.cred_file.unlink()

    @property
    def sessionid(self) -> Optional[str]:
        return self._data.get("sessionid")

    @sessionid.setter
    def sessionid(self, v: str):
        self.set("sessionid", v)

    @property
    def csrftoken(self) -> Optional[str]:
        return self._data.get("csrftoken")

    @property
    def university_id(self) -> Optional[str]:
        v = self._data.get("university_id")
        return str(v) if v else None

    @property
    def user_name(self) -> Optional[str]:
        return self._data.get("user_name")

    @property
    def domain(self) -> Optional[str]:
        return self._data.get("domain")

    def __repr__(self):
        return f"<CredentialStore at {self.cred_file}, has_session={bool(self.sessionid)}>"
