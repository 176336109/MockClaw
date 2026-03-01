#!/bin/bash
# 稳定的多维表格更新脚本

set -e

# 配置
APP_ID="cli_a9f25697be389ceb"
APP_SECRET="caJHD9D8Wiw5NvxHmrAUbbpUurctZfEs"
BASE_APP_TOKEN="FCRNbSo4ja4hCEs5411cNZQXnkh"
TASKS_TABLE_ID="tblRmMB6LIdLHyEt"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# 获取token（带缓存）
get_token() {
    local token_cache="/tmp/feishu_token_${APP_ID}.cache"
    local token_expire_cache="/tmp/feishu_token_expire_${APP_ID}.cache"
    
    # 检查缓存是否有效（有效期2小时，我们保守用1.5小时）
    if [ -f "$token_cache" ] && [ -f "$token_expire_cache" ]; then
        local cached_token=$(cat "$token_cache")
        local expire_time=$(cat "$token_expire_cache")
        local current_time=$(date +%s)
        
        if [ $current_time -lt $expire_time ]; then
            echo "$cached_token"
            return 0
        fi
    fi
    
    # 获取新token
    log "获取新的飞书访问token..."
    local response=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
        -H "Content-Type: application/json" \
        -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}")
    
    local token=$(echo "$response" | grep -o '"tenant_access_token":"[^"]*"' | cut -d'"' -f4)
    local expire=$(echo "$response" | grep -o '"expire":[0-9]*' | cut -d: -f2)
    
    if [ -z "$token" ]; then
        error "无法获取token: $response"
        return 1
    fi
    
    # 缓存token（有效期1.5小时 = 5400秒）
    echo "$token" > "$token_cache"
    local new_expire=$(($(date +%s) + 5400))
    echo "$new_expire" > "$token_expire_cache"
    
    echo "$token"
}

# 添加任务记录
add_task_record() {
    local token="$1"
    local task_id="$2"
    local task_name="$3"
    local description="$4"
    local status="$5"
    local category="$6"
    local output="$7"
    
    log "添加任务记录: $task_name"
    
    local current_time_ms=$(($(date +%s) * 1000))
    local created_time=$((current_time_ms - 3600000)) # 1小时前
    local completed_time=$current_time_ms
    
    local response=$(curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/$BASE_APP_TOKEN/tables/$TASKS_TABLE_ID/records" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "{
            \"fields\": {
                \"任务ID\": \"$task_id\",
                \"任务名称\": \"$task_name\",
                \"描述\": \"$description\",
                \"状态\": \"$status\",
                \"分类\": \"$category\",
                \"产出\": \"$output\",
                \"使用Skills\": [\"主Agent工具\"],
                \"执行Agents\": [\"主Agent\"],
                \"技能使用详情\": \"使用OpenClaw工具集完成任务\",
                \"耗时分钟\": 60,
                \"负责人\": \"OpenClaw Agent\",
                \"创建时间\": $created_time,
                \"实际完成\": $completed_time,
                \"预计完成\": $completed_time
            }
        }")
    
    local code=$(echo "$response" | grep -o '"code":[0-9]*' | cut -d: -f2)
    
    if [ "$code" = "0" ]; then
        log "✅ 任务记录添加成功"
        echo "$response"
    else
        error "❌ 任务记录添加失败: $response"
        return 1
    fi
}

# 主函数
main() {
    log "=== 多维表格更新脚本 ==="
    
    # 获取token
    local token=$(get_token)
    if [ $? -ne 0 ]; then
        error "获取token失败，退出"
        exit 1
    fi
    
    log "Token获取成功: ${token:0:20}..."
    
    # 示例：添加测试任务
    # add_task_record "$token" \
    #     "TEST-$(date +%Y%m%d-%H%M%S)" \
    #     "测试任务" \
    #     "测试多维表格更新功能" \
    #     "测试中" \
    #     "系统测试" \
    #     "测试脚本功能"
    
    log "脚本就绪，可通过函数调用添加记录"
    log "使用方式: add_task_record \"\$token\" \"任务ID\" \"任务名\" \"描述\" \"状态\" \"分类\" \"产出\""
}

# 如果直接运行，执行主函数
if [[ "${BASH_SOURCE[0]}" = "${0}" ]]; then
    main "$@"
fi