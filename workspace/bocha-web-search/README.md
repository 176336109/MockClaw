# bocha-web-search

博查AI Web Search API的OpenClaw技能，提供强大的网页搜索功能。

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-green.svg)](https://openclaw.ai)

## 特性

- 🔍 **完整API支持**：支持博查AI Web Search API的所有参数
- 📊 **多格式输出**：支持text和json格式输出
- 🎭 **模拟模式**：当没有API KEY时自动启用模拟模式
- 🛡️ **完善错误处理**：详细的错误信息和用户友好提示
- 📚 **完整文档**：包含使用示例、API参考和SDK文档
- 🧪 **测试覆盖**：包含单元测试和集成测试
- 🔧 **易于集成**：提供Python SDK和命令行接口

## 快速开始

### 安装

1. 克隆或下载本仓库：
   ```bash
   git clone https://github.com/yourusername/bocha-web-search.git
   cd bocha-web-search
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置API密钥：
   ```bash
   # 复制示例配置文件
   cp .env.example .env
   
   # 编辑.env文件，添加您的API密钥
   # 从 https://open.bocha.cn 获取API密钥
   ```

### 基本使用

#### 命令行使用
```bash
# 基本搜索
python bocha_web_search.py "OpenAI最新进展"

# 带参数搜索
python bocha_web_search.py "Python教程" \
  --freshness oneWeek \
  --count 15 \
  --include "github.com" \
  --summary \
  --format json
```

#### Python SDK使用
```python
from bocha_web_search import BochaWebSearch

# 初始化客户端
client = BochaWebSearch()

# 执行搜索
results = client.search("机器学习", count=10, summary=True)

# 处理结果
for i, result in enumerate(results.results, 1):
    print(f"{i}. {result.title}")
    print(f"   链接: {result.url}")
    print(f"   摘要: {result.snippet[:100]}...")

# 获取不同格式
print(results.to_json())  # JSON格式
print(results.to_text())  # 文本格式
```

## 详细文档

### 目录结构
```
bocha-web-search/
├── SKILL.md              # 技能文档
├── bocha_web_search.py   # 主脚本
├── requirements.txt      # Python依赖
├── .env.example          # 环境变量示例
├── openapi.yaml          # OpenAPI规范
├── README.md             # 本文件
├── examples/             # 使用示例
│   ├── basic_usage.py    # 基础使用
│   ├── advanced_usage.py # 高级使用
│   └── sdk_demo.py       # SDK演示
├── docs/                 # 文档
│   └── api_reference.md  # API参考
└── tests/                # 测试
    └── test_search.py    # 测试文件
```

### API参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `query` | string | 是 | - | 搜索关键词 |
| `freshness` | string | 否 | `noLimit` | 时间过滤：`noLimit`, `oneDay`, `oneWeek`, `oneMonth`, `oneYear`, 日期范围 |
| `summary` | boolean | 否 | `false` | 是否显示摘要 |
| `count` | integer | 否 | `10` | 结果数量（1-50） |
| `include` | string | 否 | - | 包含特定网站 |
| `exclude` | string | 否 | - | 排除特定网站 |

### 输出格式

#### JSON格式
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
  "summary": "搜索摘要",
  "metadata": {
    "count": 10,
    "freshness": "noLimit",
    "timestamp": "2024-01-01T12:00:00Z",
    "mode": "real"
  }
}
```

#### 文本格式
```
搜索结果：搜索关键词

1. 结果标题
   URL: https://example.com
   摘要: 结果摘要
   来源: example.com
   日期: 2024-01-01

搜索摘要：搜索摘要内容

共找到10个结果，搜索时间：2024-01-01 12:00:00
```

### 模拟模式

当没有设置`BOCHA_API_KEY`环境变量时，技能会自动启用模拟模式：

- 无需API KEY即可测试功能
- 返回真实的搜索结果结构
- 包含示例数据
- 适合开发和演示使用

```python
# 模拟模式示例
client = BochaWebSearch()  # 不传API KEY
results = client.search("测试查询")
print(f"模式: {results.metadata.get('mode')}")  # 输出: mock
```

## 高级功能

### 网站过滤
```python
# 只搜索github.com的结果
results = client.search("Python", include="github.com")

# 排除baidu.com的结果
results = client.search("教程", exclude="baidu.com")

# 组合使用
results = client.search(
    "开源项目",
    include="github.com",
    exclude="gitee.com"
)
```

### 时间范围搜索
```python
# 过去一周的结果
results = client.search("新闻", freshness="oneWeek")

# 自定义日期范围
results = client.search(
    "科技新闻",
    freshness="2024-01-01to2024-12-31"
)
```

### 批量搜索
```python
queries = ["机器学习", "深度学习", "自然语言处理"]
all_results = {}

for query in queries:
    results = client.search(query, count=5)
    all_results[query] = results.to_dict()

# 保存到文件
import json
with open("batch_results.json", "w") as f:
    json.dump(all_results, f, indent=2)
```

## 集成OpenClaw

### 作为OpenClaw技能使用

1. 将技能目录复制到OpenClaw的skills目录：
   ```bash
   cp -r bocha-web-search ~/.openclaw/skills/
   ```

2. 在OpenClaw中直接使用：
   ```bash
   openclaw bocha-web-search "搜索关键词"
   ```

### 配置OpenClaw别名

在OpenClaw配置中添加别名，简化使用：

```yaml
# ~/.openclaw/config.yaml
aliases:
  search: "bocha-web-search"
  bsearch: "bocha-web-search --format json"
```

然后可以直接使用：
```bash
openclaw search "关键词"
openclaw bsearch "关键词"  # JSON格式输出
```

## 开发

### 运行测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_search.py::TestBochaWebSearch

# 带详细输出
python -m pytest tests/ -v
```

### 代码规范
```bash
# 格式化代码（如果安装了black）
black bocha_web_search.py

# 检查代码风格（如果安装了flake8）
flake8 bocha_web_search.py
```

### 构建文档
```bash
# 生成API文档（如果安装了pdoc）
pdoc --html bocha_web_search.py --output-dir docs/
```

## 故障排除

### 常见问题

1. **错误：认证失败**
   - 检查`BOCHA_API_KEY`环境变量是否正确
   - 确认API密钥是否有效（访问 https://open.bocha.cn）
   - 尝试重新生成API密钥

2. **错误：网络连接错误**
   - 检查网络连接
   - 确认防火墙是否允许访问API端点
   - 尝试增加超时时间：`--timeout 60`

3. **错误：结果数量无效**
   - 确保`count`参数在1-50之间
   - 检查命令行参数是否正确传递

4. **模拟模式一直启用**
   - 检查是否设置了`BOCHA_API_KEY`环境变量
   - 确认.env文件是否正确加载
   - 尝试直接传递API密钥：`BochaWebSearch(api_key="your_key")`

### 调试模式

启用调试模式获取更多信息：
```bash
python bocha_web_search.py "测试" --debug
```

或设置环境变量：
```bash
export BOCHA_DEBUG=true
```

## 贡献

欢迎贡献！请遵循以下步骤：

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

### 开发指南
- 遵循PEP 8代码风格
- 添加适当的测试
- 更新文档
- 确保所有测试通过

## 许可证

本项目基于MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

- 问题反馈：[GitHub Issues](https://github.com/yourusername/bocha-web-search/issues)
- API文档：[博查AI开放平台](https://open.bocha.cn)
- 获取API密钥：[API KEY管理](https://open.bocha.cn > API KEY管理)

## 致谢

- [博查AI](https://bocha.cn) - 提供强大的Web Search API
- [OpenClaw](https://openclaw.ai) - 优秀的AI助手平台
- 所有贡献者和用户

---

**提示**：使用模拟模式进行开发和测试，避免消耗API调用次数。在生产环境中使用前，请确保配置正确的API密钥。