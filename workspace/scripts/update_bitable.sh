#!/bin/bash
# 更新飞书多维表格脚本

echo "=== 更新多维表格 ==="

# 1. 获取token
echo "1. 获取访问token..."
TOKEN_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "cli_a9f25697be389ceb",
    "app_secret": "caJHD9D8Wiw5NvxHmrAUbbpUurctZfEs"
  }')

echo "Token响应: $TOKEN_RESPONSE"

TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"tenant_access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ 无法获取token"
    exit 1
fi

echo "✅ Token获取成功: ${TOKEN:0:20}..."

# 2. 尝试不同字段名组合
echo -e "\n2. 尝试添加记录..."

# 尝试1：使用记忆中的字段名
echo "尝试1：使用记忆字段名..."
RESPONSE1=$(curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/FCRNbSo4ja4hCEs5411cNZQXnkh/tables/tblRmMB6LIdLHyEt/records" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "技能名称": "bocha-web-search",
      "可用情况": "可用",
      "描述": "博查AI Web Search API技能",
      "配置信息": "API Key已配置",
      "测试结果": "3次测试成功",
      "问题记录": "环境变量需要.env",
      "解决方案": "已创建.env文件",
      "更新时间": "2026-03-01"
    }
  }')

echo "响应1: $RESPONSE1"

# 尝试2：使用简单字段名
echo -e "\n尝试2：使用简单字段名..."
RESPONSE2=$(curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/FCRNbSo4ja4hCEs5411cNZQXnkh/tables/tblRmMB6LIdLHyEt/records" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "名称": "bocha-web-search",
      "状态": "可用",
      "描述": "博查AI搜索技能",
      "配置": "API Key已配置",
      "测试": "3次测试成功",
      "问题": "环境变量需要.env",
      "解决": "已创建.env文件",
      "时间": "2026-03-01"
    }
  }')

echo "响应2: $RESPONSE2"

# 尝试3：最少字段
echo -e "\n尝试3：最少字段..."
RESPONSE3=$(curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/FCRNbSo4ja4hCEs5411cNZQXnkh/tables/tblRmMB6LIdLHyEt/records" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "名称": "bocha-web-search",
      "状态": "可用",
      "描述": "博查AI搜索技能"
    }
  }')

echo "响应3: $RESPONSE3"

echo -e "\n=== 完成 ==="
echo "如果所有尝试都失败，可能是："
echo "1. Token过期（有效期约2小时）"
echo "2. 字段名不正确"
echo "3. 需要先查看表格实际结构"