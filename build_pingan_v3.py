"""
Ping An orange theme on white background — McKinsey v3.
8:9 portrait single-page exhibit.
Hero chart: time-reallocation stacked bar (Before / After).
Supporting: 6 AI engines, KPI tiles, closed-loop bar, key takeaway, footnote.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# ---------- Ping An orange palette ----------
ORANGE        = RGBColor(0xE9, 0x47, 0x09)   # primary brand
ORANGE_DARK   = RGBColor(0xB8, 0x35, 0x05)
ORANGE_DARKER = RGBColor(0x7E, 0x24, 0x02)
ORANGE_MID    = RGBColor(0xFF, 0x8A, 0x3D)
ORANGE_LIGHT  = RGBColor(0xFF, 0xC8, 0x9B)
ORANGE_PALE   = RGBColor(0xFF, 0xF1, 0xE6)
GREY_TXT      = RGBColor(0x33, 0x3A, 0x47)
GREY_BODY     = RGBColor(0x4A, 0x55, 0x68)
GREY_MID      = RGBColor(0x8A, 0x95, 0xA5)
GREY_LINE     = RGBColor(0xC8, 0xCE, 0xD4)
GREY_PALE     = RGBColor(0xF4, 0xF6, 0xF9)
GREY_FILL     = RGBColor(0xC8, 0xCE, 0xD4)   # low-value segment
SLATE         = RGBColor(0x1F, 0x2A, 0x44)
WHITE         = RGBColor(0xFF, 0xFF, 0xFF)
BLACK         = RGBColor(0x1A, 0x1A, 0x1A)

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

def add_line(x1, y1, x2, y2, color=GREY_LINE, weight=0.5):
    line = slide.shapes.add_connector(1, x1, y1, x2, y2)
    line.line.color.rgb = color
    line.line.width = Pt(weight)
    return line

# ============================================================
# 0. PING AN BRAND RIBBON (top 0.10 inch)
# ============================================================
add_rect(Inches(0), Inches(0), SW, Inches(0.10), fill=ORANGE)

# ============================================================
# 1. TOP STRIP
# ============================================================
add_text(Inches(0.40), Inches(0.20), Inches(5.0), Inches(0.22),
         [{"text": "PINGAN", "size": 9, "bold": True, "color": ORANGE,
           "font": EN_FONT},
          {"text": "  |  PAone × 银卡服销 · 现管 1+N",
           "size": 8.5, "bold": True, "color": GREY_TXT}],
         anchor=MSO_ANCHOR.MIDDLE)
add_text(Inches(5.50), Inches(0.20), Inches(2.10), Inches(0.22),
         [{"text": "EXHIBIT 4 OF 4",
           "size": 8, "bold": True, "color": GREY_MID, "font": EN_FONT}],
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
add_line(Inches(0.40), Inches(0.46), Inches(7.60), Inches(0.46),
         color=ORANGE, weight=1.5)

# ============================================================
# 2. ACTION TITLE
# ============================================================
add_text(Inches(0.40), Inches(0.58), Inches(7.20), Inches(0.95),
         [{"text": "PAone 1+N 释放 ",
           "size": 17, "bold": True, "color": BLACK},
          {"text": "~70%",
           "size": 19, "bold": True, "color": ORANGE},
          {"text": " 现管组长的标准化数据动作时间，",
           "size": 17, "bold": True, "color": BLACK},
          {"newline": True,
           "text": "重投到识别 / 干预 / 辅导 / 复制 / 训练 AI 等不可替代的高价值动作",
           "size": 17, "bold": True, "color": BLACK}],
         anchor=MSO_ANCHOR.TOP)

# standfirst
add_text(Inches(0.40), Inches(1.58), Inches(7.20), Inches(0.40),
         [{"text": "6 个 AI 能力单元接管查数 / 催办 / 救火 / 材料拼接，",
           "size": 9.5, "italic": True, "color": GREY_BODY},
          {"text": "组长有效管理半径预计提升 2 ~ 3 倍。",
           "size": 9.5, "italic": True, "color": GREY_BODY}])

add_line(Inches(0.40), Inches(2.05), Inches(7.60), Inches(2.05),
         color=GREY_LINE, weight=0.5)

# ============================================================
# 3. HERO CHART : 100% stacked bars
# ============================================================
CHART_X0 = Inches(0.40)
LABEL_W  = Inches(0.95)
TOTAL_W  = Inches(7.20)
CHART_Y0 = Inches(2.18)

add_text(CHART_X0, CHART_Y0, TOTAL_W, Inches(0.22),
         [{"text": "EXHIBIT  ", "size": 8, "bold": True,
           "color": GREY_MID, "font": EN_FONT},
          {"text": "现管组长每日工作时间分配",
           "size": 9, "bold": True, "color": ORANGE_DARK},
          {"text": "    % of working hours - illustrative",
           "size": 8, "italic": True, "color": GREY_MID, "font": EN_FONT}])

# legend
LEG_Y = CHART_Y0 + Inches(0.30)
def legend_chip(x, y, color, text):
    add_rect(x, y + Inches(0.04), Inches(0.16), Inches(0.12), fill=color)
    add_text(x + Inches(0.20), y, Inches(2.6), Inches(0.20),
             [{"text": text, "size": 8, "color": GREY_BODY}],
             anchor=MSO_ANCHOR.MIDDLE)

legend_chip(CHART_X0,                LEG_Y, GREY_FILL,    "数据 / 材料动作（低价值）")
legend_chip(CHART_X0 + Inches(2.55), LEG_Y, ORANGE_LIGHT, "辅导")
legend_chip(CHART_X0 + Inches(3.65), LEG_Y, ORANGE_DARK,  "干预 · 复制 · 训练 AI（高价值）")

# bars
BAR_H = Inches(0.46)
BAR_GAP = Inches(0.20)
BAR_Y_BEFORE = LEG_Y + Inches(0.30)
BAR_Y_AFTER  = BAR_Y_BEFORE + BAR_H + BAR_GAP

before = [
    ("数据 / 材料动作", 71, GREY_FILL,    BLACK),
    ("辅导",            12, ORANGE_LIGHT, ORANGE_DARKER),
    ("干预 · 复制",     17, ORANGE_DARK,  WHITE),
]
after = [
    ("剩余",                  12, GREY_FILL,    BLACK),
    ("辅导",                  22, ORANGE_LIGHT, ORANGE_DARKER),
    ("干预 · 复制 · 训练 AI", 66, ORANGE_DARK,  WHITE),
]

def draw_stacked_bar(label, label_color, bar_y, segments, total_w):
    add_text(CHART_X0, bar_y - Inches(0.02),
             LABEL_W, BAR_H + Inches(0.05),
             [{"text": label, "size": 10, "bold": True, "color": label_color}],
             anchor=MSO_ANCHOR.MIDDLE)
    bar_x0 = CHART_X0 + LABEL_W + Inches(0.10)
    bar_w  = total_w - LABEL_W - Inches(0.10)
    cur_x = bar_x0
    for (seg_label, pct, fill, txt_color) in segments:
        seg_w = Emu(int(bar_w * pct / 100))
        add_rect(cur_x, bar_y, seg_w, BAR_H, fill=fill)
        if pct >= 10:
            add_text(cur_x, bar_y, seg_w, BAR_H,
                     [{"text": f"{pct}%", "size": 12, "bold": True,
                       "color": txt_color, "font": EN_FONT}],
                     align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        cur_x += seg_w
    add_text(bar_x0 + bar_w + Inches(0.05), bar_y,
             Inches(0.5), BAR_H,
             [{"text": "100%", "size": 8, "bold": True,
               "color": GREY_MID, "font": EN_FONT}],
             anchor=MSO_ANCHOR.MIDDLE)

draw_stacked_bar("Before · 传统现管", GREY_BODY,   BAR_Y_BEFORE, before, TOTAL_W)
draw_stacked_bar("After · PAone 1+N", ORANGE_DARK, BAR_Y_AFTER,  after,  TOTAL_W)

# delta annotation between bars
DELTA_Y = BAR_Y_BEFORE + BAR_H + Inches(0.02)
DELTA_H = BAR_GAP - Inches(0.04)
add_text(CHART_X0 + Inches(1.05), DELTA_Y - Inches(0.02),
         Inches(6.2), DELTA_H + Inches(0.04),
         [{"text": "▲ ", "size": 9, "bold": True, "color": ORANGE,
           "font": EN_FONT},
          {"text": "高价值动作占比 17% → 66%，",
           "size": 8.5, "bold": True, "color": ORANGE_DARK},
          {"text": "+49 pp",
           "size": 9, "bold": True, "color": ORANGE, "font": EN_FONT},
          {"text": "（数据 / 材料动作 71% → 12%）",
           "size": 8.5, "color": GREY_BODY}],
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)

RULE_Y = BAR_Y_AFTER + BAR_H + Inches(0.10)
add_line(CHART_X0, RULE_Y, CHART_X0 + TOTAL_W, RULE_Y,
         color=GREY_LINE, weight=0.5)

# ============================================================
# 4. MECHANISM : 6 AI engines (3 cols x 2 rows)
# ============================================================
MECH_Y0 = RULE_Y + Inches(0.15)
add_text(CHART_X0, MECH_Y0, TOTAL_W, Inches(0.22),
         [{"text": "MECHANISM   ", "size": 8, "bold": True,
           "color": GREY_MID, "font": EN_FONT},
          {"text": "6 个 AI 能力单元 — 数智指挥舱（",
           "size": 9, "bold": True, "color": ORANGE_DARK},
          {"text": "PAone", "size": 9, "bold": True, "color": ORANGE_DARK,
           "font": EN_FONT},
          {"text": "）",  "size": 9, "bold": True, "color": ORANGE_DARK}])

ENG_Y0 = MECH_Y0 + Inches(0.28)
ENG_W  = Inches(2.32)
ENG_H  = Inches(0.55)
ENG_GAP_X = Inches(0.12)
ENG_GAP_Y = Inches(0.10)

engines = [
    ("01", "数据巡场", "替代人工查数"),
    ("02", "异常预警", "提前锁风险"),
    ("03", "话术萃取", "复制销冠打法"),
    ("04", "精准辅导", "辅导经验数据化"),
    ("05", "复盘生成", "材料一键产出"),
    ("06", "语料进化", "反向训练 AI"),
]

for i, (num, name, value) in enumerate(engines):
    col = i % 3
    row = i // 3
    x = CHART_X0 + col * (ENG_W + ENG_GAP_X)
    y = ENG_Y0 + row * (ENG_H + ENG_GAP_Y)
    # left orange accent bar
    add_rect(x, y, Inches(0.06), ENG_H, fill=ORANGE)
    # body
    add_rect(x + Inches(0.06), y, ENG_W - Inches(0.06), ENG_H,
             fill=WHITE, line=GREY_LINE, line_w=Pt(0.5))
    # number
    add_text(x + Inches(0.16), y, Inches(0.36), ENG_H,
             [{"text": num, "size": 11, "bold": True, "color": ORANGE_DARK,
               "font": EN_FONT}],
             anchor=MSO_ANCHOR.MIDDLE)
    # name
    add_text(x + Inches(0.55), y + Inches(0.04),
             ENG_W - Inches(0.65), Inches(0.24),
             [{"text": name, "size": 10, "bold": True, "color": BLACK}],
             anchor=MSO_ANCHOR.TOP)
    # value
    add_text(x + Inches(0.55), y + Inches(0.28),
             ENG_W - Inches(0.65), Inches(0.24),
             [{"text": value, "size": 8, "color": GREY_BODY, "italic": True}],
             anchor=MSO_ANCHOR.TOP)

# ============================================================
# 5. KPI tiles
# ============================================================
KPI_Y0 = ENG_Y0 + 2 * (ENG_H + ENG_GAP_Y) + Inches(0.18)
add_text(CHART_X0, KPI_Y0, TOTAL_W, Inches(0.22),
         [{"text": "PRO-FORMA IMPACT   ",
           "size": 8, "bold": True, "color": GREY_MID, "font": EN_FONT},
          {"text": "试点目标值（直觉测算，待实测校准）",
           "size": 8.5, "italic": True, "color": GREY_BODY}])

KPI_Y = KPI_Y0 + Inches(0.28)
KPI_H = Inches(0.78)
KPI_W = (TOTAL_W - Inches(0.20)) / 3

kpis = [
    ("~70%", "数据/材料动作时间被 AI 接管",   ORANGE_DARK),
    ("2-3x", "组长有效管理半径放大",           ORANGE_DARK),
    ("+49pp", "高价值动作占比提升",            ORANGE),
]
for i, (num, desc, color) in enumerate(kpis):
    x = CHART_X0 + i * (KPI_W + Inches(0.10))
    add_rect(x, KPI_Y, KPI_W, KPI_H, fill=ORANGE_PALE)
    add_rect(x, KPI_Y, Inches(0.06), KPI_H, fill=color)
    add_text(x + Inches(0.18), KPI_Y + Inches(0.04),
             KPI_W - Inches(0.25), Inches(0.42),
             [{"text": num, "size": 22, "bold": True, "color": color,
               "font": EN_FONT}],
             anchor=MSO_ANCHOR.TOP)
    add_text(x + Inches(0.18), KPI_Y + Inches(0.46),
             KPI_W - Inches(0.25), Inches(0.30),
             [{"text": desc, "size": 8.5, "color": GREY_BODY}],
             anchor=MSO_ANCHOR.TOP)

# ============================================================
# 6. CLOSED LOOP BAR
# ============================================================
LOOP_Y = KPI_Y + KPI_H + Inches(0.18)
add_text(CHART_X0, LOOP_Y, TOTAL_W, Inches(0.22),
         [{"text": "CLOSED LOOP   ",
           "size": 8, "bold": True, "color": GREY_MID, "font": EN_FONT},
          {"text": "数据采集 → AI 识别 → 组长干预 → 话术沉淀 → 团队复制 → 模型进化",
           "size": 9, "bold": True, "color": ORANGE_DARK}])

BAR_Y2 = LOOP_Y + Inches(0.26)
BAR_H2 = Inches(0.16)
seg_w = TOTAL_W / 6
loop_steps = ["采集", "识别", "干预", "沉淀", "复制", "进化"]
for i, step in enumerate(loop_steps):
    x = CHART_X0 + i * seg_w
    if i == 5:
        fill = ORANGE; tc = WHITE
    else:
        fill = ORANGE_PALE if i % 2 == 0 else WHITE; tc = ORANGE_DARK
    add_rect(x, BAR_Y2, seg_w, BAR_H2, fill=fill,
             line=ORANGE, line_w=Pt(0.5))
    add_text(x, BAR_Y2, seg_w, BAR_H2,
             [{"text": step, "size": 8.5, "bold": True, "color": tc}],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# ============================================================
# 7. KEY TAKEAWAY
# ============================================================
KT_Y = BAR_Y2 + BAR_H2 + Inches(0.18)
KT_H = Inches(0.55)
add_rect(CHART_X0, KT_Y, TOTAL_W, KT_H, fill=ORANGE_PALE)
add_rect(CHART_X0, KT_Y, Inches(0.10), KT_H, fill=ORANGE)
add_text(CHART_X0 + Inches(0.22), KT_Y + Inches(0.04),
         Inches(1.3), Inches(0.20),
         [{"text": "KEY TAKEAWAY",
           "size": 7.5, "bold": True, "color": ORANGE_DARK, "font": EN_FONT}],
         anchor=MSO_ANCHOR.TOP)
add_text(CHART_X0 + Inches(0.22), KT_Y + Inches(0.20),
         TOTAL_W - Inches(0.30), Inches(0.34),
         [{"text": "现管 1+N 不是减负工具，而是",
           "size": 10.5, "bold": True, "color": BLACK},
          {"text": "现场管理操作系统",
           "size": 10.5, "bold": True, "color": ORANGE},
          {"text": " — 把组长从动作执行者升级为指挥官 + AI 训练师。",
           "size": 10.5, "bold": True, "color": BLACK}],
         anchor=MSO_ANCHOR.TOP)

# ============================================================
# 8. FOOTNOTE
# ============================================================
FT_Y = KT_Y + KT_H + Inches(0.10)
add_line(CHART_X0, FT_Y, CHART_X0 + TOTAL_W, FT_Y,
         color=GREY_LINE, weight=0.4)
add_text(CHART_X0, FT_Y + Inches(0.04), Inches(6.0), Inches(0.30),
         [{"text": "Source: ", "size": 7, "bold": True,
           "color": GREY_MID, "font": EN_FONT},
          {"text": "银卡服销现场管理诊断 2025Q4 抽样调研 (N=87)；PAone 1+N 产品规划 v2026.05；",
           "size": 7, "color": GREY_MID},
          {"newline": True,
           "text": "Note: 时间分配为示意目标值，实际比例视分行 / 团队差异；'+49 pp' 为目标态相对当前态的预计提升。",
           "size": 7, "italic": True, "color": GREY_MID}],
         anchor=MSO_ANCHOR.TOP)
add_text(Inches(6.40), FT_Y + Inches(0.04),
         Inches(1.20), Inches(0.20),
         [{"text": "Page  1 / 1",
           "size": 7, "bold": True, "color": GREY_MID, "font": EN_FONT}],
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.TOP)

# bottom 4pt orange ribbon (echoes top)
add_rect(Inches(0), SH - Inches(0.06), SW, Inches(0.06), fill=ORANGE)

# ---------- save ----------
out = "/projects/sandbox/kiro2026/PAone_现管1+N_平安橙v3.pptx"
prs.save(out)
print("Saved:", out)
