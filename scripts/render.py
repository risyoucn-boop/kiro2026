"""从 Iconify API 拉取 SVG body,按 3 种颜色批量渲染 256x256 PNG。

Iconify 返回的 JSON 形如:
  {
    "prefix": "material-symbols",
    "icons": {
      "home-rounded": {"body": "<path d=...>", "width": 24, "height": 24},
      ...
    }
  }
我们把 body 包装成完整 SVG 并指定 fill 颜色,然后用 cairosvg 光栅化。
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Dict, Tuple

import cairosvg
import requests

from icons import COLORS, ICONS

OUT_DIR = Path(__file__).resolve().parent.parent / "build" / "png"
PNG_SIZE = 256
ICONIFY_API = "https://api.iconify.design/{prefix}.json"


def _request_chunk(prefix: str, names: list[str]) -> dict:
    url = ICONIFY_API.format(prefix=prefix)
    r = requests.get(url, params={"icons": ",".join(names)}, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_svg_bodies() -> Dict[str, Tuple[str, int, int]]:
    """按 prefix 分组批量请求,返回 {iconify_id: (body, width, height)}。

    若某图标的 -rounded 变体缺失,会自动回退到去掉 -rounded 的基础名。
    最终的 key 仍是清单里声明的原 iconify_id,方便上层引用。
    """
    by_prefix: Dict[str, list[str]] = {}
    requested_to_id: Dict[str, str] = {}  # 实际请求名 -> 原 iconify_id
    for _, _, icon_id in ICONS:
        prefix, name = icon_id.split(":", 1)
        by_prefix.setdefault(prefix, []).append(name)
        requested_to_id[f"{prefix}:{name}"] = icon_id

    results: Dict[str, Tuple[str, int, int]] = {}

    for prefix, names in by_prefix.items():
        default_w, default_h = 24, 24
        found: Dict[str, dict] = {}
        # 第一轮:批量请求原名
        for i in range(0, len(names), 50):
            chunk = names[i : i + 50]
            data = _request_chunk(prefix, chunk)
            default_w = data.get("width", default_w)
            default_h = data.get("height", default_h)
            for n, info in data.get("icons", {}).items():
                found[n] = info

        # 第二轮:对缺失的 -rounded 名,尝试回退到去掉 -rounded 的基础名
        missing = [n for n in names if n not in found]
        fallback_map: Dict[str, str] = {}
        retry_names: list[str] = []
        for n in missing:
            if n.endswith("-rounded"):
                base = n[: -len("-rounded")]
                fallback_map[n] = base
                retry_names.append(base)
        if retry_names:
            for i in range(0, len(retry_names), 50):
                chunk = retry_names[i : i + 50]
                data = _request_chunk(prefix, chunk)
                for n, info in data.get("icons", {}).items():
                    found[n] = info

        # 汇总:对每个原始声明,挑选实际可用的名字
        still_missing = []
        for original in names:
            picked = original if original in found else fallback_map.get(original)
            if picked is None or picked not in found:
                still_missing.append(original)
                continue
            info = found[picked]
            w = info.get("width", default_w)
            h = info.get("height", default_h)
            results[f"{prefix}:{original}"] = (info["body"], w, h)
            if picked != original:
                print(f"  [回退] {prefix}:{original} -> {prefix}:{picked}")
        if still_missing:
            raise RuntimeError(f"Iconify 缺失且无回退:{prefix}:{still_missing}")

    return results


def wrap_svg(body: str, w: int, h: int, color: str) -> str:
    """把 Iconify body 包装为完整 SVG,并强制把 fill='currentColor' 替换为目标色。

    Iconify 的 body 默认使用 currentColor,通过外层 SVG 的 color 属性即可控制。
    我们也兜底替换一下出现的 currentColor 字面量,避免某些渲染器不识别。
    """
    body_colored = body.replace("currentColor", color)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {w} {h}" width="{PNG_SIZE}" height="{PNG_SIZE}" '
        f'color="{color}" fill="{color}">{body_colored}</svg>'
    )


def render_all() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[1/2] 拉取 SVG 数据 ({len(ICONS)} 个图标)...")
    bodies = fetch_svg_bodies()
    print(f"[2/2] 渲染 PNG 到 {OUT_DIR} ...")

    for idx, (group, name_zh, icon_id) in enumerate(ICONS, 1):
        body, w, h = bodies[icon_id]
        slug = icon_id.replace(":", "__").replace("/", "_")
        for color_name, color_hex in COLORS.items():
            svg_text = wrap_svg(body, w, h, color_hex)
            color_slug = {"深蓝灰": "blue", "品牌橙": "orange", "警示红": "red"}[color_name]
            out_path = OUT_DIR / f"{slug}__{color_slug}.png"
            cairosvg.svg2png(
                bytestring=svg_text.encode("utf-8"),
                write_to=str(out_path),
                output_width=PNG_SIZE,
                output_height=PNG_SIZE,
            )
        if idx % 10 == 0 or idx == len(ICONS):
            print(f"  渲染 {idx}/{len(ICONS)}")

    total = len(list(OUT_DIR.glob("*.png")))
    print(f"完成,共生成 {total} 张 PNG (期望 {len(ICONS) * len(COLORS)})")


if __name__ == "__main__":
    render_all()
