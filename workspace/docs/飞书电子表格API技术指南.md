# 飞书电子表格API技术指南

## 1. 认证与访问令牌

### 1.1 认证流程
飞书API使用OAuth 2.0认证，OpenClaw已内置完整的认证机制。

#### 1.1.1 访问令牌类型
1. **租户访问令牌 (Tenant Access Token)**
   - 用于企业级应用
   - 有效期：2小时
   - 自动刷新机制

2. **用户访问令牌 (User Access Token)**
   - 用于用户级操作
   - 需要用户授权

#### 1.1.2 当前认证状态
```javascript
// OpenClaw已处理认证，无需手动获取token
// 所有feishu_*工具会自动携带有效token
```

### 1.2 权限验证
使用 `feishu_app_scopes` 工具检查权限：
```javascript
const scopes = await feishu_app_scopes();
console.log('当前权限:', scopes.granted);
```

## 2. 电子表格API详解

### 2.1 创建电子表格

#### API端点
```
POST /open-apis/sheets/v3/spreadsheets
```

#### 请求参数
```json
{
  "title": "表格标题",
  "folder_token": "可选文件夹token"
}
```

#### 响应示例
```json
{
  "spreadsheet": {
    "spreadsheet_token": "shtxxxxxxxxxxxx",
    "title": "表格标题",
    "owner_id": "ou_xxxxxxxxxxxx",
    "url": "https://example.feishu.cn/sheets/shtxxxxxxxxxxxx"
  }
}
```

#### OpenClaw工具调用
```javascript
// 方案一：扩展feishu_doc工具
const result = await feishu_doc({
  action: 'create_sheet',
  title: '任务管理系统',
  folder_token: 'fldxxxxxxxxxxxx'
});

// 方案二：独立feishu_sheet工具
const result = await feishu_sheet({
  action: 'create',
  title: '任务管理系统',
  folder: 'fldxxxxxxxxxxxx'
});
```

### 2.2 读取单元格数据

#### API端点
```
GET /open-apis/sheets/v3/spreadsheets/{spreadsheetToken}/values/{range}
```

#### 范围格式
- `Sheet1!A1` - 单个单元格
- `Sheet1!A1:C10` - 单元格区域
- `Sheet1!A:A` - 整列
- `Sheet1!1:1` - 整行

#### OpenClaw工具调用
```javascript
const data = await feishu_doc({
  action: 'read_sheet',
  spreadsheet_token: 'shtxxxxxxxxxxxx',
  range: 'Sheet1!A1:D10'
});

console.log('读取的数据:', data.values);
```

### 2.3 写入单元格数据

#### API端点
```
PUT /open-apis/sheets/v3/spreadsheets/{spreadsheetToken}/values/{range}
```

#### 请求体
```json
{
  "valueRange": {
    "range": "Sheet1!A1",
    "values": [
      ["标题1", "标题2", "标题3"],
      ["数据1", "数据2", "数据3"]
    ]
  }
}
```

#### OpenClaw工具调用
```javascript
const result = await feishu_doc({
  action: 'write_sheet',
  spreadsheet_token: 'shtxxxxxxxxxxxx',
  range: 'Sheet1!A1',
  values: [
    ["任务ID", "任务名称", "状态"],
    ["T001", "API开发", "进行中"]
  ]
});

console.log('更新单元格数:', result.updated_cells);
```

### 2.4 批量操作

#### 批量读取
```javascript
const batchData = await feishu_doc({
  action: 'batch_read_sheet',
  spreadsheet_token: 'shtxxxxxxxxxxxx',
  ranges: ['Sheet1!A1:D10', 'Sheet2!A1:B5']
});
```

#### 批量写入
```javascript
const batchResult = await feishu_doc({
  action: 'batch_write_sheet',
  spreadsheet_token: 'shtxxxxxxxxxxxx',
  updates: [
    {
      range: 'Sheet1!A1',
      values: [["标题1", "标题2"]]
    },
    {
      range: 'Sheet1!A3',
      values: [["数据1", "数据2"]]
    }
  ]
});
```

## 3. 多维表格API详解

### 3.1 创建多维表格应用

#### API端点
```
POST /open-apis/bitable/v1/apps
```

#### 请求参数
```json
{
  "name": "应用名称",
  "folder_token": "可选文件夹token"
}
```

#### OpenClaw工具调用
```javascript
const app = await feishu_doc({
  action: 'create_bitable',
  name: '项目任务管理',
  folder_token: 'fldxxxxxxxxxxxx'
});

console.log('应用Token:', app.app_token);
```

### 3.2 记录CRUD操作

#### 3.2.1 创建记录
```javascript
const record = await feishu_doc({
  action: 'bitable_record',
  app_token: 'bascxxxxxxxxxxxx',
  table_id: 'tblxxxxxxxxxxxx',
  operation: 'create',
  record_data: {
    fields: {
      "任务名称": "API集成测试",
      "优先级": "高",
      "状态": "进行中",
      "负责人": "张三",
      "截止日期": "2026-03-01"
    }
  }
});
```

#### 3.2.2 读取记录
```javascript
const records = await feishu_doc({
  action: 'bitable_record',
  app_token: 'bascxxxxxxxxxxxx',
  table_id: 'tblxxxxxxxxxxxx',
  operation: 'read',
  filter: 'CurrentValue.[状态] = "进行中"',
  sort: ['-创建时间'],
  page_size: 50
});
```

#### 3.2.3 更新记录
```javascript
const updated = await feishu_doc({
  action: 'bitable_record',
  app_token: 'bascxxxxxxxxxxxx',
  table_id: 'tblxxxxxxxxxxxx',
  operation: 'update',
  record_id: 'recxxxxxxxxxxxx',
  record_data: {
    fields: {
      "状态": "已完成",
      "完成时间": "2026-02-28 15:30:00"
    }
  }
});
```

#### 3.2.4 删除记录
```javascript
const deleted = await feishu_doc({
  action: 'bitable_record',
  app_token: 'bascxxxxxxxxxxxx',
  table_id: 'tblxxxxxxxxxxxx',
  operation: 'delete',
  record_id: 'recxxxxxxxxxxxx'
});
```

## 4. 任务管理系统实现

### 4.1 数据结构设计

#### 4.1.1 电子表格版本
```javascript
// 工作表结构
const sheetStructure = {
  columns: [
    { name: '任务ID', width: 80 },
    { name: '任务名称', width: 200 },
    { name: '描述', width: 300 },
    { name: '优先级', width: 80 },
    { name: '状态', width: 100 },
    { name: '负责人', width: 100 },
    { name: '创建时间', width: 120 },
    { name: '截止时间', width: 120 },
    { name: '完成时间', width: 120 },
    { name: '备注', width: 200 }
  ],
  data: [
    ['T001', 'API集成开发', '完成飞书API集成', '高', '进行中', '张三', '2026-02-28', '2026-03-01', '', ''],
    ['T002', '文档编写', '编写技术文档', '中', '待开始', '李四', '2026-02-28', '2026-03-05', '', '']
  ]
};
```

#### 4.1.2 多维表格版本
```javascript
// 表格字段定义
const tableFields = {
  fields: [
    { field_name: '任务名称', type: 'text' },
    { field_name: '描述', type: 'textarea' },
    { 
      field_name: '优先级', 
      type: 'singleSelect',
      property: {
        options: [
          { name: '高', color: 'red' },
          { name: '中', color: 'orange' },
          { name: '低', color: 'green' }
        ]
      }
    },
    {
      field_name: '状态',
      type: 'singleSelect',
      property: {
        options: [
          { name: '待开始', color: 'gray' },
          { name: '进行中', color: 'blue' },
          { name: '已完成', color: 'green' },
          { name: '已取消', color: 'red' }
        ]
      }
    },
    { field_name: '负责人', type: 'person' },
    { field_name: '创建时间', type: 'date' },
    { field_name: '截止时间', type: 'date' },
    { field_name: '完成时间', type: 'date' },
    { field_name: '标签', type: 'multiSelect' },
    { field_name: '附件', type: 'attachment' }
  ]
};
```

### 4.2 核心功能实现

#### 4.2.1 任务管理类
```javascript
class TaskManager {
  constructor(spreadsheetToken) {
    this.spreadsheetToken = spreadsheetToken;
  }
  
  // 创建任务
  async createTask(taskData) {
    return await feishu_doc({
      action: 'write_sheet',
      spreadsheet_token: this.spreadsheetToken,
      range: this.getNextRowRange(),
      values: [[
        this.generateTaskId(),
        taskData.name,
        taskData.description || '',
        taskData.priority || '中',
        taskData.status || '待开始',
        taskData.assignee || '',
        new Date().toISOString().slice(0, 10),
        taskData.deadline || '',
        '',
        taskData.notes || ''
      ]]
    });
  }
  
  // 更新任务状态
  async updateTaskStatus(taskId, status, progress) {
    // 先找到任务所在行
    const tasks = await this.getAllTasks();
    const taskIndex = tasks.findIndex(t => t[0] === taskId);
    
    if (taskIndex === -1) {
      throw new Error(`任务 ${taskId} 不存在`);
    }
    
    const row = taskIndex + 2; // +1 for header, +1 for 1-indexed
    
    return await feishu_doc({
      action: 'write_sheet',
      spreadsheet_token: this.spreadsheetToken,
      range: `Sheet1!E${row}`,
      values: [[status]]
    });
  }
  
  // 获取所有任务
  async getAllTasks() {
    const data = await feishu_doc({
      action: 'read_sheet',
      spreadsheet_token: this.spreadsheetToken,
      range: 'Sheet1!A2:J1000'
    });
    
    return data.values || [];
  }
  
  // 按状态筛选任务
  async getTasksByStatus(status) {
    const tasks = await this.getAllTasks();
    return tasks.filter(task => task[4] === status);
  }
  
  // 生成任务ID
  generateTaskId() {
    const timestamp = Date.now().toString().slice(-6);
    const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    return `T${timestamp}${random}`;
  }
  
  // 获取下一行范围
  getNextRowRange() {
    // 实际实现中需要先获取当前行数
    return 'Sheet1!A100'; // 简化示例
  }
}
```

#### 4.2.2 统计报表生成
```javascript
class TaskStatistics {
  constructor(taskManager) {
    this.taskManager = taskManager;
  }
  
  // 生成状态统计
  async generateStatusStats() {
    const tasks = await this.taskManager.getAllTasks();
    
    const stats = {
      total: tasks.length,
      byStatus: {},
      byPriority: {},
      byAssignee: {}
    };
    
    tasks.forEach(task => {
      const status = task[4] || '未知';
      const priority = task[3] || '未知';
      const assignee = task[5] || '未分配';
      
      stats.byStatus[status] = (stats.byStatus[status] || 0) + 1;
      stats.byPriority[priority] = (stats.byPriority[priority] || 0) + 1;
      stats.byAssignee[assignee] = (stats.byAssignee[assignee] || 0) + 1;
    });
    
    return stats;
  }
  
  // 生成完成率统计
  async generateCompletionRate() {
    const tasks = await this.taskManager.getAllTasks();
    const completed = tasks.filter(task => task[4] === '已完成').length;
    
    return {
      total: tasks.length,
      completed: completed,
      completionRate: tasks.length > 0 ? (completed / tasks.length * 100).toFixed(1) : 0
    };
  }
  
  // 生成时间线统计
  async generateTimelineStats(startDate, endDate) {
    const tasks = await this.taskManager.getAllTasks();
    
    const timeline = {};
    tasks.forEach(task => {
      const createDate = task[6];
      if (createDate && createDate >= startDate && createDate <= endDate) {
        timeline[createDate] = (timeline[createDate] || 0) + 1;
      }
    });
    
    return timeline;
  }
}
```

### 4.3 使用示例

```javascript
// 初始化任务管理器
const taskManager = new TaskManager('shtxxxxxxxxxxxx');

// 创建新任务
await taskManager.createTask({
  name: 'API测试任务',
  description: '测试飞书电子表格API',
  priority: '高',
  assignee: '张三',
  deadline: '2026-03-01'
});

// 更新任务状态
await taskManager.updateTaskStatus('T001', '进行中');

// 获取进行中的任务
const inProgressTasks = await taskManager.getTasksByStatus('进行中');
console.log('进行中的任务:', inProgressTasks.length);

// 生成统计报表
const stats = new TaskStatistics(taskManager);
const statusStats = await stats.generateStatusStats();
const completionRate = await stats.generateCompletionRate();

console.log('任务统计:');
console.log('- 总数:', statusStats.total);
console.log('- 状态分布:', statusStats.byStatus);
console.log('- 完成率:', completionRate.completionRate + '%');
```

## 5. OpenClaw集成方案

### 5.1 工具扩展实现

#### 5.1.1 feishu_doc工具扩展
```javascript
// 在现有的feishu_doc工具中添加电子表格功能
module.exports = {
  name: 'feishu_doc',
  description: '飞书文档和电子表格操作工具',
  
  async execute(params) {
    switch (params.action) {
      case 'create_sheet':
        return await this.createSpreadsheet(params);
        
      case 'read_sheet':
        return await this.readSpreadsheet(params);
        
      case 'write_sheet':
        return await this.writeSpreadsheet(params);
        
      case 'create_bitable':
        return await this.createBitableApp(params);
        
      case 'bitable_record':
        return await this.bitableRecordOperation(params);
        
      default:
        // 原有的文档操作
        return await originalFeishuDoc(params);
    }
  },
  
  async createSpreadsheet(params) {
    const { title, folder_token } = params;
    
    const response = await this.callFeishuApi({
      method: 'POST',
      endpoint: '/sheets/v3/spreadsheets',
      data: { title, folder_token }
    });
    
    return response.data;
  },
  
  async readSpreadsheet(params) {
    const { spreadsheet_token, range } = params;
    
    const response = await this.callFeishuApi({
      method: 'GET',
      endpoint: `/sheets/v3/spreadsheets/${spreadsheet_token}/values/${range}`
    });
    
    return response.data;
  },
  
  async writeSpreadsheet(params) {
    const { spreadsheet_token, range, values } = params;
    
    const response = await this.callFeishuApi({
      method: 'PUT',
      endpoint: `/sheets/v3/spreadsheets/${spreadsheet_token}/values/${range}`,
      data: {
        valueRange: { range, values }
      }
    });
    
    return response.data;
  },
  
  async createBitableApp(params) {
    const { name, folder_token } = params;
    
    const response = await this.callFeishuApi({
      method: 'POST',
      endpoint: '/bitable/v1/apps',
      data: { name, folder_token }
    });
    
    return response.data;
  },
  
  async bitableRecordOperation(params) {
    const { app_token, table_id, operation, record_data, record_id } = params;
    
    let endpoint, method;
    
    switch (operation) {
      case 'create':
        endpoint = `/bitable/v1/apps/${app_token}/tables/${table_id}/records`;
        method = 'POST';
        break;
        
      case 'read':
        endpoint = `/bitable/v1/apps/${app_token}/tables/${table_id}/records`;
        method = 'GET';
        break;
        
      case 'update':
        endpoint = `/bitable/v1/apps/${app_token}/tables/${table_id}/records/${record_id}`;
        method = 'PUT';
        break;
        
      case 'delete':
        endpoint = `/bitable/v1/apps/${app_token}/tables/${table_id}/records/${record_id}`;
        method = 'DELETE';
        break;
    }
    
    const response = await this.callFeishuApi({
      method,
      endpoint,
      data: operation ===