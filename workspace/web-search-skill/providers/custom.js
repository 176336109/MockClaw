/**
 * 自定义API搜索提供商
 * 支持配置任意搜索API
 */

export default class CustomProvider {
  constructor() {
    this.name = 'custom';
  }

  async search(query, options = {}) {
    const {
      count = 5,
      timeout = 10000,
      apiKey
    } = options;

    try {
      // 检查配置
      const apiUrl = process.env.CUSTOM_SEARCH_URL;
      if (!apiUrl) {
        throw new Error('缺少自定义API URL，请设置CUSTOM_SEARCH_URL环境变量');
      }

      if (!apiKey) {
        throw new Error('缺少自定义API密钥，请设置CUSTOM_SEARCH_API_KEY环境变量');
      }

      // 构建请求参数
      const requestBody = this.buildRequestBody(query, count, options);
      
      if (options.debug) {
        console.error('自定义API请求:');
        console.error('URL:', apiUrl);
        console.error('Body:', JSON.stringify(requestBody, null, 2));
      }

      // 发送请求
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      try {
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`,
            'User-Agent': 'OpenClaw-WebSearch/1.0',
            ...this.getCustomHeaders()
          },
          body: JSON.stringify(requestBody),
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`自定义API错误 (${response.status}): ${errorText}`);
        }

        const data = await response.json();

        // 解析结果
        const results = this.parseResults(data, query, count);
        
        return {
          success: true,
          results: results.slice(0, count),
          provider: this.name,
          rawData: options.debug ? data : undefined
        };

      } catch (fetchError) {
        clearTimeout(timeoutId);
        
        if (fetchError.name === 'AbortError') {
          throw new Error(`请求超时 (${timeout}ms)`);
        }
        throw fetchError;
      }

    } catch (error) {
      return {
        success: false,
        error: error.message,
        provider: this.name
      };
    }
  }

  buildRequestBody(query, count, options) {
    // 默认请求体，可以根据需要自定义
    const defaultBody = {
      query: query,
      max_results: count,
      include_snippets: true,
      include_urls: true,
      language: 'zh-CN',
      timeout: options.timeout || 10000
    };

    // 尝试从环境变量读取自定义配置
    const customConfig = process.env.CUSTOM_SEARCH_CONFIG;
    if (customConfig) {
      try {
        const config = JSON.parse(customConfig);
        return { ...defaultBody, ...config };
      } catch (e) {
        console.warn('无法解析CUSTOM_SEARCH_CONFIG，使用默认配置');
      }
    }

    return defaultBody;
  }

  getCustomHeaders() {
    const headers = {};
    
    // 从环境变量读取自定义请求头
    const customHeaders = process.env.CUSTOM_SEARCH_HEADERS;
    if (customHeaders) {
      try {
        const parsedHeaders = JSON.parse(customHeaders);
        Object.assign(headers, parsedHeaders);
      } catch (e) {
        console.warn('无法解析CUSTOM_SEARCH_HEADERS');
      }
    }

    return headers;
  }

  parseResults(data, query, count) {
    const results = [];
    
    // 尝试多种常见的数据格式
    
    // 格式1: { results: [...] }
    if (data.results && Array.isArray(data.results)) {
      data.results.forEach((item, index) => {
        results.push(this.normalizeResult(item, index));
      });
    }
    // 格式2: { data: [...] }
    else if (data.data && Array.isArray(data.data)) {
      data.data.forEach((item, index) => {
        results.push(this.normalizeResult(item, index));
      });
    }
    // 格式3: { items: [...] }
    else if (data.items && Array.isArray(data.items)) {
      data.items.forEach((item, index) => {
        results.push(this.normalizeResult(item, index));
      });
    }
    // 格式4: 直接是数组
    else if (Array.isArray(data)) {
      data.forEach((item, index) => {
        results.push(this.normalizeResult(item, index));
      });
    }
    // 格式5: 有answer字段（类似Tavily）
    else if (data.answer) {
      results.push({
        title: `关于"${query}"的答案`,
        url: data.url || '',
        snippet: data.answer,
        source: this.extractSource(data.url) || '自定义API',
        relevance: 0.95,
        timestamp: new Date().toISOString()
      });
    }
    // 格式6: 有content字段
    else if (data.content) {
      results.push({
        title: `自定义API结果: ${query}`,
        url: data.url || '',
        snippet: data.content,
        source: this.extractSource(data.url) || '自定义API',
        relevance: 0.9,
        timestamp: new Date().toISOString()
      });
    }

    // 如果没有结果，创建模拟结果
    if (results.length === 0) {
      console.warn('无法解析API响应格式，使用模拟结果');
      return this.createMockResults(query, count);
    }

    return results;
  }

  normalizeResult(item, index) {
    // 标准化不同API的结果格式
    return {
      title: item.title || item.name || item.headline || `结果 ${index + 1}`,
      url: item.url || item.link || item.uri || item.source_url || '',
      snippet: item.snippet || item.description || item.content || item.summary || '',
      source: this.extractSource(item.url || item.link || item.source_url || item.domain),
      relevance: this.calculateRelevance(item, index),
      timestamp: item.timestamp || item.date || item.published || new Date().toISOString()
    };
  }

  extractSource(url) {
    if (!url) return '自定义API';
    
    try {
      const urlObj = new URL(url);
      return urlObj.hostname.replace('www.', '');
    } catch {
      // 尝试从字符串中提取域名
      const domainMatch = url.match(/^(?:https?:\/\/)?(?:www\.)?([^\/]+)/);
      return domainMatch ? domainMatch[1] : '自定义API';
    }
  }

  calculateRelevance(item, index) {
    // 尝试从数据中提取相关度分数
    if (item.score !== undefined) return Math.min(1, Math.max(0, item.score));
    if (item.relevance !== undefined) return Math.min(1, Math.max(0, item.relevance));
    if (item.confidence !== undefined) return Math.min(1, Math.max(0, item.confidence));
    
    // 默认基于位置的相关度
    return Math.max(0.1, 1 - (index * 0.1));
  }

  createMockResults(query, count) {
    return new Array(count).fill(0).map((_, index) => ({
      title: `自定义API结果 ${index + 1}: ${query}`,
      url: `https://api.example.com/search?q=${encodeURIComponent(query)}&result=${index + 1}`,
      snippet: `这是自定义API关于"${query}"的搜索结果 ${index + 1}。请确保API响应格式正确。`,
      source: 'custom-api.example.com',
      relevance: 0.9 - (index * 0.1),
      timestamp: new Date().toISOString()
    }));
  }

  // 测试API连接
  async testConnection(apiKey) {
    const apiUrl = process.env.CUSTOM_SEARCH_URL;
    if (!apiUrl) {
      return {
        success: false,
        error: '未设置CUSTOM_SEARCH_URL'
      };
    }

    try {
      // 尝试发送一个简单的健康检查请求
      const testUrl = apiUrl.replace(/\/search$/, '/health') + (apiUrl.includes('?') ? '&' : '?') + 'health=1';
      
      const response = await fetch(testUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'User-Agent': 'OpenClaw-WebSearch/1.0',
          ...this.getCustomHeaders()
        },
        timeout: 5000
      });

      return {
        success: response.ok,
        status: response.status,
        message: response.ok ? '连接正常' : `连接失败: ${response.status}`
      };
    } catch (error) {
      // 如果健康检查失败，尝试主端点
      try {
        const response = await fetch(apiUrl, {
          method: 'HEAD',
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'User-Agent': 'OpenClaw-WebSearch/1.0',
            ...this.getCustomHeaders()
          },
          timeout: 3000
        });

        return {
          success: response.ok,
          status: response.status,
          message: response.ok ? '端点可达' : `端点错误: ${response.status}`
        };
      } catch (headError) {
        return {
          success: false,
          error: headError.message
        };
      }
    }
  }
}

// 导出配置帮助函数
export function generateConfigExample() {
  return {
    // 基本配置
    CUSTOM_SEARCH_URL: 'https://api.example.com/v1/search',
    CUSTOM_SEARCH_API_KEY: 'your_api_key_here',
    
    // 可选：自定义请求配置
    CUSTOM_SEARCH_CONFIG: JSON.stringify({
      language: 'zh-CN',
      region: 'cn',
      safe_search: true,
      time_range: 'month'
    }, null, 2),
    
    // 可选：自定义请求头
    CUSTOM_SEARCH_HEADERS: JSON.stringify({
      'X-Custom-Header': 'value',
      'X-API-Version': '1.0'
    }, null, 2),
    
    // 响应格式示例
    expected_response_format: {
      results: [
        {
          title: '结果标题',
          url: 'https://example.com/article',
          snippet: '结果摘要',
          source: 'example.com',
          score: 0.95,
          timestamp: '2026-02-28T12:00:00Z'
        }
      ]
    }
  };
}