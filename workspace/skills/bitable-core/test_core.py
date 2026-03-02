#!/usr/bin/env python3
"""
测试多维表格核心技能
"""

import sys
import json
from pathlib import Path

# 添加技能目录到路径
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from bitable_core import BitableCore

def test_health_check():
    """测试健康检查"""
    print("🧪 测试健康检查...")
    core = BitableCore()
    health = core.check_health()
    
    print(f"整体状态: {health['overall_status']}")
    print(f"Token状态: {health['components']['token']['healthy']}")
    print(f"API状态: {health['components']['api']['healthy']}")
    print(f"表格状态: {health['components']['table']['healthy']}")
    print(f"备份状态: {health['components']['backup']['healthy']}")
    
    return health['overall_status'] == 'healthy'

def test_sync_single_task():
    """测试同步单个任务"""
    print("\n🧪 测试同步单个任务...")
    core = BitableCore()
    
    # 测试任务
    test_task = {
        'task_id': 'TEST-20260302-001',
        'task_name': '测试多维表格核心技能',
        'status': '进行中',
        'details': '测试核心技能的同步功能'
    }
    
    result = core.sync_task_status(**test_task)
    
    print(f"任务ID: {result['task_id']}")
    print(f"同步成功: {result['sync_success']}")
    print(f"本地成功: {result['local_success']}")
    print(f"耗时: {result['elapsed_seconds']}秒")
    
    if result.get('error'):
        print(f"错误: {result['error']}")
    
    return result['sync_success']

def test_batch_sync():
    """测试批量同步"""
    print("\n🧪 测试批量同步...")
    core = BitableCore()
    
    # 添加多个测试任务
    test_tasks = [
        {
            'task_id': 'TEST-20260302-002',
            'task_name': '测试任务1',
            'status': '已完成',
            'details': '批量同步测试1'
        },
        {
            'task_id': 'TEST-20260302-003', 
            'task_name': '测试任务2',
            'status': '进行中',
            'details': '批量同步测试2'
        },
        {
            'task_id': 'TEST-20260302-004',
            'task_name': '测试任务3',
            'status': '等待指示',
            'details': '批量同步测试3'
        }
    ]
    
    results = []
    for task in test_tasks:
        result = core.sync_task_status(**task)
        results.append(result)
        print(f"  {task['task_id']}: {'✅' if result['sync_success'] else '❌'}")
    
    success_count = sum(1 for r in results if r['sync_success'])
    print(f"批量同步结果: {success_count}/{len(results)} 成功")
    
    return success_count == len(results)

def test_generate_report():
    """测试生成报告"""
    print("\n🧪 测试生成报告...")
    core = BitableCore()
    
    report = core.generate_report()
    
    print(f"技能: {report['skill']}")
    print(f"重要性: {report['importance']}")
    print(f"健康状态: {report['health']['overall_status']}")
    print(f"任务统计: {report['statistics'].get('total_tasks', 'N/A')} 个任务")
    print(f"同步率: {report['statistics'].get('sync_rate', 'N/A'):.1f}%")
    print(f"可用性: {report['metrics'].get('availability', 'N/A'):.1f}%")
    
    # 保存报告
    report_file = skill_dir / "test_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"报告已保存到: {report_file}")
    
    return True

def test_error_recovery():
    """测试错误恢复"""
    print("\n🧪 测试错误恢复...")
    core = BitableCore()
    
    # 测试无效token情况
    print("测试本地备份功能...")
    
    # 先确保本地数据库工作
    test_task = {
        'task_id': 'TEST-RECOVERY-001',
        'task_name': '错误恢复测试',
        'status': '测试中',
        'details': '测试本地备份和恢复功能'
    }
    
    result = core.sync_task_status(**test_task)
    
    print(f"本地保存: {'✅' if result['local_success'] else '❌'}")
    print(f"远程同步: {'✅' if result['sync_success'] else '❌'}")
    
    # 即使远程失败，本地也应该成功
    return result['local_success']

def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("🧪 多维表格核心技能全面测试")
    print("=" * 60)
    
    test_results = []
    
    # 测试1: 健康检查
    try:
        health_ok = test_health_check()
        test_results.append(('健康检查', health_ok))
    except Exception as e:
        print(f"健康检查失败: {e}")
        test_results.append(('健康检查', False))
    
    # 测试2: 单个任务同步
    try:
        sync_ok = test_sync_single_task()
        test_results.append(('单个任务同步', sync_ok))
    except Exception as e:
        print(f"单个任务同步失败: {e}")
        test_results.append(('单个任务同步', False))
    
    # 测试3: 批量同步
    try:
        batch_ok = test_batch_sync()
        test_results.append(('批量同步', batch_ok))
    except Exception as e:
        print(f"批量同步失败: {e}")
        test_results.append(('批量同步', False))
    
    # 测试4: 生成报告
    try:
        report_ok = test_generate_report()
        test_results.append(('生成报告', report_ok))
    except Exception as e:
        print(f"生成报告失败: {e}")
        test_results.append(('生成报告', False))
    
    # 测试5: 错误恢复
    try:
        recovery_ok = test_error_recovery()
        test_results.append(('错误恢复', recovery_ok))
    except Exception as e:
        print(f"错误恢复失败: {e}")
        test_results.append(('错误恢复', False))
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, passed in test_results if passed)
    
    for test_name, passed in test_results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:20} {status}")
    
    print(f"\n总计: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过！核心技能正常工作。")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} 个测试失败，需要检查。")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)