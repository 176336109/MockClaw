#!/usr/bin/env python3
"""
博查AI Web Search SDK演示
展示如何在其他Python项目中使用此SDK
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bocha_web_search import BochaWebSearch, SearchResult, SearchResponse


class SearchApp:
    """示例应用：使用博查AI Web Search SDK"""
    
    def __init__(self, api_key=None):
        """初始化应用"""
        self.client = BochaWebSearch(api_key=api_key)
        print(f"应用初始化完成，模式: {'模拟' if self.client.mock_mode else '真实'}")
    
    def search_and_display(self, query, **kwargs):
        """搜索并显示结果"""
        print(f"\n🔍 搜索: {query}")
        print("-" * 60)
        
        try:
            # 执行搜索
            response = self.client.search(query, **kwargs)
            
            # 显示基本信息
            self._display_basic_info(response)
            
            # 显示结果
            self._display_results(response)
            
            # 显示摘要（如果有）
            self._display_summary(response)
            
            return response
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return None
    
    def _display_basic_info(self, response):
        """显示基本信息"""
        print(f"📊 找到 {len(response.results)} 个结果")
        
        metadata = response.metadata
        if metadata:
            mode = metadata.get('mode', '真实')
            freshness = metadata.get('freshness', 'noLimit')
            print(f"📅 时间过滤: {freshness}")
            print(f"🎭 模式: {mode}")
    
    def _display_results(self, response, max_results=3):
        """显示搜索结果"""
        print(f"\n📋 搜索结果（显示前{max_results}个）:")
        
        for i, result in enumerate(response.results[:max_results], 1):
            print(f"\n{i}. {result.title}")
            print(f"   🔗 {result.url}")
            print(f"   📝 {result.snippet[:100]}...")
            
            if result.date:
                print(f"   📅 {result.date}")
            
            if result.source:
                print(f"   🏢 来源: {result.source}")
    
    def _display_summary(self, response):
        """显示搜索摘要"""
        if response.summary:
            print(f"\n📄 搜索摘要:")
            print(f"   {response.summary}")
    
    def export_results(self, response, format="json", filename=None):
        """导出搜索结果"""
        if not response:
            print("❌ 没有结果可导出")
            return False
        
        if not filename:
            # 生成默认文件名
            import re
            safe_query = re.sub(r'[^\w\-_]', '_', response.query)[:50]
            timestamp = response.metadata.get('timestamp', '').split('T')[0]
            filename = f"search_{safe_query}_{timestamp}.{format}"
        
        try:
            if format.lower() == "json":
                content = response.to_json()
            else:
                content = response.to_text()
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"✅ 结果已导出到: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ 导出失败: {e}")
            return False
    
    def batch_search(self, queries, **kwargs):
        """批量搜索多个关键词"""
        print(f"\n🔄 批量搜索 {len(queries)} 个关键词")
        print("=" * 60)
        
        results = {}
        for query in queries:
            print(f"\n正在搜索: {query}")
            response = self.search_and_display(query, **kwargs)
            results[query] = response
        
        return results


def demo_integration_with_other_libs():
    """演示与其他库的集成"""
    print("\n" + "=" * 60)
    print("📚 与其他库的集成演示")
    print("=" * 60)
    
    # 模拟客户端
    client = BochaWebSearch()
    
    try:
        # 示例：与pandas集成（如果可用）
        try:
            import pandas as pd
            
            response = client.search("数据分析工具", count=5)
            
            # 将结果转换为DataFrame
            data = []
            for result in response.results:
                data.append({
                    'title': result.title,
                    'url': result.url,
                    'snippet': result.snippet[:100] + '...',
                    'source': result.source or '未知',
                    'date': result.date or '未知'
                })
            
            df = pd.DataFrame(data)
            print("\n📊 使用pandas显示结果:")
            print(df.to_string(index=False))
            
        except ImportError:
            print("📊 pandas未安装，跳过DataFrame演示")
        
        # 示例：与json库集成
        print("\n📄 使用json库处理结果:")
        response = client.search("JSON示例", count=2)
        json_str = response.to_json()
        
        import json
        data = json.loads(json_str)
        print(f"JSON解析成功，包含 {len(data.get('results', []))} 个结果")
        
        # 示例：文件操作
        print("\n💾 文件操作集成:")
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json_str)
            print(f"临时文件已创建: {f.name}")
        
    except Exception as e:
        print(f"集成演示失败: {e}")


def main():
    """主演示函数"""
    print("=" * 60)
    print("博查AI Web Search SDK演示")
    print("=" * 60)
    
    # 初始化应用
    app = SearchApp()
    
    # 演示1：基本搜索
    print("\n🎯 演示1：基本搜索")
    response1 = app.search_and_display(
        "Python异步编程",
        count=5,
        summary=True
    )
    
    # 导出结果
    if response1:
        app.export_results(response1, format="json")
        app.export_results(response1, format="text")
    
    # 演示2：高级搜索
    print("\n\n🎯 演示2：高级搜索（网站过滤）")
    response2 = app.search_and_display(
        "开源项目",
        include="github.com",
        exclude="gitee.com",
        freshness="oneMonth",
        count=4
    )
    
    # 演示3：批量搜索
    print("\n\n🎯 演示3：批量搜索")
    queries = ["机器学习", "深度学习", "强化学习"]
    batch_results = app.batch_search(
        queries,
        count=2,
        summary=True
    )
    
    # 演示4：错误处理
    print("\n\n🎯 演示4：错误处理演示")
    
    # 无效查询
    print("\n尝试空查询:")
    try:
        app.client.search("")
    except ValueError as e:
        print(f"✅ 正确捕获错误: {e}")
    
    # 无效数量
    print("\n尝试无效数量:")
    try:
        app.client.search("测试", count=100)
    except ValueError as e:
        print(f"✅ 正确捕获错误: {e}")
    
    # 演示5：与其他库集成
    demo_integration_with_other_libs()
    
    print("\n" + "=" * 60)
    print("🎉 SDK演示完成！")
    print("=" * 60)
    
    # 使用说明
    print("\n📖 使用说明:")
    print("1. 设置环境变量 BOCHA_API_KEY 以使用真实API")
    print("2. 查看 examples/ 目录了解更多示例")
    print("3. 参考 SKILL.md 获取完整文档")
    print("4. 运行 python -m pytest tests/ 运行测试")


if __name__ == "__main__":
    main()