#!/usr/bin/env python3
"""
安全配置检查脚本 - 仅检查配置完整性，不显示具体内容
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def security_check():
    """安全配置检查 - 不暴露隐私信息"""
    print("=" * 60)
    print("🔒 安全配置检查")
    print("=" * 60)
    
    # 检查必需配置项
    required_configs = [
        ("EMAIL_USERNAME", "邮箱用户名"),
        ("EMAIL_PASSWORD", "邮箱密码"),
        ("DASHSCOPE_API_KEY", "AI API密钥"),
        ("DASHSCOPE_APP_ID", "AI应用ID"),
        ("REPORT_FROM_EMAILS", "收集邮箱列表"),
    ]
    
    missing_configs = []
    configured_count = 0
    
    for env_key, desc in required_configs:
        env_value = os.getenv(env_key)
        if env_value and env_value.strip():
            print(f"✅ {desc}: 已配置")
            configured_count += 1
        else:
            print(f"❌ {desc}: 未配置")
            missing_configs.append(env_key)
    
    # 检查可选配置
    optional_configs = [
        ("REPORT_RECIPIENTS", "自动发送收件人"),
        ("REPORT_TIME", "发送时间"),
    ]
    
    print(f"\n📋 可选配置:")
    for env_key, desc in optional_configs:
        env_value = os.getenv(env_key)
        if env_value and env_value.strip():
            print(f"✅ {desc}: 已配置")
        else:
            print(f"⚠️ {desc}: 未配置 (将使用默认值)")
    
    # 统计信息
    print(f"\n📊 配置统计:")
    print(f"   必需配置: {configured_count}/{len(required_configs)} 项")
    
    if missing_configs:
        print(f"\n❗ 缺少以下必需配置:")
        for config in missing_configs:
            print(f"   - {config}")
        print(f"\n💡 请在 .env 文件中添加这些配置")
        return False
    else:
        print(f"\n🎉 所有必需配置都已完成！")
        return True

def check_email_count():
    """检查邮箱数量配置"""
    from_emails = os.getenv("REPORT_FROM_EMAILS", "")
    if from_emails:
        email_list = [email.strip() for email in from_emails.split(",") if email.strip()]
        print(f"\n📬 邮箱收集配置:")
        print(f"   收集邮箱数量: {len(email_list)} 个")
        if len(email_list) == 0:
            print(f"   ⚠️ 邮箱列表为空，将无法收集日报")
        elif len(email_list) > 10:
            print(f"   ⚠️ 邮箱数量较多，可能影响处理速度")
        else:
            print(f"   ✅ 邮箱数量合理")
    else:
        print(f"\n❌ 未配置收集邮箱，无法收集日报")

def show_env_template():
    """显示环境变量模板（不包含具体值）"""
    print(f"\n📝 .env 文件配置模板:")
    print("=" * 60)
    print("""
# 邮箱配置（必需）
EMAIL_USERNAME=your-email@company.com
EMAIL_PASSWORD=your-password

# AI配置（必需）
DASHSCOPE_API_KEY=your-api-key
DASHSCOPE_APP_ID=your-app-id

# 日报收集配置（必需）
REPORT_FROM_EMAILS=user1@company.com,user2@company.com,user3@company.com

# 可选配置
REPORT_RECIPIENTS=boss@company.com,manager@company.com
REPORT_TIME=09:00
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/api/v1/
""")
    print("=" * 60)

if __name__ == "__main__":
    print("🔒 正在进行安全配置检查...")
    print("   (不会显示任何隐私信息)")
    
    is_complete = security_check()
    check_email_count()
    
    if not is_complete:
        show_env_template()
        print("\n❌ 配置不完整，请补充必需配置后重试")
    else:
        print("\n✅ 配置检查通过，系统可以正常使用")
    
    print("=" * 60) 