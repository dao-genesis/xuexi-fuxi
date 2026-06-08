# -*- coding: utf-8 -*-
"""
图 道 (img_dao)  ——  大方无隅，大器免成

道法：
    LLM 视觉之入，图也。然图大、图繁、图众则 token 涌：
    一页 1920×1080 之主版图，原态喂 LLM 约费数千 token。
    一章 80 页则数十万 token，钱与上下文皆不支。

    此关之器：
      1. 缩 ──  保信息之要，去冗余之大；
      2. 拼 ──  众小成一大，省协议开销；
      3. 分 ──  长章分批，亦不失节次；
      4. 量 ──  粗估 token，预防爆窗。

依赖:
    pip install pillow  （已装）

用法:
    from _图_道 import 缩图, 拼网格, 分批喂图

    缩图("page_001.jpg", out="...", max_dim=1568)
    拼网格(["p1.jpg","p2.jpg",...], out="grid.jpg", cols=3, cell=512)
    for batch in 分批喂图(image_paths, max_per_batch=20):
        cli.chat(prompt, images=batch)
"""

from __future__ import annotations

import io
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Optional, Union

from PIL import Image


# ============================================================
# 一、单图缩 / 转
# ============================================================

def 缩图(
    src: Union[str, Path, bytes, Image.Image],
    *,
    max_dim: int = 1568,
    quality: int = 85,
    fmt: str = "JPEG",
    out: Optional[Union[str, Path]] = None,
) -> bytes:
    """图缩到长边 ≤ max_dim。保 aspect。

    src: 路径 / bytes / PIL Image
    out: 若给则写盘，否则仅返 bytes
    返: 编码后之 bytes（可直喂 LLM 之 base64 input）

    道：max_dim=1568 取 OpenAI Vision 之"高细"档（≤2048）之余。
        小图（< max_dim）不放大，仅原样转码。
    """
    img = _load_image(src)

    # 缩
    w, h = img.size
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        new_size = (int(w * scale), int(h * scale))
        img = img.resize(new_size, Image.LANCZOS)

    # 转 RGB（去 alpha，避免 JPEG 异）
    if fmt.upper() == "JPEG" and img.mode != "RGB":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode in ("RGBA", "LA"):
            bg.paste(img, mask=img.split()[-1])
        else:
            bg.paste(img)
        img = bg

    buf = io.BytesIO()
    save_kwargs = {}
    if fmt.upper() == "JPEG":
        save_kwargs.update(quality=quality, optimize=True)
    img.save(buf, format=fmt, **save_kwargs)
    data = buf.getvalue()

    if out:
        out_path = Path(out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(data)

    return data


def _load_image(src: Union[str, Path, bytes, Image.Image]) -> Image.Image:
    if isinstance(src, Image.Image):
        return src
    if isinstance(src, bytes):
        return Image.open(io.BytesIO(src))
    return Image.open(Path(src))


# ============================================================
# 二、拼网格（众小成一大）
# ============================================================

def 拼网格(
    images: Iterable[Union[str, Path, bytes, Image.Image]],
    *,
    cols: int = 3,
    cell: int = 512,
    gap: int = 8,
    bg: tuple[int, int, int] = (255, 255, 255),
    label: bool = True,
    label_pad: int = 28,
    out: Optional[Union[str, Path]] = None,
    quality: int = 85,
) -> bytes:
    """多图拼为网格，每格 cell×cell（缩入），加序号标。

    label=True 时每格上方留 label_pad 像素之白条，写"p1, p2, ..."。

    返：JPEG bytes
    """
    imgs = [_load_image(s) for s in images]
    n = len(imgs)
    if n == 0:
        raise ValueError("无图可拼")

    rows = math.ceil(n / cols)
    # 每格之实际高（含 label 区）
    cell_h = cell + (label_pad if label else 0)

    grid_w = cols * cell + (cols + 1) * gap
    grid_h = rows * cell_h + (rows + 1) * gap

    canvas = Image.new("RGB", (grid_w, grid_h), bg)

    if label:
        from PIL import ImageDraw
        draw = ImageDraw.Draw(canvas)
        try:
            from PIL import ImageFont
            font = ImageFont.load_default()
        except Exception:
            font = None

    for i, im in enumerate(imgs):
        r, c = divmod(i, cols)
        # 缩单图入 cell×cell
        im2 = im.copy()
        im2.thumbnail((cell, cell), Image.LANCZOS)
        # 转 RGB
        if im2.mode != "RGB":
            tmp = Image.new("RGB", im2.size, bg)
            if im2.mode in ("RGBA", "LA"):
                tmp.paste(im2, mask=im2.split()[-1])
            else:
                tmp.paste(im2)
            im2 = tmp

        # 定位（cell 内居中）
        x0 = gap + c * (cell + gap)
        y0_label = gap + r * (cell_h + gap)
        y0 = y0_label + (label_pad if label else 0)
        # 居中
        cx = x0 + (cell - im2.width) // 2
        cy = y0 + (cell - im2.height) // 2
        canvas.paste(im2, (cx, cy))

        if label and font is not None:
            draw.text((x0 + 4, y0_label + 4), f"p{i+1}", fill=(80, 80, 80), font=font)

    buf = io.BytesIO()
    canvas.save(buf, format="JPEG", quality=quality, optimize=True)
    data = buf.getvalue()

    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_bytes(data)

    return data


# ============================================================
# 三、分批
# ============================================================

@dataclass
class ImageBatch:
    """一批图。"""
    index: int        # 第几批（0 起）
    total: int        # 共几批
    indices: list[int]  # 本批对应之原始 page 序号（0 起）
    paths: list[Path]


def 分批喂图(
    image_paths: list[Union[str, Path]],
    *,
    max_per_batch: int = 20,
) -> Iterator[ImageBatch]:
    """将一长串图分为 ≤ max_per_batch 之批。

    用例：
        for batch in 分批喂图(pages, max_per_batch=20):
            cli.chat_json(
                f"批 {batch.index+1}/{batch.total}, 含 p{batch.indices[0]+1}..p{batch.indices[-1]+1}：\\n" + prompt,
                images=batch.paths,
            )
    """
    paths = [Path(p) for p in image_paths]
    n = len(paths)
    if n == 0:
        return
    total = math.ceil(n / max_per_batch)
    for bi in range(total):
        lo = bi * max_per_batch
        hi = min(lo + max_per_batch, n)
        yield ImageBatch(
            index=bi,
            total=total,
            indices=list(range(lo, hi)),
            paths=paths[lo:hi],
        )


# ============================================================
# 四、token 估算（粗）
# ============================================================

def 估_图_tokens(
    image: Union[str, Path, bytes, Image.Image],
    *,
    detail: str = "high",
) -> int:
    """粗估单图之 token 数（OpenAI Vision 公式）。

    low:   85 token (固定)
    high:  170 token × 每 512×512 块 + 85 base
    返：int
    """
    if detail == "low":
        return 85

    img = _load_image(image)
    w, h = img.size
    # 先缩到 ≤2048×2048 之大边
    if max(w, h) > 2048:
        scale = 2048 / max(w, h)
        w = int(w * scale)
        h = int(h * scale)
    # 再缩到短边 ≤ 768
    if min(w, h) > 768:
        scale = 768 / min(w, h)
        w = int(w * scale)
        h = int(h * scale)

    blocks_w = math.ceil(w / 512)
    blocks_h = math.ceil(h / 512)
    return 85 + 170 * blocks_w * blocks_h


def 估_批_tokens(
    image_paths: list[Union[str, Path]],
    *,
    detail: str = "high",
) -> dict:
    """估算一批图之总 token。"""
    per: list[int] = []
    for p in image_paths:
        try:
            per.append(估_图_tokens(p, detail=detail))
        except Exception:
            per.append(0)
    return {
        "count": len(per),
        "total_tokens_est": sum(per),
        "avg_tokens_est": sum(per) // max(1, len(per)),
        "per_image": per,
    }


# ============================================================
# 五、自测
# ============================================================

if __name__ == "__main__":
    import sys

    # 找一张测试图（环境毒理学 主版第一页）
    test_root = Path(__file__).parent / "解析仓库" / "环境毒理学-2026春-090963-001-森巴提·叶尔肯"
    test_dirs = sorted([d for d in test_root.glob("*") if d.is_dir() and d.name.startswith("00")]) if test_root.exists() else []
    if not test_dirs:
        print("× 测试样本未备（解析仓库未生成或环境毒理学不在）")
        sys.exit(0)

    pdf_dir = test_dirs[0]
    pages = sorted(pdf_dir.glob("page_*.jpg"))[:9]
    if not pages:
        print("× 无 page_*.jpg")
        sys.exit(0)

    print(f"测试图来源: {pdf_dir.name}, {len(pages)} 页")

    # 1. 缩
    out_dir = Path(__file__).parent / ".图道_测试"
    out_dir.mkdir(exist_ok=True)
    data = 缩图(pages[0], max_dim=1024, out=out_dir / "p001_small.jpg")
    print(f"缩图: {pages[0].name} {pages[0].stat().st_size//1024} KiB → {len(data)//1024} KiB (max=1024)")

    # 2. 拼网格
    grid_data = 拼网格(pages, cols=3, cell=384, out=out_dir / "grid.jpg")
    print(f"拼网格: 9 图 → grid.jpg {len(grid_data)//1024} KiB")

    # 3. 分批
    paths_long = pages * 5  # 45 张
    batches = list(分批喂图(paths_long, max_per_batch=20))
    print(f"分批 (45 张, 20/批): {len(batches)} 批: {[len(b.paths) for b in batches]}")

    # 4. 估 token
    est = 估_批_tokens(pages, detail="high")
    print(f"估 token (9 张 high): 总 {est['total_tokens_est']}, 均 {est['avg_tokens_est']}/图")
    est_low = 估_批_tokens(pages, detail="low")
    print(f"估 token (9 张 low):  总 {est_low['total_tokens_est']}")

    # 5. 拼图代价
    grid_path = out_dir / "grid.jpg"
    grid_est = 估_图_tokens(grid_path, detail="high")
    print(f"拼图 grid.jpg (一张) high token: {grid_est}  ← 比单图×9 ({est['total_tokens_est']}) 省 {est['total_tokens_est']-grid_est}")

    print(f"\n样本写于: {out_dir}")
