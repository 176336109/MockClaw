# API参考文档

## BochaWebSearch类

### 构造函数
```python
BochaWebSearch(
    api_key: Optional[str] = None,
    endpoint: str = "https://api.bocha.cn/v1/web-search",
    timeout: int = 30,
    debug: bool = False
)
```

**参数：**
- `api_key` (str, 可选): API密钥。如果为None，则从环境变量`BOCHA_API_KEY`读取，如果都没有则启用模拟模式。
- `endpoint` (str, 可选): API端点，默认为官方端点。
- `timeout` (int, 可选): 请求超时时间（秒），默认30秒。
- `debug` (bool, 可选): 是否启用调试模式，默认False。

**属性：**
- `mock_mode` (bool): 是否为模拟模式（当没有API KEY时自动启用）
- `headers` (dict): 请求头，包含认证信息

### search方法
```python
search(
    query: str,
    freshness: str = "noLimit",
    summary: bool = False,
    count: int = 10,
    include: Optional[str] = None,
    exclude: Optional[str] = None
) -> SearchResponse
```

执行网页搜索。

**参数：**
- `query` (str, 必填): 搜索关键词
- `freshness` (str, 可选): 时间过滤选项，可选值：
  - `"noLimit"`: 不限时间（默认）
  - `"oneDay"`: 过去24小时
  - `"oneWeek"`: 过去一周
  - `"oneMonth"`: 过去一个月
  - `"oneYear"`: 过去一年
  - `"YYYY-MM-DDtoYYYY-MM-DD"`: 自定义日期范围
- `summary` (bool, 可选): 是否显示搜索结果摘要，默认False
- `count` (int, 可选): 返回结果数量，范围1-50，默认10
- `include` (str, 可选): 包含特定网站（例如："github.com"）
- `exclude` (str, 可选): 排除特定网站（例如："baidu.com"）

**返回：**
- `SearchResponse`: 搜索结果响应对象

**异常：**
- `ValueError`: 参数验证失败（如空查询、无效数量）
- `Exception`: API请求失败、网络错误等

## SearchResponse类

### 构造函数
```python
SearchResponse(
    query: str,
    results: List[SearchResult],
    summary: Optional[str] = None,
    metadata: Optional[Dict] = None
)
```

**属性：**
- `query` (str): 搜索关键词
- `results` (List[SearchResult]): 搜索结果列表
- `summary` (Optional[str]): 搜索摘要（如果启用）
- `metadata` (Dict): 元数据，包含：
  - `count` (int): 结果数量
  - `freshness` (str): 使用的时间过滤
  - `timestamp` (str): 搜索时间戳
  - `mode` (str): 模式（"real"或"mock"）

### 方法

#### to_dict()
```python
to_dict() -> Dict
```
将响应转换为字典格式。

**返回：**
- `Dict`: 包含所有数据的字典

#### to_json()
```python
to_json(indent: int = 2) -> str
```
将响应转换为JSON字符串。

**参数：**
- `indent` (int, 可选): JSON缩进，默认2

**返回：**
- `str`: JSON格式字符串

#### to_text()
```python
to_text() -> str
```
将响应转换为可读的文本格式。

**返回：**
- `str`: 文本格式字符串

## SearchResult类

### 构造函数
```python
SearchResult(
    title: str,
    url: str,
    snippet: str,
    display_url: str,
    date: Optional[str] = None,
    source: Optional[str] = None
)
```

**属性：**
- `title` (str): 结果标题
- `url` (str): 结果URL
- `snippet` (str): 结果摘要
- `display_url` (str): 显示URL（域名）
- `date` (Optional[str]): 发布日期
- `source` (Optional[str]): 来源网站

### 方法

#### to_dict()
```python
to_dict() -> Dict
```
将结果转换为字典格式。

#### to_text()
```python
to_text(index: int) -> str
```
将结果转换为文本格式。

**参数：**
- `index` (int): 结果序号

**返回：**
- `str`: 文本格式字符串

## 命令行接口

### 基本用法
```bash
openclaw bocha-web-search "搜索关键词"
```

### 完整参数
```bash
openclaw bocha-web-search "关键词" \
  --freshness oneWeek \
  --count 15 \
  --include "github.com" \
  --exclude "baidu.com" \
  --summary \
  --format json \
  --debug \
  --timeout 60
```

### 参数说明
| 参数 | 说明 | 默认值 | 可选值 |
|------|------|--------|--------|
| `query` | 搜索关键词（位置参数） | - | 任意字符串 |
| `--freshness` | 时间过滤 | `noLimit` | `noLimit`, `oneDay`, `oneWeek`, `oneMonth`, `oneYear`, 日期范围 |
| `--summary` | 显示摘要 | `False` | 布尔标志 |
| `--count` | 结果数量 | `10` | 1-50 |
| `--include` | 包含网站 | `None` | 域名字符串 |
| `--exclude` | 排除网站 | `None` | 域名字符串 |
| `--format` | 输出格式 | `text` | `text`, `json` |
| `--debug` | 调试模式 | `False` | 布尔标志 |
| `--timeout` | 请求超时 | `30` | 正整数（秒） |

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `BOCHA_API_KEY` | API密钥 | `None` |
| `BOCHA_API_ENDPOINT` | API端点 | `https://api.bocha.cn/v1/web-search` |
| `BOCHA_REQUEST_TIMEOUT` | 请求超时 | `30` |
| `BOCHA_DEBUG` | 调试模式 | `false` |
| `BOCHA_DEFAULT_FORMAT` | 默认输出格式 | `text` |
| `BOCHA_DEFAULT_COUNT` | 默认结果数量 | `10` |
| `BOCHA_DEFAULT_FRESHNESS` | 默认时间过滤 | `noLimit` |
| `BOCHA_DEFAULT_SUMMARY` | 默认是否显示摘要 | `false` |

## 错误代码

### 参数错误
- **错误信息**: "搜索关键词不能为空"
  - **原因**: `query`参数为空或只包含空格
  - **解决方案**: 提供有效的搜索关键词

- **错误信息**: "结果数量必须在1-50之间"
  - **原因**: `count`参数不在有效范围内
  - **解决方案**: 将`count`参数设置为1-50之间的整数

### API错误
- **错误信息**: "API请求错误：认证失败"
  - **原因**: API密钥无效或过期
  - **解决方案**: 检查`BOCHA_API_KEY`环境变量或重新获取API密钥

- **错误信息**: "请求超时（30秒）"
  - **原因**: 网络连接超时
  - **解决方案**: 检查网络连接，或使用`--timeout`参数增加超时时间

- **错误信息**: "网络连接错误，请检查网络连接"
  - **原因**: 无法连接到API服务器
  - **解决方案**: 检查网络连接和防火墙设置

### 其他错误
- **错误信息**: "API返回了无效的JSON响应"
  - **原因**: API服务器返回了非JSON格式的响应
  - **解决方案**: 联系API提供商或检查API端点配置

## 示例代码

### Python SDK使用
```python
from bocha_web_search import BochaWebSearch

# 初始化客户端
client = BochaWebSearch()

# 基本搜索
results = client.search("Python教程")

# 带所有参数的搜索
results = client.search(
    query="机器学习",
    freshness="oneMonth",
    count=20,
    include="arxiv.org",
    exclude="wikipedia.org",
    summary=True
)

# 处理结果
for i, result in enumerate(results.results, 1):
    print(f"{i}. {result.title}")
    print(f"   链接: {result.url}")
    print(f"   摘要: {result.snippet[:100]}...")

# 获取不同格式
json_output = results.to_json()
text_output = results.to_text()
dict_output = results.to_dict()
```

### 错误处理
```python
from bocha_web_search import BochaWebSearch

client = BochaWebSearch()

try:
    results = client.search("测试", count=100)  # 无效数量
except ValueError as e:
    print(f"参数错误: {e}")
    # 处理参数错误
except Exception as e:
    print(f"其他错误: {e}")
    # 处理其他错误
else:
    # 搜索成功
    print(f"找到 {len(results.results)} 个结果")
```

### 批量处理
```python
from bocha_web_search import BochaWebSearch
import json

client = BochaWebSearch()
queries = ["人工智能", "机器学习", "深度学习"]

all_results = {}
for query in queries:
    try:
        results = client.search(query, count=5)
        all_results[query] = results.to_dict()
    except Exception as e:
        print(f"搜索 '{query}' 失败: {e}")

# 保存到文件
with open("search_results.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, ensure_ascii=False, indent=2)
```

## 最佳实践

### 1. 错误处理
始终使用try-except块包裹搜索调用，以处理可能的错误。

### 2. 参数验证
在调用搜索前验证用户输入，特别是`query`和`count`参数。

### 3. 资源管理
对于长时间运行的应用，考虑：
- 设置合理的超时时间
- 实现重试机制
- 使用连接池

### 4. 性能优化
- 对于批量搜索，考虑并行处理
- 缓存频繁搜索的结果
- 合理设置`count`参数，避免请求过多数据

### 5. 用户体验
- 提供清晰的错误信息
- 支持多种输出格式
- 实现模拟模式用于开发和测试