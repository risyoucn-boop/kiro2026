"""生成 PPTX 图标速览:封面 + 每组分页 + 三色对照页。

每个图标在 PPT 里是真正的 SVG 矢量(PowerPoint 2016+ 原生支持),
可在 PPT 中右键改色、放大无损。低版本 PowerPoint 自动用 PNG 兜底。

布局:
- 封面 1 页
- 每个业务分组: 一页 12 图 (3 行 × 4 列),图标在卡片正中,下方写中文名
- 末尾三色对照页,每组代表图标的 3 色横向对照
"""

from __future__ import annotations

import math
from collections import OrderedDict
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.package import Part
from pptx.opc.packuri import PackURI
from pptx.util import Emu, Inches, Pt

from icons import COLORS, ICONS

ROOT = Path(__file__).resolve().parent.parent
PNG_DIR = ROOT / "build" / "png"
SVG_DIR = ROOT / "assets" / "svg"
OUT_PPTX = ROOT / "build" / "icon_library.pptx"

SLIDE_W, SLIDE_H = Inches(13.333), Inches(7.5)  # 16:9
COLS, ROWS = 4, 3                                # 一页 12 图
ICON_SIZE = Inches(1.2)                          # 0.8" 的 1.5×
CARD_PAD = Inches(0.15)
TITLE_H = Inches(0.7)

DARK_BLUE = RGBColor(0x2C, 0x3E, 0x50)
ORANGE   = RGBColor(0xE6, 0x7E, 0x22)
RED      = RGBColor(0xC0, 0x39, 0x2B)
GRAY_BG  = RGBColor(0xF5, 0xF6, 0xF8)
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
TEXT_DARK = RGBColor(0x33, 0x33, 0x33)
TEXT_MUTE = RGBColor(0x88, 0x88, 0x88)

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_ASVG = "http://schemas.microsoft.com/office/drawing/2016/SVG/main"
SVG_BLIP_EXT_URI = "{96DAC541-7B7A-43D3-8B79-37D633B846F1}"


# ---------- 通用工具 ----------
def _set_slide_size(prs: Presentation):
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H


def _add_blank_slide(prs: Presentation):
    return prs.slides.add_slide(prs.slide_layouts[6])


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


def _add_filled_rect(slide, left, top, width, height, fill_rgb,
                     line_rgb=None, line_width_pt=None):
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


# ---------- 关键: 把 SVG 嵌入 PNG picture (现代 PPT 显示矢量,旧版用 PNG 兜底) ----------
_svg_part_counter = {"n": 0}


def _attach_svg_to_picture(slide, pic, svg_path: Path):
    """给已经放进 slide 的 PNG picture 附加一个 SVG 作为矢量优先表示。

    PowerPoint 2016+ 会读 a:blip 上的 asvg:svgBlip 扩展并优先渲染 SVG,
    不支持的旧版 PowerPoint/WPS 仍走原来的 PNG 路径。
    """
    slide_part = slide.part
    package = slide_part.package

    # 给 SVG 起一个全局唯一 partname
    _svg_part_counter["n"] += 1
    n = _svg_part_counter["n"]
    partname = PackURI(f"/ppt/media/icon{n}.svg")

    # 创建/复用 SVG 媒体 part
    svg_blob = svg_path.read_bytes()
    svg_part = Part(
        partname=partname,
        content_type="image/svg+xml",
        blob=svg_blob,
        package=package,
    )
    rId = slide_part.relate_to(svg_part, RT.IMAGE)

    # 在原 PNG 的 <a:blip> 里挂 <a:extLst><a:ext><asvg:svgBlip/>
    blip = pic._element.find(f".//{{{NS_A}}}blip")
    if blip is None:
        return  # 容错: 没找到 blip 就放弃,不至于让流程崩
    extLst = etree.SubElement(blip, f"{{{NS_A}}}extLst")
    ext = etree.SubElement(extLst, f"{{{NS_A}}}ext", uri=SVG_BLIP_EXT_URI)
    svgBlip = etree.SubElement(
        ext,
        f"{{{NS_ASVG}}}svgBlip",
        nsmap={"asvg": NS_ASVG},
    )
    svgBlip.set(f"{{{NS_R}}}embed", rId)


def _add_vector_icon(slide, png_path: Path, svg_path: Path,
                     left, top, width, height):
    """放一个 PNG,然后把 SVG 挂上去。返回 picture shape。"""
    pic = slide.shapes.add_picture(str(png_path), left, top, width, height)
    if svg_path.exists():
        try:
            _attach_svg_to_picture(slide, pic, svg_path)
        except Exception as e:
            # SVG 嵌入失败时不影响整体输出
            print(f"  [warn] SVG 嵌入失败 {svg_path.name}: {e}")
    return pic


# ---------- 路径解析 ----------
def _icon_paths(idx: int, name_zh: str, icon_id: str, color_slug: str):
    """返回 (png_path, svg_path)。SVG 文件名按 NN_中文名 命名。"""
    slug = icon_id.replace(":", "__").replace("/", "_")
    png_path = PNG_DIR / f"{slug}__{color_slug}.png"
    seq = f"{idx:02d}"
    svg_path = SVG_DIR / color_slug / f"{seq}_{name_zh}.svg"
    return png_path, svg_path


# ---------- 封面 ----------
def _add_cover(prs):
    slide = _add_blank_slide(prs)
    _add_filled_rect(slide, Emu(0), Emu(0), SLIDE_W, Inches(1.6), DARK_BLUE)
    _add_textbox(slide, Inches(0.6), Inches(0.45), SLIDE_W - Inches(1.2), Inches(0.7),
                 "图标库 · 100 选 · 三色对照 · 矢量版",
                 size=34, bold=True, color=WHITE)
    _add_textbox(slide, Inches(0.6), Inches(1.05), SLIDE_W - Inches(1.2), Inches(0.45),
                 "Material Symbols Outline · SVG 矢量嵌入 · 改色不会填满方框",
                 size=14, color=RGBColor(0xCC, 0xD3, 0xDA))

    swatch_top = Inches(2.2)
    swatch_w, swatch_h = Inches(3.6), Inches(1.2)
    gap = Inches(0.4)
    total_w = swatch_w * 3 + gap * 2
    start_left = (SLIDE_W - total_w) / 2
    palette = [("深蓝灰", "#2C3E50", DARK_BLUE),
               ("品牌橙", "#E67E22", ORANGE),
               ("警示红", "#C0392B", RED)]
    for i, (name, hex_code, rgb) in enumerate(palette):
        left = start_left + (swatch_w + gap) * i
        _add_filled_rect(slide, left, swatch_top, swatch_w, swatch_h, rgb)
        _add_textbox(slide, left, swatch_top + Inches(0.15),
                     swatch_w, Inches(0.5), name,
                     size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        _add_textbox(slide, left, swatch_top + Inches(0.65),
                     swatch_w, Inches(0.4), hex_code,
                     size=14, color=WHITE, align=PP_ALIGN.CENTER)

    from collections import Counter
    counts = Counter(g for g, _, _ in ICONS)
    info = "  ·  ".join(f"{g} {n}" for g, n in counts.items())
    _add_textbox(slide, Inches(0.6), Inches(4.0), SLIDE_W - Inches(1.2), Inches(0.6),
                 f"共 {len(ICONS)} 个图标 · 8 大分组 · 每图 3 色",
                 size=18, bold=True, color=TEXT_DARK, align=PP_ALIGN.CENTER)
    _add_textbox(slide, Inches(0.6), Inches(4.5), SLIDE_W - Inches(1.2), Inches(1.6),
                 info, size=13, color=TEXT_MUTE, align=PP_ALIGN.CENTER)
    _add_textbox(slide, Inches(0.6), SLIDE_H - Inches(0.5), SLIDE_W - Inches(1.2),
                 Inches(0.4),
                 "PPT 2016+ 显示为矢量,粘到文档不会出现填色方块",
                 size=11, color=TEXT_MUTE, align=PP_ALIGN.RIGHT)


# ---------- 分组页 ----------
def _add_group_pages(prs, group_name: str, items: list,
                    color_slug: str = "blue", item_seq_offset: int = 0):
    """每组按 12 个一页拆分,卡片化排版,图标用 SVG 矢量(PNG 兜底)。"""
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
        _add_filled_rect(slide, Emu(0), Emu(0), SLIDE_W, TITLE_H, DARK_BLUE)
        title_text = group_name + (f"   ({page_idx+1}/{pages})" if pages > 1 else "")
        _add_textbox(slide, Inches(0.5), Inches(0.12), SLIDE_W / 2, Inches(0.5),
                     title_text, size=22, bold=True, color=WHITE)
        color_zh = {"blue": "深蓝灰", "orange": "品牌橙", "red": "警示红"}[color_slug]
        _add_textbox(slide, SLIDE_W / 2, Inches(0.18),
                     SLIDE_W / 2 - Inches(0.5), Inches(0.4),
                     f"色:{color_zh}   ·   一页 {page_size} 图   ·   矢量",
                     size=12, color=RGBColor(0xCC, 0xD3, 0xDA), align=PP_ALIGN.RIGHT)

        chunk = items[page_idx * page_size : (page_idx + 1) * page_size]
        chunk_offset = item_seq_offset + page_idx * page_size
        for k, (_, name_zh, icon_id) in enumerate(chunk):
            r, c = divmod(k, COLS)
            cell_left = margin_x + cell_w * c
            cell_top = margin_top + cell_h * r
            _add_filled_rect(slide, cell_left + CARD_PAD, cell_top + CARD_PAD,
                             cell_w - CARD_PAD * 2, cell_h - CARD_PAD * 2,
                             GRAY_BG, line_rgb=RGBColor(0xE5, 0xE7, 0xEB),
                             line_width_pt=0.75)
            icon_left = cell_left + (cell_w - ICON_SIZE) / 2
            icon_top = cell_top + Inches(0.3)
            global_idx = chunk_offset + k + 1
            png_path, svg_path = _icon_paths(global_idx, name_zh, icon_id, color_slug)
            _add_vector_icon(slide, png_path, svg_path,
                             icon_left, icon_top, ICON_SIZE, ICON_SIZE)

            label_top = icon_top + ICON_SIZE + Inches(0.1)
            _add_textbox(slide, cell_left, label_top, cell_w, Inches(0.35),
                         name_zh, size=13, bold=True, color=TEXT_DARK,
                         align=PP_ALIGN.CENTER)
            base = icon_id.split(":", 1)[1]
            _add_textbox(slide, cell_left, label_top + Inches(0.32),
                         cell_w, Inches(0.3),
                         base, size=9, color=TEXT_MUTE, align=PP_ALIGN.CENTER)


# ---------- 三色对照页 ----------
def _add_tricolor_compare(prs):
    seen = OrderedDict()
    for idx, (group, name_zh, icon_id) in enumerate(ICONS, 1):
        if group not in seen:
            seen[group] = (idx, name_zh, icon_id)

    slide = _add_blank_slide(prs)
    _add_filled_rect(slide, Emu(0), Emu(0), SLIDE_W, TITLE_H, DARK_BLUE)
    _add_textbox(slide, Inches(0.5), Inches(0.12), SLIDE_W - Inches(1.0), Inches(0.5),
                 "三色对照 · 矢量 · 可在 PPT 中改色",
                 size=22, bold=True, color=WHITE)

    margin_x = Inches(0.5)
    top = Inches(1.0)
    name_w = Inches(2.4)
    color_w = (SLIDE_W - margin_x * 2 - name_w) / 3
    col_lefts = [margin_x, margin_x + name_w,
                 margin_x + name_w + color_w, margin_x + name_w + color_w * 2]
    headers = ["分组 / 名称", "深蓝灰", "品牌橙", "警示红"]
    bgs = [DARK_BLUE, DARK_BLUE, ORANGE, RED]
    header_h = Inches(0.4)
    for i, (h, w, bg) in enumerate(zip(headers,
                                       [name_w, color_w, color_w, color_w], bgs)):
        _add_filled_rect(slide, col_lefts[i], top, w, header_h, bg)
        _add_textbox(slide, col_lefts[i], top + Inches(0.06), w, Inches(0.3),
                     h, size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

    rows_total_in = (SLIDE_H - top - header_h - Inches(0.4)) / 914400
    row_h_in = rows_total_in / len(seen)
    row_h = Inches(row_h_in)
    icon_size_in = min(0.7, row_h_in - 0.1)
    icon_size = Inches(icon_size_in)
    for ridx, (group, (idx, name_zh, icon_id)) in enumerate(seen.items()):
        rt = top + Inches(row_h_in * ridx) + header_h
        _add_filled_rect(slide, col_lefts[0], rt, name_w, row_h,
                         GRAY_BG if ridx % 2 == 0 else WHITE,
                         line_rgb=RGBColor(0xE5, 0xE7, 0xEB), line_width_pt=0.5)
        _add_textbox(slide, col_lefts[0] + Inches(0.15), rt + Inches(0.05),
                     name_w - Inches(0.3), Inches(0.3),
                     group, size=11, bold=True, color=TEXT_DARK)
        _add_textbox(slide, col_lefts[0] + Inches(0.15), rt + Inches(0.32),
                     name_w - Inches(0.3), Inches(0.3),
                     name_zh, size=10, color=TEXT_MUTE)

        for ci, slug in enumerate(["blue", "orange", "red"], start=1):
            _add_filled_rect(slide, col_lefts[ci], rt, color_w, row_h,
                             GRAY_BG if ridx % 2 == 0 else WHITE,
                             line_rgb=RGBColor(0xE5, 0xE7, 0xEB), line_width_pt=0.5)
            ic_left = col_lefts[ci] + (color_w - icon_size) / 2
            ic_top = rt + Inches((row_h_in - icon_size_in) / 2)
            png_path, svg_path = _icon_paths(idx, name_zh, icon_id, slug)
            _add_vector_icon(slide, png_path, svg_path,
                             ic_left, ic_top, icon_size, icon_size)


def build():
    prs = Presentation()
    _set_slide_size(prs)

    _add_cover(prs)

    groups: "OrderedDict[str, list]" = OrderedDict()
    seq_offset_per_group: dict[str, int] = {}
    cur_offset = 0
    for entry in ICONS:
        groups.setdefault(entry[0], []).append(entry)
    for g, items in groups.items():
        seq_offset_per_group[g] = cur_offset
        cur_offset += len(items)

    for group_name, items in groups.items():
        _add_group_pages(prs, group_name, items, color_slug="blue",
                         item_seq_offset=seq_offset_per_group[group_name])

    _add_tricolor_compare(prs)

    OUT_PPTX.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT_PPTX)
    size_kb = OUT_PPTX.stat().st_size // 1024
    print(f"PPTX 已生成: {OUT_PPTX} ({size_kb} KB), 共 {len(prs.slides)} 页")


if __name__ == "__main__":
    build()
