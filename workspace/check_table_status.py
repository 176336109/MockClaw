#!/usr/bin/env python3
"""
检查表格中的状态枚举，统一状态值
"""

import json
import requests
from pathlib import Path
from collections import Counter

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

# 多维表格配置
base_app_token = "FCRNbSo4ja4hCEs5411cNZQXnkh"
table_id = "tblRmMB6LIdLHyEt"
api_headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("\n2. 获取表格中的所有记录...")
search_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/records/search"

all_records = []
page_token = None
total_count = 0

while True:
    search_data = {
        "page_size": 100
    }
    if page_token:
        search_data["page_token"] = page_token
    
    response = requests.post(search_url, headers=api_headers, json=search_data, timeout=10)
    result = response.json()
    
    if result.get("code") != 0:
        print(f"❌ 获取记录失败: {result}")
        break
    
    items = result.get("data", {}).get("items", [])
    all_records.extend(items)
    total_count += len(items)
    
    has_more = result.get("data", {}).get("has_more", False)
    page_token = result.get("data", {}).get("page_token")
    
    print(f"  获取到 {len(items)} 条记录，总计 {total_count} 条")
    
    if not has_more or not page_token:
        break

print(f"\n3. 分析状态枚举（共 {len(all_records)} 条记录）...")

# 收集所有状态值
status_counter = Counter()
status_examples = {}

for record in all_records:
    fields = record.get('fields', {})
    status_field = fields.get('状态')
    
    if status_field:
        # 状态字段可能是字符串或列表
        if isinstance(status_field, list):
            # 飞书表格中的选择字段是列表格式
            for item in status_field:
                if isinstance(item, dict) and 'text' in item:
                    status = item['text']
                else:
                    status = str(item)
                status_counter[status] += 1
                
                # 保存示例
                task_name = fields.get('任务名称', '未知')
                if isinstance(task_name, list) and task_name:
                    task_name = task_name[0].get('text', '未知') if isinstance(task_name[0], dict) else str(task_name[0])
                
                if status not in status_examples:
                    status_examples[status] = {
                        'task_name': task_name,
                        'record_id': record.get('record_id')
                    }
        else:
            # 直接是字符串
            status = str(status_field)
            status_counter[status] += 1
            
            task_name = fields.get('任务名称', '未知')
            if isinstance(task_name, list) and task_name:
                task_name = task_name[0].get('text', '未知') if isinstance(task_name[0], dict) else str(task_name[0])
            
            if status not in status_examples:
                status_examples[status] = {
                    'task_name': task_name,
                    'record_id': record.get('record_id')
                }

print("\n📊 当前表格中的状态枚举:")
print("=" * 50)
for status, count in status_counter.most_common():
    example = status_examples.get(status, {})
    print(f"  {status:10} : {count:3} 条记录")
    if example:
        print(f"          示例: {example['task_name'][:30]}... (ID: {example['record_id'][:10]}...)")

# 分析问题
print("\n🔍 状态不统一问题分析:")
print("=" * 50)

# 标准状态（我们定义的）
standard_statuses = ['进行中', '完成', '等待指示', '搁置']
found_standard = []
found_non_standard = []

for status in status_counter.keys():
    if status in standard_statuses:
        found_standard.append(status)
    else:
        found_non_standard.append(status)

print(f"✅ 标准状态 ({len(found_standard)}/{len(standard_statuses)}):")
for status in found_standard:
    print(f"  • {status}")

print(f"\n❌ 非标准状态 ({len(found_non_standard)}):")
for status in found_non_standard:
    print(f"  • {status}")

# 映射建议
print("\n💡 状态映射建议:")
print("=" * 50)

status_mapping = {
    '已完成': '完成',
    '已完': '完成',
    '完成✅': '完成',
    '进行中🚀': '进行中',
    '等待中': '等待指示',
    '待处理': '等待指示',
    '暂停': '搁置',
    '取消': '搁置'
}

print("建议将以下状态统一:")
for old_status, new_status in status_mapping.items():
    if old_status in status_counter:
        print(f"  {old_status} → {new_status} ({status_counter[old_status]}条记录)")

# 需要新增的状态
potential_new_statuses = []
for status in found_non_standard:
    if status not in status_mapping and status not in standard_statuses:
        potential_new_statuses.append(status)

if potential_new_statuses:
    print(f"\n⚠️  可能需要新增的状态 ({len(potential_new_statuses)}):")
    for status in potential_new_statuses:
        print(f"  • {status} ({status_counter[status]}条记录)")

print(f"\n📋 总结:")
print(f"  总记录数: {len(all_records)}")
print(f"  不同状态数: {len(status_counter)}")
print(f"  标准状态: {len(found_standard)}")
print(f"  非标准状态: {len(found_non_standard)}")
print(f"  需要统一的记录: {sum(status_counter[s] for s in found_non_standard if s in status_mapping)}")

# 保存分析结果
result_file = Path.home() / ".openclaw" / "workspace" / "status_analysis.json"
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump({
        "timestamp": time.time(),
        "total_records": len(all_records),
        "status_counter": dict(status_counter),
        "standard_statuses": standard_statuses,
        "found_standard": found_standard,
        "found_non_standard": found_non_standard,
        "status_mapping": status_mapping,
        "status_examples": status_examples
    }, f, indent=2, ensure_ascii=False)

print(f"\n✅ 分析结果已保存: {result_file}")