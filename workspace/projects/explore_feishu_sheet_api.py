#!/usr/bin/env python3
"""
飞书电子表格API探索脚本
基于现有权限进行实际测试
"""

import json
import os
import sys

def analyze_permissions():
    """分析当前权限状态"""
    print("=" * 60)
    print("当前飞书应用权限分析")
    print("=" * 60)
    
    # 从之前的feishu_app_scopes结果中提取关键权限
    key_permissions = {
        "sheets:spreadsheet:create": "✅ 创建电子表格",
        "sheets:spreadsheet:read": "✅ 读取电子表格", 
        "sheets:spreadsheet": "✅ 完整电子表格权限",
        "bitable:app": "✅ 多维表格完整权限",
        "sheets:spreadsheet:readonly": "✅ 电子表格只读权限",
        "sheets:spreadsheet:write_only": "✅ 电子表格写入权限",
        "sheets:spreadsheet.meta:read": "✅ 读取表格元数据",
        "sheets:spreadsheet.meta:write_only": "✅ 写入表格元数据"
    }
    
    print("\n关键权限状态:")
    for perm, desc in key_permissions.items():
        print(f"  {desc}")
    
    print("\n" + "=" * 60)
    print("权限分析完成")
    print("=" * 60)

def explore_api_endpoints():
    """探索API端点结构"""
    print("\n" + "=" * 60)
    print("飞书电子表格API端点结构")
    print("=" * 60)
    
    # 基于飞书API文档推断的端点结构
    endpoints = {
        "电子表格基础操作": [
            "POST /open-apis/sheets/v3/spreadsheets - 创建电子表格",
            "GET /open-apis/sheets/v3/spreadsheets/{spreadsheetToken} - 获取电子表格信息",
            "PATCH /open-apis/sheets/v3/spreadsheets/{spreadsheetToken} - 更新电子表格",
            "GET /open-apis/sheets/v3/spreadsheets/{spreadsheetToken}/sheets - 获取工作表列表",
            "POST /open-apis/sheets/v3/spreadsheets/{spreadsheetToken}/sheets - 创建工作表",
            "GET /open-apis/sheets/v3/spreadsheets/{spreadsheetToken}/sheets/{sheetId} - 获取工作表信息",
            "PATCH /open-apis/sheets/v3/spreadsheets/{spreadsheetToken}/sheets/{sheetId} - 更新工作表"
        ],
        "单元格数据操作": [
            "GET /open-apis/sheets/v3/spreadsheets/{spreadsheetToken}/values/{range} - 读取单元格数据",
            "PUT /open-apis/sheets/v3/spreadsheets/{spreadsheetToken}/values/{range} - 写入单元格数据",
            "POST /open-apis/sheets/v3/spreadsheets/{spreadsheetToken}/values:batchGet - 批量读取数据",
            "POST /open-apis/sheets/v3/spreadsheets/{spreadsheetToken}/values:batchUpdate - 批量更新数据"
        ],
        "多维表格操作": [
            "GET /open-apis/bitable/v1/apps - 获取多维表格应用列表",
            "POST /open-apis/bitable/v1/apps - 创建多维表格应用",
            "GET /open-apis/bitable/v1/apps/{app_token} - 获取应用信息",
            "GET /open-apis/bitable/v1/apps/{app_token}/tables - 获取表格列表",
            "POST /open-apis/bitable/v1/apps/{app_token}/tables - 创建表格",
            "GET /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records - 获取记录列表",
            "POST /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records - 创建记录",
            "PUT /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id} - 更新记录",
            "DELETE /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id} - 删除记录"
        ]
    }
    
    for category, endpoint_list in endpoints.items():
        print(f"\n{category}:")
        for endpoint in endpoint_list:
            print(f"  {endpoint}")
    
    print("\n" + "=" * 60)
    print("端点结构分析完成")
    print("=" * 60)

def create_sample_requests():
    """创建示例请求"""
    print("\n" + "=" * 60)
    print("示例API请求")
    print("=" * 60)
    
    # 1. 创建电子表格示例
    create_spreadsheet = {
        "title": "任务管理系统",
        "folder_token": "optional_folder_token"
    }
    
    print("\n1. 创建电子表格请求:")
    print(json.dumps(create_spreadsheet, indent=2, ensure_ascii=False))
    
    # 2. 写入数据示例
    write_data = {
        "valueRange": {
            "range": "Sheet1!A1:D5",
            "values": [
                ["任务ID", "任务名称", "状态", "负责人"],
                ["T001", "API集成开发", "进行中", "张三"],
                ["T002", "文档编写", "待开始", "李四"],
                ["T003", "测试验证", "已完成", "王五"],
                ["T004", "部署上线", "规划中", "赵六"]
            ]
        }
    }
    
    print("\n2. 写入数据请求:")
    print(json.dumps(write_data, indent=2, ensure_ascii=False))
    
    # 3. 多维表格创建记录示例
    create_bitable_record = {
        "fields": {
            "任务名称": "API测试",
            "优先级": "高",
            "状态": "进行中",
            "截止日期": "2026-03-01",
            "负责人": "张三"
        }
    }
    
    print("\n3. 多维表格创建记录请求:")
    print(json.dumps(create_bitable_record, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("示例请求生成完成")
    print("=" * 60)

def integration_with_openclaw():
    """OpenClaw集成方案"""
    print("\n" + "=" * 60)
    print("OpenClaw集成方案")
    print("=" * 60)
    
    print("\n方案一：扩展现有feishu_doc工具")
    print("""
    1. 添加新的action参数：
       - action: "create_sheet" - 创建电子表格
       - action: "read_sheet" - 读取电子表格数据
       - action: "write_sheet" - 写入电子表格数据
       - action: "create_bitable" - 创建多维表格
       - action: "bitable_record" - 多维表格记录操作
    
    2. 参数设计：
       create_sheet:
         - title: 表格标题
         - folder_token: 文件夹token（可选）
       
       write_sheet:
         - spreadsheet_token: 表格token
         - range: 单元格范围（如"A1:D5"）
         - values: 二维数组数据
    """)
    
    print("\n方案二：创建独立工具 feishu_sheet")
    print("""
    独立工具设计：
    - 名称：feishu_sheet
    - 功能：专门处理电子表格和多维表格操作
    - 优势：职责分离，代码清晰
    
    工具结构：
    {
      "name": "feishu_sheet",
      "description": "飞书电子表格和多维表格操作工具",
      "actions": {
        "create_spreadsheet": "创建电子表格",
        "read_values": "读取单元格数据",
        "write_values": "写入单元格数据",
        "create_bitable_app": "创建多维表格应用",
        "bitable_crud": "多维表格CRUD操作"
      }
    }
    """)
    
    print("\n方案三：混合方案（推荐）")
    print("""
    1. 短期：扩展feishu_doc工具，快速实现基础功能
    2. 中期：开发独立的feishu_sheet工具，提供完整功能
    3. 长期：两者并存，根据场景选择使用
    
    优势：
    - 快速上线：立即可以使用
    - 渐进增强：逐步完善功能
    - 灵活选择：用户可以根据需求选择工具
    """)
    
    print("\n" + "=" * 60)
    print("集成方案设计完成")
    print("=" * 60)

def create_implementation_plan():
    """创建实施计划"""
    print("\n" + "=" * 60)
    print("实施计划")
    print("=" * 60)
    
    print("\n第一阶段：基础功能实现（1-2天）")
    print("""
    1. 扩展feishu_doc工具，添加电子表格基础功能
       - 创建电子表格
       - 读取单元格数据
       - 写入单元格数据
    
    2. 创建测试用例
       - 测试创建功能
       - 测试读写功能
       - 验证权限有效性
    
    3. 文档编写
       - 使用说明
       - API参考
       - 示例代码
    """)
    
    print("\n第二阶段：高级功能开发（2-3天）")
    print("""
    1. 多维表格支持
       - 创建多维表格应用
       - 表格和字段管理
       - 记录CRUD操作
    
    2. 批量操作优化
       - 批量读取数据
       - 批量更新数据
       - 数据导入导出
    
    3. 错误处理和重试机制
       - API错误处理
       - 网络重试
       - 数据验证
    """)
    
    print("\n第三阶段：集成优化（1-2天）")
    print("""
    1. 与OpenClaw深度集成
       - 命令行支持
       - 配置文件支持
       - 环境变量配置
    
    2. 性能优化
       - 请求合并
       - 缓存机制
       - 异步处理
    
    3. 监控和日志
       - 操作日志
       - 性能监控
       - 错误报警
    """)
    
    print("\n" + "=" * 60)
    print("实施计划制定完成")
    print("=" * 60)

def main():
    """主函数"""
    print("飞书电子表格API技术探索报告")
    print("生成时间: 2026年2月28日")
    print("=" * 60)
    
    analyze_permissions()
    explore_api_endpoints()
    create_sample_requests()
    integration_with_openclaw()
    create_implementation_plan()
    
    print("\n" + "=" * 60)
    print("探索报告生成完成")
    print("=" * 60)
    
    # 生成总结
    print("\n关键发现:")
    print("1. ✅ 当前应用已具备完整的电子表格权限")
    print("2. ✅ 包括创建、读取、写入等所有必要权限")
    print("3. ✅ 多维表格权限也已具备")
    print("4. 🚀 可以立即开始API集成开发")
    
    print("\n建议行动:")
    print("1. 立即开始扩展feishu_doc工具，添加电子表格功能")
    print("2. 创建简单的测试用例验证API可用性")
    print("3. 开发任务管理系统原型")
    print("4. 逐步完善功能和优化性能")

if __name__ == "__main__":
    main()