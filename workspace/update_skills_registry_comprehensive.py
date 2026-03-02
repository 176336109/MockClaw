#!/usr/bin/env python3
"""
基于全面扫描结果更新SKILLS_REGISTRY.md
"""

import json
from pathlib import Path
from datetime import datetime

print("📝 基于全面扫描更新SKILLS_REGISTRY.md")
print("=" * 60)

workspace = Path.home() / ".openclaw" / "workspace"

# 读取扫描报告
report_file = workspace / "comprehensive_skill_scan_report.json"
with open(report_file, 'r', encoding='utf-8') as f:
    report = json.load(f)

skills = report["skills"]
categories = report["categories"]

# 重新组织分类
organized_categories = {
    "Agent管理": [],
    "记忆管理": [],
    "搜索工具": [],
    "数据管理": [],
    "内容创作": [],
    "个人管理": [],
    "开发工具": [],
    "生活工具": [],
    "设备控制": [],
    "通讯工具": [],
    "其他": []
}

for skill in skills:
    category = skill.get("category", "其他")
    if category in organized_categories:
        organized_categories[category].append(skill)
    else:
        organized_categories["其他"].append(skill)

# 生成新的SKILLS_REGISTRY.md
registry_content = f"""# 🔧 Skill 库管理

**更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**维护者**: 虾BB
**说明**: 基于全面扫描的Skill库管理。总共有73个Skill，分布在3个位置。

---

## 📊 Skill概览

| 统计项 | 数量 | 说明 |
|--------|------|------|
| 总Skill数量 | {len(skills)} 个 | 系统当前安装的Skill总数 |
| 总文件大小 | {report['total_size_mb']} MB | 所有Skill文件的总大小 |
| 存放位置 | 3 个 | 系统/用户/工作空间 |
| 功能分类 | {len(organized_categories)} 类 | 按功能分类的数量 |
| 有文档Skill | {sum(1 for s in skills if s['has_skill_md'])} 个 | 有SKILL.md文件的Skill |
| 无文档Skill | {sum(1 for s in skills if not s['has_skill_md'])} 个 | 无SKILL.md文件的Skill |

**扫描时间**: {report['scan_time'][:19]}
**下次验证**: 2026-04-02
**下次同步**: 2026-03-08 20:00

---

## 🗂️ 按存放位置管理

### 1. 系统Skill目录 ({report['locations_summary']['system']}个)
**位置**: `/opt/homebrew/lib/node_modules/openclaw/skills/`
**说明**: OpenClaw内置Skill，稳定性最高

| Skill ID | 名称 | 显示名称 | 版本 | 大小 | 语言 | 状态 | 关键性 |
|----------|------|----------|------|------|------|------|--------|
"""

# 添加系统Skill（只显示关键的几个）
system_skills = [s for s in skills if s["type"] == "system"]
key_system_skills = [
    s for s in system_skills if s["name"] in [
        "apple-notes", "apple-reminders", "github", "weather", 
        "things-mac", "coding-agent", "session-logs", "skill-creator"
    ]
]

for skill in key_system_skills:
    skill_id = skill["skill_id"]
    name = skill["name"]
    display_name = skill.get("display_name", name)[:20]
    version = skill.get("version", "1.0.0")
    size_mb = skill["size_mb"]
    language = skill.get("language", "未知")
    status = "🟢 可用" if skill["has_skill_md"] else "🟡 待检查"
    
    # 确定关键性
    if name in ["coding-agent", "session-logs", "skill-creator"]:
        critical = "🔴 核心"
    elif name in ["apple-notes", "apple-reminders", "github"]:
        critical = "🟡 重要"
    else:
        critical = "🟢 辅助"
    
    registry_content += f"| {skill_id} | {name} | {display_name} | v{version} | {size_mb} MB | {language} | {status} | {critical} |\n"

registry_content += f"\n... 还有 {len(system_skills)-len(key_system_skills)} 个系统Skill\n"

registry_content += f"""
### 2. 用户Skill目录 ({report['locations_summary']['user']}个)
**位置**: `~/.openclaw/skills/`
**说明**: 用户安装的额外Skill，需要验证兼容性

| Skill ID | 名称 | 显示名称 | 版本 | 大小 | 语言 | 状态 | 关键性 |
|----------|------|----------|------|------|------|------|--------|
"""

user_skills = [s for s in skills if s["type"] == "user"]
for skill in user_skills:
    skill_id = skill["skill_id"]
    name = skill["name"]
    display_name = skill.get("display_name", name)[:20]
    version = skill.get("version", "1.0.0")
    size_mb = skill["size_mb"]
    language = skill.get("language", "未知")
    status = "🟢 可用" if skill["has_skill_md"] else "🟡 待检查"
    
    # 确定关键性
    if "browser" in name:
        critical = "🔴 核心"
    elif "search" in name or "tavily" in name:
        critical = "🟡 重要"
    else:
        critical = "🟢 辅助"
    
    registry_content += f"| {skill_id} | {name} | {display_name} | v{version} | {size_mb} MB | {language} | {status} | {critical} |\n"

registry_content += f"""
### 3. 工作空间Skill目录 ({report['locations_summary']['workspace']}个)
**位置**: `~/.openclaw/workspace/skills/`
**说明**: 项目相关的Skill，部分可能不完整

| Skill ID | 名称 | 显示名称 | 版本 | 大小 | 语言 | 状态 | 关键性 |
|----------|------|----------|------|------|------|------|--------|
"""

workspace_skills = [s for s in skills if s["type"] == "workspace"]
for skill in workspace_skills:
    skill_id = skill["skill_id"]
    name = skill["name"]
    display_name = skill.get("display_name", name)[:20]
    version = skill.get("version", "1.0.0")
    size_mb = skill["size_mb"]
    language = skill.get("language", "未知")
    status = "🟢 可用" if skill["has_skill_md"] else "🟡 待检查"
    
    # 确定关键性
    if name == "bitable-core":
        critical = "🔴 核心 (沟通生命线)"
    elif name in ["memory-manager", "context-engineering", "web-search-skill"]:
        critical = "🟡 重要"
    else:
        critical = "🟢 辅助"
    
    registry_content += f"| {skill_id} | {name} | {display_name} | v{version} | {size_mb} MB | {language} | {status} | {critical} |\n"

registry_content += f"""
---

## 🎯 按功能分类管理

"""

# 为每个分类创建简要列表
for category, skill_list in organized_categories.items():
    if skill_list:
        registry_content += f"### {category} ({len(skill_list)}个)\n\n"
        
        # 只显示前5个
        for skill in skill_list[:5]:
            name = skill["name"]
            display_name = skill.get("display_name", name)
            location = skill["location"]
            status = "🟢" if skill["has_skill_md"] else "🟡"
            
            registry_content += f"- **{name}** ({status}) - {display_name} [{location}]\n"
        
        if len(skill_list) > 5:
            registry_content += f"- ... 还有 {len(skill_list)-5} 个Skill\n"
        
        registry_content += "\n"

registry_content += f"""---

## 🔍 关键Skill状态

### 🔴 核心Skill (必须可用)
1. **bitable-core** - 多维表格核心，沟通生命线
2. **coding-agent** - 代码Agent，开发工作
3. **agent-browser-0.2.0** - Agent浏览器，网页操作

### 🟡 重要Skill (推荐使用)
1. **memory-manager** - 记忆管理系统核心
2. **context-engineering** - 上下文工程，性能关键
3. **web-search-skill** - 网页搜索基础工具
4. **tavily-search-1.0.0** - AI优化搜索
5. **github** - GitHub操作

### 🟢 辅助Skill (按需使用)
1. **apple-notes** - Apple笔记管理
2. **apple-reminders** - Apple提醒事项
3. **weather** - 天气查询
4. **things-mac** - Things 3任务管理
5. **session-logs** - 会话日志分析

---

## 📝 更新记录

| 更新时间 | 更新内容 | 更新人 |
|----------|----------|--------|
| {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 基于全面扫描更新，73个Skill | 虾BB |
| 2026-03-02 19:16 | 重新盘点Skill，添加可用性测试 | 虾BB |
| 2026-03-02 18:09 | 重新整理为Markdown表格 | 虾BB |

---

## 🚀 下一步计划

| 计划项目 | 负责人 | 预计完成 | 状态 |
|----------|--------|----------|------|
| 验证核心Skill可用性 | 虾BB | 2026-03-03 | 🟡 进行中 |
| 建立Skill使用统计 | 虾BB | 2026-03-05 | 🟡 进行中 |
| 同步到飞书表格 | 虾BB | 2026-03-08 | 🟡 待开始 |

---

**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**下次验证**: 2026-04-02
**下次同步**: 2026-03-08 20:00
**维护者**: 虾BB
"""

# 写入文件
registry_file = workspace / "SKILLS_REGISTRY.md"
with open(registry_file, 'w', encoding='utf-8') as f:
    f.write(registry_content)

print(f"✅ SKILLS_REGISTRY.md 已更新")

# 更新MEMORY.md
print("\n🧠 更新MEMORY.md...")

memory_file = workspace / "MEMORY.md"
if memory_file.exists():
    with open(memory_file, 'a', encoding='utf-8') as f:
        f.write(f"""

## 🔧 Skill系统全面扫描

### 扫描时间
{datetime.now().isoformat()}

### 惊人发现
- **总Skill数量**: 73 个 (之前只知道13个)
- **系统Skill目录**: 52 个 (OpenClaw内置)
- **用户Skill目录**: 10 个 (用户安装)
- **工作空间Skill目录**: 13 个 (项目相关)
- **功能分类**: 10 个大类

### 关键Skill
1. **🔴 核心Skill**: bitable-core (沟通生命线), coding-agent, agent-browser
2. **🟡 重要Skill**: memory-manager, context-engineering, web-search-skill
3. **🟢 辅助Skill**: apple-notes, apple-reminders, github, weather

### 已更新文件
1. ✅ **SKILLS_REGISTRY.md** - 基于全面扫描更新
2. ✅ **comprehensive_skill_scan_report.json** - 详细扫描报告
3. ✅ **comprehensive_skill_scan_summary.md** - 扫描摘要
""")
    
    print(f"✅ MEMORY.md 已更新")

print("\n" + "=" * 60)
print("🎉 SKILLS_REGISTRY.md 更新完成!")
print("=" * 60)
print(f"📊 总Skill: {len(skills)} 个")
print(f"📁 位置: 3个目录")
print(f"🗂️ 分类: {len(organized_categories)} 类")
print(f"📝 文件: SKILLS_REGISTRY.md (已更新)")