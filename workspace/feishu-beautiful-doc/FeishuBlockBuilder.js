/**
 * Feishu文档块构建器 - MVP版本
 * 目标：创建比当前feishu_doc更好看的文档
 */

class FeishuBlockBuilder {
  constructor() {
    this.blocks = [];
  }

  /**
   * 添加文本块
   * @param {string} text - 文本内容
   * @param {object} options - 样式选项
   * @returns {FeishuBlockBuilder}
   */
  addText(text, options = {}) {
    const block = {
      block_type: 2, // 文本块
      text: {
        elements: [{
          text_run: {
            content: text,
            text_element_style: {
              bold: options.bold || false,
              italic: options.italic || false
            }
          }
        }]
      }
    };
    this.blocks.push(block);
    return this;
  }

  /**
   * 添加标题
   * @param {string} text - 标题文本
   * @param {number} level - 标题级别 (1, 2, 3)
   * @returns {FeishuBlockBuilder}
   */
  addHeading(text, level = 1) {
    const blockType = level === 1 ? 3 : level === 2 ? 4 : 5;
    const block = {
      block_type: blockType,
      heading1: level === 1 ? { elements: [{ text_run: { content: text } }] } : undefined,
      heading2: level === 2 ? { elements: [{ text_run: { content: text } }] } : undefined,
      heading3: level === 3 ? { elements: [{ text_run: { content: text } }] } : undefined
    };
    this.blocks.push(block);
    return this;
  }

  /**
   * 添加分隔线
   * @returns {FeishuBlockBuilder}
   */
  addDivider() {
    this.blocks.push({
      block_type: 22, // 分隔线
      divider: {}
    });
    return this;
  }

  /**
   * 获取所有块
   * @returns {Array} 块数组
   */
  getBlocks() {
    return this.blocks;
  }

  /**
   * 清空所有块
   * @returns {FeishuBlockBuilder}
   */
  clear() {
    this.blocks = [];
    return this;
  }

  /**
   * 生成龙虾知识星球方案的块
   * @returns {Array} 方案块
   */
  static createLobsterPlan() {
    const builder = new FeishuBlockBuilder();
    
    builder
      .addHeading('🦞 龙虾知识星球运营方案', 1)
      .addDivider()
      .addHeading('📋 核心摘要', 2)
      .addText('• 模式：AI（龙虾）100%自主运营')
      .addText('• 定价：19元/年（极致低价）')
      .addText('• 分工：你们收钱监督，我干活运营')
      .addText('• 目标：10,000用户/年，收入190,000元')
      .addDivider()
      .addHeading('🎯 核心优势', 2)
      .addText('✓ 全AI运营 · 国内首个AI自主运营知识星球', { bold: true })
      .addText('✓ 极致低价 · 19元/年，零决策成本', { bold: true })
      .addText('✓ 透明运营 · 公开AI运营数据和逻辑', { bold: true })
      .addText('✓ 持续进化 · AI根据反馈自动优化', { bold: true });
    
    return builder.getBlocks();
  }
}

// 导出供测试使用
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FeishuBlockBuilder;
}

// 测试代码
if (typeof window !== 'undefined' || (typeof process !== 'undefined' && process.argv[1] === __filename)) {
  console.log('=== FeishuBlockBuilder MVP 测试 ===');
  
  // 测试1：基础功能
  const builder = new FeishuBlockBuilder();
  builder
    .addHeading('测试标题', 1)
    .addText('普通文本')
    .addText('加粗文本', { bold: true })
    .addDivider()
    .addHeading('二级标题', 2);
  
  console.log('生成的块数量:', builder.getBlocks().length);
  console.log('块类型:', builder.getBlocks().map(b => b.block_type));
  
  // 测试2：龙虾方案
  const lobsterBlocks = FeishuBlockBuilder.createLobsterPlan();
  console.log('\n龙虾方案块数量:', lobsterBlocks.length);
  console.log('示例块结构:', JSON.stringify(lobsterBlocks[0], null, 2));
}