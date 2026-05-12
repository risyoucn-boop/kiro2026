# -*- coding: utf-8 -*-
"""
服销现管数智化报告 PPTX 生成器 · 平安橙主题
白底 + 平安橙 + 16:9 商务风格
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# ===== 平安品牌配色 =====
BG_WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
BG_LIGHT    = RGBColor(0xF7, 0xF8, 0xFA)   # 浅灰底
BG_CARD     = RGBColor(0xFF, 0xFF, 0xFF)
BG_SOFT     = RGBColor(0xFD, 0xF3, 0xEA)   # 橙色极浅底
BG_SOFT_2   = RGBColor(0xFF, 0xE8, 0xD4)   # 橙色浅底

# 平安橙（主色，取 logo 标准色）
ORANGE      = RGBColor(0xEE, 0x77, 0x23)   # 主橙
ORANGE_DARK = RGBColor(0xC9, 0x5A, 0x0F)   # 深橙（重点强调）
ORANGE_LIGHT= RGBColor(0xF7, 0xA8, 0x5E)   # 浅橙

# 辅助色
DARK_BLUE   = RGBColor(0x1F, 0x3A, 0x5F)   # 深蓝（用于对比强调）
DARK_BLUE_2 = RGBColor(0x2D, 0x54, 0x88)

# 文本色阶
TEXT_DARK   = RGBColor(0x1A, 0x1D, 0x29)
TEXT        = RGBColor(0x33, 0x38, 0x47)
TEXT_MID    = RGBColor(0x6B, 0x72, 0x80)
TEXT_LIGHT  = RGBColor(0x9A, 0xA0, 0xAC)
BORDER      = RGBColor(0xE4, 0xE7, 0xEC)
BORDER_DARK = RGBColor(0xC9, 0xCF, 0xD8)

# 状态色
RED         = RGBColor(0xD9, 0x36, 0x3E)
GREEN       = RGBColor(0x1F, 0x9D, 0x55)
YELLOW      = RGBColor(0xF5, 0xB1, 0x2D)
GOLD        = RGBColor(0xD4, 0x9E, 0x1D)

# 16:9
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
blank = prs.slide_layouts[6]

FONT = "Microsoft YaHei"
FONT_MONO = "Consolas"


# ===== 工具函数 =====
def add_bg(slide, color=BG_WHITE):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bg.line.fill.background()
    bg.fill.solid()
    bg.fill.fore_color.rgb = color
    bg.shadow.inherit = False
    return bg


def add_rect(slide, x, y, w, h, fill=BG_CARD, line_color=None, line_width=0.75, corner=True, corner_adj=0.06):
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
    if corner:
        try:
            shape.adjustments[0] = corner_adj
        except Exception:
            pass
    return shape


def add_text(slide, x, y, w, h, text, size=14, color=TEXT, bold=False,
             font=FONT, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, italic=False,
             line_spacing=1.3):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.margin_left = Emu(0); tf.margin_right = Emu(0)
    tf.margin_top = Emu(0); tf.margin_bottom = Emu(0)
    tf.word_wrap = True
    tf.vertical_anchor = anchor
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
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.margin_left = Emu(0); tf.margin_right = Emu(0)
    tf.margin_top = Emu(0); tf.margin_bottom = Emu(0)
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
        r.font.color.rgb = attrs.get("color", TEXT)
    return tb


def add_section_header(slide, number, label, title, lead=None, y_start=Inches(0.5)):
    # 顶部橙色编号
    add_text(slide, Inches(0.7), y_start, Inches(10), Inches(0.3),
             f"{number}  /  {label}",
             size=10, color=ORANGE, font=FONT_MONO, bold=True)
    # 橙色短线
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                 Inches(0.7), y_start + Inches(0.4),
                                 Inches(0.55), Emu(38100))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ORANGE
    bar.line.fill.background()
    bar.shadow.inherit = False
    # 标题
    add_text(slide, Inches(0.7), y_start + Inches(0.55), Inches(12), Inches(0.55),
             title, size=24, color=TEXT_DARK, bold=True)
    if lead:
        add_text(slide, Inches(0.7), y_start + Inches(1.2), Inches(12), Inches(0.5),
                 lead, size=12, color=TEXT_MID, line_spacing=1.4)


def add_footer(slide, page_num, total=12):
    # 分割线
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                  Inches(0.7), Inches(7.12),
                                  Inches(11.9), Emu(9525))
    line.fill.solid()
    line.fill.fore_color.rgb = BORDER
    line.line.fill.background()
    line.shadow.inherit = False
    # 左侧 - 平安橙圆点 + 品牌
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                 Inches(0.7), Inches(7.25),
                                 Inches(0.12), Inches(0.12))
    dot.fill.solid()
    dot.fill.fore_color.rgb = ORANGE
    dot.line.fill.background()
    dot.shadow.inherit = False
    add_text(slide, Inches(0.9), Inches(7.22), Inches(9), Inches(0.22),
             "PAONE · 服销现管数智化转型白皮书",
             size=9, color=TEXT_LIGHT, font=FONT_MONO)
    # 右 - 页码
    add_text(slide, Inches(10.5), Inches(7.22), Inches(2.2), Inches(0.22),
             f"{page_num:02d} / {total:02d}",
             size=9, color=TEXT_LIGHT, font=FONT_MONO, align=PP_ALIGN.RIGHT)


TOTAL_PAGES = 12


# ============================================================
# SLIDE 1  封面
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s, BG_WHITE)

# 顶部橙色色带
top_bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Inches(0.12))
top_bar.fill.solid(); top_bar.fill.fore_color.rgb = ORANGE
top_bar.line.fill.background(); top_bar.shadow.inherit = False

# 左侧装饰大色块
deco = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(0.12),
                          Inches(4.5), SLIDE_H - Inches(0.12))
deco.fill.solid(); deco.fill.fore_color.rgb = ORANGE
deco.line.fill.background(); deco.shadow.inherit = False

# 左侧斜切装饰
deco2 = s.shapes.add_shape(MSO_SHAPE.RIGHT_TRIANGLE,
                           Inches(4.5), Inches(0.12),
                           Inches(1.2), SLIDE_H - Inches(0.12))
deco2.fill.solid(); deco2.fill.fore_color.rgb = ORANGE
deco2.line.fill.background(); deco2.shadow.inherit = False
deco2.rotation = 90

# 左侧文字
add_text(s, Inches(0.6), Inches(1.0), Inches(3.7), Inches(0.35),
         "PING AN · PAone", size=13, color=BG_WHITE, font=FONT_MONO,
         bold=True)
# 白色细线
line_deco = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                               Inches(0.6), Inches(1.45),
                               Inches(0.6), Emu(19050))
line_deco.fill.solid(); line_deco.fill.fore_color.rgb = BG_WHITE
line_deco.line.fill.background(); line_deco.shadow.inherit = False

add_text(s, Inches(0.6), Inches(1.7), Inches(3.7), Inches(0.4),
         "白皮书 · 2026", size=14, color=BG_WHITE, bold=False)

add_text(s, Inches(0.6), Inches(6.0), Inches(3.7), Inches(0.35),
         "WHITEPAPER", size=11, color=BG_WHITE, font=FONT_MONO)
add_text(s, Inches(0.6), Inches(6.35), Inches(3.7), Inches(0.35),
         "服销团队长数字化落地研究", size=11, color=BG_WHITE)

# 右侧主标题
add_text(s, Inches(6.2), Inches(1.6), Inches(6.8), Inches(0.4),
         "PAone × 服销现管",
         size=14, color=ORANGE, font=FONT_MONO, bold=True)

# 细橙线
title_line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                Inches(6.2), Inches(2.05),
                                Inches(0.7), Emu(28575))
title_line.fill.solid(); title_line.fill.fore_color.rgb = ORANGE
title_line.line.fill.background(); title_line.shadow.inherit = False

add_text(s, Inches(6.2), Inches(2.3), Inches(6.8), Inches(0.85),
         "现管再造",
         size=54, color=TEXT_DARK, bold=True)

add_rich_text(s, Inches(6.2), Inches(3.35), Inches(6.8), Inches(1.8),
              runs=[
                  ("当 ", {"color": TEXT, "size": 24}),
                  ("PAone", {"color": ORANGE, "size": 24, "bold": True}),
                  (" 接管机械劳动，", {"color": TEXT, "size": 24}),
                  ("\n", {}),
                  ("组长该 ", {"color": TEXT, "size": 24}),
                  ("去哪里？", {"color": ORANGE_DARK, "size": 26, "bold": True}),
              ], line_spacing=1.4)

# 分隔
sep = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                         Inches(6.2), Inches(5.3),
                         Inches(4), Emu(9525))
sep.fill.solid(); sep.fill.fore_color.rgb = BORDER_DARK
sep.line.fill.background(); sep.shadow.inherit = False

add_text(s, Inches(6.2), Inches(5.45), Inches(6.8), Inches(0.3),
         "FROM LABOR-INTENSIVE TO INTELLIGENCE-DRIVEN",
         size=11, color=TEXT_MID, font=FONT_MONO)
add_text(s, Inches(6.2), Inches(5.85), Inches(6.8), Inches(0.35),
         "量化收益  ·  角色新范式  ·  实战案例  ·  行业对标  ·  ROI 账本",
         size=12, color=TEXT)

# 底部版权条
add_text(s, Inches(6.2), Inches(6.85), Inches(6.8), Inches(0.3),
         "PING AN · INTERNAL WHITEPAPER · 2026",
         size=9, color=TEXT_LIGHT, font=FONT_MONO)


# ============================================================
# SLIDE 2  目录
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s, BG_WHITE)
add_section_header(s, "CONTENTS", "目录 / AGENDA",
                   "七个章节，一条从困境到回报的完整叙事链")

toc = [
    ("01", "WHY", "困境诊断", "组长的一天，为什么总是很忙却没干成事"),
    ("02", "WHAT", "量化收益账本", "总工时未减，但管理带宽正在结构性迁徙"),
    ("03", "WHO", "角色新范式", "组长不再是监工，而是数智指挥官"),
    ("04", "PLAYBOOK", "话术萃取实战", "从\"客户说再考虑一下\"看情报官价值"),
    ("05", "CASE", "真实挽回案例", "6 天的故事：AI 预警 × 组长介入"),
    ("06", "HOW", "90 天落地路径", "从工具接入到能力升级的三阶段"),
    ("07", "RESULT", "KPI + 行业对标", "不止是改善，而是站在行业前列"),
    ("08", "ROI", "投入产出账本", "6 个月回本，远快于行业均值"),
]

start_y = 1.9
for i, (num, en, cn, desc) in enumerate(toc):
    row = i // 2
    col = i % 2
    x = Inches(0.7 + col * 6.15)
    y = Inches(start_y + row * 1.18)
    w = Inches(5.95)
    h = Inches(1.05)
    # 卡片
    add_rect(s, x, y, w, h, fill=BG_CARD, line_color=BORDER, line_width=0.75)
    # 左侧橙色块
    left_bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                  x, y, Emu(38100), h)
    left_bar.fill.solid(); left_bar.fill.fore_color.rgb = ORANGE
    left_bar.line.fill.background(); left_bar.shadow.inherit = False
    # 编号
    add_text(s, x + Inches(0.25), y + Inches(0.14), Inches(0.85), Inches(0.5),
             num, size=26, color=ORANGE, bold=True, font=FONT_MONO)
    # EN label
    add_text(s, x + Inches(0.25), y + Inches(0.65), Inches(1.2), Inches(0.25),
             en, size=9, color=TEXT_LIGHT, font=FONT_MONO, bold=True)
    # 中文标题
    add_text(s, x + Inches(1.5), y + Inches(0.22), w - Inches(1.7), Inches(0.35),
             cn, size=15, color=TEXT_DARK, bold=True)
    # 描述
    add_text(s, x + Inches(1.5), y + Inches(0.62), w - Inches(1.7), Inches(0.35),
             desc, size=10, color=TEXT_MID)

add_footer(s, 2, TOTAL_PAGES)


# ============================================================
# SLIDE 3  WHY 困境诊断
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s, BG_WHITE)
add_section_header(s, "01", "WHY — 困境诊断",
                   "组长的一天，为什么总是\"很忙却没干成事\"？",
                   "直面当下现管岗位的三重结构性痛点 —— 这不是个人能力问题，而是工具缺位下的必然。")

pains = [
    ("01", "时间黑洞",
     "日均工时中超过 60% 被消耗在\"捞数据、做表格、人肉盯盘\"等低价值机械劳动上，真正用于业务思考与团队辅导的时间被严重挤压。",
     "> 350 min / 天"),
    ("02", "辅导失焦",
     "1V1 沟通缺少数据抓手，常常沦为\"泛泛谈心、打鸡血\"。组长无法精准定位坐席能力短板，更难以提供可执行的话术级辅导。",
     "165 min / 天 低效投入"),
    ("03", "决策滞后",
     "问题发现严重依赖夕会复盘，而非实时感知。当异常数据出现在报表上时，最佳干预窗口往往已经关闭，组长被迫陷入\"事后救火\"的被动循环。",
     "T+1 响应"),
]

card_w = Inches(3.9)
card_h = Inches(4.2)
gap = 0.25
for i, (num, title, desc, stat) in enumerate(pains):
    x = Inches(0.7 + i * (3.9 + gap))
    y = Inches(2.5)
    # 卡片
    add_rect(s, x, y, card_w, card_h, fill=BG_CARD, line_color=BORDER, line_width=0.75)
    # 顶部橙色块
    top = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, card_w, Inches(0.08))
    top.fill.solid(); top.fill.fore_color.rgb = ORANGE
    top.line.fill.background(); top.shadow.inherit = False
    # 大数字
    add_text(s, x + Inches(0.4), y + Inches(0.35), Inches(1.5), Inches(0.85),
             num, size=44, color=ORANGE, bold=True, font=FONT_MONO)
    # 标题下划线
    title_line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                    x + Inches(0.4), y + Inches(1.7),
                                    Inches(0.5), Emu(28575))
    title_line.fill.solid(); title_line.fill.fore_color.rgb = ORANGE
    title_line.line.fill.background(); title_line.shadow.inherit = False
    # 标题
    add_text(s, x + Inches(0.4), y + Inches(1.25), card_w - Inches(0.8), Inches(0.4),
             title, size=22, color=TEXT_DARK, bold=True)
    # 描述
    add_text(s, x + Inches(0.4), y + Inches(1.95), card_w - Inches(0.8), Inches(1.6),
             desc, size=12, color=TEXT_MID, line_spacing=1.6)
    # 统计徽章
    badge_y = y + card_h - Inches(0.65)
    badge = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                               x + Inches(0.4), badge_y,
                               card_w - Inches(0.8), Inches(0.42))
    badge.adjustments[0] = 0.4
    badge.fill.solid(); badge.fill.fore_color.rgb = BG_SOFT
    badge.line.fill.background(); badge.shadow.inherit = False
    add_text(s, x + Inches(0.4), badge_y, card_w - Inches(0.8), Inches(0.42),
             stat, size=11, color=ORANGE_DARK, bold=True, font=FONT_MONO,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_footer(s, 3, TOTAL_PAGES)


# ============================================================
# SLIDE 4  WHAT 带宽迁徙总览
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s, BG_WHITE)
add_section_header(s, "02", "WHAT — 量化收益账本",
                   "总工时未减，但管理带宽正在\"结构性迁徙\"",
                   "引入 PAone 后，组长总工时并没有减少。真正发生的是时间从机械劳动迁徙到了高价值辅导。")

# 大容器
cont_x = Inches(0.7)
cont_y = Inches(2.35)
cont_w = Inches(11.9)
cont_h = Inches(4.6)
add_rect(s, cont_x, cont_y, cont_w, cont_h, fill=BG_LIGHT, line_color=BORDER)

# 大数字
add_rich_text(s, cont_x, cont_y + Inches(0.3), cont_w, Inches(0.8),
              runs=[
                  ("585 min ", {"color": ORANGE, "size": 40, "bold": True}),
                  ("=", {"color": TEXT_LIGHT, "size": 40, "bold": True}),
                  (" 585 min", {"color": ORANGE, "size": 40, "bold": True}),
              ], align=PP_ALIGN.CENTER)

add_rich_text(s, cont_x, cont_y + Inches(1.1), cont_w, Inches(0.4),
              runs=[
                  ("旧模式与新模式 ", {"color": TEXT_MID, "size": 12}),
                  ("总工时完全相等", {"color": TEXT_DARK, "size": 12, "bold": True}),
                  ("，但时间结构发生质变：高价值投入从 28% 提升至 ", {"color": TEXT_MID, "size": 12}),
                  ("53%", {"color": ORANGE, "size": 13, "bold": True}),
              ], align=PP_ALIGN.CENTER)

# 条形图
bar_x = cont_x + Inches(0.8)
bar_w = Inches(10.3)
total_min = 585

# Label 旧
add_text(s, bar_x, cont_y + Inches(1.8), bar_w, Inches(0.3),
         "旧模式 · 劳动密集型", size=11, color=TEXT_MID, font=FONT_MONO)
add_text(s, bar_x, cont_y + Inches(1.8), bar_w, Inches(0.3),
         "Total: 585 min", size=11, color=TEXT_DARK, bold=True, align=PP_ALIGN.RIGHT)

old_segs = [(30,  ORANGE_LIGHT, "碎片 30", BG_WHITE),
            (155, YELLOW,       "数据盘点 155", RGBColor(0x33,0x33,0x33)),
            (165, ORANGE,       "核心辅导 165", BG_WHITE),
            (235, BORDER_DARK,  "会议协同 235", TEXT)]
cur_x = bar_x
bar_h = Inches(0.55)
bar_y = cont_y + Inches(2.15)
for minutes, color, label, text_color in old_segs:
    seg_w = Emu(int(bar_w * minutes / total_min))
    seg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, cur_x, bar_y, seg_w, bar_h)
    seg.fill.solid(); seg.fill.fore_color.rgb = color
    seg.line.fill.background(); seg.shadow.inherit = False
    add_text(s, cur_x, bar_y, seg_w, bar_h, label,
             size=10, color=text_color, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    cur_x += seg_w

# Label 新
add_text(s, bar_x, cont_y + Inches(2.95), bar_w, Inches(0.3),
         "新模式 · 数智驱动型", size=11, color=TEXT_MID, font=FONT_MONO)
add_text(s, bar_x, cont_y + Inches(2.95), bar_w, Inches(0.3),
         "Total: 585 min", size=11, color=TEXT_DARK, bold=True, align=PP_ALIGN.RIGHT)

new_segs = [(5,   ORANGE_LIGHT, "5", BG_WHITE),
            (35,  YELLOW,       "35", RGBColor(0x33,0x33,0x33)),
            (310, ORANGE_DARK,  "核心辅导 310  ·  高价值带宽", BG_WHITE),
            (235, BORDER_DARK,  "会议协同 235", TEXT)]
cur_x = bar_x
bar_y = cont_y + Inches(3.3)
for minutes, color, label, text_color in new_segs:
    seg_w = Emu(int(bar_w * minutes / total_min))
    seg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, cur_x, bar_y, seg_w, bar_h)
    seg.fill.solid(); seg.fill.fore_color.rgb = color
    seg.line.fill.background(); seg.shadow.inherit = False
    add_text(s, cur_x, bar_y, seg_w, bar_h, label,
             size=10, color=text_color, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    cur_x += seg_w

# Legend
legend_y = cont_y + Inches(4.1)
legend_items = [("碎片巡视", ORANGE_LIGHT), ("数据盘点", YELLOW),
                ("核心辅导（钻石）", ORANGE_DARK), ("会议协同", BORDER_DARK)]
lx = cont_x + Inches(1.6)
for label, color in legend_items:
    dot = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, lx, legend_y + Inches(0.08),
                             Inches(0.15), Inches(0.15))
    dot.fill.solid(); dot.fill.fore_color.rgb = color
    dot.line.fill.background(); dot.shadow.inherit = False
    add_text(s, lx + Inches(0.25), legend_y, Inches(2.3), Inches(0.3),
             label, size=10, color=TEXT_MID)
    lx += Inches(2.4)

add_footer(s, 4, TOTAL_PAGES)


# ============================================================
# SLIDE 5  WHAT 数据表
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s, BG_WHITE)
add_section_header(s, "02", "WHAT — 量化收益账本（续）",
                   "四个管理模块的时间迁徙明细",
                   "下表按价值层级排序，钻石区（核心辅导）是本次转型的最大赢家。")

table_data = [
    ("L3 钻石", ORANGE, "核心干预与 1V1 辅导", "165 min", "310 min", "▲ +87.8%", GREEN,
     "核心投向：从\"泛泛谈心\"跃升为\"数据驱动的精准赋能\"", True),
    ("L2 中性", YELLOW, "会议管理与组织协同", "235 min", "235 min", "— 持平", TEXT_MID,
     "时长不变，但决策依据从\"凭经验拍板\"升级为\"AI 情报+实时看板\"", False),
    ("L1 机械", TEXT_LIGHT, "数据盘点与材料准备", "155 min", "35 min", "▼ -77.4%", RED,
     "RPA + AIGC 一键生成早夕会与通报材料，释放机械体力活", False),
    ("L1 机械", TEXT_LIGHT, "碎片状态巡视", "30 min", "5 min", "▼ -83.3%", RED,
     "消灭\"人肉盯盘\"，规则引擎自动识别异常并主动推单", False),
]

tx = Inches(0.7)
ty = Inches(2.4)
tw = Inches(11.9)
row_h = Inches(0.95)

header_h = Inches(0.5)
hdr = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, tx, ty, tw, header_h)
hdr.fill.solid(); hdr.fill.fore_color.rgb = ORANGE
hdr.line.fill.background(); hdr.shadow.inherit = False

col_widths = [Inches(3.2), Inches(1.4), Inches(1.4), Inches(1.4), Inches(4.5)]
col_xs = [tx]
for w in col_widths[:-1]:
    col_xs.append(col_xs[-1] + w)

headers = ["管理模块", "旧模式", "新模式", "效能变化", "带宽流向与价值"]
for i, h in enumerate(headers):
    add_text(s, col_xs[i] + Inches(0.2), ty, col_widths[i], header_h,
             h, size=11, color=BG_WHITE, bold=True, anchor=MSO_ANCHOR.MIDDLE)

for ri, (lvl, lvl_color, mod, old_t, new_t, rate, rate_color, desc, highlight) in enumerate(table_data):
    rr_y = ty + header_h + Inches(ri * 0.95)
    row_bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, tx, rr_y, tw, row_h)
    if highlight:
        row_bg.fill.solid(); row_bg.fill.fore_color.rgb = BG_SOFT
    else:
        row_bg.fill.solid(); row_bg.fill.fore_color.rgb = BG_WHITE
    row_bg.line.color.rgb = BORDER; row_bg.line.width = Pt(0.5)
    row_bg.shadow.inherit = False

    if highlight:
        left_bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, tx, rr_y,
                                      Emu(38100), row_h)
        left_bar.fill.solid(); left_bar.fill.fore_color.rgb = ORANGE
        left_bar.line.fill.background(); left_bar.shadow.inherit = False

    # Level tag
    tag = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                             col_xs[0] + Inches(0.2), rr_y + Inches(0.15),
                             Inches(0.85), Inches(0.3))
    tag.adjustments[0] = 0.35
    tag.fill.solid()
    tag.fill.fore_color.rgb = BG_WHITE if highlight else BG_LIGHT
    tag.line.color.rgb = lvl_color; tag.line.width = Pt(0.5)
    tag.shadow.inherit = False
    add_text(s, col_xs[0] + Inches(0.2), rr_y + Inches(0.15),
             Inches(0.85), Inches(0.3),
             lvl, size=9, color=lvl_color, bold=True, font=FONT_MONO,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, col_xs[0] + Inches(0.2), rr_y + Inches(0.5),
             col_widths[0] - Inches(0.3), Inches(0.4),
             mod, size=12, color=TEXT_DARK, bold=True)

    for idx, (val, color, bg) in enumerate([(old_t, TEXT_MID, BG_LIGHT),
                                             (new_t, ORANGE_DARK, BG_SOFT)]):
        ttag = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                  col_xs[1 + idx] + Inches(0.15),
                                  rr_y + Inches(0.3),
                                  Inches(1.1), Inches(0.35))
        ttag.adjustments[0] = 0.3
        ttag.fill.solid(); ttag.fill.fore_color.rgb = bg
        ttag.line.fill.background(); ttag.shadow.inherit = False
        add_text(s, col_xs[1 + idx] + Inches(0.15), rr_y + Inches(0.3),
                 Inches(1.1), Inches(0.35),
                 val, size=11, color=color, bold=True, font=FONT_MONO,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    add_text(s, col_xs[3] + Inches(0.1), rr_y, col_widths[3] - Inches(0.2), row_h,
             rate, size=13, color=rate_color, bold=True, font=FONT_MONO,
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, col_xs[4] + Inches(0.15), rr_y, col_widths[4] - Inches(0.3), row_h,
             desc, size=11, color=TEXT_DARK if highlight else TEXT_MID,
             anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.4)

add_footer(s, 5, TOTAL_PAGES)


# ============================================================
# SLIDE 6  WHO 角色新范式
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s, BG_WHITE)
add_section_header(s, "03", "WHO — 角色新范式",
                   "组长不再是\"监工\"，而是\"数智指挥官\"",
                   "机械劳动被 PAone 接管 → 管理带宽被释放 → 岗位能力模型被重新定义。组长正在进化为三重新角色。")

trans_y = Inches(2.35)
trans_h = Inches(0.65)

def add_trans_box(slide, x, y, w, h, text, fill, border, text_color, line_through=False):
    b = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    b.adjustments[0] = 0.2
    b.fill.solid(); b.fill.fore_color.rgb = fill
    b.line.color.rgb = border; b.line.width = Pt(0.75)
    b.shadow.inherit = False
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.margin_left = Emu(0); tf.margin_right = Emu(0)
    tf.margin_top = Emu(0); tf.margin_bottom = Emu(0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = text
    r.font.name = FONT; r.font.size = Pt(12)
    r.font.bold = True; r.font.color.rgb = text_color
    if line_through:
        rPr = r._r.get_or_add_rPr()
        rPr.set('strike', 'sngStrike')

add_trans_box(s, Inches(0.9), trans_y, Inches(2.7), trans_h,
              "盯流程的监工", BG_LIGHT, BORDER_DARK, TEXT_MID, line_through=True)
add_text(s, Inches(3.6), trans_y, Inches(0.7), trans_h, "→",
         size=22, color=TEXT_LIGHT, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_trans_box(s, Inches(4.3), trans_y, Inches(2.7), trans_h,
              "救火的客诉员", BG_LIGHT, BORDER_DARK, TEXT_MID, line_through=True)
add_text(s, Inches(7.0), trans_y, Inches(0.7), trans_h, "→",
         size=22, color=ORANGE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_trans_box(s, Inches(7.7), trans_y, Inches(4.9), trans_h,
              "数智指挥官 · 微型业务总经理", ORANGE, ORANGE, BG_WHITE)

roles = [
    ("🛡", "EMOTIONAL SHIELD", "情绪价值终极兜底人",
     [("不再纠结流程：", "AI 已秒级完成查单与核实，组长将精力 100% 投入高风险客户的情感挽回。"),
      ("人性化防波堤：", "发挥人类共情力，处理 AI 逻辑之外的复杂客诉，守住服务品牌最后防线。")],
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

card_y = Inches(3.25)
card_w = Inches(3.85)
card_h = Inches(3.7)
for i, (icon, label, title, points, kpi) in enumerate(roles):
    x = Inches(0.7 + i * 4.1)
    add_rect(s, x, card_y, card_w, card_h, fill=BG_CARD, line_color=BORDER)
    # 顶部橙色装饰
    topdeco = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, card_y, Inches(1.3), Inches(0.05))
    topdeco.fill.solid(); topdeco.fill.fore_color.rgb = ORANGE
    topdeco.line.fill.background(); topdeco.shadow.inherit = False

    add_text(s, x + Inches(0.3), card_y + Inches(0.2), Inches(1), Inches(0.5),
             icon, size=24, color=ORANGE)
    add_text(s, x + Inches(0.3), card_y + Inches(0.85), card_w - Inches(0.6), Inches(0.25),
             label, size=9, color=ORANGE, bold=True, font=FONT_MONO)
    add_text(s, x + Inches(0.3), card_y + Inches(1.1), card_w - Inches(0.6), Inches(0.4),
             title, size=15, color=TEXT_DARK, bold=True)
    # 细线
    sep = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                             x + Inches(0.3), card_y + Inches(1.55),
                             Inches(0.6), Emu(19050))
    sep.fill.solid(); sep.fill.fore_color.rgb = ORANGE
    sep.line.fill.background(); sep.shadow.inherit = False

    py = card_y + Inches(1.7)
    for strong, rest in points:
        add_rich_text(s, x + Inches(0.3), py,
                      card_w - Inches(0.6), Inches(0.85),
                      runs=[("▸ ", {"color": ORANGE, "size": 11, "bold": True}),
                            (strong, {"color": TEXT_DARK, "size": 10, "bold": True}),
                            (rest, {"color": TEXT_MID, "size": 10})],
                      line_spacing=1.4)
        py += Inches(0.8)

    kpi_y = card_y + card_h - Inches(0.75)
    kpi_box = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                  x + Inches(0.25), kpi_y,
                                  card_w - Inches(0.5), Inches(0.58))
    kpi_box.fill.solid(); kpi_box.fill.fore_color.rgb = BG_SOFT
    kpi_box.line.fill.background(); kpi_box.shadow.inherit = False
    left = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                              x + Inches(0.25), kpi_y,
                              Emu(28575), Inches(0.58))
    left.fill.solid(); left.fill.fore_color.rgb = ORANGE
    left.line.fill.background(); left.shadow.inherit = False
    add_text(s, x + Inches(0.4), kpi_y + Inches(0.06),
             card_w - Inches(0.6), Inches(0.22),
             "KEY ACTION · 量化抓手", size=8, color=ORANGE_DARK,
             bold=True, font=FONT_MONO)
    add_text(s, x + Inches(0.4), kpi_y + Inches(0.28),
             card_w - Inches(0.6), Inches(0.28),
             kpi, size=10, color=TEXT_DARK, bold=True)

add_footer(s, 6, TOTAL_PAGES)


# ============================================================
# SLIDE 7  话术萃取实战
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s, BG_WHITE)
add_section_header(s, "04", "PLAYBOOK — 销冠话术萃取实战",
                   "拆解一次真实萃取：从\"客户说再考虑一下\"看组长的情报官价值",
                   "角色定义是虚的，样本才是实的。组长作为情报官每月从 AI 初筛的优质录音中萃取话术，反哺团队训练库。")

# 场景标题
scene_y = Inches(2.35)
scene_h = Inches(0.6)
scene_bg = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                              Inches(0.7), scene_y, Inches(11.9), scene_h)
scene_bg.adjustments[0] = 0.2
scene_bg.fill.solid(); scene_bg.fill.fore_color.rgb = BG_LIGHT
scene_bg.line.color.rgb = BORDER; scene_bg.line.width = Pt(0.5)
scene_bg.shadow.inherit = False

# SCENE badge
badge = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                           Inches(0.95), scene_y + Inches(0.12),
                           Inches(0.9), Inches(0.36))
badge.adjustments[0] = 0.5
badge.fill.solid(); badge.fill.fore_color.rgb = ORANGE
badge.line.fill.background(); badge.shadow.inherit = False
add_text(s, Inches(0.95), scene_y + Inches(0.12), Inches(0.9), Inches(0.36),
         "SCENE", size=10, color=BG_WHITE, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_text(s, Inches(2.0), scene_y, Inches(7.5), scene_h,
         "客户反馈：\"我再考虑一下，暂时不太需要\"",
         size=15, color=TEXT_DARK, bold=True, anchor=MSO_ANCHOR.MIDDLE)

add_rich_text(s, Inches(9.5), scene_y, Inches(3.0), scene_h,
              runs=[
                  ("出现频次：", {"color": TEXT_MID, "size": 10}),
                  ("\n", {}),
                  ("日均 37 次", {"color": ORANGE, "size": 12, "bold": True}),
                  ("  · 黑洞级高频", {"color": TEXT_MID, "size": 10}),
              ], align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

# 左右对比
comp_y = Inches(3.15)
comp_h = Inches(2.75)
comp_w = Inches(5.85)

# 左：普通
add_rect(s, Inches(0.7), comp_y, comp_w, comp_h,
         fill=BG_WHITE, line_color=RGBColor(0xF5, 0xC6, 0xC7), line_width=1)
lbl1 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                          Inches(0.95), comp_y + Inches(0.2),
                          Inches(2.2), Inches(0.35))
lbl1.adjustments[0] = 0.4
lbl1.fill.solid(); lbl1.fill.fore_color.rgb = RGBColor(0xFC, 0xE8, 0xE9)
lbl1.line.fill.background(); lbl1.shadow.inherit = False
add_text(s, Inches(0.95), comp_y + Inches(0.2), Inches(2.2), Inches(0.35),
         "❌ 普通坐席话术", size=10, color=RED, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_text(s, Inches(0.95), comp_y + Inches(0.75), comp_w - Inches(0.5), Inches(1.3),
         "\"好的王姐，那您有需要随时联系我哈~ 我们的产品真的很好，您可以再了解一下。祝您生活愉快！\"",
         size=11, color=TEXT, italic=True, line_spacing=1.6)

chips_y = comp_y + Inches(2.1)
chips = [("二次触达 12%", RED), ("流失率 78%", RED), ("挽回 >14 天", RED)]
cx = Inches(0.95)
for text, color in chips:
    chip = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                              cx, chips_y, Inches(1.65), Inches(0.35))
    chip.adjustments[0] = 0.35
    chip.fill.solid(); chip.fill.fore_color.rgb = RGBColor(0xFC, 0xE8, 0xE9)
    chip.line.fill.background(); chip.shadow.inherit = False
    add_text(s, cx, chips_y, Inches(1.65), Inches(0.35),
             text, size=9, color=RED, bold=True, font=FONT_MONO,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    cx += Inches(1.75)

# 右：销冠（平安橙主题）
add_rect(s, Inches(6.75), comp_y, comp_w, comp_h,
         fill=BG_SOFT, line_color=ORANGE, line_width=1)
lbl2 = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                          Inches(7.0), comp_y + Inches(0.2),
                          Inches(3.5), Inches(0.35))
lbl2.adjustments[0] = 0.4
lbl2.fill.solid(); lbl2.fill.fore_color.rgb = ORANGE
lbl2.line.fill.background(); lbl2.shadow.inherit = False
add_text(s, Inches(7.0), comp_y + Inches(0.2), Inches(3.5), Inches(0.35),
         "✓ 销冠话术（AI 萃取后沉淀）", size=10, color=BG_WHITE, bold=True,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

add_rich_text(s, Inches(7.0), comp_y + Inches(0.75),
              comp_w - Inches(0.5), Inches(1.3),
              runs=[
                  ("\"王姐，特别理解您这个感受。其实您刚说的'再考虑'，我经手的客户里 90% 最后真正的顾虑都在三件事上 —— ", {"color": TEXT, "size": 10.5, "italic": True}),
                  ("价格、理赔流程、或保障范围", {"color": ORANGE_DARK, "size": 10.5, "italic": True, "bold": True}),
                  ("。我这边有个不占用您太多时间的办法：我直接用您家庭情况帮您模拟三种方案的差别，", {"color": TEXT, "size": 10.5, "italic": True}),
                  ("看完没兴趣这事就过去", {"color": ORANGE_DARK, "size": 10.5, "italic": True, "bold": True}),
                  ("，行吗？\"", {"color": TEXT, "size": 10.5, "italic": True}),
              ], line_spacing=1.55)

chips2 = [("二次触达 46%", ORANGE_DARK), ("转化率 34%", ORANGE_DARK), ("挽回 3 天", ORANGE_DARK)]
cx = Inches(7.0)
for text, color in chips2:
    chip = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                              cx, chips_y, Inches(1.65), Inches(0.35))
    chip.adjustments[0] = 0.35
    chip.fill.solid(); chip.fill.fore_color.rgb = BG_WHITE
    chip.line.color.rgb = ORANGE; chip.line.width = Pt(0.5)
    chip.shadow.inherit = False
    add_text(s, cx, chips_y, Inches(1.65), Inches(0.35),
             text, size=9, color=color, bold=True, font=FONT_MONO,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    cx += Inches(1.75)

# 萃取心法框
take_y = Inches(6.05)
take_h = Inches(0.95)
add_rect(s, Inches(0.7), take_y, Inches(11.9), take_h,
         fill=BG_SOFT, line_color=None)
lb = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                        Inches(0.7), take_y, Emu(38100), take_h)
lb.fill.solid(); lb.fill.fore_color.rgb = ORANGE
lb.line.fill.background(); lb.shadow.inherit = False

add_rich_text(s, Inches(1.0), take_y + Inches(0.15),
              Inches(11.4), take_h - Inches(0.3),
              runs=[
                  ("📐 萃取心法（组长的情报官产出范式）：", {"color": ORANGE_DARK, "size": 12, "bold": True}),
                  ("\n", {}),
                  ("这段话术能复用，不是因为嘴甜，而是拆解出了可迁移的三段结构 —— ", {"color": TEXT, "size": 11}),
                  ("共情承接", {"color": TEXT_DARK, "size": 11, "bold": True}),
                  (" + ", {"color": TEXT_MID, "size": 11}),
                  ("行业数据锚定", {"color": TEXT_DARK, "size": 11, "bold": True}),
                  (" + ", {"color": TEXT_MID, "size": 11}),
                  ("零压力退出承诺", {"color": TEXT_DARK, "size": 11, "bold": True}),
                  ("。组长要做的就是把\"结构\"从销冠身上拆出来，变成全团队可套用的模板。", {"color": TEXT, "size": 11}),
              ], line_spacing=1.45)

add_footer(s, 7, TOTAL_PAGES)


# ============================================================
# SLIDE 8  真实案例时间轴
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s, BG_WHITE)
add_section_header(s, "05", "CASE — 真实挽回案例时间轴",
                   "一个 6 天的故事：AI 预警 × 组长介入 × 200 万续保逆转",
                   "⚠ 下方案例为原销售场景示意，银卡客服组长场景需替换为真实脱敏数据")

# 案例 Header 卡
hy = Inches(2.25)
hh = Inches(0.75)
add_rect(s, Inches(0.7), hy, Inches(11.9), hh,
         fill=BG_SOFT, line_color=ORANGE, line_width=0.75)

add_rich_text(s, Inches(1.0), hy + Inches(0.1), Inches(8), Inches(0.35),
              runs=[
                  ("CASE · ", {"color": ORANGE, "size": 13, "bold": True, "font": FONT_MONO}),
                  ("李女士续保危机", {"color": TEXT_DARK, "size": 15, "bold": True}),
              ])
add_text(s, Inches(1.0), hy + Inches(0.42), Inches(8), Inches(0.3),
         "45 岁 · 高净值客户 · 重疾险即将到期 · 家庭 200 万保额",
         size=10, color=TEXT_MID)

res_bg = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                            Inches(9.4), hy + Inches(0.15),
                            Inches(3.1), Inches(0.5))
res_bg.adjustments[0] = 0.2
res_bg.fill.solid(); res_bg.fill.fore_color.rgb = ORANGE
res_bg.line.fill.background(); res_bg.shadow.inherit = False
add_rich_text(s, Inches(9.4), hy + Inches(0.15), Inches(3.1), Inches(0.5),
              runs=[
                  ("挽回结果：续保+加保 340 万", {"color": BG_WHITE, "size": 11, "bold": True}),
              ], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

timeline = [
    ("T-3 天", "PAONE · 行为监测", ORANGE_LIGHT,
     "监测到李女士 3 次登录官网保单页、停留 8 分 47 秒，但未发起操作。同时竞品官网 cookie 出现在同设备。"),
    ("T-2 天", "PAONE · 规则引擎", ORANGE_LIGHT,
     "自动打标「流失高风险 · 紧急」，并推单至组长工作台（而非坐席）。系统备注：\"建议管理层亲自介入\"。"),
    ("T-1 天", "组长 · 情报准备", ORANGE_LIGHT,
     "调阅客户画像，发现关键线索：3 个月前咨询过理赔但未闭环。判断真实顾虑是对理赔体验的不信任。"),
    ("T 0", "组长 · 亲自致电", ORANGE,
     "15 分钟通话，全程不提续费。只谈三件事：①回溯理赔咨询 ②解释流程卡点并道歉 ③承诺专属服务对接。"),
    ("T+2 天", "客户 · 主动回访", GREEN,
     "李女士主动来电询问续保升级方案，并提出为丈夫加保。最终签单续保 200 万 + 加保 140 万 = 340 万。"),
    ("T+7 天", "组长 · AI 喂养闭环", GREEN,
     "案例打标「高净值 · 理赔体验型流失」喂给 PAone。同类客户将被自动识别并优先推单。"),
]

tly = Inches(3.15)
row_height = 0.55

# 竖线
vline = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                           Inches(1.65), tly + Inches(0.15),
                           Emu(19050), Inches(3.35))
vline.fill.solid(); vline.fill.fore_color.rgb = ORANGE
vline.line.fill.background(); vline.shadow.inherit = False

for i, (t, actor, color, desc) in enumerate(timeline):
    ry = tly + Inches(i * row_height)
    add_text(s, Inches(0.7), ry + Inches(0.12), Inches(0.85), Inches(0.3),
             t, size=11, color=color, bold=True, font=FONT_MONO,
             align=PP_ALIGN.RIGHT)
    # 圆点
    dot = s.shapes.add_shape(MSO_SHAPE.OVAL,
                             Inches(1.58), ry + Inches(0.17),
                             Inches(0.2), Inches(0.2))
    dot.fill.solid(); dot.fill.fore_color.rgb = color
    dot.line.color.rgb = BG_WHITE; dot.line.width = Pt(2)
    dot.shadow.inherit = False

    cx = Inches(1.95)
    cw = Inches(10.7)
    ch = Inches(0.48)
    card_color = BG_SOFT if color == ORANGE else BG_LIGHT
    add_rect(s, cx, ry + Inches(0.05), cw, ch,
             fill=card_color, line_color=BORDER)
    add_text(s, cx + Inches(0.2), ry + Inches(0.08), Inches(2.5), Inches(0.2),
             actor, size=8, color=color, bold=True, font=FONT_MONO)
    add_text(s, cx + Inches(0.2), ry + Inches(0.24), cw - Inches(0.3), Inches(0.3),
             desc, size=9.5, color=TEXT)

# 底部对比
contrast_y = Inches(6.6)
contrast_h = Inches(0.5)
add_rect(s, Inches(0.7), contrast_y, Inches(5.85), contrast_h,
         fill=RGBColor(0xFC, 0xE8, 0xE9), line_color=None, corner_adj=0.15)
lb = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                        Inches(0.7), contrast_y, Emu(28575), contrast_h)
lb.fill.solid(); lb.fill.fore_color.rgb = RED
lb.line.fill.background(); lb.shadow.inherit = False
add_rich_text(s, Inches(0.9), contrast_y + Inches(0.08),
              Inches(5.6), contrast_h - Inches(0.1),
              runs=[
                  ("❌ 旧模式：", {"color": RED, "size": 10, "bold": True}),
                  ("客户出现在夕会流失名单时已签他司，根因永远无法触达。", {"color": TEXT, "size": 10}),
              ], line_spacing=1.3)

add_rect(s, Inches(6.75), contrast_y, Inches(5.85), contrast_h,
         fill=BG_SOFT, line_color=None, corner_adj=0.15)
lb2 = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                         Inches(6.75), contrast_y, Emu(28575), contrast_h)
lb2.fill.solid(); lb2.fill.fore_color.rgb = ORANGE
lb2.line.fill.background(); lb2.shadow.inherit = False
add_rich_text(s, Inches(6.95), contrast_y + Inches(0.08),
              Inches(5.6), contrast_h - Inches(0.1),
              runs=[
                  ("✓ 数智指挥官：", {"color": ORANGE_DARK, "size": 10, "bold": True}),
                  ("AI 提前 3 天预警 → 组长共情挽回 → 案例反向训练 AI。", {"color": TEXT, "size": 10}),
              ], line_spacing=1.3)

add_footer(s, 8, TOTAL_PAGES)


# ============================================================
# SLIDE 9  HOW 落地路径
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s, BG_WHITE)
add_section_header(s, "06", "HOW — 落地路径",
                   "三阶段 90 天，从工具接入到能力升级",
                   "蓝图再美也要脚手架。三阶段路径让数智化转型从愿景变为可排期、可验收、可复盘的行动。")

rmy = Inches(2.4)
rmh = Inches(4.5)
add_rect(s, Inches(0.7), rmy, Inches(11.9), rmh,
         fill=BG_LIGHT, line_color=BORDER)

# 连线
line_y = rmy + Inches(0.7)
line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                          Inches(2.1), line_y,
                          Inches(9.1), Emu(19050))
line.fill.solid(); line.fill.fore_color.rgb = ORANGE_LIGHT
line.line.fill.background(); line.shadow.inherit = False

stages = [
    ("01", ORANGE_LIGHT, "工具接入", "WEEK 1 — 2",
     ["PAone 账号与权限开通，接入团队数据源",
      "规则引擎配置：异常推单阈值 / 通报口径",
      "组长完成工具基础培训与首次诊断"]),
    ("02", ORANGE, "流程重塑", "WEEK 3 — 8",
     ["废除人肉巡视、手工取数等旧 SOP",
      "建立 AI 初筛 + 组长精辅导 的 1V1 新机制",
      "夕会改造：从汇报型转向数据驱动决策型"]),
    ("03", ORANGE_DARK, "能力升级", "WEEK 9 — 12",
     ["组长完成三种新角色能力认证",
      "建立 AI 语料喂养日常机制",
      "输出首份《团队数智化复盘报告》"]),
]

stage_w = Inches(3.9)
for i, (num, color, title, period, items) in enumerate(stages):
    sx = Inches(0.9 + i * 4.05)
    sy = rmy + Inches(0.35)

    # 大圆
    circle = s.shapes.add_shape(MSO_SHAPE.OVAL,
                                sx + Inches(1.6), sy,
                                Inches(0.7), Inches(0.7))
    circle.fill.solid(); circle.fill.fore_color.rgb = color
    circle.line.color.rgb = BG_WHITE; circle.line.width = Pt(3)
    circle.shadow.inherit = False
    add_text(s, sx + Inches(1.6), sy, Inches(0.7), Inches(0.7),
             num, size=16, color=BG_WHITE, bold=True, font=FONT_MONO,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    add_text(s, sx, sy + Inches(0.85), stage_w, Inches(0.4),
             title, size=17, color=TEXT_DARK, bold=True, align=PP_ALIGN.CENTER)
    add_text(s, sx, sy + Inches(1.25), stage_w, Inches(0.3),
             period, size=10, color=ORANGE, font=FONT_MONO, align=PP_ALIGN.CENTER, bold=True)

    list_bg = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                 sx + Inches(0.15), sy + Inches(1.7),
                                 stage_w - Inches(0.3), Inches(2.0))
    list_bg.adjustments[0] = 0.08
    list_bg.fill.solid(); list_bg.fill.fore_color.rgb = BG_CARD
    list_bg.line.color.rgb = BORDER; list_bg.line.width = Pt(0.5)
    list_bg.shadow.inherit = False

    ly = sy + Inches(1.85)
    for item in items:
        add_rich_text(s, sx + Inches(0.35), ly,
                      stage_w - Inches(0.6), Inches(0.6),
                      runs=[("✓ ", {"color": ORANGE, "size": 11, "bold": True}),
                            (item, {"color": TEXT, "size": 10.5})],
                      line_spacing=1.4)
        ly += Inches(0.55)

add_footer(s, 9, TOTAL_PAGES)


# ============================================================
# SLIDE 10  RESULT + 对标
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s, BG_WHITE)
add_section_header(s, "07", "RESULT — 预期业绩 + 行业对标",
                   "不止是\"改善\"，而是站在行业前列",
                   "四个验收 KPI 配套行业基准，让每一个数字都经得起追问。")

kpis = [
    ("🎯", "高价值时间占比", "53", "%", "从 28% 提升至 53%，带宽翻倍"),
    ("💎", "高风险客户挽回率", "+25", "%", "组长介入 + AI 预警前置"),
    ("📚", "销冠话术复用率", "+40", "%", "月度话术萃取入训练库"),
    ("⏱", "异常响应时效", "T+0", "", "从 T+1 转为实时推单"),
]
ky = Inches(2.35)
kw = Inches(2.9)
kh = Inches(1.75)
for i, (icon, label, val, unit, desc) in enumerate(kpis):
    x = Inches(0.7 + i * 3.0)
    add_rect(s, x, ky, kw, kh, fill=BG_CARD, line_color=BORDER)
    top = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, ky, kw, Inches(0.05))
    top.fill.solid(); top.fill.fore_color.rgb = ORANGE
    top.line.fill.background(); top.shadow.inherit = False
    add_text(s, x, ky + Inches(0.2), kw, Inches(0.4),
             icon, size=18, color=ORANGE, align=PP_ALIGN.CENTER)
    add_text(s, x, ky + Inches(0.55), kw, Inches(0.3),
             label, size=11, color=TEXT_DARK, bold=True, align=PP_ALIGN.CENTER)
    add_rich_text(s, x, ky + Inches(0.85), kw, Inches(0.6),
                  runs=[(val, {"color": ORANGE, "size": 32, "bold": True}),
                        (unit, {"color": ORANGE_LIGHT, "size": 14})],
                  align=PP_ALIGN.CENTER)
    add_text(s, x + Inches(0.2), ky + Inches(1.42), kw - Inches(0.4), Inches(0.28),
             desc, size=9, color=TEXT_MID, align=PP_ALIGN.CENTER)

# 对标卡
by = Inches(4.35)
bh = Inches(2.75)
add_rect(s, Inches(0.7), by, Inches(11.9), bh,
         fill=BG_LIGHT, line_color=BORDER)

add_text(s, Inches(0.95), by + Inches(0.2), Inches(11), Inches(0.3),
         "📊 横向对标：我们相对行业的位置",
         size=13, color=TEXT_DARK, bold=True)
add_text(s, Inches(0.95), by + Inches(0.5), Inches(11), Inches(0.25),
         "数据来源：金融保险业服销运营基准报告 · 行业平均为呼入/服销混合型团队中位数",
         size=9, color=TEXT_MID)

benchmarks = [
    ("高价值时间占比", "超出行业中位数 2.4 倍",
     [("行业底部 25%", 15, BORDER_DARK, False),
      ("行业中位数", 22, ORANGE_LIGHT, False),
      ("PAone 模式", 53, ORANGE_DARK, True)]),
    ("销冠话术复用率", "领先行业均值 3.3 倍",
     [("行业底部 25%", 5, BORDER_DARK, False),
      ("行业中位数", 12, ORANGE_LIGHT, False),
      ("PAone 模式", 40, ORANGE_DARK, True)]),
]

bm_y = by + Inches(0.85)
bar_max_w = Inches(6.5)
for b_i, (title, caption, tracks) in enumerate(benchmarks):
    rowy = bm_y + Inches(b_i * 0.92)
    add_text(s, Inches(0.95), rowy, Inches(8), Inches(0.3),
             title, size=11, color=TEXT_DARK, bold=True)
    add_text(s, Inches(0.95), rowy, Inches(11.4), Inches(0.3),
             caption, size=10, color=ORANGE, align=PP_ALIGN.RIGHT, bold=True)

    for t_i, (name, val, color, is_us) in enumerate(tracks):
        ry = rowy + Inches(0.3 + t_i * 0.17)
        add_text(s, Inches(0.95), ry, Inches(1.8), Inches(0.18),
                 name, size=8.5, color=ORANGE_DARK if is_us else TEXT_MID,
                 bold=is_us, align=PP_ALIGN.RIGHT)
        bg_bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                    Inches(2.85), ry + Inches(0.03),
                                    bar_max_w, Inches(0.15))
        bg_bar.fill.solid(); bg_bar.fill.fore_color.rgb = BG_CARD
        bg_bar.line.color.rgb = BORDER; bg_bar.line.width = Pt(0.5)
        bg_bar.shadow.inherit = False
        fill_w = Emu(int(bar_max_w * val / 60))
        fbar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                  Inches(2.85), ry + Inches(0.03),
                                  fill_w, Inches(0.15))
        fbar.fill.solid(); fbar.fill.fore_color.rgb = color
        fbar.line.fill.background(); fbar.shadow.inherit = False
        add_text(s, Inches(9.5), ry, Inches(0.9), Inches(0.18),
                 f"{val}%", size=9, color=ORANGE_DARK if is_us else TEXT,
                 bold=True, font=FONT_MONO, align=PP_ALIGN.RIGHT)

add_footer(s, 10, TOTAL_PAGES)


# ============================================================
# SLIDE 11  ROI
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s, BG_WHITE)
add_section_header(s, "08", "ROI — 投入产出账本",
                   "6 个月回本，远快于行业 18 个月均值",
                   "标准中等规模团队（20 坐席 + 1 组长）的 12 个月 ROI 测算。数字为示意，需用真实数据替换。")

left_x = Inches(0.7)
left_w = Inches(5.5)
right_x = Inches(6.4)
right_w = Inches(6.2)
content_y = Inches(2.4)
content_h = Inches(4.55)

# 左栏：平安橙大块
add_rect(s, left_x, content_y, left_w, content_h,
         fill=ORANGE, line_color=None)

add_text(s, left_x + Inches(0.4), content_y + Inches(0.5),
         left_w - Inches(0.8), Inches(0.4),
         "12 个月净收益",
         size=11, color=BG_WHITE, bold=True, font=FONT_MONO)

add_rich_text(s, left_x + Inches(0.4), content_y + Inches(1.0),
              left_w - Inches(0.8), Inches(1.5),
              runs=[("+", {"color": BG_WHITE, "size": 56, "bold": True}),
                    ("312", {"color": BG_WHITE, "size": 80, "bold": True}),
                    (" 万", {"color": BG_WHITE, "size": 32, "bold": True})])

# 白色分割线
sep = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                         left_x + Inches(0.4), content_y + Inches(2.7),
                         Inches(0.6), Emu(19050))
sep.fill.solid(); sep.fill.fore_color.rgb = BG_WHITE
sep.line.fill.background(); sep.shadow.inherit = False

add_rich_text(s, left_x + Inches(0.4), content_y + Inches(2.95),
              left_w - Inches(0.8), Inches(1.5),
              runs=[
                  ("对比传统数智化项目 ", {"color": BG_WHITE, "size": 12}),
                  ("18 个月回本周期", {"color": BG_WHITE, "size": 12, "bold": True}),
                  ("，PAone 模式凭借低部署成本与即时业绩放大效应，", {"color": BG_WHITE, "size": 12}),
                  ("6 个月即可回本", {"color": BG_WHITE, "size": 14, "bold": True}),
                  ("。", {"color": BG_WHITE, "size": 12}),
              ], line_spacing=1.65)

# 右栏
add_rect(s, right_x, content_y, right_w, content_h,
         fill=BG_WHITE, line_color=BORDER)

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
    row_h = Inches(0.52) if not total else Inches(0.68)
    row_bg = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                right_x + Inches(0.25), irow_y,
                                right_w - Inches(0.5), row_h)
    row_bg.adjustments[0] = 0.15
    row_bg.fill.solid()
    if total:
        row_bg.fill.fore_color.rgb = BG_SOFT
        row_bg.line.color.rgb = ORANGE
        row_bg.line.width = Pt(1)
    else:
        row_bg.fill.fore_color.rgb = BG_LIGHT
        row_bg.line.fill.background()
    row_bg.shadow.inherit = False

    add_text(s, right_x + Inches(0.5), irow_y,
             right_w - Inches(2.5), row_h,
             label,
             size=12 if total else 11,
             color=TEXT_DARK if total else TEXT,
             bold=total,
             anchor=MSO_ANCHOR.MIDDLE)

    val_color = ORANGE_DARK if (positive and total) else \
                ORANGE if positive else TEXT_MID
    val_size = 16 if total else 13
    add_text(s, right_x + Inches(0.25), irow_y,
             right_w - Inches(0.65), row_h,
             value, size=val_size, color=val_color,
             bold=True, font=FONT_MONO,
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

    irow_y += row_h + Inches(0.04)

add_footer(s, 11, TOTAL_PAGES)


# ============================================================
# SLIDE 12  金句结尾
# ============================================================
s = prs.slides.add_slide(blank)
add_bg(s, BG_WHITE)

# 顶部橙色装饰带
top_strip = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Inches(0.12))
top_strip.fill.solid(); top_strip.fill.fore_color.rgb = ORANGE
top_strip.line.fill.background(); top_strip.shadow.inherit = False

bot_strip = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, SLIDE_H - Inches(0.12), SLIDE_W, Inches(0.12))
bot_strip.fill.solid(); bot_strip.fill.fore_color.rgb = ORANGE
bot_strip.line.fill.background(); bot_strip.shadow.inherit = False

# 大引号
add_text(s, Inches(0.5), Inches(1.2), Inches(12.3), Inches(1.2),
         '"', size=120, color=ORANGE, bold=True, align=PP_ALIGN.CENTER)

# 金句
add_rich_text(s, Inches(1), Inches(2.8), Inches(11.3), Inches(2.5),
              runs=[
                  ("引入 PAone 之后，现管岗位不仅是减负，", {"color": TEXT_DARK, "size": 24}),
                  ("\n", {}),
                  ("更是 ", {"color": TEXT_DARK, "size": 24}),
                  ("从\"管事\"向\"理人\"的质变", {"color": ORANGE, "size": 26, "bold": True}),
                  ("。", {"color": TEXT_DARK, "size": 24}),
                  ("\n", {}),
                  ("\n", {}),
                  ("组长不再是\"管 10 个人的监工\"，", {"color": TEXT, "size": 20}),
                  ("\n", {}),
                  ("而是 ", {"color": TEXT, "size": 20}),
                  ("指挥 10 人 + 1 个 AI 军团", {"color": ORANGE_DARK, "size": 22, "bold": True}),
                  (" 的 ", {"color": TEXT, "size": 20}),
                  ("微型业务总经理", {"color": ORANGE, "size": 22, "bold": True}),
                  ("。", {"color": TEXT, "size": 20}),
              ], align=PP_ALIGN.CENTER, line_spacing=1.7)

# 装饰线
l1 = s.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                        Inches(5.5), Inches(6.3),
                        Inches(2.3), Emu(19050))
l1.fill.solid(); l1.fill.fore_color.rgb = ORANGE
l1.line.fill.background(); l1.shadow.inherit = False

add_text(s, Inches(0.5), Inches(6.5), Inches(12.3), Inches(0.4),
         "— THE NEW PARADIGM OF SALES-SERVICE MANAGEMENT —",
         size=11, color=TEXT_MID, font=FONT_MONO, align=PP_ALIGN.CENTER)
add_text(s, Inches(0.5), Inches(6.85), Inches(12.3), Inches(0.4),
         "END / THANK YOU",
         size=11, color=ORANGE, font=FONT_MONO, align=PP_ALIGN.CENTER, bold=True)


# ============================================================
# 保存
# ============================================================
output = "report-v3-pingan.pptx"
prs.save(output)
print(f"✓ 生成完成：{output}")
print(f"  共 {len(prs.slides)} 页")
