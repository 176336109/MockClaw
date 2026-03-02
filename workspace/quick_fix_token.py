#!/usr/bin/env python3
"""
快速修复token问题
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

print("1. 获取新token...")
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
print(f"✅ 获取新token成功: {token[:20]}...")

# 保存到缓存
cache_dir = Path.home() / ".openclaw" / "workspace" / ".bitable_cache"
cache_dir.mkdir(exist_ok=True)

cache_file = cache_dir / "token_cache.json"
cache_data = {
    'token': token,
    'expires_at': time.time() + 7200  # 2小时
}

with open(cache_file, 'w') as f:
    json.dump(cache_data, f)

print(f"✅ Token已保存到缓存: {cache_file}")

# 测试API
print("\n2. 测试API调用...")
base_app_token = "FCRNbSo4ja4hCEs5411cNZQXnkh"
table_id = "tblRmMB6LIdLHyEt"

# 简单测试
test_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/records/search"
test_headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
test_data = {
    "page_size": 1
}

test_response = requests.post(test_url, headers=test_headers, json=test_data, timeout=10)
test_result = test_response.json()

if test_result.get("code") == 0:
    print(f"✅ API测试成功!")
    items = test_result.get("data", {}).get("items", [])
    print(f"   找到 {len(items)} 条记录")
else:
    print(f"❌ API测试失败: {test_result}")

print("\n3. 立即同步关键任务...")
critical_tasks = [
    {
        "任务ID": "TASK-20260302-1355",
        "任务名称": "建立session对话系统",
        "状态": "进行中",
        "描述": "创建连续对话机制，减少来回等待时间"
    },
    {
        "任务ID": "TASK-20260302-1356",
        "任务名称": "修复多维表格同步",
        "状态": "进行中",
        "描述": "解决token无效问题，恢复自动同步"
    }
]

create_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/records"

for task in critical_tasks:
    print(f"\n同步: {task['任务名称']}")
    
    record_data = {
        "fields": {
            "文本": f"任务状态更新: {task['任务名称']}",
            "任务ID": task["任务ID"],
            "任务名称": task["任务名称"],
            "状态": task["状态"],
            "描述": task["描述"],
            "创建时间": int(time.time() * 1000),
            "负责人": "OpenClaw主Agent",
            "优先级": "高"
        }
    }
    
    response = requests.post(create_url, headers=test_headers, json=record_data, timeout=10)
    result = response.json()
    
    if result.get("code") == 0:
        record_id = result.get("data", {}).get("record", {}).get("record_id")
        print(f"  ✅ 同步成功! Record ID: {record_id}")
    else:
        print(f"  ❌ 同步失败: {result}")

print("\n✅ 快速修复完成!")