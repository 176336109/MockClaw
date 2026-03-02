#!/usr/bin/env python3
"""
共享记忆库系统 - 简化版
结合拿来主义思想，去其糟粕，取其精华
"""

import os
import json
import yaml
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/shared_memory.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('shared_memory')

class SharedMemorySystem:
    """共享记忆库系统"""
    
    def __init__(self):
        self.base_path = Path.home() / "Documents" / "shared_memory"
        self.workspace_path = Path.home() / ".openclaw" / "workspace" / "shared_memory"
        
        # 确保目录存在
        self._ensure_directories()
        
        # 初始化数据库
        self.db_path = self.base_path / "memory.db"
        self._init_database()
        
        logger.info(f"共享记忆库系统初始化完成: {self.base_path}")
    
    def _ensure_directories(self):
        """确保目录结构"""
        directories = [
            self.base_path / "input",           # 输入层
            self.base_path / "processing",      # 处理层  
            self.base_path / "output",          # 输出层
            self.base_path / "archive",         # 归档层
            self.base_path / "backup",          # 备份层
            self.base_path / "logs"             # 日志层
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"确保目录存在: {directory}")
    
    def _init_database(self):
        """初始化数据库"""
        import sqlite3
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 记忆条目表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                content_type TEXT NOT NULL,
                content TEXT,
                metadata_json TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                checksum TEXT NOT NULL
            )
        ''')
        
        # 任务状态表（专门用于多维表格同步）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_sync_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                task_name TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                bitable_sync_status TEXT DEFAULT 'pending',
                bitable_sync_time TIMESTAMP,
                bitable_record_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 操作日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                target_id TEXT,
                details TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_items_status ON memory_items(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_sync_status ON task_sync_status(status, bitable_sync_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_operation_logs_time ON operation_logs(created_at)')
        
        conn.commit()
        conn.close()
        
        logger.info("数据库初始化完成")
    
    # ==================== 简化元数据系统 ====================
    
    def create_memory_item(self, title: str, content: str, content_type: str = "note", 
                          metadata: Dict = None) -> str:
        """创建记忆条目（简化元数据）"""
        # 生成唯一ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        item_id = f"{content_type}_{timestamp}_{hashlib.md5(title.encode()).hexdigest()[:8]}"
        
        # 简化元数据（只保留必要字段）
        simplified_metadata = {
            'type': content_type,
            'status': 'active',
            'created': datetime.now().isoformat(),
            'title': title
        }
        
        # 添加可选字段
        if metadata:
            # 只保留安全的可选字段
            allowed_fields = ['tags', 'author', 'priority', 'category', 'source']
            for field in allowed_fields:
                if field in metadata:
                    simplified_metadata[field] = metadata[field]
        
        # 计算校验和
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # 保存到数据库
        import sqlite3
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO memory_items 
            (item_id, title, content_type, content, metadata_json, checksum)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            item_id,
            title,
            content_type,
            content,
            json.dumps(simplified_metadata, ensure_ascii=False),
            content_hash
        ))
        
        conn.commit()
        conn.close()
        
        # 保存到文件（备份）
        self._save_to_file(item_id, title, content, simplified_metadata)
        
        # 记录操作日志
        self._log_operation('create_memory_item', item_id, 'success')
        
        logger.info(f"创建记忆条目: {item_id} - {title}")
        return item_id
    
    def _save_to_file(self, item_id: str, title: str, content: str, metadata: Dict):
        """保存到文件系统"""
        # 根据类型选择目录
        content_type = metadata.get('type', 'note')
        if content_type in ['task', 'project']:
            directory = self.base_path / "processing"
        elif content_type in ['insight', 'lesson']:
            directory = self.base_path / "output"
        else:
            directory = self.base_path / "input"
        
        # 创建文件
        file_path = directory / f"{item_id}.md"
        
        # 写入YAML元数据和内容
        with open(file_path, 'w', encoding='utf-8') as f:
            # YAML元数据
            f.write("---\n")
            yaml.dump(metadata, f, allow_unicode=True, default_flow_style=False)
            f.write("---\n\n")
            
            # 内容
            f.write(f"# {title}\n\n")
            f.write(content)
        
        logger.debug(f"保存到文件: {file_path}")
    
    # ==================== 任务状态管理（多维表格同步） ====================
    
    def update_task_status(self, task_id: str, task_name: str, status: str, details: str = "") -> Dict:
        """更新任务状态（必须同步到多维表格）"""
        logger.info(f"更新任务状态: {task_id} -> {status}")
        
        # 1. 保存到本地数据库
        local_result = self._save_task_to_db(task_id, task_name, status, details)
        
        # 2. 立即同步到多维表格（这是沟通生命线！）
        bitable_result = self._sync_to_bitable(task_id, task_name, status, details)
        
        # 3. 更新同步状态
        self._update_sync_status(task_id, bitable_result['success'])
        
        # 4. 记录到共享记忆库
        memory_content = f"""
任务ID: {task_id}
任务名称: {task_name}
状态: {status}
更新时间: {datetime.now().isoformat()}

详情:
{details}

同步状态: {'成功' if bitable_result['success'] else '失败'}
同步时间: {datetime.now().isoformat()}
"""
        
        memory_id = self.create_memory_item(
            title=f"任务状态更新: {task_name}",
            content=memory_content,
            content_type="task_status",
            metadata={
                'task_id': task_id,
                'status': status,
                'sync_success': bitable_result['success']
            }
        )
        
        result = {
            'task_id': task_id,
            'status': status,
            'local_success': local_result['success'],
            'bitable_sync_success': bitable_result['success'],
            'memory_id': memory_id,
            'timestamp': datetime.now().isoformat(),
            'error': bitable_result.get('error')
        }
        
        if bitable_result['success']:
            logger.info(f"任务状态同步成功: {task_id}")
        else:
            logger.error(f"任务状态同步失败: {task_id} - {bitable_result.get('error')}")
        
        return result
    
    def _save_task_to_db(self, task_id: str, task_name: str, status: str, details: str) -> Dict:
        """保存任务到数据库"""
        import sqlite3
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # 检查是否已存在
            cursor.execute("SELECT id FROM task_sync_status WHERE task_id = ?", (task_id,))
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有记录
                cursor.execute('''
                    UPDATE task_sync_status 
                    SET task_name = ?, status = ?, details = ?, 
                        bitable_sync_status = 'pending', updated_at = CURRENT_TIMESTAMP
                    WHERE task_id = ?
                ''', (task_name, status, details, task_id))
                action = 'updated'
            else:
                # 插入新记录
                cursor.execute('''
                    INSERT INTO task_sync_status 
                    (task_id, task_name, status, details)
                    VALUES (?, ?, ?, ?)
                ''', (task_id, task_name, status, details))
                action = 'inserted'
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'action': action}
            
        except Exception as e:
            logger.error(f"保存任务到数据库失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _sync_to_bitable(self, task_id: str, task_name: str, status: str, details: str, max_retries: int = 3) -> Dict:
        """同步到多维表格（带重试）"""
        logger.info(f"开始同步到多维表格: {task_id}")
        
        # 导入多维表格核心技能
        try:
            # 添加技能目录到路径
            skill_dir = Path.home() / ".openclaw" / "workspace" / "skills" / "bitable-core"
            import sys
            sys.path.insert(0, str(skill_dir))
            
            from bitable_core import BitableCore
            
            core = BitableCore()
            result = core.sync_task_status(task_id, task_name, status, details)
            
            return {
                'success': result['sync_success'],
                'error': result.get('error'),
                'retry_count': result.get('retry_count', 0)
            }
            
        except Exception as e:
            logger.error(f"导入多维表格技能失败: {e}")
            
            # 备用方案：直接调用API
            return self._direct_bitable_sync(task_id, task_name, status, details, max_retries)
    
    def _direct_bitable_sync(self, task_id: str, task_name: str, status: str, details: str, max_retries: int) -> Dict:
        """直接调用API同步（备用方案）"""
        import requests
        import json as json_module
        
        # 从配置文件获取token
        config_path = Path.home() / ".openclaw" / "openclaw.json"
        try:
            with open(config_path, 'r') as f:
                config = json_module.load(f)
            
            app_id = config.get('channels', {}).get('feishu', {}).get('accounts', {}).get('main', {}).get('appId')
            app_secret = config.get('channels', {}).get('feishu', {}).get('accounts', {}).get('main', {}).get('appSecret')
            
            if not app_id or not app_secret:
                return {'success': False, 'error': '未找到飞书配置'}
            
            # 获取token
            token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            token_data = {"app_id": app_id, "app_secret": app_secret}
            
            token_response = requests.post(token_url, json=token_data, timeout=10)
            token_result = token_response.json()
            
            if token_result.get("code") != 0:
                return {'success': False, 'error': f"获取token失败: {token_result.get('msg')}"}
            
            token = token_result.get("tenant_access_token")
            
            # 准备数据
            current_ts = int(time.time() * 1000)
            record_data = {
                "fields": {
                    "文本": f"任务状态更新: {task_name}",
                    "任务ID": task_id,
                    "任务名称": task_name,
                    "状态": status,
                    "描述": details[:500],  # 限制长度
                    "最后更新时间": current_ts,
                    "负责人": "OpenClaw主Agent"
                }
            }
            
            # 调用API
            app_token = "FCRNbSo4ja4hCEs5411cNZQXnkh"
            table_id = "tblRmMB6LIdLHyEt"
            url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            for attempt in range(max_retries):
                try:
                    response = requests.post(url, headers=headers, json=record_data, timeout=10)
                    result = response.json()
                    
                    if result.get("code") == 0:
                        logger.info(f"直接API同步成功: {task_id}")
                        return {'success': True, 'retry_count': attempt}
                    else:
                        logger.warning(f"直接API同步失败，尝试 {attempt + 1}/{max_retries}: {result.get('msg')}")
                        
                except Exception as e:
                    logger.error(f"直接API同步异常: {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
            
            return {'success': False, 'error': '所有重试都失败', 'retry_count': max_retries}
            
        except Exception as e:
            logger.error(f"直接API同步配置失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _update_sync_status(self, task_id: str, success: bool):
        """更新同步状态"""
        import sqlite3
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            sync_status = 'success' if success else 'failed'
            sync_time = datetime.now().isoformat() if success else None
            
            cursor.execute('''
                UPDATE task_sync_status 
                SET bitable_sync_status = ?, bitable_sync_time = ?
                WHERE task_id = ?
            ''', (sync_status, sync_time, task_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"更新同步状态失败: {e}")
    
    def _log_operation(self, operation_type: str, target_id: str = None, status: str = "success", details: str = ""):
        """记录操作日志"""
        import sqlite3
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO operation_logs 
                (operation_type, target_id, details, status)
                VALUES (?, ?, ?, ?)
            ''', (operation_type, target_id, details, status))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"记录操作日志失败: {e}")
    
    # ==================== 安全操作护栏 ====================
    
    def safe_file_operation(self, operation: str, source: str, target: str = None) -> Dict:
        """安全文件操作（操作护栏）"""
        logger.info(f"安全文件操作: {operation} {source} -> {target}")
        
        # 1. 验证路径安全性
        if not self._is_safe_path(source) or (target and not self._is_safe_path(target)):
            error_msg = "路径不在允许范围内"
            logger.error(f"路径安全检查失败: {error_msg}")
            self._log_operation('safe_file_operation', None, 'failed', error_msg)
            return {'success': False, 'error': error_msg}
        
        # 2. 检查文件类型
        if not self._is_allowed_file_type(source):
            error_msg = "文件类型不允许"
            logger.error(f"文件类型检查失败: {error_msg}")
            self._log_operation('safe_file_operation', source, 'failed', error_msg)
            return {'success': False, 'error': error_msg}
        
        # 3. 执行操作
        try:
            if operation == 'move':
                if not target:
                    return {'success': False, 'error': '移动操作需要目标路径'}
                
                # 备份源文件
                backup_path = self._create_backup(source)
                
                # 执行移动
                import shutil
                shutil.move(source, target)
                
                # 记录操作
                self._log_operation('file_move', source, 'success', f"{source} -> {target}")
                
                return {
                    'success': True,
                    'operation': 'move',
                    'source': source,
                    'target': target,
                    'backup': backup_path
                }
            
            elif operation == 'delete':
                # 备份文件
                backup_path = self._create_backup(source)
                
                # 执行删除
                os.remove(source)
                
                # 记录操作
                self._log_operation('file_delete', source, 'success', f"已删除，备份在: {backup_path}")
                
                return {
                    'success': True,
                    'operation': 'delete',
                    'source': source,
                    'backup': backup_path
                }
            
            elif operation == 'copy':
                if not target:
                    return {'success': False, 'error': '复制操作需要目标路径'}
                
                import shutil
                shutil.copy2(source, target)
                
                self._log_operation('file_copy', source, 'success', f"{source} -> {target}")
                
                return {
                    'success': True,
                    'operation': 'copy',
                    'source': source,
                    'target': target
                }
            
            else:
                return {'success': False, 'error': f'不支持的操作: {operation}'}
                
        except Exception as e:
            error_msg = f"文件操作失败: {e}"
            logger.error(error_msg)
            self._log_operation('safe_file_operation', source, 'failed', error_msg)
            return {'success': False, 'error': error_msg}
    
    def _is_safe_path(self, path: str) -> bool:
        """检查路径是否安全"""
        # 允许的路径前缀
        allowed_prefixes = [
            str(self.base_path),
            str(self.workspace_path),
            str(Path.home() / ".openclaw" / "workspace"),
            str(Path.home() / "Documents" / "shared_memory")
        ]
        
        path = os.path.abspath(path)
        
        for prefix in allowed_prefixes:
            if path.startswith(prefix):
                return True
        
        return False
    
    def _is_allowed_file_type(self, path: str) -> bool:
        """检查文件类型是否允许"""
        allowed_extensions = ['.md', '.txt', '.json', '.yaml', '.yml', '.csv']
        
        _, ext = os.path.splitext(path)
        return ext.lower() in allowed_extensions
    
    def _create_backup(self, source_path: str) -> str:
        """创建备份"""
        import shutil
        from datetime import datetime
        
        # 备份目录
        backup_dir = self.base_path / "backup" / datetime.now().strftime('%Y%m%d')
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 备份文件名
        filename = os.path.basename(source_path)
        timestamp = datetime.now().strftime('%H%M%S')
        backup_filename = f"{filename}.{timestamp}.bak"
        backup_path = backup_dir / backup_filename
        
        # 执行备份
        shutil.copy2(source_path, backup_path)
        
        logger.debug(f"创建备份: {source_path} -> {backup_path}")
        return str(backup_path)
    
    # ==================== 批量同步任务状态 ====================
    
    def sync_all_pending_tasks(self) -> Dict:
        """同步所有待处理任务到多维表格"""
        import sqlite3
        
        logger.info("开始批量同步任务状态到多维表格")
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # 获取所有待同步任务
            cursor.execute('''
                SELECT task_id, task_name, status, details 
                FROM task_sync_status 
                WHERE bitable_sync_status = 'pending' OR bitable_sync_status = 'failed'
                ORDER BY updated_at ASC
            ''')
            
            pending_tasks = cursor.fetchall()
            conn.close()
            
            results = []
            success_count = 0
            failure_count = 0
            
            for task in pending_tasks:
                task_id, task_name, status, details = task
                result = self.update_task_status(task_id, task_name, status, details)
                results.append(result)
                
                if result['bitable_sync_success']:
                    success_count += 1
                else:
                    failure_count += 1
            
            summary = {
                'total': len(pending_tasks),
                'success': success_count,
                'failure': failure_count,
                'success_rate': (success_count / len(pending_tasks) * 100) if pending_tasks else 100,
                'timestamp': datetime.now().isoformat(),
                'results': results
            }
            
            logger.info(f"批量同步完成: {summary}")
            
            # 记录批量同步结果
            self.create_memory_item(
                title="批量任务状态同步报告",
                content=json.dumps(summary, indent=2, ensure_ascii=False),
                content_type="sync_report",
                metadata={
                    'total_tasks': len(pending_tasks),
                    'success_count': success_count,
                    'failure_count': failure_count
                }
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"批量同步失败: {e}")
            return {'error': str(e), 'total': 0, 'success': 0, 'failure': 0}
    
    # ==================== 系统状态报告 ====================
    
    def generate_system_report(self) -> Dict:
        """生成系统状态报告"""
        import sqlite3
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # 统计信息
            cursor.execute("SELECT COUNT(*) FROM memory_items WHERE status = 'active'")
            memory_items_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM task_sync_status")
            total_tasks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM task_sync_status WHERE bitable_sync_status = 'success'")
            synced_tasks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM task_sync_status WHERE bitable_sync_status = 'pending'")
            pending_tasks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM task_sync_status WHERE bitable_sync_status = 'failed'")
            failed_tasks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM operation_logs")
            total_logs = cursor.fetchone()[0]
            
            conn.close()
            
            # 计算同步率
            sync_rate = (synced_tasks / total_tasks * 100) if total_tasks > 0 else 100
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'system': 'shared_memory_system',
                'directories': {
                    'base_path': str(self.base_path),
                    'workspace_path': str(self.workspace_path),
                    'exists': os.path.exists(self.workspace_path)
                },
                'statistics': {
                    'memory_items': memory_items_count,
                    'total_tasks': total_tasks,
                    'synced_tasks': synced_tasks,
                    'pending_tasks': pending_tasks,
                    'failed_tasks': failed_tasks,
                    'sync_rate': round(sync_rate, 2),
                    'operation_logs': total_logs
                },
                'health': {
                    'database': os.path.exists(self.db_path),
                    'directories': all(os.path.exists(self.base_path / d) for d in ['input', 'processing', 'output', 'archive']),
                    'bitable_connection': '待测试'  # 需要实际测试
                },
                'recent_activity': self._get_recent_activity()
            }
            
            # 保存报告
            report_file = self.base_path / "logs" / f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"系统报告生成完成: {report_file}")
            return report
            
        except Exception as e:
            logger.error(f"生成系统报告失败: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _get_recent_activity(self) -> Dict:
        """获取最近活动"""
        import sqlite3
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # 最近任务
            cursor.execute('''
                SELECT task_id, task_name, status, updated_at 
                FROM task_sync_status 
                ORDER BY updated_at DESC LIMIT 5
            ''')
            recent_tasks = cursor.fetchall()
            
            # 最近操作
            cursor.execute('''
                SELECT operation_type, target_id, status, created_at 
                FROM operation_logs 
                ORDER BY created_at DESC LIMIT 5
            ''')
            recent_operations = cursor.fetchall()
            
            conn.close()
            
            return {
                'recent_tasks': [
                    {'task_id': t[0], 'task_name': t[1], 'status': t[2], 'updated_at': t[3]}
                    for t in recent_tasks
                ],
                'recent_operations': [
                    {'operation': o[0], 'target': o[1], 'status': o[2], 'time': o[3]}
                    for o in recent_operations
                ]
            }
            
        except Exception as e:
            logger.error(f"获取最近活动失败: {e}")
            return {'error': str(e)}
    
    # ==================== 命令行接口 ====================
    
    def run_cli(self):
        """命令行接口"""
        import argparse
        
        parser = argparse.ArgumentParser(description='共享记忆库系统')
        parser.add_argument('--create-memory', type=str, help='创建记忆条目 (格式: title,content[,type])')
        parser.add_argument('--update-task', type=str, help='更新任务状态 (格式: id,name,status[,details])')
        parser.add_argument('--sync-all', action='store_true', help='同步所有待处理任务')
        parser.add_argument('--report', action='store_true', help='生成系统报告')
        parser.add_argument('--safe-move', type=str, help='安全移动文件 (格式: source,target)')
        parser.add_argument('--safe-delete', type=str, help='安全删除文件 (路径)')
        
        args = parser.parse_args()
        
        if args.create_memory:
            parts = args.create_memory.split(',', 2)
            if len(parts) >= 2:
                title = parts[0]
                content = parts[1]
                content_type = parts[2] if len(parts) > 2 else "note"
                
                memory_id = self.create_memory_item(title, content, content_type)
                print(f"记忆条目创建成功: {memory_id}")
            else:
                print("错误: 格式应为 title,content[,type]")
        
        elif args.update_task:
            parts = args.update_task.split(',', 3)
            if len(parts) >= 3:
                task_id = parts[0]
                task_name = parts[1]
                status = parts[2]
                details = parts[3] if len(parts) > 3 else ""
                
                result = self.update_task_status(task_id, task_name, status, details)
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print("错误: 格式应为 id,name,status[,details]")
        
        elif args.sync_all:
            result = self.sync_all_pending_tasks()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif args.report:
            report = self.generate_system_report()
            print(json.dumps(report, indent=2, ensure_ascii=False))
        
        elif args.safe_move:
            parts = args.safe_move.split(',', 1)
            if len(parts) == 2:
                source, target = parts
                result = self.safe_file_operation('move', source, target)
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print("错误: 格式应为 source,target")
        
        elif args.safe_delete:
            result = self.safe_file_operation('delete', args.safe_delete)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        else:
            # 默认生成报告
            report = self.generate_system_report()
            print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    system = SharedMemorySystem()
    system.run_cli()