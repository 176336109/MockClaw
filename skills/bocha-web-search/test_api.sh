#!/bin/bash
# 测试API调用和.env配置

echo "=== 博查AI技能测试 ==="

# 1. 加载.env文件
echo "1. 加载.env文件..."
if [ -f .env ]; then
    source .env
    echo "   ✅ .env文件加载成功"
    echo "   BOCHA_API_KEY: ${BOCHA_API_KEY:0:10}..."
else
    echo "   ❌ .env文件不存在"
    exit 1
fi

# 2. 测试API调用
echo "2. 测试API调用..."
QUERY="测试.env配置和扣费验证"
RESPONSE=$(curl -s -X POST "https://api.bocha.cn/v1/web-search" \
  -H "Authorization: Bearer $BOCHA_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"$QUERY\", \"count\": 1}")

# 3. 解析响应
echo "3. 解析API响应..."
if echo "$RESPONSE" | grep -q '"code":200'; then
    echo "   ✅ API调用成功！"
    # 提取日志ID用于扣费验证
    LOG_ID=$(echo "$RESPONSE" | grep -o '"log_id":"[^"]*"' | cut -d'"' -f4)
    echo "   日志ID: $LOG_ID"
    echo "   查询: $QUERY"
    
    # 提取结果信息
    TITLE=$(echo "$RESPONSE" | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)
    if [ -n "$TITLE" ]; then
        echo "   第一个结果: $TITLE"
    fi
    
    echo ""
    echo "📊 扣费验证说明："
    echo "1. 登录博查AI控制台: https://open.bocha.cn"
    echo "2. 查看API调用记录"
    echo "3. 搜索日志ID: $LOG_ID"
    echo "4. 确认是否产生费用"
    
else
    echo "   ❌ API调用失败"
    echo "   响应: $RESPONSE"
fi

echo ""
echo "=== 测试完成 ==="
