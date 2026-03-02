#!/usr/bin/env python3
"""
将多维表格核心技能集成到工作流程
"""

import sys
import json
import time
from datetime import datetime
from pathlib import Path

# 添加技能目录到路径
skill_dir = Path(__file__).parent
sys.path.insert(0, str(skill_dir))

from bitable_core import BitableCore

class WorkflowIntegrator:
    """工作流程集成器"""
    
    def __init__(self):
        self.core = BitableCore()
        self.workspace = Path.home() / ".openclaw" / "workspace"
        
    def session_start_integration(self):
        """会话开始集成"""
        print("🔄 会话开始: 集成多维表格核心技能")
        
        # 1. 检查技能健康
        print("  1. 检查技能健康状态...")
        health = self.core.check_health()
        
        if health['overall_status'] != 'healthy':
            print(f"  ⚠️ 技能状态: {health['overall_status']}")
            print(f"    需要立即修复沟通媒介!")
            
            # 尝试自动修复
            self._try_auto_fix(health)
        else:
            print(f"  ✅ 技能状态: 健康")
        
        # 2. 同步最新状态
        print("  2. 同步最新任务状态...")
        sync_result = self.core.sync_all_pending_tasks()
        
        if sync_result.get('total', 0) > 0:
            print(f"  📊 同步了 {sync_result['success']}/{sync_result['total']} 个任务")
        
        # 3. 生成会话摘要
        print("  3. 生成会话摘要...")
        summary = self._generate_session_summary(health, sync_result)
        
        # 4. 记录到记忆系统
        self._record_to_memory('session_start', summary)
        
        print("✅ 会话开始集成完成")
        return summary
    
    def task_status_change_integration(self, task_id: str, task_name: str, old_status: str, new_status: str, details: str = ""):
        """任务状态变化集成"""
        print(f"🔄 任务状态变化: {task_id} {old_status} → {new_status}")
        
        # 1. 立即同步到多维表格
        print(f"  1. 同步到多维表格...")
        sync_result = self.core.sync_task_status(task_id, task_name, new_status, details)
        
        # 2. 验证同步成功
        if sync_result['sync_success']:
            print(f"  ✅ 同步成功 (耗时: {sync_result['elapsed_seconds']}秒)")
        else:
            print(f"  ❌ 同步失败: {sync_result.get('error', '未知错误')}")
            print(f"  📝 已保存到本地备份")
        
        # 3. 记录状态变化
        change_record = {
            'task_id': task_id,
            'task_name': task_name,
            'old_status': old_status,
            'new_status': new_status,
            'sync_result': sync_result,
            'timestamp': datetime.now().isoformat()
        }
        
        # 4. 记录到记忆系统
        self._record_to_memory('task_status_change', change_record)
        
        # 5. 如果同步失败，添加到重试队列
        if not sync_result['sync_success']:
            self._schedule_retry(task_id, task_name, new_status, details)
        
        print("✅ 任务状态变化集成完成")
        return sync_result
    
    def communication_end_integration(self, communication_summary: str):
        """沟通结束集成"""
        print("🔄 沟通结束: 集成多维表格核心技能")
        
        # 1. 确保所有状态已同步
        print("  1. 确保所有状态已同步...")
        sync_result = self.core.sync_all_pending_tasks()
        
        pending_count = sync_result.get('pending', 0)
        if pending_count > 0:
            print(f"  ⚠️ 还有 {pending_count} 个任务待同步")
        else:
            print(f"  ✅ 所有任务已同步")
        
        # 2. 生成沟通摘要记录
        print("  2. 生成沟通摘要...")
        summary_record = {
            'summary': communication_summary,
            'sync_status': sync_result,
            'timestamp': datetime.now().isoformat(),
            'bitable_url': 'https://t33vwocwc8.feishu.cn/base/FCRNbSo4ja4hCEs5411cNZQXnkh'
        }
        
        # 3. 记录到多维表格（作为特殊任务）
        print("  3. 记录沟通摘要到多维表格...")
        task_id = f"COMM-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.core.sync_task_status(
            task_id=task_id,
            task_name='沟通摘要记录',
            status='已完成',
            details=communication_summary[:500]  # 限制长度
        )
        
        # 4. 记录到记忆系统
        self._record_to_memory('communication_end', summary_record)
        
        # 5. 生成技能报告
        print("  4. 生成技能报告...")
        report = self.core.generate_report()
        
        print(f"✅ 沟通结束集成完成")
        print(f"📊 技能报告:")
        print(f"   健康状态: {report['health']['overall_status']}")
        print(f"   任务统计: {report['statistics'].get('total_tasks', 0)} 个任务")
        print(f"   同步率: {report['statistics'].get('sync_rate', 0):.1f}%")
        print(f"   可用性: {report['metrics'].get('availability', 0):.1f}%")
        
        return summary_record
    
    def heartbeat_integration(self):
        """心跳集成（定期检查）"""
        print("💓 心跳检查: 多维表格核心技能")
        
        # 1. 健康检查
        health = self.core.check_health()
        
        # 2. 同步待处理任务
        sync_result = self.core.sync_all_pending_tasks()
        
        # 3. 生成心跳报告
        heartbeat_report = {
            'timestamp': datetime.now().isoformat(),
            'health': health['overall_status'],
            'sync_summary': {
                'total': sync_result.get('total', 0),
                'success': sync_result.get('success', 0),
                'failure': sync_result.get('failure', 0)
            },
            'metrics': {
                'availability': self.core._calculate_availability(),
                'error_count': self.core.health_status['error_count'],
                'success_count': self.core.health_status['success_count']
            }
        }
        
        # 4. 记录心跳
        self._record_to_memory('heartbeat', heartbeat_report)
        
        # 5. 如果状态不健康，告警
        if health['overall_status'] != 'healthy':
            print(f"🚨 心跳告警: 技能状态 {health['overall_status']}")
            self._send_alert(health)
        
        print(f"✅ 心跳检查完成: {health['overall_status']}")
        return heartbeat_report
    
    def _try_auto_fix(self, health_report: Dict):
        """尝试自动修复"""
        print("  🛠️ 尝试自动修复...")
        
        issues = []
        
        # 检查各个组件
        for component, status in health_report['components'].items():
            if not status['healthy']:
                issues.append((component, status['message']))
        
        for component, message in issues:
            print(f"    修复 {component}: {message}")
            
            if component == 'token':
                # 强制刷新token
                self.core.get_tenant_access_token(force_refresh=True)
            
            elif component == 'api':
                # 测试网络连接
                # 这里可以添加网络测试逻辑
                pass
            
            elif component == 'table':
                # 重新获取表格结构
                # 清除缓存，重新获取
                cache_file = self.core.cache_dir / "fields_mapping.json"
                if cache_file.exists():
                    cache_file.unlink()
            
            elif component == 'backup':
                # 重建本地数据库
                # 这里可以添加数据库重建逻辑
                pass
        
        # 重新检查健康状态
        print("  🔄 重新检查健康状态...")
        new_health = self.core.check_health()
        
        if new_health['overall_status'] == 'healthy':
            print("  ✅ 自动修复成功!")
        else:
            print(f"  ❌ 自动修复失败，状态: {new_health['overall_status']}")
    
    def _generate_session_summary(self, health_report: Dict, sync_result: Dict) -> Dict:
        """生成会话摘要"""
        return {
            'session_start': datetime.now().isoformat(),
            'skill_health': health_report['overall_status'],
            'pending_sync': sync_result.get('total', 0),
            'successful_sync': sync_result.get('success', 0),
            'environment': {
                'app_id': self.core.app_id[:8] + '...' if self.core.app_id else None,
                'base_token': self.core.base_app_token,
                'table_id': self.core.tasks_table_id
            }
        }
    
    def _record_to_memory(self, event_type: str, data: Dict):
        """记录到记忆系统"""
        memory_file = self.workspace / "memory" / f"{datetime.now().strftime('%Y-%m-%d')}.md"
        
        record = f"""
## 🔄 多维表格核心技能事件

### 事件类型
{event_type}

### 时间
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

### 数据
```json
{json.dumps(data, indent=2, ensure_ascii=False)}
```

---
"""
        
        try:
            with open(memory_file, 'a', encoding='utf-8') as f:
                f.write(record)
            print(f"  📝 已记录到记忆系统: {memory_file}")
        except Exception as e:
            print(f"  ⚠️ 记录到记忆系统失败: {e}")
    
    def _schedule_retry(self, task_id: str, task_name: str, status: str, details: str):
        """安排重试"""
        retry_file = self.core.cache_dir / "scheduled_retries.jsonl"
        
        retry_item = {
            'task_id': task_id,
            'task_name': task_name,
            'status': status,
            'details': details,
            'scheduled_time': time.time() + 300,  # 5分钟后重试
            'attempt_count': 1
        }
        
        with open(retry_file, 'a') as f:
            f.write(json.dumps(retry_item) + '\n')
        
        print(f"  ⏰ 已安排重试: {task_id} (5分钟后)")
    
    def _send_alert(self, health_report: Dict):
        """发送告警"""
        alert_file = self.core.cache_dir / "alerts.jsonl"
        
        alert = {
            'level': 'critical' if health_report['overall_status'] == 'critical' else 'warning',
            'component': 'bitable_core',
            'message': f"技能状态: {health_report['overall_status']}",
            'details': health_report,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(alert_file, 'a') as f:
            f.write(json.dumps(alert) + '\n')
        
        print(f"  🚨 已记录告警: {health_report['overall_status']}")

# 命令行接口
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='多维表格核心技能工作流程集成')
    parser.add_argument('--session-start', action='store_true', help='会话开始集成')
    parser.add_argument('--task-change', type=str, help='任务状态变化集成 (格式: id,name,old_status,new_status[,details])')
    parser.add_argument('--communication-end', type=str, help='沟通结束集成 (提供摘要)')
    parser.add_argument('--heartbeat', action='store_true', help='心跳集成')
    
    args = parser.parse_args()
    
    integrator = WorkflowIntegrator()
    
    if args.session_start:
        result = integrator.session_start_integration()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.task_change:
        parts = args.task_change.split(',', 4)
        if len(parts) >= 4:
            task_id = parts[0]
            task_name = parts[1]
            old_status = parts[2]
            new_status = parts[3]
            details = parts[4] if len(parts) > 4 else ""
            
            result = integrator.task_status_change_integration(
                task_id, task_name, old_status, new_status, details
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("错误: 格式应为 id,name,old_status,new_status[,details]")
    
    elif args.communication_end:
        result = integrator.communication_end_integration(args.communication_end)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.heartbeat:
        result = integrator.heartbeat_integration()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        # 默认运行会话开始
        result = integrator.session_start_integration()
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()