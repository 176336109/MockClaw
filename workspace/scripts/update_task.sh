#!/bin/bash
# 标准化任务更新脚本

source /Users/mocklab/.openclaw/workspace/scripts/bitable_updater.sh

# 生成任务ID
TASK_ID="TASK-$(date +%Y%m%d-%H%M%S)"

# 获取token
TOKEN=$(get_token)
if [ $? -ne 0 ]; then
    echo "获取token失败"
    exit 1
fi

# 添加任务记录
add_task_record "$TOKEN" \
    "$TASK_ID" \
    "系统优化：建立多维表格自动更新机制" \
    "基于方案B选择，建立稳定的多维表格直接更新系统，解决token管理、字段匹配、错误处理问题" \
    "进行中" \
    "系统开发" \
    "1. 创建稳定的token缓存机制\n2. 建立标准化更新脚本\n3. 添加错误处理和重试逻辑\n4. 集成到工作流程中"