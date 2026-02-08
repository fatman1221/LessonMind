#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试通义千问API密钥是否有效
"""
import dashscope
from config import settings

def test_api_key():
    """测试API密钥"""
    print("=" * 50)
    print("通义千问API密钥测试")
    print("=" * 50)
    
    # 显示API密钥信息（部分隐藏）
    api_key = settings.DASHSCOPE_API_KEY
    if api_key:
        masked_key = f"{api_key[:10]}...{api_key[-10:]}" if len(api_key) > 20 else api_key
        print(f"API密钥: {masked_key}")
        print(f"密钥长度: {len(api_key)}")
    else:
        print("❌ 未配置API密钥")
        return False
    
    print("\n正在测试API连接...")
    
    try:
        dashscope.api_key = api_key
        from dashscope import Generation
        
        response = Generation.call(
            model='qwen-turbo',
            messages=[
                {'role': 'user', 'content': '你好，请回复"测试成功"'}
            ],
            result_format='message'
        )
        
        if response.status_code == 200:
            print("✅ API密钥有效！")
            print(f"✅ 响应内容: {response.output.choices[0].message.content}")
            return True
        else:
            print(f"❌ API调用失败")
            print(f"   状态码: {response.status_code}")
            print(f"   错误信息: {response.message}")
            
            # 提供解决建议
            error_msg = response.message or ""
            if "Access denied" in error_msg or "overdue" in error_msg.lower():
                print("\n💡 解决建议:")
                print("   1. 检查阿里云账户是否欠费")
                print("   2. 检查API密钥是否有效")
                print("   3. 访问: https://dashscope.console.aliyun.com/ 查看账户状态")
                print("   4. 参考文档: API_KEY_TROUBLESHOOTING.md")
            
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        
        error_str = str(e)
        if "Access denied" in error_str or "overdue" in error_str.lower():
            print("\n💡 解决建议:")
            print("   1. 检查阿里云账户是否欠费")
            print("   2. 检查API密钥是否有效")
            print("   3. 访问: https://dashscope.console.aliyun.com/ 查看账户状态")
            print("   4. 参考文档: API_KEY_TROUBLESHOOTING.md")
        
        return False

if __name__ == "__main__":
    success = test_api_key()
    print("\n" + "=" * 50)
    if success:
        print("✅ 测试通过，API密钥可以正常使用")
    else:
        print("❌ 测试失败，请检查API密钥配置")
    print("=" * 50)

