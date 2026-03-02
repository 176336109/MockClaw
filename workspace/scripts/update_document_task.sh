#!/bin/bash
# 更新文档创建任务

source /Users/mocklab/.openclaw/workspace/scripts/bitable_updater.sh

# 获取token
TOKEN=$(get_token)
if [ $? -ne 0 ]; then
    echo "获取token失败"
    exit 1
fi

# 添加文档创建任务
add_task_record "$TOKEN" \
    "TASK-20260301-235100" \
    "创建小红书Agent团队方案飞书文档" \
    "根据审核要求，将完整的16个Agent团队方案创建为飞书文档，包含详细架构、技能状态、实施路线图和风险控制" \
    "已完成" \
    "文档创建" \
    "📄 飞书文档创建成功:\n  - 文档ID: FNvjdQ8OsoSI5hx9RKJcowxxnDe\n  - 文档链接: https://feishu.cn/docx/FNvjdQ8OsoSI5hx9RKJcowxxnDe\n  - 文档标题: 全自动小红书Agent团队建设方案\n\n📋 文档内容包含:\n  ✅ 16个Agent的完整团队架构\n  ✅ 12个已安装技能状态\n  ✅ 6个待安装技能清单\n  ✅ 四阶段实施路线图\n  ✅ 风险分析和缓解措施\n  ✅ 成功指标和资源需求\n  ✅ 下一步行动建议\n\n🎯 审核要点:\n  1. 团队架构是否合理\n  2. 技能选择是否恰当\n  3. 实施路线是否可行\n  4. 风险控制是否充分\n\n🔗 关联任务:\n  - TASK-20260301-234800: 团队建设主任务\n  - 所有进展实时同步到多维表格"