#!/bin/bash
# 更新技能状态到多维表格

source /Users/mocklab/.openclaw/workspace/scripts/bitable_updater.sh

# 获取token
TOKEN=$(get_token)
if [ $? -ne 0 ]; then
    echo "获取token失败"
    exit 1
fi

# 添加技能验证任务
add_task_record "$TOKEN" \
    "TASK-20260301-231630" \
    "Skill状态全面检查和验证" \
    "检查所有OpenClaw Skill的可用状态，验证关键技能功能，创建状态报告" \
    "进行中" \
    "系统维护" \
    "1. 检查61个Skill的可用状态\n2. 验证bocha-web-search技能完全可用\n3. 发现CLI工具缺失问题\n4. 创建SKILL_STATUS_REPORT.md\n5. 飞书工具组验证可用\n6. 8个技能已封装\n7. 需要安装gh、weather等CLI工具"