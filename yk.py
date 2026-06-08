# -*- coding: utf-8 -*-
"""
yk —— 雨课堂万能命令行入口

道法自然，一令通天下。

用法：
    python yk.py login                  # 自动登录（缓存→CDP→扫码）
    python yk.py login --qr             # 强制扫码登录
    python yk.py login --sessionid X    # 直接指定 sessionid
    python yk.py login --cdp            # 仅尝 CDP

    python yk.py whoami                 # 显当前用户
    python yk.py courses                # 列所有课程
    python yk.py courses --json         # JSON 格式

    python yk.py pdf                    # 下载所有课程之 PDF
    python yk.py pdf --filter 环境       # 仅下载课名含 "环境" 之课程
    python yk.py pdf --course-id N      # 仅下载某课
    python yk.py pdf --output PATH      # 指定输出目录

    python yk.py video --course-id N    # 下载某课视频
    python yk.py video --filter 化学

    python yk.py logout                 # 清缓存
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# 让 yuketang 包可被引入
sys.path.insert(0, str(Path(__file__).parent))
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

from yuketang import YuketangClient, log
from yuketang.core import sanitize_filename, AuthError, APIError


def cmd_login(args):
    client = YuketangClient(
        domain=args.domain,
        sessionid=args.sessionid,
        verbose=True,
    )
    if args.sessionid:
        prefer = "sessionid"
    elif args.qr_direct:
        prefer = "ws_direct"
    elif args.qr:
        prefer = "edge_pw"  # 默认 --qr 用 Playwright + 系统 Edge（最稳）
    elif args.cdp:
        prefer = "cdp"
    else:
        prefer = None

    try:
        user = client.login(prefer=prefer)
    except AuthError as e:
        log(f"\n× 登录失: {e}", "err")
        return 1

    log("\n" + "=" * 56, "ok")
    log(f"  ✓ 登录成功: {user.get('name', '?')}", "ok")
    log(f"  user_id: {user.get('user_id', '?')}", "dim")
    log(f"  school: {user.get('school_number', '?')}", "dim")
    log("=" * 56, "ok")
    return 0


def cmd_whoami(args):
    client = YuketangClient(domain=args.domain, verbose=False)
    sid = client.store.sessionid
    if not sid:
        log("× 无凭据。请先 yk login", "warn")
        return 1
    client.http.set_sessionid(sid)
    user = client.user_api.check_login()
    if user and user.get("name"):
        log(f"✓ {user.get('name')} (id={user.get('user_id', '?')}, "
            f"sid={sid[:12]}...)", "ok")
        return 0
    log(f"× 凭据无效。请重 yk login", "warn")
    return 1


def cmd_courses(args):
    client = _ensure_client(args)
    if not client:
        return 1
    courses = client.courses_api.list()
    if args.json:
        print(json.dumps(courses, ensure_ascii=False, indent=2))
        return 0
    log(f"\n共 {len(courses)} 门课程：", "title")
    log("─" * 70, "dim")
    for i, c in enumerate(courses, 1):
        name = c.get("course", {}).get("name", c.get("course_name", "无名"))
        cls = c.get("name", "")
        tea = c.get("teacher", {}).get("name", c.get("teacher_name", ""))
        cid = c.get("classroom_id", "?")
        archived = " [归档]" if c.get("_archived") else ""
        log(f"  [{i:3d}] {name} | {cls} | {tea}  cid={cid}{archived}", "info")
    return 0


def cmd_pdf(args):
    client = _ensure_client(args)
    if not client:
        return 1

    courses = client.courses_api.list()
    if args.filter:
        kw = args.filter
        courses = [c for c in courses if kw in (
            c.get("course", {}).get("name", "") or
            c.get("course_name", "") or
            c.get("name", "") or
            c.get("teacher", {}).get("name", "") or ""
        )]
    if args.course_id:
        courses = [c for c in courses if str(c.get("classroom_id")) == str(args.course_id)]

    if not courses:
        log("× 无匹配课程", "warn")
        return 1

    output = args.output or "雨课堂PDF"
    from yuketang.extractors import PDFExtractor
    extractor = PDFExtractor(
        client, output_root=output, workers=args.workers, verbose=True,
    )
    stats = extractor.download_all(courses=courses)

    log("\n" + "=" * 56, "ok")
    log(f"  ✓ 大成: {stats['total_pdfs']} 个 PDF "
        f"(共 {stats['total_courses']} 门课)", "ok")
    log("=" * 56, "ok")
    return 0


def cmd_video(args):
    client = _ensure_client(args)
    if not client:
        return 1

    courses = client.courses_api.list()
    if args.filter:
        kw = args.filter
        courses = [c for c in courses if kw in (
            c.get("course", {}).get("name", "") or
            c.get("course_name", "") or "")]
    if args.course_id:
        courses = [c for c in courses if str(c.get("classroom_id")) == str(args.course_id)]

    if not courses:
        log("× 无匹配课程", "warn")
        return 1

    output = args.output or "雨课堂Videos"
    from yuketang.extractors import VideoExtractor
    extractor = VideoExtractor(client, output_root=output, verbose=True)

    total_videos = 0
    for c in courses:
        try:
            r = extractor.download_course_videos(c)
            total_videos += r.get("videos", 0)
        except Exception as e:
            log(f"  课 {c.get('classroom_id', '?')} 异: {e}", "warn")

    log(f"\n✓ 共下载 {total_videos} 个视频", "ok")
    return 0


def cmd_logout(args):
    client = YuketangClient(domain=args.domain, verbose=False)
    client.store.clear()
    log("✓ 凭据已清", "ok")
    return 0


def _ensure_client(args) -> "YuketangClient":
    """确保 client 已登录"""
    client = YuketangClient(
        domain=args.domain or "www.yuketang.cn",
        sessionid=args.sessionid,
        verbose=False,
    )

    # 尝缓存
    if not args.sessionid:
        sid = client.store.sessionid
        if sid:
            client.http.set_sessionid(sid)

    # 验证
    user = client.user_api.check_login()
    if not user or not user.get("name"):
        log("\n[!] 缓存凭据无效或不存在。开始登录 ...", "warn")
        try:
            user = client.login(prefer=args.prefer)
        except AuthError as e:
            log(f"× 登录失: {e}", "err")
            return None
    else:
        log(f"✓ 复用凭据: {user.get('name')}", "ok")
        client._user = user

    return client


def main():
    p = argparse.ArgumentParser(
        prog="yk",
        description="雨课堂万能命令行 · 道法自然",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--domain", default="www.yuketang.cn", help="雨课堂域名")
    p.add_argument("--sessionid", help="直接指定 sessionid（跳过登录）")
    p.add_argument("--prefer",
                   choices=["sessionid", "cdp", "edge_pw", "ws_direct"],
                   help="偏好认证方式")

    sub = p.add_subparsers(dest="cmd", required=True)

    # login
    sp = sub.add_parser("login", help="登录雨课堂")
    sp.add_argument("--qr", action="store_true",
                    help="扫码登录（自动启系统 Edge）")
    sp.add_argument("--qr-direct", action="store_true",
                    dest="qr_direct",
                    help="直 WebSocket 扫码（仅校账户绑定型用户）")
    sp.add_argument("--cdp", action="store_true",
                    help="仅尝试 CDP 认证")
    sp.set_defaults(func=cmd_login)

    # whoami
    sp = sub.add_parser("whoami", help="显示当前登录用户")
    sp.set_defaults(func=cmd_whoami)

    # courses
    sp = sub.add_parser("courses", help="列所有课程")
    sp.add_argument("--json", action="store_true", help="JSON 输出")
    sp.set_defaults(func=cmd_courses)

    # pdf
    sp = sub.add_parser("pdf", help="下载课件 PDF")
    sp.add_argument("--filter", help="按关键字过滤课程名")
    sp.add_argument("--course-id", help="只下某课 (classroom_id)")
    sp.add_argument("--output", help="输出目录")
    sp.add_argument("--workers", type=int, default=8, help="并发下载数")
    sp.set_defaults(func=cmd_pdf)

    # video
    sp = sub.add_parser("video", help="下载视频")
    sp.add_argument("--filter", help="按关键字过滤课程名")
    sp.add_argument("--course-id", help="只下某课 (classroom_id)")
    sp.add_argument("--output", help="输出目录")
    sp.set_defaults(func=cmd_video)

    # logout
    sp = sub.add_parser("logout", help="清除凭据")
    sp.set_defaults(func=cmd_logout)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main() or 0)
