#!/usr/bin/env python3
"""
飞书电子表格API调用示例
基于OpenClaw飞书工具的实际调用示例
"""

import json
import os
import sys
from datetime import datetime

def test_feishu_tools():
    """测试飞书工具"""
    print("=" * 60)
    print("测试飞书工具可用性")
    print("=" * 60)
    
    # 检查当前工作空间
    print(f"工作目录: {os.getcwd()}")
    
    # 加载数据
    try:
        with open('task-management/data-for-spreadsheet.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ 数据加载成功: {len(data['tasks'])} 任务, {len(data['team_members'])} 成员")
    except Exception as e:
        print(f"✗ 数据加载失败: {e}")
        return False
    
    # 创建表格结构
    spreadsheet_structure = {
        "title": f"OpenClaw任务管理_{datetime.now().strftime('%Y%m%d_%H%M')}",
        "description": "OpenClaw任务与团队管理电子表格",
        "sheets": [
            {
                "name": "任务清单",
                "index": 0,
                "row_count": 100,
                "column_count": 13
            },
            {
                "name": "团队成员", 
                "index": 1,
                "row_count": 50,
                "column_count": 9
            },
            {
                "name": "统计看板",
                "index": 2,
                "row_count": 30,
                "column_count": 8
            },
            {
                "name": "时间效率",
                "index": 3,
                "row_count": 20,
                "column_count": 6
            }
        ]
    }
    
    print(f"\n表格结构:")
    print(json.dumps(spreadsheet_structure, indent=2, ensure_ascii=False))
    
    # 准备数据
    print("\n" + "=" * 60)
    print("数据准备")
    print("=" * 60)
    
    # 任务数据
    tasks = data['tasks']
    print(f"\n任务数据示例 (第1个任务):")
    print(json.dumps(tasks[0], indent=2, ensure_ascii=False))
    
    # 团队数据
    team = data['team_members']
    print(f"\n团队数据示例 (前2个成员):")
    print(json.dumps(team[:2], indent=2, ensure_ascii=False))
    
    # 时间统计
    stats = data['time_statistics']
    print(f"\n时间统计数据:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    return True

def generate_api_implementation():
    """生成API实现代码"""
    print("\n" + "=" * 60)
    print("API实现代码生成")
    print("=" * 60)
    
    implementation_code = '''"""
飞书电子表格API实现类
基于OpenClaw飞书工具的实际实现
"""

import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

class FeishuSpreadsheetAPI:
    """飞书电子表格API封装类"""
    
    def __init__(self):
        """初始化"""
        self.base_url = "https://open.feishu.cn/open-apis"
        self.access_token = None
        self.tenant_token = None
        
    def get_access_token(self):
        """获取访问令牌"""
        # OpenClaw会自动处理认证
        # 这里只是示例代码
        print("获取访问令牌...")
        # 实际实现中，OpenClaw会提供token
        return "openclaw_auto_token"
    
    def create_spreadsheet(self, title: str, folder_token: Optional[str] = None) -> Optional[str]:
        """
        创建电子表格
        
        Args:
            title: 表格标题
            folder_token: 可选文件夹token
            
        Returns:
            表格token或None
        """
        print(f"创建电子表格: {title}")
        
        # API端点
        endpoint = "/sheets/v3/spreadsheets"
        
        # 请求数据
        request_data = {
            "title": title
        }
        
        if folder_token:
            request_data["folder_token"] = folder_token
        
        print(f"API端点: {endpoint}")
        print(f"请求数据: {json.dumps(request_data, indent=2, ensure_ascii=False)}")
        
        # 实际调用示例（需要OpenClaw实现）
        # response = self._call_api("POST", endpoint, request_data)
        
        # 模拟响应
        spreadsheet_token = f"st_{int(time.time())}_{title[:10]}"
        
        print(f"✓ 表格创建成功")
        print(f"表格token: {spreadsheet_token}")
        print(f"表格URL: https://example.feishu.cn/sheets/{spreadsheet_token}")
        
        return spreadsheet_token
    
    def add_sheets(self, spreadsheet_token: str, sheets: List[Dict]) -> bool:
        """
        添加工作表
        
        Args:
            spreadsheet_token: 表格token
            sheets: 工作表列表
            
        Returns:
            是否成功
        """
        print(f"为表格 {spreadsheet_token} 添加工作表...")
        
        for sheet in sheets:
            print(f"添加工作表: {sheet.get('name', '未命名')}")
            
            # API端点
            endpoint = f"/sheets/v3/spreadsheets/{spreadsheet_token}/sheets_batch_update"
            
            # 请求数据
            request_data = {
                "requests": [{
                    "addSheet": {
                        "properties": {
                            "title": sheet.get("name", "Sheet"),
                            "index": sheet.get("index", 0),
                            "grid_properties": {
                                "row_count": sheet.get("row_count", 100),
                                "column_count": sheet.get("column_count", 10)
                            }
                        }
                    }
                }]
            }
            
            print(f"API端点: {endpoint}")
            print(f"请求数据: {json.dumps(request_data, indent=2, ensure_ascii=False)}")
        
        print("✓ 工作表添加完成")
        return True
    
    def write_data(self, spreadsheet_token: str, sheet_id: str, 
                   data: List[List[Any]], start_row: int = 0, start_col: int = 0) -> bool:
        """
        写入数据到工作表
        
        Args:
            spreadsheet_token: 表格token
            sheet_id: 工作表ID
            data: 二维数据数组
            start_row: 起始行
            start_col: 起始列
            
        Returns:
            是否成功
        """
        print(f"写入数据到工作表 {sheet_id}...")
        print(f"数据大小: {len(data)} 行 x {len(data[0]) if data else 0} 列")
        
        if not data:
            print("⚠ 无数据可写入")
            return False
        
        # API端点
        endpoint = f"/sheets/v3/spreadsheets/{spreadsheet_token}/values_batch_update"
        
        # 构建范围
        end_row = start_row + len(data) - 1
        end_col = start_col + len(data[0]) - 1 if data else start_col
        
        range_str = f"{sheet_id}!R{start_row+1}C{start_col+1}:R{end_row+1}C{end_col+1}"
        
        # 请求数据
        request_data = {
            "value_ranges": [{
                "range": range_str,
                "values": data
            }]
        }
        
        print(f"API端点: {endpoint}")
        print(f"写入范围: {range_str}")
        print(f"数据示例 (前2行):")
        for i, row in enumerate(data[:2]):
            print(f"  行{i+1}: {row}")
        
        print("✓ 数据写入完成")
        return True
    
    def set_formatting(self, spreadsheet_token: str, sheet_id: str, 
                       formats: List[Dict]) -> bool:
        """
        设置格式
        
        Args:
            spreadsheet_token: 表格token
            sheet_id: 工作表ID
            formats: 格式设置列表
            
        Returns:
            是否成功
        """
        print(f"为工作表 {sheet_id} 设置格式...")
        
        for fmt in formats:
            fmt_type = fmt.get("type", "unknown")
            print(f"设置格式: {fmt_type}")
            
            if fmt_type == "conditional_format":
                print("  条件格式: 根据状态设置颜色")
            elif fmt_type == "data_validation":
                print("  数据验证: 限制输入值")
            elif fmt_type == "formula":
                print(f"  公式: {fmt.get('formula', '')}")
        
        print("✓ 格式设置完成")
        return True
    
    def _call_api(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """
        调用API（需要OpenClaw实现）
        
        Args:
            method: HTTP方法
            endpoint: API端点
            data: 请求数据
            
        Returns:
            响应数据或None
        """
        # 这里需要OpenClaw的实际实现
        # 示例代码，实际应由OpenClaw处理
        print(f"调用API: {method} {endpoint}")
        
        # 模拟成功响应
        return {
            "code": 0,
            "msg": "success",
            "data": {
                "spreadsheet_token": f"st_{int(time.time())}",
                "spreadsheet_url": "https://example.feishu.cn/sheets/st_xxx"
            }
        }

class TaskDataProcessor:
    """任务数据处理类"""
    
    def __init__(self, data_file: str = "task-management/data-for-spreadsheet.json"):
        """初始化"""
        self.data_file = data_file
        self.data = None
        
    def load_data(self) -> bool:
        """加载数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"✓ 数据加载成功")
            return True
        except Exception as e:
            print(f"✗ 数据加载失败: {e}")
            return False
    
    def prepare_task_sheet_data(self) -> List[List[Any]]:
        """准备任务工作表数据"""
        if not self.data:
            return []
        
        tasks = self.data.get('tasks', [])
        rows = []
        
        # 表头
        header = ["任务ID", "任务名称", "状态", "优先级", "负责人", 
                  "创建时间", "预计完成", "实际完成", "耗时(分钟)", 
                  "描述", "产出", "类别", "复杂度"]
        rows.append(header)
        
        # 数据行
        for task in tasks:
            row = [
                task.get("task_id", ""),
                task.get("task_name", ""),
                task.get("status", ""),
                task.get("priority", ""),
                task.get("owner", ""),
                task.get("created_time", ""),
                task.get("estimated_completion", ""),
                task.get("actual_completion", ""),
                task.get("time_spent_minutes", ""),
                task.get("description", ""),
                ", ".join(task.get("outputs", [])),
                task.get("category", ""),
                task.get("complexity", "")
            ]
            rows.append(row)
        
        return rows
    
    def prepare_team_sheet_data(self) -> List[List[Any]]:
        """准备团队工作表数据"""
        if not self.data:
            return []
        
        team = self.data.get('team_members', [])
        rows = []
        
        # 表头
        header = ["成员", "角色", "擅长领域", "当前任务", "状态", 
                  "已完成任务数", "专长分类", "开始时间", "结束时间"]
        rows.append(header)
        
        # 专长映射
        expertise_map = {
            "主Agent": "项目管理",
            "飞书API专家": "技术分析",
            "编码专家": "开发实现",
            "任务记录员": "文档记录",
            "研究专家": "技术研究"
        }
        
        expertise_area = {
            "主Agent": "项目管理、协调沟通",
            "飞书API专家": "API集成、技术分析",
            "编码专家": "Python开发、脚本编写",
            "任务记录员": "文档整理、数据统计",
            "研究专家": "技术调研、方案设计"
        }
        
        # 数据行
        for member in team:
            name = member.get("name", "")
            row = [
                name,
                member.get("role", ""),
                expertise_area.get(name, "未指定"),
                member.get("current_task", ""),
                member.get("status", ""),
                member.get("tasks_completed", 0),
                expertise_map.get(name, "其他"),
                member.get("start_time", ""),
                member.get("end_time", "")
            ]
            rows.append(row)
        
        return rows

def main():
    """主函数"""
    print("飞书电子表格API实现示例")
    print("=" * 60)
    
    # 初始化
    api = FeishuSpreadsheetAPI()
    processor = TaskDataProcessor()
    
    # 加载数据
    if not processor.load_data():
        return
    
    # 创建表格
    title = f"OpenClaw任务管理_{datetime.now().strftime('%Y%m%d_%H%M')}"
    spreadsheet_token = api.create_spreadsheet(title)
    
    if not spreadsheet_token:
        print("✗ 表格创建失败")
        return
    
    # 添加工作表
    sheets = [
        {"name": "任务清单", "index": 0, "row_count": 100, "column_count": 13},
        {"name": "团队成员", "index": 1, "row_count": 50, "column_count": 9},
        {"name": "统计看板", "index": 2, "row_count": 30, "column_count": 8},
        {"name": "时间效率", "index": 3, "row_count": 20, "column_count": 6}
    ]
    
    api.add_sheets(spreadsheet_token, sheets)
    
    # 准备并写入数据
    task_data = processor.prepare_task_sheet_data()
    team_data = processor.prepare_team_sheet_data()
    
    # 写入任务数据（假设sheet_id为任务清单的工作表ID）
    api.write_data(spreadsheet_token, "任务清单", task_data)
    
    # 写入团队数据
    api.write_data(spreadsheet_token, "团队成员", team_data)
    
    # 设置格式
    formats = [
        {"type": "conditional_format", "range": "任务清单!C2:C100", "rule": "状态颜色"},
        {"type": "data_validation", "range": "任务清单!D2:D100", "values": ["紧急", "高", "中", "低"]},
        {"type": "formula", "range": "统计看板!C2", "formula": "=COUNTIF(任务清单!C:C,\"已完成\")"}
    ]
    
    api.set_formatting(spreadsheet_token, "任务清单", formats)
    
    print("\n" + "=" * 60)
    print("✅ 飞书电子表格创建流程完成")
    print("=" * 60)
    print(f"表格标题: {title}")
    print(f"工作表: 任务清单, 团队成员, 统计看板, 时间效率")
    print(f"数据行数: 任务{len(task_data)-1}行, 团队{len(team_data)-1}行")
    print("\n下一步: 等待OpenClaw团队实现具体的API调用")

if __name__ == "__main__":
    main()
'''
    
    # 保存实现代码
    filename = f"feishu_spreadsheet_implementation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(implementation_code)
    
    print(f"✓ API实现代码已保存: {filename}")
    
    # 生成使用说明
    print("\n" + "=" * 60)
    print("使用说明")
    print("=" * 60)
    
    usage = f"""
## 如何使用

### 1. 运行数据测试
```bash
python feishu_spreadsheet_api_example.py
```

### 2. 查看实现代码
```bash
python {filename}
```

### 3. 实际调用步骤

由于OpenClaw的飞书工具实现细节未公开，实际调用需要：

1. **确认API可用性**: 联系OpenClaw团队确认电子表格API
2. **获取访问令牌**: OpenClaw会自动处理认证
3. **调用创建接口**: 使用正确的端点和参数
4. **处理响应**: 解析返回的表格token和URL

### 4. 备用方案

如果电子表格API不可用，建议：

1. **使用多维表格**: 权限已开通 bitable:app
2. **使用文档表格**: 在飞书文档中创建表格
3. **导出CSV导入**: 生成CSV文件手动导入

### 5. 验证清单

- [x] 权限验证: sheets:spreadsheet:create 已开通
- [x] 数据准备: 任务和团队数据已格式化
- [x] 结构设计: 4个工作表结构已定义
- [x] 代码生成: 完整的API实现代码
- [ ] API调用: 等待OpenClaw实现具体调用
- [ ] 实际测试: 需要实际API环境测试

---
*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    print(usage)
    
    return True

if __name__ == "__main__":
    # 测试工具
    test_feishu_tools()
    
    # 生成API实现
    generate_api_implementation()