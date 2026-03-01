#!/bin/bash
# 全面功能测试

echo "=== 博查AI技能全面测试 ==="
echo "测试时间: $(date)"
echo ""

# 加载配置
source .env
echo "📁 配置加载:"
echo "  API Key: ${BOCHA_API_KEY:0:10}..."
echo "  Debug模式: $BOCHA_DEBUG"
echo "  Timeout: $BOCHA_REQUEST_TIMEOUT"
echo ""

# 测试1：基本搜索
echo "🔍 测试1：基本搜索"
test_basic() {
    local query="人工智能最新发展"
    echo "  查询: $query"
    RESPONSE=$(curl -s -X POST "https://api.bocha.cn/v1/web-search" \
      -H "Authorization: Bearer $BOCHA_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"$query\", \"count\": 2}")
    
    if echo "$RESPONSE" | grep -q '"code":200'; then
        echo "  ✅ 成功"
        LOG_ID=$(echo "$RESPONSE" | grep -o '"log_id":"[^"]*"' | cut -d'"' -f4)
        echo "  日志ID: $LOG_ID"
    else
        echo "  ❌ 失败"
    fi
}
test_basic
echo ""

# 测试2：带参数搜索
echo "🔧 测试2：带参数搜索"
test_params() {
    local query="Python教程"
    echo "  查询: $query (count=3, summary=true)"
    RESPONSE=$(curl -s -X POST "https://api.bocha.cn/v1/web-search" \
      -H "Authorization: Bearer $BOCHA_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"$query\", \"count\": 3, \"summary\": true}")
    
    if echo "$RESPONSE" | grep -q '"code":200'; then
        echo "  ✅ 成功"
        LOG_ID=$(echo "$RESPONSE" | grep -o '"log_id":"[^"]*"' | cut -d'"' -f4)
        echo "  日志ID: $LOG_ID"
    else
        echo "  ❌ 失败"
    fi
}
test_params
echo ""

# 测试3：时间过滤
echo "⏰ 测试3：时间过滤搜索"
test_freshness() {
    local query="今日新闻"
    echo "  查询: $query (freshness=oneDay)"
    RESPONSE=$(curl -s -X POST "https://api.bocha.cn/v1/web-search" \
      -H "Authorization: Bearer $BOCHA_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{\"query\": \"$query\", \"count\": 1, \"freshness\": \"oneDay\"}")
    
    if echo "$RESPONSE" | grep -q '"code":200'; then
        echo "  ✅ 成功"
        LOG_ID=$(echo "$RESPONSE" | grep -o '"log_id":"[^"]*"' | cut -d'"' -f4)
        echo "  日志ID: $LOG_ID"
    else
        echo "  ❌ 失败"
    fi
}
test_freshness
echo ""

echo "📊 测试总结："
echo "1. 所有API调用已完成"
echo "2. 请登录博查AI控制台查看扣费情况"
echo "3. 日志ID已记录，可用于查询具体调用"
echo ""
echo "控制台地址: https://open.bocha.cn"
echo "=== 测试完成 ==="
