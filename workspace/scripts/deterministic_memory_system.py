#!/usr/bin/env python3
"""
确定性记忆系统实现
目标：成功经验一次沉淀，永远可用；失败教训一次学习，避免重复
"""

import os
import json
import time
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/deterministic_memory.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('deterministic_memory')

class DeterministicMemorySystem:
    """确定性记忆系统"""
    
    def __init__(self):
        self.workspace = Path.home() / ".openclaw" / "workspace"
        self.memory_dir = self.workspace / "memory"
        self.checkpoints_dir = self.memory_dir / "checkpoints"
        self.lessons_dir = self.memory_dir / "lessons"
        
        # 创建目录
        for directory in [self.checkpoints_dir, self.lessons_dir]:
            directory.mkdir(exist_ok=True)
        
        # 数据库
        self.db_path = self.memory_dir / "deterministic_memory.db"
        self._init_database()
        
        # 缓存
        self.success_patterns_cache = {}
        self.failure_patterns_cache = {}
        
        logger.info("确定性记忆系统初始化完成")
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # 检查点表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checkpoint_id TEXT UNIQUE NOT NULL,
                checkpoint_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                data_json TEXT NOT NULL,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                checksum TEXT NOT NULL,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # 成功经验表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS success_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                context TEXT,
                solution TEXT NOT NULL,
                key_factors TEXT,
                implementation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 1.0,
                checksum TEXT NOT NULL
            )
        ''')
        
        # 失败教训表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS failure_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                context TEXT,
                problem TEXT NOT NULL,
                root_cause TEXT,
                impact TEXT,
                prevention TEXT,
                detection TEXT,
                recovery TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                occurrence_count INTEGER DEFAULT 1,
                last_occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                checksum TEXT NOT NULL
            )
        ''')
        
        # 一致性验证表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consistency_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                check_id TEXT UNIQUE NOT NULL,
                source_system TEXT NOT NULL,
                target_system TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            )
        ''')
        
        # 索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_checkpoints_type ON checkpoints(checkpoint_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_success_category ON success_patterns(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_failure_category ON failure_patterns(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_consistency_status ON consistency_checks(status)')
        
        conn.commit()
        conn.close()
    
    # ==================== 检查点系统 ====================
    
    def create_checkpoint(self, checkpoint_type: str, title: str, data: Dict, 
                         description: str = "", metadata: Dict = None) -> str:
        """创建记忆检查点"""
        # 生成检查点ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        checkpoint_id = f"CP_{checkpoint_type}_{timestamp}_{hashlib.md5(title.encode()).hexdigest()[:8]}"
        
        # 计算校验和
        data_json = json.dumps(data, sort_keys=True, ensure_ascii=False)
        checksum = hashlib.md5(data_json.encode()).hexdigest()
        
        # 准备记录
        record = {
            'checkpoint_id': checkpoint_id,
            'checkpoint_type': checkpoint_type,
            'title': title,
            'description': description,
            'data_json': data_json,
            'metadata_json': json.dumps(metadata or {}, ensure_ascii=False),
            'checksum': checksum,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 保存到数据库
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO checkpoints 
            (checkpoint_id, checkpoint_type, title, description, data_json, metadata_json, checksum)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            record['checkpoint_id'],
            record['checkpoint_type'],
            record['title'],
            record['description'],
            record['data_json'],
            record['metadata_json'],
            record['checksum']
        ))
        
        conn.commit()
        conn.close()
        
        # 保存到文件（备份）
        checkpoint_file = self.checkpoints_dir / f"{checkpoint_id}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
        
        logger.info(f"创建检查点: {checkpoint_id} - {title}")
        return checkpoint_id
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[Dict]:
        """获取检查点"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT checkpoint_id, checkpoint_type, title, description, 
                   data_json, metadata_json, created_at, checksum
            FROM checkpoints 
            WHERE checkpoint_id = ? AND status = 'active'
        ''', (checkpoint_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'checkpoint_id': row[0],
                'checkpoint_type': row[1],
                'title': row[2],
                'description': row[3],
                'data': json.loads(row[4]),
                'metadata': json.loads(row[5]) if row[5] else {},
                'created_at': row[6],
                'checksum': row[7]
            }
        
        return None
    
    def search_checkpoints(self, checkpoint_type: str = None, 
                          start_date: str = None, end_date: str = None,
                          keyword: str = None) -> List[Dict]:
        """搜索检查点"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = "SELECT checkpoint_id, checkpoint_type, title, created_at FROM checkpoints WHERE status = 'active'"
        params = []
        
        if checkpoint_type:
            query += " AND checkpoint_type = ?"
            params.append(checkpoint_type)
        
        if start_date:
            query += " AND created_at >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND created_at <= ?"
            params.append(end_date)
        
        if keyword:
            query += " AND (title LIKE ? OR description LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'checkpoint_id': row[0],
                'checkpoint_type': row[1],
                'title': row[2],
                'created_at': row[3]
            }
            for row in rows
        ]
    
    # ==================== 成功经验沉淀 ====================
    
    def record_success_pattern(self, title: str, category: str, context: str, 
                              solution: str, key_factors: List[str] = None,
                              implementation: str = "") -> str:
        """记录成功经验模式"""
        # 生成模式ID
        pattern_id = f"SUCCESS_{category}_{hashlib.md5(title.encode()).hexdigest()[:12]}"
        
        # 检查是否已存在
        existing = self._get_success_pattern(pattern_id)
        if existing:
            # 更新使用统计
            self._update_success_pattern_usage(pattern_id)
            logger.info(f"成功模式已存在，更新使用统计: {pattern_id}")
            return pattern_id
        
        # 计算校验和
        solution_hash = hashlib.md5(solution.encode()).hexdigest()
        
        # 保存到数据库
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO success_patterns 
            (pattern_id, title, category, context, solution, key_factors, implementation, checksum)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern_id,
            title,
            category,
            context,
            solution,
            json.dumps(key_factors or [], ensure_ascii=False),
            implementation,
            solution_hash
        ))
        
        conn.commit()
        conn.close()
        
        # 保存到文件
        pattern_file = self.lessons_dir / "success" / f"{pattern_id}.json"
        pattern_file.parent.mkdir(exist_ok=True)
        
        pattern_data = {
            'pattern_id': pattern_id,
            'title': title,
            'category': category,
            'context': context,
            'solution': solution,
            'key_factors': key_factors or [],
            'implementation': implementation,
            'created_at': datetime.now().isoformat(),
            'checksum': solution_hash
        }
        
        with open(pattern_file, 'w', encoding='utf-8') as f:
            json.dump(pattern_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"记录成功经验模式: {pattern_id} - {title}")
        return pattern_id
    
    def _get_success_pattern(self, pattern_id: str) -> Optional[Dict]:
        """获取成功模式"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pattern_id, title, category, context, solution, 
                   key_factors, implementation, created_at, usage_count, success_rate
            FROM success_patterns 
            WHERE pattern_id = ?
        ''', (pattern_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'pattern_id': row[0],
                'title': row[1],
                'category': row[2],
                'context': row[3],
                'solution': row[4],
                'key_factors': json.loads(row[5]) if row[5] else [],
                'implementation': row[6],
                'created_at': row[7],
                'usage_count': row[8],
                'success_rate': row[9]
            }
        
        return None
    
    def _update_success_pattern_usage(self, pattern_id: str):
        """更新成功模式使用统计"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE success_patterns 
            SET usage_count = usage_count + 1, 
                last_used_at = CURRENT_TIMESTAMP
            WHERE pattern_id = ?
        ''', (pattern_id,))
        
        conn.commit()
        conn.close()
    
    def find_success_patterns(self, category: str = None, keyword: str = None) -> List[Dict]:
        """查找成功模式"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = "SELECT pattern_id, title, category, usage_count, success_rate FROM success_patterns WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if keyword:
            query += " AND (title LIKE ? OR context LIKE ? OR solution LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
        
        query += " ORDER BY usage_count DESC, success_rate DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'pattern_id': row[0],
                'title': row[1],
                'category': row[2],
                'usage_count': row[3],
                'success_rate': row[4]
            }
            for row in rows
        ]
    
    # ==================== 失败教训沉淀 ====================
    
    def record_failure_pattern(self, title: str, category: str, context: str,
                              problem: str, root_cause: str = "",
                              impact: str = "", prevention: str = "",
                              detection: str = "", recovery: str = "") -> str:
        """记录失败教训模式"""
        # 生成模式ID
        pattern_id = f"FAILURE_{category}_{hashlib.md5(title.encode()).hexdigest()[:12]}"
        
        # 检查是否已存在
        existing = self._get_failure_pattern(pattern_id)
        if existing:
            # 更新发生次数
            self._update_failure_pattern_occurrence(pattern_id)
            logger.info(f"失败模式已存在，更新发生次数: {pattern_id}")
            return pattern_id
        
        # 计算校验和
        problem_hash = hashlib.md5(problem.encode()).hexdigest()
        
        # 保存到数据库
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO failure_patterns 
            (pattern_id, title, category, context, problem, root_cause, 
             impact, prevention, detection, recovery, checksum)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            pattern_id,
            title,
            category,
            context,
            problem,
            root_cause,
            impact,
            prevention,
            detection,
            recovery,
            problem_hash
        ))
        
        conn.commit()
        conn.close()
        
        # 保存到文件
        pattern_file = self.lessons_dir / "failure" / f"{pattern_id}.json"
        pattern_file.parent.mkdir(exist_ok=True)
        
        pattern_data = {
            'pattern_id': pattern_id,
            'title': title,
            'category': category,
            'context': context,
            'problem': problem,
            'root_cause': root_cause,
            'impact': impact,
            'prevention': prevention,
            'detection': detection,
            'recovery': recovery,
            'created_at': datetime.now().isoformat(),
            'occurrence_count': 1,
            'checksum': problem_hash
        }
        
        with open(pattern_file, 'w', encoding='utf-8') as f:
            json.dump(pattern_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"记录失败教训模式: {pattern_id} - {title}")
        return pattern_id
    
    def _get_failure_pattern(self, pattern_id: str) -> Optional[Dict]:
        """获取失败模式"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT pattern_id, title, category, context, problem, root_cause,
                   impact, prevention, detection, recovery, created_at, occurrence_count
            FROM failure_patterns 
            WHERE pattern_id = ?
        ''', (pattern_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'pattern_id': row[0],
                'title': row[1],
                'category': row[2],
                'context': row[3],
                'problem': row[4],
                'root_cause': row[5],
                'impact': row[6],
                'prevention': row[7],
                'detection': row[8],
                'recovery': row[9],
                'created_at': row[10],
                'occurrence_count': row[11]
            }
        
        return None
    
    def _update_failure_pattern_occurrence(self, pattern_id: str):
        """更新失败模式发生次数"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE failure_patterns 
            SET occurrence_count = occurrence_count + 1, 
                last_occurred_at = CURRENT_TIMESTAMP
            WHERE pattern_id = ?
        ''', (pattern_id,))
        
        conn.commit()
        conn.close()
    
    def find_failure_patterns(self, category: str = None, keyword: str = None) -> List[Dict]:
        """查找失败模式"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = "SELECT pattern_id, title, category, occurrence_count FROM failure_patterns WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if keyword:
            query += " AND (title LIKE ? OR problem LIKE ? OR root_cause LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
        
        query += " ORDER BY occurrence_count DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetch