#!/usr/bin/env python3
"""
更新飞书多维表格脚本
"""

import requests
import json
import time

# 飞书应用配置
APP_ID = "cli_a9f25697be389ceb"
APP_SECRET = "caJHD9D8Wiw5NvxHmrAUbbpUurctZfEs"

# 多维表格配置
BASE_APP_TOKEN = "FCRNbSo4ja4hCEs5411cNZQXnkh"
TABLE_ID = "tblRmMB6LIdLHyEt"

def get_tenant_access_token():
    """获取租户访问token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()
        if result.get("code") == 0:
            return result.get("tenant_access_token")
        else:
            print(f"获取token失败: {result}")
            return None
    except Exception as e:
        print(f"获取token异常: {e}")
        return None

def add_record_to_table(token, fields):
    """添加记录到表格"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "fields": fields
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()
        print(f"API响应: {result}")
        return result
    except Exception as e:
        print(f"添加记录异常: {e}")
        return None

def main():
    print("开始更新多维表格...")
    
    # 1. 获取token
    token = get_tenant_access_token()
    if not token:
        print("❌ 无法获取访问token")
        return
    
    print(f"✅ Token获取成功: {token[:20]}...")
    
    # 2. 准备bocha技能数据
    bocha_fields = {
        "技能名称": "bocha-web-search",
        "可用情况": "可用",
        "描述": "博查AI Web Search API技能，支持时间过滤、结果摘要、多格式输出",
        "配置信息": "API Key已配置在.env文件，测试通过",
        "测试结果": "3次测试全部成功，扣费正常",
        "问题记录": "环境变量需要.env文件支持（已解决）",
        "解决方案": "已创建.env配置文件和启动脚本bocha_search.sh",
        "更新时间": "2026-03-01"
    }
    
    # 3. 添加记录
    print("添加bocha-web-search技能记录...")
    result = add_record_to_table(token, bocha_fields)
    
    if result and result.get("code") == 0:
        print("✅ 记录添加成功！")
        record_id = result.get("data", {}).get("record", {}).get("record_id")
        print(f"记录ID: {record_id}")
    else:
        print("❌ 记录添加失败")
        if result:
            print(f"错误信息: {result.get('msg')}")
        
        # 尝试使用更简单的字段名
        print("\n尝试使用简单字段名...")
        simple_fields = {
            "名称": "bocha-web-search",
            "状态": "可用",
            "描述": "博查AI搜索技能",
            "配置": "API Key已配置",
            "测试": "3次测试成功",
            "问题": "环境变量需要.env",
            "解决": "已创建.env文件",
            "时间": "2026-03-01"
        }
        
        result2 = add_record_to_table(token, simple_fields)
        if result2 and result2.get("code") == 0:
            print("✅ 使用简单字段名添加成功！")
        else:
            print("❌ 仍然失败，需要查看表格实际字段名")

if __name__ == "__main__":
    main()