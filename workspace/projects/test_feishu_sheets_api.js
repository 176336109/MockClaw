// 测试飞书Sheets API调用
// 基于feishu_doc的成功模式

const { execSync } = require('child_process');
const fs = require('fs');

console.log('=== 测试飞书Sheets API ===\n');

// 方法1：尝试直接使用feishu_doc的内部机制
console.log('1. 测试现有feishu_doc工具...');
try {
  // 先创建一个测试文档，验证工具能工作
  const createResult = execSync('openclaw gateway invoke feishu_doc --json \'{"action":"create","title":"测试文档"}\' 2>&1', { encoding: 'utf8' });
  console.log('文档创建结果:', createResult.substring(0, 200));
  
  if (createResult.includes('document_id')) {
    console.log('✅ feishu_doc工具工作正常，认证有效\n');
    
    // 提取文档token
    const match = createResult.match(/"document_id":"([^"]+)"/);
    if (match) {
      const docToken = match[1];
      console.log(`文档Token: ${docToken}`);
      
      // 尝试读取文档
      const readResult = execSync(`openclaw gateway invoke feishu_doc --json '{"action":"read","doc_token":"${docToken}"}' 2>&1`, { encoding: 'utf8' });
      console.log('文档读取成功\n');
    }
  }
} catch (error) {
  console.log('❌ feishu_doc调用失败:', error.message.substring(0, 100));
}

// 方法2：检查可用的工具
console.log('\n2. 检查可用的飞书工具...');
try {
  const toolsResult = execSync('openclaw gateway invoke --list 2>&1 | grep -i feishu', { encoding: 'utf8' });
  console.log('可用的飞书工具:');
  console.log(toolsResult);
} catch (error) {
  console.log('无法列出工具:', error.message);
}

// 方法3：建议的下一步
console.log('\n3. 建议的下一步行动:');
console.log('基于feishu_doc的成功模式，我们可以:');
console.log('a) 扩展现有feishu插件，添加sheets.ts');
console.log('b) 复用现有的createFeishuClient认证机制');
console.log('c) 调用Sheets v3 API创建电子表格');
console.log('\n需要:');
console.log('1. 修改/opt/homebrew/lib/node_modules/openclaw/extensions/feishu/index.ts');
console.log('2. 添加registerFeishuSheetsTools(api)调用');
console.log('3. 创建src/sheets.ts实现Sheets API');
console.log('4. 重启OpenClaw服务');

// 方法4：检查权限
console.log('\n4. 检查文件权限...');
const feishuDir = '/opt/homebrew/lib/node_modules/openclaw/extensions/feishu';
try {
  const stat = fs.statSync(feishuDir);
  console.log(`飞书插件目录: ${feishuDir}`);
  console.log(`权限: ${stat.mode.toString(8)}`);
  console.log(`可写: ${fs.accessSync(feishuDir, fs.constants.W_OK) ? '是' : '否'}`);
} catch (error) {
  console.log(`无法访问 ${feishuDir}: ${error.message}`);
}

console.log('\n=== 测试完成 ===');