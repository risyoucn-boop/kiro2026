# -*- coding: utf-8 -*-
"""
服销现管数智化报告 PPTX 生成器
基于 report-v2.html 的叙事结构与暗黑视觉语言
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

# ===== 配色 =====
BG_DARK     = RGBColor(0x0A, 0x0C, 0x10)
BG_CARD     = RGBColor(0x15, 0x1A, 0x24)
BG_CARD_2   = RGBColor(0x1A, 0x20, 0x2C)
ORANGE      = RGBColor(0xFF, 0x6A, 0x00)
ORANGE_SOFT = RGBColor(0xFF, 0x8B, 0x3D)
CYAN        = RGBColor(0x00, 0xE5, 0xFF)
RED         = RGBColor(0xFF, 0x4D, 0x4F)
GREEN       = RGBColor(0x52, 0xC4, 0x1A)
GOLD        = RGBColor(0xFF, 0xD6, 0x66)
YELLOW      = RGBColor(0xFF, 0xB3, 0x47)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT       = RGBColor(0xE0, 0xE0, 0xE0)
GRAY        = RGBColor(0x88, 0x92, 0xB0)
DIM         = RGBColor(0x5A, 0x63, 0x78)
BORDER      = RGBColor(0x2A, 0x31, 0x40)

# 16:9 画布 (13.333 x 7.5 inch)
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H

blank = prs.slide_layouts[6]

FONT = "Microsoft YaHei"
FONT_MONO = "Consolas"


# ===== 工具函数 =====
def add_bg(slide, color=BG_DARK):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bg.line.fill.background()
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.shadow.inherit = False
    return bg


def add_rect(slide, x, y, w, h, fill=BG_CARD, line_color=None, line_width=0.75, corner=True):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if corner else MSO_SHAPE.RECTANGLE,
        x, y, w, h
    )
    if fill is None:
        shape.fill.background()
    else:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    if line_color is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(line_width)
    shape.shadow.inherit = False
    # rounded corner smaller
    if corner:
        try:
            shape.adjustments[0] = 0.08
        except Exception:
            pass
    return shape


def add_text(slide, x, y, w, h, text, size=14, color=LIGHT, bold=False,
             font=FONT, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, italic=False,
             line_spacing=1.3):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    # handle multiple lines
    lines = text.split("\n") if isinstance(text, str) else [text]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = line
        r.font.name = font
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
    return tb


def add_rich_text(slide, x, y, w, h, runs, size=14, align=PP_ALIGN.LEFT,
                  anchor=MSO_ANCHOR.TOP, line_spacing=1.3):
    """runs = [(text, {color, bold, size, font, italic})]"""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    for text, attrs in runs:
        if text == "\n":
            p = tf.add_paragraph()
            p.alignment = align
            p.line_spacing = line_spacing
            continue
        r = p.add_run()
        r.text = text
        r.font.name = attrs.get("font", FONT)
        r.font.size = Pt(attrs.get("size", size))
        r.font.bold = attrs.get("bold", False)
        r.font.italic = attrs.get("italic", False)
        r.font.color.rgb = attrs.get("color", LIGHT)
    return tb


def add_section_header(slide, number, label, title, lead=None, y_start=Inches(0.4)):
    # 顶部数字编号
    add_text(slide, Inches(0.6), y_start, Inches(6), Inches(0.3),
             f"{number}  /  {label}",
             size=11, color=ORANGE, font=FONT_MONO, bold=True)
    # 左边青色竖线
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                 Inches(0.6), y_start + Inches(0.4),
                                 Emu(45720), Inches(0.55))
    bar.fill.solid()
    bar.fill.fore_color.rgb = CYAN
    bar.line.fill.background()
    bar.shadow.inherit = False
    # 标题
    add_text(slide, Inches(0.8), y_start + Inches(0.4), Inches(12), Inches(0.6),
             title, size=26, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    if lead:
        add_text(slide, Inches(0.8), y_start + Inches(1.05), Inches(12), Inches(0.5),
                 lead, size=12, color=GRAY, line_spacing=1.4)


def add_footer(slide, page_num, total=8):
    # 底部线
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                  Inches(0.6), Inches(7.1),
                                  Inches(12.1), Emu(9525))
    line.fill.solid()
    line.fill.fore_color.rgb = BORDER
    line.line.fill.background()
    line.shadow.inherit = False

    add_text(slide, Inches(0.6), Inches(7.18), Inches(8), Inches(0.3),
             "PAONE × 服销现管 · 数智化转型白皮书",
             size=9, color=DIM, font=FONT_MONO)
    add_text(slide, Inches(10.5), Inches(7.18), Inches(2.2), Inches(0.3),
             f"{page_num:02d} / {total:02d}",
             size=9, color=DIM, font=FONT_MONO, align=PP_ALIGN.RIGHT)


# ============================================================
# SLIDE 1  封面
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s)

# 橙色光晕
glow1 = s.shapes.add_shape(MSO_SHAPE.OVAL,
                           Inches(-2), Inches(-1.5),
                           Inches(6), Inches(6))
glow1.fill.solid()
glow1.fill.fore_color.rgb = RGBColor(0x3A, 0x1A, 0x08)
glow1.line.fill.background()
glow1.shadow.inherit = False

glow2 = s.shapes.add_shape(MSO_SHAPE.OVAL,
                           Inches(9), Inches(4),
                           Inches(6), Inches(6))
glow2.fill.solid()
glow2.fill.fore_color.rgb = RGBColor(0x06, 0x2C, 0x32)
glow2.line.fill.background()
glow2.shadow.inherit = False

# 标签
tag_bg = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                            Inches(4.5), Inches(1.8),
                            Inches(4.3), Inches(0.4))
tag_bg.adjustments[0] = 0.5
tag_bg.fill.background()
tag_bg.line.color.rgb = CYAN
tag_bg.line.width = Pt(0.75)
tag_bg.shadow.inherit = False
add_text(s, Inches(4.5), Inches(1.8), Inches(4.3), Inches(0.4),
         "PAONE × 服销现管 · 数智化转型白皮书",
         size=11, color=CYAN, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# 主标题
add_text(s, Inches(0.5), Inches(2.6), Inches(12.3), Inches(0.9),
         "现管再造：当 PAone 接管机械劳动，",
         size=40, color=WHITE, bold=True, align=PP_ALIGN.CENTER)

add_rich_text(s, Inches(0.5), Inches(3.5), Inches(12.3), Inches(0.9),
              runs=[
                  ("组长该", {"color": WHITE, "size": 40, "bold": True}),
                  (" 去哪里？", {"color": CYAN, "size": 40, "bold": True}),
              ], align=PP_ALIGN.CENTER)

# 副标题
add_text(s, Inches(0.5), Inches(4.7), Inches(12.3), Inches(0.4),
         "FROM LABOR-INTENSIVE TO INTELLIGENCE-DRIVEN",
         size=14, color=GRAY, font=FONT_MONO, align=PP_ALIGN.CENTER)

add_text(s, Inches(0.5), Inches(5.1), Inches(12.3), Inches(0.4),
         "服销团队长数字化落地研究  ·  量化收益  ·  新范式路径",
         size=13, color=LIGHT, align=PP_ALIGN.CENTER)

# 底部作者信息带
fl = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                        Inches(0), Inches(6.8),
                        SLIDE_W, Inches(0.7))
fl.fill.solid()
fl.fill.fore_color.rgb = BG_CARD
fl.line.fill.background()
fl.shadow.inherit = False
add_text(s, Inches(0.6), Inches(6.95), Inches(6), Inches(0.4),
         "WHITEPAPER · 2026",
         size=10, color=ORANGE, font=FONT_MONO, bold=True)
add_text(s, Inches(7), Inches(6.95), Inches(5.7), Inches(0.4),
         "FROM IDEA TO EXECUTION",
         size=10, color=CYAN, font=FONT_MONO, align=PP_ALIGN.RIGHT)


# ============================================================
# SLIDE 2  目录
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s)
add_section_header(s, "CONTENTS", "目录 / AGENDA", "七个章节，一条从困境到回报的完整叙事链")

toc = [
    ("01", "WHY", "困境诊断", "组长的一天，为什么总是很忙却没干成事"),
    ("02", "WHAT", "量化收益账本", "总工时未减，但管理带宽正在结构性迁徙"),
    ("03", "WHO", "角色新范式", "组长不再是监工，而是数智指挥官"),
    ("04", "PLAYBOOK", "话术萃取实战", "拆解一次真实萃取：从客户说再考虑一下"),
    ("05", "CASE", "真实挽回案例时间轴", "6 天的故事：AI 预警 × 组长介入"),
    ("06", "HOW", "90 天落地路径", "从工具接入到能力升级的三阶段"),
    ("07", "RESULT", "业绩 KPI + 行业对标", "不止是改善，而是站在行业前列"),
    ("08", "ROI", "投入产出账本", "6 个月回本，远快于行业 18 个月均值"),
]

start_y = 1.8
for i, (num, en, cn, desc) in enumerate(toc):
    row = i // 2
    col = i % 2
    x = Inches(0.6 + col * 6.2)
    y = Inches(start_y + row * 1.1)
    w = Inches(6.0)
    h = Inches(1.0)
    add_rect(s, x, y, w, h, fill=BG_CARD, line_color=BORDER)
    # 编号
    add_text(s, x + Inches(0.25), y + Inches(0.15), Inches(0.8), Inches(0.4),
             num, size=22, color=CYAN, bold=True, font=FONT_MONO)
    # EN label
    add_text(s, x + Inches(0.25), y + Inches(0.55), Inches(1.2), Inches(0.3),
             en, size=9, color=ORANGE, font=FONT_MONO, bold=True)
    # 标题
    add_text(s, x + Inches(1.4), y + Inches(0.18), Inches(4.4), Inches(0.35),
             cn, size=15, color=WHITE, bold=True)
    # 描述
    add_text(s, x + Inches(1.4), y + Inches(0.55), Inches(4.4), Inches(0.4),
             desc, size=10, color=GRAY)

add_footer(s, 2, 10)


# ============================================================
# SLIDE 3  WHY 困境诊断
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s)
add_section_header(s, "01", "WHY — 困境诊断",
                   "组长的一天，为什么总是\"很忙却没干成事\"？",
                   "直面当下现管岗位的三重结构性痛点 —— 这不是个人能力问题，而是工具缺位下的必然。")

pains = [
    ("🔥", "时间黑洞",
     "日均工时中超过 60% 被消耗在\"捞数据、做表格、人肉盯盘\"等低价值机械劳动上，真正用于业务思考与团队辅导的时间被严重挤压。",
     "> 350 min / 天"),
    ("😵", "辅导失焦",
     "1V1 沟通缺少数据抓手，常常沦为\"泛泛谈心、打鸡血\"。组长无法精准定位坐席能力短板，更难以提供可执行的话术级辅导。",
     "165 min / 天 低效投入"),
    ("📉", "决策滞后",
     "问题发现严重依赖夕会复盘，而非实时感知。当异常数据出现在报表上时，最佳干预窗口往往已经关闭，组长被迫陷入\"事后救火\"的被动循环。",
     "T+1 响应"),
]

card_w = Inches(3.9)
card_h = Inches(4.0)
start_x = 0.6
gap = 0.25
for i, (icon, title, desc, stat) in enumerate(pains):
    x = Inches(start_x + i * (3.9 + gap))
    y = Inches(2.3)
    add_rect(s, x, y, card_w, card_h, fill=BG_CARD, line_color=BORDER)
    # 左侧橙色竖条
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                             x, y, Emu(38100), card_h)
    bar.fill.solid()
    bar.fill.fore_color.rgb = ORANGE
    bar.line.fill.background()
    bar.shadow.inherit = False

    add_text(s, x + Inches(0.35), y + Inches(0.3), Inches(1), Inches(0.6),
             icon, size=28)
    add_text(s, x + Inches(0.35), y + Inches(1.05), card_w - Inches(0.7), Inches(0.45),
             title, size=20, color=ORANGE, bold=True)
    add_text(s, x + Inches(0.35), y + Inches(1.65), card_w - Inches(0.7), Inches(1.8),
             desc, size=12, color=GRAY, line_spacing=1.5)
    # 统计徽章
    badge = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                               x + Inches(0.35), y + Inches(3.35),
                               Inches(2.6), Inches(0.4))
    badge.adjustments[0] = 0.35
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(0x40, 0x1E, 0x05)
    badge.line.fill.background()
    badge.shadow.inherit = False
    add_text(s, x + Inches(0.35), y + Inches(3.35), Inches(2.6), Inches(0.4),
             stat, size=11, color=ORANGE, bold=True, font=FONT_MONO,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_footer(s, 3, 10)


# ============================================================
# SLIDE 4  WHAT 带宽迁徙总览
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s)
add_section_header(s, "02", "WHAT — 量化收益账本",
                   "总工时未减，但管理带宽正在\"结构性迁徙\"",
                   "引入 PAone 后，组长总工时并没有减少。真正发生的是 —— 时间从机械劳动迁徙到了高价值辅导。")

# 大容器
cont_x = Inches(0.6)
cont_y = Inches(2.2)
cont_w = Inches(12.1)
cont_h = Inches(4.7)
add_rect(s, cont_x, cont_y, cont_w, cont_h, fill=BG_CARD, line_color=BORDER)

# 大数字
add_rich_text(s, cont_x, cont_y + Inches(0.3), cont_w, Inches(0.8),
              runs=[
                  ("585 min ", {"color": CYAN, "size": 36, "bold": True}),
                  ("=", {"color": GRAY, "size": 36, "bold": True}),
                  (" 585 min", {"color": CYAN, "size": 36, "bold": True}),
              ], align=PP_ALIGN.CENTER)

add_rich_text(s, cont_x, cont_y + Inches(1.1), cont_w, Inches(0.4),
              runs=[
                  ("旧模式与新模式 ", {"color": GRAY, "size": 12}),
                  ("总工时完全相等", {"color": WHITE, "size": 12, "bold": True}),
                  ("，但时间结构发生质变：高价值投入从 28% 提升至 ", {"color": GRAY, "size": 12}),
                  ("53%", {"color": CYAN, "size": 12, "bold": True}),
              ], align=PP_ALIGN.CENTER)

# 条形图 - 旧模式
bar_x = cont_x + Inches(0.8)
bar_w = Inches(10.5)
total_min = 585

# Label 旧
add_text(s, bar_x, cont_y + Inches(1.8), bar_w, Inches(0.3),
         "旧模式 · 劳动密集型", size=11, color=GRAY, font=FONT_MONO)
add_text(s, bar_x, cont_y + Inches(1.8), bar_w, Inches(0.3),
         "Total: 585 min", size=11, color=WHITE, bold=True, align=PP_ALIGN.RIGHT)

old_segs = [(30, ORANGE, "碎片 30", WHITE),
            (155, YELLOW, "数据盘点 155", RGBColor(0x33,0x33,0x33)),
            (165, GREEN, "核心辅导 165", RGBColor(0x00,0x33,0x33)),
            (235, RGBColor(0x4A,0x52,0x63), "会议协同 235", LIGHT)]
cur_x = bar_x
bar_h = Inches(0.55)
bar_y = cont_y + Inches(2.15)
for minutes, color, label, text_color in old_segs:
    seg_w = Emu(int(bar_w * minutes / total_min))
    seg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, cur_x, bar_y, seg_w, bar_h)
    seg.fill.solid()
    seg.fill.fore_color.rgb = color
    seg.line.fill.background()
    seg.shadow.inherit = False
    add_text(s, cur_x, bar_y, seg_w, bar_h, label,
             size=10, color=text_color, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    cur_x += seg_w

# Label 新
add_text(s, bar_x, cont_y + Inches(2.95), bar_w, Inches(0.3),
         "新模式 · 数智驱动型", size=11, color=GRAY, font=FONT_MONO)
add_text(s, bar_x, cont_y + Inches(2.95), bar_w, Inches(0.3),
         "Total: 585 min", size=11, color=WHITE, bold=True, align=PP_ALIGN.RIGHT)

new_segs = [(5, ORANGE, "5", WHITE),
            (35, YELLOW, "35", RGBColor(0x33,0x33,0x33)),
            (310, CYAN, "核心辅导 310  ·  高价值带宽", RGBColor(0x00,0x33,0x33)),
            (235, RGBColor(0x4A,0x52,0x63), "会议协同 235", LIGHT)]
cur_x = bar_x
bar_y = cont_y + Inches(3.3)
for minutes, color, label, text_color in new_segs:
    seg_w = Emu(int(bar_w * minutes / total_min))
    seg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, cur_x, bar_y, seg_w, bar_h)
    seg.fill.solid()
    seg.fill.fore_color.rgb = color
    seg.line.fill.background()
    seg.shadow.inherit = False
    add_text(s, cur_x, bar_y, seg_w, bar_h, label,
             size=10, color=text_color, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    cur_x += seg_w

# Legend
legend_y = cont_y + Inches(4.1)
legend_items = [("碎片巡视", ORANGE), ("数据盘点", YELLOW),
                ("核心辅导（钻石）", CYAN), ("会议协同", RGBColor(0x4A,0x52,0x63))]
lx = cont_x + Inches(1.5)
for label, color in legend_items:
    dot = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, lx, legend_y + Inches(0.08),
                             Inches(0.15), Inches(0.15))
    dot.fill.solid()
    dot.fill.fore_color.rgb = color
    dot.line.fill.background()
    dot.shadow.inherit = False
    add_text(s, lx + Inches(0.25), legend_y, Inches(2.3), Inches(0.3),
             label, size=10, color=GRAY)
    lx += Inches(2.5)

add_footer(s, 4, 10)


# ============================================================
# SLIDE 5  WHAT 数据表
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s)
add_section_header(s, "02", "WHAT — 量化收益账本（续）",
                   "四个管理模块的时间迁徙明细",
                   "下表按价值层级排序，钻石区（核心辅导）是本次转型的最大赢家。")

table_data = [
    ("L3 钻石", CYAN, "核心干预与 1V1 辅导", "165 min", "310 min", "▲ +87.8%", GREEN,
     "核心投向：从\"泛泛谈心\"跃升为\"数据驱动的精准赋能\"", True),
    ("L2 中性", YELLOW, "会议管理与组织协同", "235 min", "235 min", "— 持平", GRAY,
     "时长不变，但决策依据从\"凭经验拍板\"升级为\"AI 情报+实时看板\"", False),
    ("L1 机械", GRAY, "数据盘点与材料准备", "155 min", "35 min", "▼ -77.4%", RED,
     "RPA + AIGC 一键生成早夕会与通报材料，释放机械体力活", False),
    ("L1 机械", GRAY, "碎片状态巡视", "30 min", "5 min", "▼ -83.3%", RED,
     "消灭\"人肉盯盘\"，规则引擎自动识别异常并主动推单", False),
]

tx = Inches(0.6)
ty = Inches(2.3)
tw = Inches(12.1)
row_h = Inches(0.95)

# header
header_h = Inches(0.5)
hdr = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, tx, ty, tw, header_h)
hdr.fill.solid()
hdr.fill.fore_color.rgb = BG_CARD_2
hdr.line.fill.background()
hdr.shadow.inherit = False

col_widths = [Inches(3.2), Inches(1.4), Inches(1.4), Inches(1.4), Inches(4.7)]
col_xs = [tx]
for w in col_widths[:-1]:
    col_xs.append(col_xs[-1] + w)

headers = ["管理模块", "旧模式", "新模式", "效能变化", "带宽流向与价值"]
for i, h in enumerate(headers):
    add_text(s, col_xs[i] + Inches(0.2), ty, col_widths[i], header_h,
             h, size=11, color=GRAY, bold=True, anchor=MSO_ANCHOR.MIDDLE)

# rows
for ri, (lvl, lvl_color, mod, old_t, new_t, rate, rate_color, desc, highlight) in enumerate(table_data):
    rr_y = ty + header_h + Inches(ri * 0.95)
    # 行背景
    row_bg_color = BG_CARD if highlight else None
    row_bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, tx, rr_y, tw, row_h)
    if highlight:
        row_bg.fill.solid()
        row_bg.fill.fore_color.rgb = RGBColor(0x08, 0x1F, 0x26)
    else:
        row_bg.fill.background()
    row_bg.line.color.rgb = BORDER
    row_bg.line.width = Pt(0.5)
    row_bg.shadow.inherit = False
    # 高亮行左边 3pt 青色
    if highlight:
        left_bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, tx, rr_y,
                                      Emu(38100), row_h)
        left_bar.fill.solid()
        left_bar.fill.fore_color.rgb = CYAN
        left_bar.line.fill.background()
        left_bar.shadow.inherit = False

    # Level tag
    tag_w = Inches(0.85)
    tag = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                             col_xs[0] + Inches(0.2), rr_y + Inches(0.15),
                             tag_w, Inches(0.3))
    tag.adjustments[0] = 0.35
    tag.fill.solid()
    if highlight:
        tag.fill.fore_color.rgb = RGBColor(0x08, 0x2F, 0x38)
    else:
        tag.fill.fore_color.rgb = RGBColor(0x1F, 0x24, 0x2E)
    tag.line.fill.background()
    tag.shadow.inherit = False
    add_text(s, col_xs[0] + Inches(0.2), rr_y + Inches(0.15),
             tag_w, Inches(0.3),
             lvl, size=9, color=lvl_color, bold=True, font=FONT_MONO,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    # 模块名
    add_text(s, col_xs[0] + Inches(0.2), rr_y + Inches(0.5),
             col_widths[0] - Inches(0.3), Inches(0.4),
             mod, size=12, color=WHITE, bold=True)

    # 旧时间 tag
    for idx, (val, color) in enumerate([(old_t, ORANGE), (new_t, CYAN)]):
        ttag = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                  col_xs[1 + idx] + Inches(0.15),
                                  rr_y + Inches(0.3),
                                  Inches(1.1), Inches(0.35))
        ttag.adjustments[0] = 0.3
        ttag.fill.solid()
        ttag.fill.fore_color.rgb = RGBColor(0x28, 0x14, 0x02) if idx == 0 else RGBColor(0x02, 0x28, 0x2C)
        ttag.line.fill.background()
        ttag.shadow.inherit = False
        add_text(s, col_xs[1 + idx] + Inches(0.15), rr_y + Inches(0.3),
                 Inches(1.1), Inches(0.35),
                 val, size=11, color=color, bold=True, font=FONT_MONO,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # 变化率
    add_text(s, col_xs[3] + Inches(0.1), rr_y, col_widths[3] - Inches(0.2), row_h,
             rate, size=13, color=rate_color, bold=True, font=FONT_MONO,
             anchor=MSO_ANCHOR.MIDDLE)
    # 描述
    add_text(s, col_xs[4] + Inches(0.15), rr_y, col_widths[4] - Inches(0.3), row_h,
             desc, size=11, color=LIGHT if highlight else GRAY,
             anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.4)

add_footer(s, 5, 10)


# ============================================================
# SLIDE 6  WHO 角色新范式
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s)
add_section_header(s, "03", "WHO — 角色新范式",
                   "组长不再是\"监工\"，而是\"数智指挥官\"",
                   "机械劳动被 PAone 接管 → 管理带宽被释放 → 岗位能力模型被重新定义。组长正在进化为三重新角色。")

# 过渡箭头带
trans_y = Inches(2.1)
trans_h = Inches(0.7)

def add_trans_box(slide, x, y, w, h, text, fill, border, text_color, line_through=False):
    b = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    b.adjustments[0] = 0.2
    b.fill.solid()
    b.fill.fore_color.rgb = fill
    b.line.color.rgb = border
    b.line.width = Pt(0.75)
    b.shadow.inherit = False
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.margin_left = Emu(0); tf.margin_right = Emu(0)
    tf.margin_top = Emu(0); tf.margin_bottom = Emu(0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = text
    r.font.name = FONT
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = text_color
    if line_through:
        rPr = r._r.get_or_add_rPr()
        rPr.set('strike', 'sngStrike')

add_trans_box(s, Inches(0.7), trans_y, Inches(2.8), trans_h,
              "盯流程的监工", RGBColor(0x28,0x14,0x02), ORANGE, ORANGE, line_through=True)
add_text(s, Inches(3.5), trans_y, Inches(0.7), trans_h, "→",
         size=22, color=GRAY, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_trans_box(s, Inches(4.2), trans_y, Inches(2.8), trans_h,
              "救火的客诉员", RGBColor(0x28,0x14,0x02), ORANGE, ORANGE, line_through=True)
add_text(s, Inches(7.0), trans_y, Inches(0.7), trans_h, "→",
         size=22, color=GRAY, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_trans_box(s, Inches(7.7), trans_y, Inches(4.9), trans_h,
              "数智指挥官 · 微型业务总经理", RGBColor(0x02,0x28,0x2C), CYAN, CYAN)

# 三张角色卡
roles = [
    ("🛡️", "EMOTIONAL SHIELD", "情绪价值终极兜底人",
     [("不再纠结流程：", "AI 已秒级完成查单与核实，组长将精力 100% 投入高风险客户的情感挽回。"),
      ("人性化防波堤：", "发挥人类共情力，处理 AI 逻辑之外的复杂客诉，守住服务品牌的最后防线。")],
     "每周亲自挽回 ≥ 3 例 高风险客户"),
    ("🧠", "STRATEGIC ANALYST", "业务策略前线情报官",
     [("销冠话术萃取：", "从 AI 初筛的优质录音中提炼\"一枪打透\"的实战话术，而非盲目打气。"),
      ("战术反馈中枢：", "分析业绩跳水深层根因，向产品线输送基于 AI 语料洞察的前线情报。")],
     "每月输出 ≥ 1 份 话术萃取 / 市场情报简报"),
    ("⚡", "AI TRAINER", "智能工具首席语料师",
     [("喂养 AI 大脑：", "将实战中的优秀案例与复杂逻辑打标签，训练 PAone 真正\"懂业务\"。"),
      ("人机协同进化：", "组长是 AI 的教练，通过纠偏与反哺，让工具具备部门专属的管理灵魂。")],
     "每周向 PAone 标注 ≥ 10 条 优质案例 / 纠偏反馈"),
]

card_y = Inches(3.1)
card_w = Inches(3.9)
card_h = Inches(3.8)
for i, (icon, label, title, points, kpi) in enumerate(roles):
    x = Inches(0.6 + i * 4.15)
    add_rect(s, x, card_y, card_w, card_h, fill=BG_CARD, line_color=BORDER)
    add_text(s, x + Inches(0.3), card_y + Inches(0.2), Inches(1), Inches(0.5),
             icon, size=22)
    add_text(s, x + Inches(0.3), card_y + Inches(0.8), card_w - Inches(0.6), Inches(0.3),
             label, size=9, color=CYAN, bold=True, font=FONT_MONO)
    add_text(s, x + Inches(0.3), card_y + Inches(1.1), card_w - Inches(0.6), Inches(0.4),
             title, size=15, color=WHITE, bold=True)
    # points
    py = card_y + Inches(1.65)
    for strong, rest in points:
        add_rich_text(s, x + Inches(0.3), py,
                      card_w - Inches(0.6), Inches(0.85),
                      runs=[("▸ ", {"color": CYAN, "size": 11, "bold": True}),
                            (strong, {"color": LIGHT, "size": 10, "bold": True}),
                            (rest, {"color": GRAY, "size": 10})],
                      line_spacing=1.4)
        py += Inches(0.85)
    # KPI
    kpi_y = card_y + card_h - Inches(0.8)
    kpi_box = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                  x + Inches(0.25), kpi_y,
                                  card_w - Inches(0.5), Inches(0.6))
    kpi_box.fill.solid()
    kpi_box.fill.fore_color.rgb = RGBColor(0x02, 0x20, 0x24)
    kpi_box.line.fill.background()
    kpi_box.shadow.inherit = False
    left = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                              x + Inches(0.25), kpi_y,
                              Emu(28575), Inches(0.6))
    left.fill.solid()
    left.fill.fore_color.rgb = CYAN
    left.line.fill.background()
    left.shadow.inherit = False
    add_text(s, x + Inches(0.4), kpi_y + Inches(0.05),
             card_w - Inches(0.6), Inches(0.25),
             "KEY ACTION · 量化抓手", size=8, color=CYAN, bold=True, font=FONT_MONO)
    add_text(s, x + Inches(0.4), kpi_y + Inches(0.28),
             card_w - Inches(0.6), Inches(0.3),
             kpi, size=10, color=WHITE, bold=True)

add_footer(s, 6, 10)


# ============================================================
# SLIDE 7  话术萃取实战
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s)
add_section_header(s, "04", "PLAYBOOK — 销冠话术萃取实战",
                   "拆解一次真实萃取：从\"客户说再考虑一下\"看组长的情报官价值",
                   "角色定义是虚的，样本才是实的。组长作为情报官每月从 AI 初筛的优质录音中萃取话术，反哺团队训练库。")

# 场景标题
scene_y = Inches(2.2)
scene_h = Inches(0.6)
scene_bg = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                              Inches(0.6), scene_y, Inches(12.1), scene_h)
scene_bg.adjustments[0] = 0.2
scene_bg.fill.solid()
scene_bg.fill.fore_color.rgb = BG_CARD
scene_bg.line.color.rgb = BORDER
scene_bg.line.width = Pt(0.5)
scene_bg.shadow.inherit = False

# SCENE badge
badge = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                           Inches(0.85), scene_y + Inches(0.12),
                           Inches(0.9), Inches(0.36))
badge.adjustments[0] = 0.5
badge.fill.solid()
badge.fill.fore_color.rgb = GOLD
badge.line.fill.background()
badge.shadow.inherit = False
add_text(s, Inches(0.85), scene_y + Inches(0.12), Inches(0.9), Inches(0.36),
         "SCENE", size=10, color=RGBColor(0x1A, 0x15, 0x00), bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_text(s, Inches(1.9), scene_y, Inches(8), scene_h,
         "客户反馈：\"我再考虑一下，暂时不太需要\"",
         size=15, color=WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)

add_rich_text(s, Inches(9.8), scene_y, Inches(2.8), scene_h,
              runs=[
                  ("出现频次：", {"color": GRAY, "size": 10}),
                  ("\n", {}),
                  ("日均 37 次", {"color": GOLD, "size": 12, "bold": True}),
                  ("  · 黑洞级高频", {"color": GRAY, "size": 10}),
              ], align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

# 左右对比
comp_y = Inches(3.0)
comp_h = Inches(2.8)
comp_w = Inches(5.95)

# 左：普通
add_rect(s, Inches(0.6), comp_y, comp_w, comp_h,
         fill=RGBColor(0x1A, 0x08, 0x08), line_color=RGBColor(0x5A, 0x22, 0x24))
# 标签
lbl1 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                          Inches(0.85), comp_y + Inches(0.2),
                          Inches(2.2), Inches(0.35))
lbl1.adjustments[0] = 0.4
lbl1.fill.solid()
lbl1.fill.fore_color.rgb = RGBColor(0x3A, 0x0C, 0x0E)
lbl1.line.fill.background()
lbl1.shadow.inherit = False
add_text(s, Inches(0.85), comp_y + Inches(0.2), Inches(2.2), Inches(0.35),
         "❌ 普通坐席话术", size=10, color=RED, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_text(s, Inches(0.85), comp_y + Inches(0.75), comp_w - Inches(0.5), Inches(1.3),
         "\"好的王姐，那您有需要随时联系我哈~ 我们的产品真的很好，您可以再了解一下。祝您生活愉快！\"",
         size=11, color=LIGHT, italic=True, line_spacing=1.6)

# 结果 chips
chips_y = comp_y + Inches(2.15)
chips = [("二次触达 12%", RED), ("流失率 78%", RED), ("挽回 >14 天", RED)]
cx = Inches(0.85)
for text, color in chips:
    chip = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                              cx, chips_y, Inches(1.7), Inches(0.35))
    chip.adjustments[0] = 0.35
    chip.fill.solid()
    chip.fill.fore_color.rgb = RGBColor(0x3A, 0x0C, 0x0E)
    chip.line.fill.background()
    chip.shadow.inherit = False
    add_text(s, cx, chips_y, Inches(1.7), Inches(0.35),
             text, size=9, color=RED, bold=True, font=FONT_MONO,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    cx += Inches(1.8)

# 右：销冠
add_rect(s, Inches(6.75), comp_y, comp_w, comp_h,
         fill=RGBColor(0x08, 0x1A, 0x06), line_color=RGBColor(0x22, 0x5A, 0x10))
lbl2 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                          Inches(7.0), comp_y + Inches(0.2),
                          Inches(3.5), Inches(0.35))
lbl2.adjustments[0] = 0.4
lbl2.fill.solid()
lbl2.fill.fore_color.rgb = RGBColor(0x0C, 0x3A, 0x0E)
lbl2.line.fill.background()
lbl2.shadow.inherit = False
add_text(s, Inches(7.0), comp_y + Inches(0.2), Inches(3.5), Inches(0.35),
         "✓ 销冠话术（AI 萃取后沉淀）", size=10, color=GREEN, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_rich_text(s, Inches(7.0), comp_y + Inches(0.75),
              comp_w - Inches(0.5), Inches(1.3),
              runs=[
                  ("\"王姐，特别理解您这个感受。其实您刚说的'再考虑'，我经手的客户里 90% 最后真正的顾虑都在三件事上 —— ", {"color": LIGHT, "size": 10.5, "italic": True}),
                  ("价格、理赔流程、或保障范围", {"color": WHITE, "size": 10.5, "italic": True, "bold": True}),
                  ("。我这边有个不占用您太多时间的办法：我直接用您家庭情况帮您模拟三种方案的差别，", {"color": LIGHT, "size": 10.5, "italic": True}),
                  ("看完没兴趣这事就过去", {"color": WHITE, "size": 10.5, "italic": True, "bold": True}),
                  ("，行吗？\"", {"color": LIGHT, "size": 10.5, "italic": True}),
              ], line_spacing=1.55)

chips2 = [("二次触达 46%", GREEN), ("转化率 34%", GREEN), ("挽回 3 天", GREEN)]
cx = Inches(7.0)
for text, color in chips2:
    chip = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                              cx, chips_y, Inches(1.7), Inches(0.35))
    chip.adjustments[0] = 0.35
    chip.fill.solid()
    chip.fill.fore_color.rgb = RGBColor(0x0C, 0x3A, 0x0E)
    chip.line.fill.background()
    chip.shadow.inherit = False
    add_text(s, cx, chips_y, Inches(1.7), Inches(0.35),
             text, size=9, color=GREEN, bold=True, font=FONT_MONO,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    cx += Inches(1.8)

# 萃取心法框
take_y = Inches(6.0)
take_h = Inches(1.0)
add_rect(s, Inches(0.6), take_y, Inches(12.1), take_h,
         fill=RGBColor(0x02, 0x20, 0x24), line_color=None)
# 左侧青色竖条
lb = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                        Inches(0.6), take_y, Emu(38100), take_h)
lb.fill.solid()
lb.fill.fore_color.rgb = CYAN
lb.line.fill.background()
lb.shadow.inherit = False

add_rich_text(s, Inches(0.9), take_y + Inches(0.15),
              Inches(11.6), take_h - Inches(0.3),
              runs=[
                  ("📐 萃取心法（组长的情报官产出范式）：", {"color": CYAN, "size": 12, "bold": True}),
                  ("\n", {}),
                  ("这段话术能复用，不是因为嘴甜，而是拆解出了可迁移的三段结构 —— ", {"color": LIGHT, "size": 11}),
                  ("共情承接", {"color": WHITE, "size": 11, "bold": True}),
                  (" + ", {"color": GRAY, "size": 11}),
                  ("行业数据锚定", {"color": WHITE, "size": 11, "bold": True}),
                  (" + ", {"color": GRAY, "size": 11}),
                  ("零压力退出承诺", {"color": WHITE, "size": 11, "bold": True}),
                  ("。组长要做的就是把\"结构\"从销冠身上拆出来，变成全团队可套用的模板。", {"color": LIGHT, "size": 11}),
              ], line_spacing=1.45)

add_footer(s, 7, 10)


# ============================================================
# SLIDE 8  真实案例时间轴
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s)
add_section_header(s, "05", "CASE — 真实挽回案例时间轴",
                   "一个 6 天的故事：AI 预警 × 组长介入 × 200 万续保逆转",
                   "⚠ 下方案例为原销售场景示意，银卡客服组长场景需替换")

# 案例 Header 卡
hy = Inches(2.1)
hh = Inches(0.8)
add_rect(s, Inches(0.6), hy, Inches(12.1), hh,
         fill=BG_CARD, line_color=RGBColor(0x5A, 0x48, 0x0C))

add_rich_text(s, Inches(0.9), hy + Inches(0.1), Inches(8), Inches(0.35),
              runs=[
                  ("CASE · ", {"color": GOLD, "size": 14, "bold": True, "font": FONT_MONO}),
                  ("李女士续保危机", {"color": WHITE, "size": 15, "bold": True}),
              ])
add_text(s, Inches(0.9), hy + Inches(0.45), Inches(8), Inches(0.3),
         "45 岁 · 高净值客户 · 重疾险即将到期 · 家庭 200 万保额",
         size=10, color=GRAY)

# 右侧结果标签
res_bg = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                            Inches(9.3), hy + Inches(0.15),
                            Inches(3.2), Inches(0.5))
res_bg.adjustments[0] = 0.2
res_bg.fill.solid()
res_bg.fill.fore_color.rgb = GOLD
res_bg.line.fill.background()
res_bg.shadow.inherit = False
add_rich_text(s, Inches(9.3), hy + Inches(0.15), Inches(3.2), Inches(0.5),
              runs=[
                  ("挽回结果：续保+加保 340 万", {"color": RGBColor(0x1A,0x15,0x00), "size": 11, "bold": True}),
              ], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# 时间轴
timeline = [
    ("T-3 天", "PAONE · 行为监测", ORANGE,
     "监测到李女士 3 次登录官网保单页、停留 8 分 47 秒，但未发起操作。同时竞品官网 cookie 出现在同设备。"),
    ("T-2 天", "PAONE · 规则引擎", ORANGE,
     "自动打标「流失高风险 · 紧急」，并推单至组长工作台（而非坐席）。系统备注：\"建议管理层亲自介入\"。"),
    ("T-1 天", "组长 · 情报准备", ORANGE,
     "调阅客户画像，发现关键线索：3 个月前咨询过理赔但未闭环。判断真实顾虑是对理赔体验的不信任。"),
    ("T 0", "组长 · 亲自致电", GOLD,
     "15 分钟通话，全程不提续费。只谈三件事：①回溯理赔咨询 ②解释流程卡点并道歉 ③承诺专属服务对接。"),
    ("T+2 天", "客户 · 主动回访", GREEN,
     "李女士主动来电询问续保升级方案，并提出为丈夫加保。最终签单续保 200 万 + 加保 140 万 = 340 万。"),
    ("T+7 天", "组长 · AI 喂养闭环", GREEN,
     "案例打标「高净值 · 理赔体验型流失」喂给 PAone。同类客户将被自动识别并优先推单。"),
]

tly = Inches(3.1)
row_height = 0.55

# 竖线
vline = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                           Inches(1.55), tly + Inches(0.15),
                           Emu(19050), Inches(3.35))
vline.fill.solid()
vline.fill.fore_color.rgb = CYAN
vline.line.fill.background()
vline.shadow.inherit = False

for i, (t, actor, color, desc) in enumerate(timeline):
    ry = tly + Inches(i * row_height)
    # 时间
    add_text(s, Inches(0.6), ry + Inches(0.12), Inches(0.85), Inches(0.3),
             t, size=11, color=color, bold=True, font=FONT_MONO,
             align=PP_ALIGN.RIGHT)
    # 圆点
    dot = s.shapes.add_shape(MSO_SHAPE.OVAL,
                             Inches(1.48), ry + Inches(0.17),
                             Inches(0.2), Inches(0.2))
    dot.fill.solid()
    dot.fill.fore_color.rgb = color
    dot.line.color.rgb = BG_DARK
    dot.line.width = Pt(1.5)
    dot.shadow.inherit = False
    # 内容卡
    cx = Inches(1.85)
    cw = Inches(10.9)
    ch = Inches(0.48)
    add_rect(s, cx, ry + Inches(0.05), cw, ch,
             fill=BG_CARD, line_color=BORDER)
    add_text(s, cx + Inches(0.2), ry + Inches(0.08), Inches(2.5), Inches(0.2),
             actor, size=8, color=color, bold=True, font=FONT_MONO)
    add_text(s, cx + Inches(0.2), ry + Inches(0.24), cw - Inches(0.3), Inches(0.3),
             desc, size=9.5, color=LIGHT)

# 底部对比
contrast_y = Inches(6.55)
contrast_h = Inches(0.55)
add_rect(s, Inches(0.6), contrast_y, Inches(5.95), contrast_h,
         fill=RGBColor(0x1A, 0x08, 0x08), line_color=None)
lb = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                        Inches(0.6), contrast_y, Emu(28575), contrast_h)
lb.fill.solid()
lb.fill.fore_color.rgb = RED
lb.line.fill.background()
lb.shadow.inherit = False
add_rich_text(s, Inches(0.8), contrast_y + Inches(0.08),
              Inches(5.6), contrast_h - Inches(0.1),
              runs=[
                  ("❌ 旧模式：", {"color": RED, "size": 10, "bold": True}),
                  ("客户出现在夕会流失名单时已签他司，根因永远无法触达。", {"color": LIGHT, "size": 10}),
              ], line_spacing=1.3)

add_rect(s, Inches(6.75), contrast_y, Inches(5.95), contrast_h,
         fill=RGBColor(0x08, 0x1A, 0x06), line_color=None)
lb2 = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                         Inches(6.75), contrast_y, Emu(28575), contrast_h)
lb2.fill.solid()
lb2.fill.fore_color.rgb = GREEN
lb2.line.fill.background()
lb2.shadow.inherit = False
add_rich_text(s, Inches(6.95), contrast_y + Inches(0.08),
              Inches(5.6), contrast_h - Inches(0.1),
              runs=[
                  ("✓ 数智指挥官：", {"color": GREEN, "size": 10, "bold": True}),
                  ("AI 提前 3 天预警 → 组长共情挽回 → 案例反向训练 AI。", {"color": LIGHT, "size": 10}),
              ], line_spacing=1.3)

add_footer(s, 8, 10)


# ============================================================
# SLIDE 9  HOW 落地路径
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s)
add_section_header(s, "06", "HOW — 落地路径",
                   "三阶段 90 天，从工具接入到能力升级",
                   "蓝图再美也要脚手架。三阶段路径让数智化转型从愿景变为可排期、可验收、可复盘的行动。")

# 大容器
rmy = Inches(2.3)
rmh = Inches(4.5)
add_rect(s, Inches(0.6), rmy, Inches(12.1), rmh,
         fill=BG_CARD, line_color=BORDER)

# 渐变连线
line_y = rmy + Inches(0.7)
line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                          Inches(2), line_y,
                          Inches(9.3), Emu(19050))
line.fill.solid()
line.fill.fore_color.rgb = YELLOW
line.line.fill.background()
line.shadow.inherit = False

stages = [
    ("01", ORANGE, "工具接入", "WEEK 1 — 2",
     ["PAone 账号与权限开通，接入团队数据源",
      "规则引擎配置：异常推单阈值 / 通报口径",
      "组长完成工具基础培训与首次诊断"]),
    ("02", YELLOW, "流程重塑", "WEEK 3 — 8",
     ["废除人肉巡视、手工取数等旧 SOP",
      "建立 AI 初筛 + 组长精辅导 的 1V1 新机制",
      "夕会改造：从汇报型转向数据驱动决策型"]),
    ("03", CYAN, "能力升级", "WEEK 9 — 12",
     ["组长完成三种新角色能力认证",
      "建立 AI 语料喂养日常机制",
      "输出首份《团队数智化复盘报告》"]),
]

stage_w = Inches(4.0)
for i, (num, color, title, period, items) in enumerate(stages):
    sx = Inches(0.8 + i * 4.1)
    sy = rmy + Inches(0.35)

    # 大圆
    circle = s.shapes.add_shape(MSO_SHAPE.OVAL,
                                sx + Inches(1.7), sy,
                                Inches(0.7), Inches(0.7))
    circle.fill.solid()
    circle.fill.fore_color.rgb = BG_CARD
    circle.line.color.rgb = color
    circle.line.width = Pt(2.5)
    circle.shadow.inherit = False
    add_text(s, sx + Inches(1.7), sy, Inches(0.7), Inches(0.7),
             num, size=16, color=color, bold=True, font=FONT_MONO,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # 标题
    add_text(s, sx, sy + Inches(0.85), stage_w, Inches(0.4),
             title, size=17, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_text(s, sx, sy + Inches(1.25), stage_w, Inches(0.3),
             period, size=10, color=DIM, font=FONT_MONO, align=PP_ALIGN.CENTER)

    # 列表
    list_bg = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                 sx + Inches(0.15), sy + Inches(1.7),
                                 stage_w - Inches(0.3), Inches(2.0))
    list_bg.adjustments[0] = 0.08
    list_bg.fill.solid()
    list_bg.fill.fore_color.rgb = RGBColor(0x05, 0x07, 0x0B)
    list_bg.line.fill.background()
    list_bg.shadow.inherit = False

    ly = sy + Inches(1.85)
    for item in items:
        add_rich_text(s, sx + Inches(0.35), ly,
                      stage_w - Inches(0.6), Inches(0.6),
                      runs=[("✓ ", {"color": CYAN, "size": 11, "bold": True}),
                            (item, {"color": GRAY, "size": 10.5})],
                      line_spacing=1.4)
        ly += Inches(0.55)

add_footer(s, 9, 10)


# ============================================================
# SLIDE 10  RESULT + 对标
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s)
add_section_header(s, "07", "RESULT — 预期业绩 + 行业对标",
                   "不止是\"改善\"，而是站在行业前列",
                   "四个验收 KPI 配套行业基准，让每一个数字都经得起追问。")

# 上半：4 个 KPI 卡
kpis = [
    ("🎯", "高价值时间占比", "53", "%", "从 28% 提升至 53%，带宽翻倍"),
    ("💎", "高风险客户挽回率", "+25", "%", "组长介入 + AI 预警前置"),
    ("📚", "销冠话术复用率", "+40", "%", "月度话术萃取入训练库"),
    ("⏱️", "异常响应时效", "T+0", "", "从 T+1 转为实时推单"),
]
ky = Inches(2.2)
kw = Inches(2.95)
kh = Inches(1.8)
for i, (icon, label, val, unit, desc) in enumerate(kpis):
    x = Inches(0.6 + i * 3.05)
    add_rect(s, x, ky, kw, kh, fill=BG_CARD, line_color=BORDER)
    add_text(s, x, ky + Inches(0.15), kw, Inches(0.4),
             icon, size=18, align=PP_ALIGN.CENTER)
    add_text(s, x, ky + Inches(0.55), kw, Inches(0.3),
             label, size=11, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    add_rich_text(s, x, ky + Inches(0.85), kw, Inches(0.6),
                  runs=[(val, {"color": CYAN, "size": 32, "bold": True}),
                        (unit, {"color": GRAY, "size": 14})],
                  align=PP_ALIGN.CENTER)
    add_text(s, x + Inches(0.2), ky + Inches(1.45), kw - Inches(0.4), Inches(0.3),
             desc, size=9, color=DIM, align=PP_ALIGN.CENTER)

# 下半：对标卡
by = Inches(4.3)
bh = Inches(2.8)
add_rect(s, Inches(0.6), by, Inches(12.1), bh,
         fill=BG_CARD, line_color=BORDER)

add_text(s, Inches(0.85), by + Inches(0.2), Inches(11), Inches(0.3),
         "📊 横向对标：我们相对行业的位置",
         size=13, color=WHITE, bold=True)
add_text(s, Inches(0.85), by + Inches(0.5), Inches(11), Inches(0.25),
         "数据来源：金融保险业服销运营基准报告 · 行业平均为呼入/服销混合型团队中位数",
         size=9, color=GRAY)

benchmarks = [
    ("高价值时间占比", "超出行业中位数 2.4 倍",
     [("行业底部 25%", 15, RGBColor(0x44,0x4A,0x5A), False),
      ("行业中位数", 22, ORANGE, False),
      ("PAone 模式", 53, CYAN, True)]),
    ("销冠话术复用率", "领先行业均值 3.3 倍",
     [("行业底部 25%", 5, RGBColor(0x44,0x4A,0x5A), False),
      ("行业中位数", 12, ORANGE, False),
      ("PAone 模式", 40, CYAN, True)]),
]

bm_y = by + Inches(0.85)
bar_max_w = Inches(6.5)
for b_i, (title, caption, tracks) in enumerate(benchmarks):
    rowy = bm_y + Inches(b_i * 0.95)
    add_text(s, Inches(0.85), rowy, Inches(8), Inches(0.3),
             title, size=11, color=WHITE, bold=True)
    add_text(s, Inches(0.85), rowy, Inches(11.65), Inches(0.3),
             caption, size=10, color=GRAY, align=PP_ALIGN.RIGHT)

    # 3 条水平 bar，高度较小
    for t_i, (name, val, color, is_us) in enumerate(tracks):
        ry = rowy + Inches(0.3 + t_i * 0.18)
        add_text(s, Inches(0.85), ry, Inches(1.8), Inches(0.18),
                 name, size=8.5, color=CYAN if is_us else GRAY,
                 bold=is_us, align=PP_ALIGN.RIGHT)
        # 背景条
        bg_bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                    Inches(2.75), ry + Inches(0.03),
                                    bar_max_w, Inches(0.15))
        bg_bar.fill.solid()
        bg_bar.fill.fore_color.rgb = RGBColor(0x1F, 0x24, 0x2E)
        bg_bar.line.fill.background()
        bg_bar.shadow.inherit = False
        # 填充条
        fill_w = Emu(int(bar_max_w * val / 60))  # 60% 为 100%
        fbar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                  Inches(2.75), ry + Inches(0.03),
                                  fill_w, Inches(0.15))
        fbar.fill.solid()
        fbar.fill.fore_color.rgb = color
        fbar.line.fill.background()
        fbar.shadow.inherit = False
        # 数值
        add_text(s, Inches(9.4), ry, Inches(0.9), Inches(0.18),
                 f"{val}%", size=9, color=CYAN if is_us else LIGHT,
                 bold=True, font=FONT_MONO, align=PP_ALIGN.RIGHT)

add_footer(s, 10, 10)


# ============================================================
# SLIDE 11  ROI
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s)
add_section_header(s, "08", "ROI — 投入产出账本",
                   "6 个月回本，远快于行业 18 个月均值",
                   "标准中等规模团队（20 坐席 + 1 组长）的 12 个月 ROI 测算。数字为示意，需用真实数据替换。")

# 左右两栏
left_x = Inches(0.6)
left_w = Inches(5.5)
right_x = Inches(6.3)
right_w = Inches(6.4)
content_y = Inches(2.3)
content_h = Inches(4.6)

add_rect(s, left_x, content_y, left_w, content_h,
         fill=RGBColor(0x1A, 0x14, 0x02), line_color=RGBColor(0x5A, 0x48, 0x0C))

add_text(s, left_x + Inches(0.4), content_y + Inches(0.5),
         left_w - Inches(0.8), Inches(0.4),
         "12 个月净收益",
         size=11, color=GOLD, bold=True, font=FONT_MONO)

add_rich_text(s, left_x + Inches(0.4), content_y + Inches(1.0),
              left_w - Inches(0.8), Inches(1.5),
              runs=[("+", {"color": WHITE, "size": 56, "bold": True}),
                    ("312", {"color": GOLD, "size": 72, "bold": True}),
                    (" 万", {"color": WHITE, "size": 32, "bold": True})])

add_rich_text(s, left_x + Inches(0.4), content_y + Inches(2.9),
              left_w - Inches(0.8), Inches(1.5),
              runs=[
                  ("对比传统数智化项目 ", {"color": GRAY, "size": 12}),
                  ("18 个月回本周期", {"color": WHITE, "size": 12, "bold": True}),
                  ("，PAone 模式凭借低部署成本与即时业绩放大效应，", {"color": GRAY, "size": 12}),
                  ("6 个月即可回本", {"color": GOLD, "size": 13, "bold": True}),
                  ("。", {"color": GRAY, "size": 12}),
              ], line_spacing=1.6)

# 右栏：明细
add_rect(s, right_x, content_y, right_w, content_h,
         fill=BG_CARD, line_color=BORDER)

roi_items = [
    ("工具部署 + 年订阅费", "- 48 万", False, False),
    ("组长 + 坐席培训成本", "- 15 万", False, False),
    ("高风险客户挽回增量（+25%）", "+ 180 万", True, False),
    ("话术复用带来转化率提升", "+ 125 万", True, False),
    ("组长带宽释放（机会成本）", "+ 70 万", True, False),
    ("12 个月净收益", "+ 312 万", True, True),
]

irow_y = content_y + Inches(0.3)
for label, value, positive, total in roi_items:
    row_h = Inches(0.55) if not total else Inches(0.7)
    row_bg = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                right_x + Inches(0.25), irow_y,
                                right_w - Inches(0.5), row_h)
    row_bg.adjustments[0] = 0.15
    row_bg.fill.solid()
    if total:
        row_bg.fill.fore_color.rgb = RGBColor(0x06, 0x2A, 0x0A)
        row_bg.line.color.rgb = GREEN
        row_bg.line.width = Pt(0.75)
    else:
        row_bg.fill.fore_color.rgb = RGBColor(0x05, 0x07, 0x0B)
        row_bg.line.fill.background()
    row_bg.shadow.inherit = False

    add_text(s, right_x + Inches(0.5), irow_y,
             right_w - Inches(2.5), row_h,
             label,
             size=12 if total else 11,
             color=WHITE if total else GRAY,
             bold=total,
             anchor=MSO_ANCHOR.MIDDLE)

    val_color = GREEN if positive else WHITE
    val_size = 16 if total else 13
    add_text(s, right_x + Inches(0.25), irow_y,
             right_w - Inches(0.65), row_h,
             value, size=val_size, color=val_color,
             bold=True, font=FONT_MONO,
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

    irow_y += row_h + Inches(0.05)

add_footer(s, 11, 10)


# ============================================================
# SLIDE 12  金句结尾
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s)

# 光晕
glow = s.shapes.add_shape(MSO_SHAPE.OVAL,
                          Inches(3.5), Inches(1),
                          Inches(6.3), Inches(5.5))
glow.fill.solid()
glow.fill.fore_color.rgb = RGBColor(0x02, 0x14, 0x18)
glow.line.fill.background()
glow.shadow.inherit = False

# 大引号
add_text(s, Inches(0.5), Inches(1.5), Inches(12.3), Inches(1.2),
         '"', size=96, color=CYAN, bold=True, align=PP_ALIGN.CENTER)

# 金句
add_rich_text(s, Inches(1), Inches(2.8), Inches(11.3), Inches(2.5),
              runs=[
                  ("引入 PAone 之后，现管岗位不仅是减负，", {"color": WHITE, "size": 24}),
                  ("\n", {}),
                  ("更是 ", {"color": WHITE, "size": 24}),
                  ("从\"管事\"向\"理人\"的质变", {"color": CYAN, "size": 26, "bold": True}),
                  ("。", {"color": WHITE, "size": 24}),
                  ("\n", {}),
                  ("\n", {}),
                  ("组长不再是\"管 10 个人的监工\"，", {"color": LIGHT, "size": 20}),
                  ("\n", {}),
                  ("而是 ", {"color": LIGHT, "size": 20}),
                  ("指挥 10 人 + 1 个 AI 军团", {"color": ORANGE, "size": 22, "bold": True}),
                  (" 的 ", {"color": LIGHT, "size": 20}),
                  ("微型业务总经理", {"color": CYAN, "size": 22, "bold": True}),
                  ("。", {"color": LIGHT, "size": 20}),
              ], align=PP_ALIGN.CENTER, line_spacing=1.7)

# 底部线
l1 = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                        Inches(3), Inches(6.5),
                        Inches(7.3), Emu(9525))
l1.fill.solid()
l1.fill.fore_color.rgb = CYAN
l1.line.fill.background()
l1.shadow.inherit = False

add_text(s, Inches(0.5), Inches(6.7), Inches(12.3), Inches(0.4),
         "— THE NEW PARADIGM OF SALES-SERVICE MANAGEMENT —",
         size=11, color=DIM, font=FONT_MONO, align=PP_ALIGN.CENTER)
add_text(s, Inches(0.5), Inches(7.05), Inches(12.3), Inches(0.4),
         "END / THANK YOU",
         size=10, color=DIM, font=FONT_MONO, align=PP_ALIGN.CENTER, bold=True)


# ============================================================
# 保存
# ============================================================
output = "report-v2.pptx"
prs.save(output)
print(f"✓ 生成完成：{output}")
print(f"  共 {len(prs.slides)} 页")
