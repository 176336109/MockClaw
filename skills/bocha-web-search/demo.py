#!/usr/bin/env python3
"""
博查AI Web Search演示脚本
展示技能的主要功能
"""

import sys
import os
import time

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bocha_web_search import BochaWebSearch


def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def demo_basic_search():
    """演示基本搜索"""
    print_header("1. 基本搜索演示")
    
    client = BochaWebSearch()
    
    # 演示1：简单搜索
    print("🔍 演示：简单搜索")
    print("-" * 40)
    
    response = client.search("人工智能发展现状")
    print(f"搜索关键词: {response.query}")
    print(f"找到结果数: {len(response.results)}")
    
    if response.results:
        print("\n第一个结果:")
        result = response.results[0]
        print(f"  标题: {result.title}")
        print(f"  链接: {result.url}")
        print(f"  摘要: {result.snippet[:80]}...")
    
    time.sleep(1)


def demo_advanced_features():
    """演示高级功能"""
    print_header("2. 高级功能演示")
    
    client = BochaWebSearch()
    
    # 演示2：时间过滤
    print("⏰ 演示：时间过滤搜索")
    print("-" * 40)
    
    response = client.search(
        query="科技新闻",
        freshness="oneWeek",
        count=3
    )
    
    print(f"时间过滤: 过去一周")
    print(f"结果数量: {len(response.results)}")
    
    for i, result in enumerate(response.results[:2], 1):
        print(f"\n{i}. {result.title}")
        print(f"  日期: {result.date or '未知'}")
    
    time.sleep(1)
    
    # 演示3：网站过滤
    print("\n🌐 演示：网站过滤搜索")
    print("-" * 40)
    
    response = client.search(
        query="Python编程",
        include="github.com",
        count=3
    )
    
    print(f"包含网站: github.com")
    
    for i, result in enumerate(response.results, 1):
        print(f"{i}. {result.title}")
        print(f"  来源: {result.display_url}")
    
    time.sleep(1)
    
    # 演示4：摘要功能
    print("\n📄 演示：搜索摘要")
    print("-" * 40)
    
    response = client.search(
        query="机器学习应用",
        summary=True,
        count=2
    )
    
    if response.summary:
        print(f"搜索摘要: {response.summary}")
    else:
        print("（模拟模式下摘要可能不可用）")
    
    time.sleep(1)


def demo_output_formats():
    """演示输出格式"""
    print_header("3. 输出格式演示")
    
    client = BochaWebSearch()
    
    response = client.search("数据科学", count=2)
    
    # JSON格式
    print("📋 JSON格式输出:")
    print("-" * 40)
    json_output = response.to_json()
    # 只显示前200个字符
    preview = json_output[:200] + "..." if len(json_output) > 200 else json_output
    print(preview)
    
    time.sleep(1)
    
    # 文本格式
    print("\n📝 文本格式输出:")
    print("-" * 40)
    text_output = response.to_text()
    # 只显示前10行
    lines = text_output.split('\n')
    for line in lines[:10]:
        print(line)
    if len(lines) > 10:
        print("...")
    
    time.sleep(1)


def demo_error_handling():
    """演示错误处理"""
    print_header("4. 错误处理演示")
    
    client = BochaWebSearch()
    
    # 演示无效参数
    print("⚠️  演示：无效参数处理")
    print("-" * 40)
    
    try:
        response = client.search("", count=10)
    except ValueError as e:
        print(f"✅ 正确捕获错误: {e}")
    
    try:
        response = client.search("测试", count=100)
    except ValueError as e:
        print(f"✅ 正确捕获错误: {e}")
    
    time.sleep(1)


def demo_integration():
    """演示集成使用"""
    print_header("5. 集成使用演示")
    
    client = BochaWebSearch()
    
    # 演示批量搜索
    print("🔄 演示：批量搜索")
    print("-" * 40)
    
    keywords = ["Python", "JavaScript", "Java"]
    print(f"批量搜索关键词: {', '.join(keywords)}")
    
    for keyword in keywords:
        try:
            response = client.search(keyword, count=1)
            print(f"\n{keyword}: 找到 {len(response.results)} 个结果")
            if response.results:
                print(f"  示例: {response.results[0].title[:50]}...")
        except Exception as e:
            print(f"\n{keyword}: 搜索失败 - {e}")
    
    time.sleep(1)


def show_usage_instructions():
    """显示使用说明"""
    print_header("使用说明")
    
    print("📖 命令行使用:")
    print("  python bocha_web_search.py \"搜索关键词\"")
    print("  python bocha_web_search.py \"关键词\" --format json --count 5")
    print("  python bocha_web_search.py \"新闻\" --freshness oneDay --summary")
    
    print("\n📖 Python SDK使用:")
    print("  from bocha_web_search import BochaWebSearch")
    print("  client = BochaWebSearch()")
    print("  results = client.search(\"关键词\", count=10, summary=True)")
    
    print("\n📖 环境变量配置:")
    print("  export BOCHA_API_KEY=\"your_api_key\"")
    print("  export BOCHA_DEBUG=true")
    
    print("\n📖 获取API密钥:")
    print("  访问 https://open.bocha.cn > API KEY管理")


def main():
    """主函数"""
    print("🎯 博查AI Web Search技能演示")
    print("=" * 60)
    
    # 检查模式
    client = BochaWebSearch()
    mode = "模拟模式" if client.mock_mode else "真实模式"
    print(f"运行模式: {mode}")
    
    if client.mock_mode:
        print("⚠️  提示：未检测到API密钥，使用模拟模式")
        print("      设置 BOCHA_API_KEY 环境变量以使用真实API")
    
    print("\n开始演示...")
    
    # 运行所有演示
    demo_basic_search()
    demo_advanced_features()
    demo_output_formats()
    demo_error_handling()
    demo_integration()
    
    # 显示使用说明
    show_usage_instructions()
    
    print("\n" + "=" * 60)
    print("🎉 演示完成！")
    print("\n更多示例请查看 examples/ 目录")
    print("完整文档请查看 README.md 和 docs/ 目录")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n演示已中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        sys.exit(1)