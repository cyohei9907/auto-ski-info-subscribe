#!/usr/bin/env python
"""测试 Redis 连接"""
import redis

try:
    # 尝试连接 Redis
    r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=5)
    
    # 测试 ping
    response = r.ping()
    print(f"✅ Redis 连接成功!")
    print(f"   PING 响应: {response}")
    
    # 测试写入
    r.set('test_key', 'test_value')
    value = r.get('test_key')
    print(f"   读写测试: {value.decode('utf-8')}")
    
    # 清理
    r.delete('test_key')
    print(f"✅ Redis 工作正常!")
    
except redis.exceptions.ConnectionError as e:
    print(f"❌ Redis 连接失败:")
    print(f"   错误: {e}")
    print(f"\n可能的原因:")
    print(f"   1. Redis 容器没有运行")
    print(f"   2. 端口映射不正确")
    print(f"   3. 防火墙阻止连接")
    print(f"\n解决方案:")
    print(f"   运行: docker ps --filter 'name=redis'")
    print(f"   检查端口映射是否包含: 0.0.0.0:6379->6379/tcp")

except Exception as e:
    print(f"❌ 未知错误: {e}")
