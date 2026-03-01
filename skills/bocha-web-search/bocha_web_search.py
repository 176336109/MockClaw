#!/usr/bin/env python3
"""
博查AI Web Search API的OpenClaw技能
支持完整的搜索功能和模拟模式
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import requests
    from requests.exceptions import RequestException, Timeout, ConnectionError
except ImportError:
    print("错误：缺少requests库，请运行：pip install requests")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Freshness(Enum):
    """时间过滤选项"""
    NO_LIMIT = "noLimit"
    ONE_DAY = "oneDay"
    ONE_WEEK = "oneWeek"
    ONE_MONTH = "oneMonth"
    ONE_YEAR = "oneYear"


class OutputFormat(Enum):
    """输出格式"""
    TEXT = "text"
    JSON = "json"


@dataclass
class SearchResult:
    """搜索结果"""
    title: str
    url: str
    snippet: str
    display_url: str
    date: Optional[str] = None
    source: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    def to_text(self, index: int) -> str:
        """转换为文本格式"""
        text = f"{index}. {self.title}\n"
        text += f"   URL: {self.url}\n"
        text += f"   摘要: {self.snippet}\n"
        if self.display_url:
            text += f"   来源: {self.display_url}\n"
        if self.date:
            text += f"   日期: {self.date}\n"
        return text


@dataclass
class SearchResponse:
    """搜索响应"""
    query: str
    results: List[SearchResult]
    summary: Optional[str] = None
    metadata: Optional[Dict] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {
                "count": len(self.results),
                "timestamp": datetime.now().isoformat()
            }
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "summary": self.summary,
            "metadata": self.metadata
        }
    
    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def to_text(self) -> str:
        """转换为文本格式"""
        text = f"搜索结果：{self.query}\n\n"
        
        for i, result in enumerate(self.results, 1):
            text += result.to_text(i) + "\n"
        
        if self.summary:
            text += f"\n搜索摘要：{self.summary}\n"
        
        count = len(self.results)
        timestamp = self.metadata.get("timestamp", datetime.now().isoformat())
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = timestamp
        
        text += f"\n共找到{count}个结果，搜索时间：{time_str}"
        return text


class BochaWebSearch:
    """博查AI Web Search客户端"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: str = "https://api.bocha.cn/v1/web-search",
        timeout: int = 30,
        debug: bool = False
    ):
        """
        初始化客户端
        
        Args:
            api_key: API密钥，如果为None则使用模拟模式
            endpoint: API端点
            timeout: 请求超时时间（秒）
            debug: 是否启用调试模式
        """
        self.api_key = api_key or os.getenv("BOCHA_API_KEY")
        self.endpoint = endpoint or os.getenv("BOCHA_API_ENDPOINT", "https://api.bocha.cn/v1/web-search")
        self.timeout = timeout or int(os.getenv("BOCHA_REQUEST_TIMEOUT", "30"))
        self.debug = debug or (os.getenv("BOCHA_DEBUG", "").lower() == "true")
        
        # 如果没有API KEY，启用模拟模式
        self.mock_mode = not self.api_key
        if self.mock_mode:
            logger.warning("未设置API KEY，启用模拟模式")
        
        # 设置请求头
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "OpenClaw-Bocha-Web-Search/1.0"
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
    
    def search(
        self,
        query: str,
        freshness: str = "noLimit",
        summary: bool = False,
        count: int = 10,
        include: Optional[str] = None,
        exclude: Optional[str] = None
    ) -> SearchResponse:
        """
        执行搜索
        
        Args:
            query: 搜索关键词
            freshness: 时间过滤
            summary: 是否显示摘要
            count: 结果数量（1-50）
            include: 包含网站
            exclude: 排除网站
        
        Returns:
            SearchResponse: 搜索结果
        """
        # 验证参数
        self._validate_params(query, count)
        
        # 如果是模拟模式，返回模拟数据
        if self.mock_mode:
            return self._mock_search(query, count, summary)
        
        # 准备请求数据
        data = {
            "query": query,
            "freshness": freshness,
            "summary": summary,
            "count": count
        }
        
        if include:
            data["include"] = include
        if exclude:
            data["exclude"] = exclude
        
        try:
            # 发送请求
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=data,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # 解析响应
            result_data = response.json()
            return self._parse_response(query, result_data, summary)
            
        except Timeout:
            raise Exception(f"请求超时（{self.timeout}秒）")
        except ConnectionError:
            raise Exception("网络连接错误，请检查网络连接")
        except RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("error", {}).get("message", str(e))
                except:
                    error_msg = str(e)
                raise Exception(f"API请求错误：{error_msg}")
            else:
                raise Exception(f"请求失败：{str(e)}")
        except json.JSONDecodeError:
            raise Exception("API返回了无效的JSON响应")
        except Exception as e:
            raise Exception(f"搜索失败：{str(e)}")
    
    def _validate_params(self, query: str, count: int):
        """验证参数"""
        if not query or not query.strip():
            raise ValueError("搜索关键词不能为空")
        
        if count < 1 or count > 50:
            raise ValueError("结果数量必须在1-50之间")
    
    def _parse_response(self, query: str, data: Dict, summary_enabled: bool) -> SearchResponse:
        """解析API响应"""
        results = []
        
        # 解析网页结果
        web_pages = data.get("webPages", {}).get("value", [])
        for item in web_pages:
            result = SearchResult(
                title=item.get("name", ""),
                url=item.get("url", ""),
                snippet=item.get("snippet", ""),
                display_url=item.get("displayUrl", ""),
                date=item.get("datePublished"),
                source=item.get("source", "")
            )
            results.append(result)
        
        # 解析图片结果（如果有）
        images = data.get("images", {}).get("value", [])
        for item in images:
            result = SearchResult(
                title=item.get("name", ""),
                url=item.get("contentUrl", ""),
                snippet=item.get("thumbnailUrl", ""),
                display_url=item.get("hostPageDisplayUrl", ""),
                date=item.get("datePublished"),
                source=item.get("source", "")
            )
            results.append(result)
        
        # 获取摘要
        summary = None
        if summary_enabled:
            summary = data.get("summary", {}).get("text")
        
        # 创建响应对象
        metadata = {
            "count": len(results),
            "freshness": data.get("queryContext", {}).get("freshness", "noLimit"),
            "timestamp": datetime.now().isoformat()
        }
        
        return SearchResponse(
            query=query,
            results=results,
            summary=summary,
            metadata=metadata
        )
    
    def _mock_search(self, query: str, count: int, summary_enabled: bool) -> SearchResponse:
        """模拟搜索（用于测试和演示）"""
        logger.info(f"模拟搜索：{query}")
        
        # 生成模拟结果
        results = []
        for i in range(min(count, 5)):  # 模拟模式最多返回5个结果
            result = SearchResult(
                title=f"模拟结果 {i+1}：{query}",
                url=f"https://example.com/result/{i+1}",
                snippet=f"这是关于'{query}'的模拟搜索结果摘要。模拟模式用于测试和演示，无需API KEY。",
                display_url=f"example.com/result/{i+1}",
                date=datetime.now().strftime("%Y-%m-%d"),
                source="模拟数据源"
            )
            results.append(result)
        
        # 模拟摘要
        summary = None
        if summary_enabled:
            summary = f"关于'{query}'的模拟搜索摘要。这是在模拟模式下生成的示例摘要。要获取真实搜索结果，请设置BOCHA_API_KEY环境变量。"
        
        # 创建响应对象
        metadata = {
            "count": len(results),
            "freshness": "noLimit",
            "timestamp": datetime.now().isoformat(),
            "mode": "mock"
        }
        
        return SearchResponse(
            query=query,
            results=results,
            summary=summary,
            metadata=metadata
        )


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="博查AI Web Search - 强大的网页搜索工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  %(prog)s "OpenAI最新进展"
  %(prog)s "Python教程" --format json
  %(prog)s "科技新闻" --freshness oneDay --count 20
  %(prog)s "编程教程" --include "github.com" --exclude "baidu.com" --summary
        """
    )
    
    # 必需参数
    parser.add_argument(
        "query",
        help="搜索关键词"
    )
    
    # 可选参数
    parser.add_argument(
        "--freshness",
        choices=["noLimit", "oneDay", "oneWeek", "oneMonth", "oneYear"],
        default="noLimit",
        help="时间过滤（默认：noLimit）"
    )
    
    parser.add_argument(
        "--summary",
        action="store_true",
        help="显示搜索结果摘要"
    )
    
    parser.add_argument(
        "--count",
        type=int,
        choices=range(1, 51),
        default=10,
        help="结果数量（1-50，默认：10）"
    )
    
    parser.add_argument(
        "--include",
        help="包含特定网站（例如：github.com）"
    )
    
    parser.add_argument(
        "--exclude",
        help="排除特定网站（例如：baidu.com）"
    )
    
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="输出格式（默认：text）"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="请求超时时间（秒，默认：30）"
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    try:
        # 创建客户端
        client = BochaWebSearch(
            debug=args.debug,
            timeout=args.timeout
        )
        
        # 执行搜索
        response = client.search(
            query=args.query,
            freshness=args.freshness,
            summary=args.summary,
            count=args.count,
            include=args.include,
            exclude=args.exclude
        )
        
        # 输出结果
        if args.format == "json":
            print(response.to_json())
        else:
            print(response.to_text())
            
    except ValueError as e:
        print(f"参数错误：{e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()