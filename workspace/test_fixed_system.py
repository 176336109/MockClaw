#!/usr/bin/env python3
"""
测试修复后的系统
"""

import sys
from pathlib import Path

# 添加技能目录到路径
skill_dir = Path.home() / ".openclaw" / "workspace" / "skills" / "bitable-core"
sys.path.insert(0, str(skill_dir))

from bitable_core import BitableCore

print("1. 初始化BitableCore...")
core = BitableCore()

print("2. 检查健康状态...")
health = core.check_health()
print(f"整体状态: {health['overall_status']}")
print(f"Token状态: {health['components']['token']['healthy']}")
print(f"API状态: {health['components']['api']['healthy']}")
print(f"表格状态: {health['components']['table']['healthy']}")

print("\n3. 测试同步任务...")
test_tasks = [
    {
        'id': 'TASK-20260302-1350',
        'name': '修复多维表格API问题',
        'status': '进行中',
        'details': '修复字段名不匹配问题，恢复自动同步'
    },
    {
        'id': 'TASK-20260302-1351',
        'name': '验证状态反馈系统',
        'status': '进行中',
        'details': '验证心跳机制和状态监控是否正常工作'
    }
]

for task in test_tasks:
    print(f"\n同步任务: {task['name']}")
    result = core.sync_task_status(
        task['id'],
        task['name'],
        task['status'],
        task['details']
    )
    
    if result['sync_success']:
        print(f"  ✅ 同步成功!")
        print(f"     耗时: {result['elapsed_seconds']}秒")
        print(f"     重试次数: {result['retry_count']}")
    else:
        print(f"  ❌ 同步失败: {result.get('error')}")

print("\n4. 批量同步测试...")
# 测试批量同步
from shared_memory_system import SharedMemorySystem

memory_system = SharedMemorySystem()
sync_result = memory_system.sync_all_pending_tasks()

print(f"批量同步结果:")
print(f"  总任务数: {sync_result.get('total', 0)}")
print(f"  成功数: {sync_result.get('success', 0)}")
print(f"  失败数: {sync_result.get('failure', 0)}")
print(f"  成功率: {sync_result.get('success_rate', 0):.1f}%")

print("\n✅ 测试完成!")