# Web Search API Skill for OpenClaw

通用Web搜索API技能，支持多个国内AI搜索平台。提供统一的搜索接口，可配置不同API提供商。

## 🚀 快速开始

### 1. 安装技能
```bash
# 复制到OpenClaw技能目录
cp -r web-search-skill ~/.openclaw/skills/
```

### 2. 配置环境变量
```bash
# 选择提供商并设置API密钥（添加到 ~/.zshrc 或 ~/.bashrc）

# 使用DeepSeek
export WEB_SEARCH_PROVIDER="deepseek"
export DEEPSEEK_API_KEY="your_deepseek_api_key"

# 或使用智谱AI
export WEB_SEARCH_PROVIDER="glm"
export GLM_API_KEY="your_glm_api_key"

# 或自定义API
export WEB_SEARCH_PROVIDER="custom"
export CUSTOM_SEARCH_API_KEY="your_custom_api_key"
export CUSTOM_SEARCH_URL="https://api.example.com/search"
```

### 3. 测试搜索
```bash
cd ~/.openclaw/skills/web-search-skill
node search.mjs "人工智能发展"
```

## 📋 功能特性

### 支持多个提供商
- **DeepSeek** - 免费额度大，中文优化好
- **智谱AI (GLM)** - 企业级服务，稳定性好
- **自定义API** - 灵活适配各种API

### 统一接口
- 相同的命令行参数
- 一致的输出格式
- 统一的错误处理

### 智能回退
- API失败时自动切换到模拟模式
- 提供商不可用时使用备用方案
- 网络错误时自动重试

## 🛠️ 使用方法

### 基本搜索
```bash
node search.mjs "搜索关键词"
```

### 高级选项
```bash
# 指定提供商和结果数量
node search.mjs "机器学习" --provider glm --count 10

# JSON格式输出
node search.mjs "深度学习" --format json

# 调试模式
node search.mjs "测试" --debug
```

### 命令行选项
| 选项 | 缩写 | 默认值 | 说明 |
|------|------|--------|------|
| `--provider` | `-p` | 环境变量 | 搜索提供商 |
| `--count` | `-n` | 5 | 结果数量 (1-20) |
| `--format` | `-f` | text | 输出格式 (text/json) |
| `--timeout` | `-t` | 10000 | 超时时间(毫秒) |
| `--debug` | `-d` | false | 调试模式 |

## 🔧 集成到OpenClaw

### 作为工具使用
在OpenClaw工具中直接调用：
```javascript
const result = await exec(`node search.mjs "${query}" --format json`);
const data = JSON.parse(result);
```

### 创建搜索Agent
```bash
# 创建专门的搜索Agent
openclaw sessions_spawn --agent search-agent --task "使用web-search技能进行搜索"
```

### 在Skill中调用
```javascript
// 在你的Skill中调用搜索
const searchResult = await exec(
  `node ${__dirname}/search.mjs "${query}" --provider deepseek --format json`
);
```

## 🎯 输出格式

### 文本格式 (默认)
```
## 搜索结果 (5个)

1. [人工智能发展趋势](https://example.com/ai-trends)
   摘要: 人工智能正在快速发展，特别是在深度学习领域...
   来源: example.com
   相关度: 0.85

2. [机器学习应用](https://example.com/ml-applications)
   ...
```

### JSON格式
```json
{
  "query": "人工智能",
  "provider": "deepseek",
  "count": 5,
  "results": [
    {
      "title": "人工智能发展趋势",
      "url": "https://example.com/ai-trends",
      "snippet": "人工智能正在快速发展...",
      "source": "example.com",
      "relevance": 0.85,
      "timestamp": "2026-02-28T12:30:00Z"
    }
  ],
  "timestamp": "2026-02-28T12:30:00Z"
}
```

## 🔌 添加新提供商

### 1. 创建提供商文件
在 `providers/` 目录创建新文件，例如 `newprovider.js`：

```javascript
export default class NewProvider {
  constructor() {
    this.name = 'newprovider';
    this.baseUrl = 'https://api.newprovider.com';
  }

  async search(query, options) {
    // 实现搜索逻辑
    return {
      success: true,
      results: [...],
      provider: this.name
    };
  }
}
```

### 2. 更新环境变量支持
在 `search.mjs` 中添加对新提供商的环境变量检查。

### 3. 测试新提供商
```bash
export WEB_SEARCH_PROVIDER="newprovider"
export NEWPROVIDER_API_KEY="your_key"
node search.mjs "测试" --provider newprovider
```

## 🐛 故障排除

### 常见问题

1. **"Missing API key" 错误**
   ```bash
   # 检查环境变量
   echo $WEB_SEARCH_PROVIDER
   echo $DEEPSEEK_API_KEY
   
   # 重新加载配置
   source ~/.zshrc
   ```

2. **网络超时**
   ```bash
   # 增加超时时间
   node search.mjs "查询" --timeout 30000
   ```

3. **提供商不可用**
   ```bash
   # 切换到其他提供商
   node search.mjs "查询" --provider glm
   ```

4. **权限问题**
   ```bash
   # 确保脚本可执行
   chmod +x search.mjs
   ```

### 调试模式
使用 `--debug` 选项查看详细日志：
```bash
node search.mjs "测试" --debug
```

## 📚 API提供商配置

### DeepSeek
1. 访问 [DeepSeek官网](https://www.deepseek.com)
2. 注册账号并获取API密钥
3. 设置环境变量：
   ```bash
   export DEEPSEEK_API_KEY="your_api_key"
   ```

### 智谱AI (GLM)
1. 访问 [智谱AI开放平台](https://open.bigmodel.cn)
2. 申请API访问权限
3. 设置环境变量：
   ```bash
   export GLM_API_KEY="your_api_key"
   ```

### 自定义API
1. 准备API端点
2. 设置环境变量：
   ```bash
   export CUSTOM_SEARCH_URL="https://api.example.com/search"
   export CUSTOM_SEARCH_API_KEY="your_api_key"
   ```

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

### 开发指南
1. Fork 本仓库
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

### 代码规范
- 使用ES6+语法
- 添加适当的注释
- 编写单元测试
- 遵循现有代码风格

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

感谢以下项目提供的灵感：
- [OpenClaw](https://github.com/openclaw/openclaw)
- [Tavily](https://tavily.com)
- [DeepSeek](https://www.deepseek.com)
- [智谱AI](https://open.bigmodel.cn)

## 📞 支持

如有问题，请：
1. 查看 [故障排除](#故障排除) 部分
2. 检查 [GitHub Issues](https://github.com/your-repo/issues)
3. 提交新的 Issue

---

**Happy Searching! 🔍**