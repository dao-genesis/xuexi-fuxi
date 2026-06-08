# -*- coding: utf-8 -*-
"""
auth —— 三路认证归一

    WebSocketQRAuth  —— wss://domain/wsapp/ 直接扫码登录（不需浏览器！）
    SessionIDAuth    —— 直接给 sessionid（最快）
    CDPAuth          —— 从 Edge/Chrome CDP 取 cookies（已开浏览器之最善）

AuthManager 自动按优先级尝试。
"""
from __future__ import annotations
import json
import os
import socket
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional, Callable, List

import requests

from .core import AuthError, log, is_success, unwrap_user
from .storage import CredentialStore


# ============================================================
# 基类
# ============================================================
class AuthMethod:
    """认证方法之基"""
    name: str = "base"

    def authenticate(self) -> Optional[str]:
        """返回 sessionid 或 None"""
        raise NotImplementedError


# ============================================================
# 一、SessionID 直认证
# ============================================================
class SessionIDAuth(AuthMethod):
    """直接以 sessionid 认证"""
    name = "sessionid"

    def __init__(self, sessionid: str, domain: str = "www.yuketang.cn"):
        self.sessionid = sessionid
        self.domain = domain

    def authenticate(self) -> Optional[str]:
        if not self.sessionid:
            return None
        # 验证之
        try:
            s = requests.Session()
            s.cookies.set("sessionid", self.sessionid, domain=".yuketang.cn")
            s.headers["User-Agent"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )
            r = s.get(f"https://{self.domain}/v2/api/web/userinfo", timeout=10)
            if r.status_code == 200 and is_success(r.json()):
                return self.sessionid
        except Exception:
            pass
        return None


# ============================================================
# 二、CDP 取 cookies（已开浏览器之善）
# ============================================================
class CDPAuth(AuthMethod):
    """通过 Chrome DevTools Protocol 从 Edge/Chrome 取 cookies"""
    name = "cdp"

    def __init__(self, port: int = 9333, auto_launch: bool = False,
                 verbose: bool = False):
        self.port = port
        self.auto_launch = auto_launch
        self.verbose = verbose

    def _is_port_open(self) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex(("127.0.0.1", self.port)) == 0

    def authenticate(self) -> Optional[str]:
        if not self._is_port_open():
            if not self.auto_launch:
                if self.verbose:
                    log(f"  CDP 端口 {self.port} 未开，跳过", "dim")
                return None
            if not self._launch_edge():
                return None

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            if self.verbose:
                log("  Playwright 未装，跳 CDP", "dim")
            return None

        try:
            with sync_playwright() as pw:
                browser = pw.chromium.connect_over_cdp(
                    f"http://127.0.0.1:{self.port}"
                )
                if not browser.contexts:
                    return None
                ctx = browser.contexts[0]
                cookies = ctx.cookies()
                for c in cookies:
                    if (c.get("name") == "sessionid"
                            and "yuketang" in c.get("domain", "")):
                        if self.verbose:
                            log(f"  ✓ CDP 得 sessionid: {c['value'][:12]}...", "ok")
                        return c["value"]
                if self.verbose:
                    log("  CDP 中无 sessionid", "dim")
                return None
        except Exception as e:
            if self.verbose:
                log(f"  CDP 异: {e}", "dim")
            return None

    def _launch_edge(self) -> bool:
        """关现有 Edge，重启带 CDP（需重登）"""
        edge_exe = None
        for p in [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]:
            if Path(p).exists():
                edge_exe = p
                break
        if not edge_exe:
            return False

        user_data = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Edge" / "User Data"
        if not user_data.exists():
            return False

        # 关现有
        try:
            import psutil
            for _ in range(3):
                found = False
                for p in psutil.process_iter(["name"]):
                    try:
                        if (p.info["name"] or "").lower() == "msedge.exe":
                            p.kill()
                            found = True
                    except Exception:
                        pass
                if not found:
                    break
                time.sleep(1)
        except ImportError:
            pass
        time.sleep(1)

        # 找 profile
        profile = "Default"
        for d in sorted(user_data.iterdir(), key=lambda x: x.name):
            if d.is_dir() and (d.name == "Default" or d.name.startswith("Profile")):
                for sub in ("Network/Cookies", "Cookies"):
                    pp = d / sub
                    if pp.exists() and pp.stat().st_size > 1000:
                        profile = d.name
                        break

        # 启
        subprocess.Popen([
            edge_exe,
            f"--remote-debugging-port={self.port}",
            f"--user-data-dir={user_data}",
            f"--profile-directory={profile}",
            "--remote-allow-origins=*",
            "--restore-last-session",
        ], creationflags=0x00000008)

        # 等
        for _ in range(40):
            time.sleep(0.5)
            if self._is_port_open():
                time.sleep(1)
                return True
        return False


# ============================================================
# 三、WebSocket 二维码登录（无须浏览器！）
# ============================================================
class WebSocketQRAuth(AuthMethod):
    """通过 wss://domain/wsapp/ 直接扫码登录

    流程：
        1. 连 WebSocket
        2. 发 requestlogin → 收到 qrcode
        3. 终端打印二维码 + 微信扫码
        4. 收到 loginsuccess → 含 Auth + UserID
        5. POST verify-origin-system-bind 取 sessionid

    回调可用：
        on_qr(qr_data)         — 二维码内容（用于客户端打印）
        on_status(status, msg) — 状态变化（pending/scanned/login_success/timeout）
    """
    name = "ws_qr"

    def __init__(self, domain: str = "www.yuketang.cn",
                 timeout: int = 180,
                 print_terminal: bool = True,
                 save_qr_image: Optional[str] = None,
                 on_qr: Optional[Callable[[str], None]] = None,
                 on_status: Optional[Callable[[str, str], None]] = None,
                 verbose: bool = True):
        self.domain = domain
        self.timeout = timeout
        self.print_terminal = print_terminal
        self.save_qr_image = save_qr_image
        self.on_qr = on_qr
        self.on_status = on_status
        self.verbose = verbose
        self._login_message: Optional[dict] = None
        self._ws = None
        self._qr_timer: Optional[threading.Timer] = None
        self._last_qr: Optional[str] = None
        self._qr_changed = threading.Event()

    def _emit_status(self, status: str, msg: str = ""):
        if self.on_status:
            try:
                self.on_status(status, msg)
            except Exception:
                pass
        if self.verbose:
            log(f"  [WS-QR] {status}: {msg}", "dim")

    def _print_qr(self, qr_data: str):
        if qr_data == self._last_qr:
            return
        self._last_qr = qr_data
        try:
            import qrcode
        except ImportError:
            log("  请装 qrcode: pip install qrcode pillow", "warn")
            return

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        if self.print_terminal:
            log("\n┌─── 雨课堂 · 微信扫码登录 ───┐", "title")
            log(f"  二维码内容: {qr_data}", "dim")
            log("  请用 [微信] 扫描下方二维码：\n", "info")
            qr.print_ascii(invert=True)
            log(f"\n  二维码每 50s 自动刷新；总超时 {self.timeout}s。", "dim")
            log("└────────────────────────────┘\n", "title")

        if self.save_qr_image:
            try:
                img = qr.make_image(fill="black", back_color="white")
                img.save(self.save_qr_image)
                log(f"  二维码图已存: {self.save_qr_image}", "dim")
            except Exception as e:
                log(f"  二维码图存失: {e}", "dim")

        if self.on_qr:
            try:
                self.on_qr(qr_data)
            except Exception:
                pass

    # -------- WebSocket 回调 --------
    def _on_message(self, ws, message):
        try:
            msg = json.loads(message)
        except Exception:
            return

        if "ticket" in msg:
            qr = msg.get("qrcode", "")
            if qr:
                self._print_qr(qr)
                self._emit_status("pending", "等待扫码")

        op = msg.get("op")
        if op == "requestlogin":
            self._fetch_qr()
        elif op == "scanned":
            self._emit_status("scanned", "已扫码，等确认")
        elif op == "loginsuccess":
            self._login_message = msg
            self._emit_status("login_success", "登录成功")
            try:
                ws.close()
            except Exception:
                pass
            if self._qr_timer:
                self._qr_timer.cancel()

    def _on_error(self, ws, error):
        if self.verbose:
            log(f"  [WS-QR] error: {error}", "err")
        self._emit_status("error", str(error))

    def _on_close(self, ws, *args):
        if self._qr_timer:
            self._qr_timer.cancel()

    def _on_open(self, ws):
        self._fetch_qr()
        # 50s 自动刷新二维码
        self._qr_timer = threading.Timer(50.0, self._fetch_qr)
        self._qr_timer.daemon = True
        self._qr_timer.start()

    def _fetch_qr(self):
        if self._ws:
            try:
                self._ws.send(json.dumps({
                    "op": "requestlogin",
                    "role": "web",
                    "version": 1.4,
                    "type": "qrcode",
                }))
            except Exception:
                pass

    # -------- 主流程 --------
    def authenticate(self) -> Optional[str]:
        try:
            import websocket
        except ImportError:
            log("  请装 websocket-client: pip install websocket-client", "warn")
            return None

        ws_url = f"wss://{self.domain}/wsapp/"
        if self.verbose:
            log(f"\n→ 连 WebSocket: {ws_url}", "info")

        self._ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self._ws.on_open = self._on_open

        # 开线程跑 ws
        ws_thread = threading.Thread(
            target=lambda: self._ws.run_forever(),
            daemon=True,
        )
        ws_thread.start()

        # 等待登录成功 or 超时
        start = time.time()
        while time.time() - start < self.timeout:
            if self._login_message:
                break
            time.sleep(0.5)

        if self._qr_timer:
            self._qr_timer.cancel()
        try:
            self._ws.close()
        except Exception:
            pass

        if not self._login_message:
            self._emit_status("timeout", f"超时 {self.timeout}s")
            return None

        # 用 Auth + UserID 换 sessionid
        return self._exchange_auth(self._login_message)

    def _exchange_auth(self, msg: dict) -> Optional[str]:
        """以 Auth + origin_user_id 换 sessionid"""
        auth = msg.get("Auth")
        user_id = msg.get("UserID")
        if not auth or not user_id:
            log(f"  loginsuccess 缺字段: {msg}", "warn")
            return None

        # 先取 university_id
        uni_id = self._get_university_id()
        if not uni_id:
            uni_id = "0"

        verify_url = (
            f"https://{self.domain}/edu_admin/account/login/"
            f"verify-origin-system-bind?term=latest&uv_id={uni_id}"
        )
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Content-Type": "application/json",
            "Referer": f"https://{self.domain}/",
            "Origin": f"https://{self.domain}",
            "Platform-Id": "3",
            "University-Id": str(uni_id),
            "Terminal-Type": "web",
            "X-Client": "web",
            "X-Csrftoken": "undefined",
            "Xtbz": "ykt",
        }
        body = {"auth": auth, "origin_user_id": str(user_id)}

        try:
            r = requests.post(verify_url, json=body, headers=headers, timeout=15)
        except Exception as e:
            log(f"  verify-origin 异: {e}", "err")
            return None

        # sessionid 在 Set-Cookie 中
        sessionid = None
        for k, v in r.cookies.items():
            if k == "sessionid":
                sessionid = v
                break

        # 备用：从 raw headers 解析
        if not sessionid:
            sc = r.headers.get("Set-Cookie", "")
            for part in sc.split(","):
                kv = part.split(";")[0].strip()
                if kv.startswith("sessionid="):
                    sessionid = kv.split("=", 1)[1]
                    break

        if not sessionid:
            # 最后：试 v2/api/web 的 wxauth 回调
            sessionid = self._try_wxauth_callback(auth, user_id)

        if sessionid:
            if self.verbose:
                log(f"  ✓ 得 sessionid: {sessionid[:12]}...", "ok")
            return sessionid

        log(f"  × verify-origin 后无 sessionid。Body: {r.text[:200]}", "warn")
        return None

    def _get_university_id(self) -> Optional[str]:
        """取 university_id（部分接口需要）"""
        try:
            url = (
                f"https://{self.domain}/edu_admin/get_custom_university_info/"
                f"?current=1&_={int(time.time() * 1000)}"
            )
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                j = r.json()
                d = j.get("data") or {}
                return str(d.get("university_id", "")) or None
        except Exception:
            pass
        return None

    def _try_wxauth_callback(self, auth: str, user_id) -> Optional[str]:
        """备用：尝试 v2/api/web 的微信回调"""
        try:
            r = requests.post(
                f"https://{self.domain}/v2/api/web/login/wxlogin/qrcode",
                json={"auth": auth, "user_id": user_id},
                timeout=10,
            )
            for k, v in r.cookies.items():
                if k == "sessionid":
                    return v
        except Exception:
            pass
        return None


# ============================================================
# 四、Playwright + 系统 Edge 登录（最稳，借浏览器之自然之力）
# ============================================================
class EdgePlaywrightAuth(AuthMethod):
    """以 Playwright 控系统 Edge 开雨课堂登录页

    流程：
        1. 启 Playwright 持久化 context（channel="msedge"）
        2. 导航至 https://{domain}/v2/web/login
        3. 自动点击「微信扫码登录」按钮
        4. 主人扫码 → 守候 cookies 中现 sessionid
        5. 取 cookies 之 sessionid + csrftoken → 回值

    此法稳过直 WS（适非校账户绑定型用户），借浏览器自然之流。
    """
    name = "edge_pw"

    def __init__(self, domain: str = "www.yuketang.cn",
                 timeout: int = 720,
                 profile_dir: Optional[str] = None,
                 verbose: bool = True):
        self.domain = domain
        self.timeout = timeout
        self.profile_dir = profile_dir
        self.verbose = verbose
        # 副产物：登录后 csrftoken 留之，便 client 用
        self.csrftoken: Optional[str] = None

    def authenticate(self) -> Optional[str]:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            if self.verbose:
                log("  Playwright 未装，跳 edge_pw", "warn")
            return None

        login_url = f"https://{self.domain}/v2/web/login"
        ctx_dir = Path(self.profile_dir or
                       Path.cwd() / ".yuketang" / "edge_pw_profile")
        ctx_dir.mkdir(parents=True, exist_ok=True)

        if self.verbose:
            log("\n→ 启系统 Edge（Playwright 控）...", "info")

        sessionid = None
        csrftoken = None

        with sync_playwright() as pw:
            try:
                browser = pw.chromium.launch_persistent_context(
                    str(ctx_dir),
                    channel="msedge",
                    headless=False,
                    args=["--disable-blink-features=AutomationControlled"],
                    viewport={"width": 1280, "height": 820},
                    timeout=30000,
                )
            except Exception as e:
                if self.verbose:
                    log(f"  × 启 Edge 失: {e}", "err")
                return None

            try:
                page = browser.pages[0] if browser.pages else browser.new_page()

                if self.verbose:
                    log(f"→ 导航至 {login_url} ...", "info")
                try:
                    page.goto(login_url, timeout=20000,
                              wait_until="domcontentloaded")
                    if self.verbose:
                        log("  ✓ 登录页加载", "ok")
                except Exception as e:
                    if self.verbose:
                        log(f"  ! 页加载异（继续）: {e}", "dim")

                # 试自动点击微信扫码登录之钮
                time.sleep(2)
                try:
                    for sel in [
                        "text=微信扫码登录",
                        "text=微信登录",
                        "text=扫码登录",
                        '[class*="qrcode"]',
                        '[class*="wechat"]',
                    ]:
                        try:
                            btn = page.locator(sel).first
                            if btn.count() > 0 and btn.is_visible(timeout=1000):
                                btn.click(timeout=3000)
                                if self.verbose:
                                    log(f"  ✓ 已点 [{sel}]", "ok")
                                break
                        except Exception:
                            continue
                except Exception:
                    pass

                page.bring_to_front()

                if self.verbose:
                    log("\n══════════════════════════════════════════", "warn")
                    log("  请于 Edge 中扫码完成登录", "warn")
                    log(f"  吾守候 sessionid 现于 cookies (至多 {self.timeout}s)",
                        "dim")
                    log("══════════════════════════════════════════\n", "warn")

                for i in range(self.timeout):
                    time.sleep(1)
                    try:
                        cookies = browser.cookies()
                    except Exception:
                        continue

                    for c in cookies:
                        if "yuketang" not in c.get("domain", ""):
                            continue
                        if c.get("name") == "sessionid" and c.get("value"):
                            sessionid = c["value"]
                        elif c.get("name") == "csrftoken" and c.get("value"):
                            csrftoken = c["value"]

                    if sessionid:
                        if self.verbose:
                            log(f"\n✓ 得 sessionid: {sessionid[:12]}... "
                                f"({i+1}s)", "ok")
                        break

                    if (i + 1) % 20 == 0:
                        try:
                            u = page.url
                        except Exception:
                            u = "?"
                        if self.verbose:
                            log(f"  ... {i+1}s/{self.timeout}s | "
                                f"页: {u[:80]}", "dim")
            finally:
                try:
                    browser.close()
                except Exception:
                    pass

        if sessionid:
            self.csrftoken = csrftoken
        return sessionid


# ============================================================
# AuthManager —— 三路归一
# ============================================================
class AuthManager:
    """认证管理器：自动按优先级尝试，得 sessionid 即归"""

    def __init__(self, http, store: CredentialStore,
                 domain: str = "www.yuketang.cn",
                 verbose: bool = True):
        self.http = http
        self.store = store
        self.domain = domain
        self.verbose = verbose

    def login(self, prefer: Optional[str] = None) -> dict:
        """智能登录。返回 user 信息。无果则抛 AuthError。"""
        methods = self._build_methods(prefer)
        for m in methods:
            if self.verbose:
                log(f"\n[认证] 尝 {m.name} ...", "info")
            try:
                sid = m.authenticate()
            except Exception as e:
                if self.verbose:
                    log(f"  {m.name} 异: {e}", "warn")
                continue
            if not sid:
                continue
            # 验证并取用户信息
            user = self._verify_and_user(sid)
            if user:
                self.http.set_sessionid(sid)
                # 收 csrftoken（若有）
                csrftoken = getattr(m, "csrftoken", None)
                self.store.update(
                    sessionid=sid,
                    csrftoken=csrftoken,
                    domain=self.domain,
                    user_name=user.get("name"),
                    user_id=user.get("user_id"),
                    school_number=user.get("school_number"),
                )
                self.store.save()
                if self.verbose:
                    log(f"  ✓ 登录成功: {user.get('name', '?')}", "ok")
                return user
        raise AuthError("全部认证法皆失")

    def _build_methods(self, prefer: Optional[str] = None) -> List[AuthMethod]:
        """构建尝试链

        默认序：缓存 → CDP → Edge-Playwright（最稳之扫码法）
        ws_qr 之直 WS 法仅当显指请用 (--prefer ws_qr 或 --qr-direct)
        """
        methods: List[AuthMethod] = []
        if prefer == "edge_pw" or prefer == "ws_qr":
            # 默认 --qr/--ws_qr 用 Edge-Playwright 法（更稳）
            methods.append(EdgePlaywrightAuth(domain=self.domain,
                                              verbose=self.verbose))
        elif prefer == "ws_direct":
            # 显指请 WS 直法
            methods.append(WebSocketQRAuth(domain=self.domain,
                                           verbose=self.verbose))
        elif prefer == "cdp":
            methods.append(CDPAuth(verbose=self.verbose))
        elif prefer == "sessionid":
            cached = self.store.sessionid
            if cached:
                methods.append(SessionIDAuth(cached, domain=self.domain))
        else:
            # 自动顺序：缓存 → CDP → Edge-Playwright
            cached = self.store.sessionid
            if cached:
                methods.append(SessionIDAuth(cached, domain=self.domain))
            methods.append(CDPAuth(verbose=self.verbose))
            methods.append(EdgePlaywrightAuth(domain=self.domain,
                                              verbose=self.verbose))
        return methods

    def _verify_and_user(self, sessionid: str) -> Optional[dict]:
        try:
            s = requests.Session()
            s.cookies.set("sessionid", sessionid, domain=".yuketang.cn")
            s.headers["User-Agent"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )
            r = s.get(f"https://{self.domain}/v2/api/web/userinfo", timeout=10)
            if r.status_code != 200:
                return None
            j = r.json()
            if not is_success(j):
                return None
            return unwrap_user(j)
        except Exception:
            return None
