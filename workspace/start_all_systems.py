#!/usr/bin/env python3
"""
启动所有系统
1. 共享记忆库系统
2. 状态反馈系统
3. 状态API服务器
4. 同步当前任务到多维表格
"""

import time
import threading
import json
from datetime import datetime
from pathlib import Path
import logging
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/all_systems.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('all_systems')

class AllSystemsManager:
    """所有系统管理器"""
    
    def __init__(self):
        self.systems = {}
        self.running = False
        
        logger.info("所有系统管理器初始化")
    
    def start_shared_memory_system(self):
        """启动共享记忆库系统"""
        try:
            from shared_memory_system import SharedMemorySystem
            system = SharedMemorySystem()
            
            # 测试系统
            report = system.generate_system_report()
            
            self.systems['shared_memory'] = {
                'instance': system,
                'status': 'running',
                'report': report
            }
            
            logger.info("共享记忆库系统启动成功")
            return True
            
        except Exception as e:
            logger.error(f"启动共享记忆库系统失败: {e}")
            return False
    
    def start_status_feedback_system(self):
        """启动状态反馈系统"""
        try:
            from status_feedback_system import feedback_system
            
            # 启动心跳
            feedback_system.start_heartbeat()
            
            # 更新初始状态
            feedback_system.update_status(
                'working',
                '启动所有系统',
                10,
                '正在初始化系统...'
            )
            
            self.systems['status_feedback'] = {
                'instance': feedback_system,
                'status': 'running'
            }
            
            logger.info("状态反馈系统启动成功")
            return True
            
        except Exception as e:
            logger.error(f"启动状态反馈系统失败: {e}")
            return False
    
    def start_status_api_server(self):
        """启动状态API服务器"""
        try:
            from status_api_server import StatusAPIServer
            
            server = StatusAPIServer(host='0.0.0.0', port=8080)
            
            # 在后台线程中启动服务器
            def run_server():
                server.start()
                # 服务器会在后台运行
            
            api_thread = threading.Thread(target=run_server, daemon=True)
            api_thread.start()
            
            # 等待服务器启动
            time.sleep(2)
            
            self.systems['status_api'] = {
                'instance': server,
                'status': 'running',
                'thread': api_thread
            }
            
            logger.info("状态API服务器启动成功")
            return True
            
        except Exception as e:
            logger.error(f"启动状态API服务器失败: {e}")
            return False
    
    def sync_current_tasks(self):
        """同步当前任务到多维表格"""
        try:
            from shared_memory_system import SharedMemorySystem
            system = SharedMemorySystem()
            
            # 更新状态反馈
            from status_feedback_system import feedback_system
            feedback_system.update_status(
                'working',
                '同步任务状态',
                30,
                '正在同步当前任务到多维表格...'
            )
            
            # 定义当前任务
            current_tasks = [
                {
                    'id': 'TASK-20260302-1311',
                    'name': '建立状态反馈系统',
                    'status': '进行中',
                    'details': '创建状态监控机制，让你随时知道我的工作状态'
                },
                {
                    'id': 'TASK-20260302-1307',
                    'name': '实施共享记忆库系统',
                    'status': '进行中',
                    'details': '基于拿来主义思想，建立简化版共享记忆库'
                },
                {
                    'id': 'TASK-20260302-1159',
                    'name': '工作流程优化',
                    'status': '进行中',
                    'details': '优化任务状态管理和沟通流程'
                },
                {
                    'id': 'TASK-20260301-233530',
                    'name': '小红书技能安装',
                    'status': '等待指示',
                    'details': '等待确认是否继续安装小红书相关技能'
                },
                {
                    'id': 'TASK-20260301-234800',
                    'name': 'Agent团队建设',
                    'status': '等待指示',
                    'details': '等待确认是否继续Agent团队建设任务'
                }
            ]
            
            results = []
            for i, task in enumerate(current_tasks):
                # 更新进度
                progress = 30 + int((i + 1) / len(current_tasks) * 50)
                feedback_system.update_status(
                    'working',
                    '同步任务状态',
                    progress,
                    f'正在同步任务: {task["name"]}'
                )
                
                # 同步任务
                result = system.update_task_status(
                    task['id'],
                    task['name'],
                    task['status'],
                    task['details']
                )
                results.append(result)
                
                # 短暂延迟，避免API限流
                time.sleep(1)
            
            # 批量同步所有待处理任务
            sync_result = system.sync_all_pending_tasks()
            
            feedback_system.update_status(
                'working',
                '同步任务状态',
                90,
                f'任务同步完成: {sync_result.get("success", 0)}成功, {sync_result.get("failure", 0)}失败'
            )
            
            self.systems['task_sync'] = {
                'status': 'completed',
                'results': results,
                'sync_result': sync_result
            }
            
            logger.info(f"任务同步完成: {sync_result}")
            return True
            
        except Exception as e:
            logger.error(f"同步任务失败: {e}")
            
            # 更新错误状态
            from status_feedback_system import feedback_system
            feedback_system.update_status(
                'error',
                '同步任务状态',
                0,
                f'同步失败: {e}'
            )
            
            return False
    
    def start_all(self):
        """启动所有系统"""
        logger.info("开始启动所有系统...")
        
        # 更新状态
        from status_feedback_system import feedback_system
        feedback_system.update_status(
            'working',
            '启动所有系统',
            5,
            '开始初始化...'
        )
        
        # 1. 启动状态反馈系统
        feedback_system.update_status('working', '启动所有系统', 10, '启动状态反馈系统...')
        if not self.start_status_feedback_system():
            logger.error("状态反馈系统启动失败，继续其他系统")
        
        # 2. 启动共享记忆库系统
        feedback_system.update_status('working', '启动所有系统', 20, '启动共享记忆库系统...')
        if not self.start_shared_memory_system():
            logger.error("共享记忆库系统启动失败，继续其他系统")
        
        # 3. 启动状态API服务器
        feedback_system.update_status('working', '启动所有系统', 30, '启动状态API服务器...')
        if not self.start_status_api_server():
            logger.error("状态API服务器启动失败，继续其他系统")
        
        # 4. 同步任务
        feedback_system.update_status('working', '启动所有系统', 40, '同步任务到多维表格...')
        if not self.sync_current_tasks():
            logger.error("任务同步失败")
        
        # 5. 完成启动
        feedback_system.update_status(
            'completed',
            '启动所有系统',
            100,
            '所有系统启动完成！'
        )
        
        self.running = True
        
        # 生成启动报告
        report = self.generate_startup_report()
        
        logger.info("所有系统启动完成")
        logger.info(f"监控页面: http://localhost:8080/")
        logger.info(f"状态API: http://localhost:8080/api/agent-status")
        
        return report
    
    def generate_startup_report(self):
        """生成启动报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'systems': {},
            'status': 'running' if self.running else 'failed',
            'monitoring': {
                'web_ui': 'http://localhost:8080/',
                'api': 'http://localhost:8080/api/agent-status',
                'status_file': str(Path.home() / ".openclaw" / "workspace" / "agent_status.json")
            }
        }
        
        for name, info in self.systems.items():
            report['systems'][name] = {
                'status': info.get('status', 'unknown'),
                'running': 'instance' in info
            }
        
        # 保存报告
        report_file = Path.home() / ".openclaw" / "workspace" / "startup_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"启动报告已保存: {report_file}")
        return report
    
    def stop_all(self):
        """停止所有系统"""
        logger.info("停止所有系统...")
        
        # 停止状态反馈系统
        if 'status_feedback' in self.systems:
            try:
                self.systems['status_feedback']['instance'].stop_heartbeat()
                logger.info("状态反馈系统已停止")
            except:
                pass
        
        # 停止API服务器
        if 'status_api' in self.systems:
            try:
                self.systems['status_api']['instance'].stop()
                logger.info("状态API服务器已停止")
            except:
                pass
        
        self.running = False
        logger.info("所有系统已停止")
    
    def run_interactive(self):
        """交互式运行"""
        print("=" * 60)
        print("🤖 OpenClaw 所有系统管理器")
        print("=" * 60)
        print()
        
        print("即将启动以下系统:")
        print("1. ✅ 共享记忆库系统")
        print("2. ✅ 状态反馈系统（让你知道我的工作状态）")
        print("3. ✅ 状态API服务器（提供监控页面）")
        print("4. ✅ 多维表格任务同步")
        print()
        
        response = input("是否启动所有系统？ (y/n): ").strip().lower()
        
        if response != 'y':
            print("取消启动")
            return
        
        print()
        print("正在启动系统，请稍候...")
        print()
        
        # 启动所有系统
        report = self.start_all()
        
        print()
        print("=" * 60)
        print("🎉 所有系统启动完成！")
        print("=" * 60)
        print()
        
        print("📊 系统状态:")
        for name, info in report['systems'].items():
            status = info['status']
            emoji = '✅' if status == 'running' else '⚠️' if status == 'completed' else '❌'
            print(f"  {emoji} {name}: {status}")
        
        print()
        print("🌐 监控信息:")
        print(f"  监控页面: {report['monitoring']['web_ui']}")
        print(f"  状态API: {report['monitoring']['api']}")
        print(f"  状态文件: {report['monitoring']['status_file']}")
        print()
        
        print("📝 你现在可以:")
        print("  1. 打开监控页面查看我的实时状态")
        print("  2. 随时查看多维表格了解任务进度")
        print("  3. 我每30秒会发送心跳信号")
        print("  4. 长时间任务会有进度更新")
        print()
        
        print("按 Ctrl+C 停止所有系统")
        print()
        
        # 保持运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print()
            print("收到停止信号...")
            self.stop_all()
            print("所有系统已停止")
            print("再见！👋")

def main():
    """主函数"""
    manager = AllSystemsManager()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--daemon':
        # 守护进程模式
        manager.start_all()
        
        # 保持运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop_all()
    else:
        # 交互模式
        manager.run_interactive()

if __name__ == "__main__":
    main()