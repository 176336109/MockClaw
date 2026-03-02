#!/usr/bin/env python3
"""
初始化三层记忆架构的知识图谱数据库
基于openclaw-memory-architecture设计思想简化实现
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime

class MemoryGraph:
    def __init__(self, db_path=None):
        if db_path is None:
            workspace = Path.home() / ".openclaw" / "workspace"
            db_path = workspace / "memory" / "memory_graph.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        
    def connect(self):
        """连接到数据库"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        return self.conn
    
    def create_schema(self):
        """创建数据库表结构"""
        
        schema = """
        -- 核心事实表 (结构化记忆)
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity TEXT NOT NULL,           -- 实体名称
            key TEXT NOT NULL,              -- 属性键
            value TEXT NOT NULL,            -- 属性值
            category TEXT,                  -- 分类
            source TEXT,                    -- 来源文件
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now')),
            activation REAL DEFAULT 1.0,    -- 激活值 (Hot/Warm/Cool)
            importance REAL DEFAULT 0.5,    -- 重要性权重
            access_count INTEGER DEFAULT 0  -- 访问次数
        );
        
        -- 关系表 (实体间关系)
        CREATE TABLE IF NOT EXISTS relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,          -- 主体
            predicate TEXT NOT NULL,         -- 谓词/关系类型
            object TEXT NOT NULL,           -- 客体
            weight REAL DEFAULT 1.0,        -- 关系权重
            source TEXT,                    -- 来源
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(subject, predicate, object)
        );
        
        -- 别名表 (实体别名解析)
        CREATE TABLE IF NOT EXISTS aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alias TEXT NOT NULL COLLATE NOCASE,  -- 别名
            entity TEXT NOT NULL,                -- 标准实体名
            UNIQUE(alias, entity)
        );
        
        -- 会话记忆表 (工作记忆)
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL UNIQUE,     -- 会话ID
            start_time TEXT NOT NULL,            -- 开始时间
            end_time TEXT,                       -- 结束时间
            channel TEXT,                        -- 渠道 (feishu, telegram等)
            summary TEXT,                        -- 会话摘要
            context TEXT,                        -- 上下文内容
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        
        -- 项目记忆表 (情景记忆)
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL UNIQUE,     -- 项目ID
            name TEXT NOT NULL,                  -- 项目名称
            description TEXT,                    -- 项目描述
            status TEXT DEFAULT 'active',        -- 状态
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        
        -- 项目事件表
        CREATE TABLE IF NOT EXISTS project_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,            -- 项目ID
            event_type TEXT NOT NULL,            -- 事件类型
            content TEXT NOT NULL,               -- 事件内容
            importance REAL DEFAULT 0.5,         -- 重要性
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (project_id) REFERENCES projects(project_id)
        );
        
        -- 创建索引
        CREATE INDEX IF NOT EXISTS idx_facts_entity ON facts(entity);
        CREATE INDEX IF NOT EXISTS idx_facts_key ON facts(key);
        CREATE INDEX IF NOT EXISTS idx_facts_category ON facts(category);
        CREATE INDEX IF NOT EXISTS idx_relations_subject ON relations(subject);
        CREATE INDEX IF NOT EXISTS idx_relations_object ON relations(object);
        CREATE INDEX IF NOT EXISTS idx_aliases_alias ON aliases(alias COLLATE NOCASE);
        CREATE INDEX IF NOT EXISTS idx_sessions_time ON sessions(start_time);
        CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
        """
        
        self.conn.executescript(schema)
        print("✅ 数据库表结构创建完成")
    
    def seed_initial_data(self):
        """初始化种子数据"""
        
        # 添加用户基本信息
        user_facts = [
            ("User", "name", "MockLab", "identity", "USER.md"),
            ("User", "timezone", "Asia/Shanghai", "preference", "USER.md"),
            ("User", "communication_style", "简洁明了、结构化", "preference", "USER.md"),
            ("User", "preference", "减少语气词和冗余表达", "preference", "USER.md"),
        ]
        
        for entity, key, value, category, source in user_facts:
            self.add_fact(entity, key, value, category, source)
        
        # 添加系统信息
        system_facts = [
            ("System", "agent_name", "OpenClaw", "system", "SOUL.md"),
            ("System", "model", "deepseek/deepseek-chat", "system", "runtime"),
            ("System", "workspace", "/Users/mocklab/.openclaw/workspace", "system", "runtime"),
        ]
        
        for entity, key, value, category, source in system_facts:
            self.add_fact(entity, key, value, category, source)
        
        # 添加当前项目
        current_projects = [
            ("PROJ-001", "三层记忆架构升级", "基于开源方案升级OpenClaw记忆系统", "active"),
            ("PROJ-002", "小红书自动化团队", "建设全自动发小红书的Agent团队", "planning"),
            ("PROJ-003", "技能状态管理系统", "管理和监控OpenClaw技能状态", "active"),
        ]
        
        for project_id, name, description, status in current_projects:
            self.add_project(project_id, name, description, status)
        
        print("✅ 初始数据种子完成")
    
    def add_fact(self, entity, key, value, category=None, source=None):
        """添加一个事实"""
        sql = """
        INSERT OR REPLACE INTO facts (entity, key, value, category, source, updated_at)
        VALUES (?, ?, ?, ?, ?, datetime('now'))
        """
        self.conn.execute(sql, (entity, key, value, category, source))
        self.conn.commit()
    
    def add_relation(self, subject, predicate, object, weight=1.0, source=None):
        """添加一个关系"""
        sql = """
        INSERT OR IGNORE INTO relations (subject, predicate, object, weight, source)
        VALUES (?, ?, ?, ?, ?)
        """
        self.conn.execute(sql, (subject, predicate, object, weight, source))
        self.conn.commit()
    
    def add_alias(self, alias, entity):
        """添加一个别名"""
        sql = """
        INSERT OR IGNORE INTO aliases (alias, entity)
        VALUES (?, ?)
        """
        self.conn.execute(sql, (alias, entity))
        self.conn.commit()
    
    def add_project(self, project_id, name, description=None, status="active"):
        """添加一个项目"""
        sql = """
        INSERT OR REPLACE INTO projects (project_id, name, description, status, updated_at)
        VALUES (?, ?, ?, ?, datetime('now'))
        """
        self.conn.execute(sql, (project_id, name, description, status))
        self.conn.commit()
    
    def add_project_event(self, project_id, event_type, content, importance=0.5):
        """添加项目事件"""
        sql = """
        INSERT INTO project_events (project_id, event_type, content, importance)
        VALUES (?, ?, ?, ?)
        """
        self.conn.execute(sql, (project_id, event_type, content, importance))
        self.conn.commit()
    
    def start_session(self, session_id, channel=None):
        """开始一个新会话"""
        sql = """
        INSERT INTO sessions (session_id, start_time, channel)
        VALUES (?, datetime('now'), ?)
        """
        self.conn.execute(sql, (session_id, channel))
        self.conn.commit()
    
    def end_session(self, session_id, summary=None, context=None):
        """结束一个会话"""
        sql = """
        UPDATE sessions 
        SET end_time = datetime('now'), summary = ?, context = ?
        WHERE session_id = ? AND end_time IS NULL
        """
        self.conn.execute(sql, (summary, context, session_id))
        self.conn.commit()
    
    def search_facts(self, query, entity=None, key=None, category=None, limit=10):
        """搜索事实"""
        conditions = []
        params = []
        
        if query:
            conditions.append("(entity LIKE ? OR key LIKE ? OR value LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        
        if entity:
            conditions.append("entity = ?")
            params.append(entity)
        
        if key:
            conditions.append("key = ?")
            params.append(key)
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"SELECT * FROM facts WHERE {where_clause} ORDER BY activation DESC, importance DESC LIMIT ?"
        params.append(limit)
        
        return self.conn.execute(sql, params).fetchall()
    
    def get_entity_facts(self, entity):
        """获取实体的所有事实"""
        sql = "SELECT key, value, category FROM facts WHERE entity = ? ORDER BY importance DESC"
        return self.conn.execute(sql, (entity,)).fetchall()
    
    def get_entity_relations(self, entity):
        """获取实体的所有关系"""
        sql = """
        SELECT predicate, object, weight 
        FROM relations 
        WHERE subject = ? 
        ORDER BY weight DESC
        """
        return self.conn.execute(sql, (entity,)).fetchall()
    
    def resolve_alias(self, alias):
        """解析别名到标准实体名"""
        sql = "SELECT entity FROM aliases WHERE alias = ? COLLATE NOCASE"
        result = self.conn.execute(sql, (alias,)).fetchone()
        return result[0] if result else alias
    
    def update_activation(self, fact_id, delta=0.1):
        """更新事实的激活值"""
        sql = "UPDATE facts SET activation = activation + ?, access_count = access_count + 1 WHERE id = ?"
        self.conn.execute(sql, (delta, fact_id))
        self.conn.commit()
    
    def decay_activation(self, decay_rate=0.95):
        """衰减所有事实的激活值"""
        sql = "UPDATE facts SET activation = activation * ? WHERE activation > 0.1"
        self.conn.execute(sql, (decay_rate,))
        self.conn.commit()
        count = self.conn.execute("SELECT changes()").fetchone()[0]
        return count
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def main():
    """主函数：初始化记忆图谱"""
    print("🧠 开始初始化三层记忆架构知识图谱...")
    
    # 确定数据库路径
    workspace = Path.home() / ".openclaw" / "workspace"
    db_path = workspace / "memory" / "memory_graph.db"
    
    print(f"📁 数据库路径: {db_path}")
    
    # 初始化记忆图谱
    with MemoryGraph(db_path) as mg:
        # 创建表结构
        mg.create_schema()
        
        # 添加种子数据
        mg.seed_initial_data()
        
        # 测试查询
        print("\n🔍 测试查询:")
        
        # 查询用户信息
        user_facts = mg.get_entity_facts("User")
        print("用户信息:")
        for key, value, category in user_facts:
            print(f"  {key}: {value} ({category})")
        
        # 查询系统信息
        system_facts = mg.get_entity_facts("System")
        print("\n系统信息:")
        for key, value, category in system_facts:
            print(f"  {key}: {value} ({category})")
        
        # 查询活跃项目
        print("\n活跃项目:")
        projects = mg.conn.execute("SELECT name, description FROM projects WHERE status = 'active'").fetchall()
        for name, desc in projects:
            print(f"  {name}: {desc}")
        
        # 统计信息
        facts_count = mg.conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
        relations_count = mg.conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
        projects_count = mg.conn.execute("SELECT COUNT(*) FROM projects").fetchall()[0]
        
        print(f"\n📊 统计信息:")
        print(f"  事实数量: {facts_count}")
        print(f"  关系数量: {relations_count}")
        print(f"  项目数量: {projects_count}")
    
    print("\n✅ 三层记忆架构知识图谱初始化完成！")
    print("   下一步: 运行记忆维护脚本和集成到OpenClaw工作流")

if __name__ == "__main__":
    main()