#!/usr/bin/env python3
"""
状态API服务器
提供Agent状态信息的HTTP API
"""

import json
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import threading
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/status_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('status_api')

class StatusAPIHandler(BaseHTTPRequestHandler):
    """状态API处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        try:
            if self.path == '/api/agent-status':
                self._handle_agent_status()
            elif self.path == '/api/health':
                self._handle_health()
            elif self.path == '/api/tasks':
                self._handle_tasks()
            elif self.path == '/':
                self._handle_index()
            else:
                self.send_error(404, "Not Found")
                
        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            self.send_error(500, f"Internal Server Error: {e}")
    
    def _handle_agent_status(self):
        """处理Agent状态请求"""
        status_data = self._get_agent_status()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(status_data, ensure_ascii=False).encode('utf-8'))
    
    def _handle_health(self):
        """处理健康检查"""
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'agent_status_api',
            'version': '1.0.0'
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(health_data).encode('utf-8'))
    
    def _handle_tasks(self):
        """处理任务列表请求"""
        # 从共享记忆库获取任务数据
        try:
            from shared_memory_system import SharedMemorySystem
            system = SharedMemorySystem()
            report = system.generate_system_report()
            
            tasks_data = {
                'tasks': report.get('recent_activity', {}).get('recent_tasks', []),
                'total': report.get('statistics', {}).get('total_tasks', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(tasks_data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            logger.error(f"获取任务数据失败: {e}")
            self.send_error(500, f"Failed to get tasks: {e}")
    
    def _handle_index(self):
        """处理首页请求（返回监控页面）"""
        try:
            # 读取HTML文件
            html_path = Path.home() / ".openclaw" / "workspace" / "status_monitor.html"
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            
        except Exception as e:
            logger.error(f"读取HTML文件失败: {e}")
            self.send_error(500, f"Failed to load page: {e}")
    
    def _get_agent_status(self):
        """获取Agent状态"""
        status_file = Path.home() / ".openclaw" / "workspace" / "agent_status.json"
        
        try:
            if status_file.exists():
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
            else:
                status_data = {
                    'agent_id': 'main',
                    'status': 'unknown',
                    'current_task': None,
                    'progress': 0,
                    'last_heartbeat': None,
                    'start_time': datetime.now().isoformat(),
                    'message': '状态文件不存在'
                }
            
            # 添加API特定信息
            status_data.update({
                'api_timestamp': datetime.now().isoformat(),
                'api_version': '1.0.0',
                'request_path': self.path
            })
            
            return status_data
            
        except Exception as e:
            logger.error(f"读取状态文件失败: {e}")
            return {
                'agent_id': 'main',
                'status': 'error',
                'message': f'读取状态失败: {e}',
                'api_timestamp': datetime.now().isoformat()
            }
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        logger.info(f"{self.address_string()} - {format % args}")

class StatusAPIServer:
    """状态API服务器"""
    
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
        
        logger.info(f"状态API服务器初始化: {host}:{port}")
    
    def start(self):
        """启动服务器"""
        try:
            self.server = HTTPServer((self.host, self.port), StatusAPIHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            logger.info(f"状态API服务器已启动: http://{self.host}:{self.port}")
            logger.info(f"监控页面: http://{self.host}:{self.port}/")
            logger.info(f"状态API: http://{self.host}:{self.port}/api/agent-status")
            
            return True
            
        except Exception as e:
            logger.error(f"启动服务器失败: {e}")
            return False
    
    def stop(self):
        """停止服务器"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("状态API服务器已停止")
    
    def is_running(self):
        """检查服务器是否运行"""
        return self.server_thread and self.server_thread.is_alive()

def start_status_api():
    """启动状态API服务"""
    server = StatusAPIServer(host='0.0.0.0', port=8080)
    
    if server.start():
        logger.info("状态API服务启动成功")
        
        # 保持主线程运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("收到中断信号，停止服务器...")
            server.stop()
    else:
        logger.error("状态API服务启动失败")

if __name__ == "__main__":
    start_status_api()