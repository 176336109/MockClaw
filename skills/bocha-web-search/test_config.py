#!/usr/bin/env python3
"""
测试技能配置读取
"""
import os
import sys

# 添加当前目录到Python路径
sys.path.append('.')

print("=== 测试技能配置读取 ===")

# 测试1：检查环境变量
print("\n1. 检查环境变量:")
print(f"   BOCHA_API_KEY in env: {'BOCHA_API_KEY' in os.environ}")
print(f"   BOCHA_API_KEY value: {os.getenv('BOCHA_API_KEY', 'NOT FOUND')}")

# 测试2：模拟技能读取配置
print("\n2. 模拟技能配置读取:")
try:
    # 尝试导入技能模块
    from bocha_web_search import BochaWebSearch
    
    # 创建实例（不传api_key，让它从环境变量读取）
    search = BochaWebSearch()
    
    print(f"   API Key设置: {search.api_key[:10]}..." if search.api_key else "   API Key: NOT FOUND")
    print(f"   Mock模式: {search.mock_mode}")
    print(f"   Endpoint: {search.endpoint}")
    print(f"   Timeout: {search.timeout}")
    print(f"   Debug模式: {search.debug}")
    
except Exception as e:
    print(f"   导入失败: {e}")

print("\n=== 测试完成 ===")
