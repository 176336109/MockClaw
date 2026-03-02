#!/usr/bin/env python3
"""
同步已完成任务到多维表格
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

# 多维表格配置
base_app_token = "FCRNbSo4ja4hCEs5411cNZQXnkh"
table_id = "tblRmMB6LIdLHyEt"
api_headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 已完成的任务列表
completed_tasks = [
    # 之前的多维表格相关任务
    {
        "任务ID": "TASK-20260301-231630",
        "任务名称": "Skill状态检查",
        "状态": "完成",
        "描述": "已完成所有Skill状态检查，更新到多维表格",
        "完成时间": int(time.time() * 1000)
    },
    {
        "任务ID": "TASK-20260301-235100",
        "任务名称": "飞书文档创建",
        "状态": "完成",
        "描述": "已创建飞书文档系统，测试完成",
        "完成时间": int(time.time() * 1000)
    },
    {
        "任务ID": "TASK-20260302-1130",
        "任务名称": "三层记忆架构实施",
        "状态": "完成",
        "描述": "已实施简化的三层记忆架构（工作记忆、情景记忆、语义记忆）",
        "完成时间": int(time.time() * 1000)
    },
    {
        "任务ID": "TASK-20260302-1159",
        "任务名称": "工作流程优化",
        "状态": "完成",
        "描述": "已优化工作流程，建立标准状态（进行中/完成/等待指示/搁置）",
        "完成时间": int(time.time() * 1000)
    },
    
    # 今天的任务
    {
        "任务ID": "TASK-20260302-1307",
        "任务名称": "实施共享记忆库系统",
        "状态": "完成",
        "描述": "基于拿来主义思想，建立简化版共享记忆库，已完成目录结构和安全护栏",
        "完成时间": int(time.time() * 1000)
    },
    {
        "任务ID": "TASK-20260302-1311",
        "任务名称": "建立状态反馈系统",
        "状态": "完成",
        "描述": "创建状态监控机制，心跳系统已建立，监控页面可用",
        "完成时间": int(time.time() * 1000)
    },
    {
        "任务ID": "TASK-20260302-1345",
        "任务名称": "修复多维表格API问题",
        "状态": "完成",
        "描述": "修复token和字段名问题，API恢复正常工作",
        "完成时间": int(time.time() * 1000)
    },
    {
        "任务ID": "TASK-20260302-1346",
        "任务名称": "部署状态监控系统",
        "状态": "完成",
        "描述": "建立状态反馈和监控机制，让你随时知道我的工作状态",
        "完成时间": int(time.time() * 1000)
    },
    {
        "任务ID": "TASK-20260302-1355",
        "任务名称": "建立session对话系统",
        "状态": "完成",
        "描述": "创建连续对话机制，减少来回等待时间",
        "完成时间": int(time.time() * 1000)
    },
    {
        "任务ID": "TASK-20260302-1356",
        "任务名称": "修复多维表格同步",
        "状态": "完成",
        "描述": "解决token无效问题，恢复自动同步",
        "完成时间": int(time.time() * 1000)
    }
]

print(f"\n2. 同步 {len(completed_tasks)} 个已完成任务...")

# 搜索URL
search_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/records/search"
# 创建/更新URL
record_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base_app_token}/tables/{table_id}/records"

results = []
success_count = 0
failure_count = 0

for task in completed_tasks:
    print(f"\n处理: {task['任务名称']} ({task['任务ID']})")
    
    try:
        # 1. 先搜索是否已存在
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
        
        search_response = requests.post(search_url, headers=api_headers, json=search_data, timeout=10)
        search_result = search_response.json()
        
        record_id = None
        if search_result.get("code") == 0:
            items = search_result.get("data", {}).get("items", [])
            if items:
                record_id = items[0].get('record_id')
                print(f"  找到现有记录: {record_id}")
        
        # 2. 准备数据
        record_data = {
            "fields": {
                "文本": f"任务完成: {task['任务名称']}",
                "任务ID": task["任务ID"],
                "任务名称": task["任务名称"],
                "状态": task["状态"],
                "描述": task["描述"],
                "创建时间": task.get("完成时间", int(time.time() * 1000)),
                "实际完成": task.get("完成时间", int(time.time() * 1000)),
                "负责人": "OpenClaw主Agent",
                "优先级": "低"  # 已完成的任务优先级低
            }
        }
        
        # 3. 创建或更新记录
        if record_id:
            # 更新现有记录
            update_url = f"{record_url}/{record_id}"
            response = requests.put(update_url, headers=api_headers, json=record_data, timeout=10)
            action = "更新"
        else:
            # 创建新记录
            response = requests.post(record_url, headers=api_headers, json=record_data, timeout=10)
            action = "创建"
        
        result = response.json()
        
        if result.get("code") == 0:
            new_record_id = result.get("data", {}).get("record", {}).get("record_id") or record_id
            print(f"  ✅ {action}成功! Record ID: {new_record_id}")
            success_count += 1
            results.append({
                "任务ID": task["任务ID"],
                "任务名称": task["任务名称"],
                "状态": "成功",
                "record_id": new_record_id,
                "action": action
            })
        else:
            print(f"  ❌ {action}失败: {result.get('msg')}")
            failure_count += 1
            results.append({
                "任务ID": task["任务ID"],
                "任务名称": task["任务名称"],
                "状态": "失败",
                "error": result.get('msg')
            })
        
        # 短暂延迟，避免API限流
        time.sleep(0.5)
        
    except Exception as e:
        print(f"  ❌ 处理异常: {e}")
        failure_count += 1
        results.append({
            "任务ID": task["任务ID"],
            "任务名称": task["任务名称"],
            "状态": "异常",
            "error": str(e)
        })

print(f"\n3. 同步完成!")
print(f"   总任务数: {len(completed_tasks)}")
print(f"   成功数: {success_count}")
print(f"   失败数: {failure_count}")
print(f"   成功率: {success_count/len(completed_tasks)*100:.1f}%")

# 保存结果
result_file = Path.home() / ".openclaw" / "workspace" / "task_sync_results.json"
with open(result_file, 'w', encoding='utf-8') as f:
    json.dump({
        "timestamp": time.time(),
        "total_tasks": len(completed_tasks),
        "success_count": success_count,
        "failure_count": failure_count,
        "success_rate": success_count/len(completed_tasks)*100,
        "results": results
    }, f, indent=2, ensure_ascii=False)

print(f"\n✅ 同步结果已保存: {result_file}")

# 显示需要手动处理的任务
if failure_count > 0:
    print(f"\n⚠️  需要手动处理的任务 ({failure_count}个):")
    for result in results:
        if result["状态"] in ["失败", "异常"]:
            print(f"  • {result['任务名称']} ({result['任务ID']}): {result.get('error', '未知错误')}")

print(f"\n📊 多维表格地址: https://t33vwocwc8.feishu.cn/base/FCRNbSo4ja4hCEs5411cNZQXnkh")