# -*- coding: utf-8 -*-
"""
学习科学 (learning_science)  ——  道之本源，落于实证

道法：
    复习之效，非在多读多抄（高亮/重读/摘抄 效用低），
    而在 **提取练习**（自测）与 **间隔重复**（分散练习）——此二者效用最高。
    （Dunlosky et al. 2013, Psych. Sci. Public Interest;
      Carpenter, Pan & Butler 2022, Nature Reviews Psychology）

此模块为纯函数之器（不触 LLM、不触磁盘），供上层驱动调用：
    · 间隔重排程   —— 按考试日反推的间隔重复日历（1/3/7/14 天）
    · 交错复习序   —— 跨章混合刷题顺序（interleaving）
    · 生成填空卡   —— cloze 卡（提取练习之轻形）
    · 生成自测项   —— 概念/公式 → 提取式问答（答案默藏）
    · 备考阶段     —— 通读→提取→模考 三段

一处定之，全链路可引。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


# ============================================================
# 〇、证据常量（可引用·可展示）
# ============================================================

# 效用评级（Dunlosky 2013）：高 / 中 / 低
学习技法效用 = {
    "练习测验·提取练习": "高",   # practice testing / retrieval practice
    "分散练习·间隔重复": "高",   # distributed practice / spacing
    "交错练习": "中",            # interleaved practice
    "自我解释": "中",            # self-explanation
    "详尽追问": "中",            # elaborative interrogation
    "双重编码·图像": "中",       # dual coding / imagery
    "高亮": "低",
    "重读": "低",
    "摘抄·概述": "低",
}

# 间隔重复之默认触点（首学日为 0，其后复习偏移天数）
默认间隔 = [1, 3, 7, 14]


# ============================================================
# 一、备考阶段（通读 → 提取 → 模考）
# ============================================================

@dataclass
class 阶段:
    名: str
    始: date
    末: date
    要旨: str

    @property
    def 天数(self) -> int:
        return (self.末 - self.始).days + 1


def 备考阶段(今日: date, 考试日: date) -> list[阶段]:
    """把可用天数切为三段：通读理解 / 提取自测 / 查漏模考。

    道法：先求其义（通读·双重编码），次以测验固之（提取），
          终以模卷验之（交错·实战）。窗口越短，后两段越重。
    """
    总天 = (考试日 - 今日).days
    if 总天 <= 0:
        # 临考当日：全力提取 + 模考
        return [阶段("冲刺·提取与模考", 今日, 考试日, "只做自测题与模拟卷，不再通读")]
    if 总天 <= 3:
        中 = 今日 + timedelta(days=1)
        return [
            阶段("速读·抓骨架", 今日, 今日, "只看每章总纲与高频考点，不抠细节"),
            阶段("提取·自测", 中, 考试日 - timedelta(days=1) if 总天 >= 2 else 考试日, "闭卷自测 + 看错题"),
            阶段("模考·查漏", 考试日, 考试日, "限时模拟卷 + 错点回看"),
        ]
    # 一般：通读约 50%，提取约 35%，模考约 15%（至少各 1 天）
    通读末 = 今日 + timedelta(days=max(1, round(总天 * 0.5)))
    提取末 = 通读末 + timedelta(days=max(1, round(总天 * 0.35)))
    if 提取末 >= 考试日:
        提取末 = 考试日 - timedelta(days=1)
    return [
        阶段("一轮·通读理解", 今日, 通读末, "逐章通读图文 + 画/看思维导图，求懂而非背"),
        阶段("二轮·提取自测", 通读末 + timedelta(days=1), 提取末, "闭卷做自测题与填空卡，错题标记"),
        阶段("三轮·模考查漏", 提取末 + timedelta(days=1), 考试日, "限时模拟卷 + 错点专项 + 易错点重背"),
    ]


# ============================================================
# 二、间隔重排程（spaced repetition calendar）
# ============================================================

@dataclass
class 日程项:
    日期: date
    任务: list[str] = field(default_factory=list)


def 间隔重排程(
    章节标签: list[str],
    今日: date,
    考试日: date,
    间隔: Optional[list[int]] = None,
) -> list[日程项]:
    """生成按日的间隔重复复习日历。

    道法（分散练习）：每章首学之后，于 +1/+3/+7/+14 天各提取一次；
          触点落在考试日之后者，前移到考试前一日（不浪费、不越界）。
          首学日把各章均摊于前半窗口，避免"临考才开工"。

    Args:
        章节标签: 形如 ["第1章 绪论", "第2章 ..."]
        今日 / 考试日: date
        间隔: 复习偏移天数（默认 [1,3,7,14]）

    Returns:
        按日期升序的 [日程项]，仅含考试日（含）之前有任务之日。
    """
    间隔 = 间隔 or 默认间隔
    总天 = (考试日 - 今日).days
    n = len(章节标签)
    if n == 0:
        return []
    议程: dict[date, list[str]] = {}

    def _记(d: date, 文: str) -> None:
        if d < 今日:
            d = 今日
        if d > 考试日:
            d = 考试日 - timedelta(days=1) if 总天 >= 1 else 考试日
        议程.setdefault(d, [])
        if 文 not in 议程[d]:
            议程[d].append(文)

    # 首学日：均摊于前半窗口（至少占 1 天间距）
    首学窗 = max(1, 总天 // 2) if 总天 > 0 else 0
    for i, 章 in enumerate(章节标签):
        off = round(i * 首学窗 / max(1, n)) if 总天 > 0 else 0
        d0 = 今日 + timedelta(days=off)
        _记(d0, f"📖 首学：{章}")
        for k in 间隔:
            _记(d0 + timedelta(days=k), f"🔁 提取复习：{章}")

    return [日程项(d, 议程[d]) for d in sorted(议程)]


# ============================================================
# 三、交错复习序（interleaving）
# ============================================================

def 交错复习序(章节标签: list[str], 轮数: int = 3) -> list[list[str]]:
    """生成交错（而非按章顺序集中）的多轮刷题序。

    道法：集中练一章易生"会了"之错觉；交错混合更近真实考试，
          迫使大脑每题先辨"这是哪类"，提取更深。
          各轮以不同起点轮转，避免每轮同序。
    """
    n = len(章节标签)
    if n == 0:
        return []
    轮: list[list[str]] = []
    for r in range(max(1, 轮数)):
        起 = r % n
        轮.append([章节标签[(起 + j) % n] for j in range(n)])
    return 轮


# ============================================================
# 四、提取练习生成器（cloze 卡 / 自测项）
# ============================================================

# 句中"关键词：定义"或"关键词 是 ..."的简单切分
_DEF_SPLIT = re.compile(r"[：:]\s*|\s+是\s+|\s+指\s+|\s+为\s+")


def 生成填空卡(条目: list[str], 每条最多挖空: int = 1) -> list[dict]:
    """把"名词：定义"式条目转为 cloze 填空卡（提取练习之轻形）。

    入：["内摩擦力：流体内部相邻流层间的切向阻力", ...]
    出：[{"正面": "____：流体内部相邻流层间的切向阻力", "背面": "内摩擦力"}, ...]
    若无法切出名词，则整条作背面、首句作提示。
    """
    卡: list[dict] = []
    for 条 in 条目:
        条 = (条 or "").strip()
        if not 条:
            continue
        parts = _DEF_SPLIT.split(条, maxsplit=1)
        if len(parts) == 2 and parts[0] and parts[1]:
            名, 释 = parts[0].strip(), parts[1].strip()
            卡.append({"正面": f"____：{释}", "背面": 名})
        else:
            卡.append({"正面": f"（回忆）{条[:18]}……", "背面": 条})
    return 卡


def 生成自测项(概念: list[dict]) -> list[dict]:
    """概念 dict（{name, def_, key_point}）→ 提取式问答（答案默藏）。

    道法：问"是什么/为什么/如何用"，迫使闭卷提取，而非重读。
    """
    项: list[dict] = []
    for c in 概念:
        名 = (c.get("name") or "").strip()
        if not 名:
            continue
        释 = (c.get("def_") or c.get("def") or "").strip()
        点 = (c.get("key_point") or "").strip()
        答 = 释 or 点 or "（见素材）"
        if 点 and 点 != 释:
            答 = f"{答}（要点：{点}）"
        项.append({"问": f"{名}是什么？为什么重要？", "答": 答})
    return 项


# ============================================================
# 五、自测
# ============================================================

def _自测() -> int:
    失败 = 0
    今 = date(2026, 6, 1)
    考 = date(2026, 6, 21)
    章 = [f"第{i}章" for i in range(1, 6)]

    # 备考阶段：三段且首尾衔接、不越界
    段 = 备考阶段(今, 考)
    assert len(段) == 3, 段
    assert 段[0].始 == 今 and 段[-1].末 == 考, 段
    for a, b in zip(段, 段[1:]):
        assert b.始 == a.末 + timedelta(days=1), (a, b)
    print("✓ 备考阶段：三段衔接、不越界")

    # 短窗：<=3 天不崩
    for d in (0, 1, 2, 3):
        段2 = 备考阶段(今, 今 + timedelta(days=d))
        assert 段2 and 段2[-1].末 <= 今 + timedelta(days=d), (d, 段2)
    print("✓ 备考阶段：短窗（0–3 天）稳健")

    # 间隔重排程：每章 1 次首学 + len(间隔) 次复习；不越考试日；按日升序
    程 = 间隔重排程(章, 今, 考)
    所有任务 = [t for it in 程 for t in it.任务]
    assert sum(1 for t in 所有任务 if t.startswith("📖")) == len(章), 所有任务
    assert all(it.日期 <= 考 for it in 程)
    assert 程 == sorted(程, key=lambda x: x.日期)
    print(f"✓ 间隔重排程：{len(程)} 个有任务日，首学 {len(章)} 章")

    # 边界：今日==考试日 不崩、不抛
    assert isinstance(间隔重排程(章, 考, 考), list)
    assert 间隔重排程([], 今, 考) == []
    print("✓ 间隔重排程：边界（空章/零窗）稳健")

    # 交错：每轮含全章、各轮起点不同
    轮 = 交错复习序(章, 轮数=3)
    assert len(轮) == 3 and all(sorted(r) == sorted(章) for r in 轮)
    assert 轮[0][0] != 轮[1][0], 轮
    print("✓ 交错复习序：各轮全覆盖、起点轮转")

    # 填空卡：能切名词
    卡 = 生成填空卡(["内摩擦力：流体内部相邻流层间的切向阻力", "无冒号整条"])
    assert 卡[0]["背面"] == "内摩擦力" and "____" in 卡[0]["正面"], 卡
    assert 卡[1]["背面"] == "无冒号整条"
    print("✓ 生成填空卡：名词挖空 / 兜底")

    # 自测项
    项 = 生成自测项([{"name": "雷诺数", "def_": "惯性力与黏性力之比", "key_point": "判别层流紊流"}])
    assert 项 and "雷诺数" in 项[0]["问"] and "层流" in 项[0]["答"], 项
    print("✓ 生成自测项：提取式问答")

    if 失败 == 0:
        print("\n全部自测通过 ✓")
    return 失败


if __name__ == "__main__":
    raise SystemExit(_自测())
