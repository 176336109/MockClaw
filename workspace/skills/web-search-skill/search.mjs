#!/usr/bin/env node

/**
 * Web Search API - 通用搜索脚本
 * 支持多个国内AI搜索平台
 */

import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 命令行参数解析
function parseArgs() {
  const args = process.argv.slice(2);
  if (args.length === 0 || args[0] === '-h' || args[0] === '--help') {
    usage();
  }

  const query = args[0];
  const options = {
    provider: process.env.WEB_SEARCH_PROVIDER || 'deepseek',
    count: 5,
    format: 'text',
    timeout: 10000,
    debug: false
  };

  for (let i = 1; i < args.length; i++) {
    const arg = args[i];
    
    if (arg === '-p' || arg === '--provider') {
      options.provider = args[i + 1];
      i++;
    } else if (arg === '-n' || arg === '--count') {
      options.count = parseInt(args[i + 1], 10);
      i++;
    } else if (arg === '-f' || arg === '--format') {
      options.format = args[i + 1];
      i++;
    } else if (arg === '-t' || arg === '--timeout') {
      options.timeout = parseInt(args[i + 1], 10);
      i++;
    } else if (arg === '-d' || arg === '--debug') {
      options.debug = true;
    } else if (arg.startsWith('-')) {
      console.error(`未知参数: ${arg}`);
      usage();
    }
  }

  // 验证参数
  if (options.count < 1 || options.count > 20) {
    console.error('结果数量必须在 1-20 之间');
    process.exit(1);
  }

  if (!['text', 'json'].includes(options.format)) {
    console.error('输出格式必须是 text 或 json');
    process.exit(1);
  }

  return { query, options };
}

function usage() {
  console.error(`
Web Search API - 通用搜索工具

用法:
  node search.mjs "查询关键词" [选项]

选项:
  -p, --provider <name>   搜索提供商 (deepseek, glm, custom)
  -n, --count <number>    结果数量 (1-20, 默认: 5)
  -f, --format <format>   输出格式 (text, json, 默认: text)
  -t, --timeout <ms>      超时时间(毫秒, 默认: 10000)
  -d, --debug             调试模式
  -h, --help              显示帮助

环境变量:
  WEB_SEARCH_PROVIDER     默认搜索提供商
  DEEPSEEK_API_KEY        DeepSeek API密钥
  GLM_API_KEY             智谱AI API密钥
  CUSTOM_SEARCH_API_KEY   自定义API密钥
  CUSTOM_SEARCH_URL       自定义API URL

示例:
  node search.mjs "人工智能发展"
  node search.mjs "机器学习" -p glm -n 10 -f json
  node search.mjs "深度学习" --debug
`);
  process.exit(2);
}

// 加载提供商模块
async function loadProvider(providerName) {
  try {
    const providerPath = join(__dirname, 'providers', `${providerName}.js`);
    
    // 检查文件是否存在
    if (!fs.existsSync(providerPath)) {
      throw new Error(`提供商 '${providerName}' 不存在`);
    }

    // 动态导入
    const module = await import(`file://${providerPath}`);
    return module.default;
  } catch (error) {
    console.error(`加载提供商失败: ${error.message}`);
    
    // 尝试加载默认提供商
    if (providerName !== 'deepseek') {
      console.log('尝试使用默认提供商: deepseek');
      return loadProvider('deepseek');
    }
    
    throw error;
  }
}

// 检查API密钥
function checkApiKey(provider) {
  const envVars = {
    deepseek: 'DEEPSEEK_API_KEY',
    glm: 'GLM_API_KEY',
    custom: 'CUSTOM_SEARCH_API_KEY'
  };

  const envVar = envVars[provider];
  if (!envVar) {
    throw new Error(`未知提供商: ${provider}`);
  }

  const apiKey = process.env[envVar];
  if (!apiKey) {
    throw new Error(`缺少环境变量: ${envVar}`);
  }

  return apiKey;
}

// 格式化输出
function formatResults(results, query, options) {
  if (options.format === 'json') {
    return JSON.stringify({
      query,
      provider: options.provider,
      count: results.length,
      results: results.map(r => ({
        title: r.title || '',
        url: r.url || '',
        snippet: r.snippet || '',
        source: r.source || '',
        relevance: r.relevance || 0,
        timestamp: r.timestamp || new Date().toISOString()
      })),
      timestamp: new Date().toISOString()
    }, null, 2);
  }

  // 文本格式
  let output = `## 搜索结果 (${results.length}个)\n\n`;
  
  results.forEach((result, index) => {
    output += `${index + 1}. [${result.title || '无标题'}](${result.url || '#'})\n`;
    
    if (result.snippet) {
      output += `   摘要: ${result.snippet}\n`;
    }
    
    if (result.source) {
      output += `   来源: ${result.source}\n`;
    }
    
    if (result.relevance) {
      output += `   相关度: ${result.relevance.toFixed(2)}\n`;
    }
    
    output += '\n';
  });

  return output;
}

// 模拟搜索（在没有真实API时使用）
async function mockSearch(query, options) {
  console.warn('警告: 使用模拟搜索模式 - 请配置真实的API密钥');
  
  return [
    {
      title: `关于"${query}"的搜索结果示例`,
      url: 'https://example.com/search-result',
      snippet: `这是关于"${query}"的模拟搜索结果。在实际使用中，请配置真实的API密钥以获取真实的搜索结果。`,
      source: 'example.com',
      relevance: 0.95,
      timestamp: new Date().toISOString()
    },
    {
      title: '如何配置Web Search API',
      url: 'https://example.com/config-guide',
      snippet: '配置API密钥的详细指南，包括环境变量设置和提供商选择。',
      source: 'docs.example.com',
      relevance: 0.85,
      timestamp: new Date().toISOString()
    }
  ].slice(0, options.count);
}

// 主函数
async function main() {
  try {
    const { query, options } = parseArgs();
    
    if (options.debug) {
      console.error('调试信息:');
      console.error(`查询: ${query}`);
      console.error(`选项: ${JSON.stringify(options, null, 2)}`);
      console.error(`环境变量 WEB_SEARCH_PROVIDER: ${process.env.WEB_SEARCH_PROVIDER}`);
    }

    let results;
    
    try {
      // 尝试加载真实提供商
      const Provider = await loadProvider(options.provider);
      const apiKey = checkApiKey(options.provider);
      
      if (options.debug) {
        console.error(`使用提供商: ${options.provider}`);
        console.error(`API密钥: ${apiKey.substring(0, 8)}...`);
      }
      
      // 创建提供商实例并执行搜索
      const provider = new Provider();
      const searchResult = await provider.search(query, {
        count: options.count,
        timeout: options.timeout,
        apiKey
      });
      
      if (searchResult.success) {
        results = searchResult.results;
      } else {
        throw new Error(searchResult.error || '搜索失败');
      }
      
    } catch (error) {
      if (options.debug) {
        console.error(`真实搜索失败: ${error.message}`);
      }
      
      // 回退到模拟搜索
      results = await mockSearch(query, options);
    }

    // 输出结果
    const output = formatResults(results, query, options);
    console.log(output);

  } catch (error) {
    console.error(`错误: ${error.message}`);
    
    if (options?.debug) {
      console.error(error.stack);
    }
    
    process.exit(1);
  }
}

// 执行主函数
main();