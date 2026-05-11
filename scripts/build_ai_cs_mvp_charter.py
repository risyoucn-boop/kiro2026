"""
生成《AI 客服 MVP 项目立项书》Word 版 (.docx)。
内容与 Markdown 版同步，方便老板/PMO 使用 Word 模板。
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def set_cell_bg(cell, color_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tc_pr.append(shd)


def set_cell_font(cell, size=10.5, bold=False, color=None):
    for p in cell.paragraphs:
        for r in p.runs:
            r.font.size = Pt(size)
            r.font.name = "微软雅黑"
            r.font.bold = bold
            if color:
                r.font.color.rgb = RGBColor.from_string(color)
            r._element.rPr.rFonts.set(qn('w:eastAsia'), "微软雅黑")


def add_heading(doc, text, level=1, color=None):
    h = doc.add_heading(text, level=level)
    for r in h.runs:
        r.font.name = "微软雅黑"
        r._element.rPr.rFonts.set(qn('w:eastAsia'), "微软雅黑")
        if color:
            r.font.color.rgb = RGBColor.from_string(color)
    return h


def add_para(doc, text, bold=False, size=10.5, color=None, align=None):
    p = doc.add_paragraph()
    if align:
        p.alignment = align
    r = p.add_run(text)
    r.font.name = "微软雅黑"
    r._element.rPr.rFonts.set(qn('w:eastAsia'), "微软雅黑")
    r.font.size = Pt(size)
    r.font.bold = bold
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    return p


def add_bullet(doc, text, size=10.5):
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run(text)
    r.font.name = "微软雅黑"
    r._element.rPr.rFonts.set(qn('w:eastAsia'), "微软雅黑")
    r.font.size = Pt(size)
    return p


def add_table(doc, headers, rows, col_widths_cm=None, header_bg="1F4E78", header_color="FFFFFF"):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Light Grid Accent 1"
    # 表头
    for i, h in enumerate(headers):
        c = table.rows[0].cells[i]
        c.text = h
        set_cell_bg(c, header_bg)
        set_cell_font(c, size=10.5, bold=True, color=header_color)
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    # 行
    for r_idx, row in enumerate(rows, start=1):
        for c_idx, val in enumerate(row):
            c = table.rows[r_idx].cells[c_idx]
            c.text = str(val)
            set_cell_font(c, size=10)
            c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    # 列宽
    if col_widths_cm:
        for i, w in enumerate(col_widths_cm):
            for row in table.rows:
                row.cells[i].width = Cm(w)
    return table


# ==================== 开始构建 ====================
doc = Document()

# 页面设置
section = doc.sections[0]
section.page_height = Cm(29.7)
section.page_width = Cm(21.0)
section.top_margin = Cm(2.0)
section.bottom_margin = Cm(2.0)
section.left_margin = Cm(2.0)
section.right_margin = Cm(2.0)

# 默认字体
style = doc.styles["Normal"]
style.font.name = "微软雅黑"
style.font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn('w:eastAsia'), "微软雅黑")

# ========== 封面 ==========
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("\n\n\n")
add_para(doc, "AI 客服 MVP 项目立项书", bold=True, size=28, color="1F4E78", align=WD_ALIGN_PARAGRAPH.CENTER)
add_para(doc, "（Project Charter - Minimum Viable Product）", size=14, color="595959", align=WD_ALIGN_PARAGRAPH.CENTER)
add_para(doc, "\n\n")
add_para(doc, "申报单位：【请替换】", size=12, align=WD_ALIGN_PARAGRAPH.CENTER)
add_para(doc, "申报日期：【请替换】YYYY-MM-DD", size=12, align=WD_ALIGN_PARAGRAPH.CENTER)
add_para(doc, "文档版本：V1.0", size=12, align=WD_ALIGN_PARAGRAPH.CENTER)
add_para(doc, "密级：内部限阅", size=12, color="C00000", align=WD_ALIGN_PARAGRAPH.CENTER)
doc.add_page_break()

# ========== 0. 基本信息 ==========
add_heading(doc, "0. 项目基本信息", level=1, color="1F4E78")
add_table(doc,
    headers=["字段", "内容"],
    rows=[
        ["项目名称", "【请替换】AI 客服降本增效首期项目（MVP）"],
        ["项目编号", "【请替换】例：PRJ-2026-AICS-001"],
        ["项目类别", "数字化转型 / 降本增效 / AI 应用"],
        ["立项日期", "【请替换】YYYY-MM-DD"],
        ["项目发起人", "【请替换】姓名 / 职位"],
        ["项目负责人 (PM)", "【请替换】姓名 / 职位"],
        ["业务负责人", "【请替换】客服中心总监"],
        ["技术负责人", "【请替换】AI/IT 负责人"],
        ["财务对接人", "【请替换】"],
        ["预计开始", "【请替换】YYYY-MM"],
        ["预计交付", "【请替换】YYYY-MM（建议 90 天内）"],
        ["申请预算", "【请替换】¥XXX 万元（首年全口径）"],
        ["预期 Y1 节省", "【请替换】¥XXX 万元"],
        ["预期静态回收期", "【请替换】< 12 个月"],
    ],
    col_widths_cm=[4.5, 12.5],
)

doc.add_page_break()

# ========== 1. 执行摘要 ==========
add_heading(doc, "1. Executive Summary（执行摘要，一页纸）", level=1, color="1F4E78")
add_para(doc, "这一页是老板唯一会认真看的一页。务必简洁、有数字、有立场。", color="595959", size=9)

add_heading(doc, "1.1 我们要做什么", level=2)
add_para(doc, "用大模型（LLM）+ Agent 技术，在客服中心首期落地 3 个高 ROI 场景，90 天内跑通一条可复制的「人机混合」客服流水线。")

add_heading(doc, "1.2 为什么现在做（Why Now）", level=2)
for line in [
    "成本压力：当前单次人工会话成本约 ¥【XX】，全年人工成本 ¥【XX】，行业对标已下降 30-50%",
    "技术成熟：开源大模型（Qwen/DeepSeek）+ Dify/FastGPT 等平台已达生产级，私有化部署可控",
    "竞争压力：头部同行已上线 AI Copilot，再不动会在效率/体验上被拉开差距",
    "时机窗口：Token 价格仍在快速下降，早布局早摊销；晚 6 个月进入会错过一轮产品迭代",
]:
    add_bullet(doc, line)

add_heading(doc, "1.3 首期投多少、赚多少（The Number）", level=2)
add_table(doc,
    headers=["项", "金额"],
    rows=[
        ["一次性建设投入", "¥【XXX】万"],
        ["Y1 运营成本（AI 平台+人力）", "¥【XXX】万"],
        ["Y1 预计节省", "¥【XXX】万"],
        ["Y1 净收益", "¥【XXX】万"],
        ["三年累计节省", "¥【XXX】万"],
        ["回收期", "【X】个月"],
    ],
    col_widths_cm=[8, 9],
)

add_heading(doc, "1.4 我们需要什么支持", level=2)
for line in [
    "预算：¥【XXX】万（CapEx 一次性 + Y1 OpEx）",
    "人：专职 PM 1 人、AI 训练师 2-3 人、业务对接 1 人（原有坐席转岗）",
    "授权：知识库脱敏导出权限 / 订单系统只读 API / 客服录音调取",
    "决策：首期场景优先级认可（见第 3 节）",
]:
    add_bullet(doc, line)

add_heading(doc, "1.5 一句话结论", level=2)
add_para(doc,
    "花 300 万，第 1 年省 1500 万，3 年累计省 1 亿+，同时把 CSAT 从 82 提到 86。不做就是每天烧 4 万。",
    bold=True, color="C00000")

doc.add_page_break()

# ========== 2. 项目背景与问题定义 ==========
add_heading(doc, "2. 项目背景与问题定义", level=1, color="1F4E78")

add_heading(doc, "2.1 当前业务现状", level=2)
add_table(doc,
    headers=["指标", "现状值", "行业参考（同规模）", "差距"],
    rows=[
        ["月均会话量", "【XX】万次", "—", "—"],
        ["人工坐席数", "【XXX】人", "—", "—"],
        ["单次人工会话成本", "¥【X.X】", "¥ 3-6（电商）/ 6-15（金融）", "【对标评估】"],
        ["平均处理时长 AHT", "【X】分钟", "5-8 分钟", "【对标评估】"],
        ["事后处理时长 ACW", "【X】分钟", "2-3 分钟", "【对标评估】"],
        ["一解率 FCR", "【XX】%", "70-80%", "【对标评估】"],
        ["转人工率", "【XX】%", "30-50%", "【对标评估】"],
        ["质检覆盖率", "【X】%（抽检）", "100%（AI 全检）", "差距明显"],
        ["CSAT 满意度", "【XX】", "85+", "【对标评估】"],
        ["坐席月均流失率", "【XX】%", "15-20%", "【对标评估】"],
    ],
    col_widths_cm=[4, 3.5, 5.5, 4],
)

add_heading(doc, "2.2 痛点与机会", level=2)
add_para(doc, "痛点（来自一线访谈 / 客诉分析）：", bold=True)
for line in [
    "简单咨询占用大量坐席（查物流、改地址、退款进度 → 占全量会话 【XX】%），但现有规则机器人自助率仅 15%",
    "坐席培训周期长（新人 3-6 个月才能独立上岗），知识库散乱，遇到复杂问题查不到",
    "质检只能抽检 5%，服务态度/违规话术问题发现滞后，客诉后置",
    "会话结束后坐席要花 【X】分钟填工单，真正服务时间被挤压",
    "夜间/节假日值班成本高，人力排班难",
]:
    add_bullet(doc, line)

add_para(doc, "机会（技术+业务双轮驱动）：", bold=True)
for line in [
    "大模型让自然语言理解首次达到生产可用，RAG 技术让知识库「说话」",
    "开源模型 + 平台（Dify/LangChain）让私有化部署成本降到可接受范围",
    "内部沉淀了 【XX】年会话日志和知识文档，是训练/评估的优质语料",
]:
    add_bullet(doc, line)

add_heading(doc, "2.3 不做的代价（Do Nothing 情景分析）", level=2)
add_para(doc, "若 1 年内不启动：", bold=True)
for line in [
    "人工成本每年以 【X】% 上涨（社保+最低工资+招聘难度），多支出 ¥【XX】万",
    "同行上线 AI 后可能把单次成本降到 ¥【X】，我们价格/服务竞争力被拉开",
    "错过模型快速下降的第一波红利，后期补课更贵",
    "AI 训练师等人才被市场瓜分，招人成本翻倍",
]:
    add_bullet(doc, line)

doc.add_page_break()

# ========== 3. 项目目标 ==========
add_heading(doc, "3. 项目目标（SMART 原则）", level=1, color="1F4E78")

add_heading(doc, "3.1 业务目标（What）", level=2)
add_table(doc,
    headers=["#", "指标", "现状", "Y1 目标", "Y3 目标"],
    rows=[
        ["O1", "单次会话全口径成本", "¥【X.X】", "降至 ¥【X.X】（-30%）", "降至 ¥【X.X】（-60%）"],
        ["O2", "AI 承接率", "15%（旧机器人）", "40%", "70%"],
        ["O3", "坐席 AHT", "【X】分钟", "降 15%", "降 25%"],
        ["O4", "质检覆盖率", "5%", "100%", "100%"],
        ["O5", "FCR", "【XX】%", "+3pp", "+5pp"],
        ["O6", "CSAT", "【XX】", "+2pp", "+4pp"],
        ["O7", "Y1 年度降本", "—", "¥【XXX】万", "—"],
    ],
    col_widths_cm=[1.2, 4, 3.3, 4.5, 4],
)

add_heading(doc, "3.2 技术目标（How Good）", level=2)
add_table(doc,
    headers=["#", "指标", "目标"],
    rows=[
        ["T1", "RAG 回答准确率（首答正确率）", "≥ 85%"],
        ["T2", "大模型 P95 响应时延", "≤ 2 秒"],
        ["T3", "AI 平台可用性", "≥ 99.5%"],
        ["T4", "知识库条目", "≥ 【XXXX】条，结构化覆盖 Top 20 意图"],
        ["T5", "数据合规", "过《个人信息保护法》自评，模型私有化部署"],
    ],
    col_widths_cm=[1.2, 6, 9.8],
)

add_heading(doc, "3.3 不做的事（Out of Scope）", level=2)
add_para(doc, "明确 MVP 不包含：", bold=True)
for line in [
    "全自动处理资金类操作（退款/转账），首期仅「AI 推荐 + 人工确认」",
    "非中文客服场景",
    "与外部第三方 SaaS 的深度打通（仅对接内部系统）",
    "视频/图像客服（首期仅文本+语音转写）",
    "营销外呼 / 主动销售（不是成本中心场景，优先级不高）",
]:
    add_bullet(doc, line)

doc.add_page_break()

# ========== 4. 场景选型 ==========
add_heading(doc, "4. 首期场景选型（MVP Scope）", level=1, color="1F4E78")

add_heading(doc, "4.1 选型逻辑", level=2)
add_para(doc, "按「见效快 × 风险低 × 价值高」三角选择。参见《AI 客服 ROI 测算模板.xlsx - Sheet 4 分场景收益》。")

add_heading(doc, "4.2 首期 3 个场景（Must-Have）", level=2)
add_table(doc,
    headers=["#", "场景", "描述", "预估年节省", "实施难度", "交付月"],
    rows=[
        ["S1", "智能质检全覆盖", "AI 对 100% 会话做质检（违规话术、态度、服务标准），替代原抽检", "¥【XX】万", "低", "M1"],
        ["S2", "坐席 Copilot", "坐席侧嵌入话术推荐、知识检索、自动填单", "¥【XX】万", "中", "M2"],
        ["S3", "RAG 智能自助", "高频 FAQ / 查单 / 政策咨询由 AI 全自动承接，3 轮没解决转人工", "¥【XX】万", "中", "M3"],
    ],
    col_widths_cm=[1, 2.5, 6, 2.5, 2, 2],
)

add_heading(doc, "4.3 二期观察（Nice-to-Have，MVP 验证后决定）", level=2)
for line in [
    "S4 会话摘要 + 工单自动生成",
    "S5 智能外呼（满意度回访）",
    "S6 新人培训陪练机器人",
    "S7 全自动售后 Agent（需打通订单/支付/库存 API，风险最高，放最后）",
]:
    add_bullet(doc, line)

doc.add_page_break()

# ========== 5. 技术方案 ==========
add_heading(doc, "5. 技术方案（精简版）", level=1, color="1F4E78")

add_heading(doc, "5.1 架构概览", level=2)
add_para(doc,
    "分 5 层：客户入口 → 统一对话网关 → (AI 自助 | 人工坐席) → AI 中台（大模型+向量库+监控）→ 离线质检。\n"
    "完整架构图见附件《技术方案详细设计 HLD》。",
    size=10)

add_heading(doc, "5.2 技术选型建议", level=2)
add_table(doc,
    headers=["层", "选型", "理由", "备选"],
    rows=[
        ["大模型", "Qwen2.5-72B（私有化）", "中文强、可商用、成本可控", "DeepSeek-V3 / GLM-4"],
        ["编排平台", "Dify（自建）或 FastGPT", "开源、可私有化、有工作流", "LangChain"],
        ["向量库", "Milvus / PGVector", "生产级、支持大规模", "Chroma（仅 Demo）"],
        ["部署", "K8s + GPU 节点", "可扩展", "裸金属单机（起步）"],
        ["坐席 Copilot", "浏览器插件 / 工作台集成", "改造量小", "独立应用"],
        ["监控", "Langfuse / Phoenix", "LLM 专用", "Prometheus + 自建"],
    ],
    col_widths_cm=[2.5, 4, 6, 4.5],
)
add_para(doc,
    "立场：强烈建议开源模型私有化 + 开源平台，长期边际成本是 SaaS 的 1/3，且客服数据不出域。",
    bold=True, color="C00000")

add_heading(doc, "5.3 数据与合规", level=2)
for line in [
    "数据分级：客户对话属二级敏感，严格脱敏后进入训练/评估集",
    "模型部署：全部私有化部署，不调用公有云 API 处理客户 PII",
    "审计：所有 AI 回复留痕 180 天以上",
    "合规：过《个保法》《生成式 AI 服务管理办法》自评，必要时备案",
]:
    add_bullet(doc, line)

doc.add_page_break()

# ========== 6. 预算明细 ==========
add_heading(doc, "6. 预算明细", level=1, color="1F4E78")

add_heading(doc, "6.1 一次性投入（CapEx）", level=2)
add_table(doc,
    headers=["项目", "金额（万元）", "说明"],
    rows=[
        ["硬件：GPU 服务器 x 【N】台", "【XX】", "4×H20 或等效，支持 Qwen-72B"],
        ["软件：AI 平台 License（自建开源则为 0）", "【XX】", "—"],
        ["实施外包（乙方）", "【XX】", "数据治理+集成+定制开发"],
        ["数据治理（内部）", "【XX】", "知识库清洗、意图标注"],
        ["初始知识库建设", "【XX】", "—"],
        ["培训与变革管理", "【XX】", "坐席培训、AI 训练师培训"],
        ["风险预留（10%）", "【XX】", "—"],
        ["小计（CapEx）", "【XXX】", "—"],
    ],
    col_widths_cm=[7, 3, 7],
)

add_heading(doc, "6.2 年度运营成本（OpEx，Y1）", level=2)
add_table(doc,
    headers=["项目", "金额（万元/年）", "说明"],
    rows=[
        ["大模型 API / GPU 摊销", "【XX】", "按 Y1 预估会话量"],
        ["AI 平台订阅 / 维护", "【XX】", "—"],
        ["AI 训练师（2-3 人）", "【XX】", "新增岗位"],
        ["运维 / 监控", "【XX】", "—"],
        ["模型迭代 / 知识库运营", "【XX】", "持续投入"],
        ["小计（OpEx-Y1）", "【XXX】", "—"],
    ],
    col_widths_cm=[7, 3, 7],
)

add_heading(doc, "6.3 总预算申请", level=2)
add_table(doc,
    headers=["科目", "金额（万元）"],
    rows=[
        ["Y0（CapEx）", "【XXX】"],
        ["Y1（OpEx）", "【XXX】"],
        ["首年合计", "【XXX】"],
    ],
    col_widths_cm=[8, 9],
)
add_para(doc, "详细 ROI 测算见附件《AI 客服 ROI 测算模板.xlsx》", size=9, color="595959")

doc.add_page_break()

# ========== 7. 组织与资源 ==========
add_heading(doc, "7. 组织与资源", level=1, color="1F4E78")

add_heading(doc, "7.1 项目组架构", level=2)
add_para(doc, "指导委员会（CXO/客服总/CIO/CFO）→ 项目负责人（PM）→ AI 技术组 / 业务产品组 / 数据合规组 + 用户代表", size=10)

add_heading(doc, "7.2 关键角色与职责", level=2)
add_table(doc,
    headers=["角色", "人数", "职责", "投入"],
    rows=[
        ["项目负责人 (PM)", "1", "全局协调、里程碑管理、对上汇报", "100%"],
        ["业务产品经理", "1", "场景设计、需求拆解、验收", "100%"],
        ["AI 训练师", "2-3", "Prompt、知识库、评估集、Bad Case 复盘", "100%"],
        ["对话设计师", "1", "人机接力流程、话术、意图体系", "80%"],
        ["数据工程师", "1", "数据脱敏、ETL、向量库", "50%"],
        ["模型/平台工程师", "1-2", "部署、编排、监控", "100%"],
        ["质检/运营主管", "1", "AI 质检规则落地、复核", "50%"],
        ["合规/法务", "1", "个保、模型备案", "20%"],
    ],
    col_widths_cm=[3, 1.5, 10, 2.5],
)

add_heading(doc, "7.3 变革管理（Change Management）", level=2)
add_para(doc, "这是 AI 项目最容易翻车的点，必须配专人：", bold=True)
for line in [
    "坐席沟通：一开始就明确「AI 不是取代人，是让人做更有价值的事」，配合转岗通道",
    "KPI 重设：不能继续按「接单量」考核，要改为「FCR + CSAT + AI 协同度」",
    "培训：每个坐席至少 4 学时 Copilot 使用培训",
    "激励：首期设定「AI 使用之星」奖励，打消抵触",
]:
    add_bullet(doc, line)

doc.add_page_break()

# ========== 8. 项目计划 ==========
add_heading(doc, "8. 项目计划（90 天 MVP）", level=1, color="1F4E78")

add_heading(doc, "8.1 关键里程碑（Gate Review）", level=2)
add_table(doc,
    headers=["里程碑", "时间", "交付物", "通过标准 (Gate)"],
    rows=[
        ["M1：项目启动", "W1", "立项批复、团队 Kickoff", "预算到位、团队就位"],
        ["M2：基线 & 准备", "W4", "成本基线报告、知识库 V1、评估集", "基线数据通过业务确认"],
        ["M3：智能质检上线", "W8", "AI 质检系统 100% 全量", "质检准确率≥85%，质检员工作量下降≥60%"],
        ["M4：Copilot 试点", "W10", "Copilot 覆盖 20% 坐席", "AHT 下降≥10%，坐席 NPS≥40"],
        ["M5：RAG 自助灰度", "W12", "RAG 承接 10% 流量", "首答准确率≥85%，转人工率≤20%"],
        ["M6：项目收尾", "W13", "ROI 报告、二期立项书", "Y1 预期 ROI 达成立项承诺 80%+"],
    ],
    col_widths_cm=[3, 1.5, 5, 7.5],
)

add_heading(doc, "8.2 核心任务 WBS（摘要）", level=2)
add_table(doc,
    headers=["WBS", "任务", "负责人", "工期"],
    rows=[
        ["1.1", "成本基线与场景选型", "PM", "2 周"],
        ["1.2", "技术选型与 POC", "技术负责人", "2 周"],
        ["2.1", "知识库清洗（Top 20 意图）", "训练师 + 业务", "3 周"],
        ["2.2", "评估集构建（≥ 500 条）", "训练师", "2 周"],
        ["2.3", "合规评估与备案", "合规", "4 周（并行）"],
        ["3.1", "AI 质检规则 + 模型调优", "训练师", "3 周"],
        ["3.2", "质检系统集成上线", "技术", "2 周"],
        ["4.1", "Copilot 插件开发", "技术", "4 周"],
        ["4.2", "坐席培训与灰度", "业务 + PM", "2 周"],
        ["5.1", "RAG 链路 + 人机接力设计", "对话设计师 + 技术", "4 周"],
        ["5.2", "RAG 灰度与监控", "技术", "2 周"],
        ["6.1", "ROI 核算与复盘", "PM + 财务", "1 周"],
        ["6.2", "二期立项书", "PM", "1 周"],
    ],
    col_widths_cm=[1.2, 7, 5, 3.8],
)

doc.add_page_break()

# ========== 9. 成功指标 ==========
add_heading(doc, "9. 成功指标与验收标准（Acceptance Criteria）", level=1, color="1F4E78")

add_heading(doc, "9.1 必须达成（硬指标）", level=2)
add_table(doc,
    headers=["#", "指标", "验收值", "数据来源"],
    rows=[
        ["A1", "智能质检覆盖率", "100%", "质检系统统计"],
        ["A2", "AI 质检员工作量压缩", "≥ 60%", "HR + 质检系统"],
        ["A3", "RAG 首答准确率（评估集）", "≥ 85%", "自动化评估"],
        ["A4", "RAG 承接率（灰度期，M3 末）", "≥ 25%", "对话网关统计"],
        ["A5", "Copilot 覆盖坐席", "≥ 60%", "工位系统"],
        ["A6", "Copilot 带来 AHT 下降", "≥ 10%", "坐席系统"],
        ["A7", "系统可用性", "≥ 99.5%", "监控平台"],
        ["A8", "CSAT 不劣化", "≥ 现状基线", "问卷/回访"],
        ["A9", "零重大事故", "0 次 P0", "事故管理"],
        ["A10", "Y1 节省达成度", "≥ 立项承诺 80%", "财务核算"],
    ],
    col_widths_cm=[1.2, 6, 4.5, 5.3],
)

add_heading(doc, "9.2 加分项（软指标）", level=2)
for line in [
    "CSAT 提升 ≥ 2pp",
    "坐席 NPS 提升",
    "对外宣传案例 1 篇",
    "申请 1 项专利 / 软著",
]:
    add_bullet(doc, line)

doc.add_page_break()

# ========== 10. 风险与应对 ==========
add_heading(doc, "10. 风险与应对", level=1, color="1F4E78")

add_table(doc,
    headers=["#", "风险", "概率", "影响", "应对措施", "责任人"],
    rows=[
        ["R1", "AI 回答错误导致客诉", "中", "高", "置信度阈值+低于则转人工；禁 AI 单独决定资金操作；舆情监控", "业务 PM"],
        ["R2", "坐席抵触 / 工会反对", "中", "高", "明确不裁员先转岗；先做 Copilot 再做自助；AI 训练师从老坐席选拔", "HRBP"],
        ["R3", "知识库质量差导致 RAG 翻车", "高", "高", "第一阶段重投入知识治理；Top 20 意图先做；Bad Case 每日复盘", "训练师"],
        ["R4", "模型幻觉 / 法律风险", "中", "高", "AI 回答加「仅供参考」兜底；承诺类走人工；保留完整对话日志", "合规"],
        ["R5", "大模型 Token 价格上涨", "低", "中", "优先私有化，SaaS 作为兜底", "技术"],
        ["R6", "项目延期", "中", "中", "90 天含 2 周 buffer；每 2 周 Gate Review；必要时砍二期保一期", "PM"],
        ["R7", "数据泄露", "低", "极高", "全链路私有化；PII 脱敏入库；权限最小化；年度渗透测试", "安全"],
        ["R8", "内部老系统集成难度超预期", "高", "中", "首期只读 API 不改老系统；必要时 RPA 打补丁", "技术"],
        ["R9", "招不到 AI 训练师", "中", "中", "内部优秀坐席+知识运营转岗培养；外包过渡", "HR"],
        ["R10", "合规审查不通过", "低", "极高", "立项阶段就拉合规/法务进场，不后置", "合规"],
    ],
    col_widths_cm=[1, 3, 1.2, 1.2, 8.6, 2],
)

doc.add_page_break()

# ========== 11. 决策请求 ==========
add_heading(doc, "11. 决策请求（Decision Ask）", level=1, color="1F4E78")
add_para(doc, "请投委会 / 指导委员会审议：", bold=True)
for line in [
    "☐ 批准立项（预算 ¥【XXX】万，工期 90 天）",
    "☐ 批准专职团队组建（AI 训练师 2-3 人、对话设计师 1 人）",
    "☐ 批准数据使用权限（知识库脱敏导出、订单系统只读 API）",
    "☐ 任命项目负责人：【姓名】",
    "☐ 确认 M3/M4/M5 三个 Gate 评审机制",
]:
    add_para(doc, "  " + line, size=11)

# ========== 12. 附件 ==========
add_heading(doc, "12. 附件清单", level=1, color="1F4E78")
add_table(doc,
    headers=["#", "文档", "状态"],
    rows=[
        ["1", "《AI 客服 ROI 测算模板.xlsx》", "✅ 已提交"],
        ["2", "《现状基线调研报告》", "【待补】"],
        ["3", "《场景选型评估报告》", "【待补】"],
        ["4", "《技术方案详细设计（HLD）》", "【待补】"],
        ["5", "《合规与数据安全评估报告》", "【待补】"],
        ["6", "《知识库现状盘点》", "【待补】"],
        ["7", "《供应商/外包商评估报告》", "【待补】"],
    ],
    col_widths_cm=[1.2, 11, 4.8],
)

doc.add_page_break()

# ========== 13. 签批页 ==========
add_heading(doc, "13. 签批页（Sign-off）", level=1, color="1F4E78")
add_table(doc,
    headers=["角色", "姓名", "签字", "日期"],
    rows=[
        ["项目发起人", "", "", ""],
        ["项目负责人", "", "", ""],
        ["业务负责人（客服）", "", "", ""],
        ["技术负责人", "", "", ""],
        ["财务负责人", "", "", ""],
        ["法务/合规", "", "", ""],
        ["指导委员会主席", "", "", ""],
    ],
    col_widths_cm=[4.5, 3.5, 5, 4],
)

add_para(doc, "\n\n文档版本：V1.0", size=9, color="595959")
add_para(doc, "最后更新：【请替换】", size=9, color="595959")
add_para(doc, "文档负责人：【请替换】", size=9, color="595959")

# ========== 保存 ==========
import os
out_dir = "/projects/sandbox/kiro2026/templates"
os.makedirs(out_dir, exist_ok=True)
out_path = f"{out_dir}/AI客服MVP立项书模板.docx"
doc.save(out_path)
print("OK:", out_path)
