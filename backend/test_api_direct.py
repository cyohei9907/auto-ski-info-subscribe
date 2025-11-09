#!/usr/bin/env python
"""直接测试 API 端点"""
import requests
import json

# 首先登录获取认证
login_url = "http://localhost:8000/api/accounts/login/"
monitor_url = "http://localhost:8000/api/monitor/accounts/1/monitor/"

# 登录数据（使用你的测试账户）
login_data = {
    "email": "test@example.com",  # 修改为你的测试账户
    "password": "test123"  # 修改为你的测试密码
}

print("=" * 80)
print("测试 monitor_account_now API")
print("=" * 80)

# 创建 session 以保持 cookies
session = requests.Session()

try:
    # 1. 登录
    print("\n1. 尝试登录...")
    response = session.post(login_url, json=login_data)
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ 登录成功")
        data = response.json()
        token = data.get('token')
        
        # 2. 调用监控 API
        print("\n2. 调用监控 API...")
        headers = {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        }
        
        response = session.post(monitor_url, headers=headers)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text[:500]}")
        
        if response.status_code == 200:
            print(f"   ✅ API 调用成功")
            print(f"   数据: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        else:
            print(f"   ❌ API 调用失败")
            
    else:
        print(f"   ❌ 登录失败")
        print(f"   响应: {response.text}")
        
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
