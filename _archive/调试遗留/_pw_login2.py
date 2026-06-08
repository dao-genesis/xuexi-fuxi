# -*- coding: utf-8 -*-
"""
Playwright 登录 v2 —— 更宽容、更耐心
"""
import sys
import time
import json
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))


def main():
    from playwright.sync_api import sync_playwright
    from yuketang.storage import CredentialStore
    from yuketang.core import log, is_success, unwrap_user
    import requests

    DOMAIN = "www.yuketang.cn"

    log("\n╭───────────────────────────────────────────────╮", "title")
    log("│  Playwright 登录 v2 · 道法自然                 │", "title")
    log("╰───────────────────────────────────────────────╯\n", "title")

    network_log = []  # 关键 API 之记

    with sync_playwright() as pw:
        log("→ 启 chromium ...", "info")
        ctx_dir = Path(__file__).parent / ".yuketang" / "pw_profile"
        ctx_dir.mkdir(parents=True, exist_ok=True)

        browser = pw.chromium.launch_persistent_context(
            str(ctx_dir),
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            viewport={"width": 1280, "height": 820},
            timeout=60000,
        )
        try:
            page = browser.pages[0] if browser.pages else browser.new_page()

            # 监网请求
            def on_response(resp):
                u = resp.url
                if ("yuketang.cn" in u and
                    any(k in u for k in [
                        "/v2/api/web/", "/edu_admin/", "/mooc-api/",
                        "/api/v3/", "wxauth", "login", "wsapp",
                    ])):
                    try:
                        body_preview = resp.text()[:200] if resp.status < 400 else ""
                    except Exception:
                        body_preview = ""
                    entry = {
                        "url": u,
                        "status": resp.status,
                        "method": resp.request.method,
                        "body": body_preview,
                    }
                    network_log.append(entry)

            page.on("response", on_response)

            # 不等任何状态，立即返
            log("→ 导航 https://www.yuketang.cn/ ...", "info")
            try:
                page.goto("https://www.yuketang.cn/", timeout=8000, wait_until="commit")
            except Exception as e:
                log(f"  立即返(可忽): {e}", "dim")

            page.bring_to_front()

            log("\n══════════════════════════════════════════════", "warn")
            log("  请于弹出之 chromium 中扫码或用账户密码登录", "warn")
            log("  吾守候每秒查 cookies", "dim")
            log("══════════════════════════════════════════════\n", "warn")

            sessionid = None
            csrftoken = None
            for i in range(360):
                time.sleep(1)
                try:
                    cookies = browser.cookies()
                except Exception as e:
                    if (i + 1) % 30 == 0:
                        log(f"  ! cookies 取异: {e}", "dim")
                    continue

                for c in cookies:
                    if "yuketang" not in c.get("domain", ""):
                        continue
                    if c.get("name") == "sessionid":
                        sessionid = c["value"]
                    elif c.get("name") == "csrftoken":
                        csrftoken = c["value"]

                if sessionid:
                    log(f"\n✓ 得 sessionid: {sessionid[:12]}...", "ok")
                    break

                if (i + 1) % 20 == 0:
                    try:
                        u = page.url
                    except Exception:
                        u = "?"
                    log(f"  ... {i+1}s/360s | 当前页: {u[:80]}", "dim")

            if not sessionid:
                log("\n× 超时未得 sessionid", "err")
                # 保留网络日志
                Path("_network.log").write_text(
                    json.dumps(network_log, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                log(f"  网络记录存于 _network.log ({len(network_log)} 条)", "dim")
                return 1

            all_cookies = [c for c in browser.cookies() if "yuketang" in c.get("domain", "")]

        finally:
            try:
                browser.close()
            except Exception:
                pass

    # 验
    log("\n→ 验证 ...", "info")
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

    store = CredentialStore()
    store.update(
        sessionid=sessionid,
        csrftoken=csrftoken,
        domain=DOMAIN,
        user_name=user.get("name"),
        user_id=user.get("user_id"),
        school_number=user.get("school_number"),
    )
    store.save()

    # 存网络日志（便于将来分析）
    Path("_network.log").write_text(
        json.dumps(network_log, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    log("\n═══════════════════════════════════════", "ok")
    log(f"  ✓ 登录成功: {user.get('name', '?')}", "ok")
    log(f"  user_id: {user.get('user_id', '?')}", "dim")
    log(f"  school: {user.get('school_number', '?')}", "dim")
    log(f"  凭据: {store.cred_file}", "dim")
    log(f"  网络记: _network.log ({len(network_log)} 条)", "dim")
    log("═══════════════════════════════════════", "ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
