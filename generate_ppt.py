# -*- coding: utf-8 -*-
"""
银卡岗位 1+N 数字化转型实践 - 董事长汇报
平安橙色主题 + 白色底板
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from copy import deepcopy
from lxml import etree

# ===== 平安橙色主题 =====
PA_ORANGE = RGBColor(0xEC, 0x6F, 0x1C)        # 主橙色
PA_ORANGE_DARK = RGBColor(0xC8, 0x55, 0x0E)   # 深橙
PA_ORANGE_LIGHT = RGBColor(0xFF, 0xE8, 0xD2)  # 浅橙底
PA_ORANGE_BG = RGBColor(0xFF, 0xF5, 0xEB)     # 极浅橙
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BLACK = RGBColor(0x1A, 0x1A, 0x1A)
DARK_GRAY = RGBColor(0x33, 0x33, 0x33)
GRAY = RGBColor(0x66, 0x66, 0x66)
LIGHT_GRAY = RGBColor(0xE5, 0xE5, 0xE5)

CN_FONT = "Microsoft YaHei"
EN_FONT = "Calibri"

# 16:9 widescreen
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

SLIDE_W = prs.slide_width
SLIDE_H = prs.slide_height


def set_run(run, text, size=14, bold=False, color=BLACK, font=CN_FONT):
    run.text = text
    run.font.name = font
    # 中文字体
    rPr = run._r.get_or_add_rPr()
    eaFont = rPr.find(qn('a:ea'))
    if eaFont is None:
        eaFont = etree.SubElement(rPr, qn('a:ea'))
    eaFont.set('typeface', CN_FONT)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


def add_textbox(slide, left, top, width, height, text, size=14, bold=False,
                color=BLACK, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font=CN_FONT):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Emu(0)
    tf.margin_right = Emu(0)
    tf.margin_top = Emu(0)
    tf.margin_bottom = Emu(0)
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    if isinstance(text, list):
        for i, t in enumerate(text):
            if i == 0:
                run = p.add_run()
            else:
                p2 = tf.add_paragraph()
                p2.alignment = align
                run = p2.add_run()
            set_run(run, t, size=size, bold=bold, color=color, font=font)
    else:
        run = p.add_run()
        set_run(run, text, size=size, bold=bold, color=color, font=font)
    return tb


def add_rect(slide, left, top, width, height, fill_color, line_color=None, line_width=0):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(line_width)
    shape.shadow.inherit = False
    return shape


def add_white_bg(slide):
    """白色底板"""
    bg = add_rect(slide, 0, 0, SLIDE_W, SLIDE_H, WHITE)
    bg.shadow.inherit = False
    return bg


def add_header(slide, title, subtitle=None, page_num=None, total_pages=9):
    """标准页头：左侧橙色竖条 + 标题；右上页码"""
    # 顶部橙色细条
    add_rect(slide, 0, 0, SLIDE_W, Inches(0.12), PA_ORANGE)
    # 左侧橙色竖块
    add_rect(slide, Inches(0.45), Inches(0.45), Inches(0.12), Inches(0.55), PA_ORANGE)
    # 标题
    add_textbox(slide, Inches(0.7), Inches(0.4), Inches(11.5), Inches(0.55),
                title, size=24, bold=True, color=PA_ORANGE_DARK, anchor=MSO_ANCHOR.MIDDLE)
    # 副标题
    if subtitle:
        add_textbox(slide, Inches(0.7), Inches(0.95), Inches(11.5), Inches(0.4),
                    subtitle, size=12, bold=False, color=GRAY)
    # 页码
    if page_num is not None:
        add_textbox(slide, Inches(11.8), Inches(0.45), Inches(1.3), Inches(0.4),
                    f"{page_num} / {total_pages}", size=11, bold=True,
                    color=PA_ORANGE, align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
    # 页头分割线
    add_rect(slide, Inches(0.45), Inches(1.4), Inches(12.5), Inches(0.02), PA_ORANGE_LIGHT)


def add_footer(slide, text="银卡岗位 1+N 数字化转型 · 董事长汇报"):
    add_rect(slide, 0, Inches(7.35), SLIDE_W, Inches(0.15), PA_ORANGE)
    add_textbox(slide, Inches(0.5), Inches(7.05), Inches(12.3), Inches(0.3),
                text, size=10, color=GRAY, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE)


# ============= 表格工具 =============
def add_table(slide, left, top, width, height, headers, rows,
              header_fill=PA_ORANGE, header_font=WHITE,
              row_alt_fill=PA_ORANGE_BG, header_size=12, body_size=10.5,
              col_widths=None):
    n_rows = len(rows) + 1
    n_cols = len(headers)
    tbl_shape = slide.shapes.add_table(n_rows, n_cols, left, top, width, height)
    tbl = tbl_shape.table

    # 列宽
    if col_widths:
        total = sum(col_widths)
        for i, w in enumerate(col_widths):
            tbl.columns[i].width = int(width * w / total)

    # 表头
    for ci, h in enumerate(headers):
        cell = tbl.cell(0, ci)
        cell.fill.solid()
        cell.fill.fore_color.rgb = header_fill
        cell.margin_left = Inches(0.08)
        cell.margin_right = Inches(0.08)
        cell.margin_top = Inches(0.04)
        cell.margin_bottom = Inches(0.04)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        set_run(run, h, size=header_size, bold=True, color=header_font)

    # 数据行
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = tbl.cell(ri + 1, ci)
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if ri % 2 == 0 else row_alt_fill
            cell.margin_left = Inches(0.08)
            cell.margin_right = Inches(0.08)
            cell.margin_top = Inches(0.04)
            cell.margin_bottom = Inches(0.04)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if ci > 0 else PP_ALIGN.CENTER
            run = p.add_run()
            set_run(run, val, size=body_size, color=DARK_GRAY)

    return tbl_shape


# ============= Slide 1: 总标题页 =============
def slide_1():
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # 空白
    add_white_bg(slide)

    # 左侧大橙色色块
    add_rect(slide, 0, 0, Inches(0.45), SLIDE_H, PA_ORANGE)
    # 顶部小橙带
    add_rect(slide, Inches(0.45), 0, SLIDE_W - Inches(0.45), Inches(0.18), PA_ORANGE_LIGHT)

    # 主标题
    add_textbox(slide, Inches(1.0), Inches(2.0), Inches(11.5), Inches(0.5),
                "银卡岗位 1+N 数字化转型实践", size=18, bold=True,
                color=GRAY)
    add_textbox(slide, Inches(1.0), Inches(2.5), Inches(11.5), Inches(1.3),
                "从单点工具到岗位能力重构", size=44, bold=True,
                color=PA_ORANGE_DARK)

    # 橙色装饰横条
    add_rect(slide, Inches(1.0), Inches(3.95), Inches(2.5), Inches(0.08), PA_ORANGE)

    # 副标题
    add_textbox(slide, Inches(1.0), Inches(4.15), Inches(11.5), Inches(1.0),
                "围绕现场管理、服务化解、知识生产、新人育成、高客经营、专业坐席等关键岗位，",
                size=15, color=DARK_GRAY)
    add_textbox(slide, Inches(1.0), Inches(4.5), Inches(11.5), Inches(0.5),
                "构建可复制、可度量、可推广的客服中心数字化工作链路。",
                size=15, color=DARK_GRAY)

    # 主判断框
    add_rect(slide, Inches(1.0), Inches(5.4), Inches(11.3), Inches(1.1), PA_ORANGE_BG,
             line_color=PA_ORANGE, line_width=1.5)
    add_textbox(slide, Inches(1.3), Inches(5.5), Inches(10.7), Inches(0.4),
                "核 心 主 张", size=12, bold=True, color=PA_ORANGE_DARK)
    add_textbox(slide, Inches(1.3), Inches(5.85), Inches(10.7), Inches(0.6),
                "不是简单上工具，而是把依赖个人经验的岗位，改造成可沉淀、可训练、可复用、可追踪的数字化能力。",
                size=14, bold=True, color=BLACK)

    # 底部信息
    add_rect(slide, 0, Inches(7.0), SLIDE_W, Inches(0.5), PA_ORANGE)
    add_textbox(slide, Inches(1.0), Inches(7.05), Inches(11.3), Inches(0.4),
                "客服中心 · 银卡岗位数字化项目组   |   向董事长专项汇报",
                size=12, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)


# ============= Slide 2: 为什么必须做 =============
def slide_2():
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_white_bg(slide)
    add_header(slide,
               "为什么必须做：客服中心正在从「人海管理」进入「岗位能力重构」",
               "传统岗位模式已难以承接新的业务压力", page_num=2)

    # 引言
    add_textbox(slide, Inches(0.5), Inches(1.5), Inches(12.3), Inches(0.45),
                "核心矛盾：不是员工不努力，也不是主管不会管，而是「依赖经验、依赖人力、依赖加班」的旧模式已到极限。",
                size=13, bold=True, color=PA_ORANGE_DARK)

    # 压力来源表
    headers = ["压力来源", "真实表现", "传统方式的问题"]
    rows = [
        ["服务压力", "投诉、升级、复杂客诉增多", "依赖资深主管个人经验"],
        ["经营压力", "服销、私财、高客、挽留任务叠加", "一线执行动作不稳定"],
        ["人力压力", "客户规模增长快于人员增长", "靠加人、加班不可持续"],
        ["培训压力", "新人上手慢、专业岗位要求高", "培训材料多，实战转化慢"],
        ["知识压力", "政策、产品、流程变化快", "知识拆解靠人工，效率低"],
        ["管理压力", "多岗位、多指标、多条线协同", "主管精力被切碎，难以精细管理"],
    ]
    add_table(slide, Inches(0.5), Inches(2.05), Inches(12.3), Inches(3.4),
              headers, rows, col_widths=[2, 5, 5], header_size=13, body_size=12)

    # 底部判断框
    add_rect(slide, Inches(0.5), Inches(5.7), Inches(12.3), Inches(1.25),
             PA_ORANGE_BG, line_color=PA_ORANGE, line_width=1.5)
    add_textbox(slide, Inches(0.75), Inches(5.8), Inches(11.8), Inches(0.4),
                "管 理 模 式 升 级 · 不 是 小 创 新", size=12, bold=True, color=PA_ORANGE_DARK)
    add_textbox(slide, Inches(0.75), Inches(6.15), Inches(11.8), Inches(0.85),
                "过去靠主管经验、员工熟练度、人力堆叠来解决问题；现在必须把岗位能力拆出来、沉淀下来、工具化、标准化，再复制到更多队伍。",
                size=13, bold=True, color=BLACK)
    add_footer(slide)


# ============= Slide 3: 总体打法 =============
def slide_3():
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_white_bg(slide)
    add_header(slide,
               "总体打法：12 个项目分层推进，6 个重点打穿，6 个保持探索",
               "形成银卡岗位 1+N 的主攻矩阵 + 场景储备池", page_num=3)

    # 左侧：6个重点项目
    add_rect(slide, Inches(0.5), Inches(1.55), Inches(6.1), Inches(0.45), PA_ORANGE)
    add_textbox(slide, Inches(0.6), Inches(1.55), Inches(6.0), Inches(0.45),
                "■ 重点 6 个项目（主攻打穿）", size=14, bold=True,
                color=WHITE, anchor=MSO_ANCHOR.MIDDLE)

    key_headers = ["#", "重点项目", "项目定位", "负责人"]
    key_rows = [
        ["1", "服销现管 1+N", "服销现场管理与过程管控", "叶爱娣 / 王凯"],
        ["2", "投诉化解能力提升", "服务现管投诉化解与员工辅导", "张卫平、文京洛"],
        ["3", "新人育成 1+N", "缩短新人独立作战周期", "待调研确定"],
        ["4", "中台/教练岗 1+N", "教练辅导链路重构", "黄敏 等"],
        ["5", "安心秘书 1+N", "高客服务升级与价值经营", "陈小娟 等"],
        ["6", "知识拆解岗 1+N", "智能客服知识生产与运维", "王晶"],
    ]
    add_table(slide, Inches(0.5), Inches(2.05), Inches(6.1), Inches(3.4),
              key_headers, key_rows, col_widths=[0.5, 2, 2.5, 2],
              header_size=11, body_size=10)

    # 右侧：6个探索项目
    add_rect(slide, Inches(6.75), Inches(1.55), Inches(6.1), Inches(0.45), PA_ORANGE_DARK)
    add_textbox(slide, Inches(6.85), Inches(1.55), Inches(6.0), Inches(0.45),
                "■ 探索 6 个项目（场景储备池）", size=14, bold=True,
                color=WHITE, anchor=MSO_ANCHOR.MIDDLE)

    exp_headers = ["#", "探索项目", "负责人", "当前定位"]
    exp_rows = [
        ["1", "GVIP 坐席 1+N", "周梦莎", "高端客户服务场景"],
        ["2", "对公坐席 1+N", "王秋梅", "对公与个人价值衔接"],
        ["3", "信 SBO 坐席 1+N", "文京洛", "专业业务坐席沉淀"],
        ["4", "顶私坐席 1+N", "张旭宏、赵书英", "基于平安One支持顶私经营"],
        ["5", "结清挽留坐席 1+N", "蔡丽莉", "挽留话术与转化"],
        ["6", "私财坐席 1+N", "鲁晓晓", "私财服务经营动作"],
    ]
    add_table(slide, Inches(6.75), Inches(2.05), Inches(6.1), Inches(3.4),
              exp_headers, exp_rows, col_widths=[0.5, 2.2, 1.5, 2.8],
              header_fill=PA_ORANGE_DARK,
              header_size=11, body_size=10)

    # 底部关键话术
    add_rect(slide, Inches(0.5), Inches(5.7), Inches(12.35), Inches(1.25),
             PA_ORANGE_BG, line_color=PA_ORANGE, line_width=1.5)
    add_textbox(slide, Inches(0.75), Inches(5.8), Inches(11.8), Inches(0.4),
                "不 平 均 用 力 · 重 点 打 穿 · 储 备 升 级", size=12,
                bold=True, color=PA_ORANGE_DARK)
    add_textbox(slide, Inches(0.75), Inches(6.15), Inches(11.8), Inches(0.85),
                "重点项目用于形成可汇报、可复制、可推广的岗位数字化样板；探索项目用于覆盖更多专业坐席场景，发现成熟后可动态升级为重点项目。",
                size=12, bold=True, color=BLACK)
    add_footer(slide)


# ============= Slide 4: 服销现管 1+N =============
def slide_4():
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_white_bg(slide)
    add_header(slide,
               "重点项目一 · 服销现管 1+N",
               "把服销过程管理从「人工盯盘」升级为「数据驱动的现场经营管理」", page_num=4)

    # 左：现状痛点
    add_rect(slide, Inches(0.5), Inches(1.55), Inches(6.1), Inches(0.4), PA_ORANGE)
    add_textbox(slide, Inches(0.6), Inches(1.55), Inches(6.0), Inches(0.4),
                "▍ 现状痛点", size=13, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    pain_h = ["现状", "问题"]
    pain_r = [
        ["主管靠经验盯服销数据", "发现问题不够及时"],
        ["尾部人员识别靠人工筛选", "耗时，且容易漏人"],
        ["服销辅导依赖主管个人判断", "辅导动作不稳定"],
        ["过程追踪散在表格、群、口头", "无法形成闭环"],
        ["业管有要求，现管负责落地", "中间执行断点多"],
    ]
    add_table(slide, Inches(0.5), Inches(1.95), Inches(6.1), Inches(2.6),
              pain_h, pain_r, col_widths=[3, 3], header_size=11, body_size=10)

    # 右：数字化动作
    add_rect(slide, Inches(6.75), Inches(1.55), Inches(6.1), Inches(0.4), PA_ORANGE)
    add_textbox(slide, Inches(6.85), Inches(1.55), Inches(6.0), Inches(0.4),
                "▍ 数字化动作", size=13, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    act_h = ["模块", "作用"]
    act_r = [
        ["服销数据看板", "自动识别团队/个人/时段异常"],
        ["尾部人员预警", "找出百产、转化率、高价值落后人员"],
        ["辅导建议助手", "根据问题类型推荐辅导动作"],
        ["跟进闭环表", "记录是否触达、复盘、改善"],
        ["优秀案例沉淀", "把绩优打法转成训练素材"],
    ]
    add_table(slide, Inches(6.75), Inches(1.95), Inches(6.1), Inches(2.6),
              act_h, act_r, col_widths=[2.5, 3.5], header_size=11, body_size=10)

    # 价值表
    add_rect(slide, Inches(0.5), Inches(4.7), Inches(12.35), Inches(0.4), PA_ORANGE_DARK)
    add_textbox(slide, Inches(0.6), Inches(4.7), Inches(12.2), Inches(0.4),
                "▍ 项目价值（给老板看）", size=13, bold=True, color=WHITE,
                anchor=MSO_ANCHOR.MIDDLE)
    val_h = ["价值维度", "具体说明"]
    val_r = [
        ["提升服销过程管理效率", "主管少花时间拉数、筛人、催进度"],
        ["提升尾部改善精准度", "从平均辅导变成问题分类辅导"],
        ["提升业管要求落地率", "把要求变成现场可执行动作"],
        ["提升经营结果稳定性", "过程稳，结果才稳"],
    ]
    add_table(slide, Inches(0.5), Inches(5.1), Inches(12.35), Inches(1.4),
              val_h, val_r, col_widths=[3, 9],
              header_fill=PA_ORANGE_DARK, header_size=11, body_size=10.5)

    # 老板引导语
    add_rect(slide, Inches(0.5), Inches(6.6), Inches(12.35), Inches(0.45),
             PA_ORANGE_BG, line_color=PA_ORANGE, line_width=1)
    add_textbox(slide, Inches(0.7), Inches(6.6), Inches(12.0), Inches(0.45),
                "■ 服销结果不是月底看出来的，而是每天过程管理做出来的——靠数据识别问题、靠工具推动辅导、靠闭环追踪结果。",
                size=11.5, bold=True, color=PA_ORANGE_DARK, anchor=MSO_ANCHOR.MIDDLE)
    add_footer(slide)


# ============= Slide 5: 投诉化解能力提升 =============
def slide_5():
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_white_bg(slide)
    add_header(slide,
               "重点项目二 · 投诉化解能力提升",
               "把资深服务现管的隐性经验沉淀为可复用的化解能力", page_num=5)

    # 左：现状痛点
    add_rect(slide, Inches(0.5), Inches(1.55), Inches(6.1), Inches(0.4), PA_ORANGE)
    add_textbox(slide, Inches(0.6), Inches(1.55), Inches(6.0), Inches(0.4),
                "▍ 现状痛点", size=13, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    pain_h = ["现状", "问题"]
    pain_r = [
        ["投诉处理高度依赖资深主管", "张卫平等长期被占用"],
        ["投诉风险判断靠经验", "新主管/新员工不易掌握"],
        ["典型案例没有系统沉淀", "同类问题反复发生"],
        ["员工遇投诉就找主管", "主管被低价值兜底拖住"],
        ["化解话术不统一", "服务风险与客户感知不稳"],
    ]
    add_table(slide, Inches(0.5), Inches(1.95), Inches(6.1), Inches(2.6),
              pain_h, pain_r, col_widths=[3, 3], header_size=11, body_size=10)

    # 右：数字化动作
    add_rect(slide, Inches(6.75), Inches(1.55), Inches(6.1), Inches(0.4), PA_ORANGE)
    add_textbox(slide, Inches(6.85), Inches(1.55), Inches(6.0), Inches(0.4),
                "▍ 数字化动作", size=13, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    act_h = ["模块", "内容"]
    act_r = [
        ["投诉场景分类库", "账单/产品/态度/承诺/重复来电…"],
        ["风险等级识别", "普通/升级/监管/舆情风险"],
        ["化解话术助手", "提供主管可用的话术框架"],
        ["典型案例库", "把张卫平等人经验拆成案例"],
        ["员工训练 + 复盘模板", "真实场景演练 + 结案沉淀"],
    ]
    add_table(slide, Inches(6.75), Inches(1.95), Inches(6.1), Inches(2.6),
              act_h, act_r, col_widths=[2.5, 3.5], header_size=11, body_size=10)

    # 关键人物 + 价值
    # 关键人物
    add_rect(slide, Inches(0.5), Inches(4.7), Inches(6.1), Inches(0.4), PA_ORANGE_DARK)
    add_textbox(slide, Inches(0.6), Inches(4.7), Inches(6.0), Inches(0.4),
                "▍ 关键人物打法", size=13, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    p_h = ["人员", "角色"]
    p_r = [
        ["张卫平", "投诉化解专家样本（输出经验/案例/风险逻辑）"],
        ["文京洛", "协助整理、试点推广、员工训练"],
        ["李祥 / 李琦", "项目提炼、资源协调、机制推动"],
    ]
    add_table(slide, Inches(0.5), Inches(5.1), Inches(6.1), Inches(1.5),
              p_h, p_r, col_widths=[1.5, 4.6],
              header_fill=PA_ORANGE_DARK, header_size=11, body_size=10)

    # 价值
    add_rect(slide, Inches(6.75), Inches(4.7), Inches(6.1), Inches(0.4), PA_ORANGE_DARK)
    add_textbox(slide, Inches(6.85), Inches(4.7), Inches(6.0), Inches(0.4),
                "▍ 项目价值", size=13, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    v_h = ["价值", "说明"]
    v_r = [
        ["降低主管重复兜底", "常见投诉由工具与案例先行消化"],
        ["前置识别投诉风险", "不等客户升级再处理"],
        ["复制资深主管经验", "个人能力 → 组织能力"],
        ["降低声誉/消保风险", "投诉处理更标准更稳"],
    ]
    add_table(slide, Inches(6.75), Inches(5.1), Inches(6.1), Inches(1.5),
              v_h, v_r, col_widths=[2, 4.1],
              header_fill=PA_ORANGE_DARK, header_size=11, body_size=10)

    # 关键论断
    add_rect(slide, Inches(0.5), Inches(6.7), Inches(12.35), Inches(0.4),
             PA_ORANGE_BG, line_color=PA_ORANGE, line_width=1)
    add_textbox(slide, Inches(0.7), Inches(6.7), Inches(12.0), Inches(0.4),
                "■ 不是再做一个话术库，而是把张卫平这类资深主管的隐性经验，转化为团队可训练、可复制、可追踪的服务能力。",
                size=11.5, bold=True, color=PA_ORANGE_DARK, anchor=MSO_ANCHOR.MIDDLE)
    add_footer(slide)


# ============= Slide 6: 重点项目三~六 =============
def slide_6():
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_white_bg(slide)
    add_header(slide,
               "重点项目三 ~ 六 · 四类关键岗位能力重构",
               "从培训、辅导、高客服务到知识生产 — 全面提效", page_num=6)

    # 大表
    headers = ["项目", "当前痛点", "数字化方向", "预期价值", "关键词"]
    rows = [
        ["新人育成 1+N",
         "新人上手慢，知识会背不会用，实战场景弱",
         "刷题训练、人机对战、场景演练、主管复盘",
         "缩短育成周期，降低新人成本",
         "育成提速"],
        ["中台/教练岗 1+N",
         "辅导靠经验，问题识别和改善追踪不闭环",
         "数据识别、问题诊断、训练匹配、效果追踪",
         "提升辅导精准度和尾部改善率",
         "辅导闭环"],
        ["安心秘书 1+N",
         "高客规模增长快，人力难同比增长",
         "服务升级、价值经营、提质增效、坐席场景共创",
         "提升高客服务承载力和价值经营能力",
         "高客产能"],
        ["知识拆解岗 1+N",
         "智能客服知识生产靠人工，效率/一致性不足",
         "知识拆解模板、意图识别、知识校验、运维闭环",
         "提升智能客服知识生产效率与准确率",
         "知识效率"],
    ]
    add_table(slide, Inches(0.5), Inches(1.6), Inches(12.35), Inches(4.2),
              headers, rows, col_widths=[2, 3.2, 3.5, 2.8, 1.5],
              header_size=12, body_size=11)

    # 底部解读框
    add_rect(slide, Inches(0.5), Inches(6.0), Inches(12.35), Inches(0.95),
             PA_ORANGE_BG, line_color=PA_ORANGE, line_width=1.5)
    add_textbox(slide, Inches(0.75), Inches(6.05), Inches(11.8), Inches(0.35),
                "■ 客服中心未来组织能力的底层建设", size=12, bold=True, color=PA_ORANGE_DARK)
    add_textbox(slide, Inches(0.75), Inches(6.4), Inches(11.8), Inches(0.55),
                "新人怎么更快成才 · 教练怎么更精准辅导 · 高客怎么在规模增长下保持服务质量 · 智能客服知识怎么更快生产更新——不是单个工具，而是底层能力。",
                size=11.5, bold=True, color=BLACK)
    add_footer(slide)


# ============= Slide 7: 六个探索项目 =============
def slide_7():
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_white_bg(slide)
    add_header(slide,
               "六个专业坐席场景：岗位 1+N 的可复制场景储备池",
               "不是凑数，而是后续复制场景与梯队", page_num=7)

    headers = ["项目", "负责人", "当前探索方向", "未来价值"]
    rows = [
        ["GVIP 坐席 1+N", "周梦莎",
         "高端客户服务场景标准化", "可沉淀高端服务 SOP"],
        ["对公坐席 1+N", "王秋梅",
         "对公客户服务与个人价值经营衔接", "可探索对公转零售路径"],
        ["信 SBO 坐席 1+N", "文京洛",
         "专业业务办理和客户解释能力沉淀", "提升复杂业务处理效率"],
        ["顶私坐席 1+N", "张旭宏、赵书英",
         "基于平安One系统支持顶私客户识别与经营", "提升顶私客户精细化经营"],
        ["结清挽留坐席 1+N", "蔡丽莉",
         "结清场景挽留话术、异议处理、转化策略", "提升挽留成功率"],
        ["私财坐席 1+N", "鲁晓晓",
         "私财客户服务与经营动作沉淀", "提升私财服务专业度"],
    ]
    add_table(slide, Inches(0.5), Inches(1.6), Inches(12.35), Inches(3.6),
              headers, rows, col_widths=[2.3, 1.8, 4.6, 3.65],
              header_size=12, body_size=11)

    # 平安One口径提示
    add_rect(slide, Inches(0.5), Inches(5.4), Inches(12.35), Inches(0.7),
             PA_ORANGE_LIGHT, line_color=PA_ORANGE, line_width=1)
    add_textbox(slide, Inches(0.75), Inches(5.45), Inches(11.8), Inches(0.3),
                "▎口径提示", size=11, bold=True, color=PA_ORANGE_DARK)
    add_textbox(slide, Inches(0.75), Inches(5.72), Inches(11.8), Inches(0.35),
                "不写「平安One 岗位 1+N」；正式表述为：顶私坐席岗位 1+N — 基于平安One系统能力，提升顶私客户识别、分析与服务经营能力。",
                size=11, bold=True, color=BLACK)

    # 总结框
    add_rect(slide, Inches(0.5), Inches(6.25), Inches(12.35), Inches(0.75),
             PA_ORANGE_BG, line_color=PA_ORANGE, line_width=1.5)
    add_textbox(slide, Inches(0.75), Inches(6.3), Inches(11.8), Inches(0.35),
                "■ 储备 ≠ 凑数 · 梯队 ≠ 平均", size=12, bold=True, color=PA_ORANGE_DARK)
    add_textbox(slide, Inches(0.75), Inches(6.62), Inches(11.8), Inches(0.4),
                "当前不平均投入；保留探索压力；一旦出现成熟场景与可复制成果，可从储备升级为重点。",
                size=11.5, bold=True, color=BLACK)
    add_footer(slide)


# ============= Slide 8: 成效衡量指标 =============
def slide_8():
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_white_bg(slide)
    add_header(slide,
               "成效衡量：以「效率、质量、经营、复制」四类指标验证岗位 1+N",
               "不用「做了工具」证明成绩，用指标证明", page_num=8)

    # 左：四维指标矩阵
    add_rect(slide, Inches(0.5), Inches(1.55), Inches(7.5), Inches(0.4), PA_ORANGE)
    add_textbox(slide, Inches(0.6), Inches(1.55), Inches(7.4), Inches(0.4),
                "▍ 四维指标矩阵", size=13, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    m_h = ["维度", "代表指标", "对应项目"]
    m_r = [
        ["效率提升", "拉数、筛人、整理、初判、知识拆解耗时下降",
         "服销现管 / 投诉 / 知识"],
        ["质量提升", "投诉化解成功率、知识准确率、新人差错率",
         "投诉 / 新人 / 知识 / GVIP"],
        ["经营提升", "尾部改善率、挽留成功率、私财/顶私触达率",
         "服销 / 挽留 / 顶私 / 私财"],
        ["组织复制", "案例库、话术库、训练场景、工具使用人数",
         "全部项目"],
        ["人才培养", "新人上岗周期、辅导有效率、演练通过率",
         "新人 / 中台教练"],
    ]
    add_table(slide, Inches(0.5), Inches(1.95), Inches(7.5), Inches(3.6),
              m_h, m_r, col_widths=[1.3, 3.5, 2.7], header_size=11, body_size=10)

    # 右：每个重点项目的硬指标
    add_rect(slide, Inches(8.15), Inches(1.55), Inches(4.7), Inches(0.4), PA_ORANGE_DARK)
    add_textbox(slide, Inches(8.25), Inches(1.55), Inches(4.6), Inches(0.4),
                "▍ 每个重点项目设一个硬指标", size=13, bold=True,
                color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    k_h = ["项目", "核心指标"]
    k_r = [
        ["服销现管", "尾部识别 + 辅导闭环效率"],
        ["投诉化解", "自助训练覆盖率 + 主管兜底下降"],
        ["新人育成", "新人独立上岗周期缩短"],
        ["中台/教练", "辅导后14/30天指标改善率"],
        ["安心秘书", "人均服务承载客户数"],
        ["知识拆解", "知识拆解 + 上线周期"],
    ]
    add_table(slide, Inches(8.15), Inches(1.95), Inches(4.7), Inches(3.6),
              k_h, k_r, col_widths=[1.5, 3.2],
              header_fill=PA_ORANGE_DARK, header_size=11, body_size=10)

    # 底部
    add_rect(slide, Inches(0.5), Inches(5.8), Inches(12.35), Inches(1.15),
             PA_ORANGE_BG, line_color=PA_ORANGE, line_width=1.5)
    add_textbox(slide, Inches(0.75), Inches(5.85), Inches(11.8), Inches(0.4),
                "■ 后续汇报口径", size=12, bold=True, color=PA_ORANGE_DARK)
    add_textbox(slide, Inches(0.75), Inches(6.2), Inches(11.8), Inches(0.7),
                "不只汇报「做了什么工具」，而是按效率、质量、经营、复制四类指标，持续跟踪每个岗位 1+N 是否真正产生价值；每个重点项目对应一项可量化的硬指标。",
                size=12, bold=True, color=BLACK)
    add_footer(slide)


# ============= Slide 9: 需要董事长支持 =============
def slide_9():
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_white_bg(slide)
    add_header(slide,
               "需要董事长支持：试点授权 · 协同机制 · 数据机制 · 技术能力 · 成果激励",
               "要资源，不要空支持", page_num=9)

    # 5 个资源卡片：横向 5 个
    cards = [
        ("1", "试点授权",
         "授权银卡作为客服中心岗位 1+N 试点单元，6 个重点岗位先跑样板，再向其他队伍复制。",
         "有「名义」才能向业管、银行、总部数字化协同。"),
        ("2", "协同机制",
         "管理层明确跨部门协同口径：业管 / 智能客服 / 数据 / 银行端 / 总部数字化。",
         "避免岗位 1+N 沦为单一团队内部自转。"),
        ("3", "数据机制",
         "建立顶私、私财、平安One、投诉、高客等敏感数据的脱敏可用机制。",
         "合规可用 — 让一线看到问题、训练能力。"),
        ("4", "技术能力",
         "AI 助手 / 数据看板 / 知识库 / 流程表单等轻量化能力支持。",
         "不上大系统，先用轻量工具跑通场景再沉淀。"),
        ("5", "成果激励",
         "对产出真实效率/质量/经营/复制成果的主管和骨干，年度评价、创新、数字化、绩效予以体现。",
         "回答「我做项目，到底算不算我的成绩？」"),
    ]
    card_w = Inches(2.42)
    card_h = Inches(4.0)
    gap = Inches(0.04)
    start_x = Inches(0.5)
    top = Inches(1.65)

    for i, (num, title, desc, why) in enumerate(cards):
        x = start_x + (card_w + gap) * i
        # 卡片底
        add_rect(slide, x, top, card_w, card_h, WHITE,
                 line_color=PA_ORANGE, line_width=1.5)
        # 顶部橙条 + 编号
        add_rect(slide, x, top, card_w, Inches(0.7), PA_ORANGE)
        add_textbox(slide, x, top + Inches(0.05), card_w, Inches(0.6),
                    f"资源 {num}", size=14, bold=True, color=WHITE,
                    align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        # 标题
        add_textbox(slide, x + Inches(0.1), top + Inches(0.8), card_w - Inches(0.2),
                    Inches(0.5), title, size=18, bold=True, color=PA_ORANGE_DARK,
                    align=PP_ALIGN.CENTER)
        # 分割线
        add_rect(slide, x + Inches(0.4), top + Inches(1.35),
                 card_w - Inches(0.8), Inches(0.03), PA_ORANGE_LIGHT)
        # 描述
        add_textbox(slide, x + Inches(0.15), top + Inches(1.45),
                    card_w - Inches(0.3), Inches(1.6),
                    desc, size=10.5, color=DARK_GRAY)
        # WHY 区块
        add_rect(slide, x + Inches(0.1), top + Inches(3.1),
                 card_w - Inches(0.2), Inches(0.85), PA_ORANGE_BG)
        add_textbox(slide, x + Inches(0.18), top + Inches(3.13),
                    card_w - Inches(0.36), Inches(0.3),
                    "WHY", size=9, bold=True, color=PA_ORANGE_DARK)
        add_textbox(slide, x + Inches(0.18), top + Inches(3.36),
                    card_w - Inches(0.36), Inches(0.6),
                    why, size=10, color=BLACK)

    # 底部主轴
    add_rect(slide, Inches(0.5), Inches(5.85), Inches(12.35), Inches(1.1),
             PA_ORANGE, line_color=PA_ORANGE_DARK, line_width=1.5)
    add_textbox(slide, Inches(0.75), Inches(5.9), Inches(11.85), Inches(0.4),
                "■ 全篇主轴", size=12, bold=True, color=WHITE)
    add_textbox(slide, Inches(0.75), Inches(6.2), Inches(11.85), Inches(0.75),
                "银卡岗位 1+N 不是做 12 个零散工具，而是以 6 个重点岗位为突破口，把客服中心最依赖个人经验、最消耗主管精力、最影响服务与经营结果的工作，改造成可复制、可训练、可追踪的数字化能力。",
                size=12, bold=True, color=WHITE)
    add_footer(slide)


# ===== 生成 =====
slide_1()
slide_2()
slide_3()
slide_4()
slide_5()
slide_6()
slide_7()
slide_8()
slide_9()

out_path = "/projects/sandbox/kiro2026/银卡岗位1+N数字化转型_董事长汇报.pptx"
prs.save(out_path)
print(f"PPT 已生成: {out_path}")
print(f"共 {len(prs.slides)} 页")
