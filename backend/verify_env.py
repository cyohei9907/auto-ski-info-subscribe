#!/usr/bin/env python
"""
验证环境变量配置是否正确
"""
import os
import sys

def check_env_variable():
    """检查环境变量是否设置"""
    print("=" * 60)
    print("环境变量验证脚本")
    print("=" * 60)
    
    # 检查新的环境变量
    ai_key = os.getenv('AI_API_KEY_GOOGLE')
    old_key = os.getenv('GEMINI_API_KEY')
    
    print("\n1. 检查系统环境变量:")
    print(f"   AI_API_KEY_GOOGLE: {'✅ 已设置' if ai_key else '❌ 未设置'}")
    if ai_key:
        print(f"   值: {ai_key[:10]}...{ai_key[-4:]}" if len(ai_key) > 14 else f"   值: {ai_key}")
    
    if old_key:
        print(f"\n   ⚠️  警告: 旧环境变量 GEMINI_API_KEY 仍然存在")
        print(f"   建议删除旧环境变量，只保留 AI_API_KEY_GOOGLE")
    
    # 检查 Django 配置
    print("\n2. 检查 Django 配置:")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'auto_ski_info.settings')
        
        import django
        django.setup()
        
        from django.conf import settings
        
        if hasattr(settings, 'GEMINI_API_KEY'):
            if settings.GEMINI_API_KEY:
                print(f"   settings.GEMINI_API_KEY: ✅ 已配置")
                print(f"   值: {settings.GEMINI_API_KEY[:10]}...{settings.GEMINI_API_KEY[-4:]}" 
                      if len(settings.GEMINI_API_KEY) > 14 else f"   值: {settings.GEMINI_API_KEY}")
            else:
                print(f"   settings.GEMINI_API_KEY: ❌ 为空")
        else:
            print(f"   settings.GEMINI_API_KEY: ❌ 未定义")
    except Exception as e:
        print(f"   ❌ 无法加载 Django 配置: {e}")
    
    # 检查 .env 文件
    print("\n3. 检查 .env 文件:")
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_file):
        print(f"   .env 文件: ✅ 存在")
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'AI_API_KEY_GOOGLE' in content:
                print(f"   AI_API_KEY_GOOGLE: ✅ 已配置")
            else:
                print(f"   AI_API_KEY_GOOGLE: ❌ 未配置")
            
            if 'GEMINI_API_KEY' in content:
                print(f"   ⚠️  警告: .env 文件中仍有 GEMINI_API_KEY")
    else:
        print(f"   .env 文件: ❌ 不存在")
    
    # 总结
    print("\n" + "=" * 60)
    if ai_key and not old_key:
        print("✅ 配置正确！环境变量迁移完成")
    elif ai_key and old_key:
        print("⚠️  建议删除旧的 GEMINI_API_KEY 环境变量")
    else:
        print("❌ 请设置 AI_API_KEY_GOOGLE 环境变量")
    print("=" * 60)

if __name__ == '__main__':
    check_env_variable()
