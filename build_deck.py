"""
Build a single-page 8:9 portrait PPTX:
"PAone 数智指挥舱 - 现管岗位 1+N 系统架构图"
Tech-style: deep navy background, neon blue lines, orange highlights.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree
import math

# ---------- palette ----------
NAVY_DEEP   = RGBColor(0x05, 0x0A, 0x1F)  # background base
NAVY_MID    = RGBColor(0x0B, 0x16, 0x36)  # background top
NAVY_PANEL  = RGBColor(0x10, 0x1C, 0x3D)  # panel fills
TECH_BLUE   = RGBColor(0x33, 0xC8, 0xFF)  # neon outline
TECH_BLUE_2 = RGBColor(0x4E, 0xA8, 0xFF)
TECH_CYAN   = RGBColor(0x66, 0xF0, 0xFF)
ORANGE      = RGBColor(0xFF, 0x9D, 0x3D)  # highlight
ORANGE_HOT  = RGBColor(0xFF, 0x6A, 0x1A)
GREY_DIM    = RGBColor(0x55, 0x60, 0x7A)
GREY_TXT    = RGBColor(0xA9, 0xB4, 0xCC)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
SOFT_WHITE  = RGBColor(0xE6, 0xEE, 0xFA)

# ---------- slide ----------
prs = Presentation()
# 8:9 portrait. Use 8 x 9 inches.
prs.slide_width  = Inches(8)
prs.slide_height = Inches(9)
SW, SH = prs.slide_width, prs.slide_height

blank = prs.slide_layouts[6]
slide = prs.slides.add_slide(blank)

# ---------- helpers ----------
def add_rect(left, top, width, height, fill=None, line=None, line_w=None,
             shape=MSO_SHAPE.RECTANGLE, shadow=False):
    s = slide.shapes.add_shape(shape, left, top, width, height)
    s.shadow.inherit = False
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        if line_w is not None:
            s.line.width = line_w
    return s

def add_text(left, top, width, height, text, *,
             size=10, bold=False, color=WHITE, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, font="Microsoft YaHei"):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    lines = text.split("\n") if isinstance(text, str) else text
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        run = p.add_run()
        run.text = ln
        run.font.name = font
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
    return tb

def add_line(x1, y1, x2, y2, color=TECH_BLUE, weight=0.75):
    line = slide.shapes.add_connector(1, x1, y1, x2, y2)
    line.line.color.rgb = color
    line.line.width = Pt(weight)
    return line

# ---------- 1. background ----------
bg = add_rect(0, 0, SW, SH, fill=NAVY_DEEP)

# subtle top band slightly lighter
add_rect(0, 0, SW, Inches(2.7), fill=NAVY_MID)

# decorative thin grid lines
for i in range(1, 16):
    y = Inches(9 * i / 16)
    add_line(0, y, SW, y, color=RGBColor(0x12, 0x22, 0x44), weight=0.5)
for i in range(1, 12):
    x = Inches(8 * i / 12)
    add_line(x, 0, x, SH, color=RGBColor(0x12, 0x22, 0x44), weight=0.5)

# corner tech brackets
def tech_bracket(x, y, size, color=TECH_BLUE, flip_x=False, flip_y=False):
    s = size
    sx = -1 if flip_x else 1
    sy = -1 if flip_y else 1
    add_line(x, y, x + sx * s, y, color=color, weight=1.5)
    add_line(x, y, x, y + sy * s, color=color, weight=1.5)

tech_bracket(Inches(0.18), Inches(0.18), Inches(0.35))
tech_bracket(Inches(7.82), Inches(0.18), Inches(0.35), flip_x=True)
tech_bracket(Inches(0.18), Inches(8.82), Inches(0.35), flip_y=True)
tech_bracket(Inches(7.82), Inches(8.82), Inches(0.35), flip_x=True, flip_y=True)

# top tag
add_rect(Inches(0.4), Inches(0.32), Inches(1.55), Inches(0.28),
         fill=None, line=TECH_BLUE, line_w=Pt(0.75))
add_text(Inches(0.4), Inches(0.32), Inches(1.55), Inches(0.28),
         "科技创新 · 4 / 4", size=9, color=TECH_CYAN,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, bold=True)

# top right meta
add_text(Inches(5.6), Inches(0.32), Inches(2.2), Inches(0.28),
         "PAone × 银卡服销 · 现管 1+N", size=9, color=GREY_TXT,
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

# ---------- 2. title block ----------
add_text(Inches(0.4), Inches(0.7), Inches(7.2), Inches(0.55),
         "银卡服销现管岗位 1+N", size=24, bold=True, color=WHITE,
         align=PP_ALIGN.LEFT)
add_text(Inches(0.4), Inches(1.2), Inches(7.2), Inches(0.5),
         "构建人机协同 · 数智指挥舱", size=18, bold=True, color=ORANGE,
         align=PP_ALIGN.LEFT)

# divider
add_line(Inches(0.4), Inches(1.78), Inches(7.6), Inches(1.78),
         color=TECH_BLUE, weight=1.2)
# small dot on divider
dot = add_rect(Inches(0.34), Inches(1.72), Inches(0.12), Inches(0.12),
               fill=ORANGE, shape=MSO_SHAPE.OVAL)

add_text(Inches(0.4), Inches(1.85), Inches(7.2), Inches(0.5),
         "PAone 接管数据巡场 · 异常预警 · 话术萃取 · 复盘生成    |    "
         "组长聚焦高价值干预与团队能力复制",
         size=9.5, color=GREY_TXT, align=PP_ALIGN.LEFT)

# ---------- 3. legacy strip (compressed gray panel) ----------
LY = Inches(2.35)
LH = Inches(0.78)
add_rect(Inches(0.4), LY, Inches(7.2), LH,
         fill=RGBColor(0x18, 0x20, 0x36),
         line=GREY_DIM, line_w=Pt(0.5))
# left label tag
add_rect(Inches(0.4), LY, Inches(1.55), LH,
         fill=RGBColor(0x22, 0x2C, 0x44))
add_text(Inches(0.4), LY, Inches(1.55), LH,
         "传统现管\n人肉盯盘模式", size=10, bold=True, color=SOFT_WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# four short tags
tags = ["手工查数", "事后复盘", "泛化辅导", "现场催办"]
tag_x0 = 2.05
tag_w = 0.95
for i, t in enumerate(tags):
    x = Inches(tag_x0 + i * (tag_w + 0.1))
    add_rect(x, LY + Inches(0.1), Inches(tag_w), Inches(0.35),
             fill=None, line=GREY_DIM, line_w=Pt(0.6),
             shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    add_text(x, LY + Inches(0.1), Inches(tag_w), Inches(0.35),
             t, size=9, color=GREY_TXT, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# tagline
add_text(Inches(2.05), LY + Inches(0.46), Inches(5.5), Inches(0.3),
         "忙在动作上   ·   慢在判断上   ·   弱在复制上",
         size=9, color=ORANGE, bold=True, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.MIDDLE)

# downward arrow connector to cockpit
add_line(Inches(4.0), LY + LH, Inches(4.0), LY + LH + Inches(0.2),
         color=TECH_BLUE, weight=1.2)
# arrow tip
arrow = slide.shapes.add_shape(MSO_SHAPE.DOWN_ARROW,
        Inches(3.92), LY + LH + Inches(0.18), Inches(0.16), Inches(0.18))
arrow.fill.solid(); arrow.fill.fore_color.rgb = TECH_BLUE
arrow.line.fill.background()

# ---------- 4. center cockpit (PAone glowing core) ----------
CY = Inches(3.55)
CH = Inches(1.55)
core_cx = Inches(4.0)
core_cy = CY + Inches(0.78)

# outer glow rings (3 concentric circles, decreasing opacity via lighter color)
def add_ring(cx, cy, r, color, weight=1.0, dash=False):
    left = cx - r
    top = cy - r
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, r * 2, r * 2)
    s.fill.background()
    s.line.color.rgb = color
    s.line.width = Pt(weight)
    if dash:
        ln = s.line._get_or_add_ln()
        prstDash = etree.SubElement(ln, qn('a:prstDash'))
        prstDash.set('val', 'dash')
    return s

add_ring(core_cx, core_cy, Inches(1.35), RGBColor(0x14, 0x33, 0x66), weight=1.0)
add_ring(core_cx, core_cy, Inches(1.10), RGBColor(0x1C, 0x55, 0x99), weight=1.0, dash=True)
add_ring(core_cx, core_cy, Inches(0.88), TECH_BLUE_2, weight=1.5)

# core disc
core_r = Inches(0.72)
core = slide.shapes.add_shape(MSO_SHAPE.OVAL,
    core_cx - core_r, core_cy - core_r, core_r * 2, core_r * 2)
core.fill.solid()
core.fill.fore_color.rgb = RGBColor(0x0F, 0x2B, 0x55)
core.line.color.rgb = TECH_CYAN
core.line.width = Pt(2.0)

# core text
add_text(core_cx - Inches(1.0), core_cy - Inches(0.42),
         Inches(2.0), Inches(0.34),
         "PAone", size=18, bold=True, color=WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(core_cx - Inches(1.0), core_cy - Inches(0.08),
         Inches(2.0), Inches(0.26),
         "服销现管 · 数智指挥舱", size=9.5, bold=True, color=TECH_CYAN,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
add_text(core_cx - Inches(1.0), core_cy + Inches(0.18),
         Inches(2.0), Inches(0.24),
         "1 名组长  +  N 个 AI 能力单元", size=8, color=SOFT_WHITE,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# orbital dots
import random
random.seed(7)
for ang_deg in [25, 95, 155, 215, 275, 335]:
    a = math.radians(ang_deg)
    r = Inches(1.10)
    cx_pt = core_cx + Emu(int(r * math.cos(a)))
    cy_pt = core_cy + Emu(int(r * math.sin(a)))
    d = Inches(0.09)
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL,
        cx_pt - d/2, cy_pt - d/2, d, d)
    dot.fill.solid(); dot.fill.fore_color.rgb = ORANGE
    dot.line.fill.background()

# left side label "传统模式"
add_text(Inches(0.4), CY + Inches(0.55), Inches(1.2), Inches(0.3),
         "← 旧模式", size=8.5, color=GREY_TXT, bold=True,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)

# right side label "AI能力矩阵"
add_text(Inches(6.4), CY + Inches(0.55), Inches(1.2), Inches(0.3),
         "AI 能力矩阵 →", size=8.5, color=TECH_CYAN, bold=True,
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

# side flanking thin panels: left "查/催/盯/复"
add_rect(Inches(0.4), CY + Inches(0.05), Inches(1.55), Inches(1.45),
         fill=RGBColor(0x12, 0x1A, 0x30),
         line=GREY_DIM, line_w=Pt(0.5),
         shape=MSO_SHAPE.ROUNDED_RECTANGLE)
add_text(Inches(0.4), CY + Inches(0.1), Inches(1.55), Inches(0.3),
         "组长动作（旧）", size=9, bold=True, color=GREY_TXT,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
old_actions = ["查数", "催办", "救火", "盯进度"]
for i, a in enumerate(old_actions):
    add_text(Inches(0.45), CY + Inches(0.42 + i * 0.24),
             Inches(1.45), Inches(0.22),
             "·  " + a, size=9, color=SOFT_WHITE,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)

# right flanking panel: "组长动作（新）"
add_rect(Inches(6.05), CY + Inches(0.05), Inches(1.55), Inches(1.45),
         fill=RGBColor(0x10, 0x24, 0x4A),
         line=TECH_BLUE_2, line_w=Pt(0.75),
         shape=MSO_SHAPE.ROUNDED_RECTANGLE)
add_text(Inches(6.05), CY + Inches(0.1), Inches(1.55), Inches(0.3),
         "组长动作（新）", size=9, bold=True, color=TECH_CYAN,
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
new_actions = ["识别", "干预", "辅导", "复制 · 训练AI"]
for i, a in enumerate(new_actions):
    add_text(Inches(6.10), CY + Inches(0.42 + i * 0.24),
             Inches(1.45), Inches(0.22),
             "▸  " + a, size=9, color=WHITE,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)

# connecting lines from cockpit core to flank panels
add_line(core_cx - Inches(0.72), core_cy,
         Inches(1.95), CY + Inches(0.78),
         color=GREY_DIM, weight=0.9)
add_line(core_cx + Inches(0.72), core_cy,
         Inches(6.05), CY + Inches(0.78),
         color=TECH_BLUE, weight=1.1)

# ---------- 5. AI 能力矩阵 (6 cards 3x2) ----------
GY0 = Inches(5.25)
card_w = Inches(2.32)
card_h = Inches(1.05)
gap_x = Inches(0.12)
gap_y = Inches(0.10)
margin_x = Inches(0.4)

cards = [
    ("01", "数据巡场引擎", "自动抓取大盘 / 员工 / 时段 / 名单 / 成交"),
    ("02", "异常预警引擎", "低产 · 掉速 · 名单浪费 · 通时不足 · 情绪波动"),
    ("03", "话术萃取引擎", "拆解销冠录音与成交结构，沉淀可复制模板"),
    ("04", "精准辅导引擎", "按个人短板推送辅导重点，辅导从经验变数据"),
    ("05", "复盘生成引擎", "自动生成早会 / 夕会 / 通报 / 跟进清单"),
    ("06", "语料进化引擎", "组长标注案例反向训练，PAone 越用越懂业务"),
]
for idx, (num, name, desc) in enumerate(cards):
    col = idx % 3
    row = idx // 3
    x = margin_x + col * (card_w + gap_x)
    y = GY0 + row * (card_h + gap_y)

    # card body
    add_rect(x, y, card_w, card_h,
             fill=RGBColor(0x0E, 0x1C, 0x3E),
             line=TECH_BLUE_2, line_w=Pt(0.75),
             shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    # left accent bar
    add_rect(x, y, Inches(0.07), card_h,
             fill=ORANGE if idx in (1, 5) else TECH_BLUE)
    # number badge
    add_text(x + Inches(0.18), y + Inches(0.08),
             Inches(0.5), Inches(0.28),
             num, size=12, bold=True, color=ORANGE,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
    # tiny chip dot
    chip = slide.shapes.add_shape(MSO_SHAPE.OVAL,
        x + card_w - Inches(0.22), y + Inches(0.13),
        Inches(0.08), Inches(0.08))
    chip.fill.solid(); chip.fill.fore_color.rgb = TECH_CYAN
    chip.line.fill.background()
    # name
    add_text(x + Inches(0.55), y + Inches(0.08),
             card_w - Inches(0.7), Inches(0.32),
             name, size=11.5, bold=True, color=WHITE,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
    # desc
    add_text(x + Inches(0.18), y + Inches(0.42),
             card_w - Inches(0.3), Inches(0.55),
             desc, size=8.5, color=GREY_TXT,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP)

# ---------- 6. 数据闭环链路 ----------
PY = Inches(7.55)
add_text(Inches(0.4), PY - Inches(0.05), Inches(7.2), Inches(0.28),
         "数据闭环  /  CLOSED-LOOP PIPELINE",
         size=8.5, bold=True, color=TECH_CYAN, align=PP_ALIGN.LEFT)

flow = ["数据采集", "AI识别", "组长干预", "话术沉淀", "团队复制", "模型进化"]
fy = PY + Inches(0.30)
fh = Inches(0.42)
total_w = Inches(7.2)
n = len(flow)
chev_w = (total_w - Inches(0.12) * (n - 1)) / n
for i, label in enumerate(flow):
    x = Inches(0.4) + i * (chev_w + Inches(0.12))
    s = slide.shapes.add_shape(MSO_SHAPE.PENTAGON, x, fy, chev_w, fh)
    s.fill.solid()
    if i == n - 1:
        s.fill.fore_color.rgb = ORANGE_HOT
    elif i == 0:
        s.fill.fore_color.rgb = RGBColor(0x12, 0x32, 0x60)
    else:
        # gradient feel via index
        shade = 0x12 + i * 8
        s.fill.fore_color.rgb = RGBColor(shade, 0x32 + i * 6, 0x60 + i * 10)
    s.line.color.rgb = TECH_BLUE
    s.line.width = Pt(0.6)
    tf = s.text_frame
    tf.margin_left = Emu(0); tf.margin_right = Emu(0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label
    r.font.name = "Microsoft YaHei"
    r.font.size = Pt(9.5); r.font.bold = True
    r.font.color.rgb = WHITE

# ---------- 7. bottom highlight banner ----------
BY = Inches(8.20)
add_rect(Inches(0.4), BY, Inches(7.2), Inches(0.62),
         fill=RGBColor(0x0C, 0x1A, 0x36),
         line=ORANGE, line_w=Pt(1.0),
         shape=MSO_SHAPE.ROUNDED_RECTANGLE)
# left orange block
add_rect(Inches(0.4), BY, Inches(0.18), Inches(0.62), fill=ORANGE)

add_text(Inches(0.7), BY + Inches(0.02), Inches(6.8), Inches(0.30),
         "现管 1+N，不是减负工具，而是现场管理操作系统。",
         size=13, bold=True, color=WHITE,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)
add_text(Inches(0.7), BY + Inches(0.32), Inches(6.8), Inches(0.28),
         "PAone 实时感知   ·   组长精准干预   ·   团队能力复制   ·   "
         "AI 持续进化",
         size=9, color=TECH_CYAN, bold=True,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)

# bottom-right footer micro
add_text(Inches(5.4), Inches(8.85), Inches(2.2), Inches(0.15),
         "© PAone Smart Ops · v2026", size=7, color=GREY_DIM,
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

# ---------- save ----------
out = "/projects/sandbox/kiro2026/PAone_现管1+N_数智指挥舱.pptx"
prs.save(out)
print("Saved:", out)
