"""
McKinsey v2 — 8:9 portrait single-page exhibit.
Hero chart: time-reallocation stacked bars (before / after).
Supporting: 6 AI engines grid + KPI tiles + closed-loop + key takeaway.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# ---------- McKinsey palette ----------
NAVY        = RGBColor(0x00, 0x3A, 0x70)   # primary
NAVY_DARK   = RGBColor(0x00, 0x29, 0x55)
BLUE_MID    = RGBColor(0x2E, 0x6F, 0xB5)
BLUE_LIGHT  = RGBColor(0x9B, 0xC4, 0xE8)
BLUE_PALE   = RGBColor(0xE6, 0xEE, 0xF7)
GREY_TXT    = RGBColor(0x4A, 0x55, 0x68)
GREY_MID    = RGBColor(0x8A, 0x95, 0xA5)
GREY_LINE   = RGBColor(0xC8, 0xCE, 0xD4)
GREY_PALE   = RGBColor(0xF4, 0xF6, 0xF9)
GREY_FILL   = RGBColor(0xC8, 0xCE, 0xD4)   # for grey bar segments
GREY_FILL_2 = RGBColor(0xA9, 0xB2, 0xBF)
RED_ACC     = RGBColor(0xC8, 0x3A, 0x1E)
WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
BLACK       = RGBColor(0x10, 0x10, 0x10)

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
# 1. TOP STRIP
# ============================================================
add_text(Inches(0.40), Inches(0.18), Inches(5.0), Inches(0.20),
         [{"text": "EXHIBIT 4 OF 4   |   现场管理操作系统  /  时间再配置",
           "size": 8, "bold": True, "color": GREY_MID, "font": EN_FONT}],
         anchor=MSO_ANCHOR.MIDDLE)
add_text(Inches(5.50), Inches(0.18), Inches(2.10), Inches(0.20),
         [{"text": "PAone × 银卡服销 · 1+N",
           "size": 8, "bold": True, "color": GREY_MID}],
         align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
add_line(Inches(0.40), Inches(0.42), Inches(7.60), Inches(0.42),
         color=NAVY, weight=1.5)

# ============================================================
# 2. ACTION TITLE (with quantitative claim)
# ============================================================
add_text(Inches(0.40), Inches(0.55), Inches(7.20), Inches(0.95),
         [{"text": "PAone 1+N 释放 ", "size": 17, "bold": True, "color": NAVY},
          {"text": "~70%", "size": 17, "bold": True, "color": RED_ACC},
          {"text": " 现管组长的标准化数据动作时间，",
           "size": 17, "bold": True, "color": NAVY},
          {"newline": True,
           "text": "重投到识别 / 干预 / 辅导 / 复制 / 训练 AI 等不可替代的高价值动作",
           "size": 17, "bold": True, "color": NAVY}],
         anchor=MSO_ANCHOR.TOP)

# standfirst
add_text(Inches(0.40), Inches(1.55), Inches(7.20), Inches(0.40),
         [{"text": "6 个 AI 能力单元接管查数 / 催办 / 救火 / 材料拼接，",
           "size": 9.5, "italic": True, "color": GREY_TXT},
          {"text": "组长有效管理半径预计提升 2 ~ 3 倍。",
           "size": 9.5, "italic": True, "color": GREY_TXT}])

# hairline
add_line(Inches(0.40), Inches(2.02), Inches(7.60), Inches(2.02),
         color=GREY_LINE, weight=0.5)

# ============================================================
# 3. HERO CHART : time reallocation (Before vs After, 100% stacked)
# ============================================================
CHART_X0 = Inches(0.40)
CHART_W  = Inches(6.20)        # bar width
LABEL_W  = Inches(0.95)        # label column width
TOTAL_W  = Inches(7.20)
CHART_Y0 = Inches(2.15)

# chart caption
add_text(CHART_X0, CHART_Y0, TOTAL_W, Inches(0.22),
         [{"text": "EXHIBIT  ", "size": 8, "bold": True,
           "color": GREY_MID, "font": EN_FONT},
          {"text": "现管组长每日工作时间分配", "size": 9, "bold": True, "color": NAVY},
          {"text": "    % of working hours · illustrative",
           "size": 8, "italic": True, "color": GREY_MID, "font": EN_FONT}])

# legend (above bars)
LEG_Y = CHART_Y0 + Inches(0.30)
def legend_chip(x, y, color, text):
    add_rect(x, y + Inches(0.04), Inches(0.16), Inches(0.12), fill=color)
    add_text(x + Inches(0.20), y, Inches(2.4), Inches(0.20),
             [{"text": text, "size": 8, "color": GREY_TXT}],
             anchor=MSO_ANCHOR.MIDDLE)

legend_chip(CHART_X0, LEG_Y, GREY_FILL, "数据 / 材料动作（低价值）")
legend_chip(CHART_X0 + Inches(2.55), LEG_Y, BLUE_LIGHT, "辅导")
legend_chip(CHART_X0 + Inches(3.65), LEG_Y, NAVY,       "干预 · 复制 · 训练 AI（高价值）")

# bar geometry
BAR_H = Inches(0.46)
BAR_GAP = Inches(0.20)
BAR_Y_BEFORE = LEG_Y + Inches(0.30)
BAR_Y_AFTER  = BAR_Y_BEFORE + BAR_H + BAR_GAP

# Before segments (low | coach | high)
before = [
    ("数据 / 材料动作", 71, GREY_FILL,  WHITE),
    ("辅导",            12, BLUE_LIGHT, NAVY_DARK),
    ("干预 · 复制",     17, NAVY,       WHITE),
]
# After segments
after = [
    ("剩余", 12, GREY_FILL,  NAVY_DARK),
    ("辅导", 22, BLUE_LIGHT, NAVY_DARK),
    ("干预 · 复制 · 训练 AI", 66, NAVY, WHITE),
]

def draw_stacked_bar(label, label_color, bar_y, segments, total_w):
    # label column
    add_text(CHART_X0, bar_y - Inches(0.02),
             LABEL_W, BAR_H + Inches(0.05),
             [{"text": label, "size": 10, "bold": True, "color": label_color}],
             anchor=MSO_ANCHOR.MIDDLE)
    bar_x0 = CHART_X0 + LABEL_W + Inches(0.10)
    bar_w  = total_w - LABEL_W - Inches(0.10)
    # draw segments
    cur_x = bar_x0
    for (seg_label, pct, fill, txt_color) in segments:
        seg_w = Emu(int(bar_w * pct / 100))
        add_rect(cur_x, bar_y, seg_w, BAR_H, fill=fill)
        # in-bar value
        if pct >= 10:
            add_text(cur_x, bar_y, seg_w, BAR_H,
                     [{"text": f"{pct}%", "size": 12, "bold": True,
                       "color": txt_color, "font": EN_FONT}],
                     align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        cur_x += seg_w
    # right end total
    add_text(bar_x0 + bar_w + Inches(0.05), bar_y,
             Inches(0.5), BAR_H,
             [{"text": "100%", "size": 8, "bold": True,
               "color": GREY_MID, "font": EN_FONT}],
             anchor=MSO_ANCHOR.MIDDLE)

draw_stacked_bar("Before · 传统现管", GREY_TXT, BAR_Y_BEFORE, before, TOTAL_W)
draw_stacked_bar("After · PAone 1+N", NAVY,    BAR_Y_AFTER,  after,  TOTAL_W)

# delta annotation between bars
DELTA_Y = BAR_Y_BEFORE + BAR_H + Inches(0.02)
DELTA_H = BAR_GAP - Inches(0.04)
add_text(CHART_X0 + Inches(1.05), DELTA_Y - Inches(0.02),
         Inches(6.2), DELTA_H + Inches(0.04),
         [{"text": "▲ ", "size": 9, "bold": True, "color": RED_ACC,
           "font": EN_FONT},
          {"text": "高价值动作占比从 17% → 66%，",
           "size": 8.5, "bold": True, "color": NAVY},
          {"text": "+49 pp", "size": 9, "bold": True, "color": RED_ACC,
           "font": EN_FONT},
          {"text": "（数据 / 材料动作 71% → 12%）",
           "size": 8.5, "color": GREY_TXT}],
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)

# bottom rule under chart
RULE_Y = BAR_Y_AFTER + BAR_H + Inches(0.10)
add_line(CHART_X0, RULE_Y, CHART_X0 + TOTAL_W, RULE_Y,
         color=GREY_LINE, weight=0.5)

# ============================================================
# 4. MECHANISM : 6 AI engines 3x2 grid (compact)
# ============================================================
MECH_Y0 = RULE_Y + Inches(0.15)
add_text(CHART_X0, MECH_Y0, TOTAL_W, Inches(0.22),
         [{"text": "MECHANISM   ", "size": 8, "bold": True,
           "color": GREY_MID, "font": EN_FONT},
          {"text": "6 个 AI 能力单元 — 数智指挥舱（", "size": 9, "bold": True,
           "color": NAVY},
          {"text": "PAone", "size": 9, "bold": True, "color": NAVY,
           "font": EN_FONT},
          {"text": "）",  "size": 9, "bold": True, "color": NAVY}])

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
    # left navy bar
    add_rect(x, y, Inches(0.06), ENG_H, fill=NAVY)
    # body
    add_rect(x + Inches(0.06), y, ENG_W - Inches(0.06), ENG_H,
             fill=WHITE, line=GREY_LINE, line_w=Pt(0.5))
    # number
    add_text(x + Inches(0.16), y, Inches(0.36), ENG_H,
             [{"text": num, "size": 11, "bold": True, "color": NAVY,
               "font": EN_FONT}],
             anchor=MSO_ANCHOR.MIDDLE)
    # name
    add_text(x + Inches(0.55), y + Inches(0.04),
             ENG_W - Inches(0.65), Inches(0.24),
             [{"text": name, "size": 10, "bold": True, "color": NAVY_DARK}],
             anchor=MSO_ANCHOR.TOP)
    # value
    add_text(x + Inches(0.55), y + Inches(0.28),
             ENG_W - Inches(0.65), Inches(0.24),
             [{"text": value, "size": 8, "color": GREY_TXT, "italic": True}],
             anchor=MSO_ANCHOR.TOP)

# ============================================================
# 5. KPI tiles (3 quantitative claims)
# ============================================================
KPI_Y0 = ENG_Y0 + 2 * (ENG_H + ENG_GAP_Y) + Inches(0.18)
add_text(CHART_X0, KPI_Y0, TOTAL_W, Inches(0.22),
         [{"text": "PRO-FORMA IMPACT   ",
           "size": 8, "bold": True, "color": GREY_MID, "font": EN_FONT},
          {"text": "试点目标值（直觉测算，待实测校准）",
           "size": 8.5, "italic": True, "color": GREY_TXT}])

KPI_Y = KPI_Y0 + Inches(0.28)
KPI_H = Inches(0.78)
KPI_W = (TOTAL_W - Inches(0.20)) / 3

kpis = [
    ("~70%", "数据/材料动作时间被 AI 接管",   NAVY),
    ("2-3x", "组长有效管理半径放大",           NAVY),
    ("+49pp", "高价值动作占比提升",            RED_ACC),
]
for i, (num, desc, color) in enumerate(kpis):
    x = CHART_X0 + i * (KPI_W + Inches(0.10))
    add_rect(x, KPI_Y, KPI_W, KPI_H, fill=GREY_PALE)
    # left accent bar
    add_rect(x, KPI_Y, Inches(0.06), KPI_H, fill=color)
    # big number
    add_text(x + Inches(0.18), KPI_Y + Inches(0.04),
             KPI_W - Inches(0.25), Inches(0.42),
             [{"text": num, "size": 22, "bold": True, "color": color,
               "font": EN_FONT}],
             anchor=MSO_ANCHOR.TOP)
    # description
    add_text(x + Inches(0.18), KPI_Y + Inches(0.46),
             KPI_W - Inches(0.25), Inches(0.30),
             [{"text": desc, "size": 8.5, "color": GREY_TXT}],
             anchor=MSO_ANCHOR.TOP)

# ============================================================
# 6. CLOSED LOOP BAR (compact)
# ============================================================
LOOP_Y = KPI_Y + KPI_H + Inches(0.18)
add_text(CHART_X0, LOOP_Y, TOTAL_W, Inches(0.22),
         [{"text": "CLOSED LOOP   ",
           "size": 8, "bold": True, "color": GREY_MID, "font": EN_FONT},
          {"text": "数据采集 → AI 识别 → 组长干预 → 话术沉淀 → 团队复制 → 模型进化",
           "size": 9, "bold": True, "color": NAVY}])

BAR_Y2 = LOOP_Y + Inches(0.26)
BAR_H2 = Inches(0.16)
seg_w = TOTAL_W / 6
loop_steps = ["采集", "识别", "干预", "沉淀", "复制", "进化"]
for i, step in enumerate(loop_steps):
    x = CHART_X0 + i * seg_w
    if i == 5:
        fill = NAVY; tc = WHITE
    else:
        fill = BLUE_PALE if i % 2 == 0 else WHITE; tc = NAVY
    add_rect(x, BAR_Y2, seg_w, BAR_H2, fill=fill,
             line=NAVY, line_w=Pt(0.5))
    add_text(x, BAR_Y2, seg_w, BAR_H2,
             [{"text": step, "size": 8.5, "bold": True, "color": tc}],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# ============================================================
# 7. KEY TAKEAWAY
# ============================================================
KT_Y = BAR_Y2 + BAR_H2 + Inches(0.18)
KT_H = Inches(0.55)
add_rect(CHART_X0, KT_Y, TOTAL_W, KT_H, fill=GREY_PALE)
add_rect(CHART_X0, KT_Y, Inches(0.10), KT_H, fill=NAVY)
add_text(CHART_X0 + Inches(0.22), KT_Y + Inches(0.04),
         Inches(1.3), Inches(0.20),
         [{"text": "KEY TAKEAWAY",
           "size": 7.5, "bold": True, "color": NAVY, "font": EN_FONT}],
         anchor=MSO_ANCHOR.TOP)
add_text(CHART_X0 + Inches(0.22), KT_Y + Inches(0.20),
         TOTAL_W - Inches(0.30), Inches(0.34),
         [{"text": "现管 1+N 不是减负工具，而是",
           "size": 10.5, "bold": True, "color": BLACK},
          {"text": "现场管理操作系统",
           "size": 10.5, "bold": True, "color": RED_ACC},
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

# ---------- save ----------
out = "/projects/sandbox/kiro2026/PAone_现管1+N_麦肯锡v2.pptx"
prs.save(out)
print("Saved:", out)
