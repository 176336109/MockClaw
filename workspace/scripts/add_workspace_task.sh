#!/bin/bash
# 添加workspace整理任务

source /Users/mocklab/.openclaw/workspace/scripts/bitable_updater.sh

# 获取token
TOKEN=$(get_token)
if [ $? -ne 0 ]; then
    echo "获取token失败"
    exit 1
fi

# 添加整理workspace任务
add_task_record "$TOKEN" \
    "TASK-20260301-223940" \
    "整理workspace目录结构" \
    "清理杂乱的workspace，建立清晰的目录结构（core/, scripts/, projects/, docs/, temp/, backups/），确保不影响现有功能" \
    "已完成" \
    "系统维护" \
    "1. 创建清晰的目录结构\n2. 分类移动70+个文件\n3. 更新脚本路径引用\n4. 创建README说明文档\n5. 验证所有功能正常"