# -*- coding: utf-8 -*-
"""
诊断之器：WS 登录后多路尝试取 sessionid
"""
import sys
import json
import time
import threading
import requests
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

DOMAIN = "www.yuketang.cn"
QR_IMG = str(Path(__file__).parent / "_qrcode_debug.png")

# 全量记录
login_message_full = None


def on_message(ws, message):
    global login_message_full
    try:
        msg = json.loads(message)
    except Exception:
        print(f"[原文非JSON] {message}")
        return
    print(f"[MSG] {json.dumps(msg, ensure_ascii=False)[:300]}")
    op = msg.get("op")
    if op == "loginsuccess":
        login_message_full = msg
        ws.close()
    elif msg.get("qrcode"):
        # 二维码：终端 + 图存
        try:
            import qrcode
            q = qrcode.QRCode(box_size=8, border=2)
            q.add_data(msg["qrcode"])
            q.make(fit=True)
            print(f"\n二维码内容: {msg['qrcode']}")
            print(f"二维码图: {QR_IMG}\n")
            q.print_ascii(invert=True)
            img = q.make_image(fill="black", back_color="white")
            img.save(QR_IMG)
            import webbrowser
            webbrowser.open(f"file:///{QR_IMG}")
        except Exception as e:
            print(f"二维码渲染异: {e}")


def on_open(ws):
    ws.send(json.dumps({
        "op": "requestlogin",
        "role": "web",
        "version": 1.4,
        "type": "qrcode",
    }))


def on_error(ws, err):
    print(f"[ERR] {err}")


def main():
    import websocket
    print("→ 连 wss://www.yuketang.cn/wsapp/ ...")
    ws = websocket.WebSocketApp(
        f"wss://{DOMAIN}/wsapp/",
        on_message=on_message,
        on_error=on_error,
        on_open=on_open,
    )

    t = threading.Thread(target=lambda: ws.run_forever(), daemon=True)
    t.start()

    # 等扫码
    start = time.time()
    while time.time() - start < 240:
        if login_message_full:
            break
        time.sleep(0.5)

    if not login_message_full:
        print("× 超时")
        return 1

    print("\n═══════════════════════════════════════")
    print("  完整 loginsuccess 消息：")
    print("═══════════════════════════════════════")
    print(json.dumps(login_message_full, ensure_ascii=False, indent=2))
    print("═══════════════════════════════════════\n")

    auth = login_message_full.get("Auth")
    user_id = login_message_full.get("UserID")

    # 试多路换 sessionid
    print("\n试多路换 sessionid：")
    print("─" * 60)

    ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
          "AppleWebKit/537.36 (KHTML, like Gecko) "
          "Chrome/131.0.0.0 Safari/537.36")

    sess = requests.Session()
    sess.headers.update({
        "User-Agent": ua,
        "Origin": f"https://{DOMAIN}",
        "Referer": f"https://{DOMAIN}/",
    })

    # 法1: /v2/api/web/login_with_uname_pwd 或 wechat callback
    candidates = [
        ("POST", "/v2/api/web/login/wxlogin/qrcode",
         {"auth": auth, "user_id": user_id}),
        ("POST", "/v2/api/web/login/wxlogin",
         {"auth": auth, "user_id": user_id}),
        ("POST", "/v2/api/web/login/wxauth/qrcode",
         {"auth": auth, "user_id": user_id}),
        ("POST", "/v2/api/web/login/wxauth",
         {"auth": auth, "user_id": user_id}),
        ("GET", "/v2/api/web/login/wxlogin/qrcode/check",
         None, {"auth": auth, "user_id": user_id}),
        # 用 Auth 作 query
        ("GET", "/v2/api/web/userinfo", None, {"Auth": auth}),
        # 试设 Auth 为 cookie
        ("GET", "/v2/api/web/userinfo", None, None, {"Auth": auth}),
        ("GET", "/v2/api/web/userinfo", None, None, {"sessionid": auth}),
        # 试 edu_admin 风
        ("POST", "/edu_admin/account/login/passport-login",
         {"auth": auth, "user_id": user_id}),
        ("POST", "/edu_admin/account/login/qrcode-login",
         {"auth": auth, "user_id": user_id}),
        # mooc-api 风
        ("POST", "/mooc-api/v1/lms/auth/wechat-qr-login/",
         {"auth": auth, "user_id": user_id}),
    ]

    found_sid = None
    for entry in candidates:
        if len(entry) == 3:
            method, path, body = entry
            params = None
            cookies = None
        elif len(entry) == 4:
            method, path, body, params = entry
            cookies = None
        else:
            method, path, body, params, cookies = entry

        # 用新 session 试，避免污染
        s = requests.Session()
        s.headers.update(sess.headers)
        if cookies:
            for ck, cv in cookies.items():
                s.cookies.set(ck, cv, domain=".yuketang.cn")
        try:
            if method == "GET":
                r = s.get(f"https://{DOMAIN}{path}", params=params, timeout=10)
            else:
                r = s.post(f"https://{DOMAIN}{path}", json=body, params=params, timeout=10)
            sid_in_cookies = None
            for k, v in r.cookies.items():
                if k == "sessionid":
                    sid_in_cookies = v
            sid_in_body = None
            try:
                j = r.json()
                if isinstance(j, dict):
                    d = j.get("data") or {}
                    if isinstance(d, dict):
                        sid_in_body = d.get("sessionid") or d.get("session_id")
            except Exception:
                j = None

            marker = ""
            if sid_in_cookies:
                marker = f" ★ sessionid (cookie): {sid_in_cookies[:20]}..."
                found_sid = sid_in_cookies
            elif sid_in_body:
                marker = f" ★ sessionid (body): {sid_in_body[:20]}..."
                found_sid = sid_in_body
            elif r.status_code == 200:
                marker = " ok body=" + str(j)[:80] if j else f" ok text={r.text[:80]}"
            else:
                marker = f" {r.status_code} {r.text[:80]}"

            print(f"  [{method} {path}]{marker}")
            if found_sid:
                print(f"\n★★★ 成功！sessionid = {found_sid}")
                # 验
                vs = requests.Session()
                vs.cookies.set("sessionid", found_sid, domain=".yuketang.cn")
                vs.headers["User-Agent"] = ua
                vr = vs.get(f"https://{DOMAIN}/v2/api/web/userinfo", timeout=10)
                print(f"    验证: {vr.status_code} {vr.text[:200]}")
                if vr.status_code == 200 and '"errcode":0' in vr.text:
                    # 存
                    from yuketang.storage import CredentialStore
                    store = CredentialStore()
                    store.update(sessionid=found_sid, domain=DOMAIN)
                    store.save()
                    print(f"\n✓ 已存于 {store.cred_file}")
                    return 0
        except Exception as e:
            print(f"  [{method} {path}] 异: {e}")

    print("\n× 全部路径均无 sessionid")
    return 1


if __name__ == "__main__":
    sys.exit(main())
