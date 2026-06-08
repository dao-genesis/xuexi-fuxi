# -*- coding: utf-8 -*-
"""
道说 提示库 (prompt_library)  ——  言有君，事有宗

道法：
    LLM 协填之事，提示乃君。
    提示既定，则万章皆可同法填，得结构化之答。
    此处之器：
      · 三类任务（章占位填充 / 速查行 / 模拟卷）
      · 每类含 system / user_template / schema / parse
      · 一处改之，全链路应。

用法:
    from _道说_提示库 import 章占位填充任务, 速查行任务

    task = 章占位填充任务.build(
        course="环境毒理学",
        chap_label="第 3 章",
        chap_title="污染物的生物转运",
        page_count=51,
    )
    out = cli.chat_json(task.user, system=task.system, schema_hint=task.schema, images=task.images_meta)
    result = 章占位填充任务.parse(out)  # → 章占位结果 dataclass
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Optional, Type


# ============================================================
# 任务基类
# ============================================================

@dataclass
class 提示任务:
    """一个 LLM 任务之全部材料。"""
    system: str
    user: str
    schema: dict
    # 元数据（非提示之一部分，便于后续处理）
    meta: dict = field(default_factory=dict)


# ============================================================
# 一、章占位填充
# ============================================================

@dataclass
class 章占位结果:
    """LLM 填出之一章结构化内容。"""
    页文转录: list[dict] = field(default_factory=list)  # [{page, text}] — 双方逻辑之资·先文后理
    核心概念: list[dict] = field(default_factory=list)  # [{name, def_, key_point}]
    关键公式: list[dict] = field(default_factory=list)  # [{formula, meaning}]
    重要案例: list[str] = field(default_factory=list)
    高频考点: list[str] = field(default_factory=list)
    思考题: list[dict] = field(default_factory=list)   # [{q, a}]
    与他章关联: dict = field(default_factory=dict)     # {承前, 启后, 跨章}
    raw: Any = None  # 原 LLM 返


class 章占位填充任务:
    """给一章之主版图 + 元信息 → 返结构化复习要点。"""

    SYSTEM = """你是一位严谨之课程复习助教。
原则：
  1. **严守图中**——所述皆据所给图像之实，不臆造。
  2. **结构化**——按所给 schema 返 JSON，键名必符。
  3. **要而不繁**——后六项每项精炼，名词解释 1-2 句，公式给原式 + 含义。
  4. **抓核心**——若图量大，优先抓"必背名词、必记公式、典型例题"。
  5. **图未及之处可注"图中未见"**——不强填、不臆补。
  6. **先文后理**——先逐页录图中可见之文（标题/正文/公式/坐标/图注），原文照录、不释义、不增删；纯图表无字之页可简述图意（如"流程图：A→B→C"或"柱状图：x 轴 Y 轴 ..."）。此为"双方逻辑之资"之底骨。
  7. **页号严守**——`页文转录` 之 `page` 必为图序号（1 始），不可错位。"""

    SCHEMA_HINT = {
        "页文转录": [
            {"page": 1, "text": "本页可见之文字（原文照录·标题/正文/公式/坐标/图注）·纯图表则简述图意"}
        ],
        "核心概念": [
            {"name": "概念名", "def_": "1-2 句定义", "key_point": "记忆要点（可空）"}
        ],
        "关键公式": [
            {"formula": "原式（用 LaTeX 或纯文本）", "meaning": "含义/用法"}
        ],
        "重要案例": ["案例描述（含数字与结论）"],
        "高频考点": ["速记要点（一句一条，10 条以内）"],
        "思考题": [
            {"q": "题面", "a": "答（含要点）"}
        ],
        "与他章关联": {
            "承前": "本章接续何章何处",
            "启后": "本章为何章何处奠基",
            "跨章": "本章涉他章之处（可空）"
        }
    }

    @classmethod
    def build(
        cls,
        *,
        course: str,
        chap_label: str,
        chap_title: str,
        page_count: int,
        teacher: str = "",
        semester: str = "",
        existing_notes: str = "",
        cross_chapters: Optional[list[int]] = None,
    ) -> 提示任务:
        """组任务。images 由调用方在 chat 时附。"""
        cross_str = ""
        if cross_chapters:
            cross_str = f"\n本章另涉第 {', '.join(map(str, cross_chapters))} 章之内容。"
        notes_str = ""
        if existing_notes.strip():
            notes_str = f"\n\n【已有笔记参考（可补充/校正）】\n{existing_notes}"

        user = f"""【课程】{course} · {teacher} · {semester}
【章节】{chap_label} · {chap_title}
【主版页数】{page_count}{cross_str}

请据所附主版图像（按页序排），按 schema 返**JSON**。

【先文后理】
  - **页文转录**：每页一条 `{{"page": N, "text": "..."}}`·N 自 1 起·"text" 照录本页可见文字（不臆造、不释义、不删冗）·纯图表则简述图意·此为底骨
  - 后六项：据所录与所见，提炼为复习要点

要点（后六项）：
  - 核心概念：12 条以内，每条 1-2 句
  - 关键公式：必备者，含原式与含义
  - 重要案例：3-5 个典型
  - 高频考点：10 条以内速记
  - 思考题：3-5 题（含答）
  - 与他章关联：承前启后简述{notes_str}"""

        return 提示任务(
            system=cls.SYSTEM,
            user=user,
            schema=cls.SCHEMA_HINT,
            meta={
                "task": "章占位填充",
                "course": course,
                "chap": chap_label,
                "title": chap_title,
                "page_count": page_count,
            },
        )

    @staticmethod
    def parse(raw: Any) -> 章占位结果:
        """LLM 返之 dict → 章占位结果"""
        if not isinstance(raw, dict):
            return 章占位结果(raw=raw)
        return 章占位结果(
            页文转录=raw.get("页文转录") or [],
            核心概念=raw.get("核心概念") or [],
            关键公式=raw.get("关键公式") or [],
            重要案例=raw.get("重要案例") or [],
            高频考点=raw.get("高频考点") or [],
            思考题=raw.get("思考题") or [],
            与他章关联=raw.get("与他章关联") or {},
            raw=raw,
        )

    @staticmethod
    def apply_page_texts(doc_json_path: Any, 页文转录: list[dict]) -> tuple[int, int]:
        """把 LLM 录之页文，回填到 _doc.json 之 pages[*].embedded_text。

        道法：「双方逻辑之资」之文层落于 _doc.json，则
              · 主公得可搜可索可摘之文
              · agent 下次入提示无需独靠图
              · 素材 md 自动展之（折叠·不污要点之净）

        Args:
            doc_json_path: _doc.json 路径（Path 或 str 皆可）
            页文转录: LLM 返之 [{page, text}, ...]

        Returns:
            (更新页数, 总页数). 不存或解析失败返 (0, 0)。
        """
        from pathlib import Path as _P
        # 共用之器（避免循环 import）
        import sys as _sys
        _here = _P(__file__).resolve().parent
        if str(_here) not in _sys.path:
            _sys.path.insert(0, str(_here))
        from _yc_common import read_json, write_json  # noqa: E402

        doc_path = _P(str(doc_json_path))
        meta = read_json(doc_path)
        if not meta or not isinstance(meta, dict):
            return 0, 0

        pages = meta.get("pages", [])
        if not pages:
            return 0, 0

        # 索引化：page 号 → text
        txt_map: dict[int, str] = {}
        for item in 页文转录 or []:
            if not isinstance(item, dict):
                continue
            try:
                n = int(item.get("page", 0))
                t = (item.get("text") or "").strip()
                if n > 0 and t:
                    txt_map[n] = t
            except (TypeError, ValueError):
                continue

        if not txt_map:
            return 0, len(pages)

        updated = 0
        for p in pages:
            idx = p.get("index", 0)
            if idx in txt_map:
                p["embedded_text"] = txt_map[idx]
                updated += 1

        if updated:
            write_json(doc_path, meta)
        return updated, len(pages)

    @staticmethod
    def render_md(result: 章占位结果) -> str:
        """章占位结果 → 替换"复习占位"区块之 markdown。"""
        lines: list[str] = []
        lines.append("## 复习要点 · LLM 协填")
        lines.append("")

        # 一、核心概念
        lines.append("### 一、核心概念")
        lines.append("")
        if result.核心概念:
            for c in result.核心概念:
                if isinstance(c, dict):
                    name = c.get("name", "?")
                    df = c.get("def_") or c.get("def", "")
                    kp = c.get("key_point", "")
                    line = f"- **{name}**：{df}"
                    if kp:
                        line += f"  *（要：{kp}）*"
                    lines.append(line)
                else:
                    lines.append(f"- {c}")
        else:
            lines.append("- （LLM 未填）")
        lines.append("")

        # 二、公式
        lines.append("### 二、关键公式 / 模型")
        lines.append("")
        if result.关键公式:
            lines.append("| 公式 | 含义 |")
            lines.append("|------|------|")
            for f in result.关键公式:
                if isinstance(f, dict):
                    formula = f.get("formula", "")
                    meaning = f.get("meaning", "")
                    lines.append(f"| `{formula}` | {meaning} |")
                else:
                    lines.append(f"| `{f}` | |")
        else:
            lines.append("- （LLM 未填）")
        lines.append("")

        # 三、案例
        lines.append("### 三、重要案例 / 例题")
        lines.append("")
        if result.重要案例:
            for case in result.重要案例:
                lines.append(f"- {case}")
        else:
            lines.append("- （LLM 未填）")
        lines.append("")

        # 四、考点
        lines.append("### 四、高频考点（速记）")
        lines.append("")
        if result.高频考点:
            for i, kp in enumerate(result.高频考点, 1):
                lines.append(f"{i}. {kp}")
        else:
            lines.append("1. （LLM 未填）")
        lines.append("")

        # 五、思考题
        lines.append("### 五、思考题 / 自测")
        lines.append("")
        if result.思考题:
            for q in result.思考题:
                if isinstance(q, dict):
                    qtext = q.get("q", "")
                    atext = q.get("a", "")
                    lines.append(f"- **Q**：{qtext}")
                    lines.append(f"  **A**：{atext}")
                    lines.append("")
                else:
                    lines.append(f"- {q}")
        else:
            lines.append("- （LLM 未填）")
        lines.append("")

        # 六、关联
        lines.append("### 六、与前后章之关联")
        lines.append("")
        rel = result.与他章关联 or {}
        if rel:
            for k in ("承前", "启后", "跨章"):
                v = rel.get(k, "")
                if v:
                    lines.append(f"- **{k}**：{v}")
        else:
            lines.append("- 承前：")
            lines.append("- 启后：")
        lines.append("")

        return "\n".join(lines)


# ============================================================
# 二、速查行（一章一行紧凑速记）
# ============================================================

@dataclass
class 速查行结果:
    核心: str = ""    # 1 句话述本章核心
    必记公式: list[str] = field(default_factory=list)
    易混: str = ""    # 易混点速记
    必考: list[str] = field(default_factory=list)
    raw: Any = None


class 速查行任务:
    """一章 → 一行（用于全课速查表）"""

    SYSTEM = """你是简练之速记助教。每章压缩为一行表。
原则：核心 1 句、公式必备 2-3 条、易混 1 句、必考 3 条。极简，不冗余。"""

    SCHEMA_HINT = {
        "核心": "本章核心（≤30 字）",
        "必记公式": ["最多 3 条"],
        "易混": "易混点 1 句",
        "必考": ["3 条速记"]
    }

    @classmethod
    def build(
        cls,
        *,
        course: str,
        chap_label: str,
        chap_title: str,
        existing_notes: str = "",
    ) -> 提示任务:
        notes = ""
        if existing_notes:
            notes = f"\n\n【已有笔记】\n{existing_notes[:3000]}"  # 限 3k 避太长

        user = f"""【课程】{course}
【章节】{chap_label} · {chap_title}

按 schema 返 JSON，要极简，作期末速查表一行用。{notes}"""

        return 提示任务(
            system=cls.SYSTEM,
            user=user,
            schema=cls.SCHEMA_HINT,
            meta={"task": "速查行", "course": course, "chap": chap_label, "title": chap_title},
        )

    @staticmethod
    def parse(raw: Any) -> 速查行结果:
        if not isinstance(raw, dict):
            return 速查行结果(raw=raw)
        return 速查行结果(
            核心=raw.get("核心", ""),
            必记公式=raw.get("必记公式") or [],
            易混=raw.get("易混", ""),
            必考=raw.get("必考") or [],
            raw=raw,
        )


# ============================================================
# 三、期末模拟卷
# ============================================================

@dataclass
class 模拟卷结果:
    选择题: list[dict] = field(default_factory=list)  # [{q, options, answer, explain}]
    填空题: list[dict] = field(default_factory=list)
    名词解释: list[dict] = field(default_factory=list)
    简答题: list[dict] = field(default_factory=list)
    论述题: list[dict] = field(default_factory=list)
    raw: Any = None


class 模拟卷任务:
    """一课 → 一卷期末模拟"""

    SYSTEM = """你是经验丰富之命题助教。据所给课程章节素材，命一份期末模拟卷。
原则：
  1. 题目覆盖各章节，重点章节多分
  2. 选择题含干扰项，答与解释皆备
  3. 简答 / 论述题给出标答要点（不必全文）
  4. 难度梯度：基础 60%、中等 30%、综合 10%"""

    SCHEMA_HINT = {
        "选择题": [
            {"q": "题干", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "answer": "A", "explain": "解析"}
        ],
        "填空题": [{"q": "题干（用 ___ 标空）", "answer": "答"}],
        "名词解释": [{"q": "名词", "answer": "解释要点"}],
        "简答题": [{"q": "题面", "answer": "答要点"}],
        "论述题": [{"q": "题面", "answer": "答框架"}]
    }

    @classmethod
    def build(
        cls,
        *,
        course: str,
        chap_summary: str,
        题型分布: Optional[dict] = None,
    ) -> 提示任务:
        dist = 题型分布 or {
            "选择题": 10,
            "填空题": 5,
            "名词解释": 4,
            "简答题": 3,
            "论述题": 1,
        }
        dist_str = "、".join(f"{k}{v}" for k, v in dist.items())

        user = f"""【课程】{course}

【章节素材】
{chap_summary[:8000]}

请命题，分布：{dist_str}。
按 schema 返 JSON。"""

        return 提示任务(
            system=cls.SYSTEM,
            user=user,
            schema=cls.SCHEMA_HINT,
            meta={"task": "模拟卷", "course": course, "dist": dist},
        )

    @staticmethod
    def parse(raw: Any) -> 模拟卷结果:
        if not isinstance(raw, dict):
            return 模拟卷结果(raw=raw)
        return 模拟卷结果(
            选择题=raw.get("选择题") or [],
            填空题=raw.get("填空题") or [],
            名词解释=raw.get("名词解释") or [],
            简答题=raw.get("简答题") or [],
            论述题=raw.get("论述题") or [],
            raw=raw,
        )


# ============================================================
# 四、思维导图（markmap + mermaid 双格式）
# ============================================================

@dataclass
class 思维导图结果:
    """LLM 生成之章节思维导图（双格式）。"""
    标题: str = ""
    markmap: str = ""   # markmap markdown 格式（兼容 Typora / markmap.js）
    mermaid: str = ""   # mermaid mindmap 格式（兼容 GitHub Markdown）
    raw: Any = None


class 思维导图任务:
    """据章节复习要点 → 生成 markmap + mermaid 思维导图。

    道法：知识树者，道之象也。层层分解，万枝归一干。
    markmap 与 mermaid 双格式：一可本地渲染，一可 GitHub 渲染。
    """

    SYSTEM = """你是知识结构化专家，专注构建层次清晰的思维导图。
原则：
  1. **Markmap 格式**（markdown 缩进列表·兼容 markmap.js/Typora/Obsidian）
     - 顶层 `# 章标题`；二层 `##` 核心主题（3-7 个）；三层 `###` 子概念；四层 `-` 要点
     - 每节点 ≤ 20 字；避免括号、引号等特殊字符嵌套
  2. **Mermaid mindmap 格式**（兼容 GitHub Markdown 代码块渲染）
     - 首行 `mindmap`；root 节点双括号；子节点用缩进
     - 节点文字 ≤ 15 字
  3. **覆盖**：核心概念 / 关键公式（如有）/ 重要结论 / 高频考点
  4. **忠实**：只梳理已给材料之内容，不臆造；图中未涉及之内容可留空
  5. **结构完整**：层次清晰，不遗漏主线知识点"""

    SCHEMA_HINT = {
        "标题": "章节标题（如 第3章 污染物的生物转运）",
        "markmap": (
            "# 章标题\n"
            "## 核心概念\n"
            "### 概念A\n"
            "- 要点1\n"
            "- 要点2\n"
            "### 概念B\n"
            "## 关键公式\n"
            "### 公式名\n"
            "- 表达式\n"
            "- 适用条件\n"
            "## 高频考点\n"
            "- 考点1\n"
            "- 考点2\n"
        ),
        "mermaid": (
            "mindmap\n"
            "  root((章标题))\n"
            "    核心概念\n"
            "      概念A\n"
            "        要点1\n"
            "      概念B\n"
            "    关键公式\n"
            "      公式名\n"
            "    高频考点\n"
            "      考点1\n"
        ),
    }

    @classmethod
    def build(
        cls,
        *,
        course: str,
        chap_label: str,
        chap_title: str,
        review_content: str = "",
        teacher: str = "",
        semester: str = "",
    ) -> 提示任务:
        """构造思维导图生成任务。review_content 为章节已填复习要点（可空）。"""
        ctx_parts: list[str] = [
            f"【课程】{course}" + (f" · {teacher} · {semester}" if teacher else ""),
            f"【章节】{chap_label} · {chap_title}",
        ]
        if review_content.strip():
            # 截取前 6000 字，避免超窗
            ctx_parts.append(f"\n【章节复习要点（已填）】\n{review_content.strip()[:6000]}")
        ctx_parts.append(
            "\n请据以上内容，生成该章节思维导图（markmap + mermaid 两种格式）。"
            "按 schema 返 JSON，markmap / mermaid 字段均为多行字符串。"
        )

        return 提示任务(
            system=cls.SYSTEM,
            user="\n".join(ctx_parts),
            schema=cls.SCHEMA_HINT,
            meta={
                "task": "思维导图",
                "course": course,
                "chap": chap_label,
                "title": chap_title,
            },
        )

    @staticmethod
    def parse(raw: Any) -> 思维导图结果:
        if not isinstance(raw, dict):
            return 思维导图结果(raw=raw)
        return 思维导图结果(
            标题=raw.get("标题", ""),
            markmap=(raw.get("markmap") or "").strip(),
            mermaid=(raw.get("mermaid") or "").strip(),
            raw=raw,
        )

    @staticmethod
    def render_md(result: 思维导图结果) -> str:
        """思维导图结果 → 替换/填充「思维导图」区块之 markdown。"""
        lines: list[str] = []
        lines.append("## 思维导图 · LLM 生成")
        lines.append("")

        if result.markmap:
            lines.append("### Markmap（Typora / markmap.js / Obsidian 可渲染）")
            lines.append("")
            lines.append("```markmap")
            lines.append(result.markmap)
            lines.append("```")
            lines.append("")

        if result.mermaid:
            lines.append("### Mermaid（GitHub Markdown 可渲染）")
            lines.append("")
            lines.append("```mermaid")
            lines.append(result.mermaid)
            lines.append("```")
            lines.append("")

        if not result.markmap and not result.mermaid:
            lines.append("- （LLM 未填）")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def render_placeholder(chap_label: str, chap_title: str) -> str:
        """生成空白占位（素材初生时使用）。"""
        lines: list[str] = []
        lines.append("## 思维导图占位 · 待 LLM 生成")
        lines.append("")
        lines.append("> 可通过「图谱」关自动生成，或手填 markmap/mermaid 格式后重生素材。")
        lines.append("")
        lines.append("```markmap")
        lines.append(f"# {chap_label} · {chap_title}")
        lines.append("  - 待填（运行「图谱」关自动生成）")
        lines.append("```")
        lines.append("")
        return "\n".join(lines)


# ============================================================
# 五、注册表（便后续按名取）
# ============================================================

任务注册 = {
    "章占位": 章占位填充任务,
    "速查行": 速查行任务,
    "模拟卷": 模拟卷任务,
    "思维导图": 思维导图任务,
}


# ============================================================
# 五、自测
# ============================================================

if __name__ == "__main__":
    import json

    # 1. 章占位任务
    t1 = 章占位填充任务.build(
        course="环境毒理学",
        chap_label="第 3 章",
        chap_title="污染物的生物转运",
        page_count=51,
        teacher="森巴提·叶尔肯",
        semester="2026春",
        cross_chapters=[2],
    )
    print("== 章占位填充任务 ==")
    print(f"  system: {len(t1.system)} 字")
    print(f"  user:   {len(t1.user)} 字")
    print(f"  schema: {list(t1.schema.keys())}")

    # 2. 用假 raw 测 parse
    fake_raw = {
        "核心概念": [{"name": "生物转运", "def_": "污染物经各途径同生物体接触而被吸收、分布、排泄之总称。"}],
        "关键公式": [{"formula": "T₁/₂ = 0.693/K", "meaning": "半衰期与速率常数换算"}],
        "重要案例": ["铅蓄积于骨骼"],
        "高频考点": ["主动转运五特点：逆/耗能/载体/选择/竞争抑制"],
        "思考题": [{"q": "肝肠循环之毒理学意义？", "a": "延长体内停留→半衰期延长→毒性加大"}],
        "与他章关联": {"承前": "第 2 章 迁移转化", "启后": "第 4 章 毒作用"},
    }
    res = 章占位填充任务.parse(fake_raw)
    print(f"  parse:  概念 {len(res.核心概念)}, 公式 {len(res.关键公式)}, 考点 {len(res.高频考点)}")
    md = 章占位填充任务.render_md(res)
    print(f"  render → {len(md)} 字 markdown")

    # 3. 速查行
    t2 = 速查行任务.build(course="环境毒理学", chap_label="第 1 章", chap_title="绪论")
    print(f"\n== 速查行任务 ==")
    print(f"  user: {len(t2.user)} 字")

    # 4. 模拟卷
    t3 = 模拟卷任务.build(course="环境毒理学", chap_summary="（章节素材集合略）"*100)
    print(f"\n== 模拟卷任务 ==")
    print(f"  user: {len(t3.user)} 字（已截至 8000）")

    print(f"\n注册之任务: {list(任务注册.keys())}")
