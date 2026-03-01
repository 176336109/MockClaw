#!/usr/bin/env python3
"""
博查AI Web Search测试
"""

import sys
import os
import unittest
from unittest.mock import patch, Mock

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bocha_web_search import BochaWebSearch, SearchResult, SearchResponse


class TestSearchResult(unittest.TestCase):
    """测试SearchResult类"""
    
    def test_search_result_creation(self):
        """测试创建搜索结果"""
        result = SearchResult(
            title="测试标题",
            url="https://example.com",
            snippet="测试摘要",
            display_url="example.com",
            date="2024-01-01",
            source="测试源"
        )
        
        self.assertEqual(result.title, "测试标题")
        self.assertEqual(result.url, "https://example.com")
        self.assertEqual(result.snippet, "测试摘要")
        self.assertEqual(result.display_url, "example.com")
        self.assertEqual(result.date, "2024-01-01")
        self.assertEqual(result.source, "测试源")
    
    def test_to_dict(self):
        """测试转换为字典"""
        result = SearchResult(
            title="测试",
            url="https://test.com",
            snippet="摘要",
            display_url="test.com"
        )
        
        data = result.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["title"], "测试")
        self.assertEqual(data["url"], "https://test.com")
        self.assertEqual(data["snippet"], "摘要")
        self.assertEqual(data["display_url"], "test.com")
    
    def test_to_text(self):
        """测试转换为文本"""
        result = SearchResult(
            title="测试标题",
            url="https://example.com",
            snippet="这是一个测试摘要",
            display_url="example.com",
            date="2024-01-01"
        )
        
        text = result.to_text(1)
        self.assertIn("1. 测试标题", text)
        self.assertIn("URL: https://example.com", text)
        self.assertIn("摘要: 这是一个测试摘要", text)
        self.assertIn("来源: example.com", text)
        self.assertIn("日期: 2024-01-01", text)


class TestSearchResponse(unittest.TestCase):
    """测试SearchResponse类"""
    
    def setUp(self):
        """设置测试数据"""
        self.results = [
            SearchResult(
                title="结果1",
                url="https://example.com/1",
                snippet="摘要1",
                display_url="example.com"
            ),
            SearchResult(
                title="结果2",
                url="https://example.com/2",
                snippet="摘要2",
                display_url="example.com"
            )
        ]
    
    def test_search_response_creation(self):
        """测试创建搜索响应"""
        response = SearchResponse(
            query="测试查询",
            results=self.results,
            summary="测试摘要",
            metadata={"count": 2}
        )
        
        self.assertEqual(response.query, "测试查询")
        self.assertEqual(len(response.results), 2)
        self.assertEqual(response.summary, "测试摘要")
        self.assertEqual(response.metadata["count"], 2)
        self.assertIn("timestamp", response.metadata)
    
    def test_to_dict(self):
        """测试转换为字典"""
        response = SearchResponse(
            query="测试",
            results=self.results
        )
        
        data = response.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["query"], "测试")
        self.assertEqual(len(data["results"]), 2)
        self.assertIsNone(data["summary"])
        self.assertIn("metadata", data)
    
    def test_to_json(self):
        """测试转换为JSON"""
        response = SearchResponse(
            query="测试",
            results=self.results
        )
        
        json_str = response.to_json()
        self.assertIsInstance(json_str, str)
        self.assertIn('"query": "测试"', json_str)
        self.assertIn('"results"', json_str)
    
    def test_to_text(self):
        """测试转换为文本"""
        response = SearchResponse(
            query="测试查询",
            results=self.results,
            summary="这是一个测试摘要"
        )
        
        text = response.to_text()
        self.assertIn("搜索结果：测试查询", text)
        self.assertIn("1. 结果1", text)
        self.assertIn("2. 结果2", text)
        self.assertIn("搜索摘要：这是一个测试摘要", text)
        self.assertIn("共找到2个结果", text)


class TestBochaWebSearch(unittest.TestCase):
    """测试BochaWebSearch类"""
    
    def setUp(self):
        """设置测试环境"""
        # 清除环境变量以确保测试一致性
        for key in ["BOCHA_API_KEY", "BOCHA_API_ENDPOINT", "BOCHA_DEBUG"]:
            if key in os.environ:
                del os.environ[key]
    
    def test_init_without_api_key(self):
        """测试无API KEY初始化"""
        client = BochaWebSearch()
        self.assertTrue(client.mock_mode)
        self.assertIsNone(client.api_key)
    
    def test_init_with_api_key(self):
        """测试有API KEY初始化"""
        client = BochaWebSearch(api_key="test_key")
        self.assertFalse(client.mock_mode)
        self.assertEqual(client.api_key, "test_key")
        self.assertIn("Authorization", client.headers)
    
    def test_init_with_env_var(self):
        """测试环境变量初始化"""
        os.environ["BOCHA_API_KEY"] = "env_key"
        client = BochaWebSearch()
        self.assertFalse(client.mock_mode)
        self.assertEqual(client.api_key, "env_key")
    
    def test_validate_params_valid(self):
        """测试有效参数验证"""
        client = BochaWebSearch()
        
        # 不应抛出异常
        client._validate_params("测试查询", 10)
        client._validate_params("测试查询", 1)
        client._validate_params("测试查询", 50)
    
    def test_validate_params_invalid(self):
        """测试无效参数验证"""
        client = BochaWebSearch()
        
        # 空查询
        with self.assertRaises(ValueError):
            client._validate_params("", 10)
        
        with self.assertRaises(ValueError):
            client._validate_params("   ", 10)
        
        # 无效数量
        with self.assertRaises(ValueError):
            client._validate_params("测试", 0)
        
        with self.assertRaises(ValueError):
            client._validate_params("测试", 51)
    
    @patch('bocha_web_search.requests.post')
    def test_real_search_success(self, mock_post):
        """测试真实搜索成功"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "webPages": {
                "value": [
                    {
                        "name": "测试标题1",
                        "url": "https://example.com/1",
                        "snippet": "测试摘要1",
                        "displayUrl": "example.com"
                    },
                    {
                        "name": "测试标题2",
                        "url": "https://example.com/2",
                        "snippet": "测试摘要2",
                        "displayUrl": "example.com"
                    }
                ]
            },
            "queryContext": {
                "freshness": "noLimit"
            }
        }
        mock_post.return_value = mock_response
        
        # 创建客户端
        client = BochaWebSearch(api_key="test_key")
        
        # 执行搜索
        response = client.search("测试查询", count=2)
        
        # 验证结果
        self.assertEqual(response.query, "测试查询")
        self.assertEqual(len(response.results), 2)
        self.assertEqual(response.results[0].title, "测试标题1")
        self.assertEqual(response.results[1].url, "https://example.com/2")
        
        # 验证请求
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "https://api.bocha.cn/v1/web-search")
        self.assertEqual(call_args[1]['json']['query'], "测试查询")
        self.assertEqual(call_args[1]['json']['count'], 2)
    
    @patch('bocha_web_search.requests.post')
    def test_real_search_with_summary(self, mock_post):
        """测试带摘要的真实搜索"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "webPages": {
                "value": [
                    {
                        "name": "测试标题",
                        "url": "https://example.com",
                        "snippet": "测试摘要",
                        "displayUrl": "example.com"
                    }
                ]
            },
            "summary": {
                "text": "这是一个测试摘要"
            },
            "queryContext": {
                "freshness": "oneWeek"
            }
        }
        mock_post.return_value = mock_response
        
        client = BochaWebSearch(api_key="test_key")
        response = client.search("测试查询", summary=True)
        
        self.assertEqual(response.summary, "这是一个测试摘要")
        self.assertEqual(response.metadata["freshness"], "oneWeek")
    
    @patch('bocha_web_search.requests.post')
    def test_real_search_error(self, mock_post):
        """测试真实搜索错误"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": {
                "message": "认证失败"
            }
        }
        mock_post.return_value = mock_response
        
        client = BochaWebSearch(api_key="invalid_key")
        
        with self.assertRaises(Exception) as context:
            client.search("测试查询")
        
        self.assertIn("认证失败", str(context.exception))
    
    def test_mock_search(self):
        """测试模拟搜索"""
        client = BochaWebSearch()  # 无API KEY，使用模拟模式
        
        response = client.search("测试查询", count=3, summary=True)
        
        # 验证模拟结果
        self.assertEqual(response.query, "测试查询")
        self.assertTrue(len(response.results) <= 5)  # 模拟模式最多5个结果
        self.assertIsNotNone(response.summary)
        self.assertEqual(response.metadata.get("mode"), "mock")
        
        # 验证结果结构
        for result in response.results:
            self.assertIsInstance(result, SearchResult)
            self.assertIn("测试查询", result.title)
            self.assertIn("模拟", result.snippet)
    
    def test_mock_search_with_params(self):
        """测试带参数的模拟搜索"""
        client = BochaWebSearch()
        
        response = client.search(
            query="人工智能",
            freshness="oneMonth",
            count=5,
            include="arxiv.org",
            exclude="wikipedia.org",
            summary=True
        )
        
        self.assertEqual(response.query, "人工智能")
        self.assertEqual(response.metadata.get("freshness"), "noLimit")  # 模拟模式固定值
        self.assertEqual(len(response.results), 5)
        self.assertIsNotNone(response.summary)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_complete_workflow(self):
        """测试完整工作流程"""
        # 1. 创建客户端（模拟模式）
        client = BochaWebSearch()
        
        # 2. 执行搜索
        response = client.search(
            query="集成测试",
            count=2,
            summary=True
        )
        
        # 3. 验证响应
        self.assertIsInstance(response, SearchResponse)
        self.assertEqual(len(response.results), 2)
        
        # 4. 转换为不同格式
        json_output = response.to_json()
        self.assertIsInstance(json_output, str)
        self.assertIn('"query": "集成测试"', json_output)
        
        text_output = response.to_text()
        self.assertIsInstance(text_output, str)
        self.assertIn("搜索结果：集成测试", text_output)
        
        dict_output = response.to_dict()
        self.assertIsInstance(dict_output, dict)
        self.assertEqual(dict_output["query"], "集成测试")
    
    def test_error_handling_workflow(self):
        """测试错误处理工作流程"""
        client = BochaWebSearch()
        
        # 测试无效参数
        with self.assertRaises(ValueError):
            client.search("", count=10)
        
        with self.assertRaises(ValueError):
            client.search("测试", count=100)
        
        # 测试有效参数不应抛出异常
        try:
            client.search("测试", count=10)
        except ValueError:
            self.fail("有效参数不应抛出ValueError")


if __name__ == "__main__":
    unittest.main()