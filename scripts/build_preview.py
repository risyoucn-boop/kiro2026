"""把所有图标拼成两张静态预览 PNG,作为 README 的可视证据。

preview_grid.png : 100 个图标的网格 (深蓝灰主色),自带分组小标题
preview_tricolor.png : 每组挑 1 个,横向三色对照
"""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from icons import COLORS, ICONS

ROOT = Path(__file__).resolve().parent.parent
PNG_DIR = ROOT / "build" / "png"
OUT_DIR = ROOT / "build"

# ---- 字体 ----
def _font(size: int):
    candidates = [
        "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/google-noto-cjk/NotoSansCJK-DemiLight.ttc",
        "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Light.ttc",
        "/usr/share/fonts/google-noto-sans-cjk-vf-fonts/NotoSansCJK-VF.otf.ttc",
        "/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc",
        "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _icon(icon_id: str, slug: str) -> Path:
    s = icon_id.replace(":", "__").replace("/", "_")
    return PNG_DIR / f"{s}__{slug}.png"


def build_grid_preview():
    """100 图标网格 (深蓝灰),按分组依次排列。"""
    cols = 10
    cell = 110
    pad_x, pad_y = 30, 30
    icon_size = 72
    label_h = 22
    group_label_h = 36

    groups: "OrderedDict[str, list]" = OrderedDict()
    for entry in ICONS:
        groups.setdefault(entry[0], []).append(entry)

    # 计算行数:每个分组独占完整行,组首加一个标题条
    rows_per_group = []
    total_rows = 0
    for items in groups.values():
        r = (len(items) + cols - 1) // cols
        rows_per_group.append(r)
        total_rows += r

    title_h = 80
    width = pad_x * 2 + cols * cell
    height = (
        title_h
        + len(groups) * group_label_h
        + total_rows * (cell + label_h)
        + pad_y * 2
    )

    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    title_font = _font(28)
    sub_font = _font(14)
    group_font = _font(18)
    label_font = _font(13)

    # 顶部标题
    draw.rectangle([0, 0, width, title_h], fill=(44, 62, 80))
    draw.text((pad_x, 18), "图标库 · 100 选 · 深蓝灰主色预览",
              font=title_font, fill=(255, 255, 255))
    draw.text((pad_x, 50), f"Material Symbols · {len(groups)} 组 · {len(ICONS)} 个",
              font=sub_font, fill=(204, 211, 218))

    y = title_h + pad_y
    for (group, items) in groups.items():
        # 分组标题条
        draw.rectangle([pad_x, y, width - pad_x, y + group_label_h - 6],
                       fill=(245, 246, 248))
        draw.rectangle([pad_x, y, pad_x + 4, y + group_label_h - 6],
                       fill=(230, 126, 34))
        draw.text((pad_x + 14, y + 4), f"{group}  ({len(items)})",
                  font=group_font, fill=(44, 62, 80))
        y += group_label_h

        # 单元格
        for i, (_, name_zh, icon_id) in enumerate(items):
            r, c = divmod(i, cols)
            cx = pad_x + c * cell + (cell - icon_size) // 2
            cy = y + r * (cell + label_h)
            # 图标
            ic = Image.open(_icon(icon_id, "blue")).convert("RGBA")
            ic = ic.resize((icon_size, icon_size), Image.LANCZOS)
            img.paste(ic, (cx, cy + 6), ic)
            # 文字
            tx = pad_x + c * cell
            ty = cy + icon_size + 8
            tw = cell
            # 居中
            bbox = draw.textbbox((0, 0), name_zh, font=label_font)
            txt_w = bbox[2] - bbox[0]
            draw.text((tx + (tw - txt_w) // 2, ty), name_zh,
                      font=label_font, fill=(51, 51, 51))

        y += rows_per_group[list(groups.keys()).index(group)] * (cell + label_h) + 8

    out = OUT_DIR / "preview_grid.png"
    img.save(out, "PNG", optimize=True)
    print(f"网格预览: {out} ({out.stat().st_size // 1024} KB, {width}x{height})")
    return out


def build_tricolor_preview():
    """每组取 1 个代表图,横向 3 色对照。"""
    seen = OrderedDict()
    for group, name_zh, icon_id in ICONS:
        if group not in seen:
            seen[group] = (name_zh, icon_id)

    rows = len(seen)
    cell_h = 130
    name_w = 220
    color_w = 200
    pad = 30
    width = pad * 2 + name_w + color_w * 3
    title_h = 90
    header_h = 44
    height = title_h + header_h + cell_h * rows + pad

    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    title_font = _font(26)
    sub_font = _font(13)
    head_font = _font(15)
    name_font = _font(16)
    sub_name_font = _font(13)

    # 标题条
    draw.rectangle([0, 0, width, title_h], fill=(44, 62, 80))
    draw.text((pad, 18), "三色对照 · 各组代表图标",
              font=title_font, fill=(255, 255, 255))
    draw.text((pad, 52), "深蓝灰  ·  品牌橙  ·  警示红",
              font=sub_font, fill=(204, 211, 218))

    # 表头
    headers = [("分组 / 名称", (44, 62, 80)),
               ("深蓝灰", (44, 62, 80)),
               ("品牌橙", (230, 126, 34)),
               ("警示红", (192, 57, 43))]
    widths = [name_w, color_w, color_w, color_w]
    x = pad
    y = title_h
    for (txt, color), w in zip(headers, widths):
        draw.rectangle([x, y, x + w, y + header_h], fill=color)
        bbox = draw.textbbox((0, 0), txt, font=head_font)
        tw = bbox[2] - bbox[0]
        draw.text((x + (w - tw) // 2, y + 12), txt,
                  font=head_font, fill=(255, 255, 255))
        x += w
    y += header_h

    # 每行
    icon_size = 80
    for ridx, (group, (name_zh, icon_id)) in enumerate(seen.items()):
        bg = (250, 250, 250) if ridx % 2 == 0 else (255, 255, 255)
        draw.rectangle([pad, y, pad + name_w + color_w * 3, y + cell_h], fill=bg)
        draw.line([pad, y + cell_h, pad + name_w + color_w * 3, y + cell_h],
                  fill=(229, 231, 235))

        # 名称列
        draw.text((pad + 14, y + 28), group, font=name_font, fill=(44, 62, 80))
        draw.text((pad + 14, y + 60), name_zh, font=sub_name_font, fill=(120, 120, 120))

        # 三色图
        for ci, slug in enumerate(["blue", "orange", "red"]):
            ic = Image.open(_icon(icon_id, slug)).convert("RGBA")
            ic = ic.resize((icon_size, icon_size), Image.LANCZOS)
            cx = pad + name_w + color_w * ci + (color_w - icon_size) // 2
            cy = y + (cell_h - icon_size) // 2
            img.paste(ic, (cx, cy), ic)

        y += cell_h

    out = OUT_DIR / "preview_tricolor.png"
    img.save(out, "PNG", optimize=True)
    print(f"三色对照: {out} ({out.stat().st_size // 1024} KB, {width}x{height})")
    return out


if __name__ == "__main__":
    build_grid_preview()
    build_tricolor_preview()
