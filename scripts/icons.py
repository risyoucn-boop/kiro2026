"""精选 100 个 Material Symbols 图标,按 8 大业务场景分组。

每条记录: (group, name_zh, iconify_id)
iconify_id 形如 'material-symbols:home-rounded'
"""

ICONS = [
    # 1. 导航与界面 (15)
    ("导航与界面", "首页",       "material-symbols:home-rounded"),
    ("导航与界面", "菜单",       "material-symbols:menu-rounded"),
    ("导航与界面", "返回",       "material-symbols:arrow-back-rounded"),
    ("导航与界面", "前进",       "material-symbols:arrow-forward-rounded"),
    ("导航与界面", "更多",       "material-symbols:more-horiz"),
    ("导航与界面", "搜索",       "material-symbols:search-rounded"),
    ("导航与界面", "筛选",       "material-symbols:filter-alt"),
    ("导航与界面", "设置",       "material-symbols:settings-rounded"),
    ("导航与界面", "关闭",       "material-symbols:close-rounded"),
    ("导航与界面", "全屏",       "material-symbols:fullscreen-rounded"),
    ("导航与界面", "刷新",       "material-symbols:refresh-rounded"),
    ("导航与界面", "排序",       "material-symbols:sort-rounded"),
    ("导航与界面", "网格视图",   "material-symbols:grid-view-rounded"),
    ("导航与界面", "列表视图",   "material-symbols:list-rounded"),
    ("导航与界面", "信息",       "material-symbols:info-rounded"),

    # 2. 用户与账户 (12)
    ("用户与账户", "用户",       "material-symbols:person-rounded"),
    ("用户与账户", "用户组",     "material-symbols:group-rounded"),
    ("用户与账户", "添加用户",   "material-symbols:person-add-rounded"),
    ("用户与账户", "登录",       "material-symbols:login-rounded"),
    ("用户与账户", "登出",       "material-symbols:logout-rounded"),
    ("用户与账户", "权限",       "material-symbols:admin-panel-settings-rounded"),
    ("用户与账户", "锁定",       "material-symbols:lock"),
    ("用户与账户", "解锁",       "material-symbols:lock-open-rounded"),
    ("用户与账户", "密码",       "material-symbols:key-rounded"),
    ("用户与账户", "指纹",       "material-symbols:fingerprint"),
    ("用户与账户", "徽章",       "material-symbols:badge-rounded"),
    ("用户与账户", "证书",       "material-symbols:verified-rounded"),

    # 3. 数据与报表 (15)
    ("数据与报表", "柱状图",     "material-symbols:bar-chart-rounded"),
    ("数据与报表", "折线图",     "material-symbols:show-chart-rounded"),
    ("数据与报表", "饼图",       "material-symbols:pie-chart"),
    ("数据与报表", "面积图",     "material-symbols:area-chart-rounded"),
    ("数据与报表", "数据表",     "material-symbols:table-chart"),
    ("数据与报表", "趋势上升",   "material-symbols:trending-up-rounded"),
    ("数据与报表", "趋势下降",   "material-symbols:trending-down-rounded"),
    ("数据与报表", "看板",       "material-symbols:dashboard-rounded"),
    ("数据与报表", "数据库",     "material-symbols:database"),
    ("数据与报表", "存储",       "material-symbols:storage-rounded"),
    ("数据与报表", "备份",       "material-symbols:backup-rounded"),
    ("数据与报表", "导出",       "material-symbols:download-rounded"),
    ("数据与报表", "导入",       "material-symbols:upload-rounded"),
    ("数据与报表", "聚合",       "material-symbols:functions-rounded"),
    ("数据与报表", "查询",       "material-symbols:query-stats-rounded"),

    # 4. 通信与协作 (12)
    ("通信与协作", "邮件",       "material-symbols:mail-rounded"),
    ("通信与协作", "通知",       "material-symbols:notifications-rounded"),
    ("通信与协作", "聊天",       "material-symbols:chat-rounded"),
    ("通信与协作", "评论",       "material-symbols:comment-rounded"),
    ("通信与协作", "电话",       "material-symbols:call"),
    ("通信与协作", "视频会议",   "material-symbols:videocam-rounded"),
    ("通信与协作", "麦克风",     "material-symbols:mic-rounded"),
    ("通信与协作", "分享",       "material-symbols:share"),
    ("通信与协作", "发送",       "material-symbols:send-rounded"),
    ("通信与协作", "@提及",      "material-symbols:alternate-email-rounded"),
    ("通信与协作", "翻译",       "material-symbols:translate-rounded"),
    ("通信与协作", "公告",       "material-symbols:campaign-rounded"),

    # 5. 文件与文档 (12)
    ("文件与文档", "文档",       "material-symbols:description-rounded"),
    ("文件与文档", "文件夹",     "material-symbols:folder-rounded"),
    ("文件与文档", "PDF",        "material-symbols:picture-as-pdf-rounded"),
    ("文件与文档", "图片",       "material-symbols:image-rounded"),
    ("文件与文档", "附件",       "material-symbols:attach-file-rounded"),
    ("文件与文档", "复制",       "material-symbols:content-copy-rounded"),
    ("文件与文档", "粘贴",       "material-symbols:content-paste-rounded"),
    ("文件与文档", "新建",       "material-symbols:note-add-rounded"),
    ("文件与文档", "编辑",       "material-symbols:edit-rounded"),
    ("文件与文档", "删除",       "material-symbols:delete-rounded"),
    ("文件与文档", "打印",       "material-symbols:print-rounded"),
    ("文件与文档", "签名",       "material-symbols:draw-rounded"),

    # 6. 状态与反馈 (12)
    ("状态与反馈", "成功",       "material-symbols:check-circle-rounded"),
    ("状态与反馈", "失败",       "material-symbols:cancel-rounded"),
    ("状态与反馈", "警告",       "material-symbols:warning-rounded"),
    ("状态与反馈", "错误",       "material-symbols:error-rounded"),
    ("状态与反馈", "帮助",       "material-symbols:help-rounded"),
    ("状态与反馈", "进行中",     "material-symbols:hourglass-top-rounded"),
    ("状态与反馈", "已完成",     "material-symbols:task-alt-rounded"),
    ("状态与反馈", "待办",       "material-symbols:pending-actions-rounded"),
    ("状态与反馈", "暂停",       "material-symbols:pause-circle-rounded"),
    ("状态与反馈", "进度",       "material-symbols:progress-activity"),
    ("状态与反馈", "同步",       "material-symbols:sync-rounded"),
    ("状态与反馈", "断开",       "material-symbols:link-off-rounded"),

    # 7. 商务与交易 (12)
    ("商务与交易", "购物车",     "material-symbols:shopping-cart-rounded"),
    ("商务与交易", "订单",       "material-symbols:receipt-long-rounded"),
    ("商务与交易", "钱包",       "material-symbols:account-balance-wallet-rounded"),
    ("商务与交易", "信用卡",     "material-symbols:credit-card-rounded"),
    ("商务与交易", "支付",       "material-symbols:payments-rounded"),
    ("商务与交易", "发票",       "material-symbols:request-quote-rounded"),
    ("商务与交易", "合同",       "material-symbols:contract-rounded"),
    ("商务与交易", "公司",       "material-symbols:domain-rounded"),
    ("商务与交易", "工作",       "material-symbols:work-rounded"),
    ("商务与交易", "日历",       "material-symbols:calendar-month-rounded"),
    ("商务与交易", "时钟",       "material-symbols:schedule-rounded"),
    ("商务与交易", "目标",       "material-symbols:flag-rounded"),

    # 8. 系统与运维 (10)
    ("系统与运维", "云",         "material-symbols:cloud-rounded"),
    ("系统与运维", "服务器",     "material-symbols:dns-rounded"),
    ("系统与运维", "API",        "material-symbols:api-rounded"),
    ("系统与运维", "终端",       "material-symbols:terminal-rounded"),
    ("系统与运维", "代码",       "material-symbols:code-rounded"),
    ("系统与运维", "Bug",        "material-symbols:bug-report-rounded"),
    ("系统与运维", "构建",       "material-symbols:build-rounded"),
    ("系统与运维", "部署",       "material-symbols:rocket-launch-rounded"),
    ("系统与运维", "监控",       "material-symbols:monitor-heart-rounded"),
    ("系统与运维", "日志",       "material-symbols:article-rounded"),
]

# 三色方案
COLORS = {
    "深蓝灰": "#2C3E50",  # 主用色
    "品牌橙": "#E67E22",  # 强调色
    "警示红": "#C0392B",  # 警示色
}

if __name__ == "__main__":
    from collections import Counter
    print(f"总数: {len(ICONS)}")
    print("分组分布:")
    for g, c in Counter(i[0] for i in ICONS).items():
        print(f"  {g}: {c}")
    assert len(ICONS) == 100, "图标必须恰好 100 个"
    # 编号唯一性检查
    ids = [i[2] for i in ICONS]
    assert len(set(ids)) == 100, "图标 ID 必须唯一"
    print("OK 100 个图标、ID 唯一")
