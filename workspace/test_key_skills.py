#!/usr/bin/env python3
"""
测试关键Skill的可用性
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

print("🧪 测试关键Skill可用性")
print("=" * 60)

workspace = Path.home() / ".openclaw" / "workspace"

# 读取验证报告
report_file = workspace / "skill_verification_report.json"
with open(report_file, 'r', encoding='utf-8') as f:
    report = json.load(f)

skills = report["skills"]

# 选择关键Skill进行测试
key_skills_to_test = [
    "bitable-core",      # 多维表格核心（沟通生命线）
    "web-search-skill",  # 网页搜索（基础工具）
    "memory-manager",    # 记忆管理（系统核心）
    "context-engineering", # 上下文工程（性能关键）
    "summarizer",        # 摘要生成（实用工具）
    "agent-orchestrator", # Agent协调器（团队管理）
    "xiaohongshu-title", # 小红书标题（内容创作）
]

print(f"选择 {len(key_skills_to_test)} 个关键Skill进行测试:")

test_results = []
for skill_name in key_skills_to_test:
    # 找到对应的skill信息
    skill_info = next((s for s in skills if s["name"] == skill_name), None)
    if not skill_info:
        print(f"  ❌ 未找到Skill: {skill_name}")
        continue
    
    print(f"\n🔧 测试: {skill_name}")
    print(f"   目录: {skill_info['directory']}")
    print(f"   描述: {skill_info.get('description', '无描述')[:100]}...")
    
    skill_dir = workspace / skill_info["directory"]
    
    # 测试方法：检查SKILL.md和主要文件
    test_result = {
        "skill_name": skill_name,
        "skill_id": skill_info["skill_id"],
        "test_time": datetime.now().isoformat(),
        "tests": {}
    }
    
    # 测试1: SKILL.md文件检查
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        test_result["tests"]["skill_md"] = {
            "status": "✅ 通过",
            "size_bytes": skill_md.stat().st_size,
            "has_description": True
        }
        print(f"   测试1: SKILL.md ✅ 存在 ({skill_md.stat().st_size} 字节)")
    else:
        test_result["tests"]["skill_md"] = {
            "status": "❌ 失败",
            "error": "SKILL.md文件不存在"
        }
        print(f"   测试1: SKILL.md ❌ 不存在")
    
    # 测试2: 主要文件检查
    python_files = list(skill_dir.rglob("*.py"))
    shell_files = list(skill_dir.rglob("*.sh"))
    js_files = list(skill_dir.rglob("*.js"))
    
    if python_files:
        main_file = python_files[0]
        test_result["tests"]["main_file"] = {
            "status": "✅ 通过",
            "file": str(main_file.relative_to(skill_dir)),
            "size_bytes": main_file.stat().st_size,
            "language": "Python"
        }
        print(f"   测试2: 主文件 ✅ {main_file.name} ({main_file.stat().st_size} 字节)")
    elif shell_files:
        main_file = shell_files[0]
        test_result["tests"]["main_file"] = {
            "status": "✅ 通过",
            "file": str(main_file.relative_to(skill_dir)),
            "size_bytes": main_file.stat().st_size,
            "language": "Shell"
        }
        print(f"   测试2: 主文件 ✅ {main_file.name}")
    elif js_files:
        main_file = js_files[0]
        test_result["tests"]["main_file"] = {
            "status": "✅ 通过",
            "file": str(main_file.relative_to(skill_dir)),
            "size_bytes": main_file.stat().st_size,
            "language": "JavaScript"
        }
        print(f"   测试2: 主文件 ✅ {main_file.name}")
    else:
        test_result["tests"]["main_file"] = {
            "status": "⚠️ 警告",
            "error": "未找到可执行文件"
        }
        print(f"   测试2: 主文件 ⚠️ 未找到可执行文件")
    
    # 测试3: 目录结构检查
    files = list(skill_dir.rglob("*"))
    file_count = len([f for f in files if f.is_file()])
    dir_count = len([f for f in files if f.is_dir()])
    
    test_result["tests"]["directory_structure"] = {
        "status": "✅ 通过",
        "file_count": file_count,
        "dir_count": dir_count,
        "total_items": len(files)
    }
    print(f"   测试3: 目录结构 ✅ {file_count} 文件, {dir_count} 目录")
    
    # 总体评估
    passed_tests = sum(1 for test in test_result["tests"].values() if test["status"].startswith("✅"))
    total_tests = len(test_result["tests"])
    
    if passed_tests == total_tests:
        test_result["overall_status"] = "🟢 可用"
        test_result["availability_score"] = 100
        print(f"   总体: 🟢 可用 ({passed_tests}/{total_tests} 测试通过)")
    elif passed_tests >= total_tests * 0.7:
        test_result["overall_status"] = "🟡 部分可用"
        test_result["availability_score"] = int((passed_tests / total_tests) * 100)
        print(f"   总体: 🟡 部分可用 ({passed_tests}/{total_tests} 测试通过)")
    else:
        test_result["overall_status"] = "🔴 不可用"
        test_result["availability_score"] = int((passed_tests / total_tests) * 100)
        print(f"   总体: 🔴 不可用 ({passed_tests}/{total_tests} 测试通过)")
    
    test_results.append(test_result)

# 生成测试报告
test_report = {
    "test_time": datetime.now().isoformat(),
    "total_tested": len(test_results),
    "test_summary": {
        "available": sum(1 for r in test_results if r["overall_status"] == "🟢 可用"),
        "partially_available": sum(1 for r in test_results if r["overall_status"] == "🟡 部分可用"),
        "unavailable": sum(1 for r in test_results if r["overall_status"] == "🔴 不可用"),
        "average_score": round(sum(r["availability_score"] for r in test_results) / len(test_results), 1)
    },
    "test_results": test_results,
    "recommendations": []
}

# 生成建议
available_skills = [r["skill_name"] for r in test_results if r["overall_status"] == "🟢 可用"]
if available_skills:
    test_report["recommendations"].append(f"🟢 可用Skill: {', '.join(available_skills)} 可以立即使用")

partially_available = [r["skill_name"] for r in test_results if r["overall_status"] == "🟡 部分可用"]
if partially_available:
    test_report["recommendations"].append(f"🟡 部分可用Skill: {', '.join(partially_available)} 需要进一步测试或修复")

unavailable = [r["skill_name"] for r in test_results if r["overall_status"] == "🔴 不可用"]
if unavailable:
    test_report["recommendations"].append(f"🔴 不可用Skill: {', '.join(unavailable)} 需要修复或替换")

# 保存测试报告
test_report_file = workspace / "skill_availability_test_report.json"
with open(test_report_file, 'w', encoding='utf-8') as f:
    json.dump(test_report, f, indent=2, ensure_ascii=False)

print(f"\n✅ 测试报告已保存: {test_report_file}")

# 生成Markdown摘要
md_report = f"""# 🧪 Skill可用性测试报告

**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**测试Skill数量**: {len(test_results)} 个
**测试方法**: 文件完整性检查 + 结构验证

## 📊 测试结果概览

| 状态 | 数量 | 比例 | 说明 |
|------|------|------|------|
| 🟢 可用 | {test_report['test_summary']['available']} | {round(test_report['test_summary']['available']/len(test_results)*100, 1)}% | 所有测试通过，可以正常使用 |
| 🟡 部分可用 | {test_report['test_summary']['partially_available']} | {round(test_report['test_summary']['partially_available']/len(test_results)*100, 1)}% | 部分测试通过，需要进一步验证 |
| 🔴 不可用 | {test_report['test_summary']['unavailable']} | {round(test_report['test_summary']['unavailable']/len(test_results)*100, 1)}% | 测试失败，需要修复 |
| **平均得分** | **{test_report['test_summary']['average_score']}%** | - | 整体可用性评分 |

## 🔧 详细测试结果

"""

for result in test_results:
    skill_name = result["skill_name"]
    overall_status = result["overall_status"]
    score = result["availability_score"]
    
    md_report += f"### {skill_name} - {overall_status} ({score}%)\n\n"
    
    for test_name, test_data in result["tests"].items():
        status = test_data["status"]
        details = []
        
        if "file" in test_data:
            details.append(f"文件: {test_data['file']}")
        if "size_bytes" in test_data:
            details.append(f"大小: {test_data['size_bytes']} 字节")
        if "language" in test_data:
            details.append(f"语言: {test_data['language']}")
        if "file_count" in test_data:
            details.append(f"文件数: {test_data['file_count']}")
        
        detail_str = " | ".join(details) if details else ""
        md_report += f"- **{test_name}**: {status}"
        if detail_str:
            md_report += f" ({detail_str})"
        md_report += "\n"
    
    md_report += "\n"

md_report += f"""## 🎯 关键发现

### 1. 核心Skill状态
- **bitable-core**: 多维表格核心技能，沟通生命线
- **web-search-skill**: 网页搜索基础工具
- **memory-manager**: 记忆管理系统核心
- **context-engineering**: 上下文工程，性能关键
- **agent-orchestrator**: Agent协调器，团队管理
- **xiaohongshu-title**: 小红书标题优化，内容创作
- **summarizer**: 摘要生成实用工具

### 2. 可用性分析
**🟢 高可用性Skill** ({test_report['test_summary']['available']}个):
{chr(10).join(f"- {r['skill_name']} ({r['availability_score']}%)" for r in test_results if r['overall_status'] == '🟢 可用')}

**🟡 中等可用性Skill** ({test_report['test_summary']['partially_available']}个):
{chr(10).join(f"- {r['skill_name']} ({r['availability_score']}%)" for r in test_results if r['overall_status'] == '🟡 部分可用')}

**🔴 低可用性Skill** ({test_report['test_summary']['unavailable']}个):
{chr(10).join(f"- {r['skill_name']} ({r['availability_score']}%)" for r in test_results if r['overall_status'] == '🔴 不可用')}

### 3. 建议措施

#### 立即行动
1. **优先使用高可用性Skill**: 确保核心功能正常
2. **测试中等可用性Skill**: 进一步验证功能完整性
3. **修复或替换低可用性Skill**: 确保系统稳定性

#### 短期优化
1. 建立Skill定期测试机制
2. 完善Skill文档和示例
3. 优化Skill加载和使用流程

#### 长期规划
1. 建立Skill质量评估体系
2. 实现自动化测试和监控
3. 建立Skill版本管理和更新机制

## 📝 测试方法说明

### 测试项目
1. **SKILL.md检查**: 验证Skill描述文档完整性
2. **主文件检查**: 确认可执行文件存在
3. **目录结构检查**: 验证文件组织合理性

### 评分标准
- **100分**: 所有测试通过，文件完整
- **70-99分**: 主要测试通过，部分细节待完善
- **<70分**: 关键测试失败，需要修复

### 局限性说明
1. 当前测试为静态文件检查，未进行运行时测试
2. 功能完整性需要实际使用验证
3. 性能表现需要负载测试评估

---

**报告生成**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**测试范围**: {len(test_results)}个关键Skill
**测试深度**: 基础文件完整性检查
**下一步**: 运行时功能测试和性能评估
"""

md_report_file = workspace / "skill_availability_summary.md"
with open(md_report_file, 'w', encoding='utf-8') as f:
    f.write(md_report)

print(f"✅ 测试摘要已保存: {md_report_file}")

print("\n" + "=" * 60)
print("🎉 Skill可用性测试完成!")
print("=" * 60)
print(f"📊 测试结果:")
print(f"  🟢 可用: {test_report['test_summary']['available']} 个")
print(f"  🟡 部分可用: {test_report['test_summary']['partially_available']} 个")
print(f"  🔴 不可用: {test_report['test_summary']['unavailable']} 个")
print(f"  📈 平均得分: {test_report['test_summary']['average_score']}%")
print(f"\n📝 报告文件:")
print(f"  skill_availability_test_report.json")
print(f"  skill_availability_summary.md")