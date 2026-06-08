# -*- coding: utf-8 -*-
"""
扫码登录 + 同时存二维码为图——便于前端扫
"""
import sys
import time
import webbrowser
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))

from yuketang import YuketangClient
from yuketang.auth import WebSocketQRAuth, AuthManager
from yuketang.core import log, is_success, unwrap_user
import requests

QR_IMAGE_PATH = str(Path(__file__).parent / "_qrcode_login.png")

# 自定义 QR 钩子：图片存盘 + 自动打开
def on_qr(qr_data: str):
    log(f"\n>>> 二维码图已存: {QR_IMAGE_PATH}", "ok")
    log(f">>> 二维码内容: {qr_data}", "dim")
    # 试自动打开图片
    try:
        webbrowser.open(f"file:///{QR_IMAGE_PATH}")
        log(">>> 已尝试自动打开图片（用默认看图程序）", "ok")
    except Exception:
        pass


def on_status(status: str, msg: str):
    log(f"  [状态] {status}: {msg}", "info")


def main():
    log("\n╭───────────────────────────────────────────────╮", "title")
    log("│  雨课堂扫码登录 · 图于前端 · 道法自然          │", "title")
    log("╰───────────────────────────────────────────────╯\n", "title")

    client = YuketangClient(verbose=True)

    auth = WebSocketQRAuth(
        domain="www.yuketang.cn",
        timeout=240,
        print_terminal=True,
        save_qr_image=QR_IMAGE_PATH,
        on_qr=on_qr,
        on_status=on_status,
        verbose=True,
    )

    sessionid = auth.authenticate()
    if not sessionid:
        log("\n× 扫码超时", "err")
        return 1

    # 验证并存
    log(f"\n✓ 得 sessionid: {sessionid[:12]}...", "ok")
    s = requests.Session()
    s.cookies.set("sessionid", sessionid, domain=".yuketang.cn")
    s.headers["User-Agent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )
    r = s.get("https://www.yuketang.cn/v2/api/web/userinfo", timeout=10)
    if r.status_code != 200 or not is_success(r.json()):
        log("× 验证失", "err")
        log(f"  响应: {r.text[:200]}", "dim")
        return 1
    user = unwrap_user(r.json())

    # 存
    client.store.update(
        sessionid=sessionid,
        domain="www.yuketang.cn",
        user_name=user.get("name"),
        user_id=user.get("user_id"),
        school_number=user.get("school_number"),
    )
    client.store.save()

    log("\n═══════════════════════════════════════", "ok")
    log(f"  ✓ 登录成功: {user.get('name', '?')}", "ok")
    log(f"  user_id: {user.get('user_id', '?')}", "dim")
    log(f"  school_number: {user.get('school_number', '?')}", "dim")
    log(f"  凭据已存: {client.store.cred_file}", "dim")
    log("═══════════════════════════════════════", "ok")

    # 清理二维码图
    try:
        Path(QR_IMAGE_PATH).unlink()
    except Exception:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
