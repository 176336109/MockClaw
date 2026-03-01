/**
 * Feishu美观文档MVP工具
 * 使用现有feishu_doc工具创建更好看的文档
 */

const FeishuBlockBuilder = require('./FeishuBlockBuilder.js');

class FeishuBeautifulMVP {
  /**
   * 创建美观文档
   * @param {string} title - 文档标题
   * @param {Array} blocks - 块数组
   * @returns {Promise<object>} 创建结果
   */
  static async createBeautifulDocument(title, blocks) {
    try {
      // 1. 创建文档
      const createResult = await this.callFeishuDoc('create', { title });
      
      if (!createResult.document_id) {
        throw new Error('创建文档失败: ' + JSON.stringify(createResult));
      }
      
      const docId = createResult.document_id;
      console.log(`文档创建成功: ${docId}`);
      
      // 2. 更新文档内容（这里简化，实际需要逐个添加块）
      // 由于feishu_doc工具限制，我们先用简单方式
      const content = this.blocksToMarkdown(blocks);
      const updateResult = await this.callFeishuDoc('write', {
        doc_token: docId,
        content: content
      });
      
      return {
        success: true,
        document_id: docId,
        title: title,
        url: `https://feishu.cn/docx/${docId}`,
        blocks_count: blocks.length
      };
      
    } catch (error) {
      console.error('创建文档失败:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  /**
   * 将块转换为Markdown（简化版）
   * @param {Array} blocks - 块数组
   * @returns {string} Markdown内容
   */
  static blocksToMarkdown(blocks) {
    let markdown = '';
    
    for (const block of blocks) {
      switch (block.block_type) {
        case 3: // H1
          markdown += `# ${this.getBlockContent(block)}\n\n`;
          break;
        case 4: // H2
          markdown += `## ${this.getBlockContent(block)}\n\n`;
          break;
        case 5: // H3
          markdown += `### ${this.getBlockContent(block)}\n\n`;
          break;
        case 2: // 文本
          markdown += `${this.getBlockContent(block)}\n`;
          break;
        case 22: // 分隔线
          markdown += '---\n\n';
          break;
        default:
          markdown += `${this.getBlockContent(block)}\n`;
      }
    }
    
    return markdown;
  }
  
  /**
   * 获取块内容
   * @param {object} block - 块对象
   * @returns {string} 内容文本
   */
  static getBlockContent(block) {
    if (block.text && block.text.elements && block.text.elements[0]) {
      return block.text.elements[0].text_run.content;
    }
    if (block.heading1 && block.heading1.elements && block.heading1.elements[0]) {
      return block.heading1.elements[0].text_run.content;
    }
    if (block.heading2 && block.heading2.elements && block.heading2.elements[0]) {
      return block.heading2.elements[0].text_run.content;
    }
    if (block.heading3 && block.heading3.elements && block.heading3.elements[0]) {
      return block.heading3.elements[0].text_run.content;
    }
    return '';
  }
  
  /**
   * 调用feishu_doc工具
   * @param {string} action - 操作类型
   * @param {object} params - 参数
   * @returns {Promise<object>} 结果
   */
  static async callFeishuDoc(action, params) {
    // 这里需要集成到OpenClaw的工具调用系统
    // 暂时返回模拟结果
    return new Promise((resolve) => {
      setTimeout(() => {
        if (action === 'create') {
          resolve({
            document_id: 'test_' + Date.now(),
            title: params.title,
            url: 'https://feishu.cn/docx/test'
          });
        } else if (action === 'write') {
          resolve({
            success: true,
            revision_id: 1
          });
        }
      }, 100);
    });
  }
  
  /**
   * 创建龙虾知识星球文档
   * @returns {Promise<object>} 创建结果
   */
  static async createLobsterPlanDocument() {
    const blocks = FeishuBlockBuilder.createLobsterPlan();
    return await this.createBeautifulDocument('🦞 龙虾知识星球运营方案', blocks);
  }
}

// 测试
if (require.main === module) {
  console.log('=== Feishu美观文档MVP测试 ===\n');
  
  // 测试块构建器
  console.log('1. 测试块构建器:');
  const builder = new FeishuBlockBuilder();
  builder
    .addHeading('MVP测试文档', 1)
    .addText('这是一个MVP测试')
    .addDivider()
    .addHeading('功能列表', 2)
    .addText('• 功能1', { bold: true })
    .addText('• 功能2');
  
  const blocks = builder.getBlocks();
  console.log(`生成 ${blocks.length} 个块`);
  
  // 测试Markdown转换
  console.log('\n2. 测试Markdown转换:');
  const markdown = FeishuBeautifulMVP.blocksToMarkdown(blocks);
  console.log(markdown);
  
  // 测试文档创建
  console.log('3. 测试文档创建:');
  FeishuBeautifulMVP.createLobsterPlanDocument()
    .then(result => {
      console.log('创建结果:', result);
    })
    .catch(error => {
      console.error('创建失败:', error);
    });
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FeishuBeautifulMVP;
}