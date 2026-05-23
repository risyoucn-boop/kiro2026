"""生成 PPTX 图标速览:封面 + 每组分页 + 三色对照页。

布局:
- 封面 1 页
- 每个业务分组: 一页 12 图 (3 行 × 4 列),图标在卡片正中,下方写中文名
- 末尾三色对照页,展示同一组图标的三色版本
"""

from __future__ import annotations

import math
from collections import OrderedDict
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

from icons import COLORS, ICONS

ROOT = Path(__file__).resolve().parent.parent
PNG_DIR = ROOT / "build" / "png"
OUT_PPTX = ROOT / "build" / "icon_library.pptx"

SLIDE_W, SLIDE_H = Inches(13.333), Inches(7.5)  # 16:9
COLS, ROWS = 4, 3                                # 一页 12 图
ICON_SIZE = Inches(1.2)                          # 上一版 0.8" 的 1.5×
CARD_PAD = Inches(0.15)
TITLE_H = Inches(0.7)

DARK_BLUE = RGBColor(0x2C, 0x3E, 0x50)
ORANGE   = RGBColor(0xE6, 0x7E, 0x22)
RED      = RGBColor(0xC0, 0x39, 0x2B)
GRAY_BG  = RGBColor(0xF5, 0xF6, 0xF8)
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
TEXT_DARK = RGBColor(0x33, 0x33, 0x33)
TEXT_MUTE = RGBColor(0x88, 0x88, 0x88)


def _set_slide_size(prs: Presentation):
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H


def _add_blank_slide(prs: Presentation):
    blank_layout = prs.slide_layouts[6]
    return prs.slides.add_slide(blank_layout)


def _add_textbox(slide, left, top, width, height, text, *, size=18, bold=False,
                 color=TEXT_DARK, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Microsoft YaHei"
    return tb


def _add_filled_rect(slide, left, top, width, height, fill_rgb, line_rgb=None, line_width_pt=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shp.adjustments[0] = 0.08
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill_rgb
    if line_rgb is not None:
        shp.line.color.rgb = line_rgb
        if line_width_pt:
            shp.line.width = Pt(line_width_pt)
    else:
        shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


# ---------- 封面 ----------
def _add_cover(prs):
    slide = _add_blank_slide(prs)
    # 顶部色带
    _add_filled_rect(slide, Emu(0), Emu(0), SLIDE_W, Inches(1.6), DARK_BLUE)
    _add_textbox(slide, Inches(0.6), Inches(0.45), SLIDE_W - Inches(1.2), Inches(0.7),
                 "图标库 · 100 选 · 三色对照", size=34, bold=True, color=WHITE)
    _add_textbox(slide, Inches(0.6), Inches(1.05), SLIDE_W - Inches(1.2), Inches(0.45),
                 "Material Symbols · 8 大业务场景 · 256px 源图",
                 size=14, color=RGBColor(0xCC, 0xD3, 0xDA))

    # 三色色卡
    swatch_top = Inches(2.2)
    swatch_w, swatch_h = Inches(3.6), Inches(1.2)
    gap = Inches(0.4)
    total_w = swatch_w * 3 + gap * 2
    start_left = (SLIDE_W - total_w) / 2
    palette = [("深蓝灰", "#2C3E50", DARK_BLUE), ("品牌橙", "#E67E22", ORANGE), ("警示红", "#C0392B", RED)]
    for i, (name, hex_code, rgb) in enumerate(palette):
        left = start_left + (swatch_w + gap) * i
        _add_filled_rect(slide, left, swatch_top, swatch_w, swatch_h, rgb)
        _add_textbox(slide, left, swatch_top + Inches(0.15),
                     swatch_w, Inches(0.5), name,
                     size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        _add_textbox(slide, left, swatch_top + Inches(0.65),
                     swatch_w, Inches(0.4), hex_code,
                     size=14, color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER)

    # 概览统计
    from collections import Counter
    counts = Counter(g for g, _, _ in ICONS)
    info = "  ·  ".join(f"{g} {n}" for g, n in counts.items())
    _add_textbox(slide, Inches(0.6), Inches(4.0), SLIDE_W - Inches(1.2), Inches(0.6),
                 f"共 {len(ICONS)} 个图标 · 8 大分组",
                 size=18, bold=True, color=TEXT_DARK, align=PP_ALIGN.CENTER)
    _add_textbox(slide, Inches(0.6), Inches(4.5), SLIDE_W - Inches(1.2), Inches(1.6),
                 info, size=13, color=TEXT_MUTE, align=PP_ALIGN.CENTER)

    _add_textbox(slide, Inches(0.6), SLIDE_H - Inches(0.5), SLIDE_W - Inches(1.2), Inches(0.4),
                 "每页 12 图 · 卡片化布局 · 图标 1.5×",
                 size=11, color=TEXT_MUTE, align=PP_ALIGN.RIGHT)


# ---------- 分组页 ----------
def _icon_path(icon_id: str, color_slug: str) -> Path:
    slug = icon_id.replace(":", "__").replace("/", "_")
    return PNG_DIR / f"{slug}__{color_slug}.png"


def _add_group_pages(prs, group_name: str, items: list, color_slug: str = "blue"):
    """每组按 12 个一页拆分,卡片化排版。"""
    page_size = COLS * ROWS  # 12
    pages = math.ceil(len(items) / page_size)
    margin_x = Inches(0.5)
    margin_top = Inches(1.1)
    grid_w = SLIDE_W - margin_x * 2
    grid_h = SLIDE_H - margin_top - Inches(0.4)
    cell_w = grid_w / COLS
    cell_h = grid_h / ROWS

    for page_idx in range(pages):
        slide = _add_blank_slide(prs)
        # 顶部标题条
        _add_filled_rect(slide, Emu(0), Emu(0), SLIDE_W, TITLE_H, DARK_BLUE)
        title_text = f"{group_name}"
        if pages > 1:
            title_text += f"   ({page_idx + 1}/{pages})"
        _add_textbox(slide, Inches(0.5), Inches(0.12), SLIDE_W / 2, Inches(0.5),
                     title_text, size=22, bold=True, color=WHITE)
        _add_textbox(slide, SLIDE_W / 2, Inches(0.18), SLIDE_W / 2 - Inches(0.5), Inches(0.4),
                     f"色:{ {'blue':'深蓝灰','orange':'品牌橙','red':'警示红'}[color_slug] }   ·   一页 {page_size} 图",
                     size=12, color=RGBColor(0xCC, 0xD3, 0xDA), align=PP_ALIGN.RIGHT)

        chunk = items[page_idx * page_size : (page_idx + 1) * page_size]
        for k, (_, name_zh, icon_id) in enumerate(chunk):
            r, c = divmod(k, COLS)
            cell_left = margin_x + cell_w * c
            cell_top = margin_top + cell_h * r
            # 卡片
            _add_filled_rect(slide, cell_left + CARD_PAD, cell_top + CARD_PAD,
                             cell_w - CARD_PAD * 2, cell_h - CARD_PAD * 2,
                             GRAY_BG, line_rgb=RGBColor(0xE5, 0xE7, 0xEB), line_width_pt=0.75)
            # 图标 (居中,下方留出文字行)
            icon_left = cell_left + (cell_w - ICON_SIZE) / 2
            icon_top = cell_top + Inches(0.3)
            slide.shapes.add_picture(str(_icon_path(icon_id, color_slug)),
                                     icon_left, icon_top, ICON_SIZE, ICON_SIZE)
            # 中文名
            label_top = icon_top + ICON_SIZE + Inches(0.1)
            _add_textbox(slide, cell_left, label_top, cell_w, Inches(0.35),
                         name_zh, size=13, bold=True, color=TEXT_DARK, align=PP_ALIGN.CENTER)
            # 编号 + iconify 名
            seq = ICONS.index((items[0][0], name_zh, icon_id)) + 1 if False else None
            base = icon_id.split(":", 1)[1]
            _add_textbox(slide, cell_left, label_top + Inches(0.32), cell_w, Inches(0.3),
                         base, size=9, color=TEXT_MUTE, align=PP_ALIGN.CENTER)


# ---------- 三色对照页 ----------
def _add_tricolor_compare(prs):
    """挑每组的代表图各 1 个,做三色横向对照。"""
    # 每组取第一个作为代表
    seen = OrderedDict()
    for group, name_zh, icon_id in ICONS:
        if group not in seen:
            seen[group] = (name_zh, icon_id)

    slide = _add_blank_slide(prs)
    _add_filled_rect(slide, Emu(0), Emu(0), SLIDE_W, TITLE_H, DARK_BLUE)
    _add_textbox(slide, Inches(0.5), Inches(0.12), SLIDE_W - Inches(1.0), Inches(0.5),
                 "三色对照 · 各组代表图标", size=22, bold=True, color=WHITE)

    # 表头: 分组 | 中文名 | 深蓝灰 | 品牌橙 | 警示红
    margin_x = Inches(0.5)
    top = Inches(1.0)
    name_w = Inches(2.4)
    color_w = (SLIDE_W - margin_x * 2 - name_w) / 3
    col_lefts = [margin_x, margin_x + name_w,
                 margin_x + name_w + color_w, margin_x + name_w + color_w * 2]
    headers = ["分组 / 名称", "深蓝灰", "品牌橙", "警示红"]
    header_top = top
    header_h = Inches(0.4)
    for i, h in enumerate(headers):
        w = name_w if i == 0 else color_w
        bg = DARK_BLUE if i == 0 else (ORANGE if i == 2 else (RED if i == 3 else DARK_BLUE))
        # 实际颜色按列名
        bgs = [DARK_BLUE, DARK_BLUE, ORANGE, RED]
        _add_filled_rect(slide, col_lefts[i], header_top, w, header_h, bgs[i])
        _add_textbox(slide, col_lefts[i], header_top + Inches(0.06), w, Inches(0.3),
                     h, size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    # 行
    rows_total_in = (SLIDE_H - top - header_h - Inches(0.4)) / 914400  # EMU -> inches
    row_h_in = rows_total_in / len(seen)
    row_h = Inches(row_h_in)
    icon_size_in = min(0.7, row_h_in - 0.1)
    icon_size = Inches(icon_size_in)
    for ridx, (group, (name_zh, icon_id)) in enumerate(seen.items()):
        rt = top + Inches(row_h_in * ridx) + header_h
        # 名称列
        _add_filled_rect(slide, col_lefts[0], rt, name_w, row_h,
                         GRAY_BG if ridx % 2 == 0 else WHITE,
                         line_rgb=RGBColor(0xE5, 0xE7, 0xEB), line_width_pt=0.5)
        _add_textbox(slide, col_lefts[0] + Inches(0.15), rt + Inches(0.05),
                     name_w - Inches(0.3), Inches(0.3),
                     group, size=11, bold=True, color=TEXT_DARK)
        _add_textbox(slide, col_lefts[0] + Inches(0.15), rt + Inches(0.32),
                     name_w - Inches(0.3), Inches(0.3),
                     name_zh, size=10, color=TEXT_MUTE)

        # 三色图列
        for ci, slug in enumerate(["blue", "orange", "red"], start=1):
            _add_filled_rect(slide, col_lefts[ci], rt, color_w, row_h,
                             GRAY_BG if ridx % 2 == 0 else WHITE,
                             line_rgb=RGBColor(0xE5, 0xE7, 0xEB), line_width_pt=0.5)
            ic_left = col_lefts[ci] + (color_w - icon_size) / 2
            ic_top = rt + Inches((row_h_in - icon_size_in) / 2)
            slide.shapes.add_picture(str(_icon_path(icon_id, slug)),
                                     ic_left, ic_top, icon_size, icon_size)


def build():
    prs = Presentation()
    _set_slide_size(prs)

    _add_cover(prs)

    # 按分组生成 (保持原顺序)
    groups: "OrderedDict[str, list]" = OrderedDict()
    for entry in ICONS:
        groups.setdefault(entry[0], []).append(entry)

    # 主体: 每组用深蓝灰主色展示
    for group_name, items in groups.items():
        _add_group_pages(prs, group_name, items, color_slug="blue")

    _add_tricolor_compare(prs)

    OUT_PPTX.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT_PPTX)
    print(f"PPTX 已生成: {OUT_PPTX} ({OUT_PPTX.stat().st_size // 1024} KB), 共 {len(prs.slides)} 页")


if __name__ == "__main__":
    build()
