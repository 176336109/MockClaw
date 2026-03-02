#!/usr/bin/env python3
"""
测试bitable API调用
"""

import json
import requests
from pathlib import Path
import time

# 加载配置
config_path = Path.home() / ".openclaw" / "openclaw.json"
with open(config_path, 'r') as f:
    config = json.load(f)

feishu_config = config.get('channels', {}).get('feishu', {})
accounts = feishu_config.get('accounts', {}).get('main', {})

app_id = accounts.get('appId')
app_secret = accounts.get('appSecret')

print("1. 获取token...")
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
print(f"✅ Token获取成功: {token[:20]}...")

# 测试字段获取
print("\n2. 测试字段获取...")
base_app_token = "FCRNbSo4ja4hCEs5411cNZQXnkh"
table_id = "tblRmMB6LIdLHyEt"

fields_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/fields"
fields_headers = {"Authorization": f"Bearer {token}"}

fields_response = requests.get(fields_url, headers=fields_headers, timeout=10)
fields_result = fields_response.json()

if fields_result.get("code") == 0:
    fields = fields_result.get("data", {}).get("items", [])
    print(f"✅ 获取到 {len(fields)} 个字段")
    
    # 显示字段信息
    print("\n字段列表:")
    for field in fields:
        field_name = field.get('field_name')
        field_id = field.get('field_id')
        field_type = field.get('type')
        print(f"  - {field_name} ({field_type}): {field_id}")
else:
    print(f"❌ 获取字段失败: {fields_result}")

# 测试创建记录
print("\n3. 测试创建记录...")
current_ts = int(time.time() * 1000)
record_data = {
    "fields": {
        "文本": "测试任务: API测试",
        "任务ID": "TEST-20260302-1345",
        "任务名称": "测试API调用",
        "状态": "进行中",
        "描述": "测试多维表格API是否正常工作",
        "最后更新时间": current_ts,
        "负责人": "OpenClaw主Agent",
        "优先级": "高"
    }
}

create_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/records"
create_headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

create_response = requests.post(create_url, headers=create_headers, json=record_data, timeout=10)
create_result = create_response.json()

if create_result.get("code") == 0:
    record_id = create_result.get("data", {}).get("record", {}).get("record_id")
    print(f"✅ 创建记录成功! Record ID: {record_id}")
    
    # 测试更新记录
    print("\n4. 测试更新记录...")
    update_data = {
        "fields": {
            "状态": "完成",
            "描述": "API测试完成，一切正常",
            "最后更新时间": int(time.time() * 1000)
        }
    }
    
    update_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/records/{record_id}"
    update_response = requests.put(update_url, headers=create_headers, json=update_data, timeout=10)
    update_result = update_response.json()
    
    if update_result.get("code") == 0:
        print(f"✅ 更新记录成功!")
    else:
        print(f"❌ 更新记录失败: {update_result}")
    
else:
    print(f"❌ 创建记录失败: {create_result}")
    
    # 如果是字段名错误，尝试其他字段名
    if create_result.get('code') == 1254002:  # 字段不存在
        print("\n尝试使用实际字段名...")
        
        # 先搜索现有记录看看字段名
        search_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/records/search"
        search_data = {
            "page_size": 1
        }
        
        search_response = requests.post(search_url, headers=create_headers, json=search_data, timeout=10)
        search_result = search_response.json()
        
        if search_result.get("code") == 0:
            items = search_result.get("data", {}).get("items", [])
            if items:
                actual_fields = items[0].get('fields', {})
                print(f"实际字段名: {list(actual_fields.keys())}")
                
                # 使用实际字段名重试
                actual_record_data = {
                    "fields": {
                        "文本": "测试任务: 使用实际字段名",
                        "任务ID": "TEST-20260302-1346",
                        "任务名称": "测试实际字段名",
                        "状态": "进行中"
                    }
                }
                
                # 只使用存在的字段
                for key in list(actual_record_data["fields"].keys()):
                    if key not in actual_fields:
                        print(f"警告: 字段 '{key}' 不存在，移除")
                        del actual_record_data["fields"][key]
                
                retry_response = requests.post(create_url, headers=create_headers, json=actual_record_data, timeout=10)
                retry_result = retry_response.json()
                
                if retry_result.get("code") == 0:
                    print(f"✅ 使用实际字段名创建成功!")
                else:
                    print(f"❌ 重试失败: {retry_result}")

print("\n5. 测试搜索记录...")
search_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/records/search"
search_data = {
    "filter": {
        "conjunction": "and",
        "conditions": [
            {
                "field_name": "任务ID",
                "operator": "is",
                "value": ["TEST-20260302-1345"]
            }
        ]
    },
    "page_size": 10
}

search_response = requests.post(search_url, headers=create_headers, json=search_data, timeout=10)
search_result = search_response.json()

if search_result.get("code") == 0:
    items = search_result.get("data", {}).get("items", [])
    print(f"✅ 搜索到 {len(items)} 条记录")
    for item in items:
        print(f"  - {item.get('fields', {})}")
else:
    print(f"❌ 搜索失败: {search_result}")

print("\n✅ 所有测试完成!")