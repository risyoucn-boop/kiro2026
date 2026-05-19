"""
McKinsey-style single-page exhibit, 8:9 portrait.
Topic: PAone 数智指挥舱重构现管岗位（1+N）
Design language: white space, restrained palette (navy + grey + 1 red accent),
hairline rules, action title, standfirst, from-to matrix, hub-spoke diagram,
closed-loop bar, key-takeaway box, source footnote.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# ---------- McKinsey palette ----------
NAVY       = RGBColor(0x00, 0x3A, 0x70)   # primary
NAVY_DARK  = RGBColor(0x00, 0x29, 0x55)
BLUE_MID   = RGBColor(0x2E, 0x6F, 0xB5)
BLUE_PALE  = RGBColor(0xE6, 0xEE, 0xF7)
GREY_TXT   = RGBColor(0x4A, 0x55, 0x68)
GREY_MID   = RGBColor(0x8A, 0x95, 0xA5)
GREY_LINE  = RGBColor(0xC8, 0xCE, 0xD4)
GREY_PALE  = RGBColor(0xF4, 0xF6, 0xF9)
RED_ACC    = RGBColor(0xC8, 0x3A, 0x1E)   # use ONCE
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
BLACK      = RGBColor(0x10, 0x10, 0x10)

# ---------- slide ----------
prs = Presentation()
prs.slide_width  = Inches(8)
prs.slide_height = Inches(9)
SW, SH = prs.slide_width, prs.slide_height
slide = prs.slides.add_slide(prs.slide_layouts[6])

CN_FONT = "Microsoft YaHei"
EN_FONT = "Arial"

# ---------- helpers ----------
def add_rect(left, top, width, height, fill=None, line=None, line_w=None,
             shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, left, top, width, height)
    s.shadow.inherit = False
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        if line_w is not None:
            s.line.width = line_w
    return s

def add_text(left, top, width, height, runs, *,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    """runs: list of dicts {text, size, bold, italic, color, font}
       OR a single string (uses defaults)."""
    if isinstance(runs, str):
        runs = [{"text": runs}]
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    first = True
    for r in runs:
        if r.get("newline") and not first:
            p = tf.add_paragraph()
        elif first:
            p = tf.paragraphs[0]
        else:
            # same paragraph continuation
            p = tf.paragraphs[-1]
        p.alignment = align
        run = p.add_run()
        run.text = r.get("text", "")
        run.font.name = r.get("font", CN_FONT)
        run.font.size = Pt(r.get("size", 10))
        run.font.bold = r.get("bold", False)
        run.font.italic = r.get("italic", False)
        run.font.color.rgb = r.get("color", BLACK)
        first = False
    return tb

def add_line(x1, y1, x2, y2, color=GREY_LINE, weight=0.5, dashed=False):
    line = slide.shapes.add_connector(1, x1, y1, x2, y2)
    line.line.color.rgb = color
    line.line.width = Pt(weight)
    if dashed:
        from pptx.oxml.ns import qn
        from lxml import etree
        ln = line.line._get_or_add_ln()
        prst = etree.SubElement(ln, qn('a:prstDash'))
        prst.set('val', 'dash')
    return line

# ============================================================
# 1. TOP STRIP : exhibit label + page number + thin rule
# ============================================================
add_text(Inches(0.40), Inches(0.18), Inches(5.0), Inches(0.20),
         [{"text": "EXHIBIT 4 OF 4   |   现场管理操作系统",
           "size": 8, "bold": True, "color": GREY_MID,
           "font": EN_FONT}],
         anchor=MSO_ANCHOR.MIDDLE)
add_text(Inches(5.50), Inches(0.18), Inches(2.10), Inches(0.20),
         [{"text": "PAone × 银卡服销 · 1+N",
           "size": 8, "bold": True, "color": GREY_MID}],
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
add_line(Inches(0.40), Inches(0.42), Inches(7.60), Inches(0.42),
         color=NAVY, weight=1.5)

# ============================================================
# 2. ACTION TITLE
# ============================================================
add_text(Inches(0.40), Inches(0.55), Inches(7.20), Inches(0.95),
         [{"text": "PAone 数智指挥舱将现管岗位重构为「1 名指挥官 + N 个 AI 引擎」，",
           "size": 17, "bold": True, "color": NAVY},
          {"newline": True,
           "text": "组长把时间从查数 / 催办 / 救火转向识别 / 干预 / 复制 / 训练 AI",
           "size": 17, "bold": True, "color": NAVY}],
         anchor=MSO_ANCHOR.TOP)

# standfirst
add_text(Inches(0.40), Inches(1.55), Inches(7.20), Inches(0.55),
         [{"text": "约 ", "size": 9.5, "italic": True, "color": GREY_TXT},
          {"text": "70%", "size": 9.5, "italic": True, "bold": True, "color": RED_ACC},
          {"text": " 现管时间消耗在手工查数与材料生产上；1+N 指挥舱通过 6 个 AI 能力单元",
           "size": 9.5, "italic": True, "color": GREY_TXT},
          {"newline": True,
           "text": "接管标准化数据动作，组长聚焦不可替代的判断与团队能力复制。",
           "size": 9.5, "italic": True, "color": GREY_TXT}])

# hairline below standfirst
add_line(Inches(0.40), Inches(2.12), Inches(7.60), Inches(2.12),
         color=GREY_LINE, weight=0.5)

# ============================================================
# 3. FROM-TO MATRIX (4 rows x 3 cols)
# ============================================================
TBL_X = Inches(0.40)
TBL_Y = Inches(2.22)
COL_W = [Inches(1.40), Inches(2.85), Inches(2.95)]
ROW_H = Inches(0.42)
HDR_H = Inches(0.32)

# section label
add_text(TBL_X, TBL_Y - Inches(0.05), Inches(7.20), Inches(0.22),
         [{"text": "FROM ", "size": 8, "bold": True, "color": GREY_MID, "font": EN_FONT},
          {"text": "传统现管   ", "size": 8, "bold": True, "color": GREY_MID},
          {"text": "→ ", "size": 8, "bold": True, "color": NAVY, "font": EN_FONT},
          {"text": "TO ", "size": 8, "bold": True, "color": NAVY, "font": EN_FONT},
          {"text": "PAone 1+N 数智指挥舱",
           "size": 8, "bold": True, "color": NAVY}])

# header row
hx = TBL_X
hy = TBL_Y + Inches(0.20)
hdr_cells = ["维度", "传统现管 · 人肉盯盘", "PAone 1+N · AI 接管"]
hdr_colors = [GREY_TXT, GREY_TXT, NAVY]
for i, txt in enumerate(hdr_cells):
    fill = GREY_PALE if i < 2 else BLUE_PALE
    add_rect(hx, hy, COL_W[i], HDR_H, fill=fill)
    add_text(hx + Inches(0.10), hy, COL_W[i] - Inches(0.20), HDR_H,
             [{"text": txt, "size": 9, "bold": True, "color": hdr_colors[i]}],
             anchor=MSO_ANCHOR.MIDDLE)
    hx += COL_W[i]

# bottom rule under header
add_line(TBL_X, hy + HDR_H, TBL_X + sum(COL_W, Emu(0)), hy + HDR_H,
         color=NAVY, weight=1.0)

rows = [
    ("数据获取",
     "组长每日手工查报表 / 跑后台 / 拉名单",
     "数据巡场引擎自动抓取大盘 · 员工 · 时段 · 名单 · 成交"),
    ("风险识别",
     "事后复盘，问题暴露已晚",
     "异常预警引擎实时锁定低产 · 掉速 · 名单浪费 · 通时不足"),
    ("经验复制",
     "靠组长记忆与口头辅导，质量参差",
     "话术萃取 + 精准辅导引擎，按个人短板推送沉淀模板"),
    ("材料生产",
     "早会 / 夕会 / 通报材料人肉拼接",
     "复盘生成引擎一键产出，语料进化引擎反向训练 AI"),
]

ry = hy + HDR_H
for r_idx, (dim, old, new) in enumerate(rows):
    rx = TBL_X
    if r_idx % 2 == 1:
        add_rect(rx, ry, sum(COL_W, Emu(0)), ROW_H, fill=GREY_PALE)
    cells = [
        (dim, NAVY,    True),
        (old, GREY_TXT, False),
        (new, NAVY_DARK, False),
    ]
    for i, (txt, color, bold) in enumerate(cells):
        add_text(rx + Inches(0.10), ry, COL_W[i] - Inches(0.20), ROW_H,
                 [{"text": txt, "size": 9, "bold": bold, "color": color}],
                 anchor=MSO_ANCHOR.MIDDLE)
        rx += COL_W[i]
    # row separator
    add_line(TBL_X, ry + ROW_H, TBL_X + sum(COL_W, Emu(0)), ry + ROW_H,
             color=GREY_LINE, weight=0.4)
    ry += ROW_H

# ============================================================
# 4. ARCHITECTURE DIAGRAM : PAone hub + 6 satellite engines
# ============================================================
ARCH_Y0 = ry + Inches(0.25)

# section label
add_text(TBL_X, ARCH_Y0, Inches(7.20), Inches(0.22),
         [{"text": "1+N 指挥舱架构",
           "size": 8, "bold": True, "color": GREY_MID},
          {"text": "    1 名组长指挥官  +  6 个 AI 能力单元",
           "size": 8, "bold": True, "color": NAVY}])

# central hub box
HUB_W = Inches(2.40)
HUB_H = Inches(0.62)
HUB_X = (SW - HUB_W) / 2
HUB_Y = ARCH_Y0 + Inches(0.30)
add_rect(HUB_X, HUB_Y, HUB_W, HUB_H, fill=NAVY,
         shape=MSO_SHAPE.ROUNDED_RECTANGLE)
add_text(HUB_X, HUB_Y, HUB_W, HUB_H,
         [{"text": "PAone 数智指挥舱",
           "size": 12, "bold": True, "color": WHITE}],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
# small subscript inside hub
add_text(HUB_X, HUB_Y + Inches(0.36), HUB_W, Inches(0.22),
         [{"text": "1 组长  +  N 个 AI 引擎",
           "size": 8, "color": BLUE_PALE}],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# 6 engine cards : 2 columns x 3 rows below hub
ENG_Y0 = HUB_Y + HUB_H + Inches(0.25)
ENG_W = Inches(3.50)
ENG_H = Inches(0.50)
ENG_GAP_X = Inches(0.20)
ENG_GAP_Y = Inches(0.10)

engines = [
    ("01", "数据巡场引擎", "替代人工查数"),
    ("02", "异常预警引擎", "提前锁定风险"),
    ("03", "话术萃取引擎", "形成可复制打法"),
    ("04", "精准辅导引擎", "辅导从经验变数据"),
    ("05", "复盘生成引擎", "材料一键产出"),
    ("06", "语料进化引擎", "反向训练 AI 大脑"),
]

eng_positions = []
for i, (num, name, value) in enumerate(engines):
    col = i % 2
    row = i // 2
    x = TBL_X + col * (ENG_W + ENG_GAP_X)
    y = ENG_Y0 + row * (ENG_H + ENG_GAP_Y)
    eng_positions.append((x, y))

    # left navy bar (4pt wide)
    add_rect(x, y, Inches(0.06), ENG_H, fill=NAVY)
    # body
    add_rect(x + Inches(0.06), y, ENG_W - Inches(0.06), ENG_H,
             fill=WHITE, line=GREY_LINE, line_w=Pt(0.5))
    # number
    add_text(x + Inches(0.18), y, Inches(0.40), ENG_H,
             [{"text": num, "size": 11, "bold": True, "color": NAVY,
               "font": EN_FONT}],
             anchor=MSO_ANCHOR.MIDDLE)
    # name
    add_text(x + Inches(0.62), y, Inches(1.55), ENG_H,
             [{"text": name, "size": 10, "bold": True, "color": NAVY_DARK}],
             anchor=MSO_ANCHOR.MIDDLE)
    # value description (right-aligned grey)
    add_text(x + Inches(2.15), y, ENG_W - Inches(2.25), ENG_H,
             [{"text": value, "size": 8.5, "color": GREY_TXT, "italic": True}],
             align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

# connect hub to each engine (thin grey lines from hub bottom to top of each card)
hub_bottom_cx = HUB_X + HUB_W / 2
hub_bottom_cy = HUB_Y + HUB_H
# vertical trunk line
trunk_y = ENG_Y0 - Inches(0.12)
add_line(hub_bottom_cx, hub_bottom_cy, hub_bottom_cx, trunk_y,
         color=GREY_MID, weight=0.6)
# horizontal spine
left_spine_x  = TBL_X + ENG_W / 2
right_spine_x = TBL_X + ENG_W + ENG_GAP_X + ENG_W / 2
add_line(left_spine_x, trunk_y, right_spine_x, trunk_y,
         color=GREY_MID, weight=0.6)
# drop into each card top
for (x, y) in eng_positions:
    cx = x + ENG_W / 2
    add_line(cx, trunk_y, cx, y, color=GREY_MID, weight=0.6)

# ============================================================
# 5. CLOSED-LOOP PROCESS BAR (single horizontal flow)
# ============================================================
ENG_BOTTOM = ENG_Y0 + 3 * ENG_H + 2 * ENG_GAP_Y
LOOP_Y = ENG_BOTTOM + Inches(0.20)

add_text(TBL_X, LOOP_Y, Inches(7.20), Inches(0.22),
         [{"text": "CLOSED LOOP   ", "size": 8, "bold": True,
           "color": GREY_MID, "font": EN_FONT},
          {"text": "数据采集 → AI 识别 → 组长干预 → 话术沉淀 → 团队复制 → 模型进化",
           "size": 9, "bold": True, "color": NAVY}])

# small horizontal bar showing 6 segments
BAR_Y = LOOP_Y + Inches(0.28)
BAR_H = Inches(0.18)
BAR_W = Inches(7.20)
seg_w = BAR_W / 6
loop_steps = ["采集", "识别", "干预", "沉淀", "复制", "进化"]
for i, step in enumerate(loop_steps):
    x = TBL_X + i * seg_w
    # alternating shade
    if i == 5:
        fill = NAVY
        txt_color = WHITE
    else:
        fill = BLUE_PALE if i % 2 == 0 else WHITE
        txt_color = NAVY
    add_rect(x, BAR_Y, seg_w, BAR_H, fill=fill,
             line=NAVY, line_w=Pt(0.5))
    add_text(x, BAR_Y, seg_w, BAR_H,
             [{"text": step, "size": 8.5, "bold": True, "color": txt_color}],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# ============================================================
# 6. KEY TAKEAWAY BOX
# ============================================================
KT_Y = BAR_Y + BAR_H + Inches(0.22)
KT_H = Inches(0.62)
add_rect(TBL_X, KT_Y, Inches(7.20), KT_H, fill=GREY_PALE)
# left navy bar
add_rect(TBL_X, KT_Y, Inches(0.10), KT_H, fill=NAVY)
add_text(TBL_X + Inches(0.25), KT_Y + Inches(0.04),
         Inches(1.3), Inches(0.22),
         [{"text": "KEY TAKEAWAY", "size": 8, "bold": True,
           "color": NAVY, "font": EN_FONT}],
         anchor=MSO_ANCHOR.TOP)
add_text(TBL_X + Inches(0.25), KT_Y + Inches(0.22),
         Inches(7.0), Inches(0.42),
         [{"text": "现管 1+N 不是减负工具，而是",
           "size": 11, "bold": True, "color": BLACK},
          {"text": "现场管理操作系统",
           "size": 11, "bold": True, "color": RED_ACC},
          {"text": "  ——  PAone 实时感知 · 组长精准干预 · 团队能力复制 · AI 持续进化。",
           "size": 11, "bold": True, "color": BLACK}],
         anchor=MSO_ANCHOR.TOP)

# ============================================================
# 7. FOOTNOTE / SOURCE
# ============================================================
FT_Y = KT_Y + KT_H + Inches(0.10)
add_line(TBL_X, FT_Y, Inches(7.60), FT_Y, color=GREY_LINE, weight=0.4)
add_text(TBL_X, FT_Y + Inches(0.04), Inches(6.0), Inches(0.20),
         [{"text": "Source: ", "size": 7, "bold": True,
           "color": GREY_MID, "font": EN_FONT},
          {"text": "银卡服销现场管理诊断 2025Q4 抽样调研 (N=87)；PAone 1+N 产品规划 v2026.05。",
           "size": 7, "color": GREY_MID}],
         anchor=MSO_ANCHOR.TOP)
add_text(Inches(6.40), FT_Y + Inches(0.04),
         Inches(1.20), Inches(0.20),
         [{"text": "Page  1 / 1", "size": 7, "bold": True,
           "color": GREY_MID, "font": EN_FONT}],
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.TOP)

# ---------- save ----------
out = "/projects/sandbox/kiro2026/PAone_现管1+N_麦肯锡版.pptx"
prs.save(out)
print("Saved:", out)
