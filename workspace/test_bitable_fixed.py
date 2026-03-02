#!/usr/bin/env python3
"""
测试bitable API调用（修复字段名问题）
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

# 使用正确的字段名
base_app_token = "FCRNbSo4ja4hCEs5411cNZQXnkh"
table_id = "tblRmMB6LIdLHyEt"

# 正确的字段名（根据实际字段列表）
correct_fields = {
    "文本": "fld0WO220l",
    "任务ID": "fldvW39Rpe",
    "任务名称": "fld6Lbbl9h",
    "状态": "fldhPuiSnm",
    "优先级": "fldovvqCGX",
    "负责人": "fldq1XIKMn",
    "创建时间": "fldYDbvwlf",
    "预计完成": "fldKVCcjKv",
    "实际完成": "fldxtCa9uA",
    "耗时分钟": "fldOOANzpF",
    "描述": "fldhtpelmF",
    "产出": "fldA4G0uIl",
    "分类": "fldcgtwp3e",
    "执行Agents": "fldhdhbFxi",
    "使用Skills": "fld58jbPHY",
    "技能使用详情": "fldi1HxyWn"
}

print("\n2. 测试创建记录（使用正确字段名）...")
current_ts = int(time.time() * 1000)
record_data = {
    "fields": {
        "文本": "测试任务: API测试修复",
        "任务ID": "TEST-20260302-1349",
        "任务名称": "测试API调用修复",
        "状态": "进行中",
        "描述": "测试多维表格API修复字段名问题",
        "创建时间": current_ts,
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
    
    # 搜索验证
    print("\n3. 搜索验证...")
    search_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/records/search"
    search_data = {
        "filter": {
            "conjunction": "and",
            "conditions": [
                {
                    "field_name": "任务ID",
                    "operator": "is",
                    "value": ["TEST-20260302-1349"]
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
            fields = item.get('fields', {})
            print(f"  任务ID: {fields.get('任务ID')}")
            print(f"  任务名称: {fields.get('任务名称')}")
            print(f"  状态: {fields.get('状态')}")
            print(f"  创建时间: {fields.get('创建时间')}")
    
    # 测试更新
    print("\n4. 测试更新记录...")
    update_data = {
        "fields": {
            "状态": "完成",
            "描述": "API测试修复完成，字段名问题已解决",
            "实际完成": int(time.time() * 1000)
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

print("\n5. 测试同步实际任务...")
actual_tasks = [
    {
        "任务ID": "TASK-20260302-1311",
        "任务名称": "建立状态反馈系统",
        "状态": "进行中",
        "描述": "创建状态监控机制，让你随时知道我的工作状态"
    },
    {
        "任务ID": "TASK-20260302-1307",
        "任务名称": "实施共享记忆库系统",
        "状态": "进行中", 
        "描述": "基于拿来主义思想，建立简化版共享记忆库"
    }
]

for task in actual_tasks:
    print(f"\n同步任务: {task['任务名称']}")
    
    task_data = {
        "fields": {
            "文本": f"任务状态更新: {task['任务名称']}",
            "任务ID": task["任务ID"],
            "任务名称": task["任务名称"],
            "状态": task["状态"],
            "描述": task["描述"],
            "创建时间": int(time.time() * 1000),
            "负责人": "OpenClaw主Agent",
            "优先级": "高" if task["状态"] == "等待指示" else "中"
        }
    }
    
    # 先搜索是否已存在
    search_data = {
        "filter": {
            "conjunction": "and",
            "conditions": [
                {
                    "field_name": "任务ID",
                    "operator": "is",
                    "value": [task["任务ID"]]
                }
            ]
        },
        "page_size": 1
    }
    
    search_response = requests.post(search_url, headers=create_headers, json=search_data, timeout=10)
    search_result = search_response.json()
    
    if search_result.get("code") == 0:
        items = search_result.get("data", {}).get("items", [])
        if items:
            # 更新现有记录
            existing_id = items[0].get('record_id')
            update_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/records/{existing_id}"
            update_response = requests.put(update_url, headers=create_headers, json=task_data, timeout=10)
            update_result = update_response.json()
            
            if update_result.get("code") == 0:
                print(f"  ✅ 更新成功 (Record ID: {existing_id})")
            else:
                print(f"  ❌ 更新失败: {update_result}")
        else:
            # 创建新记录
            create_response = requests.post(create_url, headers=create_headers, json=task_data, timeout=10)
            create_result = create_response.json()
            
            if create_result.get("code") == 0:
                record_id = create_result.get("data", {}).get("record", {}).get("record_id")
                print(f"  ✅ 创建成功 (Record ID: {record_id})")
            else:
                print(f"  ❌ 创建失败: {create_result}")
    else:
        print(f"  ❌ 搜索失败: {search_result}")

print("\n✅ 所有测试完成!")