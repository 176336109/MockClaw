#!/usr/bin/env python3
"""
检查多维表格的实际字段结构
"""

import json
import requests
from pathlib import Path

print("🔍 检查多维表格字段结构")
print("=" * 60)

# 加载配置
config_path = Path.home() / ".openclaw" / "openclaw.json"
with open(config_path, 'r') as f:
    config = json.load(f)

feishu_config = config.get('channels', {}).get('feishu', {})
accounts = feishu_config.get('accounts', {}).get('main', {})

app_id = accounts.get('appId')
app_secret = accounts.get('appSecret')

# 获取token
url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
headers = {"Content-Type": "application/json; charset=utf-8"}
data = {
    "app_id": app_id,
    "app_secret": app_secret
}

response = requests.post(url, headers=headers, json=data, timeout=10)
result = response.json()

if result.get("code") != 0:
    print(f"❌ 获取token失败: {result}")
    exit(1)

token = result.get("tenant_access_token")

# 获取表格信息
base_app_token = "FCRNbSo4ja4hCEs5411cNZQXnkh"
table_id = "tblRmMB6LIdLHyEt"
api_headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 获取表格元数据
meta_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}"
response = requests.get(meta_url, headers=api_headers, timeout=10)
result = response.json()

if result.get("code") == 0:
    table_info = result.get("data", {}).get("table", {})
    print(f"✅ 表格信息获取成功")
    print(f"   表格名称: {table_info.get('name')}")
    print(f"   修订版本: {table_info.get('revision')}")
    
    # 获取字段信息
    fields_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/fields"
    response = requests.get(fields_url, headers=api_headers, timeout=10)
    fields_result = response.json()
    
    if fields_result.get("code") == 0:
        fields = fields_result.get("data", {}).get("items", [])
        print(f"\n📋 字段列表 (共{len(fields)}个):")
        print("=" * 60)
        
        for field in fields:
            field_name = field.get('field_name')
            field_type = field.get('type')
            field_id = field.get('field_id')
            print(f"  🔹 {field_name}")
            print(f"     类型: {field_type}")
            print(f"     ID: {field_id}")
            
            # 显示选项（如果是单选/多选）
            if field_type in [3, 4]:  # 3: 单选, 4: 多选
                options = field.get('property', {}).get('options', [])
                if options:
                    print(f"     选项: {[opt.get('name') for opt in options]}")
            
            print()
    else:
        print(f"❌ 获取字段失败: {fields_result.get('msg')}")
else:
    print(f"❌ 获取表格信息失败: {result.get('msg')}")

# 获取几条示例记录看看实际字段名
print("\n📝 示例记录字段名:")
print("=" * 60)

search_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/records/search"
search_data = {
    "page_size": 3
}

response = requests.post(search_url, headers=api_headers, json=search_data, timeout=10)
search_result = response.json()

if search_result.get("code") == 0:
    items = search_result.get("data", {}).get("items", [])
    print(f"获取到 {len(items)} 条示例记录")
    
    for i, item in enumerate(items, 1):
        print(f"\n记录 {i}:")
        fields = item.get('fields', {})
        for field_name, field_value in fields.items():
            print(f"  {field_name}: {field_value}")
else:
    print(f"❌ 获取示例记录失败: {search_result.get('msg')}")

print("\n" + "=" * 60)
print("✅ 字段检查完成")
print("=" * 60)