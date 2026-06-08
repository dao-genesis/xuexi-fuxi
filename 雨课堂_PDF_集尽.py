# -*- coding: utf-8 -*-
"""
雨课堂 PDF 集尽  ——  反者道之动也

道法自然，无为而无不为：
    既已扫码登录于浏览器之内，则脚本顺其势，承其cookies而潜行。
    顺雨课堂之API，遍取诸课件，合幻灯片之零散为PDF之整然。

依赖：
    pip install requests pillow
    （可选 pip install browser-cookie3  ——  自浏览器自动取 cookies）

用法（任择其一）：
    1) 自动模式（推荐）：
       python 雨课堂_PDF_集尽.py
       ——脚本会询问你的 sessionid，或尝试从浏览器自动读取

    2) 直输 sessionid：
       python 雨课堂_PDF_集尽.py --sessionid <你的sessionid>

    3) 指定课程关键字过滤：
       python 雨课堂_PDF_集尽.py --filter "环境毒理学"
"""

import argparse
import concurrent.futures
import json
import os
import re
import sys
import time
import traceback
from io import BytesIO
from pathlib import Path

try:
    import requests
except ImportError:
    print("缺少 requests，请运行: pip install requests", file=sys.stderr)
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("缺少 Pillow，请运行: pip install pillow", file=sys.stderr)
    sys.exit(1)


# ============================================================
# 通用工具
# ============================================================

INVALID_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|\r\n\t]')

def sanitize_filename(name: str, max_len: int = 80) -> str:
    """除恶字之于文件名也"""
    if not name:
        return "无名"
    name = INVALID_FILENAME_CHARS.sub("_", str(name)).strip()
    name = re.sub(r"\s+", " ", name)
    # 处理两端的圆点
    name = name.strip(". ")
    if not name:
        return "无名"
    return name[:max_len]


def log(msg: str, level: str = "info"):
    """彩色之教也"""
    colors = {
        "info": "\033[36m",     # cyan
        "ok": "\033[32m",       # green
        "warn": "\033[33m",     # yellow
        "err": "\033[31m",      # red
        "dim": "\033[90m",      # gray
        "title": "\033[1;35m",  # bold magenta
    }
    reset = "\033[0m"
    prefix = colors.get(level, "")
    print(f"{prefix}{msg}{reset}", flush=True)


def _is_success(j) -> bool:
    """判雨课堂API响应是否成功——万物负阴而抱阳"""
    if not isinstance(j, dict):
        return False
    return bool(j.get("success") or j.get("errcode") == 0 or j.get("code") == 0)


def _unwrap_data(j) -> dict:
    """取API响应之data——data或为dict或为list，一归于dict"""
    data = j.get("data") if isinstance(j, dict) else None
    if isinstance(data, list):
        return data[0] if data else {}
    return data if isinstance(data, dict) else {}


# ============================================================
# Session 之得：三道之门
# ============================================================

POSSIBLE_HOSTS = [
    "www.yuketang.cn",
    "pro.yuketang.cn",
    "changjiang.yuketang.cn",
]


def get_sessionid_from_browser(domain: str = "yuketang.cn"):
    """从已登录浏览器中取 cookies；若未装 browser-cookie3 则返回 None"""
    try:
        import browser_cookie3  # type: ignore
    except ImportError:
        return None

    candidates = []
    # 尝试主流浏览器
    for loader_name in ("edge", "chrome", "firefox", "chromium", "brave"):
        loader = getattr(browser_cookie3, loader_name, None)
        if not loader:
            continue
        try:
            cj = loader(domain_name=domain)
            for c in cj:
                if c.name == "sessionid" and domain in c.domain:
                    candidates.append((loader_name, c.domain, c.value))
        except Exception:
            pass

    if not candidates:
        return None

    # 若多个浏览器都有，让用户选
    if len(candidates) == 1:
        loader_name, dom, val = candidates[0]
        log(f"自{loader_name} 浏览器（{dom}）取得 sessionid", "ok")
        return val

    log("发现多处浏览器登录态：", "info")
    for i, (loader_name, dom, val) in enumerate(candidates):
        log(f"  [{i + 1}] {loader_name}  域: {dom}  sid: {val[:8]}...", "dim")
    while True:
        s = input("择一（数字）: ").strip()
        try:
            idx = int(s) - 1
            if 0 <= idx < len(candidates):
                return candidates[idx][2]
        except ValueError:
            pass


def prompt_sessionid_manually() -> str:
    """请君自陈 sessionid"""
    log("\n========================================================", "title")
    log(" 雨课堂 sessionid 之取法（一劳永逸）", "title")
    log("========================================================", "title")
    log(" 1. 浏览器中登录: https://www.yuketang.cn/v2/web/index", "info")
    log(" 2. 按下 F12 打开开发者工具", "info")
    log(" 3. 切换至『Application』(应用) 标签 ——> 『Cookies』", "info")
    log(" 4. 选 https://www.yuketang.cn", "info")
    log(" 5. 复制 'sessionid' 之值（一长串字符）", "info")
    log("========================================================\n", "title")
    while True:
        sid = input("请粘贴 sessionid: ").strip().strip('"').strip("'")
        if sid:
            return sid
        log("sessionid 不可空。请重输。", "warn")


def login_via_playwright(headless: bool = False) -> str | None:
    """启 playwright 之 chromium，由汝扫码，吾自取 sessionid。

    此乃"无为而无不为"之上道——只须扫一次码，余皆机自为。
    返回 sessionid，或 None（取消）。
    """
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError:
        log("未装 playwright。如欲用此功能，请先:", "warn")
        log("    pip install playwright", "warn")
        log("    playwright install chromium", "warn")
        return None

    log("\n╭" + "─" * 60 + "╮", "title")
    log("│  启动 chromium 浏览器，待汝扫码登录...               │", "title")
    log("│  登录成功后，吾自取登录态，无须汝再为                │", "title")
    log("╰" + "─" * 60 + "╯", "title")

    sessionid = None
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=headless)
        except Exception as e:
            log(f"启动 chromium 失败: {e}", "err")
            log("请运行: playwright install chromium", "warn")
            return None

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        try:
            page.goto("https://www.yuketang.cn/v2/web/index", timeout=60_000)
            log("\n→ 浏览器已启。请于其中扫码登录雨课堂。", "ok")
            log("  （登录成功后将自动检测，无须汝按任何键）\n", "dim")

            # 周期检测：每 2 秒查 sessionid 是否已生
            max_wait_sec = 600  # 10 分钟
            interval = 2
            elapsed = 0
            spinner = "|/-\\"
            spin_idx = 0
            while elapsed < max_wait_sec:
                cookies = context.cookies("https://www.yuketang.cn")
                for c in cookies:
                    if c["name"] == "sessionid" and c["value"]:
                        # 验证登录态：访问 userinfo
                        try:
                            resp = page.request.get(
                                "https://www.yuketang.cn/v2/api/web/userinfo",
                                timeout=10_000,
                            )
                            if resp.ok:
                                data = resp.json()
                                if _is_success(data):
                                    sessionid = c["value"]
                                    user = _unwrap_data(data)
                                    log(
                                        f"\n✓ 登录成功: {user.get('name', '?')} "
                                        f"({user.get('school_name', '?')})",
                                        "ok",
                                    )
                                    break
                        except Exception:
                            pass
                if sessionid:
                    break
                # 进度指示
                sys.stdout.write(
                    f"\r  {spinner[spin_idx % 4]} 待汝扫码中... "
                    f"已等 {elapsed} 秒  (上限 {max_wait_sec} 秒) "
                )
                sys.stdout.flush()
                spin_idx += 1
                time.sleep(interval)
                elapsed += interval

            print()  # 换行
            if not sessionid:
                log("超时未登录。退也。", "warn")
        except KeyboardInterrupt:
            log("\n汝中止之。", "warn")
        except Exception as e:
            log(f"登录之时遇异: {e}", "err")
            traceback.print_exc()
        finally:
            try:
                browser.close()
            except Exception:
                pass

    return sessionid


def detect_yuketang_host(session: requests.Session) -> str:
    """探得雨课堂可用之子域"""
    for host in POSSIBLE_HOSTS:
        try:
            r = session.get(f"https://{host}/v2/api/web/userinfo", timeout=10)
            if r.status_code == 200:
                data = r.json()
                if _is_success(data):
                    log(f"探得可用主机: {host}", "ok")
                    return host
        except Exception:
            continue
    return "www.yuketang.cn"


# ============================================================
# 雨课堂 API 之客户
# ============================================================

class YuketangClient:
    """承汝之登录态，潜行雨课堂之API"""

    def __init__(self, sessionid: str, host: str = "www.yuketang.cn"):
        self.host = host
        self.sess = requests.Session()
        self.sess.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "xtbz": "ykt",
            "X-Client": "web",
        })
        self.sess.cookies.set("sessionid", sessionid, domain=".yuketang.cn")
        self.sess.cookies.set("xtbz", "ykt", domain=".yuketang.cn")

    # -------- 课程列表 --------
    def get_courses(self) -> list:
        """既得显课，复取归档之课"""
        courses = []

        for identity in (2, 1):  # 2=学生身份, 1=备用
            url = f"https://{self.host}/v2/api/web/courses/list?identity={identity}"
            try:
                r = self.sess.get(url, timeout=15)
                if r.status_code != 200:
                    continue
                j = r.json()
                if not (_is_success(j)):
                    continue
                for c in j.get("data", {}).get("list", []) or []:
                    courses.append(c)
                if courses:
                    break  # 已得显课，无须再试他identity
            except Exception as e:
                log(f"取课程列表 identity={identity} 失败: {e}", "warn")

        # 归档之课
        try:
            url = f"https://{self.host}/v2/api/web/classroom_archive"
            r = self.sess.get(url, timeout=15)
            if r.status_code == 200:
                j = r.json()
                if _is_success(j):
                    for c in j.get("data", {}).get("classrooms", []) or []:
                        # 归档课程之结构略异，须补 classroom_id
                        c["classroom_id"] = c.get("classroom_id") or c.get("id")
                        courses.append(c)
        except Exception as e:
            log(f"取归档课程失败: {e}", "warn")

        return courses

    # -------- lesson列表 --------
    def get_lessons(self, classroom_id) -> list:
        url = (
            f"https://{self.host}/v2/api/web/logs/learn/{classroom_id}"
            f"?actype=-1&page=0&offset=500&sort=-1"
        )
        headers = {"classroom-id": str(classroom_id), "university-id": "0"}
        r = self.sess.get(url, headers=headers, timeout=20)
        if r.status_code != 200:
            raise RuntimeError(f"取lesson列表失败: HTTP {r.status_code}")
        j = r.json()
        if not (_is_success(j)):
            raise RuntimeError(f"取lesson列表失败: {j}")
        return j.get("data", {}).get("activities", []) or []

    # -------- 课件 v3 --------
    def get_lesson_v3(self, lesson_id, classroom_id):
        url = f"https://{self.host}/api/v3/lesson-summary/student?lesson_id={lesson_id}"
        headers = {"classroom-id": str(classroom_id), "university-id": "0"}
        r = self.sess.get(url, headers=headers, timeout=20)
        try:
            j = r.json()
        except Exception:
            return None
        if not (_is_success(j)):
            return None
        return j.get("data")

    def get_presentation_v3(self, presentation_id, lesson_id, classroom_id):
        url = (
            f"https://{self.host}/api/v3/lesson-summary/student/presentation"
            f"?presentation_id={presentation_id}&lesson_id={lesson_id}"
        )
        headers = {"classroom-id": str(classroom_id), "university-id": "0"}
        r = self.sess.get(url, headers=headers, timeout=20)
        j = r.json()
        if not (_is_success(j)):
            raise RuntimeError(f"取v3presentation失败: {j}")
        return j

    # -------- 课件 v1 兜底 --------
    def get_lesson_v1(self, lesson_id, classroom_id):
        url = (
            f"https://{self.host}/v2/api/web/lessonafter/{lesson_id}/presentation"
            f"?classroom_id={classroom_id}"
        )
        headers = {"classroom-id": str(classroom_id), "university-id": "0"}
        r = self.sess.get(url, headers=headers, timeout=20)
        try:
            j = r.json()
        except Exception:
            return None
        if not (_is_success(j)):
            return None
        return j.get("data", []) or []

    def get_presentation_v1(self, presentation_id, classroom_id):
        url = (
            f"https://{self.host}/v2/api/web/lessonafter/presentation/{presentation_id}"
            f"?classroom_id={classroom_id}"
        )
        headers = {"classroom-id": str(classroom_id), "university-id": "0"}
        r = self.sess.get(url, headers=headers, timeout=20)
        j = r.json()
        if not (_is_success(j)):
            raise RuntimeError(f"取v1presentation失败: {j}")
        return j

    # -------- 用户信息：核身之验 --------
    def check_login(self) -> dict:
        url = f"https://{self.host}/v2/api/web/userinfo"
        r = self.sess.get(url, timeout=10)
        if r.status_code != 200:
            return {}
        try:
            j = r.json()
            if _is_success(j):
                return _unwrap_data(j)
        except Exception:
            pass
        return {}


# ============================================================
# 幻灯片 ——> PDF 合成
# ============================================================

def download_image(url: str, timeout: int = 30, retries: int = 3) -> bytes:
    """得一图也"""
    last_err = None
    for i in range(retries):
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200 and r.content:
                return r.content
            last_err = f"HTTP {r.status_code}"
        except Exception as e:
            last_err = str(e)
        time.sleep(0.5 * (i + 1))
    raise RuntimeError(f"图未得: {last_err}")


def slides_to_pdf(slides_info: list, output_path: Path, max_workers: int = 8):
    """合幻灯片之零散为PDF之整然

    slides_info: [{"index": int, "cover": str}, ...]
    """
    if not slides_info:
        log("  无幻灯片", "warn")
        return False

    # 排序
    slides_info = sorted(slides_info, key=lambda x: x["index"])

    # 并行下载
    log(f"  下载 {len(slides_info)} 张幻灯片...", "dim")
    images_data = [None] * len(slides_info)

    def _dl(i, url):
        return i, download_image(url)

    failed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(_dl, i, s["cover"]): i
            for i, s in enumerate(slides_info)
            if s.get("cover")
        }
        for fut in concurrent.futures.as_completed(futures):
            try:
                i, data = fut.result()
                images_data[i] = data
            except Exception as e:
                failed += 1
                log(f"    某图败: {e}", "warn")

    # 过滤 None
    valid_data = [d for d in images_data if d]
    if not valid_data:
        log("  皆败，无所合", "err")
        return False
    if failed:
        log(f"  共 {failed} 图失，{len(valid_data)} 图合", "warn")

    # 合 PDF
    try:
        images = []
        for data in valid_data:
            img = Image.open(BytesIO(data))
            # PDF 需 RGB
            if img.mode != "RGB":
                img = img.convert("RGB")
            images.append(img)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        images[0].save(
            output_path,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=images[1:],
        )
        log(f"  ✓ PDF 已生: {output_path.name}  ({len(images)} 页)", "ok")
        return True
    except Exception as e:
        log(f"  合PDF失: {e}", "err")
        return False


# ============================================================
# Lesson PDF 抓取流
# ============================================================

def grab_lesson_pdfs(
    client: YuketangClient,
    lesson: dict,
    course_folder: Path,
    name_prefix: str,
) -> int:
    """取一 lesson 之所有 PDF；返回成功之数"""
    lesson_id = lesson.get("courseware_id") or lesson.get("id")
    classroom_id = lesson["classroom_id"]
    lesson_title = sanitize_filename(lesson.get("title", "无名课时"))
    lesson_type = lesson.get("type")

    # 跳过无 PPT 之类型
    if lesson_type in (15, 17, 6, 9):
        return 0  # MOOC 课时 / 通知，本无 PPT
    if lesson_type not in (3, 14, 2):
        # 未知类型，仍试之
        pass

    succeeded = 0

    # 先试 v3
    data_v3 = client.get_lesson_v3(lesson_id, classroom_id)
    if data_v3 and data_v3.get("presentations"):
        for idx, ppt in enumerate(data_v3["presentations"]):
            try:
                ppt_raw = client.get_presentation_v3(ppt["id"], lesson_id, classroom_id)
                slides = ppt_raw.get("data", {}).get("slides", []) or []
                pres_title = (
                    ppt_raw.get("data", {}).get("presentation", {}).get("title")
                    or ppt.get("title")
                    or f"课件{idx + 1}"
                )
                pres_title = sanitize_filename(pres_title)

                slides_info = [
                    {"index": s.get("index", 0), "cover": s.get("cover", "")}
                    for s in slides if s.get("cover")
                ]
                if not slides_info:
                    continue

                pdf_name = f"{name_prefix}-{lesson_title}-{pres_title}.pdf"
                pdf_name = sanitize_filename(pdf_name, max_len=180) + ""
                if not pdf_name.endswith(".pdf"):
                    pdf_name += ".pdf"
                out_path = course_folder / pdf_name

                if out_path.exists():
                    log(f"  ✓ 已存，跳: {pdf_name}", "dim")
                    succeeded += 1
                    continue

                log(f"  → 取: {lesson_title} - {pres_title}", "info")
                if slides_to_pdf(slides_info, out_path):
                    succeeded += 1
            except Exception as e:
                log(f"  × 取v3 presentation 失: {e}", "warn")
        return succeeded

    # v1 兜底
    try:
        v1_list = client.get_lesson_v1(lesson_id, classroom_id)
        if not v1_list:
            return 0
        for idx, ppt in enumerate(v1_list):
            if "id" not in ppt:
                continue
            try:
                ppt_raw = client.get_presentation_v1(ppt["id"], classroom_id)
                slides = ppt_raw.get("data", {}).get("slides", []) or []
                pres_title = (
                    ppt_raw.get("data", {}).get("title")
                    or ppt.get("title")
                    or f"课件{idx + 1}"
                )
                pres_title = sanitize_filename(pres_title)

                slides_info = []
                for s in slides:
                    # v1 字段首字母大写
                    cover = s.get("Cover") or s.get("cover")
                    idx_val = s.get("Index", s.get("index", 0))
                    if cover:
                        slides_info.append({"index": idx_val, "cover": cover})
                if not slides_info:
                    continue

                pdf_name = f"{name_prefix}-{lesson_title}-{pres_title}.pdf"
                pdf_name = sanitize_filename(pdf_name, max_len=180)
                if not pdf_name.endswith(".pdf"):
                    pdf_name += ".pdf"
                out_path = course_folder / pdf_name

                if out_path.exists():
                    log(f"  ✓ 已存，跳: {pdf_name}", "dim")
                    succeeded += 1
                    continue

                log(f"  → 取(v1): {lesson_title} - {pres_title}", "info")
                if slides_to_pdf(slides_info, out_path):
                    succeeded += 1
            except Exception as e:
                log(f"  × 取v1 presentation 失: {e}", "warn")
    except Exception as e:
        log(f"  × v1 兜底亦失: {e}", "warn")

    return succeeded


def grab_course(client: YuketangClient, course: dict, root_folder: Path) -> int:
    """取一课之所有 lesson"""
    course_name = sanitize_filename(course.get("course", {}).get("name", "无名课程"))
    classroom_name = sanitize_filename(course.get("name", ""))
    teacher_name = sanitize_filename(course.get("teacher", {}).get("name", ""))

    folder_name = f"{course_name}-{classroom_name}-{teacher_name}".strip("-")
    folder_name = sanitize_filename(folder_name, max_len=120)
    course_folder = root_folder / folder_name
    course_folder.mkdir(parents=True, exist_ok=True)

    classroom_id = course["classroom_id"]
    log(f"\n┌── 课程: {course_name} [{classroom_name}] ({teacher_name})", "title")
    log(f"└── 目录: {course_folder}", "dim")

    try:
        lessons = client.get_lessons(classroom_id)
    except Exception as e:
        log(f"  × 取lesson列表失败: {e}", "err")
        return 0

    log(f"  共 {len(lessons)} 个 lesson", "info")

    total = 0
    for idx, lesson in enumerate(lessons):
        lesson["classroom_id"] = classroom_id
        try:
            n = grab_lesson_pdfs(
                client, lesson,
                course_folder,
                name_prefix=f"{len(lessons) - idx:03d}",
            )
            total += n
        except Exception as e:
            log(f"  × lesson {lesson.get('title')} 失: {e}", "warn")
            traceback.print_exc()

    log(f"┕ 本课共得 {total} 个 PDF", "ok")
    return total


# ============================================================
# 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="雨课堂 PDF 集尽 —— 反者道之动也",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--sessionid", "-s", help="雨课堂 sessionid")
    parser.add_argument("--host", default=None, help="雨课堂主机域名，缺省自动探测")
    parser.add_argument(
        "--output", "-o", default="雨课堂PDF",
        help="输出根目录（默认: 雨课堂PDF）",
    )
    parser.add_argument(
        "--filter", "-f", action="append", default=None,
        help="课程名关键字过滤（可多次指定）",
    )
    parser.add_argument(
        "--list-only", "-l", action="store_true",
        help="仅列出课程，不下载",
    )
    parser.add_argument(
        "--select", action="store_true",
        help="交互选择要下载的课程",
    )
    parser.add_argument(
        "--login", action="store_true",
        help="启 playwright 浏览器，扫码登录后自取 sessionid（推荐）",
    )
    parser.add_argument(
        "--no-auto-login", action="store_true",
        help="禁用自动 playwright 登录（仅试浏览器cookie / 手动）",
    )
    parser.add_argument(
        "--cache-session", default=".session_cache.txt",
        help="缓存 sessionid 到此文件，下次自动复用",
    )
    args = parser.parse_args()

    log("\n╭" + "─" * 60 + "╮", "title")
    log("│  雨课堂 PDF 集尽   ——   反者道之动，弱者道之用    │", "title")
    log("│  天下莫柔弱于水，而攻坚强者莫之能胜               │", "title")
    log("╰" + "─" * 60 + "╯\n", "title")

    # 取 sessionid 之四道：
    #   1) --sessionid 显输
    #   2) --login 强用 playwright
    #   3) 缓存文件
    #   4) 自动探查 + 手动输入
    sessionid = args.sessionid
    cache_path = Path(args.cache_session)

    if not sessionid and args.login:
        sessionid = login_via_playwright()
        if not sessionid:
            log("playwright 登录失败。退也。", "err")
            sys.exit(1)

    if not sessionid:
        # 试读缓存
        if cache_path.exists():
            try:
                cached = cache_path.read_text(encoding="utf-8").strip()
                if cached:
                    log(f"试用缓存之 sessionid (来自 {cache_path})...", "info")
                    # 验证之
                    test_sess = requests.Session()
                    test_sess.cookies.set("sessionid", cached, domain=".yuketang.cn")
                    test_sess.headers["User-Agent"] = (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/131.0.0.0 Safari/537.36"
                    )
                    try:
                        r = test_sess.get(
                            "https://www.yuketang.cn/v2/api/web/userinfo",
                            timeout=10,
                        )
                        j = r.json()
                        if r.status_code == 200 and (
                            _is_success(j)
                        ):
                            sessionid = cached
                            log("缓存有效，复用之。", "ok")
                        else:
                            log("缓存已失效。", "warn")
                    except Exception:
                        log("缓存验证失败。", "warn")
            except Exception:
                pass

    if not sessionid and not args.no_auto_login:
        # 默认：试 playwright 登录
        log("吾今启 playwright 浏览器，待汝扫码（一劳永逸）...", "info")
        sessionid = login_via_playwright()

    if not sessionid:
        # 兜底：试浏览器自取
        log("\n试自浏览器自动取 sessionid...", "info")
        sessionid = get_sessionid_from_browser()
        if not sessionid:
            log("浏览器中未得（或 cookies 被加密）。", "warn")
            sessionid = prompt_sessionid_manually()

    # 建客户
    sess = requests.Session()
    sess.cookies.set("sessionid", sessionid, domain=".yuketang.cn")
    host = args.host or detect_yuketang_host(sess)

    client = YuketangClient(sessionid, host=host)
    user_info = client.check_login()
    if not user_info:
        log("登录态无效。请重取 sessionid。", "err")
        sys.exit(1)

    log(f"\n✓ 登录成功: {user_info.get('name', '?')} "
        f"({user_info.get('school_name', '?')})", "ok")

    # 缓存 sessionid 供下次复用
    try:
        cache_path.write_text(sessionid, encoding="utf-8")
        log(f"  sessionid 已存于 {cache_path}（下次自动复用）", "dim")
    except Exception as e:
        log(f"  缓存写入失败: {e}", "warn")

    # 取课程
    log("\n→ 取课程列表...", "info")
    courses = client.get_courses()
    if not courses:
        log("无课程。请确认登录态。", "err")
        sys.exit(1)

    # 过滤
    if args.filter:
        filtered = []
        for c in courses:
            name = c.get("course", {}).get("name", "") + " " + c.get("name", "")
            if any(f in name for f in args.filter):
                filtered.append(c)
        courses = filtered

    log(f"共得 {len(courses)} 门课程", "ok")
    log("─" * 60, "dim")
    for i, c in enumerate(courses):
        course_name = c.get("course", {}).get("name", "?")
        classroom_name = c.get("name", "?")
        teacher = c.get("teacher", {}).get("name", "?")
        log(f"  [{i + 1:2d}] {course_name} | {classroom_name} | {teacher}", "info")
    log("─" * 60, "dim")

    if args.list_only:
        return

    # 选择
    if args.select:
        sel = input(
            "\n择课程（例: 1,2,5-7  或 'all' 取全）: "
        ).strip().lower()
        if sel and sel != "all":
            indexes = []
            for part in sel.split(","):
                part = part.strip()
                if "-" in part:
                    try:
                        a, b = part.split("-")
                        indexes.extend(range(int(a), int(b) + 1))
                    except ValueError:
                        pass
                else:
                    try:
                        indexes.append(int(part))
                    except ValueError:
                        pass
            courses = [courses[i - 1] for i in indexes if 1 <= i <= len(courses)]
            log(f"已择 {len(courses)} 门课程", "info")

    # 取！
    root_folder = Path(args.output).resolve()
    root_folder.mkdir(parents=True, exist_ok=True)
    log(f"\n输出根目录: {root_folder}\n", "dim")

    grand_total = 0
    for course in courses:
        try:
            n = grab_course(client, course, root_folder)
            grand_total += n
        except Exception as e:
            log(f"× 课程失: {e}", "err")
            traceback.print_exc()

    log(f"\n╭{'─' * 60}╮", "title")
    log(f"│  集尽矣！共得 {grand_total} 个 PDF", "title")
    log(f"│  归于: {root_folder}", "title")
    log(f"╰{'─' * 60}╯", "title")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n\n知止所以不殆。退也。", "warn")
        sys.exit(130)
