#!/usr/bin/env python3
"""
统一表格状态，修复状态不统一问题
"""

import json
import requests
import time
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

def extract_task_name(fields):
    """提取任务名称"""
    task_name_field = fields.get('任务名称')
    if not task_name_field:
        return "未知任务"
    
    if isinstance(task_name_field, list) and task_name_field:
        item = task_name_field[0]
        if isinstance(item, dict) and 'text' in item:
            return item['text']
        return str(item)
    return str(task_name_field)

# 状态映射规则
STATUS_MAPPING = {
    '已完成': '完成',
    '已完': '完成',
    '完成✅': '完成',
    '进行中🚀': '进行中',
    '等待中': '等待指示',
    '待处理': '等待指示',
    '暂停': '搁置',
    '取消': '搁置'
}

# 标准状态集合（更新后）
STANDARD_STATUSES = ['进行中', '完成', '等待指示', '搁置', '测试中']

print(f"\n2. 获取需要统一状态的记录...")
search_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/records/search"

# 获取所有记录
all_records = []
page_token = None

while True:
    search_data = {"page_size": 100}
    if page_token:
        search_data["page_token"] = page_token
    
    response = requests.post(search_url, headers=api_headers, json=search_data, timeout=10)
    result = response.json()
    
    if result.get("code") != 0:
        print(f"❌ 获取记录失败: {result}")
        break
    
    items = result.get("data", {}).get("items", [])
    all_records.extend(items)
    
    has_more = result.get("data", {}).get("has_more", False)
    page_token = result.get("data", {}).get("page_token")
    
    if not has_more or not page_token:
        break

print(f"  获取到 {len(all_records)} 条记录")

# 找出需要更新的记录
records_to_update = []
status_changes = Counter()

for record in all_records:
    record_id = record.get('record_id')
    fields = record.get('fields', {})
    
    # 提取当前状态
    current_status_field = fields.get('状态')
    if not current_status_field:
        continue
    
    current_status = None
    if isinstance(current_status_field, list) and current_status_field:
        # 飞书选择字段格式
        item = current_status_field[0]
        if isinstance(item, dict) and 'text' in item:
            current_status = item['text']
        else:
            current_status = str(item)
    else:
        current_status = str(current_status_field)
    
    # 检查是否需要更新
    new_status = None
    if current_status in STATUS_MAPPING:
        new_status = STATUS_MAPPING[current_status]
    elif current_status not in STANDARD_STATUSES:
        # 未知状态，可能需要处理
        print(f"  ⚠️  未知状态: {current_status} (记录: {record_id[:10]}...)")
        continue
    
    if new_status and new_status != current_status:
        records_to_update.append({
            'record_id': record_id,
            'current_status': current_status,
            'new_status': new_status,
            'task_name': extract_task_name(fields)
        })
        status_changes[(current_status, new_status)] += 1

def extract_task_name(fields):
    """提取任务名称"""
    task_name_field = fields.get('任务名称')
    if not task_name_field:
        return "未知任务"
    
    if isinstance(task_name_field, list) and task_name_field:
        item = task_name_field[0]
        if isinstance(item, dict) and 'text' in item:
            return item['text']
        return str(item)
    return str(task_name_field)

print(f"\n3. 需要更新的记录: {len(records_to_update)} 条")
print("状态变更统计:")
for (old, new), count in status_changes.most_common():
    print(f"  {old} → {new}: {count} 条")

if not records_to_update:
    print("✅ 所有记录状态已统一!")
    exit(0)

print(f"\n4. 开始统一状态更新...")
update_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/records"

success_count = 0
failure_count = 0
results = []

for i, record_info in enumerate(records_to_update):
    print(f"\n[{i+1}/{len(records_to_update)}] 更新: {record_info['task_name'][:30]}...")
    print(f"  状态: {record_info['current_status']} → {record_info['new_status']}")
    
    # 准备更新数据
    update_data = {
        "fields": {
            "状态": record_info['new_status']
        }
    }
    
    # 如果是"已完成"→"完成"，也更新文本字段
    if record_info['current_status'] == '已完成' and record_info['new_status'] == '完成':
        text_field = f"任务完成: {record_info['task_name']}"
        update_data["fields"]["文本"] = text_field
    
    # 调用API更新
    record_update_url = f"{update_url}/{record_info['record_id']}"
    
    try:
        response = requests.put(record_update_url, headers=api_headers, json=update_data, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            print(f"  ✅ 更新成功!")
            success_count += 1
            results.append({
                'record_id': record_info['record_id'],
                'task_name': record_info['task_name'],
                'old_status': record_info['current_status'],
                'new_status': record_info['new_status'],
                'success': True
            })
        else:
            print(f"  ❌ 更新失败: {result.get('msg')}")
            failure_count += 1
            results.append({
                'record_id': record_info['record_id'],
                'task_name': record_info['task_name'],
                'old_status': record_info['current_status'],
                'new_status': record_info['new_status'],
                'success': False,
                'error': result.get('msg')
            })
        
        # 短暂延迟，避免API限流
        time.sleep(0.3)
        
    except Exception as e:
        print(f"  ❌ 更新异常: {e}")
        failure_count += 1
        results.append({
            'record_id': record_info['record_id'],
            'task_name': record_info['task_name'],
            'old_status': record_info['current_status'],
            'new_status': record_info['new_status'],
            'success': False,
            'error': str(e)
        })

print(f"\n5. 统一完成!")
print(f"   总更新数: {len(records_to_update)}")
print(f"   成功数: {success_count}")
print(f"   失败数: {failure_count}")
print(f"   成功率: {success_count/len(records_to_update)*100:.1f}%")

# 保存结果
result_file = Path.home() / ".openclaw" / "workspace" / "status_unification_results.json"
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump({
        "timestamp": time.time(),
        "total_updates": len(records_to_update),
        "success_count": success_count,
        "failure_count": failure_count,
        "success_rate": success_count/len(records_to_update)*100,
        "status_changes": dict(status_changes),
        "standard_statuses": STANDARD_STATUSES,
        "results": results
    }, f, indent=2, ensure_ascii=False)

print(f"\n✅ 统一结果已保存: {result_file}")

# 显示需要手动处理的任务
if failure_count > 0:
    print(f"\n⚠️  需要手动处理的任务 ({failure_count}个):")
    for result in results:
        if not result['success']:
            print(f"  • {result['task_name']}: {result.get('error', '未知错误')}")

print(f"\n📋 标准状态列表 (已更新):")
for status in STANDARD_STATUSES:
    print(f"  • {status}")

print(f"\n📊 多维表格地址: https://t33vwocwc8.feishu.cn/base/FCRNbSo4ja4hCEs5411cNZQXnkh")