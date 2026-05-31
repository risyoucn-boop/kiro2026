# -*- coding: utf-8 -*-
"""
生成《三位科幻大师的"武功秘籍"》演讲 PPT
适合深圳小学六年级学生上台演讲使用
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

# ================= 主题色 =================
NAVY      = RGBColor(0x0B, 0x1A, 0x3A)   # 深空蓝（主背景）
DEEP_BLUE = RGBColor(0x10, 0x25, 0x4F)   # 星云深蓝
PURPLE    = RGBColor(0x3B, 0x1E, 0x6E)   # 星云紫
ACCENT    = RGBColor(0xF2, 0xC9, 0x4C)   # 星辰金（强调色）
PINK      = RGBColor(0xE9, 0x4B, 0x7B)   # 霓虹粉（强调色2）
CYAN      = RGBColor(0x4B, 0xC8, 0xE9)   # 等离子青
WHITE     = RGBColor(0xF5, 0xF7, 0xFA)   # 云白
LIGHT     = RGBColor(0xCB, 0xD5, 0xE0)   # 浅灰
DIM       = RGBColor(0x8A, 0x99, 0xB3)   # 暗灰蓝

CN_FONT   = "Microsoft YaHei"
CN_BOLD   = "Microsoft YaHei"
EN_FONT   = "Calibri"



# ================= 演示文稿初始化 =================
prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]  # 空白版式


# ================= 工具函数 =================

def add_slide():
    return prs.slides.add_slide(BLANK)


def set_solid_bg(slide, rgb):
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SW, SH)
    bg.line.fill.background()
    bg.fill.solid()
    bg.fill.fore_color.rgb = rgb
    bg.shadow.inherit = False
    # 移到最底
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
            # 设置填充透明度
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
    # 调整圆角
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


def add_line(slide, x1, y1, x2, y2, color, width=1.5):
    line = slide.shapes.add_connector(1, x1, y1, x2, y2)
    line.line.color.rgb = color
    line.line.width = Pt(width)
    return line


def add_text(slide, x, y, w, h, text, *, size=18, color=WHITE, bold=False,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font=CN_FONT,
             italic=False, line_spacing=1.25):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.word_wrap = True
    tf.vertical_anchor = anchor

    if isinstance(text, str):
        lines = text.split("\n")
    else:
        lines = list(text)

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
        # 中文字体
        rPr = run._r.get_or_add_rPr()
        ea = rPr.find(qn('a:ea'))
        if ea is None:
            ea = etree.SubElement(rPr, qn('a:ea'))
        ea.set('typeface', font)
    return tb


def add_rich_text(slide, x, y, w, h, runs, *, align=PP_ALIGN.LEFT,
                  anchor=MSO_ANCHOR.TOP, line_spacing=1.3):
    """runs: list of list of (text, dict). 每个外层 list 是一行；
    每个内层 list 是这一行的多段 run，run = (text, opts)。
    opts: size, color, bold, italic, font
    """
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
    """画一些点状星星作为背景装饰"""
    import random
    rnd = random.Random(seed)
    for _ in range(count):
        x = Emu(int(rnd.random() * SW))
        y = Emu(int(rnd.random() * SH * 0.95))
        r = rnd.choice([1, 1, 1, 2, 2, 3])
        size = Emu(int(r * 30000))
        dot = add_oval(slide, x, y, size, size, fill=WHITE)
        # 调整透明度
        sp = dot.fill.fore_color._xFill
        srgb = sp.find(qn('a:srgbClr'))
        if srgb is not None:
            alpha = etree.SubElement(srgb, qn('a:alpha'))
            alpha.set('val', str(rnd.choice([25000, 40000, 55000, 75000])))


def page_decor(slide, page_no, total, section=None):
    """页脚装饰：金色细线 + 页码 + 章节标识"""
    # 顶部金色短线
    add_rect(slide, Inches(0.6), Inches(0.45), Inches(0.5), Emu(38100),
             fill=ACCENT)
    if section:
        add_text(slide, Inches(1.2), Inches(0.32), Inches(8), Inches(0.4),
                 section, size=11, color=ACCENT, bold=True,
                 anchor=MSO_ANCHOR.MIDDLE)
    # 页码
    add_text(slide, Inches(11.5), Inches(7.05), Inches(1.5), Inches(0.3),
             f"{page_no:02d} / {total:02d}", size=10, color=DIM,
             align=PP_ALIGN.RIGHT)
    # 底部细线
    add_rect(slide, Inches(0.6), Inches(7.0), Inches(12.1), Emu(9525),
             fill=DIM, transparency=0.6)



# ================= 幻灯片构建 =================

TOTAL = 27  # 预计总页数（结尾会校对）

# ---------- Slide 1: 封面 ----------
def slide_cover():
    s = add_slide()
    set_solid_bg(s, NAVY)

    # 左侧紫色色块
    add_rect(s, 0, 0, Inches(5.2), SH, fill=PURPLE, transparency=0.55)
    # 右上金色装饰条
    add_rect(s, Inches(11.6), Inches(0), Inches(0.18), Inches(2.5),
             fill=ACCENT)
    add_rect(s, Inches(11.0), Inches(2.5), Inches(0.18), Inches(2),
             fill=PINK)

    starfield(s, count=70, seed=1)

    # 大标题
    add_text(s, Inches(0.9), Inches(2.3), Inches(11.5), Inches(1.2),
             "三位科幻大师的", size=46, bold=True, color=WHITE,
             font=CN_BOLD)
    add_rich_text(s, Inches(0.9), Inches(3.2), Inches(11.5), Inches(1.6),
                  [[("「", {"size": 64, "color": ACCENT, "bold": True}),
                    ("武功秘籍", {"size": 64, "color": ACCENT, "bold": True}),
                    ("」", {"size": 64, "color": ACCENT, "bold": True})]])

    # 副标题
    add_text(s, Inches(0.9), Inches(5.0), Inches(11.5), Inches(0.5),
             "刘慈欣  ·  安迪 · 威尔  ·  特德 · 姜",
             size=22, color=CYAN, bold=False)

    # 装饰短线
    add_rect(s, Inches(0.9), Inches(5.7), Inches(0.7), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.75), Inches(5.5), Inches(10), Inches(0.5),
             "—— 看懂科幻，写出自己的第一个故事",
             size=16, color=LIGHT)

    # 底部讲者信息
    add_text(s, Inches(0.9), Inches(6.6), Inches(11.5), Inches(0.4),
             "主讲：六年级  ·  深圳", size=12, color=DIM)


# ---------- Slide 2: 三位嘉宾介绍 ----------
def slide_three_authors(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=30, seed=2)
    page_decor(s, page, TOTAL, section="开场 · 我们今天要认识谁")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "今天的三位主角", size=34, bold=True, color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "三位站在科幻顶端的「武林高手」", size=15, color=LIGHT)

    cards = [
        {
            "tag": "中国",
            "name": "刘慈欣",
            "work": "《三体》《流浪地球》《球状闪电》",
            "label": "硬核宇宙派",
            "color": CYAN,
        },
        {
            "tag": "美国",
            "name": "安迪 · 威尔",
            "work": "《火星救援》《挽救计划》",
            "label": "理科解谜派",
            "color": ACCENT,
        },
        {
            "tag": "美籍华裔",
            "name": "特德 · 姜",
            "work": "《你一生的故事》《呼吸》《巴比伦塔》",
            "label": "哲思软科幻派",
            "color": PINK,
        },
    ]
    card_w = Inches(3.9)
    card_h = Inches(4.6)
    gap    = Inches(0.25)
    total_w = card_w * 3 + gap * 2
    start_x = (SW - total_w) // 2
    y = Inches(2.2)

    for i, c in enumerate(cards):
        x = start_x + (card_w + gap) * i
        # 卡片底
        add_round_rect(s, x, y, card_w, card_h, fill=DEEP_BLUE,
                       line=c["color"], line_width=Pt(1.25), corner=0.06)
        # 顶部色条
        add_rect(s, x, y, card_w, Inches(0.18), fill=c["color"])
        # 圆形头像占位
        ax = x + (card_w - Inches(1.6)) // 2
        add_oval(s, ax, y + Inches(0.55), Inches(1.6), Inches(1.6),
                 fill=PURPLE, line=c["color"], line_width=Pt(1.5))
        # 姓氏首字
        first = c["name"][0]
        add_text(s, ax, y + Inches(0.55), Inches(1.6), Inches(1.6),
                 first, size=54, bold=True, color=ACCENT,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        # 国籍标签
        add_text(s, x, y + Inches(2.3), card_w, Inches(0.35),
                 c["tag"], size=11, color=c["color"],
                 align=PP_ALIGN.CENTER, bold=True)
        # 名字
        add_text(s, x, y + Inches(2.65), card_w, Inches(0.6),
                 c["name"], size=26, bold=True, color=WHITE,
                 align=PP_ALIGN.CENTER)
        # 流派标签
        add_text(s, x, y + Inches(3.3), card_w, Inches(0.35),
                 c["label"], size=13, color=ACCENT,
                 align=PP_ALIGN.CENTER, italic=True)
        # 代表作
        add_text(s, x + Inches(0.3), y + Inches(3.75), card_w - Inches(0.6),
                 Inches(0.8), c["work"], size=12, color=LIGHT,
                 align=PP_ALIGN.CENTER, line_spacing=1.4)



# ---------- Slide 3: 目录 ----------
def slide_agenda(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=20, seed=3)
    page_decor(s, page, TOTAL, section="目录 · 今天聊什么")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "我们的飞行路线", size=34, bold=True, color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "听完之后，你也能写出自己的第一个科幻段落",
             size=15, color=LIGHT)

    # 两大模块
    mods = [
        {
            "no": "PART 01",
            "title": "科幻小说说明书",
            "items": [
                "1.  科幻小说的三大种类",
                "2.  故事的四块积木",
                "3.  让人拍大腿的有趣设定",
            ],
            "color": CYAN,
        },
        {
            "no": "PART 02",
            "title": "三位大师的写作秘诀",
            "items": [
                "1.  刘慈欣  ——  追问「然后呢？」",
                "2.  安迪 · 威尔  ——  让主角列清单",
                "3.  特德 · 姜  ——  从一道人生选择题出发",
            ],
            "color": ACCENT,
        },
    ]
    card_w = Inches(5.7)
    card_h = Inches(4.4)
    gap    = Inches(0.4)
    total_w = card_w * 2 + gap
    start_x = (SW - total_w) // 2
    y = Inches(2.3)

    for i, m in enumerate(mods):
        x = start_x + (card_w + gap) * i
        add_round_rect(s, x, y, card_w, card_h, fill=DEEP_BLUE,
                       line=m["color"], line_width=Pt(1.25), corner=0.05)
        # 编号
        add_text(s, x + Inches(0.5), y + Inches(0.4), Inches(3),
                 Inches(0.5), m["no"], size=14, color=m["color"],
                 bold=True)
        # 标题
        add_text(s, x + Inches(0.5), y + Inches(0.85), card_w - Inches(1),
                 Inches(0.8), m["title"], size=28, bold=True, color=WHITE)
        # 横线
        add_rect(s, x + Inches(0.5), y + Inches(1.85), Inches(1.2),
                 Emu(28575), fill=m["color"])
        # 列表
        for j, it in enumerate(m["items"]):
            add_text(s, x + Inches(0.5), y + Inches(2.15) + Inches(0.6) * j,
                     card_w - Inches(1), Inches(0.55),
                     it, size=15, color=LIGHT, line_spacing=1.3)


# ---------- Slide 4: PART 1 章节封面 ----------
def slide_part_cover(page, part_no, kicker, title, subtitle, accent_color):
    s = add_slide()
    set_solid_bg(s, NAVY)
    # 全屏紫色叠层
    add_rect(s, 0, 0, SW, SH, fill=PURPLE, transparency=0.6)
    starfield(s, count=80, seed=10 + part_no)

    # 大号 PART 编号
    add_text(s, Inches(0.9), Inches(1.5), Inches(8), Inches(2.2),
             f"PART {part_no:02d}", size=160, bold=True, color=ACCENT,
             font=EN_FONT)
    # kicker
    add_text(s, Inches(1.0), Inches(3.55), Inches(11), Inches(0.5),
             kicker, size=16, color=accent_color, bold=True)
    # 主标题
    add_text(s, Inches(0.9), Inches(4.05), Inches(11.5), Inches(1.0),
             title, size=52, bold=True, color=WHITE)
    # 副标题
    add_rect(s, Inches(0.95), Inches(5.25), Inches(0.5), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.55), Inches(5.1), Inches(11), Inches(0.5),
             subtitle, size=18, color=LIGHT)

    page_decor(s, page, TOTAL, section=f"PART {part_no:02d}")



# ---------- Slide: 科幻三大种类 总览 ----------
def slide_types_overview(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=20, seed=4)
    page_decor(s, page, TOTAL, section="PART 01 · 三大种类")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "科幻小说的三大种类", size=34, bold=True, color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "硬一点、软一点、再灾难一点——你最爱哪一种？",
             size=15, color=LIGHT)

    items = [
        ("硬科幻",  "科学迷的游乐园",
         "靠物理、化学、天文知识\n一步步算出活下来的方法",
         "刘慈欣 · 安迪 · 威尔", CYAN, "H"),
        ("软科幻",  "情感与哲思的茶馆",
         "科学只是背景\n重点是人的感情、选择和命运",
         "特德 · 姜", PINK, "S"),
        ("灾难科幻", "末日生存指南",
         "地球或人类遭遇大麻烦\n看人类怎么用智慧团结活下去",
         "刘慈欣", ACCENT, "D"),
    ]
    card_w = Inches(3.9)
    card_h = Inches(4.6)
    gap    = Inches(0.25)
    total_w = card_w * 3 + gap * 2
    start_x = (SW - total_w) // 2
    y = Inches(2.2)

    for i, (name, sub, desc, master, col, mark) in enumerate(items):
        x = start_x + (card_w + gap) * i
        add_round_rect(s, x, y, card_w, card_h, fill=DEEP_BLUE,
                       line=col, line_width=Pt(1.25), corner=0.05)
        # 大字母标识
        add_text(s, x + Inches(0.4), y + Inches(0.3), Inches(1.2),
                 Inches(1.2), mark, size=68, bold=True, color=col,
                 font=EN_FONT)
        # 类型名
        add_text(s, x + Inches(0.4), y + Inches(1.55), card_w - Inches(0.8),
                 Inches(0.7), name, size=28, bold=True, color=WHITE)
        # 副标题
        add_text(s, x + Inches(0.4), y + Inches(2.2), card_w - Inches(0.8),
                 Inches(0.4), sub, size=14, color=col, italic=True)
        # 横线
        add_rect(s, x + Inches(0.4), y + Inches(2.65), Inches(1),
                 Emu(19050), fill=col)
        # 描述
        add_text(s, x + Inches(0.4), y + Inches(2.85), card_w - Inches(0.8),
                 Inches(1.2), desc, size=14, color=LIGHT,
                 line_spacing=1.5)
        # 代表大师
        add_text(s, x + Inches(0.4), y + Inches(3.95), card_w - Inches(0.8),
                 Inches(0.35), "代表大师", size=10, color=DIM, bold=True)
        add_text(s, x + Inches(0.4), y + Inches(4.2), card_w - Inches(0.8),
                 Inches(0.4), master, size=14, color=ACCENT, bold=True)


# ---------- Slide: 硬科幻 ----------
def slide_hard_scifi(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=18, seed=5)
    page_decor(s, page, TOTAL, section="PART 01 · 三大种类 · ①")

    # 大编号
    add_text(s, Inches(0.9), Inches(0.7), Inches(2), Inches(1.5),
             "01", size=110, bold=True, color=CYAN, font=EN_FONT)
    add_text(s, Inches(2.6), Inches(1.05), Inches(8), Inches(0.55),
             "HARD SCI-FI", size=14, color=DIM, bold=True, font=EN_FONT)
    add_text(s, Inches(2.6), Inches(1.35), Inches(8), Inches(0.85),
             "硬科幻 — 科学迷的游乐园", size=34, bold=True, color=WHITE)

    add_rect(s, Inches(0.9), Inches(2.45), Inches(0.6), Emu(38100),
             fill=CYAN)
    add_text(s, Inches(1.6), Inches(2.32), Inches(11), Inches(0.5),
             "用真实的物理、化学、天文，一步步把人物从绝境救回来",
             size=15, color=LIGHT)

    # 左：例子1 火星救援
    ex_y = Inches(3.1)
    add_round_rect(s, Inches(0.9), ex_y, Inches(5.85), Inches(3.7),
                   fill=DEEP_BLUE, line=CYAN, line_width=Pt(1), corner=0.04)
    add_text(s, Inches(1.15), ex_y + Inches(0.25), Inches(5.5), Inches(0.4),
             "例子 ①", size=12, color=CYAN, bold=True)
    add_text(s, Inches(1.15), ex_y + Inches(0.55), Inches(5.5), Inches(0.6),
             "安迪·威尔《火星救援》", size=22, bold=True, color=ACCENT)
    add_text(s, Inches(1.15), ex_y + Inches(1.3), Inches(5.5), Inches(2.3),
             "宇航员被困火星，靠：\n"
             "    用火箭燃料造水\n"
             "    精确计算土豆产量\n"
             "    每一次出舱都做好热量预算\n\n"
             "每一步都像在做一道扎实的应用题。",
             size=14, color=LIGHT, line_spacing=1.5)

    # 右：例子2 三体
    add_round_rect(s, Inches(7.0), ex_y, Inches(5.85), Inches(3.7),
                   fill=DEEP_BLUE, line=CYAN, line_width=Pt(1), corner=0.04)
    add_text(s, Inches(7.25), ex_y + Inches(0.25), Inches(5.5), Inches(0.4),
             "例子 ②", size=12, color=CYAN, bold=True)
    add_text(s, Inches(7.25), ex_y + Inches(0.55), Inches(5.5), Inches(0.6),
             "刘慈欣《三体》· 水滴", size=22, bold=True, color=ACCENT)
    add_text(s, Inches(7.25), ex_y + Inches(1.3), Inches(5.5), Inches(2.3),
             "「水滴」探测器：\n"
             "    用强互作用力材料制造\n"
             "    表面光滑到分子都无法附着\n"
             "    一击就能贯穿整支舰队\n\n"
             "听起来魔法，其实背后全是真实物理。",
             size=14, color=LIGHT, line_spacing=1.5)



# ---------- Slide: 软科幻 ----------
def slide_soft_scifi(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=18, seed=6)
    page_decor(s, page, TOTAL, section="PART 01 · 三大种类 · ②")

    add_text(s, Inches(0.9), Inches(0.7), Inches(2), Inches(1.5),
             "02", size=110, bold=True, color=PINK, font=EN_FONT)
    add_text(s, Inches(2.6), Inches(1.05), Inches(8), Inches(0.55),
             "SOFT SCI-FI", size=14, color=DIM, bold=True, font=EN_FONT)
    add_text(s, Inches(2.6), Inches(1.35), Inches(8), Inches(0.85),
             "软科幻 — 情感与哲思的茶馆", size=34, bold=True, color=WHITE)

    add_rect(s, Inches(0.9), Inches(2.45), Inches(0.6), Emu(38100),
             fill=PINK)
    add_text(s, Inches(1.6), Inches(2.32), Inches(11), Inches(0.5),
             "科学是背景；放在镜头中央的，是「人」",
             size=15, color=LIGHT)

    # 大引言卡
    add_round_rect(s, Inches(0.9), Inches(3.0), Inches(11.5), Inches(3.85),
                   fill=DEEP_BLUE, line=PINK, line_width=Pt(1), corner=0.03)
    # 引号装饰
    add_text(s, Inches(1.1), Inches(3.0), Inches(2), Inches(1.6),
             "“", size=160, color=PINK, bold=True, font=EN_FONT)

    add_text(s, Inches(2.4), Inches(3.35), Inches(9.8), Inches(0.55),
             "代表大师 · 特德 · 姜", size=14, color=PINK, bold=True)
    add_text(s, Inches(2.4), Inches(3.7), Inches(9.8), Inches(0.7),
             "《你一生的故事》", size=26, bold=True, color=ACCENT)

    add_text(s, Inches(2.4), Inches(4.55), Inches(9.8), Inches(2.1),
             "外星人的语言能让人同时看到过去和未来。\n"
             "主角知道自己的女儿，将会早早离开这个世界。\n"
             "可她依然选择，把这个孩子生下来，好好地爱她。\n\n"
             "读完这本书，你会愣很久很久——这就是软科幻的力量。",
             size=15, color=LIGHT, line_spacing=1.6)


# ---------- Slide: 灾难科幻 ----------
def slide_disaster_scifi(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=18, seed=7)
    page_decor(s, page, TOTAL, section="PART 01 · 三大种类 · ③")

    add_text(s, Inches(0.9), Inches(0.7), Inches(2), Inches(1.5),
             "03", size=110, bold=True, color=ACCENT, font=EN_FONT)
    add_text(s, Inches(2.6), Inches(1.05), Inches(8), Inches(0.55),
             "DISASTER SCI-FI", size=14, color=DIM, bold=True,
             font=EN_FONT)
    add_text(s, Inches(2.6), Inches(1.35), Inches(8), Inches(0.85),
             "未来 / 灾难科幻 — 末日生存指南",
             size=32, bold=True, color=WHITE)

    add_rect(s, Inches(0.9), Inches(2.45), Inches(0.6), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.6), Inches(2.32), Inches(11), Inches(0.5),
             "天塌下来了，怎么办？看人类靠智慧和团结活下去",
             size=15, color=LIGHT)

    ex_y = Inches(3.1)
    # 例 1：流浪地球
    add_round_rect(s, Inches(0.9), ex_y, Inches(5.85), Inches(3.7),
                   fill=DEEP_BLUE, line=ACCENT, line_width=Pt(1),
                   corner=0.04)
    add_text(s, Inches(1.15), ex_y + Inches(0.25), Inches(5.5), Inches(0.4),
             "例子 ①", size=12, color=ACCENT, bold=True)
    add_text(s, Inches(1.15), ex_y + Inches(0.55), Inches(5.5), Inches(0.6),
             "刘慈欣《流浪地球》", size=22, bold=True, color=WHITE)
    add_text(s, Inches(1.15), ex_y + Inches(1.3), Inches(5.5), Inches(2.3),
             "太阳即将爆炸——\n\n"
             "人类不逃命，也不躲避，\n"
             "而是给整个地球装上行星发动机，\n"
             "带着家园一起逃跑。\n\n"
             "这就是中国式浪漫的灾难想象。",
             size=14, color=LIGHT, line_spacing=1.5)

    # 例 2：三体
    add_round_rect(s, Inches(7.0), ex_y, Inches(5.85), Inches(3.7),
                   fill=DEEP_BLUE, line=ACCENT, line_width=Pt(1),
                   corner=0.04)
    add_text(s, Inches(7.25), ex_y + Inches(0.25), Inches(5.5), Inches(0.4),
             "例子 ②", size=12, color=ACCENT, bold=True)
    add_text(s, Inches(7.25), ex_y + Inches(0.55), Inches(5.5), Inches(0.6),
             "刘慈欣《三体》· 三部曲", size=22, bold=True, color=WHITE)
    add_text(s, Inches(7.25), ex_y + Inches(1.3), Inches(5.5), Inches(2.3),
             "外星人即将入侵，人类绞尽脑汁：\n"
             "    面壁计划：四个人独自构思方案\n"
             "    黑暗森林威慑：以同归于尽逼和平\n"
             "    曲率飞船：直接折叠空间逃走\n\n"
             "每一种应对，都是一次脑洞大开的极限思考。",
             size=14, color=LIGHT, line_spacing=1.5)


# ---------- Slide: 类型小结 ----------
def slide_types_tip(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=20, seed=8)
    page_decor(s, page, TOTAL, section="PART 01 · 类型小提醒")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "一个温柔的小提醒", size=34, bold=True, color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "再「硬」的科幻，最后打动你的，永远是「人」",
             size=15, color=LIGHT)

    # 中央大引言卡
    add_round_rect(s, Inches(1.4), Inches(2.6), Inches(10.5), Inches(3.9),
                   fill=DEEP_BLUE, line=ACCENT, line_width=Pt(1.25),
                   corner=0.03)

    # 大引号
    add_text(s, Inches(1.6), Inches(2.5), Inches(2), Inches(1.6),
             "“", size=130, color=ACCENT, bold=True, font=EN_FONT)

    add_rich_text(s, Inches(2.7), Inches(3.1), Inches(8.8), Inches(2.6),
                  [
                      [("很多书是 ", {"size": 22, "color": WHITE}),
                       ("混搭", {"size": 22, "color": ACCENT, "bold": True}),
                       (" 的——", {"size": 22, "color": WHITE})],
                      [("", {"size": 8, "color": WHITE})],
                      [("比如《三体》既是 ", {"size": 18, "color": LIGHT}),
                       ("硬科幻", {"size": 18, "color": CYAN, "bold": True}),
                       (" ，又是 ", {"size": 18, "color": LIGHT}),
                       ("灾难科幻", {"size": 18, "color": ACCENT,
                                  "bold": True}),
                       ("。", {"size": 18, "color": LIGHT})],
                      [("", {"size": 8, "color": WHITE})],
                      [("但不管哪一类，最打动人的永远是里面",
                        {"size": 18, "color": LIGHT})],
                      [("「", {"size": 24, "color": PINK, "bold": True}),
                       ("人", {"size": 24, "color": PINK, "bold": True}),
                       ("」", {"size": 24, "color": PINK, "bold": True}),
                       (" 的情感——", {"size": 18, "color": LIGHT})],
                      [("硬如刘慈欣，写到最后，",
                        {"size": 18, "color": LIGHT})],
                      [("也是人类紧紧握住爱人的手。",
                        {"size": 18, "color": LIGHT})],
                  ], line_spacing=1.4)



# ---------- Slide: 四块积木 总览 ----------
def slide_structure(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=20, seed=9)
    page_decor(s, page, TOTAL, section="PART 01 · 故事的骨架")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "科幻故事的「四块积木」", size=34, bold=True, color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "几乎每一个科幻故事，都由这四块拼成（以《火星救援》为例）",
             size=15, color=LIGHT)

    blocks = [
        ("一个假设",  "如果……会怎样？",
         "如果一个人被独自丢在火星？", CYAN, "?"),
        ("一个麻烦",  "假设带来的大问题",
         "食物撑不到救援，无法和地球联系。", PINK, "!"),
        ("一个英雄",  "不一定有超能力，\n但一定要动脑子",
         "宇航员马克——一位植物学专家。", ACCENT, "★"),
        ("一个结局",  "问题解决了吗？",
         "成功获救：靠科学计算 + 一点点运气。", CYAN, "✓"),
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
        # 编号气泡
        add_oval(s, x + Inches(0.3), y + Inches(0.3), Inches(0.7),
                 Inches(0.7), fill=col)
        add_text(s, x + Inches(0.3), y + Inches(0.3), Inches(0.7),
                 Inches(0.7), str(i + 1), size=20, bold=True, color=NAVY,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=EN_FONT)
        # 大符号
        add_text(s, x + Inches(1.1), y + Inches(0.25), Inches(1.5),
                 Inches(0.85), mark, size=46, bold=True, color=col,
                 font=EN_FONT)
        # 名字
        add_text(s, x + Inches(0.3), y + Inches(1.3), card_w - Inches(0.6),
                 Inches(0.7), name, size=24, bold=True, color=WHITE)
        # 副说明
        add_text(s, x + Inches(0.3), y + Inches(2.05),
                 card_w - Inches(0.6), Inches(0.9), sub, size=14,
                 color=col, italic=True, line_spacing=1.4)
        # 横线
        add_rect(s, x + Inches(0.3), y + Inches(3.0), Inches(1),
                 Emu(19050), fill=col)
        # 标签
        add_text(s, x + Inches(0.3), y + Inches(3.15),
                 card_w - Inches(0.6), Inches(0.35),
                 "《火星救援》中", size=11, color=DIM, bold=True)
        # 例子
        add_text(s, x + Inches(0.3), y + Inches(3.45),
                 card_w - Inches(0.6), Inches(1.1), ex, size=13,
                 color=LIGHT, line_spacing=1.45)


# ---------- Slide: 四块积木 应用《你一生的故事》 ----------
def slide_structure_chiang(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=20, seed=10)
    page_decor(s, page, TOTAL, section="PART 01 · 故事的骨架")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "再用一次：拆解《你一生的故事》",
             size=32, bold=True, color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=PINK)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "同样的四块积木，也能拼出特德 · 姜的「软」故事",
             size=15, color=LIGHT)

    rows = [
        ("①  假设", "如果学会一种外星语言，就能预知未来？", CYAN),
        ("②  麻烦", "你将提前看到自己人生中所有的不幸。", PINK),
        ("③  英雄", "一位语言学家——\n她的勇气，是「明知结局，仍然拥抱现在」。",
         ACCENT),
        ("④  结局", "她选择生下女儿，全心全意爱她，然后温柔地目送她离去。",
         CYAN),
    ]
    y0 = Inches(2.4)
    row_h = Inches(1.05)
    for i, (label, content, col) in enumerate(rows):
        ry = y0 + row_h * i
        # 行底
        add_round_rect(s, Inches(0.9), ry, Inches(11.5),
                       row_h - Inches(0.15), fill=DEEP_BLUE, line=col,
                       line_width=Pt(0.75), corner=0.12)
        # 左侧色块
        add_rect(s, Inches(0.9), ry, Inches(0.18),
                 row_h - Inches(0.15), fill=col)
        # label
        add_text(s, Inches(1.3), ry, Inches(2.4), row_h - Inches(0.15),
                 label, size=20, bold=True, color=col,
                 anchor=MSO_ANCHOR.MIDDLE)
        # content
        add_text(s, Inches(3.8), ry, Inches(8.4), row_h - Inches(0.15),
                 content, size=15, color=LIGHT,
                 anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.4)

    # 底部温馨提示
    add_text(s, Inches(0.9), Inches(6.8), Inches(12), Inches(0.4),
             "★ 以后读科幻，试着找出这四块积木——故事一下就清晰啦",
             size=13, color=ACCENT, italic=True)



# ---------- Slide: 有趣设定 总览 ----------
def slide_settings_overview(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=25, seed=11)
    page_decor(s, page, TOTAL, section="PART 01 · 拍大腿的设定")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "让人拍大腿的有趣设定", size=34, bold=True, color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "三位大师，三种「我怎么没想到」", size=15, color=LIGHT)

    items = [
        ("刘慈欣",        "把宇宙变成黑暗森林",        CYAN),
        ("安迪 · 威尔",   "在火星种土豆给自己吃",      ACCENT),
        ("特德 · 姜",     "一种语言能让你看到一生",    PINK),
    ]
    card_w = Inches(3.9)
    card_h = Inches(4.4)
    gap    = Inches(0.25)
    total_w = card_w * 3 + gap * 2
    start_x = (SW - total_w) // 2
    y = Inches(2.4)

    for i, (n, m, col) in enumerate(items):
        x = start_x + (card_w + gap) * i
        add_round_rect(s, x, y, card_w, card_h, fill=DEEP_BLUE,
                       line=col, line_width=Pt(1), corner=0.05)
        add_rect(s, x, y, card_w, Inches(0.16), fill=col)
        add_text(s, x, y + Inches(0.6), card_w, Inches(0.5),
                 f"大师 {chr(0x2160 + i)}", size=12, color=col, bold=True,
                 align=PP_ALIGN.CENTER)
        add_text(s, x, y + Inches(1.1), card_w, Inches(0.9),
                 n, size=30, bold=True, color=WHITE,
                 align=PP_ALIGN.CENTER)
        # 中央装饰
        add_rect(s, x + (card_w - Inches(1)) // 2, y + Inches(2.15),
                 Inches(1), Emu(19050), fill=col)
        add_text(s, x + Inches(0.3), y + Inches(2.45), card_w - Inches(0.6),
                 Inches(1.5), m, size=15, color=LIGHT,
                 align=PP_ALIGN.CENTER, line_spacing=1.4)
        add_text(s, x, y + Inches(3.75), card_w, Inches(0.4),
                 "下一页详细看 →", size=11, color=ACCENT, italic=True,
                 align=PP_ALIGN.CENTER)


# ---------- 单个作家的设定页 ----------
def slide_settings_master(page, name, tag, color, items, section_no):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=18, seed=12 + section_no)
    page_decor(s, page, TOTAL,
               section=f"PART 01 · 拍大腿的设定 · {section_no}")

    # 顶部标识
    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             f"{name} 的「世界观工具箱」", size=30, bold=True,
             color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=color)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             tag, size=14, color=LIGHT, italic=True)

    # 三个设定卡片纵向排列
    cy = Inches(2.2)
    cw = Inches(11.5)
    ch = Inches(1.45)
    cgap = Inches(0.18)
    for i, (title, body) in enumerate(items):
        y = cy + (ch + cgap) * i
        add_round_rect(s, Inches(0.9), y, cw, ch, fill=DEEP_BLUE,
                       line=color, line_width=Pt(0.75), corner=0.08)
        # 左侧编号大字
        add_text(s, Inches(1.05), y, Inches(1.2), ch,
                 f"0{i + 1}", size=42, bold=True, color=color,
                 anchor=MSO_ANCHOR.MIDDLE, font=EN_FONT)
        # 竖线
        add_rect(s, Inches(2.2), y + Inches(0.25), Emu(19050),
                 ch - Inches(0.5), fill=color)
        # 标题
        add_text(s, Inches(2.45), y + Inches(0.18), Inches(9.5),
                 Inches(0.5), title, size=18, bold=True, color=ACCENT)
        # 内容
        add_text(s, Inches(2.45), y + Inches(0.62), Inches(9.5),
                 ch - Inches(0.7), body, size=13, color=LIGHT,
                 line_spacing=1.4)



# ---------- Slide: 写作秘诀 总览 ----------
def slide_secrets_overview(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=25, seed=20)
    page_decor(s, page, TOTAL, section="PART 02 · 三条写作秘诀")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "三位大师的「独门武功」", size=34, bold=True, color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "每一招都简单到——你今晚就能用",
             size=15, color=LIGHT)

    secrets = [
        ("秘诀 ①", "刘慈欣", "追问「然后呢？」",
         "从一个巨大的「如果」开始，\n往下连追三步。", CYAN),
        ("秘诀 ②", "安迪 · 威尔", "让主角列清单",
         "把困境拆成「我有 / 我缺 / 怎么补」，\n一步一步算出来。", ACCENT),
        ("秘诀 ③", "特德 · 姜", "从一道人生选择题出发",
         "先想一个关于人的哲学问题，\n再让科幻设定服务它。", PINK),
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
        # 顶部色条
        add_rect(s, x, y, card_w, Inches(0.18), fill=col)

        add_text(s, x + Inches(0.4), y + Inches(0.4), card_w - Inches(0.8),
                 Inches(0.5), no, size=14, color=col, bold=True)
        add_text(s, x + Inches(0.4), y + Inches(0.85), card_w - Inches(0.8),
                 Inches(0.7), name, size=24, bold=True, color=WHITE)
        # 大字关键句
        add_text(s, x + Inches(0.4), y + Inches(1.85), card_w - Inches(0.8),
                 Inches(1.4), key, size=22, bold=True, color=ACCENT,
                 line_spacing=1.3)
        # 横线
        add_rect(s, x + Inches(0.4), y + Inches(3.25), Inches(1.0),
                 Emu(19050), fill=col)
        # 描述
        add_text(s, x + Inches(0.4), y + Inches(3.45), card_w - Inches(0.8),
                 Inches(1.2), desc, size=14, color=LIGHT, line_spacing=1.5)


# ---------- Slide: 秘诀一 刘慈欣 - 概念 ----------
def slide_secret_liu(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=20, seed=21)
    page_decor(s, page, TOTAL, section="PART 02 · 秘诀 ①")

    add_text(s, Inches(0.9), Inches(0.7), Inches(2), Inches(1.2),
             "01", size=110, bold=True, color=CYAN, font=EN_FONT)
    add_text(s, Inches(2.6), Inches(1.05), Inches(11), Inches(0.5),
             "秘诀 ① · 刘慈欣", size=14, color=DIM, bold=True)
    add_text(s, Inches(2.6), Inches(1.35), Inches(11), Inches(0.85),
             "从「一个巨大的如果」往下推三步",
             size=30, bold=True, color=WHITE)

    add_rect(s, Inches(0.9), Inches(2.45), Inches(0.6), Emu(38100),
             fill=CYAN)
    add_text(s, Inches(1.6), Inches(2.32), Inches(11), Inches(0.5),
             "他像下棋一样：每多走一步，世界就翻一次天",
             size=15, color=LIGHT)

    # 左：他怎么写
    add_round_rect(s, Inches(0.9), Inches(3.0), Inches(5.85), Inches(3.85),
                   fill=DEEP_BLUE, line=CYAN, line_width=Pt(1), corner=0.04)
    add_text(s, Inches(1.15), Inches(3.2), Inches(5.5), Inches(0.4),
             "他是怎么写的？", size=14, color=CYAN, bold=True)
    add_text(s, Inches(1.15), Inches(3.55), Inches(5.5), Inches(0.6),
             "《三体》的诞生过程", size=20, bold=True, color=ACCENT)
    add_rich_text(s, Inches(1.15), Inches(4.25), Inches(5.5), Inches(2.5),
                  [
                      [("如果外星文明比我们强大得多，",
                        {"size": 14, "color": WHITE})],
                      [("而且它们正赶来——人类会怎样？",
                        {"size": 14, "color": WHITE})],
                      [("", {"size": 6, "color": WHITE})],
                      [("→  ", {"size": 14, "color": ACCENT, "bold": True}),
                       ("人类陷入恐慌，成立联合政府",
                        {"size": 13, "color": LIGHT})],
                      [("→  ", {"size": 14, "color": ACCENT, "bold": True}),
                       ("有人背叛人类、有人愿意牺牲",
                        {"size": 13, "color": LIGHT})],
                      [("→  ", {"size": 14, "color": ACCENT, "bold": True}),
                       ("最后，整个太阳系被二维化……",
                        {"size": 13, "color": LIGHT})],
                      [("", {"size": 6, "color": WHITE})],
                      [("他，一直推到了宇宙的尽头。",
                        {"size": 14, "color": ACCENT, "italic": True})],
                  ], line_spacing=1.5)

    # 右：核心方法
    add_round_rect(s, Inches(7.0), Inches(3.0), Inches(5.85), Inches(3.85),
                   fill=PURPLE, line=ACCENT, line_width=Pt(1.25),
                   corner=0.04)
    add_text(s, Inches(7.25), Inches(3.2), Inches(5.5), Inches(0.4),
             "你能直接用的方法", size=14, color=ACCENT, bold=True)
    add_text(s, Inches(7.25), Inches(3.55), Inches(5.5), Inches(0.6),
             "写「如果……」+ 连追三次「然后呢？」",
             size=20, bold=True, color=WHITE)
    add_text(s, Inches(7.25), Inches(4.55), Inches(5.5), Inches(2.3),
             "Step 1.  写一句  「如果……」\n"
             "Step 2.  问自己  「然后呢？」\n"
             "Step 3.  再问一次「然后呢？」\n"
             "Step 4.  再问一次「然后呢？」\n\n"
             "三次之后，一个完整故事就长出来了。",
             size=14, color=LIGHT, line_spacing=1.6)



# ---------- Slide: 秘诀一 - 例子演示 ----------
def slide_secret_liu_demo(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=20, seed=22)
    page_decor(s, page, TOTAL, section="PART 02 · 秘诀 ① · 试一试")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "现场演示：往下推三步", size=32, bold=True, color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=CYAN)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "两个例子，看看「然后呢？」怎么把点子变成故事",
             size=15, color=LIGHT)

    # 例子 1
    ex1_y = Inches(2.3)
    add_round_rect(s, Inches(0.9), ex1_y, Inches(5.85), Inches(4.55),
                   fill=DEEP_BLUE, line=CYAN, line_width=Pt(1),
                   corner=0.04)
    add_text(s, Inches(1.15), ex1_y + Inches(0.2), Inches(5.5),
             Inches(0.4), "例子 ①", size=12, color=CYAN, bold=True)
    add_text(s, Inches(1.15), ex1_y + Inches(0.55), Inches(5.5),
             Inches(0.6), "如果学校可以漂浮在空中？",
             size=20, bold=True, color=ACCENT)
    add_rich_text(s, Inches(1.15), ex1_y + Inches(1.4), Inches(5.5),
                  Inches(3.0),
                  [
                      [("→ 然后呢？  ", {"size": 14, "color": CYAN,
                                       "bold": True}),
                       ("上学要坐飞行器。",
                        {"size": 14, "color": LIGHT})],
                      [("", {"size": 8, "color": WHITE})],
                      [("→ 然后呢？  ", {"size": 14, "color": CYAN,
                                       "bold": True}),
                       ("有一天飞行器没油了。",
                        {"size": 14, "color": LIGHT})],
                      [("", {"size": 8, "color": WHITE})],
                      [("→ 然后呢？  ", {"size": 14, "color": CYAN,
                                       "bold": True}),
                       ("主角用太阳能板充电，",
                        {"size": 14, "color": LIGHT})],
                      [("                  ",
                        {"size": 14, "color": LIGHT}),
                       ("差点迟到，却写出了一首歌。",
                        {"size": 14, "color": LIGHT})],
                  ], line_spacing=1.4)

    # 例子 2
    add_round_rect(s, Inches(7.0), ex1_y, Inches(5.85), Inches(4.55),
                   fill=DEEP_BLUE, line=CYAN, line_width=Pt(1),
                   corner=0.04)
    add_text(s, Inches(7.25), ex1_y + Inches(0.2), Inches(5.5),
             Inches(0.4), "例子 ②", size=12, color=CYAN, bold=True)
    add_text(s, Inches(7.25), ex1_y + Inches(0.55), Inches(5.5),
             Inches(0.6), "如果我能和动物说话？",
             size=20, bold=True, color=ACCENT)
    add_rich_text(s, Inches(7.25), ex1_y + Inches(1.4), Inches(5.5),
                  Inches(3.0),
                  [
                      [("→ 然后呢？  ", {"size": 14, "color": CYAN,
                                       "bold": True}),
                       ("猫告诉我：谁考试作弊。",
                        {"size": 14, "color": LIGHT})],
                      [("", {"size": 8, "color": WHITE})],
                      [("→ 然后呢？  ", {"size": 14, "color": CYAN,
                                       "bold": True}),
                       ("猫开始要求每天买小鱼干。",
                        {"size": 14, "color": LIGHT})],
                      [("", {"size": 8, "color": WHITE})],
                      [("→ 然后呢？  ", {"size": 14, "color": CYAN,
                                       "bold": True}),
                       ("我破产了，",
                        {"size": 14, "color": LIGHT})],
                      [("                  ",
                        {"size": 14, "color": LIGHT}),
                       ("只好跑去宠物店打工还债。",
                        {"size": 14, "color": LIGHT})],
                  ], line_spacing=1.4)


# ---------- Slide: 秘诀二 安迪·威尔 - 概念 ----------
def slide_secret_weir(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=20, seed=23)
    page_decor(s, page, TOTAL, section="PART 02 · 秘诀 ②")

    add_text(s, Inches(0.9), Inches(0.7), Inches(2), Inches(1.2),
             "02", size=110, bold=True, color=ACCENT, font=EN_FONT)
    add_text(s, Inches(2.6), Inches(1.05), Inches(11), Inches(0.5),
             "秘诀 ② · 安迪 · 威尔", size=14, color=DIM, bold=True)
    add_text(s, Inches(2.6), Inches(1.35), Inches(11), Inches(0.85),
             "让主角「列清单」解决问题", size=30, bold=True,
             color=WHITE)

    add_rect(s, Inches(0.9), Inches(2.45), Inches(0.6), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.6), Inches(2.32), Inches(11), Inches(0.5),
             "遇到天大麻烦，先别哭——拿出纸笔，开始算",
             size=15, color=LIGHT)

    # 左：他是怎么写的
    add_round_rect(s, Inches(0.9), Inches(3.0), Inches(5.85), Inches(3.85),
                   fill=DEEP_BLUE, line=ACCENT, line_width=Pt(1),
                   corner=0.04)
    add_text(s, Inches(1.15), Inches(3.2), Inches(5.5), Inches(0.4),
             "他是怎么写的？", size=14, color=ACCENT, bold=True)
    add_text(s, Inches(1.15), Inches(3.55), Inches(5.5), Inches(0.6),
             "马克在火星上的清单", size=20, bold=True, color=WHITE)
    add_text(s, Inches(1.15), Inches(4.25), Inches(5.5), Inches(2.5),
             "我有什么？\n"
             "我需要什么？\n"
             "差多少？\n"
             "怎么补？\n\n"
             "卡路里、水、土豆产量、平方米——\n"
             "全部一项一项算，再一步步执行。",
             size=14, color=LIGHT, line_spacing=1.55)

    # 右：方法
    add_round_rect(s, Inches(7.0), Inches(3.0), Inches(5.85), Inches(3.85),
                   fill=PURPLE, line=ACCENT, line_width=Pt(1.25),
                   corner=0.04)
    add_text(s, Inches(7.25), Inches(3.2), Inches(5.5), Inches(0.4),
             "你能直接用的方法", size=14, color=ACCENT, bold=True)
    add_text(s, Inches(7.25), Inches(3.55), Inches(5.5), Inches(0.6),
             "让你的主角，掏出本子开始列清单",
             size=20, bold=True, color=WHITE)
    add_rich_text(s, Inches(7.25), Inches(4.5), Inches(5.5), Inches(2.3),
                  [
                      [("我有：", {"size": 15, "color": CYAN, "bold": True}),
                       ("当下能用的资源",
                        {"size": 14, "color": LIGHT})],
                      [("", {"size": 6, "color": WHITE})],
                      [("我缺：", {"size": 15, "color": PINK, "bold": True}),
                       ("活下去必需的东西",
                        {"size": 14, "color": LIGHT})],
                      [("", {"size": 6, "color": WHITE})],
                      [("怎么补：",
                        {"size": 15, "color": ACCENT, "bold": True}),
                       ("一条一条写出可以执行的计划",
                        {"size": 14, "color": LIGHT})],
                      [("", {"size": 6, "color": WHITE})],
                      [("清单写出来，故事就往前走了。",
                        {"size": 14, "color": ACCENT, "italic": True})],
                  ], line_spacing=1.4)



# ---------- Slide: 秘诀二 - 例子演示 ----------
def slide_secret_weir_demo(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=20, seed=24)
    page_decor(s, page, TOTAL, section="PART 02 · 秘诀 ② · 试一试")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "现场演示：荒岛求生清单", size=32, bold=True, color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "小明被困荒岛——他没有哭，他蹲下来在沙地上写：",
             size=15, color=LIGHT)

    # 模拟一张笔记本
    add_round_rect(s, Inches(2.6), Inches(2.4), Inches(8.1), Inches(4.4),
                   fill=WHITE, line=ACCENT, line_width=Pt(1.5),
                   corner=0.04)
    # 顶部色条
    add_rect(s, Inches(2.6), Inches(2.4), Inches(8.1), Inches(0.45),
             fill=ACCENT)
    add_text(s, Inches(2.6), Inches(2.4), Inches(8.1), Inches(0.45),
             "  小  明  的  笔  记  本", size=15, color=NAVY, bold=True,
             anchor=MSO_ANCHOR.MIDDLE)

    # 三段
    NV = NAVY
    add_rich_text(s, Inches(3.0), Inches(3.05), Inches(7.3), Inches(3.7),
                  [
                      [("我有：",
                        {"size": 18, "color": CYAN, "bold": True}),
                       ("一把小刀  ·  一个塑料瓶  ·  半包饼干。",
                        {"size": 16, "color": NV})],
                      [("", {"size": 8, "color": NV})],
                      [("我需要：",
                        {"size": 18, "color": PINK, "bold": True}),
                       ("水  ·  火  ·  能睡觉的地方。",
                        {"size": 16, "color": NV})],
                      [("", {"size": 8, "color": NV})],
                      [("我的计划：",
                        {"size": 18, "color": PURPLE, "bold": True})],
                      [("  ①  ",
                        {"size": 15, "color": ACCENT, "bold": True}),
                       ("用塑料瓶蒸馏海水", {"size": 15, "color": NV})],
                      [("  ②  ",
                        {"size": 15, "color": ACCENT, "bold": True}),
                       ("用小刀钻木取火", {"size": 15, "color": NV})],
                      [("  ③  ",
                        {"size": 15, "color": ACCENT, "bold": True}),
                       ("用树枝搭一个能挡风的小棚",
                        {"size": 15, "color": NV})],
                  ], line_spacing=1.35)

    # 提示
    add_text(s, Inches(0.9), Inches(7.0), Inches(12), Inches(0.4),
             "★  当读者跟着主角一起算明白「该怎么活下来」，故事就有了科学的力量",
             size=12, color=ACCENT, italic=True)


# ---------- Slide: 秘诀三 特德·姜 - 概念 ----------
def slide_secret_chiang(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=20, seed=25)
    page_decor(s, page, TOTAL, section="PART 02 · 秘诀 ③")

    add_text(s, Inches(0.9), Inches(0.7), Inches(2), Inches(1.2),
             "03", size=110, bold=True, color=PINK, font=EN_FONT)
    add_text(s, Inches(2.6), Inches(1.05), Inches(11), Inches(0.5),
             "秘诀 ③ · 特德 · 姜", size=14, color=DIM, bold=True)
    add_text(s, Inches(2.6), Inches(1.35), Inches(11), Inches(0.85),
             "用一个「人生选择题」做设定", size=30, bold=True,
             color=WHITE)

    add_rect(s, Inches(0.9), Inches(2.45), Inches(0.6), Emu(38100),
             fill=PINK)
    add_text(s, Inches(1.6), Inches(2.32), Inches(11), Inches(0.5),
             "他不先想飞船和外星人——他先想，「人」会怎么活",
             size=15, color=LIGHT)

    # 左：他怎么写
    add_round_rect(s, Inches(0.9), Inches(3.0), Inches(5.85), Inches(3.85),
                   fill=DEEP_BLUE, line=PINK, line_width=Pt(1), corner=0.04)
    add_text(s, Inches(1.15), Inches(3.2), Inches(5.5), Inches(0.4),
             "他是怎么写的？", size=14, color=PINK, bold=True)
    add_text(s, Inches(1.15), Inches(3.55), Inches(5.5), Inches(0.6),
             "先抛出一个「人生选择题」", size=20, bold=True,
             color=ACCENT)
    add_text(s, Inches(1.15), Inches(4.25), Inches(5.5), Inches(2.5),
             "如果你能预知未来所有的不幸，\n你还愿意继续走下去吗？\n\n"
             "如果你发现自己的每一个选择，\n都已经被命运提前写好——\n"
             "你还会认真地去选吗？\n\n"
             "他先想清楚问题，再造一个世界来逼你回答。",
             size=14, color=LIGHT, line_spacing=1.55)

    # 右：方法
    add_round_rect(s, Inches(7.0), Inches(3.0), Inches(5.85), Inches(3.85),
                   fill=PURPLE, line=ACCENT, line_width=Pt(1.25),
                   corner=0.04)
    add_text(s, Inches(7.25), Inches(3.2), Inches(5.5), Inches(0.4),
             "你能直接用的方法", size=14, color=ACCENT, bold=True)
    add_text(s, Inches(7.25), Inches(3.55), Inches(5.5), Inches(0.6),
             "先想一道「关于人的选择题」，再让设定服务它",
             size=18, bold=True, color=WHITE)
    add_text(s, Inches(7.25), Inches(4.65), Inches(5.5), Inches(2.2),
             "Step 1.  写一道你最纠结的人生选择题\n"
             "Step 2.  设计一个能逼出这个选择的科幻设定\n"
             "Step 3.  让主角在这道题里挣扎、流泪、做出选择\n\n"
             "不必爆炸、不必激战——\n"
             "光是「想用又不敢用」，就足够动人。",
             size=13, color=LIGHT, line_spacing=1.5)



# ---------- Slide: 秘诀三 - 例子 ----------
def slide_secret_chiang_demo(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=20, seed=26)
    page_decor(s, page, TOTAL, section="PART 02 · 秘诀 ③ · 试一试")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "三道选择题，挑一道写下去",
             size=32, bold=True, color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=PINK)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "试一试：哪一道，让你愣了一秒钟？",
             size=15, color=LIGHT)

    qs = [
        ("Q1", "如果有一台机器，能消除你被朋友嘲笑的伤心记忆——\n你，会按下那个按钮吗？", CYAN),
        ("Q2", "如果你能提前看到下周期末考试的成绩——\n你，会告诉你最好的朋友吗？", PINK),
        ("Q3", "如果你已经知道，最好的朋友将来一定会背叛你——\n现在的你，还会跟他一起玩吗？", ACCENT),
    ]
    cy = Inches(2.4)
    cw = Inches(11.5)
    ch = Inches(1.35)
    cgap = Inches(0.18)
    for i, (no, body, col) in enumerate(qs):
        y = cy + (ch + cgap) * i
        add_round_rect(s, Inches(0.9), y, cw, ch, fill=DEEP_BLUE, line=col,
                       line_width=Pt(0.75), corner=0.08)
        # 编号
        add_oval(s, Inches(1.1), y + Inches(0.3), Inches(0.75),
                 Inches(0.75), fill=col)
        add_text(s, Inches(1.1), y + Inches(0.3), Inches(0.75),
                 Inches(0.75), no, size=15, bold=True, color=NAVY,
                 align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE,
                 font=EN_FONT)
        # 内容
        add_text(s, Inches(2.1), y, Inches(10.1), ch, body,
                 size=15, color=LIGHT, anchor=MSO_ANCHOR.MIDDLE,
                 line_spacing=1.45)

    add_text(s, Inches(0.9), Inches(6.85), Inches(12), Inches(0.4),
             "★  写出主角「想用又不敢用、知道答案又不敢说」的过程，就是动人的软科幻",
             size=12, color=ACCENT, italic=True)


# ---------- Slide: 总结 ----------
def slide_summary(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=25, seed=30)
    page_decor(s, page, TOTAL, section="结尾 · 把今天装进口袋")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "三句话，带回家", size=34, bold=True, color=WHITE)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "今天讲了很多——但你只要记住这三句话",
             size=15, color=LIGHT)

    items = [
        ("刘慈欣",      "从一个「如果」开始，连追三步「然后呢？」", CYAN),
        ("安迪 · 威尔", "让主角拿出本子，列一份解决问题的清单",   ACCENT),
        ("特德 · 姜",   "先写一道关于人的选择题，再造一个世界来逼答", PINK),
    ]
    cy = Inches(2.45)
    cw = Inches(11.5)
    ch = Inches(1.25)
    cgap = Inches(0.25)
    for i, (name, line, col) in enumerate(items):
        y = cy + (ch + cgap) * i
        add_round_rect(s, Inches(0.9), y, cw, ch, fill=DEEP_BLUE, line=col,
                       line_width=Pt(1), corner=0.08)
        add_rect(s, Inches(0.9), y, Inches(0.18), ch, fill=col)
        add_text(s, Inches(1.3), y, Inches(2.8), ch, name, size=22,
                 bold=True, color=ACCENT, anchor=MSO_ANCHOR.MIDDLE)
        # 竖线
        add_rect(s, Inches(4.1), y + Inches(0.3), Emu(19050),
                 ch - Inches(0.6), fill=col)
        add_text(s, Inches(4.3), y, Inches(8), ch, line, size=17,
                 color=LIGHT, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.4)

    # 底部金句
    add_round_rect(s, Inches(0.9), Inches(6.4), Inches(11.5), Inches(0.55),
                   fill=PURPLE, line=ACCENT, line_width=Pt(0.75),
                   corner=0.4)
    add_text(s, Inches(0.9), Inches(6.4), Inches(11.5), Inches(0.55),
             "★  科幻不是胡思乱想，而是「有逻辑地，做一场好梦」",
             size=15, color=ACCENT, bold=True,
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


# ---------- Slide: 行动号召 ----------
def slide_call_to_action(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    starfield(s, count=30, seed=31)
    page_decor(s, page, TOTAL, section="结尾 · 现在轮到你了")

    add_text(s, Inches(0.9), Inches(0.85), Inches(12), Inches(0.7),
             "现在，轮到你啦", size=34, bold=True, color=ACCENT)
    add_rect(s, Inches(0.9), Inches(1.55), Inches(0.6), Emu(38100),
             fill=ACCENT)
    add_text(s, Inches(1.6), Inches(1.45), Inches(11), Inches(0.5),
             "回家做一件事，把今天的内容真正变成你自己的",
             size=15, color=LIGHT)

    # 三步骤
    steps = [
        ("STEP 1", "选 1 个秘诀",
         "刘慈欣的「然后呢？」\n安迪 · 威尔的「列清单」\n特德 · 姜的「选择题」",
         CYAN),
        ("STEP 2", "选 1 个设定",
         "时间循环？\n记忆传输？\n和动物说话？\n……或你自己想的",
         ACCENT),
        ("STEP 3", "写下你的第一段",
         "不用很长，\n两百字就够。\n\n相信我，你能做到。",
         PINK),
    ]
    card_w = Inches(3.9)
    card_h = Inches(4.2)
    gap    = Inches(0.25)
    total_w = card_w * 3 + gap * 2
    start_x = (SW - total_w) // 2
    y = Inches(2.5)

    for i, (no, title, body, col) in enumerate(steps):
        x = start_x + (card_w + gap) * i
        add_round_rect(s, x, y, card_w, card_h, fill=DEEP_BLUE,
                       line=col, line_width=Pt(1.25), corner=0.05)
        add_rect(s, x, y, card_w, Inches(0.18), fill=col)
        add_text(s, x + Inches(0.4), y + Inches(0.4), card_w - Inches(0.8),
                 Inches(0.4), no, size=13, color=col, bold=True,
                 font=EN_FONT)
        add_text(s, x + Inches(0.4), y + Inches(0.85),
                 card_w - Inches(0.8), Inches(0.7), title, size=24,
                 bold=True, color=WHITE)
        add_rect(s, x + Inches(0.4), y + Inches(1.7), Inches(1),
                 Emu(19050), fill=col)
        add_text(s, x + Inches(0.4), y + Inches(1.95),
                 card_w - Inches(0.8), Inches(2.2), body, size=14,
                 color=LIGHT, line_spacing=1.55)

    # 底部金句
    add_text(s, Inches(0.9), Inches(6.85), Inches(12), Inches(0.4),
             "★  写完之后，别忘了告诉我——下一个科幻大师，可能就是你",
             size=14, color=ACCENT, italic=True, align=PP_ALIGN.CENTER)


# ---------- Slide: 谢谢 ----------
def slide_thanks(page):
    s = add_slide()
    set_solid_bg(s, NAVY)
    add_rect(s, 0, 0, SW, SH, fill=PURPLE, transparency=0.55)
    starfield(s, count=100, seed=99)
    page_decor(s, page, TOTAL, section="The End")

    # 大字 THANK YOU
    add_text(s, Inches(0.9), Inches(2.1), Inches(11.5), Inches(1.6),
             "THANK YOU", size=110, bold=True, color=ACCENT,
             align=PP_ALIGN.CENTER, font=EN_FONT)
    # 中文
    add_text(s, Inches(0.9), Inches(3.7), Inches(11.5), Inches(0.8),
             "谢   谢   大   家", size=34, bold=True, color=WHITE,
             align=PP_ALIGN.CENTER)
    # 装饰线
    add_rect(s, Inches(6.27), Inches(4.65), Inches(0.8), Emu(38100),
             fill=ACCENT)
    # 寄语
    add_text(s, Inches(0.9), Inches(4.95), Inches(11.5), Inches(0.6),
             "愿你也能，写出属于自己的星辰大海",
             size=18, color=LIGHT, italic=True, align=PP_ALIGN.CENTER)
    # 三位大师作为致敬
    add_text(s, Inches(0.9), Inches(6.0), Inches(11.5), Inches(0.5),
             "致敬   ·   刘慈欣   ·   安迪 · 威尔   ·   特德 · 姜",
             size=14, color=DIM, align=PP_ALIGN.CENTER)



# ================= 主流程 =================

# 三位作家的有趣设定数据
LIU_SETTINGS = [
    ("黑暗森林法则（《三体》）",
     "宇宙像一片黑暗森林，每个文明都是带枪的猎人——谁先暴露，谁就被消灭。读完之后，你也许会忍不住，抬头看看窗外的星空。"),
    ("思想钢印（《三体》）",
     "给士兵注射一种东西，让他坚信「人类必胜」。哪怕面对无法战胜的敌人，他也会冲锋。问题是：如果活下去需要自我欺骗，你愿意吗？"),
    ("球状闪电（《球状闪电》）",
     "球状闪电其实是宏观的「电子」；被它击中的人会以量子态存在——生与死同时发生。主角的父母没有真的离开，只是「坍缩」到了另一个状态。"),
]
WEIR_SETTINGS = [
    ("火星种土豆（《火星救援》）",
     "一个人，用粪便当肥料、用火箭燃料造水，在火星大棚里种出了能救自己命的土豆。这不是魔法，是一道道步步可算的科学题。"),
    ("跨物种的语言破译（《挽救计划》）",
     "人类遇到外星蜘蛛「洛基」，对方只会「敲—敲—敲」。主角用质数数列当翻译机，两个完全不同的生物，硬是从零开始学会了交流。"),
    ("我超爱这个设定 ★",
     "因为它在告诉我们：科学，不只是冷冰冰的公式，它能跨越光年——让两个完全不同的生灵，成为朋友。"),
]
CHIANG_SETTINGS = [
    ("预知未来的语言（《你一生的故事》）",
     "学会外星人的语言后，你的思维方式会改变，能同时看见过去与未来。你知道女儿会怎样离开，却仍然，选择把她生下来。"),
    ("回环的宇宙（《巴比伦塔》）",
     "人类造通天塔，凿穿了天幕——结果发现，自己回到了地面。你以为已经走了很远，最后才明白，原来一直回到原点。"),
    ("宇宙的呼吸（《呼吸》）",
     "在一个靠气压驱动的世界，主人公发现宇宙的气压正在均匀，万物终将归于寂静。他平静地写下这一切，像是在与世界温柔告别。"),
]


def main():
    p = 1
    slide_cover();                                                 # 1
    slide_three_authors(p := p + 1)                                # 2
    slide_agenda(p := p + 1)                                       # 3
    slide_part_cover(p := p + 1, 1, "PART 01",
                     "科幻小说说明书",
                     "种类 · 骨架 · 设定——三块拼图拼出科幻全图",
                     CYAN)                                          # 4
    slide_types_overview(p := p + 1)                               # 5
    slide_hard_scifi(p := p + 1)                                   # 6
    slide_soft_scifi(p := p + 1)                                   # 7
    slide_disaster_scifi(p := p + 1)                               # 8
    slide_types_tip(p := p + 1)                                    # 9
    slide_structure(p := p + 1)                                    # 10
    slide_structure_chiang(p := p + 1)                             # 11
    slide_settings_overview(p := p + 1)                            # 12
    slide_settings_master(p := p + 1, "刘慈欣",
                          "硬核宇宙派 · 设定一出，世界观秒变",
                          CYAN, LIU_SETTINGS, 1)                    # 13
    slide_settings_master(p := p + 1, "安迪 · 威尔",
                          "理科解谜派 · 用真实科学撑起每一步",
                          ACCENT, WEIR_SETTINGS, 2)                 # 14
    slide_settings_master(p := p + 1, "特德 · 姜",
                          "哲思软科幻派 · 不爆炸，但让你想很久",
                          PINK, CHIANG_SETTINGS, 3)                 # 15
    slide_part_cover(p := p + 1, 2, "PART 02",
                     "三位大师的写作秘诀",
                     "每一招，都是你今天就能用在作文里的方法",
                     ACCENT)                                        # 16
    slide_secrets_overview(p := p + 1)                             # 17
    slide_secret_liu(p := p + 1)                                   # 18
    slide_secret_liu_demo(p := p + 1)                              # 19
    slide_secret_weir(p := p + 1)                                  # 20
    slide_secret_weir_demo(p := p + 1)                             # 21
    slide_secret_chiang(p := p + 1)                                # 22
    slide_secret_chiang_demo(p := p + 1)                           # 23
    slide_summary(p := p + 1)                                      # 24
    slide_call_to_action(p := p + 1)                               # 25
    slide_thanks(p := p + 1)                                       # 26

    out = "/projects/sandbox/kiro2026/三位科幻大师的武功秘籍.pptx"
    prs.save(out)
    print(f"OK -> {out}  ({p} slides)")


if __name__ == "__main__":
    main()
