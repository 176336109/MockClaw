#!/usr/bin/env python3
"""
多维表格核心技能实现
沟通媒介，必须永远可用，不可改变
"""

import os
import json
import time
import requests
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/bitable_core.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('bitable_core')

class BitableCore:
    """多维表格核心技能"""
    
    def __init__(self):
        self.workspace = Path.home() / ".openclaw" / "workspace"
        self.config_path = Path.home() / ".openclaw" / "openclaw.json"
        self.cache_dir = self.workspace / ".bitable_cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
        self.app_id = self.config.get('app_id')
        self.app_secret = self.config.get('app_secret')
        
        # 多维表格配置
        self.base_app_token = "FCRNbSo4ja4hCEs5411cNZQXnkh"
        self.tasks_table_id = "tblRmMB6LIdLHyEt"
        
        # 状态跟踪
        self.health_status = {
            'last_check': None,
            'status': 'unknown',
            'error_count': 0,
            'success_count': 0
        }
        
        # 初始化缓存
        self._init_cache()
        
        logger.info("BitableCore初始化完成")
    
    def _load_config(self) -> Dict:
        """加载配置"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            feishu_config = config.get('channels', {}).get('feishu', {})
            accounts = feishu_config.get('accounts', {}).get('main', {})
            
            return {
                'app_id': accounts.get('appId'),
                'app_secret': accounts.get('appSecret')
            }
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            # 尝试从环境变量获取
            return {
                'app_id': os.getenv('FEISHU_APP_ID'),
                'app_secret': os.getenv('FEISHU_APP_SECRET')
            }
    
    def _init_cache(self):
        """初始化缓存"""
        # token缓存
        self.token_cache_file = self.cache_dir / "token_cache.json"
        if not self.token_cache_file.exists():
            with open(self.token_cache_file, 'w') as f:
                json.dump({'token': None, 'expires_at': 0}, f)
        
        # 表格结构缓存
        self.structure_cache_file = self.cache_dir / "structure_cache.json"
        
        # 操作队列
        self.queue_file = self.cache_dir / "operation_queue.jsonl"
        if not self.queue_file.exists():
            self.queue_file.touch()
        
        # 本地数据库备份
        self.local_db = self.cache_dir / "local_backup.db"
        self._init_local_db()
    
    def _init_local_db(self):
        """初始化本地数据库备份"""
        conn = sqlite3.connect(str(self.local_db))
        cursor = conn.cursor()
        
        # 创建任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                task_name TEXT,
                status TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                synced_at TIMESTAMP,
                sync_status TEXT DEFAULT 'pending'
            )
        ''')
        
        # 创建同步日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation TEXT,
                target TEXT,
                status TEXT,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ==================== Token管理 ====================
    
    def get_tenant_access_token(self, force_refresh: bool = False) -> Optional[str]:
        """获取租户访问token（多级缓存）"""
        # 1. 检查内存缓存
        if hasattr(self, '_cached_token') and not force_refresh:
            token, expires_at = self._cached_token
            if time.time() < expires_at - 60:  # 提前1分钟刷新
                logger.debug("使用内存缓存token")
                return token
        
        # 2. 检查文件缓存
        try:
            with open(self.token_cache_file, 'r') as f:
                cache = json.load(f)
            
            token = cache.get('token')
            expires_at = cache.get('expires_at', 0)
            
            if token and time.time() < expires_at - 60:
                self._cached_token = (token, expires_at)
                logger.debug("使用文件缓存token")
                return token
        except:
            pass
        
        # 3. 从API获取
        logger.info("从API获取新token")
        token = self._fetch_new_token()
        
        if token:
            # 更新缓存
            expires_at = time.time() + 7200  # 2小时有效期
            self._cached_token = (token, expires_at)
            
            cache_data = {'token': token, 'expires_at': expires_at}
            with open(self.token_cache_file, 'w') as f:
                json.dump(cache_data, f)
            
            return token
        
        # 4. 使用备用token源
        logger.warning("API获取token失败，尝试备用方案")
        return self._get_backup_token()
    
    def _fetch_new_token(self) -> Optional[str]:
        """从飞书API获取token"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                token = result.get("tenant_access_token")
                logger.info("成功获取新token")
                return token
            else:
                logger.error(f"获取token失败: {result}")
                return None
                
        except Exception as e:
            logger.error(f"获取token异常: {e}")
            return None
    
    def _get_backup_token(self) -> Optional[str]:
        """获取备用token"""
        # 1. 环境变量
        token = os.getenv('FEISHU_TENANT_ACCESS_TOKEN')
        if token:
            logger.info("使用环境变量token")
            return token
        
        # 2. 配置文件
        backup_config = self.workspace / "feishu_backup_config.json"
        if backup_config.exists():
            try:
                with open(backup_config, 'r') as f:
                    config = json.load(f)
                    token = config.get('tenant_access_token')
                    if token:
                        logger.info("使用配置文件token")
                        return token
            except:
                pass
        
        # 3. 手动输入的token（最后手段）
        manual_token_file = self.cache_dir / "manual_token.txt"
        if manual_token_file.exists():
            try:
                token = manual_token_file.read_text().strip()
                if token:
                    logger.warning("使用手动token")
                    return token
            except:
                pass
        
        logger.error("所有token源都失败")
        return None
    
    # ==================== 健康检查 ====================
    
    def check_health(self) -> Dict:
        """检查技能健康状态"""
        check_time = datetime.now().isoformat()
        
        # 1. 检查token获取
        token_status = self._check_token_health()
        
        # 2. 检查API连接
        api_status = self._check_api_health()
        
        # 3. 检查表格访问
        table_status = self._check_table_health()
        
        # 4. 检查本地备份
        backup_status = self._check_backup_health()
        
        # 综合状态
        overall_status = 'healthy'
        if not all([token_status['healthy'], api_status['healthy'], table_status['healthy']]):
            overall_status = 'degraded'
        if not backup_status['healthy']:
            overall_status = 'critical' if overall_status == 'healthy' else overall_status
        
        health_report = {
            'timestamp': check_time,
            'overall_status': overall_status,
            'components': {
                'token': token_status,
                'api': api_status,
                'table': table_status,
                'backup': backup_status
            },
            'metrics': {
                'error_count': self.health_status['error_count'],
                'success_count': self.health_status['success_count'],
                'availability': self._calculate_availability()
            }
        }
        
        # 更新状态
        self.health_status.update({
            'last_check': check_time,
            'status': overall_status
        })
        
        # 保存报告
        report_file = self.cache_dir / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(health_report, f, indent=2)
        
        logger.info(f"健康检查完成: {overall_status}")
        return health_report
    
    def _check_token_health(self) -> Dict:
        """检查token健康"""
        try:
            token = self.get_tenant_access_token()
            return {
                'healthy': bool(token),
                'message': 'Token获取成功' if token else 'Token获取失败',
                'token_length': len(token) if token else 0
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'Token检查异常: {e}',
                'error': str(e)
            }
    
    def _check_api_health(self) -> Dict:
        """检查API健康（通过实际功能测试）"""
        try:
            # 不测试通用API端点，而是测试实际功能
            # 尝试获取表格结构（这是实际使用的功能）
            token = self.get_tenant_access_token()
            if not token:
                return {'healthy': False, 'message': '无有效token'}
            
            # 测试实际使用的API：获取表格字段
            url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.base_app_token}/tables/{self.tasks_table_id}/fields"
            headers = {"Authorization": f"Bearer {token}"}
            
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=5)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    return {
                        'healthy': True,
                        'message': 'API功能正常',
                        'response_time': round(elapsed * 1000, 2),
                        'status_code': response.status_code,
                        'field_count': len(result.get("data", {}).get("items", []))
                    }
                else:
                    # 即使返回错误码，也可能是权限问题而不是API不可用
                    # 检查错误类型
                    error_code = result.get("code")
                    error_msg = result.get("msg", "")
                    
                    if error_code in [99991663, 99991664]:  # 无权限错误
                        return {
                            'healthy': True,  # API本身可用，只是权限问题
                            'message': f'API可用但权限受限: {error_msg}',
                            'status_code': response.status_code,
                            'error_code': error_code
                        }
                    else:
                        return {
                            'healthy': False,
                            'message': f'API功能错误: {error_msg}',
                            'status_code': response.status_code,
                            'error_code': error_code
                        }
            else:
                return {
                    'healthy': False,
                    'message': f'API连接错误: {response.status_code}',
                    'status_code': response.status_code,
                    'response_text': response.text[:200]
                }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'API检查异常: {e}',
                'error': str(e)
            }
    
    def _check_table_health(self) -> Dict:
        """检查表格健康"""
        try:
            token = self.get_tenant_access_token()
            if not token:
                return {'healthy': False, 'message': '无有效token'}
            
            url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.base_app_token}/tables/{self.tasks_table_id}/records?page_size=1"
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    total = result.get("data", {}).get("total", 0)
                    return {
                        'healthy': True,
                        'message': '表格访问正常',
                        'record_count': total,
                        'table_id': self.tasks_table_id
                    }
                else:
                    return {
                        'healthy': False,
                        'message': f'表格API错误: {result.get("msg")}',
                        'error_code': result.get("code")
                    }
            else:
                return {
                    'healthy': False,
                    'message': f'表格HTTP错误: {response.status_code}',
                    'status_code': response.status_code
                }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'表格检查异常: {e}',
                'error': str(e)
            }
    
    def _check_backup_health(self) -> Dict:
        """检查备份健康"""
        try:
            conn = sqlite3.connect(str(self.local_db))
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
            tables = cursor.fetchall()
            
            # 检查记录数量
            cursor.execute("SELECT COUNT(*) FROM tasks")
            task_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sync_logs")
            log_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'healthy': len(tables) > 0,
                'message': '备份系统正常' if len(tables) > 0 else '备份表不存在',
                'task_count': task_count,
                'log_count': log_count,
                'db_size': os.path.getsize(self.local_db)
            }
        except Exception as e:
            return {
                'healthy': False,
                'message': f'备份检查异常: {e}',
                'error': str(e)
            }
    
    def _calculate_availability(self) -> float:
        """计算可用性"""
        total = self.health_status['error_count'] + self.health_status['success_count']
        if total == 0:
            return 100.0
        return (self.health_status['success_count'] / total) * 100
    
    # ==================== 核心同步功能 ====================
    
    def sync_task_status(self, task_id: str, task_name: str, status: str, details: str = "") -> Dict:
        """同步任务状态（核心功能，必须成功）"""
        logger.info(f"开始同步任务状态: {task_id} -> {status}")
        
        # 记录开始时间
        start_time = time.time()
        
        # 1. 先保存到本地数据库
        local_result = self._save_to_local_db(task_id, task_name, status, details)
        
        # 2. 尝试同步到多维表格
        sync_result = self._sync_to_bitable(task_id, task_name, status, details)
        
        # 3. 更新同步状态
        self._update_sync_status(task_id, sync_result['success'])
        
        # 4. 记录指标
        elapsed = time.time() - start_time
        if sync_result['success']:
            self.health_status['success_count'] += 1
            logger.info(f"任务同步成功: {task_id}, 耗时: {elapsed:.2f}s")
        else:
            self.health_status['error_count'] += 1
            logger.error(f"任务同步失败: {task_id}, 错误: {sync_result.get('error')}")
        
        return {
            'task_id': task_id,
            'status': status,
            'sync_success': sync_result['success'],
            'local_success': local_result['success'],
            'elapsed_seconds': round(elapsed, 2),
            'error': sync_result.get('error'),
            'retry_count': sync_result.get('retry_count', 0),
            'timestamp': datetime.now().isoformat()
        }
    
    def _save_to_local_db(self, task_id: str, task_name: str, status: str, details: str) -> Dict:
        """保存到本地数据库"""
        try:
            conn = sqlite3.connect(str(self.local_db))
            cursor = conn.cursor()
            
            # 检查是否已存在
            cursor.execute("SELECT id FROM tasks WHERE task_id = ?", (task_id,))
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有记录
                cursor.execute('''
                    UPDATE tasks 
                    SET task_name = ?, status = ?, details = ?, synced_at = NULL, sync_status = 'pending'
                    WHERE task_id = ?
                ''', (task_name, status, details, task_id))
            else:
                # 插入新记录
                cursor.execute('''
                    INSERT INTO tasks (task_id, task_name, status, details)
                    VALUES (?, ?, ?, ?)
                ''', (task_id, task_name, status, details))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'action': 'updated' if existing else 'inserted'}
        except Exception as e:
            logger.error(f"保存到本地数据库失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _sync_to_bitable(self, task_id: str, task_name: str, status: str, details: str, max_retries: int = 3) -> Dict:
        """同步到多维表格（带重试）"""
        for attempt in range(max_retries):
            try:
                token = self.get_tenant_access_token()
                if not token:
                    raise ValueError("无法获取有效token")
                
                # 获取表格结构（带缓存）
                fields_mapping = self._get_fields_mapping()
                
                # 准备数据
                record_data = self._prepare_record_data(task_id, task_name, status, details, fields_mapping)
                
                # 调用API
                result = self._call_bitable_api(token, record_data)
                
                if result['success']:
                    return {'success': True, 'retry_count': attempt}
                else:
                    logger.warning(f"同步失败，尝试 {attempt + 1}/{max_retries}: {result.get('error')}")
                    
                    # 等待后重试
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # 指数退避
                    
            except Exception as e:
                logger.error(f"同步异常，尝试 {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        
        # 所有重试都失败
        logger.error(f"所有重试都失败: {task_id}")
        
        # 添加到重试队列
        self._add_to_retry_queue(task_id, task_name, status, details)
        
        return {
            'success': False,
            'error': '所有重试都失败',
            'retry_count': max_retries
        }
    
    def _get_fields_mapping(self) -> Dict:
        """获取字段映射（带缓存）"""
        cache_file = self.cache_dir / "fields_mapping.json"
        
        # 检查缓存
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                
                # 缓存有效期1小时
                if time.time() - cached.get('timestamp', 0) < 3600:
                    logger.debug("使用缓存的字段映射")
                    return cached.get('mapping', {})
            except:
                pass
        
        # 从API获取
        logger.info("从API获取字段映射")
        mapping = self._fetch_fields_from_api()
        
        if mapping:
            # 保存缓存
            cache_data = {
                'timestamp': time.time(),
                'mapping': mapping
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
        
        return mapping or {}
    
    def _fetch_fields_from_api(self) -> Dict:
        """从API获取字段信息"""
        try:
            token = self.get_tenant_access_token()
            if not token:
                return {}
            
            url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.base_app_token}/tables/{self.tasks_table_id}/fields"
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.get(url, headers=headers, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                fields = result.get("data", {}).get("items", [])
                mapping = {}
                
                for field in fields:
                    field_name = field.get('field_name')
                    field_id = field.get('field_id')
                    field_type = field.get('type')
                    
                    if field_name and field_id:
                        mapping[field_name] = {
                            'id': field_id,
                            'type': field_type,
                            'name': field_name
                        }
                
                logger.info(f"获取到 {len(mapping)} 个字段")
                return mapping
            else:
                logger.error(f"获取字段失败: {result}")
                return {}
                
        except Exception as e:
            logger.error(f"获取字段异常: {e}")
            return {}
    
    def _prepare_record_data(self, task_id: str, task_name: str, status: str, details: str, fields_mapping: Dict) -> Dict:
        """准备记录数据"""
        # 基础字段映射
        field_values = {}
        
        # 文本字段
        field_values['文本'] = f"任务状态更新: {task_name}"
        
        # 任务ID字段
        if '任务ID' in fields_mapping:
            field_values['任务ID'] = task_id
        elif '任务id' in fields_mapping:
            field_values['任务id'] = task_id
        elif 'task_id' in fields_mapping:
            field_values['task_id'] = task_id
        
        # 任务名称字段
        if '任务名称' in fields_mapping:
            field_values['任务名称'] = task_name
        elif '任务名' in fields_mapping:
            field_values['任务名'] = task_name
        elif 'task_name' in fields_mapping:
            field_values['task_name'] = task_name
        
        # 状态字段
        if '状态' in fields_mapping:
            field_values['状态'] = status
        elif 'status' in fields_mapping:
            field_values['status'] = status
        
        # 描述字段
        if '描述' in fields_mapping:
            field_values['描述'] = details
        elif 'description' in fields_mapping:
            field_values['description'] = details
        
        # 时间字段（当前时间戳，毫秒）
        current_ts = int(time.time() * 1000)
        # 使用正确的字段名：创建时间
        if '创建时间' in fields_mapping:
            field_values['创建时间'] = current_ts
        elif '最后更新时间' in fields_mapping:
            field_values['最后更新时间'] = current_ts
        elif '更新时间' in fields_mapping:
            field_values['更新时间'] = current_ts
        elif 'updated_at' in fields_mapping:
            field_values['updated_at'] = current_ts
        
        # 负责人字段
        if '负责人' in fields_mapping:
            field_values['负责人'] = 'OpenClaw主Agent'
        
        # 优先级字段（根据状态自动设置）
        if '优先级' in fields_mapping:
            if status in ['等待指示', '阻塞']:
                field_values['优先级'] = '高'
            elif status == '进行中':
                field_values['优先级'] = '中'
            else:
                field_values['优先级'] = '低'
        
        return field_values
    
    def _call_bitable_api(self, token: str, field_values: Dict) -> Dict:
        """调用bitable API"""
        try:
            # 先检查记录是否存在
            existing_record = self._find_existing_record(token, field_values.get('任务ID'))
            
            if existing_record:
                # 更新现有记录
                return self._update_record(token, existing_record['record_id'], field_values)
            else:
                # 创建新记录
                return self._create_record(token, field_values)
                
        except Exception as e:
            logger.error(f"调用API异常: {e}")
            return {'success': False, 'error': str(e)}
    
    def _find_existing_record(self, token: str, task_id: str) -> Optional[Dict]:
        """查找现有记录"""
        if not task_id:
            return None
        
        try:
            # 构建筛选条件
            filter_condition = {
                "conjunction": "and",
                "conditions": [
                    {
                        "field_name": "任务ID",
                        "operator": "is",
                        "value": [task_id]
                    }
                ]
            }
            
            url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.base_app_token}/tables/{self.tasks_table_id}/records/search"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "filter": filter_condition,
                "page_size": 1
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                items = result.get("data", {}).get("items", [])
                if items:
                    return {
                        'record_id': items[0].get('record_id'),
                        'fields': items[0].get('fields', {})
                    }
            
            return None
            
        except Exception as e:
            logger.warning(f"查找记录失败: {e}")
            return None
    
    def _create_record(self, token: str, field_values: Dict) -> Dict:
        """创建新记录"""
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.base_app_token}/tables/{self.tasks_table_id}/records"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "fields": field_values
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                record_id = result.get("data", {}).get("record", {}).get("record_id")
                logger.info(f"创建记录成功: {record_id}")
                return {'success': True, 'record_id': record_id}
            else:
                logger.error(f"创建记录失败: {result}")
                return {
                    'success': False,
                    'error': result.get('msg'),
                    'error_code': result.get('code')
                }
                
        except Exception as e:
            logger.error(f"创建记录异常: {e}")
            return {'success': False, 'error': str(e)}
    
    def _update_record(self, token: str, record_id: str, field_values: Dict) -> Dict:
        """更新现有记录"""
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.base_app_token}/tables/{self.tasks_table_id}/records/{record_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "fields": field_values
        }
        
        try:
            response = requests.put(url, headers=headers, json=data, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                logger.info(f"更新记录成功: {record_id}")
                return {'success': True, 'record_id': record_id}
            else:
                logger.error(f"更新记录失败: {result}")
                return {
                    'success': False,
                    'error': result.get('msg'),
                    'error_code': result.get('code')
                }
                
        except Exception as e:
            logger.error(f"更新记录异常: {e}")
            return {'success': False, 'error': str(e)}
    
    def _add_to_retry_queue(self, task_id: str, task_name: str, status: str, details: str):
        """添加到重试队列"""
        queue_item = {
            'task_id': task_id,
            'task_name': task_name,
            'status': status,
            'details': details,
            'timestamp': time.time(),
            'retry_count': 0
        }
        
        with open(self.queue_file, 'a') as f:
            f.write(json.dumps(queue_item) + '\n')
        
        logger.info(f"添加到重试队列: {task_id}")
    
    def _update_sync_status(self, task_id: str, success: bool):
        """更新同步状态"""
        try:
            conn = sqlite3.connect(str(self.local_db))
            cursor = conn.cursor()
            
            sync_status = 'success' if success else 'failed'
            synced_at = datetime.now().isoformat() if success else None
            
            cursor.execute('''
                UPDATE tasks 
                SET sync_status = ?, synced_at = ?
                WHERE task_id = ?
            ''', (sync_status, synced_at, task_id))
            
            # 记录同步日志
            cursor.execute('''
                INSERT INTO sync_logs (operation, target, status, error_message)
                VALUES (?, ?, ?, ?)
            ''', ('sync_task', task_id, sync_status, '' if success else '同步失败'))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"更新同步状态失败: {e}")
    
    # ==================== 批量操作 ====================
    
    def sync_all_pending_tasks(self) -> Dict:
        """同步所有待处理任务"""
        try:
            conn = sqlite3.connect(str(self.local_db))
            cursor = conn.cursor()
            
            # 获取所有待同步任务
            cursor.execute("SELECT task_id, task_name, status, details FROM tasks WHERE sync_status = 'pending' OR sync_status = 'failed'")
            pending_tasks = cursor.fetchall()
            
            conn.close()
            
            results = []
            success_count = 0
            failure_count = 0
            
            for task in pending_tasks:
                task_id, task_name, status, details = task
                result = self.sync_task_status(task_id, task_name, status, details)
                results.append(result)
                
                if result['sync_success']:
                    success_count += 1
                else:
                    failure_count += 1
            
            summary = {
                'total': len(pending_tasks),
                'success': success_count,
                'failure': failure_count,
                'success_rate': (success_count / len(pending_tasks) * 100) if pending_tasks else 100,
                'results': results
            }
            
            logger.info(f"批量同步完成: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"批量同步失败: {e}")
            return {'error': str(e), 'total': 0, 'success': 0, 'failure': 0}
    
    # ==================== 监控和报告 ====================
    
    def generate_report(self) -> Dict:
        """生成技能报告"""
        # 健康检查
        health = self.check_health()
        
        # 统计信息
        try:
            conn = sqlite3.connect(str(self.local_db))
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM tasks")
            total_tasks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE sync_status = 'success'")
            synced_tasks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE sync_status = 'failed'")
            failed_tasks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE sync_status = 'pending'")
            pending_tasks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sync_logs")
            total_logs = cursor.fetchone()[0]
            
            conn.close()
            
            stats = {
                'total_tasks': total_tasks,
                'synced_tasks': synced_tasks,
                'failed_tasks': failed_tasks,
                'pending_tasks': pending_tasks,
                'sync_rate': (synced_tasks / total_tasks * 100) if total_tasks else 0,
                'total_logs': total_logs
            }
        except Exception as e:
            stats = {'error': str(e)}
        
        # 性能指标
        metrics = {
            'availability': self._calculate_availability(),
            'error_count': self.health_status['error_count'],
            'success_count': self.health_status['success_count'],
            'last_check': self.health_status['last_check']
        }
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'skill': 'bitable_core',
            'importance': 'core_infrastructure',
            'health': health,
            'statistics': stats,
            'metrics': metrics,
            'config': {
                'app_id': self.app_id[:8] + '...' if self.app_id else None,
                'base_app_token': self.base_app_token,
                'tasks_table_id': self.tasks_table_id
            }
        }
        
        # 保存报告
        report_file = self.cache_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    # ==================== 命令行接口 ====================
    
    def run_cli(self):
        """命令行接口"""
        import argparse
        
        parser = argparse.ArgumentParser(description='多维表格核心技能')
        parser.add_argument('--health', action='store_true', help='检查健康状态')
        parser.add_argument('--sync', action='store_true', help='同步所有待处理任务')
        parser.add_argument('--report', action='store_true', help='生成报告')
        parser.add_argument('--task', type=str, help='同步单个任务 (格式: id,name,status,details)')
        
        args = parser.parse_args()
        
        if args.health:
            health = self.check_health()
            print(json.dumps(health, indent=2, ensure_ascii=False))
        
        elif args.sync:
            result = self.sync_all_pending_tasks()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif args.report:
            report = self.generate_report()
            print(json.dumps(report, indent=2, ensure_ascii=False))
        
        elif args.task:
            parts = args.task.split(',', 3)
            if len(parts) >= 3:
                task_id = parts[0]
                task_name = parts[1]
                status = parts[2]
                details = parts[3] if len(parts) > 3 else ""
                
                result = self.sync_task_status(task_id, task_name, status, details)
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print("错误: 任务格式应为 id,name,status[,details]")
        
        else:
            # 默认运行健康检查
            health = self.check_health()
            print(json.dumps(health, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    core = BitableCore()
    core.run_cli()