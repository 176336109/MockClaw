#!/usr/bin/env python3
"""
获取多维表格实际结构
"""

import json
import requests
from pathlib import Path

def get_config():
    """获取配置"""
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    feishu_config = config.get('channels', {}).get('feishu', {})
    accounts = feishu_config.get('accounts', {}).get('main', {})
    
    return accounts.get('appId'), accounts.get('appSecret')

def get_access_token(app_id, app_secret):
    """获取token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json; charset=utf-8"}
    data = {"app_id": app_id, "app_secret": app_secret}
    
    response = requests.post(url, headers=headers, json=data, timeout=10)
    result = response.json()
    
    if result.get("code") == 0:
        return result.get("tenant_access_token")
    else:
        print(f"❌ 获取token失败: {result}")
        return None

def get_table_structure(token, app_token, table_id):
    """获取表格结构"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers, timeout=10)
    result = response.json()
    
    if result.get("code") == 0:
        fields = result.get("data", {}).get("items", [])
        return fields
    else:
        print(f"❌ 获取表格结构失败: {result}")
        return []

def get_table_records(token, app_token, table_id):
    """获取表格现有记录"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers, timeout=10)
    result = response.json()
    
    if result.get("code") == 0:
        records = result.get("data", {}).get("items", [])
        return records
    else:
        print(f"❌ 获取记录失败: {result}")
        return []

def main():
    print("🔍 获取多维表格结构...")
    
    # 1. 获取配置
    app_id, app_secret = get_config()
    if not app_id or not app_secret:
        print("❌ 配置缺失")
        return
    
    print(f"✅ 应用ID: {app_id[:8]}...")
    
    # 2. 获取token
    token = get_access_token(app_id, app_secret)
    if not token:
        return
    
    print(f"✅ Token: {token[:20]}...")
    
    # 3. 多维表格信息
    app_token = "FCRNbSo4ja4hCEs5411cNZQXnkh"  # 从URL提取
    table_id = "tblRmMB6LIdLHyEt"  # 从MEMORY.md得知
    
    print(f"📊 多维表格:")
    print(f"   应用token: {app_token}")
    print(f"   表格ID: {table_id}")
    
    # 4. 获取表格结构
    print("\n📋 表格字段结构:")
    fields = get_table_structure(token, app_token, table_id)
    
    if fields:
        for field in fields:
            field_name = field.get('field_name', '未知')
            field_type = field.get('type', '未知')
            field_id = field.get('field_id', '未知')
            print(f"   - {field_name} ({field_type}) [ID: {field_id}]")
    else:
        print("   ❌ 无法获取字段结构")
    
    # 5. 获取现有记录
    print("\n📝 现有记录:")
    records = get_table_records(token, app_token, table_id)
    
    if records:
        print(f"   找到 {len(records)} 条记录")
        for i, record in enumerate(records[:3]):  # 显示前3条
            record_id = record.get('record_id', '未知')
            fields = record.get('fields', {})
            print(f"   [{i+1}] 记录ID: {record_id}")
            for key, value in fields.items():
                print(f"       {key}: {value}")
    else:
        print("   ⚠️ 没有现有记录或无法获取")
    
    # 6. 保存结构信息
    structure_info = {
        "app_token": app_token,
        "table_id": table_id,
        "fields": fields,
        "record_count": len(records),
        "sample_records": records[:2] if records else []
    }
    
    output_file = Path.home() / ".openclaw" / "workspace" / "bitable_structure.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structure_info, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 结构信息已保存到: {output_file}")
    
    # 7. 建议
    print("\n🎯 下一步建议:")
    if fields:
        print("   1. 使用正确的字段名更新脚本")
        print("   2. 根据字段类型调整数据格式")
        print("   3. 测试更新功能")
    else:
        print("   1. 检查表格ID是否正确")
        print("   2. 验证API权限")
        print("   3. 确认多维表格是否存在")

if __name__ == "__main__":
    main()