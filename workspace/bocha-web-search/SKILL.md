# bocha-web-search Skill

博查AI Web Search API的OpenClaw技能，提供强大的网页搜索功能。

## 功能特性

- 🔍 **智能搜索**：支持博查AI Web Search API的所有参数
- 📊 **多格式输出**：支持text和json格式输出
- 🎭 **模拟模式**：当没有API KEY时自动启用模拟模式
- 🔧 **完整参数支持**：
  - `query`：搜索关键词（必填）
  - `freshness`：时间过滤（noLimit, oneDay, oneWeek, oneMonth, oneYear, 日期范围）
  - `summary`：是否显示摘要
  - `count`：结果数量（1-50）
  - `include`：包含特定网站
  - `exclude`：排除特定网站
- 🛡️ **错误处理**：完善的错误处理和用户友好的提示
- 📚 **完整文档**：包含使用示例和Python SDK

## 安装

1. 将技能目录复制到OpenClaw的skills目录：
   ```bash
   cp -r bocha-web-search ~/.openclaw/skills/
   ```

2. 配置环境变量：
   ```bash
   # 在~/.bashrc或~/.zshrc中添加
   export BOCHA_API_KEY="your-api-key-here"
   ```

3. 或者创建配置文件：
   ```bash
   cp bocha-web-search/.env.example ~/.openclaw/bocha-web-search.env
   ```

## 使用方法

### 命令行使用

```bash
# 基本搜索
openclaw bocha-web-search "OpenAI最新进展"

# 指定输出格式
openclaw bocha-web-search "Python教程" --format json
openclaw bocha-web-search "Python教程" --format text

# 时间过滤
openclaw bocha-web-search "科技新闻" --freshness oneDay
openclaw bocha-web-search "科技新闻" --freshness "2024-01-01to2024-12-31"

# 结果数量
openclaw bocha-web-search "AI工具" --count 20

# 网站过滤
openclaw bocha-web-search "编程教程" --include "github.com" --exclude "baidu.com"

# 显示摘要
openclaw bocha-web-search "天气" --summary

# 所有参数组合
openclaw bocha-web-search "机器学习" \
  --freshness oneWeek \
  --count 15 \
  --include "arxiv.org" \
  --exclude "wikipedia.org" \
  --summary \
  --format json
```

### Python SDK使用

```python
from bocha_web_search import BochaWebSearch

# 初始化客户端
client = BochaWebSearch(api_key="your-api-key")

# 基本搜索
results = client.search("OpenAI最新进展")

# 带参数搜索
results = client.search(
    query="Python教程",
    freshness="oneWeek",
    count=10,
    include="github.com",
    exclude="baidu.com",
    summary=True
)

# 获取JSON格式结果
json_results = results.to_json()

# 获取文本格式结果
text_results = results.to_text()
```

## API参数说明

### query (必填)
搜索关键词，支持中文和英文。

### freshness (可选)
时间过滤选项：
- `noLimit`：不限时间（默认）
- `oneDay`：过去24小时
- `oneWeek`：过去一周
- `oneMonth`：过去一个月
- `oneYear`：过去一年
- `YYYY-MM-DDtoYYYY-MM-DD`：自定义日期范围

### summary (可选)
是否显示搜索结果摘要：
- `true`：显示摘要
- `false`：不显示摘要（默认）

### count (可选)
返回结果数量，范围1-50，默认10。

### include (可选)
包含特定网站，支持域名或子域名。

### exclude (可选)
排除特定网站，支持域名或子域名。

## 输出格式

### JSON格式
```json
{
  "query": "搜索关键词",
  "results": [
    {
      "title": "结果标题",
      "url": "https://example.com",
      "snippet": "结果摘要",
      "displayUrl": "example.com",
      "date": "2024-01-01",
      "source": "来源网站"
    }
  ],
  "summary": "搜索摘要（如果启用）",
  "metadata": {
    "count": 10,
    "freshness": "noLimit",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### 文本格式
```
搜索结果：搜索关键词

1. 结果标题
   URL: https://example.com
   摘要: 结果摘要
   来源: example.com
   日期: 2024-01-01

2. 结果标题
   URL: https://example2.com
   摘要: 结果摘要
   来源: example2.com
   日期: 2024-01-02

搜索摘要：搜索摘要内容

共找到10个结果，搜索时间：2024-01-01 12:00:00
```

## 模拟模式

当没有设置`BOCHA_API_KEY`环境变量时，技能会自动启用模拟模式，返回模拟的搜索结果用于测试和演示。

模拟模式特点：
- 无需API KEY即可测试功能
- 返回真实的搜索结果结构
- 包含示例数据
- 适合开发和演示使用

## 错误处理

技能包含完善的错误处理机制：

1. **API错误**：处理HTTP错误和API响应错误
2. **参数验证**：验证输入参数的合法性
3. **网络错误**：处理网络连接问题
4. **配置错误**：检查环境变量和配置
5. **用户友好提示**：提供清晰的错误信息和解决方案

## 配置

### 环境变量
```bash
# API密钥（必需，除非使用模拟模式）
export BOCHA_API_KEY="your-api-key-here"

# API端点（可选，默认使用官方端点）
export BOCHA_API_ENDPOINT="https://api.bocha.cn/v1/web-search"

# 请求超时（可选，默认30秒）
export BOCHA_REQUEST_TIMEOUT=30

# 启用调试模式（可选）
export BOCHA_DEBUG=true
```

### 配置文件
技能支持从以下位置读取配置：
1. 环境变量
2. `~/.openclaw/bocha-web-search.env`文件
3. 技能目录下的`.env`文件

## 开发

### 项目结构
```
bocha-web-search/
├── SKILL.md              # 技能文档（本文件）
├── bocha_web_search.py   # 主脚本
├── requirements.txt      # Python依赖
├── .env.example          # 环境变量示例
├── openapi.yaml          # OpenAPI规范
├── examples/             # 使用示例
│   ├── basic_usage.py    # 基础使用示例
│   ├── advanced_usage.py # 高级使用示例
│   └── sdk_demo.py       # SDK演示
├── docs/                 # 文档
│   └── api_reference.md  # API参考
└── tests/                # 测试
    └── test_search.py    # 测试文件
```

### 运行测试
```bash
cd bocha-web-search
python -m pytest tests/
```

## 许可证

MIT License

## 支持

- 问题反馈：GitHub Issues
- API文档：https://open.bocha.cn
- 获取API KEY：https://open.bocha.cn > API KEY管理