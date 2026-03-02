#!/usr/bin/env python3
"""
测试token获取
"""

import json
import requests
from pathlib import Path

# 加载配置
config_path = Path.home() / ".openclaw" / "openclaw.json"
with open(config_path, 'r') as f:
    config = json.load(f)

feishu_config = config.get('channels', {}).get('feishu', {})
accounts = feishu_config.get('accounts', {}).get('main', {})

app_id = accounts.get('appId')
app_secret = accounts.get('appSecret')

print(f"App ID: {app_id}")
print(f"App Secret: {app_secret[:10]}...")

# 尝试获取token
url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
headers = {"Content-Type": "application/json; charset=utf-8"}
data = {
    "app_id": app_id,
    "app_secret": app_secret
}

try:
    print("\n尝试获取token...")
    response = requests.post(url, headers=headers, json=data, timeout=10)
    result = response.json()
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get("code") == 0:
        token = result.get("tenant_access_token")
        print(f"\n✅ 成功获取token!")
        print(f"Token前20位: {token[:20]}...")
        
        # 测试API调用
        print("\n测试API调用...")
        test_url = "https://open.feishu.cn/open-apis/bitable/v1/apps/FCRNbSo4ja4hCEs5411cNZQXnkh/tables"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        test_response = requests.get(test_url, headers=headers, timeout=10)
        test_result = test_response.json()
        
        print(f"API测试状态码: {test_response.status_code}")
        print(f"API测试结果: {json.dumps(test_result, indent=2, ensure_ascii=False)}")
        
    else:
        print(f"\n❌ 获取token失败: {result.get('msg')}")
        
except Exception as e:
    print(f"\n❌ 异常: {e}")
    import traceback
    traceback.print_exc()