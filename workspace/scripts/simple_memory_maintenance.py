#!/usr/bin/env python3
"""
简化的三层记忆架构维护脚本
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta

def get_db_connection():
    """获取数据库连接"""
    workspace = Path.home() / ".openclaw" / "workspace"
    db_path = workspace / "memory" / "memory_graph.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def run_daily_decay():
    """运行每日激活衰减"""
    print("🔄 运行激活衰减...")
    
    conn = get_db_connection()
    
    try:
        # 衰减激活值 (95%保留)
        cursor = conn.execute("UPDATE facts SET activation = activation * 0.95 WHERE activation > 0.1")
        decayed = cursor.rowcount
        print(f"  衰减了 {decayed} 个事实的激活值")
        
        # 统计激活分布
        stats = {
            "total": conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0],
            "hot": conn.execute("SELECT COUNT(*) FROM facts WHERE activation > 2.0").fetchone()[0],
            "warm": conn.execute("SELECT COUNT(*) FROM facts WHERE activation BETWEEN 1.0 AND 2.0").fetchone()[0],
            "cool": conn.execute("SELECT COUNT(*) FROM facts WHERE activation < 1.0").fetchone()[0],
            "last_decay": datetime.now().isoformat()
        }
        
        # 保存统计
        stats_file = Path.home() / ".openclaw" / "workspace" / "memory" / "memory_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"📊 激活分布: 热({stats['hot']}) 温({stats['warm']}) 冷({stats['cool']})")
        
        conn.commit()
        
    except Exception as e:
        print(f"  错误: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    print("✅ 激活衰减完成")

def sync_from_files():
    """从文件同步数据"""
    print("🔄 从文件同步数据...")
    
    workspace = Path.home() / ".openclaw" / "workspace"
    conn = get_db_connection()
    
    try:
        # 同步USER.md
        user_file = workspace / "USER.md"
        if user_file.exists():
            with open(user_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单提取用户信息
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if ':' in line and not line.startswith('#'):
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key and value:
                        conn.execute(
                            "INSERT OR REPLACE INTO facts (entity, key, value, category, source, updated_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
                            ("User", key, value, "user_info", "USER.md")
                        )
            
            print("  同步了USER.md")
        
        # 同步MEMORY.md
        memory_file = workspace / "MEMORY.md"
        if memory_file.exists():
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取重要事实
            lines = content.split('\n')
            for line in lines:
                if line.startswith('- ') or line.startswith('* '):
                    fact = line[2:].strip()
                    if ':' in fact:
                        key, value = fact.split(':', 1)
                        conn.execute(
                            "INSERT OR REPLACE INTO facts (entity, key, value, category, source, updated_at) VALUES (?, ?, ?, ?, ?, datetime('now'))",
                            ("System", key.strip(), value.strip(), "memory", "MEMORY.md")
                        )
            
            print("  同步了MEMORY.md")
        
        # 同步项目状态
        conn.execute(
            "UPDATE projects SET status = 'active', updated_at = datetime('now') WHERE project_id = 'PROJ-001'"
        )
        
        # 添加当前会话
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        conn.execute(
            "INSERT INTO sessions (session_id, start_time, channel) VALUES (?, datetime('now'), ?)",
            (session_id, "feishu")
        )
        
        conn.commit()
        print("✅ 文件同步完成")
        
    except Exception as e:
        print(f"  错误: {e}")
        conn.rollback()
    finally:
        conn.close()

def generate_report():
    """生成报告"""
    print("📈 生成记忆系统报告...")
    
    conn = get_db_connection()
    
    try:
        # 收集统计
        stats = {
            "timestamp": datetime.now().isoformat(),
            "facts": {
                "total": conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0],
                "by_entity": dict(conn.execute(
                    "SELECT entity, COUNT(*) FROM facts GROUP BY entity"
                ).fetchall())
            },
            "sessions": conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],
            "projects": conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0],
            "active_projects": conn.execute("SELECT COUNT(*) FROM projects WHERE status = 'active'").fetchone()[0]
        }
        
        # 保存报告
        report_file = Path.home() / ".openclaw" / "workspace" / "memory" / "memory_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        # 打印摘要
        print(f"\n📊 记忆系统状态:")
        print(f"  事实总数: {stats['facts']['total']}")
        print(f"  会话记录: {stats['sessions']}")
        print(f"  项目总数: {stats['projects']} (活跃: {stats['active_projects']})")
        
        print(f"\n  实体分布:")
        for entity, count in stats['facts']['by_entity'].items():
            print(f"    {entity}: {count}")
        
        print(f"\n✅ 报告已保存到: {report_file}")
        
    except Exception as e:
        print(f"  错误: {e}")
    finally:
        conn.close()

def main():
    """主函数"""
    print("🧠 开始三层记忆架构维护...")
    
    # 1. 同步文件
    sync_from_files()
    
    # 2. 衰减激活
    run_daily_decay()
    
    # 3. 生成报告
    generate_report()
    
    print("\n🎉 三层记忆架构维护完成！")
    print("   系统已升级到三层记忆架构:")
    print("   1. 工作记忆层 (会话管理)")
    print("   2. 情景记忆层 (项目管理)")
    print("   3. 语义记忆层 (知识图谱)")

if __name__ == "__main__":
    main()