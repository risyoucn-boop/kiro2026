"""
生成《AI 客服 ROI 测算模板》Excel 文件。
sheet:
  0. 使用说明
  1. 输入参数（核心假设，唯一需要改的页）
  2. 现状基线
  3. AI 改造后测算
  4. 分场景收益明细
  5. 三年现金流与 ROI
  6. 敏感性分析
  7. 汇报 Dashboard
"""
from openpyxl import Workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, NamedStyle
)
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule

wb = Workbook()

# ---------- 样式 ----------
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

TITLE_FONT = Font(name="微软雅黑", size=16, bold=True, color="FFFFFF")
TITLE_FILL = PatternFill("solid", fgColor="1F4E78")

H2_FONT = Font(name="微软雅黑", size=12, bold=True, color="FFFFFF")
H2_FILL = PatternFill("solid", fgColor="2E75B6")

INPUT_FILL = PatternFill("solid", fgColor="C6EFCE")      # 绿色 = 输入
CALC_FILL  = PatternFill("solid", fgColor="FFF2CC")      # 黄色 = 计算
NOTE_FILL  = PatternFill("solid", fgColor="F2F2F2")      # 灰色 = 备注
HIGH_FILL  = PatternFill("solid", fgColor="FCE4D6")      # 橙色 = 关键结果

CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT   = Alignment(horizontal="left",   vertical="center", wrap_text=True)
RIGHT  = Alignment(horizontal="right",  vertical="center", wrap_text=True)

BOLD   = Font(name="微软雅黑", size=11, bold=True)
NORMAL = Font(name="微软雅黑", size=11)
SMALL  = Font(name="微软雅黑", size=9, color="595959")

def set_col_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

def put_title(ws, text, span=6):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=span)
    c = ws.cell(row=1, column=1, value=text)
    c.font = TITLE_FONT
    c.fill = TITLE_FILL
    c.alignment = CENTER
    ws.row_dimensions[1].height = 32

def put_header(ws, row, headers, fill=H2_FILL, font=H2_FONT):
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=row, column=i, value=h)
        c.font = font
        c.fill = fill
        c.alignment = CENTER
        c.border = BORDER
    ws.row_dimensions[row].height = 26

def style_row(ws, row, n_cols, fill=None, font=NORMAL, align=None, number_format=None):
    for col in range(1, n_cols + 1):
        c = ws.cell(row=row, column=col)
        c.font = font
        if fill: c.fill = fill
        if align: c.alignment = align
        else: c.alignment = LEFT if col == 1 else RIGHT
        c.border = BORDER
        if number_format and col >= 2:
            c.number_format = number_format

# ================================================================
# Sheet 1: 使用说明
# ================================================================
ws = wb.active
ws.title = "0-使用说明"
set_col_widths(ws, [4, 40, 60])
put_title(ws, "AI 客服 ROI 测算模板 - 使用说明", span=3)

notes = [
    ("使用步骤", ""),
    ("Step 1", "打开 [1-输入参数] 页，填写绿色格子。这是唯一需要改的页。"),
    ("Step 2", "查看 [2-现状基线] 页，确认你当前的人工客服成本结构是否符合实际。"),
    ("Step 3", "查看 [3-AI改造后测算] 页，看到整体降本效果与新单位成本。"),
    ("Step 4", "查看 [4-分场景收益] 页，定位哪些场景贡献最大，决定立项优先级。"),
    ("Step 5", "查看 [5-三年现金流ROI] 页，向 CFO / 老板汇报用这张。"),
    ("Step 6", "查看 [6-敏感性分析] 页，回答'如果 AI 承接率只做到 50% 怎么办'这类问题。"),
    ("Step 7", "查看 [7-Dashboard] 页，一页纸汇报用。"),
    ("", ""),
    ("颜色图例", ""),
    ("绿色格子", "输入项，只改这些。"),
    ("黄色格子", "公式计算项，不要手改，会破坏联动。"),
    ("橙色格子", "关键结果，重点看。"),
    ("灰色格子", "备注和参考值。"),
    ("", ""),
    ("行业经验参考值", ""),
    ("单次人工会话成本", "电商 3~6 元 / 金融 6~15 元 / 运营商 4~8 元"),
    ("单次 AI 自助成本", "0.1~0.5 元（含 Token + 平台摊销）"),
    ("AI 承接率（1 年目标）", "首期 30%~50%，成熟期 60%~80%"),
    ("AHT 降幅（Copilot 场景）", "15%~30%"),
    ("质检覆盖率提升", "5% → 100%，质检人员可压缩 60%~80%"),
    ("FCR 提升", "3~8 个百分点"),
    ("", ""),
    ("注意事项", ""),
    ("注意 1", "人力成本按全口径（工资+社保+场地+管理+流失成本），一般为裸工资 × 1.5~1.8。"),
    ("注意 2", "AI 成本要含：大模型 API / GPU 摊销 / 平台软件 / AI 训练师人力 / 实施外包。"),
    ("注意 3", "不要只看第一年，大模型项目第 2-3 年规模化才是 ROI 主要来源。"),
    ("注意 4", "CSAT、NPS 的提升很难折现，本模板默认不算入财务收益，作为软性收益单独列示。"),
]

row = 3
ws.cell(row=row, column=1, value="").fill = PatternFill()
put_header(ws, row, ["#", "项目", "说明"])
row += 1
for k, v in notes:
    if v == "" and k != "":
        # 小标题
        ws.cell(row=row, column=1, value="")
        c = ws.cell(row=row, column=2, value=k)
        c.font = Font(name="微软雅黑", size=12, bold=True, color="1F4E78")
        c.fill = NOTE_FILL
        ws.cell(row=row, column=3, value="")
        ws.cell(row=row, column=2).alignment = LEFT
    elif k == "" and v == "":
        pass
    else:
        ws.cell(row=row, column=1, value="")
        ws.cell(row=row, column=2, value=k).alignment = LEFT
        ws.cell(row=row, column=3, value=v).alignment = LEFT
    for col in range(1, 4):
        ws.cell(row=row, column=col).border = BORDER
        if ws.cell(row=row, column=col).font is None or ws.cell(row=row, column=col).font.name != "微软雅黑":
            ws.cell(row=row, column=col).font = NORMAL
    ws.row_dimensions[row].height = 22
    row += 1

# ================================================================
# Sheet 2: 输入参数
# ================================================================
ws = wb.create_sheet("1-输入参数")
set_col_widths(ws, [6, 36, 16, 16, 50])
put_title(ws, "1. 输入参数（绿色格子 = 需要你填）", span=5)

put_header(ws, 3, ["#", "参数名称", "数值", "单位", "说明 / 参考"])

# (参数名, 默认值, 单位, 说明)
# 用 named cells, 后面公式引用
params = [
    # --- A. 业务规模 ---
    ("A. 业务规模基线", None, None, None),
    ("月均会话量",              1_000_000, "次/月", "含在线+电话+工单，全渠道合计"),
    ("人工坐席数",                   1500, "人",    "一线坐席，不含质检/主管"),
    ("质检人员数",                     80, "人",    "原有质检团队规模"),
    ("坐席月均工时",                  176, "小时/人/月", "按每月22天 × 8小时"),

    # --- B. 人工成本 ---
    ("B. 人工成本（全口径）", None, None, None),
    ("坐席月均全成本",              8000, "元/人/月", "裸工资 × 1.5~1.8（含社保、场地、管理摊销）"),
    ("质检员月均全成本",           10000, "元/人/月", "一般高于坐席 20%"),
    ("主管/运营人员数",              100, "人",    "不直接参与对话但与规模挂钩"),
    ("主管/运营月均全成本",        15000, "元/人/月", ""),

    # --- C. 现状 KPI ---
    ("C. 现状 KPI", None, None, None),
    ("现有机器人承接率",            0.15, "%", "老一代规则机器人的自助率"),
    ("平均会话时长 AHT",              8, "分钟/次", "人工会话平均处理时长"),
    ("事后处理时长 ACW",              3, "分钟/次", "会话结束后填单/记录的时长"),
    ("一解率 FCR",                  0.65, "%", "一次咨询解决率"),
    ("质检覆盖率",                  0.05, "%", "抽检比例"),
    ("CSAT 满意度",                 0.82, "%", "当前客户满意度"),

    # --- D. AI 方案目标 ---
    ("D. AI 方案目标（Y1/Y2/Y3）", None, None, None),
    ("AI 承接率 Y1",                0.35, "%", "第 1 年目标，典型 30%~50%"),
    ("AI 承接率 Y2",                0.55, "%", "第 2 年"),
    ("AI 承接率 Y3",                0.70, "%", "第 3 年，成熟期"),
    ("Copilot 覆盖坐席比例 Y1",     0.60, "%", "多少比例的坐席使用 Copilot"),
    ("Copilot 覆盖坐席比例 Y2",     0.90, "%", ""),
    ("Copilot 覆盖坐席比例 Y3",     1.00, "%", ""),
    ("Copilot 带来 AHT 降幅",       0.20, "%", "15%~30%"),
    ("Copilot 带来 ACW 降幅",       0.50, "%", "工单自动生成后降幅 40%~60%"),
    ("AI 质检覆盖率",               1.00, "%", "AI 质检一般做到 100%"),
    ("AI 质检员压缩比例",           0.70, "%", "60%~80%"),
    ("FCR 提升（百分点）",          0.05, "%", "3~8 个百分点"),

    # --- E. AI 成本 ---
    ("E. AI 成本", None, None, None),
    ("单次 AI 会话成本",            0.30, "元/次", "含 Token + 平台摊销，0.1~0.5"),
    ("AI 平台年订阅/摊销",      1_500_000, "元/年", "大模型私有化 / SaaS 订阅 / GPU 摊销"),
    ("一次性建设投入",          3_000_000, "元",    "项目实施+定制开发+数据治理，第 0 年投入"),
    ("AI 训练师/运营人数",             8, "人",    "新增岗位"),
    ("AI 训练师月均全成本",        18000, "元/人/月", ""),
    ("年度模型维护/迭代费",      800_000, "元/年", "持续调优、知识运营"),

    # --- F. 软性收益参数 ---
    ("F. 软性收益（可选）", None, None, None),
    ("CSAT 每提升 1pp 带来留存收入增量", 500_000, "元/年", "仅做估算，不计入主 ROI"),
    ("预期 CSAT 提升",              0.04, "%", "4 个百分点"),

    # --- G. 财务参数 ---
    ("G. 财务参数", None, None, None),
    ("折现率 WACC",                 0.08, "%", "用于 NPV"),
    ("测算周期",                       3, "年", "默认 3 年"),
]

row = 4
section_rows = {}
param_rows = {}
for name, val, unit, note in params:
    if val is None:  # 小标题
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=5)
        c = ws.cell(row=row, column=1, value=name)
        c.font = BOLD
        c.fill = PatternFill("solid", fgColor="DDEBF7")
        c.alignment = LEFT
        c.border = BORDER
        section_rows[name] = row
    else:
        ws.cell(row=row, column=1, value="").border = BORDER
        ws.cell(row=row, column=2, value=name).border = BORDER
        ws.cell(row=row, column=2).alignment = LEFT
        ws.cell(row=row, column=2).font = NORMAL

        c = ws.cell(row=row, column=3, value=val)
        c.fill = INPUT_FILL
        c.font = BOLD
        c.alignment = CENTER
        c.border = BORDER
        if "%" in (unit or ""):
            c.number_format = "0.00%"
        elif "元" in (unit or "") and val >= 1000:
            c.number_format = "#,##0"
        elif "元" in (unit or ""):
            c.number_format = "0.00"
        else:
            c.number_format = "#,##0"

        ws.cell(row=row, column=4, value=unit).border = BORDER
        ws.cell(row=row, column=4).alignment = CENTER
        ws.cell(row=row, column=4).font = SMALL

        ws.cell(row=row, column=5, value=note).border = BORDER
        ws.cell(row=row, column=5).alignment = LEFT
        ws.cell(row=row, column=5).font = SMALL
        ws.cell(row=row, column=5).fill = NOTE_FILL

        param_rows[name] = row
    ws.row_dimensions[row].height = 22
    row += 1

# 辅助函数: 拿到 '1-输入参数' 某参数的单元格引用
P_SHEET = "'1-输入参数'"
def P(name):
    r = param_rows[name]
    return f"{P_SHEET}!$C${r}"

# ================================================================
# Sheet 3: 现状基线
# ================================================================
ws = wb.create_sheet("2-现状基线")
set_col_widths(ws, [6, 30, 18, 16, 40])
put_title(ws, "2. 现状基线（改造前）", span=5)
put_header(ws, 3, ["#", "指标", "数值", "单位", "口径说明"])

baseline = [
    ("年会话量",          f"={P('月均会话量')}*12",        "次/年",  "月均×12"),
    ("人工承接量（年）", f"={P('月均会话量')}*12*(1-{P('现有机器人承接率')})", "次/年", "扣除旧机器人自助"),
    ("坐席年人力成本",   f"={P('人工坐席数')}*{P('坐席月均全成本')}*12",  "元/年",  "坐席×月成本×12"),
    ("质检年人力成本",   f"={P('质检人员数')}*{P('质检员月均全成本')}*12","元/年",  "质检×月成本×12"),
    ("主管年人力成本",   f"={P('主管/运营人员数')}*{P('主管/运营月均全成本')}*12","元/年", "主管×月成本×12"),
    ("年人工总成本",     "=C6+C7+C8",                     "元/年",  "坐席+质检+主管"),
    ("单次人工会话成本", "=C9/C4",                         "元/次",  "年人工成本 ÷ 年会话量（全口径）"),
    ("单次人工会话成本(仅坐席)","=C6/C4",                  "元/次",  "仅坐席摊销口径"),
    ("平均处理时长(AHT+ACW)", f"={P('平均会话时长 AHT')}+{P('事后处理时长 ACW')}","分钟/次","处理+事后"),
    ("年坐席总工时",     f"={P('人工坐席数')}*{P('坐席月均工时')}*12", "人时/年", ""),
    ("人均日均会话量",   f"=C4/{P('人工坐席数')}/250",    "次/人/日",  "按年 250 个工作日"),
    ("FCR",              f"={P('一解率 FCR')}",            "%",      "一解率"),
    ("质检覆盖率",       f"={P('质检覆盖率')}",            "%",      "抽检比例"),
    ("CSAT",             f"={P('CSAT 满意度')}",           "%",      ""),
]

row = 4
for i, (name, formula, unit, note) in enumerate(baseline, 1):
    ws.cell(row=row, column=1, value=i).border = BORDER
    ws.cell(row=row, column=1).alignment = CENTER
    ws.cell(row=row, column=2, value=name).border = BORDER
    ws.cell(row=row, column=2).alignment = LEFT
    c = ws.cell(row=row, column=3, value=formula)
    c.fill = CALC_FILL
    c.border = BORDER
    c.alignment = RIGHT
    c.font = BOLD
    if "%" in unit:
        c.number_format = "0.00%"
    elif "元" in unit:
        c.number_format = '"¥"#,##0.00'
    elif "次" in unit or "人时" in unit:
        c.number_format = "#,##0.00"
    else:
        c.number_format = "#,##0.00"
    ws.cell(row=row, column=4, value=unit).border = BORDER
    ws.cell(row=row, column=4).alignment = CENTER
    ws.cell(row=row, column=4).font = SMALL
    ws.cell(row=row, column=5, value=note).border = BORDER
    ws.cell(row=row, column=5).alignment = LEFT
    ws.cell(row=row, column=5).font = SMALL
    ws.cell(row=row, column=5).fill = NOTE_FILL
    ws.row_dimensions[row].height = 22
    row += 1

BASELINE_SHEET = "'2-现状基线'"
# baseline 关键单元格引用（数据从 row=4 起，baseline 列表 14 项）
BL_YEAR_VOL      = f"{BASELINE_SHEET}!$C$4"   # 年会话量
BL_HUMAN_VOL     = f"{BASELINE_SHEET}!$C$5"   # 人工承接量
BL_AGENT_COST    = f"{BASELINE_SHEET}!$C$6"   # 坐席年成本
BL_QA_COST       = f"{BASELINE_SHEET}!$C$7"   # 质检年成本
BL_MGR_COST      = f"{BASELINE_SHEET}!$C$8"   # 主管年成本
BL_TOTAL_HUMAN   = f"{BASELINE_SHEET}!$C$9"   # 年人工总成本
BL_UNIT_COST     = f"{BASELINE_SHEET}!$C$10"  # 单次人工成本（全口径）
BL_UNIT_AGENT    = f"{BASELINE_SHEET}!$C$11"  # 单次（仅坐席）
BL_HANDLE_TIME   = f"{BASELINE_SHEET}!$C$12"  # AHT+ACW

# ================================================================
# Sheet 4: AI 改造后测算（三年）
# ================================================================
ws = wb.create_sheet("3-AI改造后测算")
set_col_widths(ws, [34, 18, 18, 18, 36])
put_title(ws, "3. AI 改造后测算（Y1 / Y2 / Y3）", span=5)
put_header(ws, 3, ["指标", "Y1", "Y2", "Y3", "备注"])

def num_fmt(unit):
    if "%" in unit:
        return "0.00%"
    if "元" in unit:
        return '"¥"#,##0'
    return "#,##0"

# 定义 AI 承接率 & Copilot 覆盖（分三年）
# 辅助引用
AI_RATE = {
    "Y1": P("AI 承接率 Y1"),
    "Y2": P("AI 承接率 Y2"),
    "Y3": P("AI 承接率 Y3"),
}
CP_RATE = {
    "Y1": P("Copilot 覆盖坐席比例 Y1"),
    "Y2": P("Copilot 覆盖坐席比例 Y2"),
    "Y3": P("Copilot 覆盖坐席比例 Y3"),
}

# 行定义: (名称, 单位, [Y1公式, Y2公式, Y3公式], 备注)
rows_def = [
    ("年会话量",                      "次/年",
        [f"={BL_YEAR_VOL}"]*3,
        "与基线相同"),
    ("AI 承接率",                     "%",
        [f"={AI_RATE['Y1']}", f"={AI_RATE['Y2']}", f"={AI_RATE['Y3']}"],
        "目标值"),
    ("AI 自助会话量",                  "次/年",
        [f"={BL_YEAR_VOL}*{AI_RATE['Y1']}",
         f"={BL_YEAR_VOL}*{AI_RATE['Y2']}",
         f"={BL_YEAR_VOL}*{AI_RATE['Y3']}"],
        "年会话×AI承接率"),
    ("人工承接会话量",                 "次/年",
        [f"={BL_YEAR_VOL}*(1-{AI_RATE['Y1']})",
         f"={BL_YEAR_VOL}*(1-{AI_RATE['Y2']})",
         f"={BL_YEAR_VOL}*(1-{AI_RATE['Y3']})"],
        "剩余由人工处理"),

    # ----- 坐席工时压缩 -----
    ("人工承接需坐席数（基准AHT）",    "人",
        [f"=B6*({P('平均会话时长 AHT')}+{P('事后处理时长 ACW')})/60/({P('坐席月均工时')}*12)"]*3,
        "(会话量×处理时长/60) ÷ 人均年工时，基准口径"),
    ("Copilot 加权 AHT+ACW",           "分钟",
        [f"={P('平均会话时长 AHT')}*(1-{CP_RATE[y]}*{P('Copilot 带来 AHT 降幅')})+{P('事后处理时长 ACW')}*(1-{CP_RATE[y]}*{P('Copilot 带来 ACW 降幅')})"
         for y in ["Y1","Y2","Y3"]],
        "Copilot 覆盖率×降幅"),
    ("实际需坐席数",                   "人",
        [f"=B6*B8/60/({P('坐席月均工时')}*12)"]*3,
        "结合 Copilot 后的真实需求"),
    # 这里 B6/B8 会被手动调整为真实引用（后面补）
    ("可压缩坐席数",                   "人",
        [f"={P('人工坐席数')}-B9"]*3,
        "基准坐席 - 实际需坐席"),
    ("坐席年成本（改造后）",           "元/年",
        [f"=B9*{P('坐席月均全成本')}*12"]*3,
        ""),
    ("质检人员（改造后）",             "人",
        [f"={P('质检人员数')}*(1-{P('AI 质检员压缩比例')})"]*3,
        ""),
    ("质检年成本（改造后）",           "元/年",
        [f"=B12*{P('质检员月均全成本')}*12"]*3,
        ""),
    ("主管年成本（按坐席比例缩放）",    "元/年",
        [f"={BL_MGR_COST}*B9/{P('人工坐席数')}"]*3,
        "主管规模随坐席等比例缩减"),

    # ----- AI 成本 -----
    ("AI 自助会话成本",                "元/年",
        [f"=B5*{P('单次 AI 会话成本')}"]*3,
        "AI 会话量 × 单次 AI 成本"),
    ("AI 平台订阅/摊销",               "元/年",
        [f"={P('AI 平台年订阅/摊销')}"]*3, ""),
    ("AI 训练师人力成本",              "元/年",
        [f"={P('AI 训练师/运营人数')}*{P('AI 训练师月均全成本')}*12"]*3, ""),
    ("年度模型维护/迭代",              "元/年",
        [f"={P('年度模型维护/迭代费')}"]*3, ""),
    ("AI 总成本",                      "元/年",
        [f"=B15+B16+B17+B18"]*3,
        "AI 相关全部开销"),

    # ----- 合计与对比 -----
    ("改造后总成本",                   "元/年",
        [f"=B11+B13+B14+B19"]*3,
        "人工 + AI"),
    ("现状总成本（基线）",             "元/年",
        [f"={BL_TOTAL_HUMAN}"]*3, "对照"),
    ("年度节省",                       "元/年",
        [f"=B22-B21"]*3,
        "正数 = 降本，负数 = 增本"),
    ("降本率",                         "%",
        [f"=B23/B22"]*3, ""),
    ("新单次会话成本",                 "元/次",
        [f"=B21/{BL_YEAR_VOL}"]*3, ""),
    ("原单次会话成本",                 "元/次",
        [f"={BL_UNIT_COST}"]*3, ""),
    ("单次会话成本降幅",               "%",
        [f"=(B27-B26)/B27"]*3, "越大越好"),

    # ----- KPI -----
    ("预计 FCR（改造后）",             "%",
        [f"={P('一解率 FCR')}+{P('FCR 提升（百分点）')}"]*3, ""),
    ("质检覆盖率",                     "%",
        [f"={P('AI 质检覆盖率')}"]*3, ""),
    ("CSAT（估算）",                   "%",
        [f"={P('CSAT 满意度')}+{P('预期 CSAT 提升')}*({y_idx}/3)" for y_idx in [1,2,3]],
        "线性爬升"),
]

# 注意: rows_def 中有些公式写了 "B6", "B8", "B9" 这种相对引用，它们在本 sheet 的实际行位置
# 需要根据写入顺序动态修正。为避免错误，改为直接用行号映射。
# 重新严谨地写入：
rows_with_row = []
start_row = 4
for idx, (name, unit, formulas, note) in enumerate(rows_def):
    rows_with_row.append(start_row + idx)

# 我们需要的行号：
R_YEAR_VOL      = rows_with_row[0]   # 年会话量
R_AI_RATE       = rows_with_row[1]
R_AI_VOL        = rows_with_row[2]
R_HUMAN_VOL     = rows_with_row[3]
R_AGENTS_BASE   = rows_with_row[4]   # 基准需坐席
R_HANDLE_CP     = rows_with_row[5]   # Copilot 后加权 AHT+ACW
R_AGENTS_REAL   = rows_with_row[6]   # 实际需坐席
R_AGENT_CUT     = rows_with_row[7]
R_AGENT_COST    = rows_with_row[8]
R_QA_HEAD       = rows_with_row[9]
R_QA_COST       = rows_with_row[10]
R_MGR_COST      = rows_with_row[11]
R_AI_USAGE      = rows_with_row[12]
R_AI_PLATFORM   = rows_with_row[13]
R_AI_TRAINER    = rows_with_row[14]
R_AI_MAINT      = rows_with_row[15]
R_AI_TOTAL      = rows_with_row[16]
R_NEW_TOTAL     = rows_with_row[17]
R_BASE_TOTAL    = rows_with_row[18]
R_SAVING        = rows_with_row[19]
R_SAVE_PCT      = rows_with_row[20]
R_NEW_UNIT      = rows_with_row[21]
R_OLD_UNIT      = rows_with_row[22]
R_UNIT_DROP     = rows_with_row[23]
R_FCR           = rows_with_row[24]
R_QA_COV        = rows_with_row[25]
R_CSAT          = rows_with_row[26]

# 现在用正确的行号重建公式
def col(year_idx):  # Y1->B, Y2->C, Y3->D
    return ["B", "C", "D"][year_idx]

correct_formulas = []
for idx, (name, unit, _formulas, note) in enumerate(rows_def):
    rn = rows_with_row[idx]
    f_list = []
    for y_idx, y in enumerate(["Y1","Y2","Y3"]):
        cL = col(y_idx)
        if idx == 0:  # 年会话量
            f = f"={BL_YEAR_VOL}"
        elif idx == 1:  # AI 承接率
            f = f"={AI_RATE[y]}"
        elif idx == 2:  # AI 自助会话量
            f = f"={cL}{R_YEAR_VOL}*{cL}{R_AI_RATE}"
        elif idx == 3:  # 人工承接会话量
            f = f"={cL}{R_YEAR_VOL}*(1-{cL}{R_AI_RATE})"
        elif idx == 4:  # 基准需坐席 = 人工承接×(AHT+ACW)/60 / 年工时
            f = (f"={cL}{R_HUMAN_VOL}*({P('平均会话时长 AHT')}+{P('事后处理时长 ACW')})/60"
                 f"/({P('坐席月均工时')}*12)")
        elif idx == 5:  # Copilot 后 AHT+ACW
            f = (f"={P('平均会话时长 AHT')}*(1-{CP_RATE[y]}*{P('Copilot 带来 AHT 降幅')})"
                 f"+{P('事后处理时长 ACW')}*(1-{CP_RATE[y]}*{P('Copilot 带来 ACW 降幅')})")
        elif idx == 6:  # 实际需坐席
            f = (f"={cL}{R_HUMAN_VOL}*{cL}{R_HANDLE_CP}/60"
                 f"/({P('坐席月均工时')}*12)")
        elif idx == 7:  # 可压缩坐席
            f = f"={P('人工坐席数')}-{cL}{R_AGENTS_REAL}"
        elif idx == 8:  # 坐席成本（改造后）
            f = f"={cL}{R_AGENTS_REAL}*{P('坐席月均全成本')}*12"
        elif idx == 9:  # 质检人数
            f = f"={P('质检人员数')}*(1-{P('AI 质检员压缩比例')})"
        elif idx == 10:  # 质检成本
            f = f"={cL}{R_QA_HEAD}*{P('质检员月均全成本')}*12"
        elif idx == 11:  # 主管成本（按坐席比例）
            f = f"={BL_MGR_COST}*{cL}{R_AGENTS_REAL}/{P('人工坐席数')}"
        elif idx == 12:  # AI 会话成本
            f = f"={cL}{R_AI_VOL}*{P('单次 AI 会话成本')}"
        elif idx == 13:
            f = f"={P('AI 平台年订阅/摊销')}"
        elif idx == 14:
            f = f"={P('AI 训练师/运营人数')}*{P('AI 训练师月均全成本')}*12"
        elif idx == 15:
            f = f"={P('年度模型维护/迭代费')}"
        elif idx == 16:  # AI 总成本
            f = f"={cL}{R_AI_USAGE}+{cL}{R_AI_PLATFORM}+{cL}{R_AI_TRAINER}+{cL}{R_AI_MAINT}"
        elif idx == 17:  # 改造后总成本
            f = f"={cL}{R_AGENT_COST}+{cL}{R_QA_COST}+{cL}{R_MGR_COST}+{cL}{R_AI_TOTAL}"
        elif idx == 18:  # 基线总成本
            f = f"={BL_TOTAL_HUMAN}"
        elif idx == 19:  # 节省
            f = f"={cL}{R_BASE_TOTAL}-{cL}{R_NEW_TOTAL}"
        elif idx == 20:  # 降本率
            f = f"={cL}{R_SAVING}/{cL}{R_BASE_TOTAL}"
        elif idx == 21:  # 新单次
            f = f"={cL}{R_NEW_TOTAL}/{cL}{R_YEAR_VOL}"
        elif idx == 22:  # 原单次
            f = f"={BL_UNIT_COST}"
        elif idx == 23:  # 降幅
            f = f"=({cL}{R_OLD_UNIT}-{cL}{R_NEW_UNIT})/{cL}{R_OLD_UNIT}"
        elif idx == 24:
            f = f"={P('一解率 FCR')}+{P('FCR 提升（百分点）')}"
        elif idx == 25:
            f = f"={P('AI 质检覆盖率')}"
        elif idx == 26:
            f = f"={P('CSAT 满意度')}+{P('预期 CSAT 提升')}*({y_idx+1}/3)"
        else:
            f = ""
        f_list.append(f)
    correct_formulas.append(f_list)

# 把数据写进去
for idx, (name, unit, _formulas, note) in enumerate(rows_def):
    rn = rows_with_row[idx]
    ws.cell(row=rn, column=1, value=name).border = BORDER
    ws.cell(row=rn, column=1).alignment = LEFT
    ws.cell(row=rn, column=1).font = NORMAL

    for y_idx in range(3):
        c = ws.cell(row=rn, column=2+y_idx, value=correct_formulas[idx][y_idx])
        c.fill = CALC_FILL
        c.border = BORDER
        c.font = BOLD
        c.alignment = RIGHT
        c.number_format = num_fmt(unit)

    ws.cell(row=rn, column=5, value=note).border = BORDER
    ws.cell(row=rn, column=5).alignment = LEFT
    ws.cell(row=rn, column=5).font = SMALL
    ws.cell(row=rn, column=5).fill = NOTE_FILL
    ws.row_dimensions[rn].height = 22

# 高亮关键结果
for rn in [R_SAVING, R_SAVE_PCT, R_NEW_UNIT, R_UNIT_DROP]:
    for col_i in range(2, 5):
        ws.cell(row=rn, column=col_i).fill = HIGH_FILL
    ws.cell(row=rn, column=1).font = BOLD

SAVE_Y = {"Y1": f"'3-AI改造后测算'!B{R_SAVING}",
          "Y2": f"'3-AI改造后测算'!C{R_SAVING}",
          "Y3": f"'3-AI改造后测算'!D{R_SAVING}"}
NEW_TOTAL_Y = {"Y1": f"'3-AI改造后测算'!B{R_NEW_TOTAL}",
               "Y2": f"'3-AI改造后测算'!C{R_NEW_TOTAL}",
               "Y3": f"'3-AI改造后测算'!D{R_NEW_TOTAL}"}
BASE_TOTAL_Y = {"Y1": f"'3-AI改造后测算'!B{R_BASE_TOTAL}",
                "Y2": f"'3-AI改造后测算'!C{R_BASE_TOTAL}",
                "Y3": f"'3-AI改造后测算'!D{R_BASE_TOTAL}"}
NEW_UNIT_Y = {"Y1": f"'3-AI改造后测算'!B{R_NEW_UNIT}",
              "Y2": f"'3-AI改造后测算'!C{R_NEW_UNIT}",
              "Y3": f"'3-AI改造后测算'!D{R_NEW_UNIT}"}
SAVE_PCT_Y = {"Y1": f"'3-AI改造后测算'!B{R_SAVE_PCT}",
              "Y2": f"'3-AI改造后测算'!C{R_SAVE_PCT}",
              "Y3": f"'3-AI改造后测算'!D{R_SAVE_PCT}"}

# ================================================================
# Sheet 5: 分场景收益明细
# ================================================================
ws = wb.create_sheet("4-分场景收益")
set_col_widths(ws, [28, 14, 14, 14, 14, 14, 40])
put_title(ws, "4. 分场景收益明细（Y3 成熟期口径）", span=7)
put_header(ws, 3, ["场景", "覆盖比例", "单位成本降幅", "年节省(元)", "上线周期(月)", "实施难度", "说明"])

# 简化模型：各场景独立贡献的 Y3 净节省 = 相关基线成本 × 覆盖 × 降幅
# 注：这里是"分项贡献估算"，与 sheet3 的整体口径可能有小差异，用于立项优先级排序
scenarios = [
    ("智能质检全检",
     f"={P('AI 质检覆盖率')}",
     f"={P('AI 质检员压缩比例')}",
     f"={BL_QA_COST}*{P('AI 质检员压缩比例')}",
     1, "低", "最快见效，建议首选"),

    ("坐席 Copilot（话术+检索+填单）",
     f"={P('Copilot 覆盖坐席比例 Y3')}",
     f"=({P('平均会话时长 AHT')}*{P('Copilot 带来 AHT 降幅')}+{P('事后处理时长 ACW')}*{P('Copilot 带来 ACW 降幅')})/({P('平均会话时长 AHT')}+{P('事后处理时长 ACW')})",
     f"={BL_AGENT_COST}*{P('Copilot 覆盖坐席比例 Y3')}*(({P('平均会话时长 AHT')}*{P('Copilot 带来 AHT 降幅')}+{P('事后处理时长 ACW')}*{P('Copilot 带来 ACW 降幅')})/({P('平均会话时长 AHT')}+{P('事后处理时长 ACW')}))",
     3, "中", "AHT/ACW 压缩，坐席减员或承接更多量"),

    ("RAG 智能自助（高频FAQ/查单/政策）",
     f"={P('AI 承接率 Y3')}-{P('现有机器人承接率')}",
     "=1-" + P('单次 AI 会话成本') + "/" + BL_UNIT_COST,
     f"={BL_YEAR_VOL}*({P('AI 承接率 Y3')}-{P('现有机器人承接率')})*({BL_UNIT_COST}-{P('单次 AI 会话成本')})",
     3, "中", "把简单咨询从人工转到 AI"),

    ("会话摘要 + 工单自动生成",
     f"={P('Copilot 覆盖坐席比例 Y3')}",
     f"={P('事后处理时长 ACW')}*{P('Copilot 带来 ACW 降幅')}/({P('平均会话时长 AHT')}+{P('事后处理时长 ACW')})",
     f"={BL_AGENT_COST}*{P('Copilot 覆盖坐席比例 Y3')}*({P('事后处理时长 ACW')}*{P('Copilot 带来 ACW 降幅')}/({P('平均会话时长 AHT')}+{P('事后处理时长 ACW')}))",
     2, "低", "Copilot 的子项，已含在 Copilot 内，此处仅单独拆解参考"),

    ("智能外呼/满意度回访",
     0.80, 0.70,
     f"={BL_AGENT_COST}*0.05*0.80*0.70",
     2, "低", "按坐席 5% 从事外呼估算"),

    ("全自动 Agent 售后（调 API 闭环）",
     0.30, 0.60,
     f"={BL_YEAR_VOL}*0.30*({BL_UNIT_COST}-{P('单次 AI 会话成本')})*0.6",
     6, "高", "需打通订单/支付/库存 API，第二期做"),

    ("培训/陪练/知识沉淀（内部降本）",
     1.0, 0.30,
     f"=({BL_MGR_COST}*0.2)*0.30",
     3, "低", "缩短新人爬坡+节省培训人力"),
]

row = 4
scen_rows = []
for sc in scenarios:
    name, cov, drop, saving, months, diff, note = sc
    scen_rows.append(row)
    ws.cell(row=row, column=1, value=name).border = BORDER
    ws.cell(row=row, column=1).alignment = LEFT
    ws.cell(row=row, column=1).font = NORMAL

    for col_i, val, fmt in [
        (2, cov, "0.00%"),
        (3, drop, "0.00%"),
        (4, saving, '"¥"#,##0'),
        (5, months, "0"),
    ]:
        c = ws.cell(row=row, column=col_i, value=val)
        c.fill = CALC_FILL
        c.border = BORDER
        c.alignment = RIGHT
        c.font = BOLD
        c.number_format = fmt

    ws.cell(row=row, column=6, value=diff).border = BORDER
    ws.cell(row=row, column=6).alignment = CENTER
    ws.cell(row=row, column=7, value=note).border = BORDER
    ws.cell(row=row, column=7).alignment = LEFT
    ws.cell(row=row, column=7).font = SMALL
    ws.cell(row=row, column=7).fill = NOTE_FILL
    ws.row_dimensions[row].height = 24
    row += 1

# 合计行（注：Copilot 已含摘要，说明中提示）
total_row = row
ws.cell(row=total_row, column=1, value="合计（估算，含重叠，见说明）").font = BOLD
ws.cell(row=total_row, column=1).border = BORDER
ws.cell(row=total_row, column=1).fill = HIGH_FILL
for col_i in [2,3,5,6]:
    ws.cell(row=total_row, column=col_i, value="").border = BORDER
    ws.cell(row=total_row, column=col_i).fill = HIGH_FILL
c = ws.cell(row=total_row, column=4, value=f"=SUM(D{scen_rows[0]}:D{scen_rows[-1]})")
c.fill = HIGH_FILL; c.border = BORDER; c.font = BOLD; c.alignment = RIGHT
c.number_format = '"¥"#,##0'
ws.cell(row=total_row, column=7, value="此处为简单求和，Copilot 与'摘要'存在口径重叠，真实整合后应以 Sheet3 为准。").border = BORDER
ws.cell(row=total_row, column=7).fill = NOTE_FILL
ws.cell(row=total_row, column=7).font = SMALL
ws.cell(row=total_row, column=7).alignment = LEFT
ws.row_dimensions[total_row].height = 28

# ================================================================
# Sheet 6: 三年现金流 & NPV/IRR/回收期
# ================================================================
ws = wb.create_sheet("5-三年现金流ROI")
set_col_widths(ws, [30, 18, 18, 18, 18, 40])
put_title(ws, "5. 三年现金流 / NPV / IRR / 回收期", span=6)
put_header(ws, 3, ["项目", "Y0", "Y1", "Y2", "Y3", "说明"])

cf_rows = [
    ("一次性投入（CapEx）",
     [f"=-{P('一次性建设投入')}", 0, 0, 0],
     "第 0 年项目投入"),
    ("年度节省（OpEx 减少）",
     [0, f"={SAVE_Y['Y1']}", f"={SAVE_Y['Y2']}", f"={SAVE_Y['Y3']}"],
     "取自 Sheet3"),
    ("软性收益估算（CSAT）",
     [0,
      f"={P('CSAT 每提升 1pp 带来留存收入增量')}*{P('预期 CSAT 提升')}*100*(1/3)",
      f"={P('CSAT 每提升 1pp 带来留存收入增量')}*{P('预期 CSAT 提升')}*100*(2/3)",
      f"={P('CSAT 每提升 1pp 带来留存收入增量')}*{P('预期 CSAT 提升')}*100*(3/3)"],
     "可选，含义大CSAT不折现时置零"),
    ("净现金流",
     None,  # 用公式
     "一次性+节省+软性"),
    ("累计净现金流",
     None,
     "累计"),
    ("折现净现金流",
     None,
     "按 WACC 折现"),
    ("累计折现净现金流",
     None,
     ""),
]

r0 = 4
# 写入前 3 行（有明确公式）
for i in range(3):
    name, vals, note = cf_rows[i]
    rn = r0 + i
    ws.cell(row=rn, column=1, value=name).border = BORDER
    ws.cell(row=rn, column=1).alignment = LEFT
    ws.cell(row=rn, column=1).font = NORMAL
    for j, v in enumerate(vals):
        c = ws.cell(row=rn, column=2+j, value=v)
        c.fill = CALC_FILL
        c.border = BORDER
        c.font = BOLD
        c.alignment = RIGHT
        c.number_format = '"¥"#,##0'
    ws.cell(row=rn, column=6, value=note).border = BORDER
    ws.cell(row=rn, column=6).alignment = LEFT
    ws.cell(row=rn, column=6).font = SMALL
    ws.cell(row=rn, column=6).fill = NOTE_FILL
    ws.row_dimensions[rn].height = 22

# 净现金流 = 一次性 + 节省 + 软性
R_CAPEX = r0
R_SAVE  = r0 + 1
R_SOFT  = r0 + 2
R_NET   = r0 + 3
R_CUM   = r0 + 4
R_DISC  = r0 + 5
R_CUMD  = r0 + 6

# 4. 净现金流
ws.cell(row=R_NET, column=1, value="净现金流").border = BORDER
ws.cell(row=R_NET, column=1).alignment = LEFT
ws.cell(row=R_NET, column=1).font = BOLD
for j, cL in enumerate(["B","C","D","E"]):
    c = ws.cell(row=R_NET, column=2+j, value=f"={cL}{R_CAPEX}+{cL}{R_SAVE}+{cL}{R_SOFT}")
    c.fill = HIGH_FILL; c.border = BORDER; c.font = BOLD; c.alignment = RIGHT
    c.number_format = '"¥"#,##0'
ws.cell(row=R_NET, column=6, value="一次性+节省+软性").border = BORDER
ws.cell(row=R_NET, column=6).alignment = LEFT
ws.cell(row=R_NET, column=6).font = SMALL
ws.cell(row=R_NET, column=6).fill = NOTE_FILL

# 5. 累计净现金流
ws.cell(row=R_CUM, column=1, value="累计净现金流").border = BORDER
ws.cell(row=R_CUM, column=1).alignment = LEFT
ws.cell(row=R_CUM, column=1).font = BOLD
formulas_cum = [f"=B{R_NET}", f"=B{R_CUM}+C{R_NET}", f"=C{R_CUM}+D{R_NET}", f"=D{R_CUM}+E{R_NET}"]
for j, cL in enumerate(["B","C","D","E"]):
    c = ws.cell(row=R_CUM, column=2+j, value=formulas_cum[j])
    c.fill = HIGH_FILL; c.border = BORDER; c.font = BOLD; c.alignment = RIGHT
    c.number_format = '"¥"#,##0'
ws.cell(row=R_CUM, column=6, value="首次转正年 = 回收期").border = BORDER
ws.cell(row=R_CUM, column=6).font = SMALL
ws.cell(row=R_CUM, column=6).fill = NOTE_FILL
ws.cell(row=R_CUM, column=6).alignment = LEFT

# 6. 折现净现金流
ws.cell(row=R_DISC, column=1, value="折现净现金流").border = BORDER
ws.cell(row=R_DISC, column=1).alignment = LEFT
ws.cell(row=R_DISC, column=1).font = BOLD
for j, (cL, t) in enumerate(zip(["B","C","D","E"], [0,1,2,3])):
    c = ws.cell(row=R_DISC, column=2+j, value=f"={cL}{R_NET}/(1+{P('折现率 WACC')})^{t}")
    c.fill = CALC_FILL; c.border = BORDER; c.font = BOLD; c.alignment = RIGHT
    c.number_format = '"¥"#,##0'
ws.cell(row=R_DISC, column=6, value=f"按 WACC 折现到 Y0").border = BORDER
ws.cell(row=R_DISC, column=6).font = SMALL
ws.cell(row=R_DISC, column=6).fill = NOTE_FILL
ws.cell(row=R_DISC, column=6).alignment = LEFT

# 7. 累计折现净现金流
ws.cell(row=R_CUMD, column=1, value="累计折现净现金流").border = BORDER
ws.cell(row=R_CUMD, column=1).alignment = LEFT
ws.cell(row=R_CUMD, column=1).font = BOLD
formulas_cumd = [f"=B{R_DISC}", f"=B{R_CUMD}+C{R_DISC}", f"=C{R_CUMD}+D{R_DISC}", f"=D{R_CUMD}+E{R_DISC}"]
for j, cL in enumerate(["B","C","D","E"]):
    c = ws.cell(row=R_CUMD, column=2+j, value=formulas_cumd[j])
    c.fill = HIGH_FILL; c.border = BORDER; c.font = BOLD; c.alignment = RIGHT
    c.number_format = '"¥"#,##0'
ws.cell(row=R_CUMD, column=6, value="Y3 累计值 即 NPV（Y0→Y3）").border = BORDER
ws.cell(row=R_CUMD, column=6).font = SMALL
ws.cell(row=R_CUMD, column=6).fill = NOTE_FILL
ws.cell(row=R_CUMD, column=6).alignment = LEFT

for rn in [R_NET, R_CUM, R_DISC, R_CUMD]:
    ws.row_dimensions[rn].height = 22

# KPI 汇总
kpi_start = R_CUMD + 2
ws.merge_cells(start_row=kpi_start, start_column=1, end_row=kpi_start, end_column=6)
c = ws.cell(row=kpi_start, column=1, value="关键财务指标")
c.font = H2_FONT; c.fill = H2_FILL; c.alignment = CENTER

kpi_rows = [
    ("NPV（净现值）",
     f"=E{R_CUMD}",
     "越大越好；>0 项目就值得做"),
    ("IRR（内部收益率）",
     f"=IFERROR(IRR(B{R_NET}:E{R_NET}),\"需调整输入\")",
     "行业经验 AI 项目 IRR > 30% 算优秀"),
    ("投资回收期（年，静态）",
     # 用 MATCH 找首个累计>0 的列
     f"=IFERROR(MATCH(TRUE,INDEX(B{R_CUM}:E{R_CUM}>0,0),0)-1,\"超3年\")",
     "静态回收期，不折现"),
    ("三年总节省（不含一次性）",
     f"=SUM(C{R_SAVE}:E{R_SAVE})+SUM(C{R_SOFT}:E{R_SOFT})",
     ""),
    ("三年 ROI",
     f"=(SUM(C{R_SAVE}:E{R_SAVE})+SUM(C{R_SOFT}:E{R_SOFT})+B{R_CAPEX})/(-B{R_CAPEX})",
     "（总收益 - 投入）/ 投入"),
]

rr = kpi_start + 1
for name, formula, note in kpi_rows:
    ws.cell(row=rr, column=1, value=name).border = BORDER
    ws.cell(row=rr, column=1).alignment = LEFT
    ws.cell(row=rr, column=1).font = BOLD
    c = ws.cell(row=rr, column=2, value=formula)
    c.fill = HIGH_FILL; c.border = BORDER; c.font = BOLD; c.alignment = RIGHT
    if "ROI" in name or "IRR" in name:
        c.number_format = "0.00%"
    elif "回收期" in name:
        c.number_format = "0.0"
    else:
        c.number_format = '"¥"#,##0'
    ws.merge_cells(start_row=rr, start_column=3, end_row=rr, end_column=5)
    ws.cell(row=rr, column=3, value="").border = BORDER
    ws.cell(row=rr, column=6, value=note).border = BORDER
    ws.cell(row=rr, column=6).font = SMALL
    ws.cell(row=rr, column=6).fill = NOTE_FILL
    ws.cell(row=rr, column=6).alignment = LEFT
    ws.row_dimensions[rr].height = 22
    rr += 1

# ================================================================
# Sheet 7: 敏感性分析
# ================================================================
ws = wb.create_sheet("6-敏感性分析")
set_col_widths(ws, [24] + [15]*7)
put_title(ws, "6. 敏感性分析：AI 承接率 × 单次 AI 成本 → Y3 年度节省", span=8)

ws.cell(row=3, column=1, value="AI 承接率 Y3 ↓ / 单次AI成本 →").font = BOLD
ws.cell(row=3, column=1).fill = H2_FILL
ws.cell(row=3, column=1).font = H2_FONT
ws.cell(row=3, column=1).alignment = CENTER
ws.cell(row=3, column=1).border = BORDER

ai_costs = [0.10, 0.20, 0.30, 0.40, 0.50, 0.70, 1.00]
ai_rates = [0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]

for j, ac in enumerate(ai_costs):
    c = ws.cell(row=3, column=2+j, value=ac)
    c.fill = H2_FILL; c.font = H2_FONT; c.border = BORDER; c.alignment = CENTER
    c.number_format = "0.00"

start_sens_row = 4
for i, r in enumerate(ai_rates):
    row = start_sens_row + i
    c = ws.cell(row=row, column=1, value=r)
    c.fill = INPUT_FILL; c.font = BOLD; c.border = BORDER; c.alignment = CENTER
    c.number_format = "0.00%"
    for j, ac in enumerate(ai_costs):
        # 简化公式：Y3 节省 ≈ 基线 - 新成本（仅替换变量 AI承接率 & 单次AI成本）
        # 近似口径：保持 Copilot Y3 等其他参数不变
        formula = (
            f"=({BL_TOTAL_HUMAN})"
            # 新坐席成本（按 AI 承接率 r）
            f"-(({BL_YEAR_VOL}*(1-{r})*"
            f"({P('平均会话时长 AHT')}*(1-{P('Copilot 覆盖坐席比例 Y3')}*{P('Copilot 带来 AHT 降幅')})"
            f"+{P('事后处理时长 ACW')}*(1-{P('Copilot 覆盖坐席比例 Y3')}*{P('Copilot 带来 ACW 降幅')})))"
            f"/60/({P('坐席月均工时')}*12)"
            f")*{P('坐席月均全成本')}*12"
            # 质检（改造后）
            f"-({P('质检人员数')}*(1-{P('AI 质检员压缩比例')})*{P('质检员月均全成本')}*12)"
            # 主管按比例
            f"-({BL_MGR_COST}*(({BL_YEAR_VOL}*(1-{r})*"
            f"({P('平均会话时长 AHT')}*(1-{P('Copilot 覆盖坐席比例 Y3')}*{P('Copilot 带来 AHT 降幅')})"
            f"+{P('事后处理时长 ACW')}*(1-{P('Copilot 覆盖坐席比例 Y3')}*{P('Copilot 带来 ACW 降幅')})))"
            f"/60/({P('坐席月均工时')}*12))/{P('人工坐席数')})"
            # AI 成本
            f"-({BL_YEAR_VOL}*{r}*{ac})"
            f"-{P('AI 平台年订阅/摊销')}"
            f"-{P('AI 训练师/运营人数')}*{P('AI 训练师月均全成本')}*12"
            f"-{P('年度模型维护/迭代费')}"
        )
        c = ws.cell(row=row, column=2+j, value=formula)
        c.fill = CALC_FILL; c.border = BORDER; c.alignment = RIGHT; c.font = NORMAL
        c.number_format = '"¥"#,##0'

# 颜色标度：红→黄→绿
sens_range = f"B{start_sens_row}:H{start_sens_row+len(ai_rates)-1}"
ws.conditional_formatting.add(
    sens_range,
    ColorScaleRule(start_type="min", start_color="F8696B",
                   mid_type="percentile", mid_value=50, mid_color="FFEB84",
                   end_type="max", end_color="63BE7B"),
)

# 下方提示
tip_row = start_sens_row + len(ai_rates) + 2
ws.merge_cells(start_row=tip_row, start_column=1, end_row=tip_row, end_column=8)
c = ws.cell(row=tip_row, column=1,
    value="解读：绿色区域是你应该冲的目标；如果现实只能落在红色区域，说明项目 ROI 不成立，要么降投入、要么扩场景。")
c.font = BOLD; c.fill = HIGH_FILL; c.alignment = LEFT; c.border = BORDER
ws.row_dimensions[tip_row].height = 28

# ================================================================
# Sheet 8: Dashboard
# ================================================================
ws = wb.create_sheet("7-Dashboard")
set_col_widths(ws, [4, 30, 20, 4, 30, 20])
put_title(ws, "7. 汇报 Dashboard（一页纸）", span=6)

# 左列：基线
left_block = [
    ("—— 现状基线 ——", None),
    ("年会话量",        f"={BL_YEAR_VOL}"),
    ("坐席数",          f"={P('人工坐席数')}"),
    ("年人工总成本",    f"={BL_TOTAL_HUMAN}"),
    ("单次会话成本",    f"={BL_UNIT_COST}"),
    ("FCR",             f"={P('一解率 FCR')}"),
    ("质检覆盖率",      f"={P('质检覆盖率')}"),
    ("CSAT",            f"={P('CSAT 满意度')}"),
]

right_block = [
    ("—— Y3 改造后 ——", None),
    ("AI 承接率",        f"={P('AI 承接率 Y3')}"),
    ("改造后总成本",     f"={NEW_TOTAL_Y['Y3']}"),
    ("年度节省",         f"={SAVE_Y['Y3']}"),
    ("降本率",           f"={SAVE_PCT_Y['Y3']}"),
    ("新单次会话成本",   f"={NEW_UNIT_Y['Y3']}"),
    ("FCR",              f"={P('一解率 FCR')}+{P('FCR 提升（百分点）')}"),
    ("CSAT",             f"={P('CSAT 满意度')}+{P('预期 CSAT 提升')}"),
]

for i, ((lname, lformula), (rname, rformula)) in enumerate(zip(left_block, right_block)):
    row = 3 + i
    if lname.startswith("——"):
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=3)
        c = ws.cell(row=row, column=2, value=lname)
        c.font = H2_FONT; c.fill = H2_FILL; c.alignment = CENTER; c.border = BORDER
        ws.merge_cells(start_row=row, start_column=5, end_row=row, end_column=6)
        c = ws.cell(row=row, column=5, value=rname)
        c.font = H2_FONT; c.fill = H2_FILL; c.alignment = CENTER; c.border = BORDER
        ws.row_dimensions[row].height = 26
        continue

    ws.cell(row=row, column=2, value=lname).border = BORDER
    ws.cell(row=row, column=2).alignment = LEFT
    ws.cell(row=row, column=2).font = NORMAL
    c = ws.cell(row=row, column=3, value=lformula)
    c.fill = CALC_FILL; c.border = BORDER; c.font = BOLD; c.alignment = RIGHT
    if "CSAT" in lname or "FCR" in lname or "覆盖" in lname or "承接" in lname or "率" in lname:
        c.number_format = "0.00%"
    elif "成本" in lname:
        c.number_format = '"¥"#,##0.00' if "单次" in lname else '"¥"#,##0'
    else:
        c.number_format = "#,##0"

    ws.cell(row=row, column=5, value=rname).border = BORDER
    ws.cell(row=row, column=5).alignment = LEFT
    ws.cell(row=row, column=5).font = NORMAL
    c = ws.cell(row=row, column=6, value=rformula)
    c.fill = HIGH_FILL; c.border = BORDER; c.font = BOLD; c.alignment = RIGHT
    if "CSAT" in rname or "FCR" in rname or "率" in rname:
        c.number_format = "0.00%"
    elif "成本" in rname or "节省" in rname:
        c.number_format = '"¥"#,##0.00' if "单次" in rname else '"¥"#,##0'
    else:
        c.number_format = "#,##0"
    ws.row_dimensions[row].height = 22

# 底部关键结论
row = 3 + len(left_block) + 2
ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=6)
c = ws.cell(row=row, column=2, value="关键结论（Executive Summary）")
c.font = TITLE_FONT; c.fill = TITLE_FILL; c.alignment = CENTER; c.border = BORDER
ws.row_dimensions[row].height = 28

summary_lines = [
    ("1. 项目总投入",         f"={P('一次性建设投入')}",        '"¥"#,##0'),
    ("2. 三年总节省",         f"=SUM({SAVE_Y['Y1']},{SAVE_Y['Y2']},{SAVE_Y['Y3']})",       '"¥"#,##0'),
    ("3. NPV",                f"='5-三年现金流ROI'!E{R_CUMD}",  '"¥"#,##0'),
    ("4. IRR",                f"=IFERROR('5-三年现金流ROI'!B{kpi_start+2},\"N/A\")",    "0.00%"),
    ("5. 静态回收期（年）",   f"='5-三年现金流ROI'!B{kpi_start+3}","0.0"),
    ("6. 单次成本降幅",       f"=1-{NEW_UNIT_Y['Y3']}/{BL_UNIT_COST}",                "0.00%"),
]
for line, formula, nf in summary_lines:
    row += 1
    ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
    c = ws.cell(row=row, column=2, value=line)
    c.font = BOLD; c.alignment = LEFT; c.border = BORDER
    ws.merge_cells(start_row=row, start_column=5, end_row=row, end_column=6)
    c = ws.cell(row=row, column=5, value=formula)
    c.fill = HIGH_FILL; c.font = BOLD; c.alignment = RIGHT; c.border = BORDER
    c.number_format = nf
    ws.row_dimensions[row].height = 24

# ---------- 保存 ----------
import os
out_dir = "/projects/sandbox/kiro2026/templates"
os.makedirs(out_dir, exist_ok=True)
out_path = f"{out_dir}/AI客服ROI测算模板.xlsx"
wb.save(out_path)
print("OK:", out_path)
