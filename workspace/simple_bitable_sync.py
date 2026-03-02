#!/usr/bin/env python3
"""
简单同步到飞书多维表格
"""

import sys
from pathlib import Path

workspace = Path.home() / ".openclaw" / "workspace"

print("🔄 准备同步到飞书多维表格")
print("=" * 50)

# 显示需要同步的内容
print("\n📋 需要同步的内容:")
print("=" * 50)

# 1. Agent信息
print("\n1. AGENTS_REGISTRY.md 更新:")
print("-" * 30)
agents_file = workspace / "AGENTS_REGISTRY.md"
with open(agents_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    # 找到Agent表格
    in_table = False
    for i, line in enumerate(lines):
        if "| Agent ID | 名称 | 职能 |" in line:
            in_table = True
            print(line.rstrip())
        elif in_table and "|----------|------|------|" in line:
            print(line.rstrip())
        elif in_table and "| AG_" in line:
            print(line.rstrip())
        elif in_table and not line.strip().startswith("|"):
            break

# 2. 任务信息
print("\n2. TASKS_REGISTRY.md 更新:")
print("-" * 30)
tasks_file = workspace / "TASKS_REGISTRY.md"
with open(tasks_file, 'r', encoding='utf-8') as f:
    content = f.read()
    
    # 查找最新任务
    if "TASK_20260302_004" in content:
        print("新增任务: TASK_20260302_004")
        print("名称: Skill系统全面扫描")
        print("状态: ✅ 完成")
        print("时间: 2026-03-02 19:31 → 19:33")
        print("成果: 扫描3个目录，发现73个Skill")

# 3. Skill信息
print("\n3. SKILLS_REGISTRY.md 更新:")
print("-" * 30)
skills_file = workspace / "SKILLS_REGISTRY.md"
with open(skills_file, 'r', encoding='utf-8') as f:
    content = f.read()
    
    # 提取关键信息
    if "总Skill数量" in content:
        lines = content.split('\n')
        for line in lines:
            if "总Skill数量" in line or "系统Skill目录" in line or "用户Skill目录" in line:
                print(line.strip())

print("\n" + "=" * 50)
print("🎯 同步指令:")

print("\n请手动更新飞书多维表格:")
print("1. 打开: https://t33vwocwc8.feishu.cn/base/FCRNbSo4ja4hCEs5411cNZQXnkh")
print("2. 更新以下内容:")

print("\n📊 Agent表 (更新):")
print("- 添加: AG_005 CodeMaster (代码专家)")
print("- 添加: AG_006 Scribe (书记员)")
print("- 添加: AG_007 Inspector (检查员)")
print("- 状态: 🟡 待分配")

print("\n📋 任务表 (添加):")
print("- 任务ID: TASK_20260302_004")
print("- 名称: Skill系统全面扫描")
print("- 状态: ✅ 完成")
print("- 时间: 2026-03-02 19:31 → 19:33")
print("- 成果: 发现73个Skill")

print("\n🔧 Skill表 (更新):")
print("- 总数量: 73个 (之前13个)")
print("- 系统Skill: 52个")
print("- 用户Skill: 10个")
print("- 工作空间Skill: 13个")
print("- 关键Skill: bitable-core, coding-agent, agent-browser")

print("\n" + "=" * 50)
print("✅ 同步信息准备完成")
print("请根据以上内容更新飞书多维表格")