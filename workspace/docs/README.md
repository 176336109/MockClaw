# 飞书文档专家Agent

一个专门处理飞书文档的智能Agent，能够自动化创建、转换和分析飞书文档。

## 功能特性

### 🚀 核心功能
- **智能文档创建**：根据需求自动生成结构化文档
- **格式转换**：支持Markdown到飞书文档的高质量转换
- **文档分析**：分析文档结构，提供优化建议
- **模板管理**：提供多种文档模板，支持自定义

### 📋 支持的内容类型
- 标题（H1-H3）
- 段落文本（支持粗体、斜体、删除线、下划线、行内代码）
- 无序列表和有序列表
- 代码块（支持语法高亮）
- 引用块
- 分隔线

### 🔧 技术特性
- 完整的飞书API封装
- 错误处理和重试机制
- 批量操作优化
- 缓存策略支持
- 可扩展的架构设计

## 快速开始

### 环境要求
- Python 3.8+
- 飞书开放平台应用（需要文档相关权限）
- 网络访问权限

### 安装

1. 克隆项目：
```bash
git clone <repository-url>
cd feishu-doc-agent
```

2. 安装依赖：
```bash
pip install requests
```

3. 配置飞书应用：
   - 在[飞书开放平台](https://open.feishu.cn/)创建应用
   - 获取App ID和App Secret
   - 为应用添加文档相关权限

### 基本使用

```python
from feishu_doc_agent import FeishuAPIClient, DocumentCreator

# 初始化客户端
client = FeishuAPIClient(
    app_id="your_app_id",
    app_secret="your_app_secret"
)

# 创建文档专家
creator = DocumentCreator(client)

# 从Markdown创建文档
result = creator.create_from_markdown(
    title="测试文档",
    markdown_content="""
# 标题
这是一个测试文档

## 二级标题
- 列表项1
- 列表项2

> 这是一个引用
"""
)

print(f"文档创建成功: {result['url']}")
```

### 使用模板

```python
# 创建会议纪要
meeting_data = {
    "topic": "项目启动会",
    "time": "2024-03-01 14:00",
    "participants": "张三、李四、王五",
    "location": "会议室A",
    "agenda1": "项目背景介绍",
    "agenda2": "项目目标讨论",
    "agenda3": "任务分配",
    "resolution1": "确定项目名称为'星辰计划'",
    "resolution2": "成立项目小组",
    "action1": "完成需求文档",
    "owner1": "张三",
    "deadline1": "2024-03-05",
    "action2": "技术方案设计",
    "owner2": "李四",
    "deadline2": "2024-03-08"
}

result = creator.create_meeting_minutes(meeting_data)
```

## 架构设计

### 模块结构
```
feishu_doc_agent/
├── core/
│   ├── api_client.py      # Feishu API客户端
│   ├── block_builder.py   # 文档块构建器
│   └── converter.py       # 格式转换器
├── agents/
│   ├── creator.py         # 文档创建专家
│   ├── analyzer.py        # 文档分析专家
│   └── converter.py       # 格式转换专家
├── templates/             # 文档模板
├── utils/                # 工具函数
└── config.py             # 配置文件
```

### 核心类说明

#### 1. FeishuAPIClient
飞书API的封装类，提供：
- 认证令牌管理
- 文档CRUD操作
- 错误处理和重试
- 请求频率控制

#### 2. DocumentBuilder
文档块构建器，用于：
- 创建各种类型的文档块
- 管理块样式和格式
- 处理块层级关系

#### 3. MarkdownConverter
Markdown转换器，实现：
- Markdown语法解析
- 到飞书块的映射
- 样式转换处理

#### 4. DocumentCreator
文档创建专家，提供：
- 智能文档生成
- 模板应用
- 批量操作优化

## API参考

### FeishuAPIClient

#### 初始化
```python
client = FeishuAPIClient(app_id, app_secret)
```

#### 方法
- `create_document(title, folder_token=None)` - 创建文档
- `append_blocks(document_token, blocks)` - 追加块
- `get_document_blocks(document_token)` - 获取文档块

### DocumentCreator

#### 初始化
```python
creator = DocumentCreator(api_client)
```

#### 方法
- `create_from_markdown(title, markdown_content, folder_token=None)` - 从Markdown创建文档
- `create_meeting_minutes(meeting_data)` - 创建会议纪要
- `create_project_proposal(project_data)` - 创建项目提案

## 高级用法

### 自定义模板
```python
# 创建自定义模板
custom_template = {
    "name": "周报模板",
    "sections": [
        {"type": "heading1", "content": "周报 - {week}"},
        {"type": "heading2", "content": "本周工作"},
        {"type": "bullet", "content": "{work_item1}"},
        {"type": "bullet", "content": "{work_item2}"},
        {"type": "heading2", "content": "下周计划"},
        {"type": "bullet", "content": "{plan_item1}"},
        {"type": "bullet", "content": "{plan_item2}"}
    ]
}

# 使用自定义模板
creator.add_template("weekly_report", custom_template)
result = creator.create_from_template("weekly_report", template_data)
```

### 批量处理
```python
# 批量创建文档
documents = [
    {"title": "文档1", "content": "内容1"},
    {"title": "文档2", "content": "内容2"},
    {"title": "文档3", "content": "内容3"}
]

for doc in documents:
    result = creator.create_from_markdown(doc["title"], doc["content"])
    print(f"创建成功: {result['url']}")
    time.sleep(1)  # 避免频率限制
```

### 错误处理
```python
try:
    result = creator.create_from_markdown(title, content)
except RateLimitError as e:
    print(f"频率限制，等待后重试: {e}")
    time.sleep(60)
    result = creator.create_from_markdown(title, content)
except AuthenticationError as e:
    print(f"认证失败: {e}")
    # 重新获取令牌
except Exception as e:
    print(f"创建文档失败: {e}")
```

## 配置说明

### 环境变量
```bash
export FEISHU_APP_ID=your_app_id
export FEISHU_APP_SECRET=your_app_secret
export FEISHU_DOC_FOLDER_TOKEN=folder_token  # 可选，默认文档存放文件夹
```

### 配置文件
创建 `config.yaml`：
```yaml
feishu:
  app_id: your_app_id
  app_secret: your_app_secret
  default_folder: folder_token
  
agent:
  batch_size: 10
  retry_times: 3
  timeout: 30
  
templates:
  meeting_minutes: templates/meeting_minutes.md
  project_proposal: templates/project_proposal.md
  weekly_report: templates/weekly_report.md
```

## 性能优化

### 批量操作
- 使用批量添加块，减少API调用次数
- 合理设置批次大小（建议10-20个块/批次）

### 缓存策略
- 缓存访问令牌，避免频繁获取
- 缓存文档结构，减少重复查询

### 错误重试
- 实现指数退避重试机制
- 区分可重试错误和不可重试错误

## 限制和注意事项

### API限制
- 频率限制：注意飞书API的调用频率限制
- 大小限制：单个文档最大10MB，单个块最大1MB
- 功能限制：某些高级功能（如复杂表格）可能不支持

### 转换限制
- Markdown表格无法直接转换
- 复杂嵌套结构可能丢失
- 某些HTML标签不支持

### 最佳实践
1. **测试环境先行**：先在测试环境验证功能
2. **逐步迁移**：分批处理大量文档
3. **监控日志**：记录所有操作日志
4. **备份数据**：重要文档定期备份

## 故障排除

### 常见问题

#### 1. 认证失败
- 检查App ID和App Secret是否正确
- 确认应用权限是否足够
- 验证网络连接是否正常

#### 2. 频率限制
- 降低请求频率
- 实现指数退避重试
- 考虑批量操作减少调用次数

#### 3. 格式转换问题
- 简化Markdown结构
- 分步转换复杂文档
- 验证转换结果

#### 4. 性能问题
- 优化批次大小
- 实现缓存机制
- 使用异步处理

### 调试模式
```python
import logging

logging.basicConfig(level=logging.DEBUG)
# 现在可以看到详细的请求和响应信息
```

## 开发指南

### 添加新功能

#### 1. 添加新块类型
```python
# 在block_builder.py中添加新方法
def add_table(self, rows, columns):
    """添加表格块"""
    # 实现表格块构建逻辑
```

#### 2. 添加新模板
```python
# 创建新模板文件
# templates/new_template.md

# 在DocumentCreator中注册模板
creator.add_template("new_template", template_content)
```

#### 3. 扩展转换器
```python
# 在converter.py中添加新解析规则
def _parse_table(self, lines):
    """解析Markdown表格"""
    # 实现表格解析逻辑
```

### 测试
```bash
# 运行单元测试
python -m pytest tests/

# 运行集成测试
python tests/integration_test.py

# 性能测试
python tests/performance_test.py
```

### 代码规范
- 遵循PEP 8编码规范
- 添加类型注解
- 编写文档字符串
- 添加单元测试

## 贡献指南

### 报告问题
1. 在GitHub Issues中创建问题
2. 描述问题现象和复现步骤
3. 提供相关日志和错误信息

### 提交代码
1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

### 开发流程
1. 讨论功能设计
2. 实现核心功能
3. 编写测试用例
4. 更新文档
5. 代码审查
6. 合并发布

## 许可证

本项目采用MIT许可证。详见[LICENSE](LICENSE)文件。

## 支持

- 文档：查看[详细文档](docs/)
- 问题：提交[GitHub Issues](https://github.com/your-repo/issues)
- 讨论：加入[Discord频道](https://discord.gg/your-channel)

## 更新日志

### v1.0.0 (2024-03-01)
- 初始版本发布
- 支持基本文档创建和转换
- 提供会议纪要模板
- 实现错误处理和重试机制

---

**飞书文档专家Agent** - 让文档处理更智能、更高效！