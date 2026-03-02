/**
 * DeepSeek搜索提供商
 * 使用DeepSeek API进行搜索
 */

export default class DeepSeekProvider {
  constructor() {
    this.name = 'deepseek';
    this.baseUrl = 'https://api.deepseek.com';
  }

  async search(query, options = {}) {
    const {
      count = 5,
      timeout = 10000,
      apiKey
    } = options;

    try {
      // 检查API密钥
      if (!apiKey) {
        throw new Error('缺少DeepSeek API密钥，请设置DEEPSEEK_API_KEY环境变量');
      }

      // 构建请求参数
      const requestBody = {
        query: query,
        max_results: Math.min(count, 10), // DeepSeek可能有限制
        include_answer: true,
        include_raw_content: false
      };

      if (options.debug) {
        console.error('DeepSeek请求参数:', JSON.stringify(requestBody, null, 2));
      }

      // 发送请求
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      try {
        const response = await fetch(`${this.baseUrl}/search`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`,
            'User-Agent': 'OpenClaw-WebSearch/1.0'
          },
          body: JSON.stringify(requestBody),
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`DeepSeek API错误 (${response.status}): ${errorText}`);
        }

        const data = await response.json();

        // 解析结果
        const results = this.parseResults(data, query);
        
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

  parseResults(data, query) {
    const results = [];
    
    // 尝试不同的结果格式
    if (data.results && Array.isArray(data.results)) {
      // 标准格式
      data.results.forEach((item, index) => {
        results.push({
          title: item.title || `结果 ${index + 1}`,
          url: item.url || '',
          snippet: item.snippet || item.content || '',
          source: this.extractSource(item.url),
          relevance: item.score || 1 - (index * 0.1),
          timestamp: new Date().toISOString()
        });
      });
    } else if (data.answer) {
      // 如果有AI生成的答案
      results.push({
        title: `关于"${query}"的答案`,
        url: '',
        snippet: data.answer,
        source: 'deepseek.ai',
        relevance: 0.95,
        timestamp: new Date().toISOString()
      });
    } else if (data.data && Array.isArray(data.data)) {
      // 备用格式
      data.data.forEach((item, index) => {
        results.push({
          title: item.title || item.name || `结果 ${index + 1}`,
          url: item.url || item.link || '',
          snippet: item.description || item.content || '',
          source: this.extractSource(item.url || item.link),
          relevance: item.relevance || item.score || 1 - (index * 0.1),
          timestamp: item.timestamp || new Date().toISOString()
        });
      });
    }

    // 如果没有结果，返回默认结果
    if (results.length === 0) {
      results.push({
        title: `搜索: ${query}`,
        url: 'https://www.deepseek.com',
        snippet: '使用DeepSeek API进行搜索，请确保API密钥正确配置。',
        source: 'deepseek.com',
        relevance: 0.9,
        timestamp: new Date().toISOString()
      });
    }

    return results;
  }

  extractSource(url) {
    if (!url) return 'unknown';
    
    try {
      const urlObj = new URL(url);
      return urlObj.hostname.replace('www.', '');
    } catch {
      return 'unknown';
    }
  }

  // 测试API连接
  async testConnection(apiKey) {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'User-Agent': 'OpenClaw-WebSearch/1.0'
        },
        timeout: 5000
      });

      return {
        success: response.ok,
        status: response.status,
        message: response.ok ? '连接正常' : `连接失败: ${response.status}`
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }
}

// 导出模拟搜索函数（用于测试）
export async function mockDeepSeekSearch(query, count = 5) {
  return new Array(count).fill(0).map((_, index) => ({
    title: `DeepSeek结果 ${index + 1}: ${query}`,
    url: `https://deepseek.com/search?q=${encodeURIComponent(query)}&result=${index + 1}`,
    snippet: `这是DeepSeek关于"${query}"的模拟搜索结果 ${index + 1}。在实际使用中，请配置真实的DeepSeek API密钥。`,
    source: 'deepseek.com',
    relevance: 1 - (index * 0.15),
    timestamp: new Date().toISOString()
  }));
}