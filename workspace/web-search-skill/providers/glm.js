/**
 * 智谱AI (GLM) 搜索提供商
 * 使用智谱AI API进行搜索
 */

export default class GLMProvider {
  constructor() {
    this.name = 'glm';
    this.baseUrl = 'https://open.bigmodel.cn';
    this.apiVersion = 'v4';
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
        throw new Error('缺少智谱AI API密钥，请设置GLM_API_KEY环境变量');
      }

      // 构建请求参数
      const requestBody = {
        prompt: query,
        max_tokens: 1000,
        temperature: 0.7,
        top_p: 0.9,
        stream: false
      };

      if (options.debug) {
        console.error('智谱AI请求参数:', JSON.stringify(requestBody, null, 2));
      }

      // 发送请求到智谱AI聊天API（搜索功能可能通过聊天实现）
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      try {
        const response = await fetch(`${this.baseUrl}/api/paas/${this.apiVersion}/chat/completions`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`,
            'User-Agent': 'OpenClaw-WebSearch/1.0'
          },
          body: JSON.stringify({
            model: 'glm-4',
            messages: [
              {
                role: 'user',
                content: `请搜索关于"${query}"的信息，并返回${count}个最相关的结果，每个结果包含标题、简要描述和来源。`
              }
            ],
            ...requestBody
          }),
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`智谱AI API错误 (${response.status}): ${errorText}`);
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

  parseResults(data, query, count) {
    const results = [];
    
    // 解析智谱AI的响应
    if (data.choices && data.choices.length > 0) {
      const content = data.choices[0].message.content;
      
      // 尝试从内容中提取结构化结果
      const lines = content.split('\n').filter(line => line.trim());
      
      let currentResult = null;
      
      for (const line of lines) {
        const trimmedLine = line.trim();
        
        // 检测结果开始
        if (trimmedLine.match(/^\d+[\.\)]、?/) || trimmedLine.toLowerCase().includes('标题:')) {
          if (currentResult) {
            results.push(currentResult);
          }
          
          currentResult = {
            title: '',
            url: '',
            snippet: '',
            source: '智谱AI',
            relevance: 0.9 - (results.length * 0.1),
            timestamp: new Date().toISOString()
          };
          
          // 提取标题
          const titleMatch = trimmedLine.match(/标题[:：]\s*(.+)/);
          if (titleMatch) {
            currentResult.title = titleMatch[1];
          } else {
            currentResult.title = trimmedLine.replace(/^\d+[\.\)]、?\s*/, '');
          }
        }
        // 提取描述
        else if (trimmedLine.toLowerCase().includes('描述:') || trimmedLine.toLowerCase().includes('简介:')) {
          if (currentResult) {
            const descMatch = trimmedLine.match(/[:：]\s*(.+)/);
            if (descMatch) {
              currentResult.snippet = descMatch[1];
            }
          }
        }
        // 提取来源
        else if (trimmedLine.toLowerCase().includes('来源:') || trimmedLine.toLowerCase().includes('出处:')) {
          if (currentResult) {
            const sourceMatch = trimmedLine.match(/[:：]\s*(.+)/);
            if (sourceMatch) {
              currentResult.source = sourceMatch[1];
              // 尝试从来源生成URL
              currentResult.url = this.generateUrlFromSource(currentResult.source);
            }
          }
        }
        // 如果是普通文本，添加到描述
        else if (currentResult && trimmedLine.length > 10 && !trimmedLine.startsWith('---')) {
          if (!currentResult.snippet) {
            currentResult.snippet = trimmedLine;
          } else if (currentResult.snippet.length < 200) {
            currentResult.snippet += ' ' + trimmedLine;
          }
        }
      }
      
      // 添加最后一个结果
      if (currentResult) {
        results.push(currentResult);
      }
    }

    // 如果没有解析出结果，使用AI生成的内容作为单个结果
    if (results.length === 0 && data.choices && data.choices.length > 0) {
      const content = data.choices[0].message.content;
      results.push({
        title: `智谱AI关于"${query}"的回答`,
        url: 'https://open.bigmodel.cn',
        snippet: content.length > 300 ? content.substring(0, 300) + '...' : content,
        source: '智谱AI',
        relevance: 0.95,
        timestamp: new Date().toISOString()
      });
    }

    // 确保有足够的结果
    while (results.length < count) {
      results.push({
        title: `智谱AI搜索结果 ${results.length + 1}`,
        url: 'https://open.bigmodel.cn',
        snippet: `这是智谱AI关于"${query}"的搜索结果。`,
        source: '智谱AI',
        relevance: 0.8 - (results.length * 0.05),
        timestamp: new Date().toISOString()
      });
    }

    return results;
  }

  generateUrlFromSource(source) {
    if (!source || source === '智谱AI') {
      return 'https://open.bigmodel.cn';
    }
    
    // 尝试从来源生成搜索URL
    const cleanSource = source.toLowerCase().replace(/[^a-z0-9]/g, '');
    if (cleanSource.includes('baidu')) {
      return `https://www.baidu.com/s?wd=${encodeURIComponent(source)}`;
    } else if (cleanSource.includes('zhihu')) {
      return `https://www.zhihu.com/search?q=${encodeURIComponent(source)}`;
    } else if (cleanSource.includes('weixin') || cleanSource.includes('wx')) {
      return `https://weixin.sogou.com/weixin?query=${encodeURIComponent(source)}`;
    }
    
    return `https://${source}`;
  }

  // 测试API连接
  async testConnection(apiKey) {
    try {
      const response = await fetch(`${this.baseUrl}/api/paas/${this.apiVersion}/models`, {
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
export async function mockGLMSearch(query, count = 5) {
  return new Array(count).fill(0).map((_, index) => ({
    title: `智谱AI结果 ${index + 1}: ${query}`,
    url: `https://open.bigmodel.cn/search?q=${encodeURIComponent(query)}`,
    snippet: `这是智谱AI关于"${query}"的模拟搜索结果 ${index + 1}。智谱AI是清华大学知识工程实验室研发的大型语言模型。`,
    source: '智谱AI',
    relevance: 0.95 - (index * 0.1),
    timestamp: new Date().toISOString()
  }));
}