#!/bin/bash
# 更新小红书技能搜索任务

source /Users/mocklab/.openclaw/workspace/scripts/bitable_updater.sh

# 获取token
TOKEN=$(get_token)
if [ $? -ne 0 ]; then
    echo "获取token失败"
    exit 1
fi

# 添加小红书技能搜索任务
add_task_record "$TOKEN" \
    "TASK-20260301-233530" \
    "搜索和安装小红书图文自动维护技能" \
    "根据需求搜索小红书自动维护图文的相关技能，找到10+个相关技能，成功安装2个核心技能，创建完整实施方案" \
    "进行中" \
    "技能搜索" \
    "✅ 搜索到10个小红书相关技能\n✅ 搜索到4个通用社交媒体技能\n✅ 成功安装: xiaohongshu-title (小红书标题生成)\n✅ 成功安装: social-media-scheduler (社交媒体排期)\n✅ 创建完整实施方案文档\n✅ 分析现有可用技能组合\n✅ 制定三阶段实施计划\n📋 下一步: 验证安装技能功能，继续安装其他核心技能"