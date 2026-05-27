# -*- coding: utf-8 -*-
"""
银卡岗位 1+N 数字化转型 · 4 页麦肯锡高密度版（平安橙色 + 白底）
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

# ===== 平安橙色主题 =====
PA_ORANGE      = RGBColor(0xEC, 0x6F, 0x1C)
PA_ORANGE_DARK = RGBColor(0xC8, 0x55, 0x0E)
PA_ORANGE_DEEP = RGBColor(0x8E, 0x3B, 0x06)
PA_ORANGE_LT   = RGBColor(0xFF, 0xE8, 0xD2)
PA_ORANGE_BG   = RGBColor(0xFF, 0xF5, 0xEB)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
INK       = RGBColor(0x14, 0x14, 0x14)
DARK      = RGBColor(0x33, 0x33, 0x33)
GRAY      = RGBColor(0x66, 0x66, 0x66)
LIGHTGRAY = RGBColor(0xCF, 0xCF, 0xCF)
MIDGRAY   = RGBColor(0x9E, 0x9E, 0x9E)
PALE      = RGBColor(0xF7, 0xF7, 0xF7)

CN_FONT = "Microsoft YaHei"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height


# ===================== 工具函数 =====================
def set_run(run, text, size=11, bold=False, color=INK, italic=False):
    run.text = text
    run.font.name = CN_FONT
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = etree.SubElement(rPr, qn('a:ea'))
    ea.set('typeface', CN_FONT)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color


def tb(slide, l, t, w, h, text, size=11, bold=False, color=INK,
       align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, italic=False, line_spacing=1.15):
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.vertical_anchor = anchor
    lines = text if isinstance(text, list) else [text]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        run = p.add_run()
        set_run(run, ln, size=size, bold=bold, color=color, italic=italic)
    return box


def rect(slide, l, t, w, h, fill, line=None, lw=0):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(lw)
    s.shadow.inherit = False
    return s


def line_h(slide, l, t, w, color=PA_ORANGE, weight=1.0):
    """水平细线"""
    return rect(slide, l, t, w, Pt(weight) * 1, color)


def white_bg(slide):
    rect(slide, 0, 0, SW, SH, WHITE)


# ---- 麦肯锡风格表格 ----
def mck_table(slide, l, t, w, h, headers, rows,
              col_widths=None,
              header_fill=PA_ORANGE, header_color=WHITE,
              header_size=10.5, body_size=9.5,
              first_col_bold=True, first_col_color=PA_ORANGE_DARK,
              tier_marks=None,  # {row_idx: ("S", PA_ORANGE)}  在第0列加色块
              row_fills=None):  # 自定义每行底色
    n_rows = len(rows) + 1
    n_cols = len(headers)
    shp = slide.shapes.add_table(n_rows, n_cols, l, t, w, h)
    tbl = shp.table

    if col_widths:
        s_ = sum(col_widths)
        for i, cw in enumerate(col_widths):
            tbl.columns[i].width = int(w * cw / s_)

    # header
    for ci, hd in enumerate(headers):
        cell = tbl.cell(0, ci)
        cell.fill.solid()
        cell.fill.fore_color.rgb = header_fill
        cell.margin_left = cell.margin_right = Inches(0.06)
        cell.margin_top = cell.margin_bottom = Inches(0.03)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        tfx = cell.text_frame
        tfx.word_wrap = True
        p = tfx.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        set_run(run, hd, size=header_size, bold=True, color=header_color)

    # body
    for ri, row in enumerate(rows):
        if row_fills and ri in row_fills:
            fill = row_fills[ri]
        else:
            fill = WHITE if ri % 2 == 0 else PA_ORANGE_BG
        for ci, val in enumerate(row):
            cell = tbl.cell(ri + 1, ci)
            cell.fill.solid()
            cell.fill.fore_color.rgb = fill
            cell.margin_left = cell.margin_right = Inches(0.06)
            cell.margin_top = cell.margin_bottom = Inches(0.025)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tfx = cell.text_frame
            tfx.word_wrap = True
            p = tfx.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if ci > 0 else PP_ALIGN.CENTER
            run = p.add_run()
            is_first = (ci == 0)
            color = first_col_color if (is_first and first_col_bold) else DARK
            set_run(run, val, size=body_size,
                    bold=(is_first and first_col_bold), color=color)
    return shp


# ===================== 麦肯锡页眉/页脚 =====================
def mck_header(slide, page, total, title, insight):
    """
    麦肯锡风格页眉：
    - 顶部细蓝/橙线
    - 行动型大标题 (action title)
    - 灰色洞察副线 (so-what)
    - 标题与正文之间的水平规则线
    """
    # 顶部品牌细线
    rect(slide, 0, 0, SW, Inches(0.08), PA_ORANGE)

    # 左上角"品牌色块 + 项目名"
    rect(slide, Inches(0.4), Inches(0.22), Inches(0.06), Inches(0.22), PA_ORANGE)
    tb(slide, Inches(0.52), Inches(0.2), Inches(6.0), Inches(0.28),
       "银卡岗位 1+N 数字化转型 · 董事长汇报",
       size=9, bold=True, color=GRAY, anchor=MSO_ANCHOR.MIDDLE)

    # 右上角页码
    tb(slide, Inches(11.4), Inches(0.2), Inches(1.5), Inches(0.28),
       f"PAGE  {page} / {total}",
       size=9, bold=True, color=PA_ORANGE,
       align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

    # 行动标题（action title） — 黑底加粗
    tb(slide, Inches(0.4), Inches(0.55), Inches(12.5), Inches(0.55),
       title, size=20, bold=True, color=INK, anchor=MSO_ANCHOR.MIDDLE,
       line_spacing=1.05)

    # 副线洞察 (so what)
    tb(slide, Inches(0.4), Inches(1.1), Inches(12.5), Inches(0.45),
       insight, size=12, bold=False, color=PA_ORANGE_DARK,
       italic=False, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.2)

    # 分割线（橙色 + 灰色双层）
    rect(slide, Inches(0.4), Inches(1.6), Inches(0.6), Inches(0.04), PA_ORANGE)
    rect(slide, Inches(1.0), Inches(1.62), Inches(11.9), Inches(0.012), LIGHTGRAY)


def mck_footer(slide, source="资料来源 / Source：银卡岗位 1+N 项目组（李祥） · 卢总会 4月数字化实践材料 · 内部访谈"):
    rect(slide, Inches(0.4), Inches(7.18), Inches(12.5), Inches(0.012), LIGHTGRAY)
    tb(slide, Inches(0.4), Inches(7.22), Inches(8.0), Inches(0.22),
       source, size=8.5, color=MIDGRAY, italic=True, anchor=MSO_ANCHOR.TOP)
    tb(slide, Inches(8.4), Inches(7.22), Inches(4.5), Inches(0.22),
       "PING AN · 银卡客服中心 · CONFIDENTIAL",
       size=8.5, bold=True, color=PA_ORANGE,
       align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.TOP)


def kicker(slide, l, t, w, h, label, body):
    """底部金句框（橙色细边 + 浅橙底）"""
    rect(slide, l, t, w, h, PA_ORANGE_BG, line=PA_ORANGE, lw=1.25)
    rect(slide, l, t, Inches(0.08), h, PA_ORANGE)
    tb(slide, l + Inches(0.2), t + Inches(0.05), w - Inches(0.3), Inches(0.28),
       label, size=10, bold=True, color=PA_ORANGE_DARK)
    tb(slide, l + Inches(0.2), t + Inches(0.32), w - Inches(0.3), h - Inches(0.36),
       body, size=11, bold=True, color=INK, line_spacing=1.25)


# ===================== Slide 1：三大目标 =====================
def slide_1():
    s = prs.slides.add_slide(prs.slide_layouts[6])
    white_bg(s)
    mck_header(
        s, 1, 4,
        "银卡岗位 1+N 数字化三大目标：组织有影响 · 项目有成果 · 现场有改善",
        "不是为了数字化而数字化 — 让银卡数字化既能被组织看见，又能形成标杆成果，最终真正改善现场管理与一线作业效率",
    )

    # 三个支柱卡片 — McKinsey columns
    cards = [
        {
            "no": "01", "tag": "组织价值",
            "title": "组织有影响",
            "kw": "有节奏  ·  有露出  ·  有辨识度",
            "report": "提升银卡在总部 / 分公司数字化转型中的战略可见度",
            "actions": [
                "■ 形成季度化成果输出节奏",
                "■ 主动对接卢总会、分公司会、总部数字化条线",
                "■ 把银卡从「项目执行队伍」升级为「数字化样板队伍」",
                "■ 在数字化舞台持续被看见、形成银卡品牌",
            ],
            "metric": "季度上会次数 / 总部数字化条线露出频次",
        },
        {
            "no": "02", "tag": "项目价值",
            "title": "项目有成果",
            "kw": "可申报  ·  可获奖  ·  可复制",
            "report": "打造可申报、可评奖、可复制的标杆案例",
            "actions": [
                "■ 重点项目优先打穿，不平均铺开",
                "■ 数据 / 案例 / 工具 / 机制同步沉淀",
                "■ Q2 冲奖：中台教练、服销现管、知识拆解",
                "■ 形成岗位 1+N 方法论，向更多队伍复制",
            ],
            "metric": "可申报案例数 / 获奖项目数 / 复制覆盖队伍数",
        },
        {
            "no": "03", "tag": "现场价值",
            "title": "现场有改善",
            "kw": "减重复  ·  提质量  ·  促经营",
            "report": "回到一线真实场景，真正推动提质增效与队伍减负",
            "actions": [
                "■ 减少主管重复兜底、重复拉数、重复解释",
                "■ 提升坐席训练效率与新人独立作战速度",
                "■ 稳定服务、经营与高客承载结果",
                "■ 把个人经验转成组织能力",
            ],
            "metric": "主管单日重复动作时长 / 新人独立上岗周期 / 高客承载客户数",
        },
    ]

    card_top = Inches(1.85)
    card_h = Inches(4.5)
    card_w = Inches(4.05)
    gap = Inches(0.13)
    start_x = Inches(0.5)

    for i, c in enumerate(cards):
        x = start_x + (card_w + gap) * i

        # 卡片底
        rect(s, x, card_top, card_w, card_h, WHITE, line=LIGHTGRAY, lw=0.75)
        # 顶部橙色编号块
        rect(s, x, card_top, Inches(1.3), Inches(0.6), PA_ORANGE)
        tb(s, x, card_top, Inches(1.3), Inches(0.6),
           c["no"], size=22, bold=True, color=WHITE,
           align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        # tag 灰底
        rect(s, x + Inches(1.3), card_top, card_w - Inches(1.3), Inches(0.6), PA_ORANGE_BG)
        tb(s, x + Inches(1.4), card_top, card_w - Inches(1.5), Inches(0.6),
           c["tag"], size=11, bold=True, color=PA_ORANGE_DARK,
           anchor=MSO_ANCHOR.MIDDLE)

        # 主标题
        tb(s, x + Inches(0.2), card_top + Inches(0.75), card_w - Inches(0.4),
           Inches(0.55), c["title"], size=24, bold=True, color=INK)

        # 关键词副标
        tb(s, x + Inches(0.2), card_top + Inches(1.3), card_w - Inches(0.4),
           Inches(0.3), c["kw"], size=11, bold=True, color=PA_ORANGE)

        # 分割线
        rect(s, x + Inches(0.2), card_top + Inches(1.65),
             card_w - Inches(0.4), Inches(0.02), LIGHTGRAY)

        # 汇报口径
        tb(s, x + Inches(0.2), card_top + Inches(1.75), card_w - Inches(0.4),
           Inches(0.25), "汇报口径", size=9, bold=True, color=GRAY)
        tb(s, x + Inches(0.2), card_top + Inches(1.98), card_w - Inches(0.4),
           Inches(0.55), c["report"], size=11, bold=True, color=INK,
           line_spacing=1.25)

        # 具体落点
        tb(s, x + Inches(0.2), card_top + Inches(2.6), card_w - Inches(0.4),
           Inches(0.25), "具体落点", size=9, bold=True, color=GRAY)
        tb(s, x + Inches(0.2), card_top + Inches(2.83), card_w - Inches(0.4),
           Inches(1.3), c["actions"], size=10, color=DARK, line_spacing=1.3)

        # 衡量指标
        rect(s, x + Inches(0.2), card_top + Inches(4.13),
             card_w - Inches(0.4), Inches(0.32), PA_ORANGE_LT)
        tb(s, x + Inches(0.3), card_top + Inches(4.13),
           card_w - Inches(0.5), Inches(0.32),
           f"衡量指标   {c['metric']}", size=8.5, bold=True,
           color=PA_ORANGE_DEEP, anchor=MSO_ANCHOR.MIDDLE)

    # 底部金句
    kicker(s, Inches(0.5), Inches(6.55), Inches(12.33), Inches(0.55),
           "FINAL TAKEAWAY",
           "三大目标互为支撑：组织影响是「场」、项目成果是「品」、现场改善是「本」；缺一项，数字化转型都难持续。")
    mck_footer(s)


# ===================== Slide 2：项目池排序 =====================
def slide_2():
    s = prs.slides.add_slide(prs.slide_layouts[6])
    white_bg(s)
    mck_header(
        s, 2, 4,
        "项目池重构：12 个岗位 1+N 分层排序，6 个重点项目优先打穿",
        "排序不按谁先报，而按四标准 — 成熟度 · 痛点强度 · 可复制性 · 上会与获奖潜力",
    )

    # 排序标准条 — 4 个 chip
    chips = [
        ("① 成熟度", "材料/数据已沉淀"),
        ("② 痛点强度", "现场真痛、高频耗时"),
        ("③ 可复制性", "可向更多队伍复制"),
        ("④ 上会/获奖潜力", "可申报、可评奖"),
    ]
    chip_w = Inches(2.95)
    chip_top = Inches(1.7)
    for i, (k, v) in enumerate(chips):
        x = Inches(0.5) + (chip_w + Inches(0.05)) * i
        rect(s, x, chip_top, Inches(0.08), Inches(0.42), PA_ORANGE)
        rect(s, x + Inches(0.08), chip_top, chip_w - Inches(0.08), Inches(0.42), PA_ORANGE_BG)
        tb(s, x + Inches(0.2), chip_top, chip_w - Inches(0.2), Inches(0.42),
           f"{k}   {v}", size=10, bold=True, color=PA_ORANGE_DARK,
           anchor=MSO_ANCHOR.MIDDLE)

    # 主表格
    headers = ["#", "项目", "负责人", "重要性", "排序原因（精要）",
               "历史提报 / 材料基础", "供稿"]
    rows = [
        ["1", "服销现管 1+N", "叶爱娣 / 王凯",  "高",
         "直接对应服销经营结果，解决盯盘/筛人/辅导/闭环耗时",
         "已形成 4 月卢总会数字化实践材料",       "李祥"],
        ["2", "中台/教练岗 1+N", "黄敏 等",     "高",
         "教练辅导从经验型 → 数据识别+训练匹配+效果追踪",
         "已有阶段成果，可包装为 Q2 上奖项目",       "李祥"],
        ["3", "知识拆解岗 1+N", "王晶",         "高",
         "对应智能客服知识生产效率，标准化样板可复制",
         "已形成 3 月卢总会数字化实践材料",       "李祥"],
        ["4", "投诉化解能力提升", "张卫平、文京洛", "高",
         "服务现管真实痛点强，资深主管经验组织化",
         "最近重点研究讨论，新增爆点",               "李祥"],
        ["5", "新人育成 1+N",   "待调研确定",    "高",
         "新人上手慢、知识会背不会用、主管带教耗时",
         "需先完成主管端、新人端调研",               "李祥"],
        ["6", "安心秘书 1+N",   "陈小娟 等",    "高",
         "银卡高客招牌，支撑服务升级、价值经营",
         "已提报安秘相关数字化实践材料",           "李祥"],
        ["7", "顶私坐席 1+N",   "张旭宏、赵书英", "中",
         "基于平安One系统能力，支撑顶私客户经营",
         "已有平安One 客户分析材料基础",           "李祥"],
        ["8", "结清挽留坐席 1+N", "蔡丽莉",      "中",
         "挽留场景有经营转化价值，需沉淀策略模型",
         "待形成案例化成果",                         "李祥"],
        ["9", "私财坐席 1+N",   "鲁晓晓",       "中",
         "可沉淀私财客户服务/触达/经营动作",
         "待孵化",                                   "李祥"],
        ["10", "GVIP 坐席 1+N", "周梦莎",       "中",
         "高端客户服务有价值，需先形成标准化样板",
         "待孵化",                                   "李祥"],
        ["11", "信 SBO 坐席 1+N", "文京洛",     "中低",
         "专业业务有空间，成果颗粒度需进一步验证",
         "待孵化",                                   "李祥"],
        ["12", "对公坐席 1+N",  "王秋梅",       "中低",
         "银行端目标不够清晰，暂不作为主战场",
         "待观察",                                   "李祥"],
    ]
    # 给前 6 行（重点）淡橙底；后 6 行（储备）白底
    row_fills = {i: PA_ORANGE_LT for i in range(6)}
    for i in range(6, 12):
        row_fills[i] = WHITE if i % 2 == 0 else PALE

    mck_table(
        s, Inches(0.5), Inches(2.25), Inches(12.33), Inches(4.0),
        headers, rows,
        col_widths=[0.4, 1.7, 1.5, 0.7, 4.4, 2.8, 0.5],
        header_size=10, body_size=9.5,
        row_fills=row_fills,
    )

    # 左侧分层标识
    rect(s, Inches(0.2), Inches(2.6), Inches(0.18), Inches(1.85), PA_ORANGE)
    tb(s,  Inches(0.18), Inches(2.6), Inches(0.22), Inches(1.85),
       "重\n点", size=10, bold=True, color=WHITE,
       align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.0)

    rect(s, Inches(0.2), Inches(4.5), Inches(0.18), Inches(1.75), PA_ORANGE_DARK)
    tb(s,  Inches(0.18), Inches(4.5), Inches(0.22), Inches(1.75),
       "储\n备", size=10, bold=True, color=WHITE,
       align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, line_spacing=1.0)

    # 底部 Q2 / Q3 / Q4 节奏
    rhythm_top = Inches(6.35)
    rhythm_h = Inches(0.7)
    qs = [
        ("Q2", "冲奖样板", "中台教练 · 服销现管 · 知识拆解", PA_ORANGE),
        ("Q3", "新增爆点", "投诉化解 · 新人育成 · 安心秘书", PA_ORANGE_DARK),
        ("Q4", "盘点升级", "顶私 · 私财 · GVIP · 结清挽留 · 信 SBO · 对公", PA_ORANGE_DEEP),
    ]
    qw = Inches(4.06)
    for i, (q, lbl, body, c) in enumerate(qs):
        x = Inches(0.5) + (qw + Inches(0.08)) * i
        rect(s, x, rhythm_top, qw, rhythm_h, WHITE, line=c, lw=1.2)
        rect(s, x, rhythm_top, Inches(0.85), rhythm_h, c)
        tb(s, x, rhythm_top, Inches(0.85), rhythm_h, q,
           size=22, bold=True, color=WHITE,
           align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        tb(s, x + Inches(0.95), rhythm_top + Inches(0.05),
           qw - Inches(1.0), Inches(0.3),
           lbl, size=11, bold=True, color=c)
        tb(s, x + Inches(0.95), rhythm_top + Inches(0.32),
           qw - Inches(1.0), Inches(0.4),
           body, size=9.5, bold=True, color=DARK, line_spacing=1.2)

    mck_footer(s)


# ===================== Slide 3：推进机制 =====================
def slide_3():
    s = prs.slides.add_slide(prs.slide_layouts[6])
    white_bg(s)
    mck_header(
        s, 3, 4,
        "推进机制：李祥控总盘 · 责任人交付成果 · 按季度形成上会与获奖节奏",
        "不靠临时催材料 — 建立「总盘统筹 + 项目主责 + 月度复盘 + 季度交付」的常态化机制",
    )

    # 2x2 quadrants
    quads = [
        # 1 责任体系
        {"x": Inches(0.5),  "y": Inches(1.85), "w": Inches(6.16), "h": Inches(2.6),
         "no": "WHO", "title": "责任体系（统筹 + 主责 + 兜底）",
         "type": "table",
         "headers": ["角色", "职责"],
         "col_widths": [2, 5],
         "rows": [
             ["李祥",        "控总盘 · 定节奏 · 抓材料 · 对接业管/总部数字化/获奖机会"],
             ["李琦、花蕊",  "分工介入项目推进 · 解决主管卡点 · 推动过程落地"],
             ["管总",        "关键项目兜底 · 资源协调 · 方向把关"],
             ["项目责任人",  "提供真实场景 · 推动一线试点 · 沉淀案例与数据"],
             ["骨干 / 坐席", "参与试用 · 反馈场景 · 验证工具是否真正有用"],
         ]},
        # 2 推进节奏
        {"x": Inches(6.83), "y": Inches(1.85), "w": Inches(6.0), "h": Inches(2.6),
         "no": "WHEN", "title": "推进节奏（周 → 月 → 季 → 年）",
         "type": "table",
         "headers": ["周期", "动作", "输出"],
         "col_widths": [1.2, 2.5, 3],
         "rows": [
             ["每周",   "项目轻量跟进",        "进展 / 卡点 / 下周动作"],
             ["每月",   "A 类项目复盘",        "阶段成果 / 数据变化 / 试点反馈"],
             ["每季度", "项目成果输出",        "上会材料 / 获奖材料 / 案例沉淀"],
             ["年底",   "项目总评",            "复制 / 升级 / 淘汰决策"],
         ]},
        # 3 5类交付物
        {"x": Inches(0.5),  "y": Inches(4.55), "w": Inches(6.16), "h": Inches(2.55),
         "no": "WHAT", "title": "每个项目必须交付的 5 类东西",
         "type": "table",
         "headers": ["交付物", "说明"],
         "col_widths": [2, 5],
         "rows": [
             ["场景清单",      "高频 / 耗时 / 痛苦动作清单"],
             ["工具 / 模板",   "看板 · 话术库 · 训练助手 · 知识拆解模板"],
             ["试点记录",      "谁在用 · 怎么用 · 用了几次"],
             ["效果数据",      "节省时间 · 质量 · 经营 · 风险变化"],
             ["汇报材料",      "卢总会 / 分公司会 / 总部数字化 / 奖项申报"],
         ]},
        # 4 季度安排
        {"x": Inches(6.83), "y": Inches(4.55), "w": Inches(6.0), "h": Inches(2.55),
         "no": "SEQUENCE", "title": "季度主攻与目标",
         "type": "table",
         "headers": ["季度", "主攻项目", "目标 / 核心交付"],
         "col_widths": [1, 3, 3.5],
         "rows": [
             ["Q2", "中台教练 · 服销现管 · 知识拆解",
              "上奖台 — 三套数字化实践材料 + 数据佐证"],
             ["Q3", "投诉化解 · 新人育成 · 安心秘书",
              "新增亮点 — 服务提效 / 育成提速 / 高客产能"],
             ["Q4", "顶私 · 私财 · GVIP · 结清挽留 · 信 SBO · 对公",
              "专业坐席项目盘点 — 升级 / 降级 / 收口"],
         ]},
    ]

    for q in quads:
        # 卡片底
        rect(s, q["x"], q["y"], q["w"], q["h"], WHITE,
             line=LIGHTGRAY, lw=0.75)
        # 顶部小标 + WHO/WHEN/WHAT/SEQUENCE
        rect(s, q["x"], q["y"], q["w"], Inches(0.42), PA_ORANGE_BG)
        rect(s, q["x"], q["y"], Inches(0.06), Inches(0.42), PA_ORANGE)
        tb(s, q["x"] + Inches(0.18), q["y"], Inches(1.5), Inches(0.42),
           q["no"], size=10, bold=True, color=PA_ORANGE_DARK,
           anchor=MSO_ANCHOR.MIDDLE)
        tb(s, q["x"] + Inches(1.4), q["y"], q["w"] - Inches(1.5), Inches(0.42),
           q["title"], size=12, bold=True, color=INK, anchor=MSO_ANCHOR.MIDDLE)
        # 内嵌表
        tbl_top = q["y"] + Inches(0.5)
        tbl_h = q["h"] - Inches(0.6)
        mck_table(
            s, q["x"] + Inches(0.15), tbl_top,
            q["w"] - Inches(0.3), tbl_h,
            q["headers"], q["rows"],
            col_widths=q["col_widths"],
            header_size=9.5, body_size=9,
        )

    # 底部金句条
    kicker(s, Inches(0.5), Inches(7.18 - 0.05) - Inches(0.5),
           Inches(12.33), Inches(0.45),
           "GOVERNANCE TAKEAWAY",
           "每个重点项目都有责任人 · 有交付物 · 有节奏 · 有验证指标 — 数字化推进从「靠催」走向「靠机制」。")
    mck_footer(s)


# ===================== Slide 4：投诉化解 =====================
def slide_4():
    s = prs.slides.add_slide(prs.slide_layouts[6])
    white_bg(s)
    mck_header(
        s, 4, 4,
        "最新突破：投诉化解能力数字化 — 推动服务现管从「个人兜底」走向「组织化化解」",
        "不是再做一个话术库 — 把张卫平等资深主管的隐性经验，拆解为场景 · 风险 · 话术 · 案例 · 训练 · 复盘的可复制能力",
    )

    # 上：6 模块卡片（2行3列）
    modules = [
        ("01", "场景分类",   "账单 / 态度 / 承诺 / 产品误解 / 重复来电…", "投诉场景清单"),
        ("02", "风险识别",   "普通不满 / 升级 / 监管 / 舆情",            "风险分级表"),
        ("03", "化解话术",   "情绪承接 → 事实确认 → 方案 → 收口",         "主管话术库"),
        ("04", "案例沉淀",   "典型案例 / 错误动作 / 正确处理 / 要点",      "案例库"),
        ("05", "员工训练",   "人机对练 / 情景判断 / 禁忌识别",             "训练题库 + 陪练脚本"),
        ("06", "复盘闭环",   "处理结果 / 风险原因 / 是否可预防",           "复盘模板"),
    ]
    mod_top = Inches(1.85)
    mod_w = Inches(4.05)
    mod_h = Inches(1.05)
    gap_x = Inches(0.13)
    gap_y = Inches(0.1)
    for i, (no, name, desc, deliver) in enumerate(modules):
        col = i % 3
        row = i // 3
        x = Inches(0.5) + (mod_w + gap_x) * col
        y = mod_top + (mod_h + gap_y) * row
        rect(s, x, y, mod_w, mod_h, WHITE, line=PA_ORANGE_LT, lw=1.0)
        # 左侧编号块
        rect(s, x, y, Inches(0.7), mod_h, PA_ORANGE)
        tb(s, x, y, Inches(0.7), mod_h, no,
           size=18, bold=True, color=WHITE,
           align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        tb(s, x + Inches(0.82), y + Inches(0.08),
           mod_w - Inches(0.9), Inches(0.3),
           name, size=12, bold=True, color=INK)
        tb(s, x + Inches(0.82), y + Inches(0.38),
           mod_w - Inches(0.9), Inches(0.4),
           desc, size=9, color=DARK, line_spacing=1.2)
        # 交付物标签
        rect(s, x + Inches(0.82), y + Inches(0.76),
             mod_w - Inches(0.9), Inches(0.22), PA_ORANGE_BG)
        tb(s, x + Inches(0.92), y + Inches(0.76),
           mod_w - Inches(1.0), Inches(0.22),
           f"交付  {deliver}", size=8.5, bold=True,
           color=PA_ORANGE_DARK, anchor=MSO_ANCHOR.MIDDLE)

    # 下：FROM → TO 价值表
    val_top = Inches(4.25)
    headers = ["原来（FROM）", "数字化后（TO）", "对谁产生价值"]
    rows = [
        ["投诉靠主管现场判断",         "场景分类库 + 风险识别规则",            "新主管 / 坐席能先判断风险等级"],
        ["张卫平个人经验口口相传",     "话术库 / 案例库 / 处理路径",            "个人能力 → 组织能力"],
        ["员工一遇投诉就升级",         "训练工具学习常见场景",                 "减少低价值主管兜底"],
        ["事后口头提醒式复盘",         "标准复盘模板",                         "同类问题可沉淀、可预防"],
        ["培训只讲原则",               "真实投诉案例 + 人机演练",              "员工从「知道」到「会说会判断」"],
        ["主管反复解释同类问题",       "AI 助手先给处理建议与话术框架",        "节省主管重复沟通时间"],
    ]
    mck_table(
        s, Inches(0.5), val_top, Inches(8.35), Inches(2.05),
        headers, rows,
        col_widths=[2.7, 3.0, 3.0],
        header_size=10, body_size=9,
        first_col_bold=False,
    )
    # 表头上方一根分隔/小标
    tb(s, Inches(0.5), val_top - Inches(0.32),
       Inches(8.35), Inches(0.28),
       "▍ FROM → TO   |   关键变化与价值落点",
       size=11, bold=True, color=PA_ORANGE_DARK)

    # 右下：4 类受益方
    ben_x = Inches(8.95)
    ben_y = val_top - Inches(0.32)
    rect(s, ben_x, ben_y, Inches(3.88), Inches(0.32), PA_ORANGE)
    tb(s, ben_x, ben_y, Inches(3.88), Inches(0.32),
       "▍ 四类受益方", size=11, bold=True, color=WHITE,
       align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    bens = [
        ("服务现管", "重复兜底下降 · 转向「训练团队」"),
        ("一线员工", "投诉敏感度↑ · 不再一遇就升级"),
        ("客  户",    "二次升级↓ · 被重视感↑"),
        ("组  织",    "经验复制 · 风险识别 · 方法推广"),
    ]
    bh = Inches(0.49)
    for i, (k, v) in enumerate(bens):
        y = val_top + bh * i
        rect(s, ben_x, y, Inches(3.88), bh,
             WHITE if i % 2 == 0 else PA_ORANGE_BG)
        rect(s, ben_x, y, Inches(0.06), bh, PA_ORANGE)
        tb(s, ben_x + Inches(0.15), y, Inches(1.1), bh,
           k, size=11, bold=True, color=PA_ORANGE_DARK,
           anchor=MSO_ANCHOR.MIDDLE)
        tb(s, ben_x + Inches(1.3), y, Inches(2.55), bh,
           v, size=9.5, color=DARK, anchor=MSO_ANCHOR.MIDDLE,
           line_spacing=1.2)

    # 底部金句
    kicker(s, Inches(0.5), Inches(6.5), Inches(12.33), Inches(0.6),
           "STRATEGIC TAKEAWAY",
           "投诉化解项目的真正价值不在「话术」 — 而在把资深主管的隐性经验组织化，提升整个服务现场的风险识别与问题化解能力。")
    mck_footer(s)


# ===== 生成 =====
slide_1()
slide_2()
slide_3()
slide_4()

out = "/projects/sandbox/kiro2026/银卡岗位1+N数字化转型_麦肯锡4页版.pptx"
prs.save(out)
print(f"已生成: {out}")
print(f"共 {len(prs.slides)} 页")
