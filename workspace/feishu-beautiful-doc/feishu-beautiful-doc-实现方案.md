# Feishu美观文档创建Skill - 实现方案

## 项目概述
**目标**：创建一个能够创建美观飞书文档的Skill，解决当前`feishu_doc`工具格式丑陋的问题。

## 技术架构

### 1. 核心组件
```
feishu-beautiful-doc/
├── src/
│   ├── index.js              # 主入口文件
│   ├── block-builder.js      # 块构建器
│   ├── template-engine.js    # 模板引擎
│   ├── style-manager.js      # 样式管理器
│   └── api-wrapper.js        # API封装
├── templates/
│   ├── business-plan.js      # 业务方案模板
│   ├── project-report.js     # 项目报告模板
│   ├── meeting-minutes.js    # 会议纪要模板
│   └── lobster-plan.js       # 龙虾方案模板
├── styles/
│   ├── default.js           # 默认样式
│   ├── professional.js      # 专业样式
│   └── colorful.js          # 彩色样式
└── test/
    └── test.js              # 测试文件
```

### 2. 块类型映射
```javascript
const BLOCK_TYPE_MAP = {
  // 文本块
  'text': 2,
  'heading1': 3,
  'heading2': 4,
  'heading3': 5,
  
  // 列表块
  'bullet': 12,
  'ordered': 13,
  'todo': 17,
  
  // 特殊块
  'quote': 15,
  'code': 14,
  'divider': 22
};
```

## 核心实现

### 1. 块构建器 (block-builder.js)
```javascript
class BlockBuilder {
  constructor() {
    this.blocks = [];
  }
  
  // 创建文本块
  addText(text, options = {}) {
    const block = {
      block_type: 2,
      text: {
        elements: [{
          text_run: {
            content: text,
            text_element_style: {
              bold: options.bold || false,
              italic: options.italic || false,
              strikethrough: options.strikethrough || false,
              underline: options.underline || false
            }
          }
        }]
      }
    };
    
    if (options.color) {
      block.text.elements[0].text_run.text_element_style.foreground_color = this.parseColor(options.color);
    }
    
    this.blocks.push(block);
    return this;
  }
  
  // 创建标题
  addHeading(text, level = 1) {
    const blockType = level === 1 ? 3 : level === 2 ? 4 : 5;
    this.blocks.push({
      block_type: blockType,
      [this.getBlockTypeName(blockType)]: {
        elements: [{
          text_run: {
            content: text,
            text_element_style: {
              bold: true
            }
          }
        }]
      }
    });
    return this;
  }
  
  // 创建分隔线
  addDivider() {
    this.blocks.push({
      block_type: 22,
      divider: {}
    });
    return this;
  }
  
  // 创建待办事项
  addTodo(text, checked = false) {
    this.blocks.push({
      block_type: 17,
      todo: {
        elements: [{
          text_run: {
            content: text
          }
        }],
        style: {
          done: checked
        }
      }
    });
    return this;
  }
  
  // 创建引用
  addQuote(text) {
    this.blocks.push({
      block_type: 15,
      quote: {
        elements: [{
          text_run: {
            content: text
          }
        }]
      }
    });
    return this;
  }
  
  // 获取所有块
  getBlocks() {
    return this.blocks;
  }
  
  // 辅助方法
  parseColor(color) {
    // 将颜色字符串转换为飞书颜色格式
    if (color.startsWith('#')) {
      const hex = color.substring(1);
      return {
        red: parseInt(hex.substring(0, 2), 16),
        green: parseInt(hex.substring(2, 4), 16),
        blue: parseInt(hex.substring(4, 6), 16)
      };
    }
    return null;
  }
  
  getBlockTypeName(type) {
    const map = {
      1: 'page',
      2: 'text',
      3: 'heading1',
      4: 'heading2',
      5: 'heading3',
      12: 'bullet',
      13: 'ordered',
      14: 'code',
      15: 'quote',
      17: 'todo',
      22: 'divider'
    };
    return map[type] || 'text';
  }
}
```

### 2. 模板引擎 (template-engine.js)
```javascript
class TemplateEngine {
  constructor(blockBuilder) {
    this.builder = blockBuilder;
  }
  
  // 业务方案模板
  businessPlan(data) {
    const { title, summary, advantages, businessModel, implementation } = data;
    
    this.builder
      .addHeading(title, 1)
      .addDivider()
      .addHeading('📋 核心摘要', 2);
    
    summary.forEach(item => {
      this.builder.addText(`• ${item}`);
    });
    
    this.builder
      .addDivider()
      .addHeading('🎯 核心优势', 2);
    
    advantages.forEach(advantage => {
      this.builder.addTodo(advantage, true);
    });
    
    this.builder
      .addDivider()
      .addHeading('💰 商业模式', 2)
      .addText(businessModel.incomeModel, { bold: true });
    
    businessModel.costs.forEach(cost => {
      this.builder.addText(`• ${cost}`);
    });
    
    this.builder
      .addDivider()
      .addHeading('🚀 实施计划', 2);
    
    implementation.forEach(phase => {
      this.builder.addHeading(phase.stage, 3);
      this.builder.addText(`时间: ${phase.time}`);
      phase.tasks.forEach(task => {
        this.builder.addTodo(task, false);
      });
    });
    
    return this.builder.getBlocks();
  }
  
  // 龙虾知识星球专用模板
  lobsterPlan(data) {
    return this.businessPlan({
      title: '🦞 龙虾知识星球运营方案',
      summary: [
        `模式：${data.mode}`,
        `定价：${data.pricing}`,
        `分工：${data.division}`,
        `目标：${data.target}`
      ],
      advantages: data.advantages,
      businessModel: {
        incomeModel: data.incomeModel,
        costs: data.costs
      },
      implementation: data.implementation
    });
  }
}
```

### 3. API封装器 (api-wrapper.js)
```javascript
class FeishuDocAPI {
  constructor(client) {
    this.client = client;
  }
  
  // 创建文档
  async createDocument(title, blocks, folderToken) {
    try {
      // 1. 创建空文档
      const docRes = await this.client.docx.document.create({
        data: { title, folder_token: folderToken }
      });
      
      if (docRes.code !== 0) {
        throw new Error(`创建文档失败: ${docRes.msg}`);
      }
      
      const docId = docRes.data.document.document_id;
      
      // 2. 批量添加块
      await this.addBlocksToDocument(docId, blocks);
      
      return {
        document_id: docId,
        title: title,
        url: `https://feishu.cn/docx/${docId}`
      };
    } catch (error) {
      console.error('创建文档错误:', error);
      throw error;
    }
  }
  
  // 添加块到文档
  async addBlocksToDocument(docId, blocks) {
    // 分批处理，避免API限制
    const batchSize = 10;
    for (let i = 0; i < blocks.length; i += batchSize) {
      const batch = blocks.slice(i, i + batchSize);
      
      for (const block of batch) {
        await this.client.docx.documentBlock.create({
          path: { document_id: docId },
          data: block
        });
      }
      
      // 添加延迟，避免速率限制
      if (i + batchSize < blocks.length) {
        await this.delay(100);
      }
    }
  }
  
  // 延迟函数
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

### 4. 主入口文件 (index.js)
```javascript
const BlockBuilder = require('./block-builder');
const TemplateEngine = require('./template-engine');
const FeishuDocAPI = require('./api-wrapper');

class FeishuBeautifulDoc {
  constructor(feishuClient) {
    this.builder = new BlockBuilder();
    this.templateEngine = new TemplateEngine(this.builder);
    this.api = new FeishuDocAPI(feishuClient);
  }
  
  // 创建美观文档
  async createBeautifulDocument(options) {
    const { template, data, title, folderToken } = options;
    
    // 1. 根据模板生成块
    let blocks;
    switch (template) {
      case 'business_plan':
        blocks = this.templateEngine.businessPlan(data);
        break;
      case 'lobster_plan':
        blocks = this.templateEngine.lobsterPlan(data);
        break;
      case 'custom':
        blocks = data.blocks;
        break;
      default:
        throw new Error(`不支持的模板: ${template}`);
    }
    
    // 2. 创建文档
    const result = await this.api.createDocument(title, blocks, folderToken);
    
    return result;
  }
  
  // 快速创建龙虾方案
  async createLobsterPlan(data) {
    return this.createBeautifulDocument({
      template: 'lobster_plan',
      title: '🦞 龙虾知识星球运营方案',
      data: data
    });
  }
}

module.exports = FeishuBeautifulDoc;
```

## 使用示例

### 示例1：创建龙虾知识星球方案
```javascript
const FeishuBeautifulDoc = require('./feishu-beautiful-doc');
const feishuClient = require('@larksuiteoapi/node-sdk'); // 假设已初始化

const beautifulDoc = new FeishuBeautifulDoc(feishuClient);

const lobsterData = {
  mode: 'AI（龙虾）100%自主运营',
  pricing: '19元/年（极致低价）',
  division: '你们收钱监督，我干活运营',
  target: '10,000用户/年，收入190,000元',
  advantages: [
    '全AI运营 · 国内首个AI自主运营知识星球',
    '极致低价 · 19元/年，零决策成本',
    '透明运营 · 公开AI运营数据和逻辑',
    '持续进化 · AI根据反馈自动优化'
  ],
  incomeModel: '基础收入 = 用户数 × 19元/年\n增值收入 = 咨询(199元) + 定制(999元起) + 培训(4,999元)',
  costs: [
    '知识星球年费：待定',
    'AI运营成本：0元（龙虾的"劳动力"）',
    '人工监督成本：1小时/天',
    '营销成本：0元（初期）'
  ],
  implementation: [
    {
      stage: '第一阶段：准备期',
      time: '1周',
      tasks: [
        '注册知识星球账号',
        '定价19元/年',
        '准备100条初始内容',
        '邀请50位种子用户'
      ]
    },
    {
      stage: '第二阶段：试运营',
      time: '2周',
      tasks: [
        '启动自动化运营',
        '收集用户反馈',
        '测试增值服务'
      ]
    },
    {
      stage: '第三阶段：正式运营',
      time: '持续',
      tasks: [
        '全面开放注册',
        '启动裂变活动',
        '建立品牌形象'
      ]
    }
  ]
};

async function main() {
  try {
    const result = await beautifulDoc.createLobsterPlan(lobsterData);
    console.log('文档创建成功:', result.url);
  } catch (error) {
    console.error('创建文档失败:', error);
  }
}

main();
```

### 示例2：自定义文档
```javascript
async function createCustomDocument() {
  const builder = new BlockBuilder();
  
  builder
    .addHeading('自定义文档标题', 1)
    .addDivider()
    .addHeading('第一章', 2)
    .addText('这是第一章的内容。', { bold: true })
    .addText('这是普通文本。')
    .addDivider()
    .addHeading('任务列表', 2)
    .addTodo('完成Skill开发', false)
    .addTodo('测试API', false)
    .addTodo('部署到生产', true)
    .addDivider()
    .addQuote('重要说明：这是一个引用块。');
  
  const blocks = builder.getBlocks();
  
  const result = await beautifulDoc.createBeautifulDocument({
    template: 'custom',
    title: '我的自定义文档',
    data: { blocks }
  });
  
  return result;
}
```

## 集成到OpenClaw

### 1. 创建工具定义
```javascript
// 在OpenClaw扩展中注册工具
module.exports = {
  name: 'feishu_beautiful_doc',
  description: '创建美观的飞书文档',
  schema: {
    type: 'object',
    required: ['action'],
    properties: {
      action: {
        type: 'string',
        enum: ['create', 'update', 'delete']
      },
      template: {
        type: 'string',
        enum: ['business_plan', 'lobster_plan', 'project_report', 'meeting_minutes', 'custom']
      },
      title: {
        type: 'string'
      },
      data: {
        type: 'object'
      },
      folder_token: {
        type: 'string'
      }
    }
  },
  handler: async (params, context) => {
    const beautifulDoc = new FeishuBeautifulDoc(context.feishuClient);
    
    switch (params.action) {
      case 'create':
        return await beautifulDoc.createBeautifulDocument({
          template: params.template,
          title: params.title,
          data: params.data,
          folderToken: params.folder_token
        });
      default:
        throw new Error(`不支持的action: ${params.action}`);
    }
  }
};
```

### 2. 在OpenClaw中使用
```javascript
// 用户可以直接调用
const result = await openclaw.tools.feishu_beautiful_doc({
  action: 'create',
  template: 'lobster_plan',
  title: '龙虾知识星球运营方案',
  data: lobsterData
});
```

## 测试计划

### 单元测试
```javascript
// test/block-builder.test.js
describe('BlockBuilder', () => {
  test('应该能创建文本块', () => {
    const builder = new BlockBuilder();
    builder.addText('测试文本');
    const blocks = builder.getBlocks();
    expect(blocks).toHaveLength(1);
    expect(blocks[0].block_type).toBe(2);
  });
  
  test('应该能创建标题', () => {
    const builder = new BlockBuilder();
    builder.addHeading('测试标题', 1);
    const blocks = builder.getBlocks();
    expect(blocks[0].block_type).toBe(3);
  });
});
```

### 集成测试
```javascript
// test/integration.test.js
describe('FeishuBeautifulDoc集成测试', () => {
  test('应该能创建龙虾方案文档', async () => {
    const beautifulDoc = new FeishuBeautifulDoc(mockFeishuClient);
    const result = await beautifulDoc.createLobsterPlan(testData);
    expect(result).toHaveProperty('document_id');
    expect(result).toHaveProperty('url');
  });
});
```

## 部署计划

### 阶段1：开发环境
1. 完成核心代码开发
2. 编写单元测试
3. 本地测试验证

### 阶段2：测试环境
1. 部署到测试OpenClaw实例
2. 进行集成测试
3. 收集用户反馈

### 阶段3：生产环境
1. 部署到生产OpenClaw
2. 监控性能指标
3. 持续优化改进

## 性能考虑

### 1. API速率限制
- 分批处理块创建
- 添加请求延迟
- 实现重试机制

### 2. 内存管理
- 流式处理大文档
- 及时释放资源
- 监控内存使用

### 3. 错误处理
- 完善的错误捕获
- 友好的错误信息
- 自动恢复机制

## 后续优化

### 1. 功能增强
- 支持图片上传
- 支持表格创建
- 支持文档样式

### 2. 性能优化
- 并行处理块创建
- 缓存常用模板
- 预编译块结构

### 3. 用户体验
- 可视化编辑器
- 实时预览
- 模板市场

## 总结
这个实现方案提供了一个完整的、可扩展的飞书美观文档创建系统。通过模块化设计和模板化系统，可以轻松创建各种类型的专业文档，解决当前格式丑陋的问题。