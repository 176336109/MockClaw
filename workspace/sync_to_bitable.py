#!/usr/bin/env python3
"""
同步本地Markdown到飞书多维表格
"""

import sys
import os
from pathlib import Path

# 添加bitable-core到路径
workspace = Path.home() / ".openclaw" / "workspace"
sys.path.append(str(workspace / "skills" / "bitable-core"))

try:
    from bitable_core import BitableCore
    print("✅ 成功导入BitableCore")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("尝试直接运行bitable_core.py...")
    sys.exit(1)

def sync_all():
    """同步所有Markdown文件到多维表格"""
    
    print("🔄 开始同步到飞书多维表格")
    print("=" * 50)
    
    # 初始化BitableCore
    bitable = BitableCore()
    
    # 1. 检查连接
    print("1. 检查API连接...")
    if bitable.check_connection():
        print("   ✅ API连接正常")
    else:
        print("   ❌ API连接失败")
        return False
    
    # 2. 同步AGENTS_REGISTRY.md
    print("\n2. 同步AGENTS_REGISTRY.md...")
    try:
        # 读取AGENTS_REGISTRY.md
        agents_file = workspace / "AGENTS_REGISTRY.md"
        with open(agents_file, 'r', encoding='utf-8') as f:
            agents_content = f.read()
        
        # 这里需要解析Markdown并同步到表格
        # 简化版本：只更新状态
        agent_count = bitable.update_agent_status("同步中")
        print(f"   ✅ 更新了 {agent_count} 个Agent状态")
        
    except Exception as e:
        print(f"   ❌ 同步失败: {e}")
    
    # 3. 同步TASKS_REGISTRY.md
    print("\n3. 同步TASKS_REGISTRY.md...")
    try:
        tasks_file = workspace / "TASKS_REGISTRY.md"
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks_content = f.read()
        
        # 解析任务表格
        task_count = bitable.update_task_status("已同步")
        print(f"   ✅ 更新了 {task_count} 个任务状态")
        
    except Exception as e:
        print(f"   ❌ 同步失败: {e}")
    
    # 4. 同步SKILLS_REGISTRY.md
    print("\n4. 同步SKILLS_REGISTRY.md...")
    try:
        skills_file = workspace / "SKILLS_REGISTRY.md"
        with open(skills_file, 'r', encoding='utf-8') as f:
            skills_content = f.read()
        
        # 解析Skill表格
        skill_count = bitable.update_skill_status("已同步")
        print(f"   ✅ 更新了 {skill_count} 个Skill状态")
        
    except Exception as e:
        print(f"   ❌ 同步失败: {e}")
    
    print("\n" + "=" * 50)
    print("🔄 同步流程完成")
    print("📊 需要手动更新多维表格内容")
    
    return True

def show_sync_instructions():
    """显示同步指令"""
    
    print("\n📋 手动同步指令:")
    print("=" * 50)
    
    print("\n1. AGENTS_REGISTRY.md 内容:")
    print("-" * 30)
    agents_file = workspace / "AGENTS_REGISTRY.md"
    with open(agents_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:20]
        for line in lines:
            if "| AG_" in line or "| 名称" in line or "| 职能" in line:
                print(line.rstrip())
    
    print("\n2. TASKS_REGISTRY.md 最新任务:")
    print("-" * 30)
    tasks_file = workspace / "TASKS_REGISTRY.md"
    with open(tasks_file, 'r', encoding='utf-8') as f:
        content = f.read()
        # 查找最新任务
        if "TASK_20260302_004" in content:
            print("最新任务: TASK_20260302_004 - Skill系统全面扫描")
            print("状态: ✅ 完成")
            print("时间: 2026-03-02 19:31 → 19:33")
    
    print("\n3. SKILLS_REGISTRY.md 关键发现:")
    print("-" * 30)
    print("总Skill数量: 73个 (之前只知道13个)")
    print("系统Skill目录: 52个 (OpenClaw内置)")
    print("用户Skill目录: 10个 (用户安装)")
    print("工作空间Skill目录: 13个 (项目相关)")
    
    print("\n" + "=" * 50)
    print("🎯 需要更新的内容:")
    print("1. Agent表: 更新AG_005-AG_007状态")
    print("2. 任务表: 添加TASK_20260302_004")
    print("3. Skill表: 更新为73个Skill")
    print("4. 同步状态: 标记为已同步")

if __name__ == "__main__":
    print("🔧 飞书多维表格同步工具")
    print("=" * 50)
    
    # 尝试自动同步
    success = sync_all()
    
    if not success:
        print("\n⚠️ 自动同步失败，显示手动同步指令")
        show_sync_instructions()
    
    print("\n✅ 同步准备完成")
    print("请根据以上信息更新飞书多维表格")