"""从 Iconify API 拉取 SVG body,按 3 种颜色批量渲染:
  - 256x256 PNG -> build/png/
  - 矢量 SVG    -> assets/svg/{color_slug}/

Iconify 返回的 JSON 形如:
  {
    "prefix": "material-symbols",
    "icons": {
      "home-outline-rounded": {"body": "<path d=...>", "width": 24, "height": 24},
      ...
    }
  }
我们把 body 包装成完整 SVG 并指定 fill 颜色,
PNG 用 cairosvg 光栅化;SVG 直接落盘,可拖进 PPT/Word 做矢量改色。

Fallback 链(按风格自动尝试):
  outline-rounded -> outline -> rounded -> 基础名
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import cairosvg
import requests

from icons import COLORS, ICONS, STYLE, transform_id

ROOT = Path(__file__).resolve().parent.parent
PNG_DIR = ROOT / "build" / "png"
SVG_DIR = ROOT / "assets" / "svg"
PNG_SIZE = 256
ICONIFY_API = "https://api.iconify.design/{prefix}.json"

COLOR_SLUGS = {"深蓝灰": "blue", "品牌橙": "orange", "警示红": "red"}


def _request_chunk(prefix: str, names: list[str]) -> dict:
    url = ICONIFY_API.format(prefix=prefix)
    r = requests.get(url, params={"icons": ",".join(names)}, timeout=30)
    r.raise_for_status()
    return r.json()


def _fallback_chain(name: str) -> list[str]:
    """生成回退候选列表,先精确匹配,再逐步降级。"""
    chain: list[str] = [name]
    if name.endswith("-outline-rounded"):
        chain.append(name[: -len("-outline-rounded")] + "-outline")
        chain.append(name[: -len("-outline-rounded")] + "-rounded")
        chain.append(name[: -len("-outline-rounded")])
    elif name.endswith("-outline"):
        chain.append(name[: -len("-outline")] + "-rounded")
        chain.append(name[: -len("-outline")])
    elif name.endswith("-rounded"):
        chain.append(name[: -len("-rounded")])
    # 去重保持顺序
    seen, out = set(), []
    for n in chain:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


def fetch_svg_bodies() -> Dict[str, Tuple[str, int, int]]:
    """返回 {original_iconify_id: (body, width, height)}。"""
    # 先按 STYLE 转换原 id,得到实际请求的目标名
    targets: Dict[str, list[str]] = {}  # original_id -> chain
    for _, _, icon_id in ICONS:
        prefix, _ = icon_id.split(":", 1)
        styled = transform_id(icon_id, STYLE)
        _, styled_name = styled.split(":", 1)
        targets[icon_id] = _fallback_chain(styled_name)

    # 按 prefix 分组所有候选名
    prefix_candidates: Dict[str, set[str]] = {}
    for icon_id, chain in targets.items():
        prefix = icon_id.split(":", 1)[0]
        prefix_candidates.setdefault(prefix, set()).update(chain)

    # 批量拉取所有候选
    found: Dict[str, dict] = {}  # "prefix:name" -> info
    for prefix, names in prefix_candidates.items():
        names = list(names)
        for i in range(0, len(names), 50):
            chunk = names[i : i + 50]
            data = _request_chunk(prefix, chunk)
            default_w = data.get("width", 24)
            default_h = data.get("height", 24)
            for n, info in data.get("icons", {}).items():
                info.setdefault("width", default_w)
                info.setdefault("height", default_h)
                found[f"{prefix}:{n}"] = info

    # 按回退链挑出每个原 id 的实际 body
    results: Dict[str, Tuple[str, int, int]] = {}
    fallback_log: list[str] = []
    missing: list[str] = []
    for icon_id, chain in targets.items():
        prefix = icon_id.split(":", 1)[0]
        picked: Tuple[str, dict] | None = None
        for cand in chain:
            key = f"{prefix}:{cand}"
            if key in found:
                picked = (cand, found[key])
                break
        if picked is None:
            missing.append(icon_id)
            continue
        cand_name, info = picked
        results[icon_id] = (info["body"], info["width"], info["height"])
        # 第一候选不是原始 styled 名时记一笔
        if cand_name != chain[0]:
            fallback_log.append(f"  [回退] {icon_id} (期望 {chain[0]}) -> {cand_name}")

    if fallback_log:
        print("\n".join(fallback_log))
    if missing:
        raise RuntimeError(f"以下图标在所有回退候选中都缺失: {missing}")

    return results


def wrap_svg(body: str, w: int, h: int, color: str) -> str:
    """把 Iconify body 包装为完整 SVG,fill 全部替换为目标色。"""
    body_colored = body.replace("currentColor", color)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {w} {h}" width="{PNG_SIZE}" height="{PNG_SIZE}" '
        f'color="{color}" fill="{color}">{body_colored}</svg>'
    )


def render_all() -> None:
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    SVG_DIR.mkdir(parents=True, exist_ok=True)
    for color_slug in COLOR_SLUGS.values():
        (SVG_DIR / color_slug).mkdir(parents=True, exist_ok=True)

    print(f"[1/2] 拉取 SVG 数据 ({len(ICONS)} 个图标, STYLE={STYLE})...")
    bodies = fetch_svg_bodies()
    print(f"[2/2] 渲染到 PNG={PNG_DIR}, SVG={SVG_DIR} ...")

    for idx, (group, name_zh, icon_id) in enumerate(ICONS, 1):
        body, w, h = bodies[icon_id]
        # 用原 iconify_id 作为 slug,保持外部稳定引用
        slug = icon_id.replace(":", "__").replace("/", "_")
        # SVG 文件名:NN_中文名 (NN 为 100 内序号,便于在文件管理器里挑)
        seq = f"{idx:02d}"
        svg_filename_stem = f"{seq}_{name_zh}"

        for color_name, color_hex in COLORS.items():
            svg_text = wrap_svg(body, w, h, color_hex)
            color_slug = COLOR_SLUGS[color_name]

            # PNG (256x256, 透明背景, 给 Excel/PPTX 当后备)
            png_path = PNG_DIR / f"{slug}__{color_slug}.png"
            cairosvg.svg2png(
                bytestring=svg_text.encode("utf-8"),
                write_to=str(png_path),
                output_width=PNG_SIZE,
                output_height=PNG_SIZE,
            )

            # SVG (矢量, 透明背景, 用户可直接拖进 PPT/Word)
            svg_path = SVG_DIR / color_slug / f"{svg_filename_stem}.svg"
            svg_path.write_text(svg_text, encoding="utf-8")

        if idx % 10 == 0 or idx == len(ICONS):
            print(f"  渲染 {idx}/{len(ICONS)}")

    pn = len(list(PNG_DIR.glob("*.png")))
    sn = sum(len(list((SVG_DIR / c).glob("*.svg"))) for c in COLOR_SLUGS.values())
    print(f"完成: {pn} PNG (期望 {len(ICONS) * len(COLORS)}), "
          f"{sn} SVG (期望 {len(ICONS) * len(COLORS)})")


if __name__ == "__main__":
    render_all()
