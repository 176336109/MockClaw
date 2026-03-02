#!/usr/bin/env python3
"""
启动集成工作流系统（修复版）
"""

import sys
import time
from pathlib import Path

# 修复模块导入路径
skill_dir = Path.home() / ".openclaw" / "workspace" / "skills" / "bitable-core"
sys.path.insert(0, str(skill_dir))

try:
    from integrated_workflow import IntegratedWorkflow
    
    print("=" * 60)
    print("🚀 启动集成工作流系统")
    print("=" * 60)
    print()
    
    # 创建实例
    workflow = IntegratedWorkflow()
    
    print("系统组件检查:")
    print(f"  ✅ Session优化器: {'已加载' if workflow.session_optimizer else '未加载'}")
    print(f"  ✅ 状态反馈系统: {'已加载' if workflow.feedback_system else '未加载'}")
    print(f"  ✅ 多维表格核心: {'已加载' if workflow.bitable_core else '未加载'}")
    print(f"  ✅ 共享记忆库: {'已加载' if workflow.memory_system else '未加载'}")
    print()
    
    print("开始启动所有系统...")
    print()
    
    # 启动所有系统
    report = workflow.start_all()
    
    print()
    print("=" * 60)
    print("🎉 集成工作流启动完成！")
    print("=" * 60)
    print()
    
    print("📊 启动报告:")
    print(f"  整体健康: {report['health']['overall']}")
    print(f"  Session消息: {report['session'].get('message_count', 0)}条")
    print(f"  上下文大小: {report['session'].get('context_size_kb', 0)}KB")
    print(f"  压缩率: {report['session'].get('compression_rate', 0)}%")
    print()
    
    print("💡 优化建议:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    print()
    
    print("🌐 监控信息:")
    print("  状态监控: http://localhost:8080/")
    print("  多维表格: https://t33vwocwc8.feishu.cn/base/FCRNbSo4ja4hCEs5411cNZQXnkh")
    print()
    
    print("📝 你现在可以:")
    print("  1. 连续对话，系统会自动管理上下文")
    print("  2. 随时查看我的工作状态（心跳每30秒）")
    print("  3. 任务状态自动同步到多维表格")
    print("  4. 长时间任务会有进度反馈")
    print()
    
    print("🤖 系统运行中...")
    print("按 Ctrl+C 停止系统")
    print()
    
    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        print("收到停止信号...")
        if workflow.feedback_system:
            workflow.feedback_system.update_status('completed', '集成工作流', 100, '系统正常停止')
        print("系统已停止")
        print("再见！👋")
        
except Exception as e:
    print(f"❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()
    
    # 尝试简化启动
    print("\n尝试简化启动...")
    try:
        # 只启动状态反馈系统
        from status_feedback_system import feedback_system
        feedback_system.start_heartbeat()
        feedback_system.update_status('working', '简化启动', 50, '启动基本状态反馈系统')
        
        print("✅ 状态反馈系统已启动")
        print("心跳机制运行中，你可以知道我的工作状态")
        print("按 Ctrl+C 停止")
        
        while True:
            time.sleep(1)
            
    except Exception as e2:
        print(f"❌ 简化启动也失败: {e2}")