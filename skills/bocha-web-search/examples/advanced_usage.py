#!/usr/bin/env python3
"""
博查AI Web Search高级使用示例
"""

import sys
import os
import json

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bocha_web_search import BochaWebSearch, Freshness


def advanced_search_examples():
    """高级搜索示例"""
    print("=== 高级搜索示例 ===\n")
    
    # 初始化客户端
    client = BochaWebSearch()
    
    # 示例1：网站过滤
    print("示例1：网站过滤搜索")
    print("-" * 50)
    
    try:
        response = client.search(
            query="Python异步编程",
            include="github.com",
            exclude="baidu.com",
            count=5
        )
        
        print(f"搜索: {response.query}")
        print(f"包含网站: github.com")
        print(f"排除网站: baidu.com")
        print(f"结果数: {len(response.results)}")
        
        for i, result in enumerate(response.results[:2], 1):
            print(f"\n{i}. {result.title}")
            print(f"   来源: {result.display_url}")
        
    except Exception as e:
        print(f"搜索失败: {e}")
    
    print("\n" + "=" * 50 + "\n")
    
    # 示例2：时间范围搜索
    print("示例2：时间范围搜索")
    print("-" * 50)
    
    try:
        # 使用自定义日期范围
        response = client.search(
            query="科技新闻",
            freshness="2024-01-01to2024-12-31",  # 自定义日期范围
            count=3
        )
        
        print(f"搜索: {response.query}")
        print(f"时间范围: 2024年全年")
        print(f"结果数: {len(response.results)}")
        
        for i, result in enumerate(response.results, 1):
            date_str = result.date if result.date else "未知日期"
            print(f"\n{i}. {result.title}")
            print(f"   日期: {date_str}")
        
    except Exception as e:
        print(f"搜索失败: {e}")
    
    print("\n" + "=" * 50 + "\n")
    
    # 示例3：批量搜索
    print("示例3：批量搜索多个关键词")
    print("-" * 50)
    
    keywords = ["机器学习", "深度学习", "自然语言处理"]
    
    for keyword in keywords:
        try:
            response = client.search(
                query=keyword,
                count=2,
                summary=True
            )
            
            print(f"\n关键词: {keyword}")
            print(f"结果数: {len(response.results)}")
            
            if response.summary:
                print(f"摘要: {response.summary[:100]}...")
            
        except Exception as e:
            print(f"搜索 '{keyword}' 失败: {e}")


def output_format_examples():
    """输出格式示例"""
    print("\n\n=== 输出格式示例 ===\n")
    
    client = BochaWebSearch()
    
    try:
        response = client.search(
            query="OpenAI GPT-4",
            count=2,
            summary=True
        )
        
        # JSON格式输出
        print("1. JSON格式输出:")
        print("-" * 30)
        json_output = response.to_json(indent=2)
        print(json_output[:500] + "..." if len(json_output) > 500 else json_output)
        
        print("\n\n2. 文本格式输出:")
        print("-" * 30)
        text_output = response.to_text()
        print(text_output)
        
        # 获取原始字典数据
        print("\n\n3. 原始字典数据:")
        print("-" * 30)
        data_dict = response.to_dict()
        print(f"数据结构: {type(data_dict)}")
        print(f"包含键: {list(data_dict.keys())}")
        
        # 访问单个结果
        if response.results:
            print(f"\n第一个结果的标题: {response.results[0].title}")
            print(f"第一个结果的URL: {response.results[0].url}")
        
    except Exception as e:
        print(f"示例失败: {e}")


def error_handling_examples():
    """错误处理示例"""
    print("\n\n=== 错误处理示例 ===\n")
    
    client = BochaWebSearch()
    
    # 示例1：空查询
    print("示例1：空查询错误处理")
    print("-" * 50)
    
    try:
        response = client.search("")
    except ValueError as e:
        print(f"预期错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")
    
    # 示例2：无效数量
    print("\n示例2：无效数量错误处理")
    print("-" * 50)
    
    try:
        response = client.search("测试", count=100)  # 超过50
    except ValueError as e:
        print(f"预期错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")
    
    # 示例3：网络错误模拟（通过无效端点）
    print("\n示例3：网络错误处理")
    print("-" * 50)
    
    # 创建使用无效端点的客户端
    invalid_client = BochaWebSearch(
        endpoint="https://invalid-endpoint.example.com",
        timeout=5  # 短超时以便快速失败
    )
    
    try:
        response = invalid_client.search("测试")
    except Exception as e:
        print(f"网络错误: {e}")


def integration_example():
    """集成示例：将搜索结果保存到文件"""
    print("\n\n=== 集成示例：保存搜索结果到文件 ===\n")
    
    client = BochaWebSearch()
    
    try:
        # 执行搜索
        response = client.search(
            query="数据科学教程",
            count=5,
            summary=True
        )
        
        # 保存为JSON文件
        json_filename = "search_results.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            f.write(response.to_json())
        print(f"✓ 已保存JSON结果到: {json_filename}")
        
        # 保存为文本文件
        text_filename = "search_results.txt"
        with open(text_filename, "w", encoding="utf-8") as f:
            f.write(response.to_text())
        print(f"✓ 已保存文本结果到: {text_filename}")
        
        # 显示文件内容预览
        print(f"\nJSON文件预览（前200字符）:")
        with open(json_filename, "r", encoding="utf-8") as f:
            print(f.read()[:200] + "...")
        
    except Exception as e:
        print(f"保存失败: {e}")


def main():
    """主函数"""
    print("博查AI Web Search高级使用示例\n")
    
    # 运行所有示例
    advanced_search_examples()
    output_format_examples()
    error_handling_examples()
    integration_example()
    
    print("\n" + "=" * 50)
    print("所有示例执行完成！")


if __name__ == "__main__":
    main()