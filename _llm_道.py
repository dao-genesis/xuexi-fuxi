# -*- coding: utf-8 -*-
"""
LLM 道 (llm_dao)  ——  道冲，而用之有弗盈也

道法：
    provider 中立之 LLM 调用层。
    以 OpenAI Chat Completions 协议为公约——
    凡可通此协议者皆可：DeepSeek、Moonshot、通义、智谱、
    Together、Groq、本地 Ollama / vLLM / LM Studio，
    乃至商用 OpenAI / Azure 本身。

    本模块**零外部依赖**，唯标准库（urllib + json + hashlib）。
    若装 openai 或 httpx 亦不冲突，本模块不用之。

道之三要：
    1. 不绑实现 ──  base_url + api_key + model 三件套，
                  任配，任换，任叠。
    2. 不重花钱 ──  内置内容寻址之缓存。同问不二答。
    3. 不弃细节 ──  重试 / 超时 / token 计 / 错误情境 皆留接口。

用法（最简）:
    from _llm_道 import LLMClient
    cli = LLMClient.from_env()
    print(cli.chat("一句话述老子之教"))

用法（视觉 + JSON）:
    from pathlib import Path
    cli = LLMClient.from_env(profile="vision")
    out = cli.chat_json(
        prompt="据此图集，按 schema 总结此章核心。",
        images=list(Path("解析仓库/.../004-.../page_*.jpg")),
        schema={"概念": "list of str", "公式": "list of str"},
    )
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional, Union, Iterable

# ============================================================
# 一、配置加载（.env + 环境变量 + 多 profile）
# ============================================================

_REPO_ROOT = Path(__file__).resolve().parent
_DOT_ENV_PATH = _REPO_ROOT / ".env"
_DOT_ENV_EXAMPLE_PATH = _REPO_ROOT / ".env.example"


def _parse_dotenv(text: str) -> dict[str, str]:
    """简易 .env 解析：KEY=VALUE，行内 # 注释，引号自动去。"""
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip()
        # 去注释（# 必有前空格才算注释，避免误伤 #FFF 之类）
        if " #" in v:
            v = v.split(" #", 1)[0].rstrip()
        # 去引号
        if len(v) >= 2 and v[0] == v[-1] and v[0] in ('"', "'"):
            v = v[1:-1]
        out[k] = v
    return out


def _load_dotenv() -> dict[str, str]:
    """读 .env（若存）。结果不覆盖已存环境变量。"""
    if not _DOT_ENV_PATH.exists():
        return {}
    try:
        return _parse_dotenv(_DOT_ENV_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _env(key: str, default: Optional[str] = None) -> Optional[str]:
    """读环境变量；优先 os.environ，再 .env 文件。"""
    v = os.environ.get(key)
    if v is not None:
        return v
    cache = getattr(_env, "_dotenv", None)
    if cache is None:
        cache = _load_dotenv()
        setattr(_env, "_dotenv", cache)
    return cache.get(key, default)


# ============================================================
# 二、配置数据类（profile）
# ============================================================

@dataclass
class LLMConfig:
    """LLM 配置 · 一组三件套 + 附加项。"""
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    # 调用参数
    temperature: float = 0.3
    max_tokens: int = 4096
    timeout: float = 120.0
    # 重试
    retries: int = 3
    retry_backoff: float = 2.0  # 指数退避基数
    # 杂项
    extra_headers: dict[str, str] = field(default_factory=dict)
    # 是否启用缓存（per-client 默认；调用时可覆盖）
    cache_enabled: bool = True
    cache_dir: Optional[str] = None  # None → .llm_cache/

    def __post_init__(self) -> None:
        # base_url 去尾斜杠
        self.base_url = self.base_url.rstrip("/")

    @classmethod
    def from_env(cls, profile: str = "default") -> "LLMConfig":
        """从环境变量按 profile 加载。
        
        约定：
            profile=default → OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL
            profile=vision  → LLM_VISION_API_KEY 等（落空则回退 default）
            profile=<x>     → LLM_<X>_API_KEY 等（落空则回退 default）
        """
        prof = profile.upper()
        # 先取此 profile 之专属，落空回退到 OPENAI_*
        def pick(short_key: str, default: str = "") -> str:
            specific = _env(f"LLM_{prof}_{short_key}")
            if specific:
                return specific
            fallback = _env(f"OPENAI_{short_key}")
            if fallback:
                return fallback
            return default

        api_key = pick("API_KEY", "")
        base_url = pick("BASE_URL", "https://api.openai.com/v1")
        model = pick("MODEL", "gpt-4o-mini")

        # 调参（仅环境变量，profile 共用）
        temperature = float(_env("LLM_TEMPERATURE", "0.3") or "0.3")
        max_tokens = int(_env("LLM_MAX_TOKENS", "4096") or "4096")
        timeout = float(_env("LLM_TIMEOUT", "120") or "120")
        retries = int(_env("LLM_RETRIES", "3") or "3")
        cache_enabled = (_env("LLM_CACHE", "1") or "1").lower() not in ("0", "false", "no")

        return cls(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            retries=retries,
            cache_enabled=cache_enabled,
        )

    def is_ready(self) -> bool:
        """是否具备调用条件。本地 Ollama 等可无 api_key。"""
        # Ollama / vLLM 本地等通常 base_url 含 localhost/127 即无须 key
        if self.api_key:
            return True
        host = self.base_url.lower()
        if "localhost" in host or "127.0.0.1" in host or "::1" in host:
            return True
        return False

    def describe(self) -> str:
        masked = (self.api_key[:6] + "…" + self.api_key[-4:]) if self.api_key else "(无)"
        return f"{self.model} @ {self.base_url}  key={masked}"


# ============================================================
# 三、缓存（内容寻址，sha256(model + payload)）
# ============================================================

class LLMCache:
    """简易磁盘缓存。key = sha256(canonical_json(payload))"""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _hash(payload: Any) -> str:
        s = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    def _path(self, key: str) -> Path:
        return self.root / f"{key[:2]}" / f"{key}.json"

    def get(self, payload: Any) -> Optional[dict]:
        p = self._path(self._hash(payload))
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None

    def set(self, payload: Any, value: dict) -> None:
        p = self._path(self._hash(payload))
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps(
                {"payload_hash": self._hash(payload), "value": value, "ts": time.time()},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def stats(self) -> dict:
        files = list(self.root.rglob("*.json"))
        total_bytes = sum(f.stat().st_size for f in files if f.is_file())
        return {"count": len(files), "bytes": total_bytes, "root": str(self.root)}


# ============================================================
# 四、图像编码（路径 / bytes / PIL → data URL）
# ============================================================

def encode_image_data_url(
    image: Union[str, Path, bytes],
    *,
    mime: Optional[str] = None,
) -> str:
    """图像 → data:image/...;base64,xxx URL。"""
    if isinstance(image, (str, Path)):
        p = Path(image)
        data = p.read_bytes()
        if mime is None:
            ext = p.suffix.lower().lstrip(".")
            mime = {
                "jpg": "image/jpeg", "jpeg": "image/jpeg",
                "png": "image/png", "webp": "image/webp",
                "gif": "image/gif", "bmp": "image/bmp",
            }.get(ext, "image/jpeg")
    elif isinstance(image, bytes):
        data = image
        mime = mime or "image/jpeg"
    else:
        raise TypeError(f"不支持之图像类型: {type(image)}")
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


# ============================================================
# 五、消息构造
# ============================================================

def build_user_message(
    text: str,
    images: Optional[Iterable[Union[str, Path, bytes]]] = None,
) -> dict:
    """构造 user message。无图则纯文本；有图用 content 数组（vision）。"""
    if not images:
        return {"role": "user", "content": text}

    parts: list[dict] = [{"type": "text", "text": text}]
    for img in images:
        parts.append({
            "type": "image_url",
            "image_url": {"url": encode_image_data_url(img)},
        })
    return {"role": "user", "content": parts}


# ============================================================
# 六、LLM 客户端 · 核心
# ============================================================

class LLMError(Exception):
    """LLM 调用之异。"""

    def __init__(self, msg: str, *, status: Optional[int] = None, body: Optional[str] = None) -> None:
        super().__init__(msg)
        self.status = status
        self.body = body


class LLMClient:
    """LLM 客户端。OpenAI Chat Completions 协议。"""

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        cache_dir = config.cache_dir or str(_REPO_ROOT / ".llm_cache")
        self.cache = LLMCache(Path(cache_dir)) if config.cache_enabled else None

    @classmethod
    def from_env(cls, profile: str = "default") -> "LLMClient":
        return cls(LLMConfig.from_env(profile))

    # ─────────────────────────────────────────────
    # 主调
    # ─────────────────────────────────────────────

    def chat(
        self,
        messages: Union[str, list[dict]],
        *,
        system: Optional[str] = None,
        images: Optional[Iterable[Union[str, Path, bytes]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[dict] = None,
        model: Optional[str] = None,
        cache: Optional[bool] = None,
        extra_payload: Optional[dict] = None,
    ) -> str:
        """同步聊天。返回助手文本。

        messages: str → 包成单条 user；list → 直用（自带 system/user/assistant）
        images:   仅当 messages 为 str 且无 list 形式时生效
        """
        # 构造 messages
        if isinstance(messages, str):
            msgs: list[dict] = []
            if system:
                msgs.append({"role": "system", "content": system})
            msgs.append(build_user_message(messages, images))
        else:
            msgs = list(messages)
            if system and not any(m.get("role") == "system" for m in msgs):
                msgs.insert(0, {"role": "system", "content": system})

        payload: dict[str, Any] = {
            "model": model or self.config.model,
            "messages": msgs,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.config.max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format
        if extra_payload:
            payload.update(extra_payload)

        # 缓存
        use_cache = (cache if cache is not None else self.config.cache_enabled) and self.cache is not None
        if use_cache:
            hit = self.cache.get(payload)
            if hit and "value" in hit:
                v = hit["value"]
                if isinstance(v, dict) and "content" in v:
                    return v["content"]

        # 调
        resp = self._do_request(payload)

        # 提取
        try:
            content = resp["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise LLMError(f"响应结构非常: {e}, raw={resp}") from e

        # 缓存
        if use_cache:
            self.cache.set(payload, {
                "content": content,
                "usage": resp.get("usage", {}),
                "model": resp.get("model"),
            })

        return content

    def chat_json(
        self,
        prompt: str,
        *,
        schema_hint: Optional[Union[str, dict]] = None,
        images: Optional[Iterable[Union[str, Path, bytes]]] = None,
        system: Optional[str] = None,
        strict: bool = True,
        **kwargs,
    ) -> Any:
        """要 LLM 返 JSON。优先用 response_format，落败回退到 prompt 注入 + 解析。

        schema_hint: 简单 dict（仅作提示）或字符串描述
        strict: 解析失败时是否抛异（False 则返 raw 文本）
        """
        # 组装提示
        instr_lines: list[str] = []
        instr_lines.append(prompt)
        if schema_hint:
            if isinstance(schema_hint, dict):
                hint_str = json.dumps(schema_hint, ensure_ascii=False, indent=2)
            else:
                hint_str = str(schema_hint)
            instr_lines.append(
                "\n──\n返回**仅** JSON（无 markdown 代码块包裹），形如：\n" + hint_str
            )
        full_prompt = "\n".join(instr_lines)

        # 尝试 response_format=json_object（OpenAI / 通义 / DeepSeek 支持）
        rf = kwargs.pop("response_format", {"type": "json_object"})

        try:
            raw = self.chat(
                full_prompt, system=system, images=images, response_format=rf, **kwargs,
            )
        except LLMError:
            # 有些 provider 不支持 response_format，去之重试
            raw = self.chat(full_prompt, system=system, images=images, **kwargs)

        # 解 JSON
        cleaned = _strip_json_fence(raw)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            if strict:
                raise LLMError(f"JSON 解析失败: {cleaned[:200]}...")
            return raw

    # ─────────────────────────────────────────────
    # 底层请求
    # ─────────────────────────────────────────────

    def _do_request(self, payload: dict) -> dict:
        url = f"{self.config.base_url}/chat/completions"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        headers.update(self.config.extra_headers)

        last_err: Optional[Exception] = None
        for attempt in range(1, max(1, self.config.retries) + 1):
            try:
                req = urllib.request.Request(url, data=body, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
                    raw = resp.read().decode("utf-8")
                    return json.loads(raw)
            except urllib.error.HTTPError as e:
                err_body = ""
                try:
                    err_body = e.read().decode("utf-8", errors="replace")
                except Exception:
                    pass
                # 4xx 多为参数错，不必重试
                if 400 <= e.code < 500 and e.code not in (408, 429):
                    raise LLMError(
                        f"HTTP {e.code}: {e.reason}", status=e.code, body=err_body
                    ) from e
                last_err = LLMError(
                    f"HTTP {e.code}: {e.reason}", status=e.code, body=err_body
                )
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                last_err = LLMError(f"网错: {e}")
            except json.JSONDecodeError as e:
                last_err = LLMError(f"响应非 JSON: {e}")

            # 退避
            if attempt < self.config.retries:
                sleep_s = self.config.retry_backoff ** (attempt - 1)
                time.sleep(min(sleep_s, 30))

        assert last_err is not None
        raise last_err


# ============================================================
# 七、辅助
# ============================================================

_JSON_FENCE_RE_PREFIXES = ("```json", "```JSON", "```")


def _strip_json_fence(text: str) -> str:
    """去除 ```json...``` 包裹（若有）。"""
    s = text.strip()
    for pre in _JSON_FENCE_RE_PREFIXES:
        if s.startswith(pre):
            s = s[len(pre):].lstrip("\n").rstrip()
            if s.endswith("```"):
                s = s[: -3].rstrip()
            return s
    return s


# ============================================================
# 八、CLI 自测
# ============================================================

def _print_status() -> None:
    print("== LLM 道 · 状 ==")
    print(f"  .env 路径: {_DOT_ENV_PATH}  (存={_DOT_ENV_PATH.exists()})")
    for prof in ("default", "vision", "long"):
        cfg = LLMConfig.from_env(prof)
        ready = "✓" if cfg.is_ready() else "✗"
        print(f"  [{prof:8s}] {ready}  {cfg.describe()}")
    # 缓存状
    cache = LLMCache(_REPO_ROOT / ".llm_cache")
    s = cache.stats()
    print(f"  缓存: {s['count']} 条, {s['bytes']/1024:.1f} KiB @ {s['root']}")


def _smoke_call(prompt: str = "用一句话述老子之教，限 30 字。") -> None:
    cli = LLMClient.from_env()
    if not cli.config.is_ready():
        print("× 未配 API key，跳。请填 .env 后再试。")
        print(f"  样: {_DOT_ENV_EXAMPLE_PATH}")
        return
    print(f"→ {cli.config.describe()}")
    print(f"问: {prompt}")
    t0 = time.time()
    out = cli.chat(prompt, max_tokens=128)
    dt = time.time() - t0
    print(f"答 ({dt:.1f}s): {out}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("status", "stat", "-s"):
        _print_status()
    elif args[0] in ("smoke", "test", "-t"):
        prompt = " ".join(args[1:]) if len(args) > 1 else "用一句话述老子之教，限 30 字。"
        _smoke_call(prompt)
    elif args[0] in ("clear-cache", "clean"):
        cache = LLMCache(_REPO_ROOT / ".llm_cache")
        import shutil
        if cache.root.exists():
            shutil.rmtree(cache.root)
            print(f"× 已清缓存: {cache.root}")
        else:
            print("缓存目录不存。")
    else:
        print("用法:")
        print("  python _llm_道.py             # 看配置状")
        print("  python _llm_道.py smoke [提示] # 烟雾调一次")
        print("  python _llm_道.py clean       # 清缓存")
