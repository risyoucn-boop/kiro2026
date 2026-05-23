"""All hand-designed base icon concepts, grouped by category.

A *base* is a tuple:
    (key, cn_name, en_name, parts_factory, metaphor, usage, keywords_cn, keywords_en)

`parts_factory` is a zero-arg callable that returns a fresh list of part dicts.
We always construct fresh lists because downstream transforms mutate them.
"""
from __future__ import annotations

from builders import (
    rect, circle, ellipse, line, polygon, path, donut, star, gear, arrow,
    round_rect, square_centered, triangle, diamond, hex_h, hex_v,
    cross_x, plus_cross, check_mark, exclam, question,
    small_arrow_up, small_arrow_down, small_arrow_right, small_arrow_left,
    doc_outline, folder_outline, shield_outline, chevron_right,
    speech_bubble, cloud_outline, heart_path, person_glyph,
    magnifier, clock_glyph, bullseye, gauge_glyph,
    lightbulb_glyph, flag_glyph, lock_glyph, key_glyph,
    envelope_glyph, chat_bubble_pair, phone_glyph,
    chart_bars, chart_line, chart_pie,
    database_cylinder, factory_glyph, server_rack, robot_glyph,
    calendar_glyph, hand_glyph, briefcase_glyph, book_glyph,
    bell_glyph, funnel_glyph, link_glyph, cycle_glyph,
)


# ============================================================
# 01 DATA — 数据指标趋势
# ============================================================

DATA_BASES = [
    ("trend_up", "趋势上升", "TrendingUp",
     lambda: [arrow(3, 19, 21, 6, shaft_w=2.4, head_w=6.5, head_l=5.5)],
     "向上箭头表示指标增长", "用于业绩、活跃度、转化率等正向指标的可视化",
     ["上升", "增长", "向上", "提升", "增长率"], ["up", "growth", "rise", "increase"]),

    ("trend_down", "趋势下降", "TrendingDown",
     lambda: [arrow(3, 5, 21, 18, shaft_w=2.4, head_w=6.5, head_l=5.5)],
     "向下箭头表示指标下滑", "用于不良率、流失率、成本下降等指标",
     ["下降", "下滑", "下行", "回落"], ["down", "decline", "drop"]),

    ("bar_chart", "柱状图", "BarChart",
     lambda: chart_bars((6, 11, 16)),
     "三根柱子象征对比维度", "用于横向对比类业务，如分组数据、月份对比",
     ["柱状", "对比", "条形", "分组"], ["bar", "compare", "histogram"]),

    ("bar_chart_5", "多列柱状", "BarChart5",
     lambda: chart_bars((4, 8, 12, 9, 14), x_start=3, bar_w=2.4, gap=1.4),
     "多柱表示更多分组细节", "适合多维度细分的对比展示",
     ["多柱", "细分", "对比"], ["bars", "segmented", "breakdown"]),

    ("line_chart", "折线图", "LineChart",
     lambda: chart_line([(4, 17), (8, 11), (12, 14), (16, 7), (20, 9)]),
     "折线表示时间序列", "用于趋势、走势、时序变化",
     ["折线", "趋势", "时序", "走势"], ["line", "trend", "timeseries"]),

    ("pie_chart", "饼图", "PieChart",
     lambda: chart_pie(),
     "圆环切分表示占比", "用于结构占比、份额分布",
     ["饼图", "占比", "份额", "结构"], ["pie", "share", "distribution"]),

    ("dashboard", "仪表盘", "Dashboard",
     lambda: gauge_glyph(),
     "速度表象征核心指标", "用于综合健康度、KPI驾驶舱",
     ["仪表盘", "驾驶舱", "KPI", "核心指标"], ["dashboard", "gauge", "kpi"]),

    ("kpi_card", "指标卡", "KpiCard",
     lambda: [
         round_rect(2, 5, 20, 14, 1.5),
         rect(4, 8, 8, 1.4, rx=0.4),
         rect(4, 11, 12, 2.4, rx=0.4),
         arrow(15, 16, 19, 12, shaft_w=1.0, head_w=2.6, head_l=2.0),
     ],
     "一张卡片+一个指标+一个箭头", "用于看板单卡、首屏KPI",
     ["指标卡", "看板", "卡片"], ["kpi", "card", "metric"]),

    ("scatter", "散点分布", "ScatterPlot",
     lambda: [
         rect(2, 21, 20, 1, rx=0.2),
         rect(2, 3, 1, 19, rx=0.2),
         circle(7, 17, 1.0), circle(10, 13, 1.0), circle(11, 18, 1.0),
         circle(14, 9, 1.0), circle(16, 14, 1.0), circle(18, 7, 1.0),
         circle(19, 11, 1.0), circle(8, 8, 1.0),
     ],
     "离散点图象征样本分布", "用于相关性分析、数据探索",
     ["散点", "分布", "相关性"], ["scatter", "distribution", "correlation"]),

    ("growth_curve", "增长曲线", "GrowthCurve",
     lambda: [
         rect(2, 21, 20, 1, rx=0.2),
         rect(2, 3, 1, 19, rx=0.2),
         path("M 3 19 C 8 19 11 18 13 14 C 15 10 17 6 21 4 L 21 6 C 18 7 16 11 14 15 C 12 19 8 21 3 21 Z"),
     ],
     "S形/J形曲线象征指数增长", "用于增长黑客、用户增长、复利场景",
     ["增长曲线", "指数", "复利"], ["growth", "curve", "exponential"]),

    ("target", "目标靶心", "Target",
     lambda: bullseye(),
     "靶心象征精准目标", "用于OKR、KPI、目标管理",
     ["靶心", "目标", "精准", "OKR"], ["target", "bullseye", "okr"]),

    ("funnel_data", "漏斗数据", "DataFunnel",
     lambda: funnel_glyph(),
     "漏斗象征逐层筛选", "用于转化漏斗、流量漏斗",
     ["漏斗", "筛选", "转化"], ["funnel", "filter", "conversion"]),

    ("pulse", "心电脉搏", "Pulse",
     lambda: [
         path("M 2 12 L 6 12 L 8 6 L 11 18 L 14 9 L 16 14 L 18 12 L 22 12"),
     ],
     "脉冲线象征活跃/异常点", "用于实时监控、心跳健康度",
     ["脉冲", "心跳", "实时", "活跃"], ["pulse", "heartbeat", "live"]),

    ("calendar_data", "日数据", "DailyMetric",
     lambda: calendar_glyph(),
     "日历+点位象征日维度数据", "用于日报、按天指标",
     ["日报", "日数据", "按天"], ["daily", "calendar", "day"]),

    ("ranking", "排行榜", "Ranking",
     lambda: [
         rect(4, 12, 4, 8, rx=0.4),
         rect(10, 6, 4, 14, rx=0.4),
         rect(16, 10, 4, 10, rx=0.4),
         polygon([(11.2, 4), (12.8, 4), (12.0, 2.5)]),
         rect(2, 20, 20, 1, rx=0.2),
     ],
     "Top榜单的领奖台造型", "用于销售排行、人员排名",
     ["排行", "Top", "领奖台"], ["ranking", "top", "leaderboard"]),
]


# ============================================================
# 02 TRAIN — 员工培训辅导
# ============================================================

TRAIN_BASES = [
    ("classroom", "课堂教学", "Classroom",
     lambda: [
         rect(3, 4, 18, 11, rx=0.6),
         line(2, 14.5, 22, 14.5, w=0.8),
         circle(7, 19, 1.6), circle(12, 19, 1.6), circle(17, 19, 1.6),
         rect(6, 7, 12, 1.0, rx=0.3),
         rect(6, 9.5, 8, 1.0, rx=0.3),
     ],
     "黑板+座位象征课堂", "用于培训课程、内训",
     ["课堂", "教学", "培训"], ["classroom", "training", "lesson"]),

    ("instructor", "讲师授课", "Instructor",
     lambda: [
         circle(8, 6, 2.6),
         path("M 3 21 L 3 12 Q 3 9 8 9 Q 13 9 13 12 L 13 16 L 11 16 L 11 21 Z"),
         rect(15, 8, 6, 7, rx=0.4),
         rect(15.6, 14.6, 0.5, 6, rx=0.2),
     ],
     "讲师在白板前授课", "用于讲师/导师场景",
     ["讲师", "导师", "授课"], ["instructor", "trainer", "teach"]),

    ("mentor_pair", "师徒辅导", "MentorPair",
     lambda: [
         circle(8, 7, 2.4), circle(16, 8.5, 1.8),
         path("M 4 21 L 4 13 Q 4 11 8 11 Q 12 11 12 13 L 12 21 Z"),
         path("M 13 21 L 13 14 Q 13 12.5 16 12.5 Q 19 12.5 19 14 L 19 21 Z"),
         line(11, 9, 13.5, 10, w=0.8),
     ],
     "一前一后表示一对一辅导", "用于带教、1V1、师徒关系",
     ["带教", "1V1", "师徒"], ["mentor", "coach", "pair"]),

    ("book_open", "书本", "OpenBook",
     lambda: book_glyph(),
     "翻开的书象征学习", "用于学习材料、教材",
     ["书本", "教材", "学习"], ["book", "study", "textbook"]),

    ("certificate_train", "结业证书", "Certificate",
     lambda: [
         round_rect(3, 4, 18, 14, 1.0),
         rect(5, 7, 14, 1.0, rx=0.3),
         rect(5, 9.5, 10, 1.0, rx=0.3),
         circle(17, 18, 2.6),
         polygon([(15.5, 19), (16.5, 22), (17.5, 21), (18.5, 22), (18.5, 19)]),
     ],
     "证书+绶带象征认证", "用于结业、考核通过",
     ["证书", "认证", "结业"], ["certificate", "diploma", "cert"]),

    ("idea_bulb", "灵感想法", "IdeaBulb",
     lambda: lightbulb_glyph(),
     "灯泡象征启发", "用于知识点、灵感、创新",
     ["灵感", "想法", "灯泡"], ["idea", "bulb", "insight"]),

    ("podium", "讲台演讲", "Podium",
     lambda: [
         rect(8, 13, 8, 8, rx=0.4),
         rect(7, 12, 10, 1.4, rx=0.3),
         circle(12, 5, 2.4),
         rect(11, 7.6, 2, 5, rx=0.4),
     ],
     "讲台+演讲者", "用于演讲、宣讲会",
     ["讲台", "演讲", "宣讲"], ["podium", "speech", "lectern"]),

    ("video_lesson", "视频课程", "VideoLesson",
     lambda: [
         round_rect(2, 4, 20, 14, 1.0),
         polygon([(10, 8), (10, 14), (15, 11)]),
         rect(8, 19, 8, 1.4, rx=0.4),
     ],
     "播放按钮象征视频学习", "用于在线课程、录播",
     ["视频", "课程", "在线学习"], ["video", "course", "lesson"]),

    ("award_badge", "学习徽章", "AwardBadge",
     lambda: [
         star(12, 11, 9.5, 4.0, points=8, rot=-90),
         circle(12, 11, 4.5),
         polygon([(8.5, 14), (9.5, 22), (12, 19), (14.5, 22), (15.5, 14)]),
     ],
     "勋章+绶带象征学习成就", "用于积分徽章、学习成就",
     ["徽章", "勋章", "成就"], ["badge", "award", "medal"]),

    ("exam_paper", "考核试卷", "ExamPaper",
     lambda: [
         round_rect(4, 2, 16, 20, 0.8),
         rect(7, 6, 7, 1.0, rx=0.3),
         rect(7, 9, 10, 1.0, rx=0.3),
         rect(7, 12, 8, 1.0, rx=0.3),
         circle(7, 16.5, 1.0),
         line(9.5, 16, 16, 16, w=0.8),
         circle(7, 19, 1.0),
         line(9.5, 18.5, 16, 18.5, w=0.8),
     ],
     "试卷+选项象征考核", "用于测验、考核、问卷",
     ["试卷", "考核", "测验"], ["exam", "test", "quiz"]),

    ("group_study", "小组学习", "GroupStudy",
     lambda: [
         circle(7, 7, 2.0),
         circle(17, 7, 2.0),
         circle(12, 6, 2.0),
         path("M 3 18 L 3 14 Q 3 12 7 12 Q 10 12 10 14"),
         path("M 14 18 L 14 14 Q 14 12 17 12 Q 21 12 21 14 L 21 18"),
         path("M 8 18 L 8 13 Q 8 11.5 12 11.5 Q 16 11.5 16 13 L 16 18 Z"),
         rect(2, 18, 20, 1.0, rx=0.3),
     ],
     "三人头像象征团队学习", "用于小组讨论、共学",
     ["小组", "团队", "共学"], ["group", "team", "study"]),

    ("brain_train", "脑力", "Brain",
     lambda: [
         path(
             "M 7 7 "
             "C 5 7 4 9 4 11 "
             "C 3 11 3 14 5 14 "
             "C 5 17 8 18 10 17 "
             "L 10 21 "
             "L 14 21 "
             "L 14 17 "
             "C 16 18 19 17 19 14 "
             "C 21 14 21 11 20 11 "
             "C 20 9 19 7 17 7 "
             "C 17 5 13 5 12 7 "
             "C 11 5 7 5 7 7 Z"
         ),
         line(12, 7, 12, 17, w=0.6),
     ],
     "大脑剪影象征思维", "用于学习、思考、AI 训练",
     ["大脑", "思维", "脑力"], ["brain", "mind", "thinking"]),

    ("seedling", "成长萌芽", "Seedling",
     lambda: [
         rect(11, 14, 2, 7, rx=0.4),
         path("M 12 14 C 6 12 4 8 4 4 C 9 4 12 8 12 14 Z"),
         path("M 12 14 C 18 12 20 8 20 4 C 15 4 12 8 12 14 Z"),
         rect(2, 21, 20, 1.0, rx=0.3),
     ],
     "新芽象征成长", "用于新人成长、能力萌芽",
     ["成长", "萌芽", "新人"], ["seedling", "grow", "sprout"]),

    ("tree_knowledge", "知识树", "KnowledgeTree",
     lambda: [
         circle(12, 8, 5.5),
         circle(7, 11, 4.0),
         circle(17, 11, 4.0),
         rect(11, 14, 2, 7, rx=0.4),
         rect(2, 21, 20, 1.0, rx=0.3),
     ],
     "树状结构象征知识体系", "用于课程体系、能力树",
     ["知识树", "课程体系", "能力树"], ["tree", "skill-tree", "syllabus"]),
]


# ============================================================
# 03 CUST — 客户沟通触达
# ============================================================

CUST_BASES = [
    ("chat_pair", "对话双方", "ChatPair",
     lambda: chat_bubble_pair(),
     "两个气泡象征双向沟通", "用于在线客服、IM对话",
     ["对话", "聊天", "沟通"], ["chat", "messaging", "im"]),

    ("phone_call", "电话呼出", "PhoneCall",
     lambda: phone_glyph(),
     "听筒象征电话沟通", "用于呼出、电销、客服",
     ["电话", "呼出", "话务"], ["call", "phone", "voice"]),

    ("envelope_mail", "邮件信封", "Envelope",
     lambda: envelope_glyph(),
     "信封象征邮件触达", "用于邮件营销、通知",
     ["邮件", "信封", "EDM"], ["mail", "email", "envelope"]),

    ("sms_message", "短信", "SmsMessage",
     lambda: [
         path("M 2 5 Q 2 3 4 3 L 20 3 Q 22 3 22 5 L 22 14 Q 22 16 20 16 L 9 16 L 5 20 L 5 16 L 4 16 Q 2 16 2 14 Z"),
         circle(8, 9.5, 1.0), circle(12, 9.5, 1.0), circle(16, 9.5, 1.0),
     ],
     "气泡+省略号象征短消息", "用于短信、IM 通知",
     ["短信", "消息", "SMS"], ["sms", "message", "text"]),

    ("video_call", "视频通话", "VideoCall",
     lambda: [
         round_rect(2, 6, 14, 12, 1.2),
         polygon([(16, 9), (22, 6), (22, 18), (16, 15)]),
     ],
     "摄像机外形象征视频会议", "用于视频会议、远程沟通",
     ["视频", "通话", "会议"], ["video", "call", "meeting"]),

    ("headset_service", "客服耳机", "Headset",
     lambda: [
         path("M 4 13 Q 4 4 12 4 Q 20 4 20 13 L 20 17 L 17 17 L 17 12 L 19 12 Q 18 7 12 7 Q 6 7 5 12 L 7 12 L 7 17 L 4 17 Z"),
         rect(4, 17, 4, 4, rx=0.6),
         rect(16, 17, 4, 4, rx=0.6),
     ],
     "耳麦象征客服坐席", "用于客服中心、坐席",
     ["客服", "耳机", "坐席"], ["headset", "support", "agent"]),

    ("megaphone", "营销喇叭", "Megaphone",
     lambda: [
         path("M 3 13 L 3 11 L 9 9 L 18 4 L 18 20 L 9 15 L 7 15 L 7 18 L 5 18 L 5 15 L 4 15 Q 3 15 3 13 Z"),
         path("M 19 9 Q 22 9 22 12 Q 22 15 19 15"),
     ],
     "扩音器象征传播", "用于活动宣传、营销触达",
     ["营销", "宣传", "扩音"], ["megaphone", "promote", "broadcast"]),

    ("customer_face", "客户头像", "CustomerFace",
     lambda: person_glyph(),
     "用户头像象征客户主体", "用于客户档案、个人中心",
     ["客户", "用户", "头像"], ["user", "customer", "profile"]),

    ("contact_book", "通讯录", "ContactBook",
     lambda: [
         round_rect(4, 3, 16, 18, 1.2),
         rect(2, 6, 3, 1.4), rect(2, 11, 3, 1.4), rect(2, 16, 3, 1.4),
         circle(13, 9, 2.0),
         path("M 8 18 Q 8 14 13 14 Q 18 14 18 18"),
     ],
     "联系人列表象征CRM", "用于客户档案、联系人",
     ["通讯录", "联系人", "CRM"], ["contacts", "address-book", "crm"]),

    ("meeting_calendar", "会议安排", "MeetingCalendar",
     lambda: [
         round_rect(3, 5, 18, 16, 1.2),
         rect(3, 5, 18, 4),
         rect(7, 2.5, 1.6, 4, rx=0.5),
         rect(15.4, 2.5, 1.6, 4, rx=0.5),
         circle(8, 14, 1.4), circle(12, 14, 1.4), circle(16, 14, 1.4),
         rect(7, 17, 10, 1.0, rx=0.3),
     ],
     "日历+联络人象征会议", "用于客户拜访、会议预约",
     ["会议", "拜访", "约见"], ["meeting", "appointment", "visit"]),

    ("broadcast_signal", "广播信号", "Broadcast",
     lambda: [
         circle(12, 13, 2.4),
         path("M 7 16 Q 5 13 7 10"),
         path("M 17 16 Q 19 13 17 10"),
         path("M 4 18 Q 1 13 4 8"),
         path("M 20 18 Q 23 13 20 8"),
     ],
     "信号波象征广撒触达", "用于群发、广播、推送",
     ["广播", "推送", "群发"], ["broadcast", "push", "blast"]),

    ("notification_bell", "提醒通知", "Notification",
     lambda: bell_glyph(),
     "铃铛象征实时提醒", "用于站内信、推送",
     ["提醒", "通知", "铃铛"], ["notification", "bell", "alert"]),

    ("mailbox_inbox", "收件箱", "Mailbox",
     lambda: [
         path("M 3 11 L 7 5 L 17 5 L 21 11 L 21 19 L 3 19 Z"),
         line(7, 5, 7, 11, w=0.6),
         line(17, 5, 17, 11, w=0.6),
         rect(3, 11, 4, 2.0, rx=0.2),
         rect(17, 11, 4, 2.0, rx=0.2),
     ],
     "邮筒象征收件入口", "用于收件箱、待处理",
     ["收件箱", "邮筒", "待办"], ["inbox", "mailbox", "incoming"]),

    ("touchpoint", "客户触点", "Touchpoint",
     lambda: [
         circle(12, 12, 2.6),
         circle(12, 12, 5.5),
         circle(12, 12, 9),
         line(12, 12, 12, 12.1, w=0.4),
     ],
     "同心圆象征触达层级", "用于触点策略、覆盖度",
     ["触点", "触达", "覆盖"], ["touchpoint", "reach", "coverage"]),
]


# ============================================================
# 04 SALE — 服销增长转化
# ============================================================

SALE_BASES = [
    ("cart", "购物车", "ShoppingCart",
     lambda: [
         path(
             "M 3 5 L 6 5 L 7 8 L 21 8 L 19 16 L 8 16 L 7 13"
         ),
         circle(9, 19, 1.6), circle(17, 19, 1.6),
     ],
     "购物车象征下单", "用于电商下单、购买",
     ["购物车", "下单", "购买"], ["cart", "order", "buy"]),

    ("money_bag", "钱袋", "MoneyBag",
     lambda: [
         path(
             "M 8 5 L 8 7 Q 4 9 4 14 Q 4 21 12 21 Q 20 21 20 14 Q 20 9 16 7 L 16 5 Z"
         ),
         rect(7, 4, 10, 2.0, rx=0.4),
         rect(11, 11, 2, 6, rx=0.4),
         rect(9, 13, 6, 1.4, rx=0.3),
     ],
     "钱袋+￥象征收入", "用于营收、入账",
     ["收入", "营收", "钱袋"], ["money", "revenue", "income"]),

    ("coin_stack", "金币堆", "CoinStack",
     lambda: [
         ellipse(12, 6, 7, 2.4),
         path("M 5 6 L 5 9 Q 5 11.4 12 11.4 Q 19 11.4 19 9 L 19 6"),
         path("M 5 11 L 5 14 Q 5 16.4 12 16.4 Q 19 16.4 19 14 L 19 11"),
         path("M 5 16 L 5 19 Q 5 21.4 12 21.4 Q 19 21.4 19 19 L 19 16"),
     ],
     "金币堆象征积累", "用于营收累计、积分",
     ["金币", "积累", "积分"], ["coin", "stack", "points"]),

    ("growth_arrow", "增长向上", "GrowthArrow",
     lambda: [
         arrow(3, 19, 21, 6, shaft_w=2.4, head_w=6.5, head_l=5.5),
         rect(2, 21, 20, 1.0, rx=0.3),
     ],
     "曲线箭头+底线象征业绩增长", "用于业绩、GMV",
     ["业绩增长", "向上", "GMV"], ["sales", "growth", "gmv"]),

    ("handshake", "握手成交", "Handshake",
     lambda: [
         path(
             "M 2 10 L 7 8 L 10 11 L 12 9 L 14 11 L 17 8 L 22 10 L 22 14 L 17 16 L 12 14 L 7 16 L 2 14 Z"
         ),
     ],
     "握手象征达成", "用于签约、合作",
     ["握手", "成交", "签约"], ["handshake", "deal", "agreement"]),

    ("contract_signed", "签约合同", "ContractSigned",
     lambda: [
         doc_outline(4, 2, 15, 20, 4)[0],
         rect(7, 9, 9, 1.0, rx=0.3),
         rect(7, 12, 7, 1.0, rx=0.3),
         path("M 13 17 Q 14 16 15 18 Q 16 20 17 19"),
     ],
     "合同+签字象征签约", "用于签约率、订单达成",
     ["合同", "签约", "订单"], ["contract", "agreement", "signed"]),

    ("sales_funnel", "销售漏斗", "SalesFunnel",
     lambda: funnel_glyph(),
     "漏斗象征销售线索", "用于销售漏斗、Pipeline",
     ["销售漏斗", "线索", "Pipeline"], ["funnel", "pipeline", "leads"]),

    ("conversion", "转化", "Conversion",
     lambda: [
         circle(6, 12, 3.5),
         arrow(10, 12, 14, 12, shaft_w=1.4, head_w=3.6, head_l=2.6),
         polygon([(18, 8), (22, 12), (18, 16), (18, 13.5), (15, 13.5), (15, 10.5), (18, 10.5)]),
     ],
     "圆变方象征状态转换", "用于转化率、状态扭转",
     ["转化", "转换", "扭转"], ["conversion", "convert", "transform"]),

    ("discount_tag", "折扣标签", "DiscountTag",
     lambda: [
         path("M 3 11 L 11 3 L 21 3 L 21 13 L 13 21 Z"),
         circle(17, 7, 1.6),
         line(8, 13, 14, 7, w=1.4),
         circle(8, 13, 1.0),
         circle(14, 7, 1.0),
     ],
     "标签+%象征促销", "用于活动、促销",
     ["折扣", "促销", "标签"], ["discount", "promo", "tag"]),

    ("vip_crown", "VIP皇冠", "VipCrown",
     lambda: [
         path("M 3 18 L 5 8 L 9 12 L 12 6 L 15 12 L 19 8 L 21 18 Z"),
         rect(3, 18, 18, 2.0, rx=0.4),
         circle(5, 8, 1.0), circle(12, 6, 1.0), circle(19, 8, 1.0),
     ],
     "皇冠象征高价值客户", "用于VIP、KA客户",
     ["VIP", "皇冠", "高价值"], ["vip", "crown", "premium"]),

    ("storefront", "门店", "Storefront",
     lambda: [
         path("M 2 8 L 4 4 L 20 4 L 22 8 L 22 10 L 2 10 Z"),
         rect(3, 10, 18, 11, rx=0),
         rect(8, 13, 8, 8, rx=0.3),
         rect(11, 13, 2, 8),
     ],
     "门店外立面象征线下网点", "用于门店、网点",
     ["门店", "网点", "门头"], ["store", "shop", "branch"]),

    ("product_box", "商品包装", "ProductBox",
     lambda: [
         polygon([(3, 8), (12, 4), (21, 8), (21, 18), (12, 22), (3, 18)]),
         line(12, 4, 12, 22, w=0.6),
         line(3, 8, 21, 8, w=0.6),
     ],
     "立体盒子象征SKU", "用于商品、SKU",
     ["商品", "SKU", "包装盒"], ["product", "sku", "package"]),

    ("wallet", "钱包", "Wallet",
     lambda: [
         round_rect(2, 6, 20, 14, 1.4),
         path("M 2 9 L 18 9 Q 19 9 19 10 L 19 13 L 22 13 L 22 16 L 19 16 L 19 17 Q 19 18 18 18 L 2 18 Z",
              fill_rule="evenodd"),
         circle(20, 14.5, 0.9),
     ],
     "钱包象征支付场景", "用于支付、账户",
     ["钱包", "支付", "账户"], ["wallet", "pay", "account"]),

    ("balance_scale", "天平", "BalanceScale",
     lambda: [
         rect(11, 4, 2, 17, rx=0.4),
         rect(4, 8, 16, 1.2, rx=0.3),
         path("M 4 9 L 1 14 L 7 14 Z"),
         path("M 20 9 L 17 14 L 23 14 Z"),
         rect(8, 21, 8, 1.0, rx=0.3),
     ],
     "天平象征价值/取舍", "用于成本收益、对比",
     ["天平", "对比", "成本收益"], ["balance", "scale", "compare"]),
]


# ============================================================
# 05 RISK — 风险合规管控
# ============================================================

RISK_BASES = [
    ("shield", "盾牌防护", "Shield",
     shield_outline,
     "盾牌象征防护", "用于安全、风控总盾",
     ["盾牌", "防护", "安全"], ["shield", "protect", "guard"]),

    ("lock_secure", "加锁", "Lock",
     lock_glyph,
     "锁象征访问控制", "用于权限、加密",
     ["加锁", "权限", "加密"], ["lock", "secure", "access"]),

    ("alert_triangle", "警告三角", "AlertTriangle",
     lambda: [
         polygon([(12, 2.5), (22, 21), (2, 21)]),
         rect(11.2, 9, 1.6, 6, rx=0.5),
         circle(12, 17.5, 0.9),
     ],
     "三角+!是国际通用预警标识", "用于异常、预警",
     ["警告", "预警", "三角"], ["alert", "warning", "exclaim"]),

    ("audit_clipboard", "审计清单", "AuditClipboard",
     lambda: [
         round_rect(5, 4, 14, 18, 0.8),
         rect(8, 2.5, 8, 3, rx=0.6),
         line(7, 9, 9, 11, w=0.9),
         line(9, 11, 13, 7, w=0.9),
         rect(7, 13, 10, 1.0, rx=0.3),
         rect(7, 16, 10, 1.0, rx=0.3),
         rect(7, 19, 7, 1.0, rx=0.3),
     ],
     "审计单象征核查记录", "用于稽核、审计",
     ["审计", "稽核", "核查"], ["audit", "check", "review"]),

    ("scale_law", "天平公正", "JusticeScale",
     lambda: [
         rect(11, 4, 2, 17, rx=0.4),
         rect(4, 8, 16, 1.2, rx=0.3),
         path("M 4 9 L 1 14 L 7 14 Z"),
         path("M 20 9 L 17 14 L 23 14 Z"),
         rect(8, 21, 8, 1.0, rx=0.3),
     ],
     "天平象征公正/合规", "用于合规、法务",
     ["合规", "法务", "公正"], ["compliance", "legal", "justice"]),

    ("magnifier_inspect", "审查放大镜", "MagnifierInspect",
     magnifier,
     "放大镜象征审查", "用于风险扫描、审查",
     ["审查", "放大镜", "扫描"], ["inspect", "scan", "review"]),

    ("fingerprint", "指纹识别", "Fingerprint",
     lambda: [
         path(
             "M 12 4 C 7 4 4 8 4 12 C 4 14 5 16 6 17"
         ),
         path(
             "M 12 7 C 9 7 7 9 7 12 C 7 14 8 16 9 17"
         ),
         path(
             "M 12 10 C 11 10 10 11 10 12 C 10 14 11 16 12 17"
         ),
         path(
             "M 12 4 C 17 4 20 8 20 12 C 20 16 18 18 16 19"
         ),
         path(
             "M 12 13 C 13 13 14 14 14 16 C 14 18 13 20 12 20"
         ),
     ],
     "指纹象征身份认证", "用于实名、生物识别",
     ["指纹", "实名", "生物识别"], ["fingerprint", "biometric", "id"]),

    ("gavel", "法槌", "Gavel",
     lambda: [
         polygon([(2, 8), (8, 2), (16, 10), (10, 16)]),
         line(11, 11, 21, 21, w=2.4),
         rect(2, 19, 12, 2.0, rx=0.4),
     ],
     "法槌象征裁定", "用于合规裁定、规则",
     ["法槌", "裁定", "规则"], ["gavel", "ruling", "rule"]),

    ("fire_extinguisher", "灭火器", "FireExtinguisher",
     lambda: [
         rect(8, 6, 8, 13, rx=1.0),
         rect(7, 4, 10, 2.4, rx=0.4),
         path("M 16 8 L 21 8 L 21 11 L 18 11"),
         line(8, 11, 16, 11, w=0.6),
     ],
     "灭火器象征应急处置", "用于应急、突发处理",
     ["灭火器", "应急", "突发"], ["emergency", "incident", "fire"]),

    ("siren", "警报", "Siren",
     lambda: [
         path("M 4 17 Q 4 8 12 8 Q 20 8 20 17 Z"),
         rect(2, 17, 20, 2, rx=0.4),
         rect(11, 4, 2, 4, rx=0.4),
         line(7, 6, 4, 4, w=0.8),
         line(17, 6, 20, 4, w=0.8),
     ],
     "警灯象征报警", "用于风险警报",
     ["警报", "警灯", "报警"], ["siren", "alarm", "alert"]),

    ("eye_inspect", "审查之眼", "EyeInspect",
     lambda: [
         path("M 2 12 Q 6 5 12 5 Q 18 5 22 12 Q 18 19 12 19 Q 6 19 2 12 Z M 12 8 C 9.8 8 8 9.8 8 12 C 8 14.2 9.8 16 12 16 C 14.2 16 16 14.2 16 12 C 16 9.8 14.2 8 12 8 Z",
              fill_rule="evenodd"),
         circle(12, 12, 2.0),
     ],
     "眼睛象征监督", "用于监督、可视化",
     ["监督", "可视化", "审查"], ["watch", "monitor", "supervise"]),

    ("monitor_screen", "监控屏", "MonitorScreen",
     lambda: [
         round_rect(2, 4, 20, 13, 1.0),
         rect(2, 14, 20, 1.0, rx=0.2),
         rect(8, 18, 8, 1.4, rx=0.3),
         rect(10, 17, 4, 1.4),
         line(5, 8, 9, 12, w=0.8),
         line(9, 12, 12, 9, w=0.8),
         line(12, 9, 16, 13, w=0.8),
         line(16, 13, 19, 7, w=0.8),
     ],
     "屏幕+曲线象征监控大屏", "用于风控大屏",
     ["监控", "大屏", "实时"], ["monitor", "screen", "console"]),

    ("seal_stamp", "印章", "SealStamp",
     lambda: [
         circle(12, 9, 6.5),
         star(12, 9, 4.5, 1.8, points=5, rot=-90),
         rect(4, 17, 16, 1.4, rx=0.3),
         rect(2, 19, 20, 2, rx=0.4),
     ],
     "印章象征官方批准", "用于官方文件、批准",
     ["印章", "公章", "批准"], ["seal", "stamp", "approved"]),

    ("policy_doc", "制度文档", "PolicyDoc",
     lambda: [
         doc_outline(4, 2, 15, 20, 4)[0],
         rect(7, 7, 9, 1.0, rx=0.3),
         rect(7, 10, 9, 1.0, rx=0.3),
         rect(7, 13, 7, 1.0, rx=0.3),
         polygon([(15.5, 17), (16, 19.5), (17.5, 18.2), (19, 19.5), (18.5, 17)]),
     ],
     "文档+绶带象征制度", "用于制度、规章",
     ["制度", "规章", "政策"], ["policy", "regulation", "rule"]),
]


# ============================================================
# 06 FLOW — 流程机制闭环
# ============================================================

FLOW_BASES = [
    ("flowchart_node", "流程节点", "FlowNode",
     lambda: [
         round_rect(2, 9, 7, 6, 0.8),
         round_rect(15, 9, 7, 6, 0.8),
         arrow(9, 12, 15, 12, shaft_w=1.4, head_w=3.4, head_l=2.6),
     ],
     "两节点+连线象征流程片段", "用于流程图、节点",
     ["流程", "节点", "步骤"], ["flow", "node", "step"]),

    ("cycle_loop", "闭环循环", "CycleLoop",
     cycle_glyph,
     "循环箭头象征闭环", "用于PDCA、迭代",
     ["闭环", "循环", "PDCA"], ["cycle", "loop", "pdca"]),

    ("refresh", "刷新", "Refresh",
     lambda: [
         path(
             "M 12 4 C 7 4 3 8 3 13 L 5 13 C 5 9 8 6 12 6 C 14 6 16 7 17 8 L 14 8 L 14 10 L 21 10 L 21 3 L 19 3 L 19 6 C 17 4 15 4 12 4 Z"
         ),
         path(
             "M 12 20 C 17 20 21 16 21 11 L 19 11 C 19 15 16 18 12 18 C 10 18 8 17 7 16 L 10 16 L 10 14 L 3 14 L 3 21 L 5 21 L 5 18 C 7 20 9 20 12 20 Z"
         ),
     ],
     "双向刷新象征更新", "用于刷新、同步",
     ["刷新", "同步", "更新"], ["refresh", "sync", "update"]),

    ("swap_arrows", "交换", "Swap",
     lambda: [
         path("M 4 8 L 18 8 L 18 5 L 22 9 L 18 13 L 18 10 L 4 10 Z"),
         path("M 20 16 L 6 16 L 6 13 L 2 17 L 6 21 L 6 18 L 20 18 Z"),
     ],
     "对向箭头象征互换", "用于换岗、互换",
     ["交换", "互换", "换岗"], ["swap", "exchange", "switch"]),

    ("chain_link", "链条衔接", "ChainLink",
     link_glyph,
     "锁链象征环节衔接", "用于上下游衔接",
     ["链条", "衔接", "上下游"], ["chain", "link", "connect"]),

    ("decision_diamond", "决策菱形", "DecisionDiamond",
     lambda: [
         diamond(12, 12, 10),
         path("M 9.6 11.6 L 11 13 L 14.5 9.5", fill_rule="nonzero"),
         line(9.6, 11.6, 11, 13, w=1.4),
         line(11, 13, 14.5, 9.5, w=1.4),
     ],
     "菱形象征决策点", "用于决策节点、分支",
     ["决策", "判断", "菱形"], ["decision", "branch", "diamond"]),

    ("gear_pair", "齿轮联动", "GearPair",
     lambda: [
         gear(8, 9, r_outer=6, r_inner=4.4, hole_r=1.6, teeth=8),
         gear(16, 16, r_outer=5, r_inner=3.6, hole_r=1.4, teeth=8),
     ],
     "双齿轮象征联动机制", "用于机制设计、联动",
     ["齿轮", "联动", "机制"], ["gear", "mechanism", "link"]),

    ("pipeline", "管道流水线", "Pipeline",
     lambda: [
         rect(2, 10, 7, 4, rx=0.4),
         rect(11, 10, 7, 4, rx=0.4),
         rect(20, 10, 2, 4, rx=0.4),
         rect(8, 10, 4, 4, rx=0),
         rect(17, 10, 4, 4, rx=0),
         circle(5, 6, 1.0), circle(14, 18, 1.0),
     ],
     "节段管道象征流水线", "用于工序、流水",
     ["管道", "流水", "工序"], ["pipeline", "flow", "stage"]),

    ("kanban", "看板", "Kanban",
     lambda: [
         round_rect(2, 4, 20, 16, 0.8),
         rect(7, 4, 0.6, 16),
         rect(13, 4, 0.6, 16),
         rect(4, 7, 3, 2.4, rx=0.3),
         rect(4, 11, 3, 2.4, rx=0.3),
         rect(8.5, 7, 4, 2.4, rx=0.3),
         rect(8.5, 11, 4, 2.4, rx=0.3),
         rect(15, 7, 5, 2.4, rx=0.3),
     ],
     "三栏看板象征任务流", "用于Kanban、任务管理",
     ["看板", "任务", "Kanban"], ["kanban", "board", "task"]),

    ("loop_arrow", "循环箭头", "LoopArrow",
     lambda: [
         path(
             "M 5 6 L 17 6 L 17 4 L 21 7 L 17 10 L 17 8 L 7 8 L 7 14 L 5 14 Z"
         ),
         path(
             "M 19 18 L 7 18 L 7 20 L 3 17 L 7 14 L 7 16 L 17 16 L 17 10 L 19 10 Z"
         ),
     ],
     "U形回路象征反馈闭环", "用于反馈循环",
     ["循环", "反馈", "回路"], ["loop", "feedback"]),

    ("milestone", "里程碑", "Milestone",
     lambda: [
         polygon([(12, 3), (14.6, 5.6), (12, 8), (9.4, 5.6)]),
         rect(11, 8, 2, 14, rx=0.3),
         rect(2, 21, 20, 1.0, rx=0.3),
     ],
     "桩石+杆象征里程碑", "用于阶段节点",
     ["里程碑", "阶段", "节点"], ["milestone", "stage"]),

    ("route_path", "路径", "RoutePath",
     lambda: [
         circle(4, 7, 2.0),
         circle(12, 17, 2.0),
         circle(20, 7, 2.0),
         path("M 4 7 Q 8 7 8 12 Q 8 17 12 17 Q 16 17 16 12 Q 16 7 20 7", fill_rule="nonzero"),
         line(4, 7, 8, 12, w=1.0),
         line(8, 12, 12, 17, w=1.0),
         line(12, 17, 16, 12, w=1.0),
         line(16, 12, 20, 7, w=1.0),
     ],
     "S形路径象征流程走向", "用于业务路径",
     ["路径", "走向", "路线"], ["route", "path", "way"]),

    ("branch_split", "分支拆分", "BranchSplit",
     lambda: [
         circle(5, 12, 1.8),
         circle(19, 6, 1.8),
         circle(19, 18, 1.8),
         line(7, 12, 17, 6, w=1.0),
         line(7, 12, 17, 18, w=1.0),
     ],
     "一拆二象征分支", "用于分支、并行",
     ["分支", "拆分", "并行"], ["branch", "split", "parallel"]),

    ("merge_arrows", "汇聚合并", "MergeArrows",
     lambda: [
         circle(5, 6, 1.8),
         circle(5, 18, 1.8),
         circle(19, 12, 1.8),
         line(7, 6, 17, 12, w=1.0),
         line(7, 18, 17, 12, w=1.0),
     ],
     "二合一象征汇聚", "用于合并、汇集",
     ["汇聚", "合并", "汇集"], ["merge", "join", "converge"]),
]


# ============================================================
# 07 AI — AI 机器人自动化
# ============================================================

AI_BASES = [
    ("robot_face", "机器人头", "RobotFace",
     robot_glyph,
     "可爱机器人象征AI", "用于AI助手、机器人",
     ["机器人", "AI", "助手"], ["robot", "ai", "bot"]),

    ("brain_chip", "脑+芯片", "BrainChip",
     lambda: [
         path(
             "M 7 7 C 5 7 4 9 4 11 C 3 11 3 14 5 14 C 5 17 8 18 10 17 L 10 21 L 14 21 L 14 17 C 16 18 19 17 19 14 C 21 14 21 11 20 11 C 20 9 19 7 17 7 C 17 5 13 5 12 7 C 11 5 7 5 7 7 Z"
         ),
         rect(10, 9.5, 4, 4, rx=0.4),
         line(8, 10.5, 10, 10.5, w=0.6),
         line(8, 12.5, 10, 12.5, w=0.6),
         line(14, 10.5, 16, 10.5, w=0.6),
         line(14, 12.5, 16, 12.5, w=0.6),
     ],
     "脑+芯片象征智能算力", "用于AI内核、模型",
     ["大脑", "芯片", "算力"], ["brain", "chip", "compute"]),

    ("sparkle_ai", "智能闪光", "Sparkle",
     lambda: [
         star(12, 12, 9, 2.5, points=4, rot=-90),
         star(20, 5, 2.6, 0.7, points=4, rot=-90),
         star(4, 7, 1.6, 0.5, points=4, rot=-90),
     ],
     "四角星象征AI生成", "用于AI生成内容标识",
     ["AI生成", "智能", "Sparkle"], ["sparkle", "magic", "ai"]),

    ("neural_net", "神经网络", "NeuralNet",
     lambda: [
         circle(4, 5, 1.6), circle(4, 12, 1.6), circle(4, 19, 1.6),
         circle(12, 8, 1.6), circle(12, 16, 1.6),
         circle(20, 12, 1.6),
         line(4, 5, 12, 8, w=0.6),
         line(4, 5, 12, 16, w=0.6),
         line(4, 12, 12, 8, w=0.6),
         line(4, 12, 12, 16, w=0.6),
         line(4, 19, 12, 8, w=0.6),
         line(4, 19, 12, 16, w=0.6),
         line(12, 8, 20, 12, w=0.6),
         line(12, 16, 20, 12, w=0.6),
     ],
     "节点+连线象征神经网络", "用于深度学习、模型",
     ["神经网络", "深度学习", "模型"], ["neural", "network", "deep"]),

    ("automation_arm", "自动化机械臂", "AutomationArm",
     lambda: [
         rect(2, 19, 20, 2, rx=0.3),
         rect(10, 13, 4, 8, rx=0.3),
         rect(8, 11, 8, 2, rx=0.3),
         rect(13, 5, 2, 8, rx=0.3),
         rect(11, 3, 6, 2.4, rx=0.4),
         circle(14, 9, 1.0),
     ],
     "机械臂+底座象征自动化", "用于RPA、机械化",
     ["自动化", "机械臂", "RPA"], ["automation", "arm", "rpa"]),

    ("chatbot", "对话机器人", "Chatbot",
     lambda: [
         round_rect(3, 4, 18, 12, 1.6),
         circle(9, 10, 1.2), circle(15, 10, 1.2),
         rect(9, 12.5, 6, 1.2, rx=0.4),
         rect(11.2, 16, 1.6, 3),
         polygon([(10, 19), (14, 19), (12, 21)]),
     ],
     "聊天气泡+笑脸象征对话机器人", "用于Chatbot、智能客服",
     ["聊天机器人", "Chatbot", "智能客服"], ["chatbot", "bot", "ai-agent"]),

    ("smart_assistant", "智能助手", "SmartAssistant",
     lambda: [
         circle(12, 10, 6),
         rect(11, 16, 2, 5, rx=0.3),
         rect(8, 21, 8, 1.0, rx=0.3),
         star(7, 5, 1.8, 0.5, points=4, rot=-90),
         star(18, 5, 1.4, 0.4, points=4, rot=-90),
         circle(10, 9, 0.9), circle(14, 9, 0.9),
         path("M 9 12 Q 12 14 15 12"),
         line(9, 12, 12, 13.6, w=0.7),
         line(12, 13.6, 15, 12, w=0.7),
     ],
     "笑脸+sparkle象征AI助手", "用于AI助手、Copilot",
     ["AI助手", "Copilot", "智能助手"], ["copilot", "assistant", "ai"]),

    ("vision_eye", "AI视觉", "Vision",
     lambda: [
         path("M 2 12 Q 6 5 12 5 Q 18 5 22 12 Q 18 19 12 19 Q 6 19 2 12 Z M 12 8 C 9.8 8 8 9.8 8 12 C 8 14.2 9.8 16 12 16 C 14.2 16 16 14.2 16 12 C 16 9.8 14.2 8 12 8 Z",
              fill_rule="evenodd"),
         star(12, 12, 3.0, 1.0, points=4, rot=-90),
     ],
     "眼睛+sparkle象征视觉AI", "用于CV、图像识别",
     ["视觉AI", "图像识别", "CV"], ["vision", "cv", "image"]),

    ("model_layer", "模型层", "ModelLayer",
     lambda: [
         path("M 12 3 L 22 8 L 12 13 L 2 8 Z"),
         path("M 12 11 L 22 16 L 12 21 L 2 16 Z"),
     ],
     "层叠平面象征多层模型", "用于神经层、模型结构",
     ["模型层", "Layer", "多层"], ["layer", "model", "stack"]),

    ("prompt_box", "Prompt 提示词", "PromptBox",
     lambda: [
         round_rect(2, 5, 20, 14, 1.0),
         rect(5, 9, 12, 1.2, rx=0.3),
         rect(5, 12, 9, 1.2, rx=0.3),
         rect(5, 15, 6, 1.2, rx=0.3),
         star(19, 8, 1.4, 0.5, points=4, rot=-90),
     ],
     "对话框+sparkle象征Prompt", "用于提示词、Prompt工程",
     ["Prompt", "提示词", "对话框"], ["prompt", "input", "ai"]),

    ("training_loop", "训练循环", "TrainingLoop",
     lambda: [
         circle(12, 12, 6.5),
         path("M 8 7 L 5 5 L 5 9 Z"),
         path("M 16 17 L 19 19 L 19 15 Z"),
         circle(12, 12, 2.0),
     ],
     "循环+中心点象征模型训练", "用于训练迭代",
     ["训练", "迭代", "Loop"], ["training", "iter", "loop"]),

    ("dataset", "数据集", "Dataset",
     database_cylinder,
     "圆柱体象征数据存储", "用于数据集、数据库",
     ["数据集", "数据库", "存储"], ["dataset", "database", "storage"]),

    ("embedding", "向量空间", "Embedding",
     lambda: [
         rect(2, 21, 20, 1.0, rx=0.3),
         rect(2, 3, 1.0, 19, rx=0.3),
         circle(7, 7, 1.4), circle(11, 11, 1.4), circle(15, 9, 1.4),
         circle(9, 15, 1.4), circle(17, 13, 1.4), circle(13, 17, 1.4),
         line(7, 7, 11, 11, w=0.5),
         line(11, 11, 9, 15, w=0.5),
         line(11, 11, 15, 9, w=0.5),
         line(15, 9, 17, 13, w=0.5),
     ],
     "散点+连线象征embedding空间", "用于向量、相似度",
     ["向量", "Embedding", "相似度"], ["embedding", "vector", "similarity"]),

    ("llm_box", "大模型容器", "LlmBox",
     lambda: [
         round_rect(3, 4, 18, 16, 1.6),
         rect(7, 8, 10, 1.2, rx=0.3),
         rect(7, 11, 10, 1.2, rx=0.3),
         rect(7, 14, 7, 1.2, rx=0.3),
         star(18, 7, 1.4, 0.4, points=4, rot=-90),
         rect(11, 21, 2, 1.4, rx=0.3),
     ],
     "盒子+sparkle象征LLM", "用于大模型、生成",
     ["大模型", "LLM", "生成"], ["llm", "gpt", "model"]),
]


# ============================================================
# 08 KNOW — 知识库与文档
# ============================================================

KNOW_BASES = [
    ("doc_plain", "文档", "Document",
     lambda: doc_outline(),
     "带折角的文档", "用于通用文档",
     ["文档", "Doc", "文件"], ["doc", "file", "document"]),

    ("folder", "文件夹", "Folder",
     folder_outline,
     "文件夹象征归档", "用于目录、归档",
     ["文件夹", "目录", "归档"], ["folder", "directory", "archive"]),

    ("book_open2", "书籍", "Book",
     book_glyph,
     "书本象征知识载体", "用于教材、书籍",
     ["书籍", "教材", "知识"], ["book", "manual"]),

    ("tag", "标签", "Tag",
     lambda: [
         path("M 3 11 L 11 3 L 21 3 L 21 13 L 13 21 Z"),
         circle(17, 7, 1.6),
     ],
     "标签贴象征分类", "用于打标、分类",
     ["标签", "分类", "Tag"], ["tag", "label", "category"]),

    ("bookmark", "书签", "Bookmark",
     lambda: [
         path("M 6 3 L 18 3 L 18 21 L 12 16 L 6 21 Z"),
     ],
     "书签象征收藏", "用于收藏、书签",
     ["书签", "收藏", "Bookmark"], ["bookmark", "save", "favorite"]),

    ("note_pin", "便签", "Note",
     lambda: [
         round_rect(4, 5, 16, 14, 0.8),
         rect(7, 8, 10, 1.0, rx=0.3),
         rect(7, 11, 10, 1.0, rx=0.3),
         rect(7, 14, 7, 1.0, rx=0.3),
         circle(12, 4, 1.6),
         rect(11.4, 4, 1.2, 4),
     ],
     "便签+图钉象征贴附", "用于备忘、便签",
     ["便签", "Note", "备忘"], ["note", "memo", "pin"]),

    ("doc_search", "文档搜索", "DocSearch",
     lambda: [
         doc_outline(2, 2, 12, 16, 3)[0],
         circle(17, 14, 4),
         line(20, 17, 22, 19, w=1.6),
     ],
     "文档+放大镜象征检索", "用于知识检索、查文档",
     ["搜索", "检索", "查文档"], ["search", "find", "lookup"]),

    ("library", "图书馆", "Library",
     lambda: [
         rect(3, 5, 3, 16, rx=0.3),
         rect(7, 7, 3, 14, rx=0.3),
         rect(11, 4, 3, 17, rx=0.3),
         rect(15, 6, 3, 15, rx=0.3),
         rect(19, 8, 2, 13, rx=0.3),
         rect(2, 21, 20, 1, rx=0.3),
     ],
     "书架象征知识库", "用于知识库、文库",
     ["知识库", "文库", "书架"], ["library", "kb", "books"]),

    ("encyclopedia", "百科", "Encyclopedia",
     lambda: [
         rect(4, 4, 16, 17, rx=0.6),
         rect(11, 4, 2, 17),
         rect(4, 4, 16, 1.2, rx=0.3),
         rect(11.5, 8, 1.0, 12),
         rect(7, 9, 3, 0.8, rx=0.3),
         rect(7, 11, 3, 0.8, rx=0.3),
         rect(14, 9, 3, 0.8, rx=0.3),
         rect(14, 11, 3, 0.8, rx=0.3),
     ],
     "厚书象征百科全书", "用于百科、规章手册",
     ["百科", "手册", "全书"], ["encyclopedia", "manual", "wiki"]),

    ("faq", "常见问答", "FAQ",
     lambda: [
         round_rect(3, 4, 18, 14, 1.0),
         rect(6, 7, 5, 1.4),
         rect(6, 11, 8, 1.4),
         rect(6, 14, 6, 1.4),
         rect(11, 18, 4, 4, rx=0.6),
         rect(2, 21, 20, 1, rx=0.3),
         path("M 18 7 L 18 11"),
         line(18, 7, 18, 11, w=0.8),
     ],
     "Q+A 列表象征常见问题", "用于FAQ、知识问答",
     ["FAQ", "问答", "常见问题"], ["faq", "qna", "questions"]),

    ("glossary", "术语表", "Glossary",
     lambda: [
         doc_outline(4, 2, 15, 20, 4)[0],
         rect(7, 7, 3, 1.0, rx=0.3),
         rect(11, 7, 5, 1.0, rx=0.3),
         rect(7, 10, 3, 1.0, rx=0.3),
         rect(11, 10, 5, 1.0, rx=0.3),
         rect(7, 13, 3, 1.0, rx=0.3),
         rect(11, 13, 5, 1.0, rx=0.3),
         rect(7, 16, 3, 1.0, rx=0.3),
         rect(11, 16, 5, 1.0, rx=0.3),
     ],
     "对照列表象征术语表", "用于术语表、对照",
     ["术语", "对照", "Glossary"], ["glossary", "terms"]),

    ("chapter", "章节", "Chapter",
     lambda: [
         doc_outline(4, 2, 15, 20, 4)[0],
         rect(7, 6, 8, 2.0, rx=0.3),
         rect(7, 10, 9, 1.0, rx=0.3),
         rect(7, 12, 9, 1.0, rx=0.3),
         rect(7, 16, 9, 1.0, rx=0.3),
         rect(7, 18, 9, 1.0, rx=0.3),
     ],
     "标题+段落象征章节", "用于章节、段落结构",
     ["章节", "标题", "段落"], ["chapter", "section", "paragraph"]),

    ("index_doc", "索引页", "IndexPage",
     lambda: [
         doc_outline(4, 2, 15, 20, 4)[0],
         rect(7, 7, 1.4, 1.4, rx=0.3),
         rect(10, 7, 6, 1.0, rx=0.3),
         rect(7, 10, 1.4, 1.4, rx=0.3),
         rect(10, 10, 6, 1.0, rx=0.3),
         rect(7, 13, 1.4, 1.4, rx=0.3),
         rect(10, 13, 6, 1.0, rx=0.3),
         rect(7, 16, 1.4, 1.4, rx=0.3),
         rect(10, 16, 6, 1.0, rx=0.3),
     ],
     "目录页象征索引", "用于目录、索引",
     ["索引", "目录", "Index"], ["index", "toc", "directory"]),

    ("quote_citation", "引用", "Citation",
     lambda: [
         path("M 4 6 L 9 6 L 9 13 Q 9 18 4 18 L 4 16 Q 7 16 7 13 L 4 13 Z"),
         path("M 14 6 L 19 6 L 19 13 Q 19 18 14 18 L 14 16 Q 17 16 17 13 L 14 13 Z"),
     ],
     "双引号象征引用", "用于引证、来源",
     ["引用", "引证", "Quote"], ["quote", "citation", "cite"]),
]



# ============================================================
# 09 FIELD — 现场管理巡检
# ============================================================

FIELD_BASES = [
    ("clipboard_check", "巡检清单", "ClipboardCheck",
     lambda: [
         round_rect(5, 4, 14, 18, 0.8),
         rect(8, 2.5, 8, 3, rx=0.6),
         line(8, 9, 10, 11, w=1.0),
         line(10, 11, 14, 7, w=1.0),
         line(8, 14, 10, 16, w=1.0),
         line(10, 16, 14, 12, w=1.0),
         rect(8, 19, 8, 1.0, rx=0.3),
     ],
     "清单+对勾象征巡检完成", "用于巡检表、点检",
     ["巡检", "点检", "清单"], ["check", "inspection", "checklist"]),

    ("safety_helmet", "安全帽", "SafetyHelmet",
     lambda: [
         path("M 3 18 Q 3 8 12 8 Q 21 8 21 18 Z"),
         rect(2, 18, 20, 1.4, rx=0.3),
         rect(11.4, 4, 1.2, 4),
         rect(10, 3, 4, 1.4, rx=0.3),
     ],
     "工程帽象征现场安全", "用于EHS、安全",
     ["安全帽", "现场", "EHS"], ["helmet", "safety", "site"]),

    ("location_pin", "位置点", "LocationPin",
     lambda: [
         path("M 12 2 C 7 2 4 6 4 11 C 4 17 12 22 12 22 C 12 22 20 17 20 11 C 20 6 17 2 12 2 Z"),
         circle(12, 10, 3.0),
     ],
     "地图针象征位置", "用于地图标点",
     ["位置", "定位", "标点"], ["pin", "location", "marker"]),

    ("map_glyph", "地图", "Map",
     lambda: [
         polygon([(2, 5), (9, 3), (15, 5), (22, 3), (22, 19), (15, 21), (9, 19), (2, 21)]),
         line(9, 3, 9, 19, w=0.6),
         line(15, 5, 15, 21, w=0.6),
     ],
     "折叠地图象征区域分布", "用于区域、地图",
     ["地图", "区域", "分布"], ["map", "region"]),

    ("route_marker", "路线标点", "RouteMarker",
     lambda: [
         circle(5, 7, 2.0),
         circle(19, 17, 2.0),
         path("M 5 7 Q 12 7 12 13 Q 12 17 19 17"),
         line(5, 7, 12, 7, w=0.7),
         line(12, 7, 12, 17, w=0.7),
         line(12, 17, 19, 17, w=0.7),
     ],
     "起点终点+路线", "用于巡检路线、走线",
     ["巡检路线", "走线", "Route"], ["route", "path"]),

    ("schedule_field", "排班", "Schedule",
     lambda: [
         round_rect(3, 5, 18, 16, 1.2),
         rect(3, 5, 18, 4),
         rect(7, 2.5, 1.6, 4, rx=0.5),
         rect(15.4, 2.5, 1.6, 4, rx=0.5),
         rect(6, 12, 4, 2.4, rx=0.3),
         rect(11, 12, 4, 2.4, rx=0.3),
         rect(16, 12, 3, 2.4, rx=0.3),
         rect(6, 16, 8, 2.4, rx=0.3),
     ],
     "日历+色块象征排班", "用于排班表",
     ["排班", "值班", "日程"], ["schedule", "shift", "roster"]),

    ("camera_inspect", "拍照取证", "CameraInspect",
     lambda: [
         round_rect(2, 7, 20, 13, 1.2),
         rect(8, 5, 8, 3, rx=0.5),
         circle(12, 13.5, 4),
         circle(12, 13.5, 2.0),
     ],
     "相机象征现场取证", "用于巡检拍照、取证",
     ["拍照", "取证", "相机"], ["camera", "photo", "snap"]),

    ("hand_scan", "扫码核验", "HandScan",
     lambda: [
         round_rect(3, 4, 18, 16, 1.0),
         rect(6, 7, 1.4, 10), rect(8, 7, 0.8, 10),
         rect(10, 7, 1.6, 10), rect(13, 7, 0.8, 10),
         rect(15, 7, 1.4, 10), rect(17, 7, 1.0, 10),
         rect(2, 11, 20, 1.4),
     ],
     "条码+扫描线象征扫码", "用于扫码核验",
     ["扫码", "条码", "核验"], ["scan", "barcode"]),

    ("walkie_talkie", "对讲机", "WalkieTalkie",
     lambda: [
         round_rect(7, 3, 10, 18, 1.2),
         rect(11, 1.5, 2, 2.5, rx=0.4),
         round_rect(8.5, 6, 7, 4, 0.4),
         circle(10, 13, 0.9),
         circle(12, 13, 0.9),
         circle(14, 13, 0.9),
         circle(10, 16, 0.9),
         circle(12, 16, 0.9),
         circle(14, 16, 0.9),
     ],
     "对讲机象征现场协同沟通", "用于现场对讲",
     ["对讲", "现场沟通", "协同"], ["walkie", "radio", "talk"]),

    ("vehicle_truck", "巡检车辆", "Truck",
     lambda: [
         path("M 2 9 L 14 9 L 14 17 L 2 17 Z"),
         path("M 14 11 L 19 11 L 22 14 L 22 17 L 14 17 Z"),
         circle(6, 18, 1.8),
         circle(18, 18, 1.8),
     ],
     "卡车象征出勤外勤", "用于车辆、外勤",
     ["车辆", "卡车", "外勤"], ["vehicle", "truck", "fleet"]),

    ("warehouse", "仓储", "Warehouse",
     lambda: [
         polygon([(3, 11), (12, 5), (21, 11), (21, 21), (3, 21)]),
         rect(8, 13, 8, 8, rx=0),
         rect(11, 13, 2, 8),
     ],
     "厂房+大门象征仓库", "用于仓储、库房",
     ["仓库", "仓储", "库房"], ["warehouse", "depot"]),

    ("barcode_field", "条码", "Barcode",
     lambda: [
         rect(3, 5, 1.5, 14), rect(5.5, 5, 0.7, 14),
         rect(7.5, 5, 1.0, 14), rect(9.5, 5, 1.4, 14),
         rect(12, 5, 0.6, 14), rect(13.5, 5, 1.6, 14),
         rect(16, 5, 0.7, 14), rect(17.5, 5, 1.6, 14),
         rect(20, 5, 0.7, 14),
     ],
     "条码象征唯一识别", "用于资产编号",
     ["条码", "唯一编号", "资产"], ["barcode", "uid", "asset"]),

    ("temperature", "温度计", "Thermometer",
     lambda: [
         path("M 11 4 Q 11 3 12 3 Q 13 3 13 4 L 13 14 Q 14.6 15 14.6 17 Q 14.6 20 12 20 Q 9.4 20 9.4 17 Q 9.4 15 11 14 Z"),
         circle(12, 17, 1.6),
         rect(11.4, 6, 1.2, 8),
     ],
     "温度计象征环境监测", "用于温度、环境",
     ["温度", "环境", "监测"], ["temperature", "thermo", "env"]),

    ("pressure_gauge", "压力表", "PressureGauge",
     lambda: [
         circle(12, 12, 8),
         circle(12, 12, 6.5),
         line(12, 12, 16, 9, w=1.4),
         circle(12, 12, 0.9),
         rect(11.4, 19.5, 1.2, 2.5),
         rect(8, 21, 8, 1.0, rx=0.3),
     ],
     "压力表象征机器监测", "用于设备、压力监控",
     ["压力", "表盘", "设备"], ["gauge", "pressure", "meter"]),
]


# ============================================================
# 10 ORG — 组织协同推进
# ============================================================

ORG_BASES = [
    ("team_three", "三人团队", "TeamThree",
     lambda: [
         circle(7, 7, 2.0),
         circle(17, 7, 2.0),
         circle(12, 6, 2.0),
         path("M 3 18 L 3 14 Q 3 12 7 12 Q 10 12 10 14"),
         path("M 14 18 L 14 14 Q 14 12 17 12 Q 21 12 21 14 L 21 18"),
         path("M 8 19 L 8 13 Q 8 11.5 12 11.5 Q 16 11.5 16 13 L 16 19 Z"),
         rect(2, 19, 20, 1, rx=0.3),
     ],
     "三个头像象征团队", "用于团队、小组",
     ["团队", "小组", "Team"], ["team", "group", "trio"]),

    ("hierarchy", "组织层级", "Hierarchy",
     lambda: [
         rect(9, 3, 6, 4, rx=0.4),
         rect(2, 13, 6, 4, rx=0.4),
         rect(9, 13, 6, 4, rx=0.4),
         rect(16, 13, 6, 4, rx=0.4),
         line(12, 7, 12, 10, w=0.8),
         line(5, 10, 19, 10, w=0.8),
         line(5, 10, 5, 13, w=0.8),
         line(12, 10, 12, 13, w=0.8),
         line(19, 10, 19, 13, w=0.8),
     ],
     "树状层级象征组织架构", "用于组织架构图",
     ["组织架构", "层级", "Org"], ["hierarchy", "org", "tree"]),

    ("network_org", "组织网络", "NetworkOrg",
     lambda: [
         circle(12, 5, 2.0),
         circle(5, 12, 2.0),
         circle(19, 12, 2.0),
         circle(8, 19, 2.0),
         circle(16, 19, 2.0),
         line(12, 5, 5, 12, w=0.7),
         line(12, 5, 19, 12, w=0.7),
         line(5, 12, 8, 19, w=0.7),
         line(19, 12, 16, 19, w=0.7),
         line(8, 19, 16, 19, w=0.7),
         line(5, 12, 19, 12, w=0.5),
     ],
     "节点+连线象征网络协同", "用于组织网络、矩阵",
     ["网络", "矩阵", "协同"], ["network", "graph", "matrix"]),

    ("handshake_partner", "合作", "Partnership",
     lambda: [
         path("M 2 10 L 7 8 L 10 11 L 12 9 L 14 11 L 17 8 L 22 10 L 22 14 L 17 16 L 12 14 L 7 16 L 2 14 Z"),
     ],
     "握手象征达成合作", "用于合作、伙伴",
     ["合作", "伙伴", "握手"], ["partner", "deal", "handshake"]),

    ("project_board", "项目看板", "ProjectBoard",
     lambda: [
         round_rect(2, 4, 20, 16, 0.8),
         rect(7, 4, 0.6, 16),
         rect(13, 4, 0.6, 16),
         rect(4, 7, 3, 2.4, rx=0.3),
         rect(4, 11, 3, 2.4, rx=0.3),
         rect(8.5, 7, 4, 2.4, rx=0.3),
         rect(15, 7, 5, 2.4, rx=0.3),
         rect(15, 11, 5, 2.4, rx=0.3),
     ],
     "三栏看板象征项目协同", "用于项目协同看板",
     ["项目看板", "协同", "项目"], ["project", "board", "kanban"]),

    ("meeting_table", "会议桌", "MeetingTable",
     lambda: [
         ellipse(12, 13, 9, 4),
         circle(4, 9, 1.6), circle(20, 9, 1.6),
         circle(4, 17, 1.6), circle(20, 17, 1.6),
         circle(12, 6, 1.6), circle(12, 20, 1.6),
     ],
     "圆桌+座位象征会议", "用于会议、协同",
     ["会议", "圆桌", "协同"], ["meeting", "round-table"]),

    ("role_badge", "角色标识", "RoleBadge",
     lambda: [
         circle(12, 9, 4),
         path("M 5 21 Q 5 14 12 14 Q 19 14 19 21 Z"),
         circle(17, 18, 3.0),
         path("M 15.6 18 L 16.6 19 L 18.4 17"),
         line(15.6, 18, 16.6, 19, w=0.8),
         line(16.6, 19, 18.4, 17, w=0.8),
     ],
     "人像+认证勾", "用于身份、角色",
     ["角色", "身份", "认证"], ["role", "identity"]),

    ("leader_star", "领导", "Leader",
     lambda: [
         circle(12, 7, 3.0),
         path("M 5 21 Q 5 13 12 13 Q 19 13 19 21 Z"),
         star(12, 4, 1.6, 0.5, points=5, rot=-90),
     ],
     "人像+星象征领导", "用于领导、负责人",
     ["领导", "负责人", "Leader"], ["leader", "boss", "owner"]),

    ("department", "部门", "Department",
     lambda: [
         rect(3, 12, 6, 9, rx=0.4),
         rect(10, 12, 4, 9, rx=0.4),
         rect(15, 12, 6, 9, rx=0.4),
         rect(2, 12, 20, 1.4),
         path("M 3 12 L 3 6 L 21 6 L 21 12"),
         rect(11, 8, 2, 4, rx=0.3),
     ],
     "建筑+多门象征部门划分", "用于部门、组织",
     ["部门", "组织", "Dept"], ["department", "dept"]),

    ("milestone_flag", "目标里程", "MilestoneFlag",
     flag_glyph,
     "旗帜象征里程目标", "用于阶段目标",
     ["里程", "旗帜", "目标"], ["flag", "milestone"]),

    ("standup_meeting", "每日站会", "Standup",
     lambda: [
         circle(6, 7, 1.8), circle(12, 7, 1.8), circle(18, 7, 1.8),
         path("M 3 18 L 3 11 Q 3 9 6 9 Q 9 9 9 11"),
         path("M 9 18 L 9 11 Q 9 9 12 9 Q 15 9 15 11"),
         path("M 15 18 L 15 11 Q 15 9 18 9 Q 21 9 21 11 L 21 18"),
         rect(2, 19, 20, 1.0, rx=0.3),
     ],
     "三人并排站立", "用于站会、晨会",
     ["站会", "晨会", "对齐"], ["standup", "daily"]),

    ("sync_meeting", "同步对齐", "SyncMeeting",
     lambda: [
         circle(7, 12, 4),
         circle(17, 12, 4),
         path("M 11 12 L 13 12"),
         line(11, 12, 13, 12, w=1.4),
         path("M 12 8 L 12 16"),
         line(12, 8, 12, 16, w=0.6),
     ],
     "两圆相交象征对齐", "用于对齐、共识",
     ["对齐", "同步", "共识"], ["sync", "align", "consensus"]),

    ("working_group", "工作组", "WorkingGroup",
     lambda: [
         circle(8, 9, 1.6), circle(16, 9, 1.6),
         circle(8, 16, 1.6), circle(16, 16, 1.6),
         line(8, 9, 16, 9, w=0.7),
         line(8, 16, 16, 16, w=0.7),
         line(8, 9, 8, 16, w=0.7),
         line(16, 9, 16, 16, w=0.7),
         line(8, 9, 16, 16, w=0.5),
         line(16, 9, 8, 16, w=0.5),
     ],
     "四人闭环象征专项组", "用于专项、Tiger Team",
     ["专项组", "工作组", "Tiger"], ["squad", "tiger", "task-force"]),

    ("alignment", "目标对齐", "Alignment",
     lambda: [
         arrow(2, 8, 22, 8, shaft_w=1.4, head_w=3.4, head_l=2.6),
         arrow(2, 12, 22, 12, shaft_w=1.4, head_w=3.4, head_l=2.6),
         arrow(2, 16, 22, 16, shaft_w=1.4, head_w=3.4, head_l=2.6),
     ],
     "三箭同向象征同向对齐", "用于战略对齐",
     ["对齐", "同向", "战略"], ["align", "strategy", "direction"]),
]


# ============================================================
# 11 ALERT — 问题预警诊断
# ============================================================

ALERT_BASES = [
    ("alert_bell_loud", "响铃预警", "AlertBell",
     bell_glyph,
     "铃铛+震动象征报警", "用于报警提醒",
     ["报警", "提醒", "铃铛"], ["alert", "alarm", "bell"]),

    ("warn_triangle", "警告三角", "WarnTriangle",
     lambda: [
         polygon([(12, 2.5), (22, 21), (2, 21)]),
         rect(11.2, 9, 1.6, 6, rx=0.5),
         circle(12, 17.5, 0.9),
     ],
     "三角!象征预警", "用于通用预警",
     ["预警", "警告", "三角"], ["warn", "warning", "alert"]),

    ("fault_lightning", "故障闪电", "FaultLightning",
     lambda: [
         polygon([(13, 2), (5, 13), (11, 13), (9, 22), (19, 10), (12, 10), (15, 2)]),
     ],
     "闪电象征突发故障", "用于宕机、突发故障",
     ["故障", "宕机", "闪电"], ["fault", "down", "outage"]),

    ("root_cause", "根因分析", "RootCause",
     lambda: [
         circle(12, 4, 2.4),
         line(12, 6, 12, 10, w=0.8),
         circle(7, 12, 1.8), circle(17, 12, 1.8),
         line(12, 10, 7, 12, w=0.8),
         line(12, 10, 17, 12, w=0.8),
         circle(4, 19, 1.8), circle(10, 19, 1.8),
         circle(14, 19, 1.8), circle(20, 19, 1.8),
         line(7, 14, 4, 19, w=0.6),
         line(7, 14, 10, 19, w=0.6),
         line(17, 14, 14, 19, w=0.6),
         line(17, 14, 20, 19, w=0.6),
     ],
     "树状分支象征根因下钻", "用于根因分析、5Why",
     ["根因", "下钻", "5Why"], ["root-cause", "rca", "5why"]),

    ("stethoscope", "诊断", "Stethoscope",
     lambda: [
         circle(18, 17, 3.0),
         circle(18, 17, 1.6),
         path("M 4 4 L 4 11 Q 4 17 9 17 Q 14 17 14 11 L 14 4"),
         line(4, 4, 4, 11, w=1.0),
         line(14, 4, 14, 11, w=1.0),
         path("M 4 11 Q 4 17 9 17 Q 14 17 14 11"),
         line(15, 14, 18, 14, w=0.8),
     ],
     "听诊器象征诊断", "用于系统体检、诊断",
     ["诊断", "体检", "听诊"], ["diagnose", "stethoscope", "health"]),

    ("error_bug", "缺陷", "Bug",
     lambda: [
         ellipse(12, 13, 5, 6),
         line(7, 9, 4, 6, w=0.9),
         line(17, 9, 20, 6, w=0.9),
         line(7, 13, 3, 13, w=0.9),
         line(17, 13, 21, 13, w=0.9),
         line(7, 17, 4, 20, w=0.9),
         line(17, 17, 20, 20, w=0.9),
         circle(10, 11, 0.7), circle(14, 11, 0.7),
         path("M 9 6 Q 12 3 15 6"),
     ],
     "甲虫象征缺陷", "用于Bug、缺陷",
     ["Bug", "缺陷", "故障"], ["bug", "defect", "issue"]),

    ("sla_breach", "SLA超时", "SlaBreach",
     lambda: [
         donut(10, 12, 7, 5.4),
         line(10, 12, 14, 8, w=1.4),
         line(10, 12, 10, 7, w=1.4),
         polygon([(18, 4), (22, 4), (22, 8), (18, 8)]),
         polygon([(18, 4), (22, 8)]),
         line(18, 4, 22, 8, w=1.0),
         line(18, 8, 22, 4, w=1.0),
     ],
     "时钟+X象征SLA违约", "用于超时、违约",
     ["SLA", "超时", "违约"], ["sla", "breach", "overdue"]),

    ("escalate", "升级", "Escalate",
     lambda: [
         arrow(12, 21, 12, 4, shaft_w=2.4, head_w=6.5, head_l=5.0),
         rect(2, 21, 20, 1.0, rx=0.3),
         star(12, 4, 1.4, 0.4, points=4, rot=-90),
     ],
     "向上箭头+sparkle", "用于工单升级",
     ["升级", "Escalate", "上报"], ["escalate", "raise"]),

    ("downtime", "宕机", "Downtime",
     lambda: [
         round_rect(2, 5, 20, 12, 1.0),
         rect(8, 17, 8, 1.4, rx=0.3),
         rect(10, 16, 4, 1.4),
         line(7, 8, 17, 14, w=1.4),
         line(7, 14, 17, 8, w=1.4),
     ],
     "屏幕+X象征服务宕机", "用于宕机、停机",
     ["宕机", "停机", "Down"], ["downtime", "outage", "down"]),

    ("severity_high", "高优级别", "Severity",
     lambda: [
         circle(12, 12, 9),
         polygon([(12, 4), (16, 11), (12, 14), (8, 11)]),
         rect(11.2, 16, 1.6, 4, rx=0.4),
     ],
     "圆+三角+!象征严重等级", "用于P0/P1故障",
     ["严重", "高优", "P0"], ["severity", "p0", "critical"]),

    ("queue_pile", "积压", "QueuePile",
     lambda: [
         rect(4, 16, 16, 4, rx=0.5),
         rect(4, 11, 16, 4, rx=0.5),
         rect(4, 6, 16, 4, rx=0.5),
         rect(4, 2, 12, 3, rx=0.4),
     ],
     "堆积层象征积压", "用于排队、积压",
     ["积压", "队列", "Pile"], ["queue", "backlog", "pile"]),

    ("x_block", "阻塞", "Block",
     lambda: [
         circle(12, 12, 9),
         rect(2, 11, 20, 2.0).__or__({"rx": 0}) if False else rect(2, 11, 20, 2),
         line(5, 5, 19, 19, w=2.4),
     ],
     "禁止符象征阻塞", "用于Blocker",
     ["阻塞", "禁止", "Blocker"], ["block", "blocker"]),

    ("abnormal_spike", "异常尖峰", "AbnormalSpike",
     lambda: [
         rect(2, 21, 20, 1.0, rx=0.3),
         rect(2, 3, 1, 19, rx=0.2),
         line(3, 17, 7, 16, w=1.0),
         line(7, 16, 9, 18, w=1.0),
         line(9, 18, 11, 5, w=1.0),
         line(11, 5, 13, 18, w=1.0),
         line(13, 18, 17, 17, w=1.0),
         line(17, 17, 21, 16, w=1.0),
     ],
     "尖峰曲线象征异常波动", "用于异常监测、突刺",
     ["异常", "尖峰", "突刺"], ["spike", "anomaly", "outlier"]),

    ("mttr_clock", "恢复时间", "Mttr",
     lambda: [
         clock_glyph()[0],
         clock_glyph()[1],
         clock_glyph()[2],
         circle(12, 12, 1.0),
         arrow(15, 14, 19, 19, shaft_w=1.0, head_w=2.4, head_l=2.0),
     ],
     "时钟+箭头象征恢复时间", "用于MTTR、恢复",
     ["恢复时间", "MTTR", "时长"], ["mttr", "recovery", "time"]),
]


# ============================================================
# 12 SHOW — 成果汇报展示
# ============================================================

SHOW_BASES = [
    ("trophy", "奖杯", "Trophy",
     lambda: [
         path("M 6 4 L 18 4 L 18 8 Q 18 13 12 13 Q 6 13 6 8 Z"),
         path("M 4 5 Q 1 5 1 8 Q 1 11 6 11"),
         path("M 20 5 Q 23 5 23 8 Q 23 11 18 11"),
         rect(10, 13, 4, 5, rx=0.3),
         rect(7, 18, 10, 2.0, rx=0.3),
     ],
     "奖杯象征成绩", "用于奖项、成果",
     ["奖杯", "奖项", "成果"], ["trophy", "award", "win"]),

    ("medal", "奖牌", "Medal",
     lambda: [
         path("M 6 2 L 9 2 L 12 9 L 9 9 Z"),
         path("M 18 2 L 15 2 L 12 9 L 15 9 Z"),
         circle(12, 16, 5.5),
         star(12, 16, 3.0, 1.0, points=5, rot=-90),
     ],
     "奖牌+绶带象征荣誉", "用于荣誉、表彰",
     ["奖牌", "荣誉", "表彰"], ["medal", "honor"]),

    ("podium_winner", "冠军领奖台", "PodiumWinner",
     lambda: [
         rect(9, 8, 6, 13, rx=0.3),
         rect(15, 12, 6, 9, rx=0.3),
         rect(3, 14, 6, 7, rx=0.3),
         rect(11.4, 5, 1.2, 3),
         polygon([(11, 1), (13, 1), (12.5, 4), (11.5, 4)]),
         rect(2, 21, 20, 1, rx=0.3),
     ],
     "三阶领奖台", "用于排名、表彰",
     ["领奖台", "排名", "冠军"], ["podium", "winner", "ranking"]),

    ("presentation_slide", "演示文稿", "Presentation",
     lambda: [
         round_rect(2, 4, 20, 13, 0.8),
         rect(2, 14, 20, 1, rx=0.2),
         rect(11, 17, 2, 4, rx=0.3),
         rect(8, 21, 8, 1.0, rx=0.3),
         rect(6, 11, 2, 4, rx=0.3),
         rect(10, 9, 2, 6, rx=0.3),
         rect(14, 7, 2, 8, rx=0.3),
     ],
     "投影屏+柱状", "用于演示PPT",
     ["演示", "PPT", "汇报"], ["slide", "ppt", "present"]),

    ("growth_milestone", "成果里程", "GrowthMilestone",
     lambda: [
         arrow(3, 19, 21, 6, shaft_w=2.4, head_w=6.5, head_l=5.5),
         star(20, 6, 2.6, 0.8, points=5, rot=-90),
         rect(2, 21, 20, 1, rx=0.3),
     ],
     "向上箭头+星象征成长成果", "用于增长里程",
     ["增长里程", "成果", "突破"], ["growth", "milestone", "win"]),

    ("before_after", "前后对比", "BeforeAfter",
     lambda: [
         rect(3, 6, 8, 12, rx=0.4),
         rect(13, 6, 8, 12, rx=0.4),
         arrow(11, 12, 13, 12, shaft_w=1.0, head_w=2.4, head_l=2.0),
         rect(5, 14, 4, 1.0, rx=0.3),
         rect(15, 9, 4, 1.0, rx=0.3),
         rect(15, 11, 4, 1.0, rx=0.3),
         rect(15, 13, 4, 1.0, rx=0.3),
     ],
     "两块对比+箭头", "用于改善前后对比",
     ["对比", "前后", "改善"], ["compare", "before-after"]),

    ("kpi_summary", "KPI汇总", "KpiSummary",
     lambda: [
         round_rect(2, 4, 20, 16, 0.8),
         rect(4, 7, 7, 5, rx=0.4),
         rect(13, 7, 7, 5, rx=0.4),
         rect(4, 14, 7, 5, rx=0.4),
         rect(13, 14, 7, 5, rx=0.4),
         circle(7, 9.5, 1.0), circle(16, 9.5, 1.0),
         circle(7, 16.5, 1.0), circle(16, 16.5, 1.0),
     ],
     "四宫格象征汇总报表", "用于KPI总览",
     ["KPI", "总览", "看板"], ["kpi", "overview", "summary"]),

    ("report_doc", "汇报报告", "ReportDoc",
     lambda: [
         doc_outline(4, 2, 15, 20, 4)[0],
         rect(7, 7, 9, 1.0, rx=0.3),
         rect(7, 9, 9, 1.0, rx=0.3),
         rect(7, 14, 2.0, 4, rx=0.3),
         rect(10, 13, 2.0, 5, rx=0.3),
         rect(13, 11, 2.0, 7, rx=0.3),
         rect(7, 18, 9, 0.6, rx=0.2),
     ],
     "文档+柱状象征数据汇报", "用于报告、汇报",
     ["报告", "汇报", "Report"], ["report", "doc"]),

    ("scoreboard", "成绩牌", "Scoreboard",
     lambda: [
         round_rect(2, 4, 20, 14, 0.8),
         rect(2, 7, 20, 1, rx=0.2),
         rect(4, 10, 6, 6, rx=0.4),
         rect(11, 10, 9, 2, rx=0.3),
         rect(11, 13, 9, 2, rx=0.3),
         rect(11, 16, 6, 1.0, rx=0.3),
         rect(8, 18, 8, 4, rx=0.3),
     ],
     "记分牌+底座象征成绩公示", "用于成绩公示",
     ["成绩牌", "公示", "Score"], ["scoreboard", "score"]),

    ("ribbon_award", "锦旗", "Ribbon",
     lambda: [
         circle(12, 9, 5.5),
         star(12, 9, 3.0, 1.0, points=5, rot=-90),
         polygon([(8, 13), (8, 22), (12, 19), (16, 22), (16, 13)]),
     ],
     "勋章+绶带象征锦旗", "用于表彰、嘉奖",
     ["锦旗", "嘉奖", "表彰"], ["ribbon", "honor"]),

    ("certificate_show", "证书荣誉", "CertificateShow",
     lambda: [
         round_rect(3, 4, 18, 14, 1.0),
         rect(5, 7, 14, 1.0, rx=0.3),
         rect(5, 9.5, 10, 1.0, rx=0.3),
         circle(17, 18, 2.6),
         polygon([(15.5, 19), (16.5, 22), (17.5, 21), (18.5, 22), (18.5, 19)]),
     ],
     "证书+绶带象征官方认证", "用于资质、证书",
     ["证书", "认证", "资质"], ["certificate", "diploma"]),

    ("announcement", "公告播报", "Announcement",
     lambda: [
         path("M 3 13 L 3 11 L 9 9 L 18 4 L 18 20 L 9 15 L 7 15 L 7 18 L 5 18 L 5 15 L 4 15 Q 3 15 3 13 Z"),
         path("M 19 9 Q 22 9 22 12 Q 22 15 19 15"),
     ],
     "扩音器象征公告", "用于公告、宣布",
     ["公告", "宣布", "Broadcast"], ["announce", "news"]),

    ("dashboard_summary", "汇总仪表", "DashboardSummary",
     lambda: gauge_glyph(),
     "仪表盘汇总指标", "用于综合仪表",
     ["仪表盘", "总览", "Dashboard"], ["dashboard", "summary"]),

    ("achievement_unlock", "成就解锁", "AchievementUnlock",
     lambda: [
         star(12, 12, 9, 4.0, points=8, rot=-90),
         circle(12, 12, 4.5),
         path("M 9.6 11.6 L 11 13 L 14.5 9.5"),
         line(9.6, 11.6, 11, 13, w=1.4),
         line(11, 13, 14.5, 9.5, w=1.4),
     ],
     "勋章+对勾象征成就解锁", "用于成就、徽章",
     ["成就", "解锁", "徽章"], ["achievement", "unlock"]),
]


# ============================================================
# Master registry: category code -> (chinese_name, base_list)
# ============================================================

CATEGORIES = [
    ("DATA",  "01_数据指标趋势",   DATA_BASES),
    ("TRAIN", "02_员工培训辅导",   TRAIN_BASES),
    ("CUST",  "03_客户沟通触达",   CUST_BASES),
    ("SALE",  "04_服销增长转化",   SALE_BASES),
    ("RISK",  "05_风险合规管控",   RISK_BASES),
    ("FLOW",  "06_流程机制闭环",   FLOW_BASES),
    ("AI",    "07_AI机器人自动化", AI_BASES),
    ("KNOW",  "08_知识库与文档",   KNOW_BASES),
    ("FIELD", "09_现场管理巡检",   FIELD_BASES),
    ("ORG",   "10_组织协同推进",   ORG_BASES),
    ("ALERT", "11_问题预警诊断",   ALERT_BASES),
    ("SHOW",  "12_成果汇报展示",   SHOW_BASES),
]


# Per-category list of badges most semantically relevant
CATEGORY_BADGES = {
    "DATA":  ["check", "warn", "up", "down", "eye", "clock", "smart"],
    "TRAIN": ["check", "plus", "star", "person", "smart", "clock"],
    "CUST":  ["check", "plus", "person", "heart", "clock", "sync"],
    "SALE":  ["check", "plus", "up", "down", "star", "heart"],
    "RISK":  ["warn", "lock", "eye", "check", "cross", "gear"],
    "FLOW":  ["check", "sync", "plus", "gear", "clock", "cross"],
    "AI":    ["smart", "gear", "sync", "check", "eye", "plus"],
    "KNOW":  ["plus", "check", "lock", "eye", "star", "sync"],
    "FIELD": ["check", "warn", "eye", "clock", "lock", "plus"],
    "ORG":   ["person", "check", "plus", "star", "heart", "sync"],
    "ALERT": ["warn", "cross", "eye", "clock", "sync", "lock"],
    "SHOW":  ["star", "check", "up", "heart", "person", "plus"],
}
