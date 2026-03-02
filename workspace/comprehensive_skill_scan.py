#!/usr/bin/env python3
"""
全面扫描所有Skill存放位置
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
import re

print("🔍 全面扫描Skill系统")
print("=" * 60)

# Skill存放位置
skill_locations = [
    {
        "name": "系统Skill目录",
        "path": Path("/opt/homebrew/lib/node_modules/openclaw/skills/"),
        "type": "system"
    },
    {
        "name": "用户Skill目录", 
        "path": Path.home() / ".openclaw" / "skills",
        "type": "user"
    },
    {
        "name": "工作空间Skill目录",
        "path": Path.home() / ".openclaw" / "workspace" / "skills",
        "type": "workspace"
    }
]

# 收集所有Skill
all_skills = []
skill_categories = {}

for location in skill_locations:
    if not location["path"].exists():
        print(f"❌ {location['name']} 不存在: {location['path']}")
        continue
    
    print(f"\n📁 扫描: {location['name']} ({location['path']})")
    
    for item in location["path"].iterdir():
        if item.is_dir() and item.name != "." and item.name != "..":
            skill_md = item / "SKILL.md"
            
            skill_info = {
                "skill_id": f"SK_{len(all_skills)+1:04d}",
                "name": item.name,
                "location": location["name"],
                "path": str(item),
                "type": location["type"],
                "has_skill_md": skill_md.exists(),
                "size_mb": round(sum(f.stat().st_size for f in item.rglob('*') if f.is_file()) / 1024 / 1024, 3),
                "scan_time": datetime.now().isoformat()
            }
            
            # 读取SKILL.md获取信息
            if skill_md.exists():
                try:
                    with open(skill_md, 'r', encoding='utf-8') as f:
                        content = f.read(5000)
                    
                    # 提取基本信息
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('# '):
                            skill_info["display_name"] = line[2:].strip()
                        elif "description" in line.lower() and ":" in line:
                            skill_info["description"] = line.split(":", 1)[1].strip()[:200]
                        elif "version" in line.lower() and ":" in line:
                            skill_info["version"] = line.split(":", 1)[1].strip()
                        elif "category" in line.lower() and ":" in line:
                            skill_info["category"] = line.split(":", 1)[1].strip()
                        elif "author" in line.lower() and ":" in line:
                            skill_info["author"] = line.split(":", 1)[1].strip()
                            
                except Exception as e:
                    skill_info["parse_error"] = str(e)
            else:
                skill_info["description"] = "无SKILL.md文件"
                skill_info["version"] = "1.0.0"
            
            # 检查文件类型
            python_files = list(item.rglob("*.py"))
            shell_files = list(item.rglob("*.sh"))
            js_files = list(item.rglob("*.js"))
            
            if python_files:
                skill_info["language"] = "Python"
                skill_info["main_file"] = str(python_files[0].relative_to(item))
            elif shell_files:
                skill_info["language"] = "Shell"
                skill_info["main_file"] = str(shell_files[0].relative_to(item))
            elif js_files:
                skill_info["language"] = "JavaScript"
                skill_info["main_file"] = str(js_files[0].relative_to(item))
            else:
                skill_info["language"] = "未知"
                skill_info["main_file"] = "无"
            
            # 分类
            name_lower = item.name.lower()
            if any(keyword in name_lower for keyword in ["agent", "orchestrator", "council", "team"]):
                category = "Agent管理"
            elif any(keyword in name_lower for keyword in ["memory", "context", "summarizer"]):
                category = "记忆管理"
            elif any(keyword in name_lower for keyword in ["search", "web"]):
                category = "搜索工具"
            elif any(keyword in name_lower for keyword in ["bitable", "table", "sheet"]):
                category = "数据管理"
            elif any(keyword in name_lower for keyword in ["content", "writer", "generator", "scheduler", "title"]):
                category = "内容创作"
            elif any(keyword in name_lower for keyword in ["notes", "reminders", "todo"]):
                category = "个人管理"
            elif any(keyword in name_lower for keyword in ["github", "git"]):
                category = "开发工具"
            elif any(keyword in name_lower for keyword in ["weather", "time"]):
                category = "生活工具"
            elif any(keyword in name_lower for keyword in ["camera", "screen", "audio"]):
                category = "设备控制"
            elif any(keyword in name_lower for keyword in ["discord", "telegram", "feishu"]):
                category = "通讯工具"
            else:
                category = "其他"
            
            skill_info["category"] = category
            
            if category not in skill_categories:
                skill_categories[category] = []
            skill_categories[category].append(skill_info["skill_id"])
            
            all_skills.append(skill_info)
            
            # 显示进度
            status = "✅" if skill_md.exists() else "⚠️"
            print(f"  {status} {skill_info['skill_id']}: {item.name}")

print(f"\n📊 扫描完成!")
print(f"总Skill数量: {len(all_skills)} 个")
print(f"分类数量: {len(skill_categories)} 类")

# 生成详细报告
report = {
    "scan_time": datetime.now().isoformat(),
    "total_skills": len(all_skills),
    "total_size_mb": round(sum(s["size_mb"] for s in all_skills), 3),
    "locations_summary": {
        "system": len([s for s in all_skills if s["type"] == "system"]),
        "user": len([s for s in all_skills if s["type"] == "user"]),
        "workspace": len([s for s in all_skills if s["type"] == "workspace"])
    },
    "categories": skill_categories,
    "skills": all_skills
}

# 保存报告
workspace = Path.home() / ".openclaw" / "workspace"
report_file = workspace / "comprehensive_skill_scan_report.json"
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n✅ 详细报告已保存: {report_file}")

# 生成Markdown摘要
md_summary = f"""# 🔍 全面Skill扫描报告

**扫描时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**总Skill数量**: {len(all_skills)} 个
**总文件大小**: {report['total_size_mb']} MB
**存放位置**: 3个目录

## 📊 概览统计

### 按存放位置
| 位置 | 数量 | 比例 | 说明 |
|------|------|------|------|
| 系统Skill目录 | {report['locations_summary']['system']} | {round(report['locations_summary']['system']/len(all_skills)*100, 1)}% | OpenClaw内置Skill |
| 用户Skill目录 | {report['locations_summary']['user']} | {round(report['locations_summary']['user']/len(all_skills)*100, 1)}% | 用户安装的Skill |
| 工作空间Skill目录 | {report['locations_summary']['workspace']} | {round(report['locations_summary']['workspace']/len(all_skills)*100, 1)}% | 项目相关的Skill |

### 按功能分类
| 分类 | 数量 | 比例 | 说明 |
|------|------|------|------|
"""

for category, skill_ids in skill_categories.items():
    count = len(skill_ids)
    percentage = round(count/len(all_skills)*100, 1)
    md_summary += f"| {category} | {count} | {percentage}% | {', '.join(skill_ids[:3])}{'...' if len(skill_ids) > 3 else ''} |\n"

md_summary += f"""
## 🎯 关键发现

### 1. Skill数量巨大
- **总数量**: {len(all_skills)} 个Skill (之前只知道13个)
- **系统Skill**: {report['locations_summary']['system']} 个 (内置功能)
- **用户Skill**: {report['locations_summary']['user']} 个 (额外安装)
- **工作空间Skill**: {report['locations_summary']['workspace']} 个 (项目相关)

### 2. 功能分类丰富
- **Agent管理**: {len(skill_categories.get('Agent管理', []))} 个
- **记忆管理**: {len(skill_categories.get('记忆管理', []))} 个
- **搜索工具**: {len(skill_categories.get('搜索工具', []))} 个
- **数据管理**: {len(skill_categories.get('数据管理', []))} 个
- **内容创作**: {len(skill_categories.get('内容创作', []))} 个
- **个人管理**: {len(skill_categories.get('个人管理', []))} 个
- **开发工具**: {len(skill_categories.get('开发工具', []))} 个
- **其他**: {len(skill_categories.get('其他', []))} 个

### 3. 文档完整性
- **有SKILL.md**: {sum(1 for s in all_skills if s['has_skill_md'])} 个
- **无SKILL.md**: {sum(1 for s in all_skills if not s['has_skill_md'])} 个
- **文档比例**: {round(sum(1 for s in all_skills if s['has_skill_md'])/len(all_skills)*100, 1)}%

## 📋 详细清单

### 系统Skill目录 ({report['locations_summary']['system']}个)
"""

# 按位置分组显示
for location in skill_locations:
    location_skills = [s for s in all_skills if s["location"] == location["name"]]
    if location_skills:
        md_summary += f"\n### {location['name']} ({len(location_skills)}个)\n\n"
        md_summary += "| Skill ID | 名称 | 显示名称 | 版本 | 大小 | 语言 | 分类 | 状态 |\n"
        md_summary += "|----------|------|----------|------|------|------|------|------|\n"
        
        for skill in location_skills[:20]:  # 只显示前20个
            skill_id = skill["skill_id"]
            name = skill["name"]
            display_name = skill.get("display_name", name)[:20]
            version = skill.get("version", "1.0.0")
            size_mb = skill["size_mb"]
            language = skill.get("language", "未知")
            category = skill.get("category", "其他")
            status = "🟢" if skill["has_skill_md"] else "🟡"
            
            md_summary += f"| {skill_id} | {name} | {display_name} | v{version} | {size_mb} MB | {language} | {category} | {status} |\n"
        
        if len(location_skills) > 20:
            md_summary += f"\n... 还有 {len(location_skills)-20} 个Skill\n"

md_summary += f"""
## 🔧 可用性分析

### 高可用性Skill (推荐优先使用)
1. **系统Skill目录** - 内置Skill，稳定性高
2. **有完整文档的Skill** - 有SKILL.md文件
3. **有可执行文件的Skill** - 有.py/.sh/.js文件

### 需要验证的Skill
1. **无文档的Skill** - 需要测试功能
2. **工作空间Skill** - 项目相关，可能不完整
3. **用户安装的Skill** - 需要验证兼容性

## 🚀 建议措施

### 立即行动
1. **建立Skill索引** - 创建完整的Skill目录
2. **验证核心Skill** - 测试关键功能的可用性
3. **更新SKILLS_REGISTRY.md** - 反映真实Skill状态

### 短期计划
1. **分类整理** - 按功能重新组织Skill
2. **建立测试机制** - 定期验证Skill可用性
3. **优化加载策略** - 按需加载Skill，减少内存占用

### 长期规划
1. **建立Skill质量体系** - 标准化Skill开发
2. **实现自动化管理** - Skill安装、更新、卸载
3. **建立Skill市场** - 分享和发现新Skill

## 📝 扫描方法

### 扫描范围
1. **系统Skill目录**: /opt/homebrew/lib/node_modules/openclaw/skills/
2. **用户Skill目录**: ~/.openclaw/skills/
3. **工作空间Skill目录**: ~/.openclaw/workspace/skills/

### 扫描内容
1. **基本信息**: 名称、路径、大小
2. **文档信息**: SKILL.md内容解析
3. **文件类型**: 可执行文件检查
4. **功能分类**: 基于名称和描述的自动分类

### 局限性
1. **静态分析**: 只检查文件，未测试功能
2. **分类准确度**: 基于名称的自动分类可能不准确
3. **兼容性**: 未检查与当前系统的兼容性

---

**报告生成**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**扫描范围**: 3个Skill存放位置
**扫描深度**: 基本信息 + 文档解析
**下一步**: 验证关键Skill的可用性
"""

summary_file = workspace / "comprehensive_skill_scan_summary.md"
with open(summary_file, 'w', encoding='utf-8') as f:
    f.write(md_summary)

print(f"✅ 扫描摘要已保存: {summary_file}")

print("\n" + "=" * 60)
print("🎉 全面Skill扫描完成!")
print("=" * 60)
print(f"📊 发现: {len(all_skills)} 个Skill")
print(f"📁 位置: 3个存放目录")
print(f"🗂️ 分类: {len(skill_categories)} 个功能类别")
print(f"💾 大小: {report['total_size_mb']} MB")
print(f"\n📝 报告文件:")
print(f"  comprehensive_skill_scan_report.json")
print(f"  comprehensive_skill_scan_summary.md")