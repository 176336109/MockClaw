#!/usr/bin/env python3
"""
飞书API探索脚本 - 尝试发现电子表格API
"""

import requests
import json
import os

# 基础配置
BASE_URL = "https://open.feishu.cn/open-apis"

def test_api_endpoint(endpoint, method="GET", data=None):
    """测试API端点"""
    print(f"\n测试端点: {endpoint}")
    print(f"方法: {method}")
    
    # 这里需要实际的访问令牌，但我们先只测试端点结构
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token"  # 占位符
    }
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
            print(f"不支持的方法: {method}")
            return None
        
        print(f"状态码: {response.status_code}")
        if response.status_code == 401:
            print("需要有效令牌")
        elif response.status_code == 404:
            print("端点不存在")
        elif response.status_code == 403:
            print("权限不足")
        else:
            print(f"响应: {response.text[:200]}")
        
        return response.status_code
        
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def explore_sheet_apis():
    """探索电子表格相关API"""
    print("=" * 60)
    print("探索飞书电子表格API")
    print("=" * 60)
    
    # 可能的电子表格API端点
    endpoints = [
        # 文档API（已知存在）
        ("/docx/v1/documents", "GET"),
        ("/docx/v1/documents", "POST"),
        
        # 可能的电子表格API
        ("/sheets/v1/spreadsheets", "GET"),
        ("/sheets/v1/spreadsheets", "POST"),
        ("/sheets/v3/spreadsheets", "GET"),
        ("/sheets/v3/spreadsheets", "POST"),
        
        # 多维表格API
        ("/bitable/v1/apps", "GET"),
        ("/bitable/v1/apps", "POST"),
        
        # 云盘API（已知存在）
        ("/drive/v1/files", "GET"),
        ("/drive/v1/export", "GET"),
    ]
    
    for endpoint, method in endpoints:
        test_api_endpoint(endpoint, method)
    
    print("\n" + "=" * 60)
    print("探索完成")
    print("=" * 60)

if __name__ == "__main__":
    explore_sheet_apis()