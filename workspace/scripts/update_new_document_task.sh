#!/bin/bash
# 更新新文档创建任务

source /Users/mocklab/.openclaw/workspace/scripts/bitable_updater.sh

# 获取token
TOKEN=$(get_token)
if [ $? -ne 0 ]; then
    echo "获取token失败"
    exit 1
fi

# 添加新文档创建任务
add_task_record "$TOKEN" \
    "TASK-20260301-235900" \
    "重新创建完整的小红书Agent团队方案飞书文档" \
    "由于原文档为空，重新创建了完整的方案文档，包含所有核心内容：团队架构、技能状态、实施路线、风险控制、成功指标和今日成果" \
    "已完成" \
    "文档修复" \
    "📄 新飞书文档创建成功:\n  - 文档ID: BSbldyWbqoAOANxChPpcBBX8nB7\n  - 文档链接: https://feishu.cn/docx/BSbldyWbqoAOANxChPpcBBX8nB7\n  - 文档标题: 小红书Agent团队完整方案\n\n📋 文档包含完整内容:\n  ✅ 16个Agent的团队架构 (4个层级)\n  ✅ 12个已安装技能状态\n  ✅ 6个待安装技能清单\n  ✅ 四阶段实施路线图\n  ✅ 风险分析和缓解措施\n  ✅ 成功指标和资源需求\n  ✅ 今日工作成果总结\n  ✅ 审核决策点清单\n  ✅ 下一步行动计划\n\n🔍 重点内容:\n  - 找到10个小红书相关技能\n  - 找到4个通用社交媒体技能\n  - workspace整理完成\n  - 多维表格系统建立\n  - 关键技能已验证\n\n🎯 审核要点:\n  1. 团队架构是否合理\n  2. 技能选择是否恰当\n  3. 实施路线是否可行\n  4. 风险控制是否充分\n\n⚠️ 注意事项:\n  - 原文档FNvjdQ8OsoSI5hx9RKJcowxxnDe为空\n  - 新文档BSbldyWbqoAOANxChPpcBBX8nB7包含完整内容\n  - 所有内容在此文档中，无需查看其他文件"