#!/usr/bin/env python3
"""
三层记忆架构维护脚本
包括：激活衰减、数据同步、记忆优化等功能
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加脚本目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 现在可以导入MemoryGraph
try:
    from init_memory_graph import MemoryGraph
except ImportError:
    # 如果直接导入失败，尝试相对导入
    exec(open(str(Path(__file__).parent / "init_memory_graph.py")).read())
    from init_memory_graph import MemoryGraph

class MemoryMaintenance:
    def __init__(self, db_path=None):
        if db_path is None:
            workspace = Path.home() / ".openclaw" / "workspace"
            db_path = workspace / "memory" / "memory_graph.db"
        
        self.db_path = Path(db_path)
        self.mg = MemoryGraph(db_path)
    
    def run_daily_decay(self):
        """运行每日激活衰减"""
        print("🔄 运行激活衰减...")
        
        with self.mg as mg:
            mg.connect()
            
            # 衰减激活值
            decayed = mg.decay_activation(decay_rate=0.95)
            print(f"  衰减了 {decayed} 个事实的激活值")
            
            # 标记过冷的事实 (激活值 < 0.1)
            cold_facts = mg.conn.execute(
                "SELECT id, entity, key FROM facts WHERE activation < 0.1"
            ).fetchall()
            
            if cold_facts:
                print(f"  发现 {len(cold_facts)} 个过冷事实:")
                for fid, entity, key in cold_facts[:5]:  # 只显示前5个
                    print(f"    - {entity}.{key} (激活值过低)")
            
            # 更新统计信息
            stats = {
                "total_facts": mg.conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0],
                "hot_facts": mg.conn.execute("SELECT COUNT(*) FROM facts WHERE activation > 2.0").fetchone()[0],
                "warm_facts": mg.conn.execute("SELECT COUNT(*) FROM facts WHERE activation BETWEEN 1.0 AND 2.0").fetchone()[0],
                "cool_facts": mg.conn.execute("SELECT COUNT(*) FROM facts WHERE activation < 1.0").fetchone()[0],
                "last_decay": datetime.now().isoformat()
            }
            
            # 保存统计信息
            stats_file = self.db_path.parent / "memory_stats.json"
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            
            print(f"📊 记忆统计: 总共{stats['total_facts']}事实 (热:{stats['hot_facts']}, 温:{stats['warm_facts']}, 冷:{stats['cool_facts']})")
        
        print("✅ 激活衰减完成")
    
    def sync_from_memory_files(self):
        """从记忆文件同步数据到知识图谱"""
        print("🔄 从记忆文件同步数据...")
        
        workspace = Path.home() / ".openclaw" / "workspace"
        memory_dir = workspace / "memory"
        
        with self.mg as mg:
            mg.connect()
            
            # 同步MEMORY.md
            memory_file = workspace / "MEMORY.md"
            if memory_file.exists():
                self._sync_memory_file(mg, memory_file, "MEMORY.md")
            
            # 同步USER.md
            user_file = workspace / "USER.md"
            if user_file.exists():
                self._sync_user_file(mg, user_file)
            
            # 同步每日日志
            self._sync_daily_logs(mg, memory_dir)
            
            # 同步项目文件
            projects_dir = memory_dir / "projects"
            if projects_dir.exists():
                self._sync_projects(mg, projects_dir)
        
        print("✅ 记忆文件同步完成")
    
    def _sync_memory_file(self, mg, file_path, source):
        """同步MEMORY.md文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取重要事实（简化版本）
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    # 简单提取事实
                    fact_text = line[2:].strip()
                    if ':' in fact_text:
                        key, value = fact_text.split(':', 1)
                        mg.add_fact("System", key.strip(), value.strip(), "memory", source)
        
        except Exception as e:
            print(f"  警告: 同步MEMORY.md失败: {e}")
    
    def _sync_user_file(self, mg, file_path):
        """同步USER.md文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析USER.md格式
            lines = content.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('## '):
                    current_section = line[3:].strip()
                elif line.startswith('- **'):
                    # 提取键值对
                    if ':**' in line:
                        key_value = line[4:].split(':**', 1)
                        if len(key_value) == 2:
                            key, value = key_value
                            mg.add_fact("User", key.strip(), value.strip(), current_section or "general", "USER.md")
                elif ':' in line and not line.startswith('#') and not line.startswith('---'):
                    # 简单键值对
                    key, value = line.split(':', 1)
                    mg.add_fact("User", key.strip(), value.strip(), current_section or "general", "USER.md")
        
        except Exception as e:
            print(f"  警告: 同步USER.md失败: {e}")
    
    def _sync_daily_logs(self, mg, memory_dir):
        """同步每日日志"""
        try:
            # 获取最近3天的日志
            today = datetime.now()
            for i in range(3):
                date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
                log_file = memory_dir / f"{date_str}.md"
                
                if log_file.exists():
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 提取项目事件
                    if "项目" in content or "任务" in content:
                        lines = content.split('\n')
                        for line in lines:
                            if "PROJ-" in line or "TASK-" in line:
                                # 提取项目相关事件
                                mg.add_project_event(
                                    "PROJ-001" if "记忆架构" in line else "PROJ-003",
                                    "daily_log",
                                    line.strip(),
                                    0.3
                                )
            
            print(f"  同步了最近3天的日志")
        
        except Exception as e:
            print(f"  警告: 同步每日日志失败: {e}")
    
    def _sync_projects(self, mg, projects_dir):
        """同步项目文件"""
        try:
            project_files = list(projects_dir.glob("*.md"))
            
            for project_file in project_files:
                project_name = project_file.stem
                
                with open(project_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取项目状态
                if "完成" in content or "进行中" in content or "计划" in content:
                    status = "active" if "进行中" in content else "completed" if "完成" in content else "planning"
                    
                    # 更新项目状态
                    mg.conn.execute(
                        "UPDATE projects SET status = ?, updated_at = datetime('now') WHERE name LIKE ?",
                        (status, f"%{project_name}%")
                    )
                    mg.conn.commit()
            
            print(f"  同步了 {len(project_files)} 个项目文件")
        
        except Exception as e:
            print(f"  警告: 同步项目文件失败: {e}")
    
    def optimize_memory(self):
        """优化记忆存储"""
        print("🔧 优化记忆存储...")
        
        with self.mg as mg:
            mg.connect()
            
            # 1. 清理过时会话 (30天前)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            deleted_sessions = mg.conn.execute(
                "DELETE FROM sessions WHERE start_time < ?",
                (thirty_days_ago,)
            ).rowcount
            mg.conn.commit()
            
            print(f"  清理了 {deleted_sessions} 个过时会话")
            
            # 2. 归档低重要性项目事件 (重要性 < 0.3)
            archived_events = mg.conn.execute(
                "DELETE FROM project_events WHERE importance < 0.3 AND created_at < datetime('now', '-7 days')"
            ).rowcount
            mg.conn.commit()
            
            print(f"  归档了 {archived_events} 个低重要性项目事件")
            
            # 3. 重建索引
            mg.conn.execute("REINDEX")
            mg.conn.commit()
            
            print("  重建了数据库索引")
            
            # 4. 执行VACUUM
            mg.conn.execute("VACUUM")
            mg.conn.commit()
            
            print("  执行了数据库压缩")
        
        print("✅ 记忆优化完成")
    
    def generate_report(self):
        """生成记忆系统报告"""
        print("📈 生成记忆系统报告...")
        
        with self.mg as mg:
            mg.connect()
            
            # 收集统计信息
            stats = {
                "timestamp": datetime.now().isoformat(),
                "database": {
                    "path": str(self.db_path),
                    "size_mb": self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0
                },
                "facts": {
                    "total": mg.conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0],
                    "by_category": dict(mg.conn.execute(
                        "SELECT category, COUNT(*) FROM facts GROUP BY category"
                    ).fetchall()),
                    "activation_distribution": {
                        "hot": mg.conn.execute("SELECT COUNT(*) FROM facts WHERE activation > 2.0").fetchone()[0],
                        "warm": mg.conn.execute("SELECT COUNT(*) FROM facts WHERE activation BETWEEN 1.0 AND 2.0").fetchone()[0],
                        "cool": mg.conn.execute("SELECT COUNT(*) FROM facts WHERE activation < 1.0").fetchone()[0]
                    }
                },
                "relations": mg.conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0],
                "aliases": mg.conn.execute("SELECT COUNT(*) FROM aliases").fetchone()[0],
                "sessions": {
                    "total": mg.conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0],
                    "active": mg.conn.execute("SELECT COUNT(*) FROM sessions WHERE end_time IS NULL").fetchone()[0],
                    "last_7_days": mg.conn.execute(
                        "SELECT COUNT(*) FROM sessions WHERE start_time > datetime('now', '-7 days')"
                    ).fetchone()[0]
                },
                "projects": {
                    "total": mg.conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0],
                    "by_status": dict(mg.conn.execute(
                        "SELECT status, COUNT(*) FROM projects GROUP BY status"
                    ).fetchall())
                },
                "project_events": mg.conn.execute("SELECT COUNT(*) FROM project_events").fetchone()[0]
            }
            
            # 保存报告
            report_file = self.db_path.parent / "memory_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            
            # 打印摘要
            print(f"\n📊 记忆系统报告摘要:")
            print(f"  数据库大小: {stats['database']['size_mb']:.2f} MB")
            print(f"  事实总数: {stats['facts']['total']}")
            print(f"  关系数量: {stats['relations']}")
            print(f"  会话总数: {stats['sessions']['total']} (活跃: {stats['sessions']['active']})")
            print(f"  项目总数: {stats['projects']['total']}")
            print(f"  激活分布: 热({stats['facts']['activation_distribution']['hot']}) 温({stats['facts']['activation_distribution']['warm']}) 冷({stats['facts']['activation_distribution']['cool']})")
            
            # 分类统计
            print(f"\n  事实分类:")
            for category, count in stats['facts']['by_category'].items():
                print(f"    {category}: {count}")
            
            # 项目状态
            print(f"\n  项目状态:")
            for status, count in stats['projects']['by_status'].items():
                print(f"    {status}: {count}")
        
        print(f"\n✅ 详细报告已保存到: {report_file}")

def main():
    """主函数：运行记忆维护"""
    print("🧠 开始三层记忆架构维护...")
    
    maintenance = MemoryMaintenance()
    
    # 1. 同步记忆文件
    maintenance.sync_from_memory_files()
    
    # 2. 运行激活衰减
    maintenance.run_daily_decay()
    
    # 3. 优化记忆存储
    maintenance.optimize_memory()
    
    # 4. 生成报告
    maintenance.generate_report()
    
    print("\n🎉 三层记忆架构维护完成！")
    print("   系统已升级，现在拥有:")
    print("   - 结构化知识图谱")
    print("   - 激活衰减机制")
    print("   - 自动同步功能")
    print("   - 优化存储管理")

if __name__ == "__main__":
    main()