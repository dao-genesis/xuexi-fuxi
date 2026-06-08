# -*- coding: utf-8 -*-
"""
Playwright 法登录——以浏览器为道之源

不重造 WS 协议——开雨课堂登录页，借页内二维码，监 cookie 变。
此即"上善若水"，水到渠成。
"""
import sys
import time
import threading
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))


def main():
    from playwright.sync_api import sync_playwright
    from yuketang.storage import CredentialStore
    from yuketang.core import log, is_success, unwrap_user
    import requests

    DOMAIN = "www.yuketang.cn"
    LOGIN_URL = f"https://{DOMAIN}/v2/web/login"
    HOME_URL = f"https://{DOMAIN}"

    log("\n╭───────────────────────────────────────────────╮", "title")
    log("│  Playwright 法登录 · 借浏览器之自然            │", "title")
    log("╰───────────────────────────────────────────────╯\n", "title")

    with sync_playwright() as pw:
        log("→ 启 chromium ...", "info")
        # 用持久化上下文，便于复用
        ctx_dir = Path(__file__).parent / ".yuketang" / "pw_profile"
        ctx_dir.mkdir(parents=True, exist_ok=True)

        browser = pw.chromium.launch_persistent_context(
            str(ctx_dir),
            headless=False,  # 显示，便于扫码
            args=["--disable-blink-features=AutomationControlled"],
            viewport={"width": 1200, "height": 800},
        )
        try:
            page = browser.pages[0] if browser.pages else browser.new_page()

            log(f"→ 导航至 {LOGIN_URL} ...", "info")
            try:
                page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=20000)
            except Exception as e:
                log(f"  导航异(可忽): {e}", "dim")

            page.bring_to_front()

            log("\n请在弹出之 chromium 中扫码登录雨课堂 ...", "warn")
            log("吾每秒查 cookies，得 sessionid 即归。", "dim")
            log("（亦可于此 chromium 中点 [密码登录] 用账户密码）\n", "dim")

            # 守候 sessionid 出现
            sessionid = None
            for i in range(360):  # 6 分钟
                time.sleep(1)
                try:
                    cookies = browser.cookies()
                except Exception:
                    continue
                for c in cookies:
                    if (c.get("name") == "sessionid"
                            and "yuketang" in c.get("domain", "")):
                        sessionid = c["value"]
                        break
                if sessionid:
                    break
                if (i + 1) % 15 == 0:
                    log(f"  ... 守候 {i+1}s/360s", "dim")

            if not sessionid:
                log("× 超时未得 sessionid", "err")
                return 1

            log(f"\n✓ 得 sessionid: {sessionid[:12]}...", "ok")

            # 取所有 yuketang cookies 保存
            all_yk_cookies = [
                c for c in browser.cookies()
                if "yuketang" in c.get("domain", "")
            ]

        finally:
            try:
                browser.close()
            except Exception:
                pass

    # 验
    log("\n→ 验证登录态 ...", "info")
    s = requests.Session()
    s.cookies.set("sessionid", sessionid, domain=".yuketang.cn")
    s.headers["User-Agent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )
    r = s.get(f"https://{DOMAIN}/v2/api/web/userinfo", timeout=10)
    if r.status_code != 200 or not is_success(r.json()):
        log(f"× 验证失: {r.status_code} {r.text[:200]}", "err")
        return 1
    user = unwrap_user(r.json())

    # 存所有 cookies
    store = CredentialStore()
    csrftoken = None
    for c in all_yk_cookies:
        if c.get("name") == "csrftoken":
            csrftoken = c.get("value")
    store.update(
        sessionid=sessionid,
        csrftoken=csrftoken,
        domain=DOMAIN,
        user_name=user.get("name"),
        user_id=user.get("user_id"),
        school_number=user.get("school_number"),
    )
    store.save()

    log("\n═══════════════════════════════════════", "ok")
    log(f"  ✓ 登录成功: {user.get('name', '?')}", "ok")
    log(f"  user_id: {user.get('user_id', '?')}", "dim")
    log(f"  school: {user.get('school_number', '?')}", "dim")
    log(f"  凭据存于: {store.cred_file}", "dim")
    log("═══════════════════════════════════════", "ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
