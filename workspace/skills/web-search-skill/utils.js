/**
 * Web Search Skill 工具函数
 */

/**
 * 验证搜索查询
 * @param {string} query - 搜索查询
 * @returns {boolean} 是否有效
 */
export function validateQuery(query) {
  if (!query || typeof query !== 'string') {
    return false;
  }
  
  const trimmed = query.trim();
  if (trimmed.length === 0) {
    return false;
  }
  
  // 检查是否只是空格或特殊字符
  if (!/[a-zA-Z0-9\u4e00-\u9fa5]/.test(trimmed)) {
    return false;
  }
  
  return true;
}

/**
 * 清理查询字符串
 * @param {string} query - 原始查询
 * @returns {string} 清理后的查询
 */
export function cleanQuery(query) {
  if (!query) return '';
  
  // 移除多余空格
  let cleaned = query.trim().replace(/\s+/g, ' ');
  
  // 移除可能的安全问题字符（简单过滤）
  cleaned = cleaned.replace(/[<>"']/g, '');
  
  // 限制长度
  const maxLength = 500;
  if (cleaned.length > maxLength) {
    cleaned = cleaned.substring(0, maxLength) + '...';
  }
  
  return cleaned;
}

/**
 * 计算查询的相关度分数（简单实现）
 * @param {string} query - 搜索查询
 * @param {string} text - 要匹配的文本
 * @returns {number} 相关度分数 0-1
 */
export function calculateRelevance(query, text) {
  if (!query || !text) return 0;
  
  const queryWords = query.toLowerCase().split(/\s+/).filter(w => w.length > 1);
  const textLower = text.toLowerCase();
  
  if (queryWords.length === 0) return 0;
  
  let matchCount = 0;
  for (const word of queryWords) {
    if (textLower.includes(word)) {
      matchCount++;
    }
  }
  
  return matchCount / queryWords.length;
}

/**
 * 格式化时间戳
 * @param {string|Date} timestamp - 时间戳
 * @param {string} format - 格式 (relative|iso|local)
 * @returns {string} 格式化后的时间
 */
export function formatTimestamp(timestamp, format = 'relative') {
  if (!timestamp) return '';
  
  const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
  
  if (isNaN(date.getTime())) {
    return '';
  }
  
  switch (format) {
    case 'iso':
      return date.toISOString();
    
    case 'local':
      return date.toLocaleString('zh-CN');
    
    case 'relative':
    default:
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);
      
      if (diffMins < 1) return '刚刚';
      if (diffMins < 60) return `${diffMins}分钟前`;
      if (diffHours < 24) return `${diffHours}小时前`;
      if (diffDays < 7) return `${diffDays}天前`;
      
      return date.toLocaleDateString('zh-CN');
  }
}

/**
 * 截断文本
 * @param {string} text - 原始文本
 * @param {number} maxLength - 最大长度
 * @param {string} suffix - 后缀
 * @returns {string} 截断后的文本
 */
export function truncateText(text, maxLength = 200, suffix = '...') {
  if (!text || text.length <= maxLength) {
    return text || '';
  }
  
  // 尝试在句子边界截断
  const truncated = text.substring(0, maxLength);
  const lastPeriod = truncated.lastIndexOf('.');
  const lastQuestion = truncated.lastIndexOf('?');
  const lastExclamation = truncated.lastIndexOf('!');
  const lastBoundary = Math.max(lastPeriod, lastQuestion, lastExclamation);
  
  if (lastBoundary > maxLength * 0.5) {
    return truncated.substring(0, lastBoundary + 1) + suffix;
  }
  
  return truncated + suffix;
}

/**
 * 提取域名
 * @param {string} url - URL
 * @returns {string} 域名
 */
export function extractDomain(url) {
  if (!url) return '';
  
  try {
    const urlObj = new URL(url);
    let domain = urlObj.hostname;
    
    // 移除www前缀
    if (domain.startsWith('www.')) {
      domain = domain.substring(4);
    }
    
    return domain;
  } catch {
    // 如果不是有效的URL，尝试提取
    const match = url.match(/^(?:https?:\/\/)?(?:www\.)?([^\/]+)/);
    return match ? match[1] : '';
  }
}

/**
 * 生成搜索URL
 * @param {string} provider - 提供商
 * @param {string} query - 查询
 * @returns {string} 搜索URL
 */
export function generateSearchUrl(provider, query) {
  const encodedQuery = encodeURIComponent(query);
  
  const urls = {
    deepseek: `https://www.deepseek.com/search?q=${encodedQuery}`,
    glm: `https://open.bigmodel.cn?q=${encodedQuery}`,
    baidu: `https://www.baidu.com/s?wd=${encodedQuery}`,
    google: `https://www.google.com/search?q=${encodedQuery}`,
    bing: `https://www.bing.com/search?q=${encodedQuery}`,
    duckduckgo: `https://duckduckgo.com/?q=${encodedQuery}`
  };
  
  return urls[provider] || urls.baidu;
}

/**
 * 延迟函数
 * @param {number} ms - 毫秒
 * @returns {Promise} Promise
 */
export function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 重试函数
 * @param {Function} fn - 要重试的函数
 * @param {number} maxRetries - 最大重试次数
 * @param {number} delayMs - 延迟毫秒数
 * @returns {Promise} Promise
 */
export async function retry(fn, maxRetries = 3, delayMs = 1000) {
  let lastError;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      if (attempt < maxRetries) {
        const waitTime = delayMs * Math.pow(2, attempt - 1); // 指数退避
        console.warn(`尝试 ${attempt}/${maxRetries} 失败，${waitTime}ms后重试: ${error.message}`);
        await delay(waitTime);
      }
    }
  }
  
  throw lastError;
}

/**
 * 验证API响应
 * @param {any} response - API响应
 * @returns {boolean} 是否有效
 */
export function validateApiResponse(response) {
  if (!response) return false;
  
  // 检查是否有错误
  if (response.error) return false;
  
  // 检查是否有结果
  if (response.results && Array.isArray(response.results)) {
    return response.results.length > 0;
  }
  
  if (response.data && Array.isArray(response.data)) {
    return response.data.length > 0;
  }
  
  if (response.answer && typeof response.answer === 'string') {
    return response.answer.length > 0;
  }
  
  return false;
}

/**
 * 合并搜索结果
 * @param {Array} resultsArrays - 结果数组
 * @param {number} maxResults - 最大结果数
 * @returns {Array} 合并后的结果
 */
export function mergeSearchResults(resultsArrays, maxResults = 10) {
  const allResults = [];
  
  // 收集所有结果
  for (const results of resultsArrays) {
    if (Array.isArray(results)) {
      allResults.push(...results);
    }
  }
  
  // 去重（基于URL）
  const seenUrls = new Set();
  const uniqueResults = [];
  
  for (const result of allResults) {
    if (result.url && !seenUrls.has(result.url)) {
      seenUrls.add(result.url);
      uniqueResults.push(result);
    }
  }
  
  // 按相关度排序
  uniqueResults.sort((a, b) => (b.relevance || 0) - (a.relevance || 0));
  
  // 限制数量
  return uniqueResults.slice(0, maxResults);
}

export default {
  validateQuery,
  cleanQuery,
  calculateRelevance,
  formatTimestamp,
  truncateText,
  extractDomain,
  generateSearchUrl,
  delay,
  retry,
  validateApiResponse,
  mergeSearchResults
};