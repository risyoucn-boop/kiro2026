# -*- coding: utf-8 -*-
"""
《三位科幻大师的"武功秘籍"》紧凑演讲版
13 页 · 每页约 1 分钟 · 总时长 12-13 分钟
适合深圳小学六年级学生上台演讲
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

# ================= 主题色 =================
NAVY      = RGBColor(0x0B, 0x1A, 0x3A)
DEEP_BLUE = RGBColor(0x10, 0x25, 0x4F)
PURPLE    = RGBColor(0x3B, 0x1E, 0x6E)
ACCENT    = RGBColor(0xF2, 0xC9, 0x4C)   # 金
PINK      = RGBColor(0xE9, 0x4B, 0x7B)
CYAN      = RGBColor(0x4B, 0xC8, 0xE9)
WHITE     = RGBColor(0xF5, 0xF7, 0xFA)
LIGHT     = RGBColor(0xCB, 0xD5, 0xE0)
DIM       = RGBColor(0x8A, 0x99, 0xB3)

CN_FONT   = "Microsoft YaHei"
EN_FONT   = "Calibri"

# ================= 演示文稿初始化 =================
prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]

TOTAL = 13


# ================= 工具函数 =================

def add_slide():
    return prs.slides.add_slide(BLANK)


def set_solid_bg(slide, rgb):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SW, SH)
    bg.line.fill.background()
    bg.fill.solid()
    bg.fill.fore_color.rgb = rgb
    bg.shadow.inherit = False
    spTree = bg._element.getparent()
    spTree.remove(bg._element)
    spTree.insert(2, bg._element)
    return bg


def add_rect(slide, x, y, w, h, fill=None, line=None, line_width=None,
             transparency=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shp.shadow.inherit = False
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
        if transparency is not None:
            sp = shp.fill.fore_color._xFill
            srgb = sp.find(qn('a:srgbClr'))
            if srgb is not None:
                alpha = etree.SubElement(srgb, qn('a:alpha'))
                alpha.set('val', str(int((1 - transparency) * 100000)))
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        if line_width is not None:
            shp.line.width = line_width
    return shp


def add_round_rect(slide, x, y, w, h, fill=None, line=None, line_width=None,
                   corner=0.1):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    shp.shadow.inherit = False
    shp.adjustments[0] = corner
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        if line_width is not None:
            shp.line.width = line_width
    return shp


def add_oval(slide, x, y, w, h, fill=None, line=None, line_width=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, w, h)
    shp.shadow.inherit = False
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        if line_width is not None:
            shp.line.width = line_width
    return shp


def add_text(slide, x, y, w, h, text, *, size=18, color=WHITE, bold=False,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font=CN_FONT,
             italic=False, line_spacing=1.25):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    lines = text.split("\n") if isinstance(text, str) else list(text)
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        run = p.add_run()
        run.text = line
        f = run.font
        f.name = font
        f.size = Pt(size)
        f.bold = bold
        f.italic = italic
        f.color.rgb = color
        rPr = run._r.get_or_add_rPr()
        ea = rPr.find(qn('a:ea'))
        if ea is None:
            ea = etree.SubElement(rPr, qn('a:ea'))
        ea.set('typeface', font)
    return tb


def add_rich_text(slide, x, y, w, h, runs, *, align=PP_ALIGN.LEFT,
                  anchor=MSO_ANCHOR.TOP, line_spacing=1.3):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for i, line_runs in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        for text, opts in line_runs:
            run = p.add_run()
            run.text = text
            f = run.font
            f.name = opts.get("font", CN_FONT)
            f.size = Pt(opts.get("size", 18))
            f.bold = opts.get("bold", False)
            f.italic = opts.get("italic", False)
            f.color.rgb = opts.get("color", WHITE)
            rPr = run._r.get_or_add_rPr()
            ea = rPr.find(qn('a:ea'))
            if ea is None:
                ea = etree.SubElement(rPr, qn('a:ea'))
            ea.set('typeface', opts.get("font", CN_FONT))
    return tb


def starfield(slide, count=40, seed=0):
    import random
    rnd = random.Random(seed)
    for _ in range(count):
        x = Emu(int(rnd.random() * SW))
        y = Emu(int(rnd.random() * SH * 0.95))
        r = rnd.choice([1, 1, 1, 2, 2, 3])
        size = Emu(int(r * 30000))
        dot = add_oval(slide, x, y, size, size, fill=WHITE)
        sp = dot.fill.fore_color._xFill
        srgb = sp.find(qn('a:srgbClr'))
        if srgb is not None:
            alpha = etree.SubElement(srgb, qn('a:alpha'))
            alpha.set('val', str(rnd.choice([25000, 40000, 55000, 75000])))


def page_decor(slide, page_no, section=None, time_tag=None):
    add_rect(slide, Inches(0.6), Inches(0.45), Inches(0.5), Emu(38100),
             fill=ACCENT)
    if section:
        add_text(slide, Inches(1.2), Inches(0.32), Inches(8), Inches(0.4),
                 section, size=11, color=ACCENT, bold=True,
                 anchor=MSO_ANCHOR.MIDDLE)
    if time_tag:
        add_text(slide, Inches(10.0), Inches(0.32), Inches(2.7),
                 Inches(0.4), time_tag, size=11, color=DIM, bold=True,
                 align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Inches(11.5), Inches(7.05), Inches(1.5), Inches(0.3),
             f"{page_no:02d} / {TOTAL:02d}", size=10, color=DIM,
             align=PP_ALIGN.RIGHT)
    add_rect(slide, Inches(0.6), Inches(7.0), Inches(12.1), Emu(9525),
             fill=DIM, transparency=0.6)


# ================= 各幻灯片 =================

# ---------- 1. 封面 ----------
def slide_cover():
    s = add_slide()
    set_solid_bg(s, NAVY)
    add_rect(s, 0, 0, Inches(5.2), SH, fill=PURPLE, transparency=0.55)
    add_rect(s, Inches(11.6), 0, Inches(0.18), Inches(2.5), fill=ACCENT)
    add_rect(s, Inches(11.0), Inches(2.5), Inches(0.18), Inches(2),
             fill=PINK)
    starfield(s, count=70, seed=1)

    add_text(s, Inches(0.9), Inches(2.1), Inches(11.5), Inches(1.2),
             "三位科幻大师的", size=46, bold=True, color=WHITE)
    add_text(s, Inches(0.9), Inches(3.0), Inches(11.5), Inches(1.6),
             "「武功秘籍」", size=64, bold=True, color=ACCENT)
    add_text(s, Inches(0.9), Inches(4.85), Inches(11.5), Inches(0.5),
             "刘慈欣  ·  安迪 · 威尔  ·  特德 · 姜",
             size=22, color=CYAN)
    add_rect(s, Inches(0.9), Inches(5.55), Inches(0.7), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.75), Inches(5.35), Inches(10), Inches(0.5),
             "—— 看懂科幻，写出自己的第一个故事",
             size=16, color=LIGHT)
    add_text(s, Inches(0.9), Inches(6.6), Inches(11.5), Inches(0.4),
             "主讲：六年级  ·  深圳    |    时长 ≈ 12 分钟",
             size=12, color=DIM)


# ---------- 2. 三位主角 ----------
def slide_three_authors():
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=30, seed=2)
    page_decor(s, 2, section="开场 · 我们今天要认识谁",
               time_tag="≈ 1 min")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "今天的三位主角", size=34, bold=True, color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "三位站在科幻顶端的「武林高手」",
             size=15, color=LIGHT)

    cards = [
        ("中国", "刘慈欣", "《三体》《流浪地球》",
         "硬核宇宙派", CYAN),
        ("美国", "安迪 · 威尔", "《火星救援》《挽救计划》",
         "理科解谜派", ACCENT),
        ("美籍华裔", "特德 · 姜",
         "《你一生的故事》《呼吸》", "哲思软科幻派", PINK),
    ]
    card_w = Inches(3.9)
    card_h = Inches(4.6)
    gap    = Inches(0.25)
    total_w = card_w * 3 + gap * 2
    start_x = (SW - total_w) // 2
    y = Inches(2.25)

    for i, (tag, name, work, label, col) in enumerate(cards):
        x = start_x + (card_w + gap) * i
        add_round_rect(s, x, y, card_w, card_h, fill=DEEP_BLUE,
                       line=col, line_width=Pt(1.25), corner=0.06)
        add_rect(s, x, y, card_w, Inches(0.18), fill=col)
        ax = x + (card_w - Inches(1.6)) // 2
        add_oval(s, ax, y + Inches(0.55), Inches(1.6), Inches(1.6),
                 fill=PURPLE, line=col, line_width=Pt(1.5))
        add_text(s, ax, y + Inches(0.55), Inches(1.6), Inches(1.6),
                 name[0], size=54, bold=True, color=ACCENT,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, x, y + Inches(2.3), card_w, Inches(0.35),
                 tag, size=11, color=col, align=PP_ALIGN.CENTER,
                 bold=True)
        add_text(s, x, y + Inches(2.65), card_w, Inches(0.6),
                 name, size=26, bold=True, color=WHITE,
                 align=PP_ALIGN.CENTER)
        add_text(s, x, y + Inches(3.3), card_w, Inches(0.35),
                 label, size=13, color=ACCENT,
                 align=PP_ALIGN.CENTER, italic=True)
        add_text(s, x + Inches(0.3), y + Inches(3.75), card_w - Inches(0.6),
                 Inches(0.8), work, size=12, color=LIGHT,
                 align=PP_ALIGN.CENTER, line_spacing=1.4)


# ---------- 3. 三大种类 ----------
def slide_three_types():
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=20, seed=3)
    page_decor(s, 3, section="第一站 · 科幻的三大种类",
               time_tag="≈ 1 min")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "科幻小说的三大种类", size=34, bold=True, color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "硬一点 · 软一点 · 再灾难一点——你最爱哪一种？",
             size=15, color=LIGHT)

    items = [
        ("硬科幻", "科学迷的游乐园",
         "用真实物理 / 化学 / 天文\n一步步算出活路",
         "刘慈欣《三体》水滴\n安迪 · 威尔《火星救援》",
         CYAN, "H"),
        ("软科幻", "情感与哲思的茶馆",
         "科学只是背景\n讲人的感情、选择和命运",
         "特德 · 姜\n《你一生的故事》",
         PINK, "S"),
        ("灾难科幻", "末日生存指南",
         "地球或人类遭遇大麻烦\n看人怎么靠智慧团结活下去",
         "刘慈欣《流浪地球》《三体》",
         ACCENT, "D"),
    ]
    card_w = Inches(3.9)
    card_h = Inches(4.6)
    gap    = Inches(0.25)
    total_w = card_w * 3 + gap * 2
    start_x = (SW - total_w) // 2
    y = Inches(2.2)

    for i, (name, sub, desc, ex, col, mark) in enumerate(items):
        x = start_x + (card_w + gap) * i
        add_round_rect(s, x, y, card_w, card_h, fill=DEEP_BLUE,
                       line=col, line_width=Pt(1.25), corner=0.05)
        add_text(s, x + Inches(0.4), y + Inches(0.3), Inches(1.2),
                 Inches(1.2), mark, size=68, bold=True, color=col,
                 font=EN_FONT)
        add_text(s, x + Inches(0.4), y + Inches(1.55),
                 card_w - Inches(0.8), Inches(0.7), name,
                 size=28, bold=True, color=WHITE)
        add_text(s, x + Inches(0.4), y + Inches(2.2),
                 card_w - Inches(0.8), Inches(0.4), sub,
                 size=14, color=col, italic=True)
        add_rect(s, x + Inches(0.4), y + Inches(2.65), Inches(1),
                 Emu(19050), fill=col)
        add_text(s, x + Inches(0.4), y + Inches(2.85),
                 card_w - Inches(0.8), Inches(1.0), desc,
                 size=13, color=LIGHT, line_spacing=1.5)
        add_text(s, x + Inches(0.4), y + Inches(3.85),
                 card_w - Inches(0.8), Inches(0.3),
                 "代表作品", size=10, color=DIM, bold=True)
        add_text(s, x + Inches(0.4), y + Inches(4.1),
                 card_w - Inches(0.8), Inches(0.5), ex,
                 size=12, color=ACCENT, bold=True, line_spacing=1.35)

    add_text(s, Inches(0.9), Inches(6.95), Inches(12), Inches(0.4),
             "★  小提醒：很多书是混搭的——但最打动人的，永远是「人」",
             size=12, color=ACCENT, italic=True)


# ---------- 4. 故事四块积木 ----------
def slide_structure():
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=20, seed=4)
    page_decor(s, 4, section="第二站 · 故事的骨架",
               time_tag="≈ 1 min")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "科幻故事的「四块积木」", size=34, bold=True, color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "几乎每一个科幻故事，都由这四块拼成（以《火星救援》为例）",
             size=15, color=LIGHT)

    blocks = [
        ("一个假设", "如果……会怎样？",
         "如果一个人被独自丢在火星？", CYAN, "?"),
        ("一个麻烦", "假设带来的大问题",
         "食物撑不到救援，无法和地球联系。", PINK, "!"),
        ("一个英雄", "不一定有超能力，\n但一定要动脑子",
         "宇航员马克——一位植物学专家。", ACCENT, "★"),
        ("一个结局", "问题解决了吗？",
         "成功获救：科学计算 + 一点运气。", CYAN, "✓"),
    ]
    card_w = Inches(2.95)
    card_h = Inches(4.6)
    gap    = Inches(0.18)
    total_w = card_w * 4 + gap * 3
    start_x = (SW - total_w) // 2
    y = Inches(2.2)

    for i, (name, sub, ex, col, mark) in enumerate(blocks):
        x = start_x + (card_w + gap) * i
        add_round_rect(s, x, y, card_w, card_h, fill=DEEP_BLUE,
                       line=col, line_width=Pt(1.25), corner=0.06)
        add_oval(s, x + Inches(0.3), y + Inches(0.3), Inches(0.7),
                 Inches(0.7), fill=col)
        add_text(s, x + Inches(0.3), y + Inches(0.3), Inches(0.7),
                 Inches(0.7), str(i + 1), size=20, bold=True, color=NAVY,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=EN_FONT)
        add_text(s, x + Inches(1.1), y + Inches(0.25), Inches(1.5),
                 Inches(0.85), mark, size=46, bold=True, color=col,
                 font=EN_FONT)
        add_text(s, x + Inches(0.3), y + Inches(1.3), card_w - Inches(0.6),
                 Inches(0.7), name, size=24, bold=True, color=WHITE)
        add_text(s, x + Inches(0.3), y + Inches(2.05),
                 card_w - Inches(0.6), Inches(0.9), sub, size=14,
                 color=col, italic=True, line_spacing=1.4)
        add_rect(s, x + Inches(0.3), y + Inches(3.0), Inches(1),
                 Emu(19050), fill=col)
        add_text(s, x + Inches(0.3), y + Inches(3.15),
                 card_w - Inches(0.6), Inches(0.35),
                 "《火星救援》中", size=11, color=DIM, bold=True)
        add_text(s, x + Inches(0.3), y + Inches(3.45),
                 card_w - Inches(0.6), Inches(1.1), ex, size=13,
                 color=LIGHT, line_spacing=1.45)


# ---------- 5/6/7. 大师设定页（精简版，每人 2 个最经典设定） ----------
def slide_settings(page, name, tag, color, items, section_no):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=18, seed=10 + section_no)
    page_decor(s, page,
               section=f"第三站 · 拍大腿的设定 · {section_no}/3",
               time_tag="≈ 1 min")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             f"{name} 的「世界观工具箱」", size=30, bold=True,
             color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=color)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             tag, size=14, color=LIGHT, italic=True)

    # 每人 2 张大卡，左右排
    cy = Inches(2.3)
    cw = Inches(5.85)
    ch = Inches(4.55)
    for i, (title, body) in enumerate(items[:2]):
        x = Inches(0.9) + (cw + Inches(0.25)) * i
        add_round_rect(s, x, cy, cw, ch, fill=DEEP_BLUE, line=color,
                       line_width=Pt(1), corner=0.04)
        add_text(s, x + Inches(0.35), cy + Inches(0.3), Inches(2),
                 Inches(0.5), f"设定 0{i + 1}",
                 size=12, color=color, bold=True)
        add_text(s, x + Inches(0.35), cy + Inches(0.7),
                 cw - Inches(0.7), Inches(1.0), title,
                 size=20, bold=True, color=ACCENT, line_spacing=1.3)
        add_rect(s, x + Inches(0.35), cy + Inches(2.0),
                 Inches(1), Emu(19050), fill=color)
        add_text(s, x + Inches(0.35), cy + Inches(2.2),
                 cw - Inches(0.7), Inches(2.2), body,
                 size=14, color=LIGHT, line_spacing=1.6)


# ---------- 8. 三条秘诀总览 ----------
def slide_secrets_overview():
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=25, seed=20)
    page_decor(s, 8, section="第四站 · 三条写作秘诀 · 总览",
               time_tag="≈ 1 min")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "三位大师的「独门武功」", size=34, bold=True, color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "每一招都简单到——你今晚就能写一段试试看",
             size=15, color=LIGHT)

    secrets = [
        ("秘诀 ①", "刘慈欣", "追问「然后呢？」",
         "从一个巨大的「如果」开始，\n往下连追三步。", CYAN),
        ("秘诀 ②", "安迪 · 威尔", "让主角列清单",
         "把困境拆成「我有 / 我缺 / 怎么补」，\n一步一步算出来。",
         ACCENT),
        ("秘诀 ③", "特德 · 姜", "从一道选择题出发",
         "先想一个关于人的哲学问题，\n再让科幻设定服务它。",
         PINK),
    ]
    card_w = Inches(3.9)
    card_h = Inches(4.7)
    gap    = Inches(0.25)
    total_w = card_w * 3 + gap * 2
    start_x = (SW - total_w) // 2
    y = Inches(2.2)

    for i, (no, name, key, desc, col) in enumerate(secrets):
        x = start_x + (card_w + gap) * i
        add_round_rect(s, x, y, card_w, card_h, fill=DEEP_BLUE,
                       line=col, line_width=Pt(1.25), corner=0.05)
        add_rect(s, x, y, card_w, Inches(0.18), fill=col)
        add_text(s, x + Inches(0.4), y + Inches(0.4), card_w - Inches(0.8),
                 Inches(0.5), no, size=14, color=col, bold=True)
        add_text(s, x + Inches(0.4), y + Inches(0.85),
                 card_w - Inches(0.8), Inches(0.7), name,
                 size=24, bold=True, color=WHITE)
        add_text(s, x + Inches(0.4), y + Inches(1.85),
                 card_w - Inches(0.8), Inches(1.4), key,
                 size=22, bold=True, color=ACCENT, line_spacing=1.3)
        add_rect(s, x + Inches(0.4), y + Inches(3.25), Inches(1.0),
                 Emu(19050), fill=col)
        add_text(s, x + Inches(0.4), y + Inches(3.45),
                 card_w - Inches(0.8), Inches(1.2), desc,
                 size=14, color=LIGHT, line_spacing=1.5)


# ---------- 9. 秘诀① 刘慈欣（含演示）----------
def slide_secret_liu():
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=20, seed=21)
    page_decor(s, 9, section="第四站 · 秘诀 ①",
               time_tag="≈ 1 min")

    # 顶部
    add_text(s, Inches(0.9), Inches(0.7), Inches(2), Inches(1.2),
             "01", size=90, bold=True, color=CYAN, font=EN_FONT)
    add_text(s, Inches(2.4), Inches(1.0), Inches(11), Inches(0.5),
             "秘诀 ① · 刘慈欣", size=14, color=DIM, bold=True)
    add_text(s, Inches(2.4), Inches(1.3), Inches(11), Inches(0.85),
             "从一个「如果」往下推三步",
             size=30, bold=True, color=WHITE)

    # 左：方法
    add_round_rect(s, Inches(0.9), Inches(2.7), Inches(5.85), Inches(4.15),
                   fill=PURPLE, line=ACCENT, line_width=Pt(1.25),
                   corner=0.04)
    add_text(s, Inches(1.15), Inches(2.9), Inches(5.5), Inches(0.4),
             "方法", size=14, color=ACCENT, bold=True)
    add_text(s, Inches(1.15), Inches(3.25), Inches(5.5), Inches(0.6),
             "「如果……」+ 连追 3 次「然后呢？」",
             size=20, bold=True, color=WHITE)
    add_text(s, Inches(1.15), Inches(4.2), Inches(5.5), Inches(2.7),
             "Step 1.  写一句  「如果……」\n"
             "Step 2.  问  「然后呢？」\n"
             "Step 3.  再问  「然后呢？」\n"
             "Step 4.  再问  「然后呢？」\n\n"
             "三次之后，一个完整故事就长出来了。",
             size=14, color=LIGHT, line_spacing=1.7)

    # 右：现场演示
    add_round_rect(s, Inches(7.0), Inches(2.7), Inches(5.85), Inches(4.15),
                   fill=DEEP_BLUE, line=CYAN, line_width=Pt(1),
                   corner=0.04)
    add_text(s, Inches(7.25), Inches(2.9), Inches(5.5), Inches(0.4),
             "现场演示", size=14, color=CYAN, bold=True)
    add_text(s, Inches(7.25), Inches(3.25), Inches(5.5), Inches(0.6),
             "如果学校可以漂浮在空中？",
             size=18, bold=True, color=ACCENT)
    add_rich_text(s, Inches(7.25), Inches(4.0), Inches(5.5), Inches(2.85),
                  [
                      [("→ 然后呢？  ",
                        {"size": 14, "color": CYAN, "bold": True}),
                       ("上学要坐飞行器。",
                        {"size": 14, "color": LIGHT})],
                      [("", {"size": 6, "color": WHITE})],
                      [("→ 然后呢？  ",
                        {"size": 14, "color": CYAN, "bold": True}),
                       ("飞行器没油了。",
                        {"size": 14, "color": LIGHT})],
                      [("", {"size": 6, "color": WHITE})],
                      [("→ 然后呢？  ",
                        {"size": 14, "color": CYAN, "bold": True}),
                       ("主角用太阳能板充电，",
                        {"size": 14, "color": LIGHT})],
                      [("                  ",
                        {"size": 14, "color": LIGHT}),
                       ("差点迟到，却写出了一首歌。",
                        {"size": 14, "color": LIGHT})],
                  ], line_spacing=1.5)


# ---------- 10. 秘诀② 安迪·威尔 ----------
def slide_secret_weir():
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=20, seed=22)
    page_decor(s, 10, section="第四站 · 秘诀 ②",
               time_tag="≈ 1 min")

    add_text(s, Inches(0.9), Inches(0.7), Inches(2), Inches(1.2),
             "02", size=90, bold=True, color=ACCENT, font=EN_FONT)
    add_text(s, Inches(2.4), Inches(1.0), Inches(11), Inches(0.5),
             "秘诀 ② · 安迪 · 威尔", size=14, color=DIM, bold=True)
    add_text(s, Inches(2.4), Inches(1.3), Inches(11), Inches(0.85),
             "让主角「列清单」解决问题",
             size=30, bold=True, color=WHITE)

    # 左：方法
    add_round_rect(s, Inches(0.9), Inches(2.7), Inches(5.85), Inches(4.15),
                   fill=PURPLE, line=ACCENT, line_width=Pt(1.25),
                   corner=0.04)
    add_text(s, Inches(1.15), Inches(2.9), Inches(5.5), Inches(0.4),
             "方法", size=14, color=ACCENT, bold=True)
    add_text(s, Inches(1.15), Inches(3.25), Inches(5.5), Inches(0.6),
             "把困境拆成 3 行清单",
             size=20, bold=True, color=WHITE)
    add_rich_text(s, Inches(1.15), Inches(4.15), Inches(5.5), Inches(2.7),
                  [
                      [("我有：",
                        {"size": 16, "color": CYAN, "bold": True}),
                       ("当下能用的资源",
                        {"size": 14, "color": LIGHT})],
                      [("", {"size": 6, "color": WHITE})],
                      [("我缺：",
                        {"size": 16, "color": PINK, "bold": True}),
                       ("活下去必需的东西",
                        {"size": 14, "color": LIGHT})],
                      [("", {"size": 6, "color": WHITE})],
                      [("怎么补：",
                        {"size": 16, "color": ACCENT, "bold": True}),
                       ("一条一条可执行的计划",
                        {"size": 14, "color": LIGHT})],
                      [("", {"size": 8, "color": WHITE})],
                      [("清单写完，故事就往前走了。",
                        {"size": 13, "color": ACCENT, "italic": True})],
                  ], line_spacing=1.5)

    # 右：荒岛求生清单
    add_round_rect(s, Inches(7.0), Inches(2.7), Inches(5.85), Inches(4.15),
                   fill=WHITE, line=ACCENT, line_width=Pt(1.25),
                   corner=0.03)
    add_rect(s, Inches(7.0), Inches(2.7), Inches(5.85), Inches(0.4),
             fill=ACCENT)
    add_text(s, Inches(7.0), Inches(2.7), Inches(5.85), Inches(0.4),
             "  小  明  的  笔  记  本", size=14, color=NAVY, bold=True,
             anchor=MSO_ANCHOR.MIDDLE)
    add_rich_text(s, Inches(7.3), Inches(3.3), Inches(5.3), Inches(3.45),
                  [
                      [("我有：",
                        {"size": 15, "color": CYAN, "bold": True}),
                       ("小刀  ·  塑料瓶  ·  半包饼干",
                        {"size": 14, "color": NAVY})],
                      [("", {"size": 6, "color": NAVY})],
                      [("我缺：",
                        {"size": 15, "color": PINK, "bold": True}),
                       ("水  ·  火  ·  能睡觉的地方",
                        {"size": 14, "color": NAVY})],
                      [("", {"size": 6, "color": NAVY})],
                      [("计划：",
                        {"size": 15, "color": PURPLE, "bold": True})],
                      [("  ① ",
                        {"size": 14, "color": ACCENT, "bold": True}),
                       ("用塑料瓶蒸馏海水",
                        {"size": 14, "color": NAVY})],
                      [("  ② ",
                        {"size": 14, "color": ACCENT, "bold": True}),
                       ("用小刀钻木取火",
                        {"size": 14, "color": NAVY})],
                      [("  ③ ",
                        {"size": 14, "color": ACCENT, "bold": True}),
                       ("用树枝搭一个挡风的小棚",
                        {"size": 14, "color": NAVY})],
                  ], line_spacing=1.4)


# ---------- 11. 秘诀③ 特德·姜 ----------
def slide_secret_chiang():
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=20, seed=23)
    page_decor(s, 11, section="第四站 · 秘诀 ③",
               time_tag="≈ 1 min")

    add_text(s, Inches(0.9), Inches(0.7), Inches(2), Inches(1.2),
             "03", size=90, bold=True, color=PINK, font=EN_FONT)
    add_text(s, Inches(2.4), Inches(1.0), Inches(11), Inches(0.5),
             "秘诀 ③ · 特德 · 姜", size=14, color=DIM, bold=True)
    add_text(s, Inches(2.4), Inches(1.3), Inches(11), Inches(0.85),
             "用一个「人生选择题」做设定",
             size=30, bold=True, color=WHITE)

    # 左：方法
    add_round_rect(s, Inches(0.9), Inches(2.7), Inches(5.85), Inches(4.15),
                   fill=PURPLE, line=ACCENT, line_width=Pt(1.25),
                   corner=0.04)
    add_text(s, Inches(1.15), Inches(2.9), Inches(5.5), Inches(0.4),
             "方法", size=14, color=ACCENT, bold=True)
    add_text(s, Inches(1.15), Inches(3.25), Inches(5.5), Inches(0.6),
             "先想题，再造世界",
             size=20, bold=True, color=WHITE)
    add_text(s, Inches(1.15), Inches(4.0), Inches(5.5), Inches(2.85),
             "Step 1.  写一道你最纠结的人生选择题\n\n"
             "Step 2.  设计一个能逼出这个选择的设定\n\n"
             "Step 3.  让主角在这道题里挣扎、流泪、\n"
             "             最后做出选择\n\n"
             "不必爆炸——光是「想用又不敢用」，\n就足够动人。",
             size=13, color=LIGHT, line_spacing=1.55)

    # 右：三道题
    add_round_rect(s, Inches(7.0), Inches(2.7), Inches(5.85), Inches(4.15),
                   fill=DEEP_BLUE, line=PINK, line_width=Pt(1),
                   corner=0.04)
    add_text(s, Inches(7.25), Inches(2.9), Inches(5.5), Inches(0.4),
             "三道题，挑一道写下去", size=14, color=PINK, bold=True)

    qs = [
        ("Q1", "如果有一台机器能消除你伤心的记忆，\n你会按下按钮吗？", CYAN),
        ("Q2", "如果你能提前看到期末考试成绩，\n你会告诉好朋友吗？", ACCENT),
        ("Q3", "如果你知道好朋友将来会背叛你，\n你现在还跟他玩吗？", PINK),
    ]
    qy = Inches(3.4)
    qh = Inches(1.05)
    for i, (no, body, col) in enumerate(qs):
        y = qy + qh * i + Inches(0.05) * i
        add_oval(s, Inches(7.4), y + Inches(0.18), Inches(0.6),
                 Inches(0.6), fill=col)
        add_text(s, Inches(7.4), y + Inches(0.18), Inches(0.6),
                 Inches(0.6), no, size=12, bold=True, color=NAVY,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=EN_FONT)
        add_text(s, Inches(8.15), y, Inches(4.6), qh, body,
                 size=13, color=LIGHT, line_spacing=1.45,
                 anchor=MSO_ANCHOR.MIDDLE)


# ---------- 12. 总结 + 行动号召 ----------
def slide_summary_cta():
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=30, seed=30)
    page_decor(s, 12, section="结尾 · 把今天装进口袋",
               time_tag="≈ 1 min")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "三句话带回家  +  现在轮到你",
             size=32, bold=True, color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "今天的全部，都浓缩在下面这一页里",
             size=15, color=LIGHT)

    # 上半区：三句话总结
    items = [
        ("刘慈欣", "从一个「如果」连追三步「然后呢？」", CYAN),
        ("安迪 · 威尔", "让主角拿出本子，列一份清单", ACCENT),
        ("特德 · 姜", "先写一道选择题，再造一个世界", PINK),
    ]
    y0 = Inches(2.25)
    rh = Inches(0.85)
    for i, (name, line, col) in enumerate(items):
        y = y0 + rh * i + Inches(0.08) * i
        add_round_rect(s, Inches(0.9), y, Inches(11.5), rh,
                       fill=DEEP_BLUE, line=col, line_width=Pt(0.75),
                       corner=0.15)
        add_rect(s, Inches(0.9), y, Inches(0.18), rh, fill=col)
        add_text(s, Inches(1.3), y, Inches(2.8), rh, name,
                 size=18, bold=True, color=ACCENT,
                 anchor=MSO_ANCHOR.MIDDLE)
        add_text(s, Inches(4.1), y, Inches(8.2), rh, line,
                 size=15, color=LIGHT, anchor=MSO_ANCHOR.MIDDLE)

    # 下半区：三步行动
    cta_y = Inches(5.25)
    add_text(s, Inches(0.9), cta_y, Inches(12), Inches(0.4),
             "现在轮到你——回家做一件事",
             size=15, color=ACCENT, bold=True)

    steps = [
        ("STEP 1", "选 1 个秘诀", CYAN),
        ("STEP 2", "选 1 个设定", ACCENT),
        ("STEP 3", "写下 200 字", PINK),
    ]
    sw = Inches(3.85)
    sh_ = Inches(1.0)
    sgap = Inches(0.2)
    sx0 = (SW - (sw * 3 + sgap * 2)) // 2
    sy = Inches(5.7)
    for i, (no, t, col) in enumerate(steps):
        x = sx0 + (sw + sgap) * i
        add_round_rect(s, x, sy, sw, sh_, fill=DEEP_BLUE, line=col,
                       line_width=Pt(1), corner=0.2)
        add_text(s, x + Inches(0.3), sy, Inches(1.6), sh_, no,
                 size=15, color=col, bold=True, font=EN_FONT,
                 anchor=MSO_ANCHOR.MIDDLE)
        # 竖线
        add_rect(s, x + Inches(1.55), sy + Inches(0.2), Emu(15000),
                 sh_ - Inches(0.4), fill=col)
        add_text(s, x + Inches(1.75), sy, sw - Inches(1.85), sh_, t,
                 size=17, color=WHITE, bold=True,
                 anchor=MSO_ANCHOR.MIDDLE)

    add_text(s, Inches(0.9), Inches(6.95), Inches(12), Inches(0.4),
             "★  科幻不是胡思乱想，而是「有逻辑地，做一场好梦」",
             size=13, color=ACCENT, italic=True, align=PP_ALIGN.CENTER)


# ---------- 13. 谢谢 ----------
def slide_thanks():
    s = add_slide()
    set_solid_bg(s, NAVY)
    add_rect(s, 0, 0, SW, SH, fill=PURPLE, transparency=0.55)
    starfield(s, count=100, seed=99)
    page_decor(s, 13, section="The End")

    add_text(s, Inches(0.9), Inches(2.0), Inches(11.5), Inches(1.6),
             "THANK YOU", size=110, bold=True, color=ACCENT,
             align=PP_ALIGN.CENTER, font=EN_FONT)
    add_text(s, Inches(0.9), Inches(3.6), Inches(11.5), Inches(0.8),
             "谢   谢   大   家", size=34, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER)
    add_rect(s, Inches(6.27), Inches(4.55), Inches(0.8), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(0.9), Inches(4.85), Inches(11.5), Inches(0.6),
             "愿你也能，写出属于自己的星辰大海",
             size=18, color=LIGHT, italic=True, align=PP_ALIGN.CENTER)
    add_text(s, Inches(0.9), Inches(5.95), Inches(11.5), Inches(0.5),
             "致敬   ·   刘慈欣   ·   安迪 · 威尔   ·   特德 · 姜",
             size=14, color=DIM, align=PP_ALIGN.CENTER)


# ================= 主流程 =================

LIU_SETTINGS = [
    ("黑暗森林法则（《三体》）",
     "宇宙像一片黑暗的森林，每个文明都是带枪的猎人——\n"
     "谁先暴露，谁就被消灭。\n\n"
     "读完之后，你也许会忍不住，抬头看一眼窗外的星空。"),
    ("思想钢印（《三体》）",
     "给士兵注入一种东西，让他坚信「人类必胜」。\n"
     "哪怕面对必败的敌人，他也会冲锋。\n\n"
     "刘慈欣问你：如果活下去需要自我欺骗，你愿意吗？"),
]
WEIR_SETTINGS = [
    ("火星种土豆（《火星救援》）",
     "一个人，用粪便当肥料，用火箭燃料造水，\n"
     "在火星大棚里，种出了能救自己命的土豆。\n\n"
     "这不是魔法——是一道道步步可算的科学题。"),
    ("跨物种语言破译（《挽救计划》）",
     "人类遇到外星蜘蛛「洛基」，对方只会「敲—敲—敲」。\n"
     "主角用质数数列当翻译机，硬是从零开始学会了交流。\n\n"
     "★ 我超爱这个设定——科学，能让两个完全不同的生灵成为朋友。"),
]
CHIANG_SETTINGS = [
    ("预知未来的语言（《你一生的故事》）",
     "学会外星人的语言后，你的思维方式会改变，\n"
     "能同时看见过去与未来。\n\n"
     "你知道女儿会怎样离开，却仍然，选择把她生下来。"),
    ("宇宙的呼吸（《呼吸》）",
     "在一个靠气压驱动的世界，主人公发现——\n"
     "宇宙的气压正在均匀，万物终将归于寂静。\n\n"
     "他平静地写下这一切，像是在与世界温柔告别。"),
]


def main():
    slide_cover()                                                   # 1
    slide_three_authors()                                           # 2
    slide_three_types()                                             # 3
    slide_structure()                                               # 4
    slide_settings(5, "刘慈欣",
                   "硬核宇宙派 · 一个设定，世界观秒变",
                   CYAN, LIU_SETTINGS, 1)                           # 5
    slide_settings(6, "安迪 · 威尔",
                   "理科解谜派 · 用真实科学撑起每一步",
                   ACCENT, WEIR_SETTINGS, 2)                        # 6
    slide_settings(7, "特德 · 姜",
                   "哲思软科幻派 · 不爆炸，但让你想很久",
                   PINK, CHIANG_SETTINGS, 3)                        # 7
    slide_secrets_overview()                                        # 8
    slide_secret_liu()                                              # 9
    slide_secret_weir()                                             # 10
    slide_secret_chiang()                                           # 11
    slide_summary_cta()                                             # 12
    slide_thanks()                                                  # 13

    out = "/projects/sandbox/kiro2026/三位科幻大师的武功秘籍.pptx"
    prs.save(out)
    print(f"OK -> {out}  ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
