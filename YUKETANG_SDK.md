# 雨课堂通用 SDK · 道生一

> 道生一，一生二，二生三，三生万物
> 反者道之动，弱者道之用——从根本底层逆向雨课堂之一切

## 一、立意

此 SDK 为**雨课堂之根本底层逆向**而立，一劳永逸，为后续一切需求所赖之基础。

不再为登录所困，不再为接口所迷，不再为下载所累。

```
yuketang/                    # SDK 包
├── __init__.py             # YuketangClient 总入口
├── core.py                 # 异常、日志、判定、域名（道之根）
├── storage.py              # 凭据持久化（藏其器）
├── client.py               # HTTP 客户端（统一所有请求）
├── auth.py                 # 三路认证归一（道生三）
├── api.py                  # 全量 API 端点（万物之名）
├── extractors.py           # PDF / 视频提取器（万物之用）
yk.py                       # CLI 万能入口
```

## 二、三路认证（道生三）

```
┌─────────────────────────────────────┐
│   AuthManager（道总）                │
│   按优先级自动尝试：                  │
│                                     │
│   ① SessionIDAuth  — 缓存（最快）    │
│   ② CDPAuth        — 已开浏览器      │
│   ③ WebSocketQRAuth — 扫码（兜底）   │
└─────────────────────────────────────┘
```

### 关键发现：WebSocket 二维码登录

> 此 SDK 之**核心突破**——无须浏览器、无须扫码后再处理 cookies

```
1. 连 wss://www.yuketang.cn/wsapp/
2. 发 {"op":"requestlogin", "role":"web", "version":1.4, "type":"qrcode"}
3. 收 {"qrcode":"http://weixin.qq.com/q/...", "ticket":"..."}
4. 终端打印 ASCII 二维码 + 用微信扫码
5. 收 {"op":"loginsuccess", "Auth":"...", "UserID":"..."}
6. POST https://www.yuketang.cn/edu_admin/account/login/verify-origin-system-bind
       Body: {"auth": Auth, "origin_user_id": str(UserID)}
       响应 Set-Cookie 含 sessionid
7. sessionid 存 .yuketang/credentials.json — 一劳永逸
```

## 三、API 端点全图

### 1. 用户 / 鉴权 (UserAPI)
```
GET  /v2/api/web/userinfo                    # 标准登录验证
GET  /edu_admin/check_user_session/          # mooc 风
GET  /edu_admin/get_user_basic_info/         # 详细信息
WSS  /wsapp/                                 # 二维码登录
POST /edu_admin/account/login/verify-origin-system-bind  # 换 sessionid
```

### 2. 课程 (CoursesAPI)
```
GET /v2/api/web/courses/list?identity=2      # 学生身份课程
GET /v2/api/web/courses/list?identity=1      # 备用
GET /v2/api/web/classroom_archive            # 归档课程
GET /mooc-api/v1/lms/user/user-courses/      # 新版课程
```

### 3. 课程结构 (LessonsAPI)
```
GET /v2/api/web/logs/learn/{classroom_id}    # v2: lesson 列表
GET /mooc-api/v1/lms/learn/course/chapter    # mooc: 章节树
GET /mooc-api/v1/lms/learn/leaf_info/{cid}/{leaf_id}/  # leaf 详情

leaf_type 枚:
  0 = video      （视频）
  1 = slide      （课件 PPT）
  3 = recommend  （推荐阅读）
  4 = discussion （讨论）
  5 = exam       （考试）
  6 = homework   （作业）
```

### 4. 课件 (SlidesAPI)
```
GET /api/v3/lesson-summary/student?lesson_id=X            # v3: 取 presentation 列表
GET /api/v3/lesson-summary/student/presentation?...       # v3: 取 slides
GET /v2/api/web/lessonafter/{lesson_id}/presentation      # v1: 兜底
GET /v2/api/web/lessonafter/presentation/{pid}            # v1: slides 兜底
```

### 5. 视频 (VideosAPI)
```
GET /api/open/audiovideo/playurl?video_id=X&provider=cc   # 取多清晰度 URL
GET /api/open/yunpan/video/subtitle/list?cc_id=X          # 字幕
GET /video-log/get_video_watch_progress/                  # 观看进度
POST /video-log/heartbeat/                                # 心跳（用于刷课）
```

### 6. 习题 (ExercisesAPI)
```
GET  /mooc-api/v1/lms/exercise/get_exercise_list/{leaf_id}/  # 取题
POST /mooc-api/v1/lms/exercise/problem_apply/                # 提交答案
POST /v/discussion/v2/comment/                               # 提交讨论
```

## 四、关键 Header / Cookie

```
Cookie:
  sessionid=<core>           # 核心鉴权
  csrftoken=<csrf>            # CSRF 保护
  university_id=<uid>         # 学校 ID
  platform_id=3               # 雨课堂网页端

Headers:
  x-csrftoken: <csrf>         # 与 cookie 同
  university-id: <uid>        # 与 cookie 同
  xtbz: ykt | cloud           # 标识平台 (ykt=标准, cloud=学校私有云)
  X-Client: web
  Terminal-Type: web
  Platform-Id: 3
  classroom-id: <cid>         # 部分接口需要
```

## 五、域名变体

```
www.yuketang.cn          # 标准雨课堂
pro.yuketang.cn          # Pro 版
changjiang.yuketang.cn   # 长江雨课堂

<school>.yuketang.cn:
  buu.yuketang.cn        # 北京联合大学
  tust.yuketang.cn       # 天津科技大学
  gsscut.yuketang.cn     # 华南理工大学（研究生）
  ...
```

## 六、CLI 用法

```bash
# 登录（自动选最佳方式：缓存 → CDP → 扫码）
python yk.py login

# 强制扫码
python yk.py login --qr

# 直接给 sessionid
python yk.py login --sessionid xxxxxx

# 显当前用户
python yk.py whoami

# 列所有课程
python yk.py courses
python yk.py courses --json

# 下载所有课件 PDF
python yk.py pdf
python yk.py pdf --filter 环境
python yk.py pdf --course-id 12345
python yk.py pdf --output D:/MyPDFs --workers 16

# 下载视频
python yk.py video --filter 化学

# 清凭据
python yk.py logout
```

## 七、Python API 用法

```python
from yuketang import YuketangClient

client = YuketangClient()
user = client.login()   # 自动认证，返回用户 dict

# 列课程
courses = client.courses_api.list()

# 列某课程之 lessons
lessons = client.lessons_api.list_lessons(classroom_id=12345)

# 取一 lesson 之全部幻灯片
slides_groups = client.slides_api.get_slides_for_lesson(lesson_id, classroom_id)

# 视频真实 URL
url = client.videos_api.get_best_quality_url(video_id)

# 高级提取器
client.pdf.download_all()                         # 全部课程 PDF
client.pdf.download_course(some_course)            # 单课程
client.video.download_course_videos(some_course)   # 单课程视频
```

## 八、扩展之道

要加新功能，遵架构：

- **新认证方式** → 在 `auth.py` 加 `class XxxAuth(AuthMethod)`，注册于 `AuthManager._build_methods()`
- **新 API 端点** → 在 `api.py` 相应类中加方法
- **新提取器** → 在 `extractors.py` 加 `class XxxExtractor`
- **新 CLI 命令** → 在 `yk.py` 加 `cmd_xxx` 函数 + `argparse` subparser

## 九、致谢与参考

研读以下逆向工程项目，归一为此 SDK：

- [MuWinds/yuketangHelperBUU](https://github.com/MuWinds/yuketangHelperBUU) — WebSocket QR 登录之揭示者
- [LetMeFly666/RainClassroomVideoDownload](https://github.com/LetMeFly666/RainClassroomVideoDownload) — 视频 ccid → playurl 之路径
- [zhangchi2004/THU-Yuketang-Helper](https://github.com/zhangchi2004/THU-Yuketang-Helper) — 清华雨课堂助手
- [ZaytsevZY/yuketang-helper-auto](https://github.com/ZaytsevZY/yuketang-helper-auto) — 多功能浏览器扩展

---

*天下莫柔弱于水，而攻坚强者莫之能胜——以其无以易之也。*
