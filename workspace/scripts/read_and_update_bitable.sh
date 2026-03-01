#!/bin/bash
# 读取并更新多维表格

echo "=== 读取并更新多维表格 ==="

# 1. 获取token
echo "1. 获取访问token..."
TOKEN_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "cli_a9f25697be389ceb",
    "app_secret": "caJHD9D8Wiw5NvxHmrAUbbpUurctZfEs"
  }')

TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"tenant_access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ 无法获取token"
    exit 1
fi

echo "✅ Token: ${TOKEN:0:20}..."

# 2. 读取表格记录
echo -e "\n2. 读取表格现有记录..."
READ_RESPONSE=$(curl -s -X GET "https://open.feishu.cn/open-apis/bitable/v1/apps/FCRNbSo4ja4hCEs5411cNZQXnkh/tables/tblRmMB6LIdLHyEt/records?page_size=5" \
  -H "Authorization: Bearer $TOKEN")

echo "读取响应:"
echo "$READ_RESPONSE" | head -c 600
echo ""

# 3. 从响应中提取字段名
echo -e "\n3. 分析字段结构..."
if echo "$READ_RESPONSE" | grep -q '"code":0'; then
    # 提取第一个记录的字段
    FIELDS_JSON=$(echo "$READ_RESPONSE" | grep -o '"fields":{[^}]*}' | head -1)
    if [ -n "$FIELDS_JSON" ]; then
        echo "找到字段: $FIELDS_JSON"
        
        # 提取字段名
        echo -e "\n字段名列表:"
        echo "$FIELDS_JSON" | grep -o '"\([^"]*\)":"[^"]*"' | cut -d'"' -f2 | sort -u
    else
        echo "无法解析字段"
        # 尝试直接查看数据
        echo "$READ_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if data.get('code') == 0 and 'data' in data and 'items' in data['data']:
        print('表格记录:')
        for item in data['data']['items']:
            print(f'记录: {item.get(\"record_id\", \"未知\")}')
            fields = item.get('fields', {})
            for key, value in fields.items():
                print(f'  {key}: {value}')
except:
    print('解析失败')
" 2>/dev/null || echo "需要Python解析"
    fi
else
    echo "❌ 读取失败: $READ_RESPONSE"
fi

# 4. 基于读取的字段名尝试添加记录
echo -e "\n4. 尝试添加bocha技能记录..."

# 使用从表格中看到的字段名
ADD_RESPONSE=$(curl -s -X POST "https://open.feishu.cn/open-apis/bitable/v1/apps/FCRNbSo4ja4hCEs5411cNZQXnkh/tables/tblRmMB6LIdLHyEt/records" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "任务名称": "bocha-web-search技能验证",
      "描述": "验证博查AI Web Search API技能，测试API功能，确认扣费正常",
      "状态": "已完成",
      "分类": "技能验证",
      "优先级": "高",
      "产出": "bocha-web-search技能配置完成，API测试通过，扣费验证正常",
      "使用Skills": ["bocha-web-search", "飞书API", "Shell脚本"],
      "执行Agents": ["主Agent"],
      "技能使用详情": "1. bocha-web-search: API测试和配置\n2. 飞书API: 多维表格操作\n3. Shell脚本: 自动化测试",
      "耗时分钟": "120",
      "负责人": "OpenClaw Agent",
      "创建时间": 1772322000000,
      "实际完成": 1772323200000
    }
  }')

echo "添加响应: $ADD_RESPONSE"

echo -e "\n=== 完成 ==="