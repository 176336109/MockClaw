---
name: web-search
description: |
  通用Web搜索API技能，支持多个国内AI搜索平台。
  提供统一的搜索接口，可配置不同API提供商。
metadata:
  openclaw:
    emoji: "🔍"
    requires:
      bins: ["node"]
      env: ["WEB_SEARCH_API_KEY", "WEB_SEARCH_PROVIDER"]
    primaryEnv: "WEB_SEARCH_API_KEY"
---

# Web Search API Skill

通用Web搜索API技能，支持多个国内AI搜索平台。提供统一的搜索接口，可配置不同API提供商。

## 支持的提供商

### 1. DeepSeek搜索
- **API端点**: `https://api.deepseek.com/search`
- **环境变量**: `DEEPSEEK_API_KEY`
- **特点**: 免费额度大，中文优化好

### 2. 智谱AI (GLM)
- **API端点**: `https://open.bigmodel.cn/api/search`
- **环境变量**: `GLM_API_KEY`
- **特点**: 企业级服务，稳定性好

### 3. 自定义API
- **API端点**: 可配置
- **环境变量**: `CUSTOM_SEARCH_API_KEY`, `CUSTOM_SEARCH_URL`
- **特点**: 灵活适配各种API

## 快速开始

### 安装
```bash
# 将本技能目录复制到 ~/.openclaw/skills/
cp -r web-search-skill ~/.openclaw/skills/
```

### 配置环境变量
```bash
# 选择提供商并设置API密钥
export WEB_SEARCH_PROVIDER="deepseek"  # deepseek | glm | custom
export DEEPSEEK_API_KEY="your_api_key_here"

# 或者使用智谱AI
export WEB_SEARCH_PROVIDER="glm"
export GLM_API_KEY="your_glm_api_key"

# 或者自定义API
export WEB_SEARCH_PROVIDER="custom"
export CUSTOM_SEARCH_API_KEY="your_key"
export CUSTOM_SEARCH_URL="https://api.example.com/search"
```

## 使用方法

### 基本搜索
```bash
node search.mjs "搜索关键词"
```

### 带选项搜索
```bash
node search.mjs "搜索关键词" -n 10 --format json
```

### 指定提供商
```bash
node search.mjs "搜索关键词" --provider deepseek
```

## 命令行选项

| 选项 | 缩写 | 默认值 | 说明 |
|------|------|--------|------|
| `--provider` | `-p` | 环境变量 | 搜索提供商 |
| `--count` | `-n` | 5 | 结果数量 (1-20) |
| `--format` | `-f` | text | 输出格式 (text/json) |
| `--timeout` | `-t` | 10000 | 超时时间(毫秒) |
| `--debug` | `-d` | false | 调试模式 |

## 输出格式

### 文本格式 (默认)
```
## 搜索结果 (5个)

1. [标题](URL)
   摘要: 这里是搜索结果摘要...
   来源: example.com
   相关度: 0.85

2. [另一个标题](另一个URL)
   ...
```

### JSON格式
```json
{
  "query": "搜索关键词",
  "provider": "deepseek",
  "count": 5,
  "results": [
    {
      "title": "结果标题",
      "url": "https://example.com",
      "snippet": "结果摘要",
      "source": "example.com",
      "relevance": 0.85
    }
  ],
  "timestamp": "2026-02-28T12:30:00Z"
}
```

## 错误处理

技能包含完善的错误处理：

1. **API密钥缺失** - 提示用户设置环境变量
2. **网络错误** - 重试机制和超时处理
3. **API限制** - 友好的错误信息
4. **提供商不可用** - 自动切换到备用提供商

## 集成到OpenClaw

### 作为工具使用
```javascript
// 在OpenClaw工具中调用
const result = await exec(`node search.mjs "${query}" --format json`);
const data = JSON.parse(result);
```

### 创建搜索Agent
```bash
# 创建专门的搜索Agent
openclaw sessions_spawn --agent search-agent --task "使用web-search技能进行搜索"
```

## 扩展开发

### 添加新提供商
1. 在 `providers/` 目录创建新文件
2. 实现统一的接口
3. 更新 `search.mjs` 中的提供商列表

### 示例提供商模板
```javascript
// providers/template.js
module.exports = {
  name: 'template',
  search: async function(query, options) {
    // 实现搜索逻辑
    return {
      success: true,
      results: [...],
      provider: this.name
    };
  }
};
```

## 最佳实践

1. **密钥管理**: 使用环境变量，不要硬编码
2. **错误处理**: 总是处理API错误和网络异常
3. **结果缓存**: 对相同查询进行缓存以提高性能
4. **限流控制**: 遵守API提供商的速率限制

## 故障排除

### 常见问题

1. **"Missing API key"**
   ```bash
   # 检查环境变量
   echo $WEB_SEARCH_PROVIDER
   echo $DEEPSEEK_API_KEY
   ```

2. **网络超时**
   ```bash
   # 增加超时时间
   node search.mjs "查询" --timeout 30000
   ```

3. **提供商不可用**
   ```bash
   # 切换到备用提供商
   node search.mjs "查询" --provider glm
   ```

### 调试模式
```bash
node search.mjs "测试" --debug
```

## 许可证

MIT License - 自由使用和修改