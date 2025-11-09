#!/usr/bin/env python
"""测试API端点返回数据"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from x_monitor.views import TweetListView
from x_monitor.models import XAccount

User = get_user_model()

def test_api_endpoint():
    """测试推文列表API"""
    print("=" * 60)
    print("测试 /monitor/tweets/ API 端点")
    print("=" * 60)
    
    # 获取用户
    user = User.objects.get(username='admin')
    print(f"\n用户: {user.username}")
    
    # 获取账户
    account = XAccount.objects.filter(user=user).first()
    if not account:
        print("❌ 用户没有X账户")
        return
    
    print(f"账户: @{account.username} (ID: {account.id})")
    
    # 创建请求
    factory = RequestFactory()
    request = factory.get(f'/monitor/tweets/?account_id={account.id}')
    request.user = user
    
    # 调用视图
    view = TweetListView.as_view()
    response = view(request)
    
    print(f"\nAPI 响应:")
    print(f"  状态码: {response.status_code}")
    
    if hasattr(response, 'data'):
        print(f"  数据类型: {type(response.data)}")
        
        if isinstance(response.data, dict):
            print(f"  返回结构:")
            for key in response.data.keys():
                print(f"    - {key}")
            
            if 'results' in response.data:
                results = response.data['results']
                print(f"\n  推文数量: {len(results)}")
                
                if len(results) > 0:
                    print(f"\n  第一条推文示例:")
                    tweet = results[0]
                    for key, value in tweet.items():
                        if key == 'content':
                            print(f"    {key}: {value[:50]}...")
                        else:
                            print(f"    {key}: {value}")
                else:
                    print("\n  ⚠️ results 数组为空")
        elif isinstance(response.data, list):
            print(f"  推文数量: {len(response.data)}")
            if len(response.data) > 0:
                print(f"\n  第一条推文:")
                print(f"    {response.data[0]}")
    else:
        print(f"  响应内容: {response.content[:200]}")

if __name__ == '__main__':
    test_api_endpoint()
