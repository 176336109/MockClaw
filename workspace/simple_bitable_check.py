#!/usr/bin/env python3
"""
简单检查多维表格字段
"""

import json
import requests
from pathlib import Path

print("🔍 简单检查多维表格")
print("=" * 60)

# 加载配置
config_path = Path.home() / ".openclaw" / "openclaw.json"
with open(config_path, 'r') as f:
    config = json.load(f)

feishu_config = config.get('channels', {}).get('feishu', {})
accounts = feishu_config.get('accounts', {}).get('main', {})

app_id = accounts.get('appId')
app_secret = accounts.get('appSecret')

# 获取token
url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
headers = {"Content-Type": "application/json; charset=utf-8"}
data = {
    "app_id": app_id,
    "app_secret": app_secret
}

try:
    response = requests.post(url, headers=headers, json=data, timeout=10)
    print(f"Token请求状态: {response.status_code}")
    print(f"Token响应文本: {response.text[:200]}...")
    
    result = response.json()
    print(f"Token结果code: {result.get('code')}")
    
    if result.get("code") != 0:
        print(f"❌ 获取token失败: {result}")
        exit(1)
    
    token = result.get("tenant_access_token")
    print(f"✅ Token获取成功: {token[:20]}...")
    
except Exception as e:
    print(f"❌ 请求异常: {e}")
    exit(1)

print("\n" + "=" * 60)
print("✅ 基础检查完成")
print("=" * 60)