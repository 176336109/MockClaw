#!/usr/bin/env python3
"""
集成工作流
结合：session优化 + 状态反馈 + 多维表格同步
"""

import time
import threading
from datetime import datetime
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/integrated_workflow.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('integrated_workflow')

class IntegratedWorkflow:
    """集成工作流"""
    
    def __init__(self):
        self.workspace = Path.home() / ".openclaw" / "workspace"
        
        # 初始化所有系统
        self._init_systems()
        
        logger.info("集成工作流初始化完成")
    
    def _init_systems(self):
        """初始化所有系统"""
        try:
            # 1. Session优化器
            from session_optimizer import SessionOptimizer
            self.session_optimizer = SessionOptimizer()
            logger.info("Session优化器加载成功")
        except Exception as e:
            logger.error(f"加载Session优化器失败: {e}")
            self.session_optimizer = None
        
        try:
            # 2. 状态反馈系统
            from status_feedback_system import feedback_system
            self.feedback_system = feedback_system
            logger.info("状态反馈系统加载成功")
        except Exception as e:
            logger.error(f"加载状态反馈系统失败: {e}")
            self.feedback_system = None
        
        try:
            # 3. 多维表格核心
            from skills.bitable_core.bitable_core import BitableCore
            self.bitable_core = BitableCore()
            logger.info("多维表格核心加载成功")
        except Exception as e:
            logger.error(f"加载多维表格核心失败: {e}")
            self.bitable_core = None
        
        try:
            # 4. 共享记忆库
            from shared_memory_system import SharedMemorySystem
            self.memory_system = SharedMemorySystem()
            logger.info("共享记忆库加载成功")
        except Exception as e:
            logger.error(f"加载共享记忆库失败: {e}")
            self.memory_system = None
    
    def start_all(self):
        """启动所有系统"""
        logger.info("启动所有系统...")
        
        # 启动状态反馈心跳
        if self.feedback_system:
            self.feedback_system.start_heartbeat()
            self.feedback_system.update_status(
                'working',
                '启动集成工作流',
                10,
                '正在初始化所有系统...'
            )
        
        # 检查系统健康
        health_report = self.check_system_health()
        
        # 同步到多维表格
        if self.bitable_core and health_report['bitable']['healthy']:
            self.feedback_system.update_status('working', '启动集成工作流', 30, '同步系统状态到多维表格...')
            self._sync_system_status()
        
        # 生成报告
        self.feedback_system.update_status('working', '启动集成工作流', 50, '生成系统报告...')
        report = self.generate_system_report()
        
        # 完成启动
        self.feedback_system.update_status(
            'completed',
            '启动集成工作流',
            100,
            f'所有系统启动完成！消息数量: {report["session"]["message_count"]}'
        )
        
        logger.info("所有系统启动完成")
        return report
    
    def check_system_health(self) -> dict:
        """检查系统健康"""
        health = {
            'timestamp': datetime.now().isoformat(),
            'session': {'healthy': bool(self.session_optimizer), 'message': ''},
            'feedback': {'healthy': bool(self.feedback_system), 'message': ''},
            'bitable': {'healthy': bool(self.bitable_core), 'message': ''},
            'memory': {'healthy': bool(self.memory_system), 'message': ''},
            'overall': 'healthy'
        }
        
        # 检查bitable健康
        if self.bitable_core:
            try:
                bitable_health = self.bitable_core.check_health()
                health['bitable'].update({
                    'healthy': bitable_health['overall_status'] == 'healthy',
                    'status': bitable_health['overall_status'],
                    'details': bitable_health
                })
            except Exception as e:
                health['bitable'].update({
                    'healthy': False,
                    'message': f'健康检查失败: {e}'
                })
        
        # 计算整体健康
        unhealthy_count = sum(1 for sys in ['session', 'feedback', 'bitable', 'memory'] 
                            if not health[sys]['healthy'])
        
        if unhealthy_count == 0:
            health['overall'] = 'healthy'
        elif unhealthy_count <= 2:
            health['overall'] = 'degraded'
        else:
            health['overall'] = 'critical'
        
        return health
    
    def _sync_system_status(self):
        """同步系统状态到多维表格"""
        if not self.bitable_core:
            return
        
        tasks = [
            {
                'id': 'SYS-20260302-1400',
                'name': '集成工作流系统',
                'status': '进行中',
                'details': 'Session优化 + 状态反馈 + 多维表格同步'
            },
            {
                'id': 'SYS-20260302-1401',
                'name': '上下文压缩管理',
                'status': '进行中',
                'details': '安装context-engineering, memory-manager, summarizer技能'
            },
            {
                'id': 'SYS-20260302-1402',
                'name': '多维表格同步修复',
                'status': '完成',
                'details': '修复token和字段名问题，API恢复正常'
            }
        ]
        
        for task in tasks:
            try:
                result = self.bitable_core.sync_task_status(
                    task['id'],
                    task['name'],
                    task['status'],
                    task['details']
                )
                
                if result['sync_success']:
                    logger.info(f"系统状态同步成功: {task['name']}")
                else:
                    logger.error(f"系统状态同步失败: {task['name']} - {result.get('error')}")
            except Exception as e:
                logger.error(f"同步异常: {task['name']} - {e}")
    
    def generate_system_report(self) -> dict:
        """生成系统报告"""
        health = self.check_system_health()
        
        # 获取session信息
        session_info = {}
        if self.session_optimizer:
            session = self.session_optimizer.get_session()
            session_info = {
                'session_id': session.get('session_id'),
                'message_count': session.get('message_count', 0),
                'context_size_kb': round(session.get('context_size', 0) / 1024, 2),
                'compression_rate': session.get('compression_rate', 0)
            }
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'health': health,
            'session': session_info,
            'systems': {
                'session_optimizer': bool(self.session_optimizer),
                'status_feedback': bool(self.feedback_system),
                'bitable_core': bool(self.bitable_core),
                'memory_system': bool(self.memory_system)
            },
            'recommendations': self._generate_recommendations(health, session_info)
        }
        
        # 保存报告
        report_file = self.workspace / "integrated_system_report.json"
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"系统报告已保存: {report_file}")
        return report
    
    def _generate_recommendations(self, health: dict, session_info: dict) -> list:
        """生成优化建议"""
        recommendations = []
        
        # 健康建议
        if health['overall'] != 'healthy':
            recommendations.append(f"系统健康状态: {health['overall']}，需要检查")
        
        # Session建议
        if session_info.get('message_count', 0) > 10:
            recommendations.append(f"当前session有{session_info['message_count']}条消息，建议开启自动压缩")
        
        if session_info.get('context_size_kb', 0) > 100:
            recommendations.append(f"上下文大小{session_info['context_size_kb']}KB，建议使用摘要功能")
        
        # 功能建议
        if not self.bitable_core:
            recommendations.append("多维表格核心未加载，影响任务同步")
        
        if not self.feedback_system:
            recommendations.append("状态反馈系统未加载，影响状态监控")
        
        if not recommendations:
            recommendations.append("系统运行良好，建议定期检查健康状态")
        
        return recommendations
    
    def process_user_message(self, message: str) -> dict:
        """处理用户消息（集成处理）"""
        logger.info(f"处理用户消息: {message[:50]}...")
        
        # 1. 添加到session
        if self.session_optimizer:
            msg_id = self.session_optimizer.add_message('user', message)
        
        # 2. 更新状态
        if self.feedback_system:
            self.feedback_system.update_status(
                'working',
                '处理用户消息',
                20,
                f'处理: {message[:30]}...'
            )
        
        # 3. 保存到记忆库
        if self.memory_system:
            memory_id = self.memory_system.create_memory_item(
                title=f"用户消息: {message[:30]}...",
                content=message,
                content_type="user_message",
                metadata={'source': 'feishu', 'processed': False}
            )
        
        # 4. 同步到多维表格（如果是任务相关）
        if '任务' in message or 'TASK' in message:
            self._extract_and_sync_task(message)
        
        response = {
            'processed': True,
            'timestamp': datetime.now().isoformat(),
            'session_msg_id': msg_id if 'msg_id' in locals() else None,
            'memory_id': memory_id if 'memory_id' in locals() else None
        }
        
        return response
    
    def _extract_and_sync_task(self, message: str):
        """提取并同步任务信息"""
        if not self.bitable_core:
            return
        
        # 简单任务提取逻辑
        task_keywords = ['任务', 'TASK', '完成', '进行中', '等待指示', '搁置']
        
        if any(keyword in message for keyword in task_keywords):
            # 提取任务ID（简单实现）
            import re
            task_id_match = re.search(r'TASK-\d{8}-\d+', message)
            
            if task_id_match:
                task_id = task_id_match.group()
                task_status = '进行中'  # 默认
                
                if '完成' in message:
                    task_status = '完成'
                elif '等待' in message:
                    task_status = '等待指示'
                elif '搁置' in message:
                    task_status = '搁置'
                
                # 同步到多维表格
                try:
                    result = self.bitable_core.sync_task_status(
                        task_id,
                        f"从消息提取的任务: {task_id}",
                        task_status,
                        f"从用户消息提取: {message[:100]}..."
                    )
                    
                    if result['sync_success']:
                        logger.info(f"任务提取同步成功: {task_id}")
                except Exception as e:
                    logger.error(f"任务提取同步失败: {e}")
    
    def run_interactive(self):
        """交互式运行"""
        print("=" * 60)
        print("🤖 集成工作流系统")
        print("=" * 60)
        print()
        
        print("系统组件:")
        print(f"  ✅ Session优化器: {'已加载' if self.session_optimizer else '未加载'}")
        print(f"  ✅ 状态反馈系统: {'已加载' if self.feedback_system else '未加载'}")
        print(f"  ✅ 多维表格核心: {'已加载' if self.bitable_core else '未加载'}")
        print(f"  ✅ 共享记忆库: {'已加载' if self.memory_system else '未加载'}")
        print()
        
        print("即将启动集成工作流...")
        response = input("是否启动？ (y/n): ").strip().lower()
        
        if response != 'y':
            print("取消启动")
            return
        
        print()
        print("启动中，请稍候...")
        print()
        
        # 启动所有系统
        report = self.start_all()
        
        print()
        print("=" * 60)
        print("🎉 集成工作流启动完成！")
        print("=" * 60)
        print()
        
        print("📊 系统状态:")
        print(f"  整体健康: {report['health']['overall']}")
        print(f"  Session消息: {report['session'].get('message_count', 0)}条")
        print(f"  上下文大小: {report['session'].get('context_size_kb', 0)}KB")
        print(f"  压缩率: {report['session'].get('compression_rate', 0)}%")
        print()
        
        print("💡 优化建议:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
        print()
        
        print("🌐 监控信息:")
        print("  状态监控: http://localhost:8080/ (如果API服务器运行)")
        print("  多维表格: https://t33vwocwc8.feishu.cn/base/FCRNbSo4ja4hCEs5411cNZQXnkh")
        print()
        
        print("📝 你现在可以:")
        print("  1. 连续对话，系统会自动管理上下文")
        print("  2. 随时查看我的工作状态")
        print("  3. 任务状态自动同步到多维表格")
        print("  4. 长时间任务会有进度反馈")
        print()
        
        print("按 Ctrl+C 停止系统")
        print()
        
        # 保持运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print()
            print("收到停止信号...")
            if self.feedback_system:
                self.feedback_system.update_status('completed', '集成工作流', 100, '系统正常停止')
            print("系统已停止")
            print("再见！👋")

def main():
    """主函数"""
    workflow = IntegratedWorkflow()
    workflow.run_interactive()

if __name__ == "__main__":
    main()