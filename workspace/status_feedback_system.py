#!/usr/bin/env python3
"""
状态反馈系统
让你随时知道我的工作状态
"""

import time
import threading
import json
from datetime import datetime
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/status_feedback.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('status_feedback')

class StatusFeedbackSystem:
    """状态反馈系统"""
    
    def __init__(self):
        self.status_file = Path.home() / ".openclaw" / "workspace" / "agent_status.json"
        self.heartbeat_interval = 30  # 秒
        self.heartbeat_thread = None
        self.running = False
        
        # 初始化状态文件
        self._init_status_file()
        
        logger.info("状态反馈系统初始化完成")
    
    def _init_status_file(self):
        """初始化状态文件"""
        initial_status = {
            'agent_id': 'main',
            'status': 'idle',
            'current_task': None,
            'progress': 0,
            'last_heartbeat': None,
            'start_time': datetime.now().isoformat(),
            'message': '系统就绪',
            'tasks': []
        }
        
        self._save_status(initial_status)
    
    def _save_status(self, status_data: dict):
        """保存状态到文件"""
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存状态失败: {e}")
    
    def get_status(self) -> dict:
        """获取当前状态"""
        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'status': 'unknown', 'message': '无法读取状态文件'}
    
    def update_status(self, status: str, task: str = None, progress: int = 0, message: str = ""):
        """更新状态"""
        current = self.get_status()
        
        # 如果是新任务，添加到任务列表
        if task and task != current.get('current_task'):
            task_record = {
                'task': task,
                'start_time': datetime.now().isoformat(),
                'status': 'started',
                'progress': progress
            }
            current['tasks'].append(task_record)
        
        # 更新状态
        current.update({
            'status': status,
            'current_task': task,
            'progress': progress,
            'last_update': datetime.now().isoformat(),
            'message': message or f"状态: {status}, 进度: {progress}%"
        })
        
        self._save_status(current)
        
        # 如果是重要状态变化，发送通知
        if status in ['error', 'completed', 'blocked']:
            self._send_notification(status, task, message)
        
        logger.info(f"状态更新: {status} - {task} ({progress}%)")
    
    def _send_notification(self, status: str, task: str, message: str):
        """发送通知（可以扩展为飞书消息）"""
        # 这里可以集成飞书消息发送
        notification = {
            'type': 'status_change',
            'status': status,
            'task': task,
            'message': message,
            'time': datetime.now().isoformat()
        }
        
        # 保存到通知文件
        notification_file = Path.home() / ".openclaw" / "workspace" / "notifications.jsonl"
        with open(notification_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(notification, ensure_ascii=False) + '\n')
        
        logger.info(f"通知已保存: {status} - {task}")
    
    def start_heartbeat(self):
        """开始心跳"""
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            logger.warning("心跳线程已在运行")
            return
        
        self.running = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_worker, daemon=True)
        self.heartbeat_thread.start()
        logger.info("心跳线程已启动")
    
    def stop_heartbeat(self):
        """停止心跳"""
        self.running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=5)
            logger.info("心跳线程已停止")
    
    def _heartbeat_worker(self):
        """心跳工作线程"""
        logger.info("心跳工作线程开始运行")
        
        while self.running:
            try:
                # 更新心跳时间
                current = self.get_status()
                current['last_heartbeat'] = datetime.now().isoformat()
                current['uptime'] = int(time.time() - datetime.fromisoformat(current['start_time']).timestamp())
                self._save_status(current)
                
                # 检查是否卡死（超过2分钟无心跳）
                self._check_stuck()
                
                # 等待下一次心跳
                time.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"心跳工作线程异常: {e}")
                time.sleep(5)
        
        logger.info("心跳工作线程结束")
    
    def _check_stuck(self):
        """检查是否卡死"""
        current = self.get_status()
        
        if current.get('last_heartbeat'):
            last_heartbeat = datetime.fromisoformat(current['last_heartbeat'])
            now = datetime.now()
            
            # 如果超过2分钟无心跳，标记为可能卡死
            if (now - last_heartbeat).total_seconds() > 120:
                logger.warning(f"可能卡死: 最后心跳 {last_heartbeat.isoformat()}")
                
                # 更新状态为警告
                current['status'] = 'warning'
                current['message'] = f'可能卡死，最后心跳: {last_heartbeat.isoformat()}'
                self._save_status(current)
    
    def run_task_with_feedback(self, task_name: str, task_func, *args, **kwargs):
        """运行任务并提供反馈"""
        logger.info(f"开始运行任务: {task_name}")
        
        # 更新状态为开始
        self.update_status('working', task_name, 0, f"开始任务: {task_name}")
        
        try:
            # 运行任务
            result = task_func(*args, **kwargs)
            
            # 更新状态为完成
            self.update_status('completed', task_name, 100, f"任务完成: {task_name}")
            
            logger.info(f"任务完成: {task_name}")
            return result
            
        except Exception as e:
            # 更新状态为错误
            self.update_status('error', task_name, 0, f"任务失败: {str(e)}")
            
            logger.error(f"任务失败: {task_name} - {e}")
            raise
    
    def create_progress_tracker(self, total_steps: int, task_name: str):
        """创建进度跟踪器"""
        class ProgressTracker:
            def __init__(self, feedback_system, total_steps, task_name):
                self.feedback = feedback_system
                self.total_steps = total_steps
                self.task_name = task_name
                self.current_step = 0
            
            def step(self, message: str = ""):
                """完成一个步骤"""
                self.current_step += 1
                progress = int((self.current_step / self.total_steps) * 100)
                
                self.feedback.update_status(
                    'working',
                    self.task_name,
                    progress,
                    f"{message} ({self.current_step}/{self.total_steps})"
                )
                
                logger.info(f"进度更新: {self.task_name} - {progress}% - {message}")
            
            def complete(self, message: str = "任务完成"):
                """标记任务完成"""
                self.feedback.update_status('completed', self.task_name, 100, message)
        
        return ProgressTracker(self, total_steps, task_name)

# 全局实例
feedback_system = StatusFeedbackSystem()

# 装饰器：为函数添加状态反馈
def with_status_feedback(task_name: str):
    """状态反馈装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            return feedback_system.run_task_with_feedback(task_name, func, *args, **kwargs)
        return wrapper
    return decorator

# 示例使用
if __name__ == "__main__":
    import sys
    
    # 启动心跳
    feedback_system.start_heartbeat()
    
    # 命令行接口
    if len(sys.argv) > 1:
        if sys.argv[1] == 'status':
            status = feedback_system.get_status()
            print(json.dumps(status, indent=2, ensure_ascii=False))
        
        elif sys.argv[1] == 'update':
            if len(sys.argv) >= 3:
                status = sys.argv[2]
                task = sys.argv[3] if len(sys.argv) > 3 else None
                progress = int(sys.argv[4]) if len(sys.argv) > 4 else 0
                message = sys.argv[5] if len(sys.argv) > 5 else ""
                
                feedback_system.update_status(status, task, progress, message)
                print(f"状态已更新: {status}")
            else:
                print("用法: python status_feedback_system.py update <status> [task] [progress] [message]")
        
        elif sys.argv[1] == 'test':
            # 测试任务
            @with_status_feedback("测试任务")
            def test_task():
                time.sleep(5)
                return "测试完成"
            
            result = test_task()
            print(f"测试结果: {result}")
        
        else:
            print("可用命令: status, update, test")
    else:
        # 显示当前状态
        status = feedback_system.get_status()
        print("状态反馈系统运行中")
        print(f"当前状态: {status['status']}")
        print(f"当前任务: {status.get('current_task', '无')}")
        print(f"进度: {status.get('progress', 0)}%")
        print(f"最后心跳: {status.get('last_heartbeat', '无')}")
        print(f"消息: {status.get('message', '')}")
    
    # 保持运行（如果是主程序）
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        feedback_system.stop_heartbeat()
        print("\n系统已停止")