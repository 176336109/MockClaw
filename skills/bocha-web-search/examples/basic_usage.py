#!/usr/bin/env python3
"""
博查AI Web Search基础使用示例
"""

import sys
import os

# 添加父目录到路径，以便导入bocha_web_search
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bocha_web_search import BochaWebSearch


def main():
    """基础使用示例"""
    print("=== 博查AI Web Search基础使用示例 ===\n")
    
    # 方法1：使用环境变量中的API KEY
    print("方法1：使用环境变量中的API KEY")
    print("-" * 50)
    
    # 检查是否有API KEY
    api_key = os.getenv("BOCHA_API_KEY")
    if api_key:
        print(f"检测到API KEY: {api_key[:10]}...")
        client = BochaWebSearch()
    else:
        print("未检测到API KEY，使用模拟模式")
        client = BochaWebSearch()
    
    # 执行搜索
    try:
        response = client.search("Python编程教程")
        
        # 输出结果
        print(f"\n搜索关键词: {response.query}")
        print(f"找到结果数: {len(response.results)}")
        
        # 显示前3个结果
        print("\n前3个结果:")
        for i, result in enumerate(response.results[:3], 1):
            print(f"{i}. {result.title}")
            print(f"   来源: {result.display_url}")
            print(f"   摘要: {result.snippet[:100]}...")
            print()
        
        # 显示摘要（如果有）
        if response.summary:
            print(f"搜索摘要: {response.summary}")
        
    except Exception as e:
        print(f"搜索失败: {e}")
    
    print("\n" + "=" * 50 + "\n")
    
    # 方法2：直接指定API KEY
    print("方法2：直接指定API KEY")
    print("-" * 50)
    
    # 如果有API KEY，使用真实模式
    if api_key:
        client = BochaWebSearch(api_key=api_key)
        
        try:
            # 带参数的搜索
            response = client.search(
                query="机器学习",
                freshness="oneMonth",
                count=5,
                summary=True
            )
            
            print(f"\n搜索关键词: {response.query}")
            print(f"时间过滤: 过去一个月")
            print(f"结果数量: {len(response.results)}")
            
            if response.summary:
                print(f"\n搜索摘要: {response.summary}")
            
        except Exception as e:
            print(f"搜索失败: {e}")
    else:
        print("未设置API KEY，跳过真实模式示例")
    
    print("\n" + "=" * 50 + "\n")
    
    # 方法3：使用模拟模式
    print("方法3：使用模拟模式（无需API KEY）")
    print("-" * 50)
    
    client = BochaWebSearch()  # 不传API KEY会自动使用模拟模式
    
    try:
        response = client.search(
            query="人工智能发展",
            count=3,
            summary=True
        )
        
        print(f"\n模拟搜索: {response.query}")
        print(f"模式: {response.metadata.get('mode', 'real')}")
        
        for i, result in enumerate(response.results, 1):
            print(f"\n{i}. {result.title}")
            print(f"   URL: {result.url}")
            print(f"   摘要: {result.snippet}")
        
        if response.summary:
            print(f"\n模拟摘要: {response.summary}")
        
    except Exception as e:
        print(f"模拟搜索失败: {e}")


if __name__ == "__main__":
    main()