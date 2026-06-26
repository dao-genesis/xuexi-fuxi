# 📚 复习板块 · 全方位复习站

> 道生一，一生二，二生三，三生万物。
> 从课程原始 PDF 出发，经「抽取 → 聚合 → 素材 → LLM 精炼 → 编译 → 思维导图 → 期末资料」流水线，
> 生成可在**公网任意浏览器**直接查看的复习页：综合复习资料 / 章节素材 / 学习系统 / 期末冲刺 / 知识图谱 / 原始课件 PDF 原文，皆汇于一页。

## 🌐 在线复习网址（一览）

**📖 总览首页**：https://zhouyoukang1234-spec.github.io/xuexi-fuxi/

| 学科 | 任课 / 进度 | 在线复习页 |
| --- | --- | --- |
| 🗺️ **地理信息系统 GIS** | 教师 黄源生 · 2026春 · 4 章 · 6 份课件 | [📖 打开复习页](https://zhouyoukang1234-spec.github.io/xuexi-fuxi/gis.html) |
| ⚖️ **环境法学** | 教师 杨建英 · 2026春 · 6 章 · 14 份课件 | [📖 打开复习页](https://zhouyoukang1234-spec.github.io/xuexi-fuxi/environmental-law.html) |
| 🏙️ **环境规划与管理** | 教师 王思雨 · 2026春 · 5 章 · 11 份课件 | [📖 打开复习页](https://zhouyoukang1234-spec.github.io/xuexi-fuxi/environmental-planning.html) |
| 💧 **流体力学** | 教师 曾强 · 2026春 · 7 章 · 14 份课件 | [📖 打开复习页](https://zhouyoukang1234-spec.github.io/xuexi-fuxi/fluid-mechanics.html) |
| 🧪 **环境毒理学** | 教师 森巴提·叶尔肯 · 2026春 · 7 章 · 15 份课件 | [📖 打开复习页](https://zhouyoukang1234-spec.github.io/xuexi-fuxi/environmental-toxicology.html) |
| 📜 **中国近现代史纲要** | 教师 亚里坤·买买提亚尔 · 2026春 | [📖 打开复习页](https://zhouyoukang1234-spec.github.io/xuexi-fuxi/modern-history.html) |

## 🧩 各科内容模块

- 🗺️ **地理信息系统 GIS** — 章节精讲×4 ｜ 总览资料×3 ｜ 真题与网络资源×7 ｜ 期末冲刺×3 ｜ 原始课件×1
- ⚖️ **环境法学** — 章节精讲×6 ｜ 总览资料×3 ｜ 真题与网络资源×4 ｜ 期末冲刺×3 ｜ 原始课件×1
- 🏙️ **环境规划与管理** — 章节精讲×5 ｜ 总览资料×3 ｜ 真题与网络资源×4 ｜ 期末冲刺×3 ｜ 原始课件×1
- 💧 **流体力学** — 章节精讲×7 ｜ 总览资料×3 ｜ 期末冲刺×3 ｜ 原始课件×1
- 🧪 **环境毒理学** — 章节精讲×7 ｜ 考前综合×3 ｜ 原始课件×1
- 📜 **中国近现代史纲要** — 导览×1 ｜ 复习资料×3 ｜ 例题精解 · 深化×1 ｜ 知识图谱×1

## 🛠️ 生成 / 更新

```bash
python 复习板块_生成.py            # 生成全部课程 → docs/
python 复习板块_生成.py 流体力学   # 仅生成指定课程
```

产物输出至 `docs/`（`index.html` 总览 + `<slug>.html` 每课一页，自包含、可直接部署为 GitHub Pages 静态站点）。
工程约定与流水线细节见 [`AGENTS.md`](AGENTS.md)。

---
> 本文件由 `复习板块_生成.py` 自动生成（与 `docs/index.html` 同源），请勿手改；如需调整请改生成器后重新生成。
