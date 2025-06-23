#!/usr/bin/env python3
"""
创建 .env 配置文件
"""

def create_env_file():
    """创建.env文件"""
    env_content = """# 企业邮箱配置（使用发现的正确配置）
EMAIL_USERNAME=zhangzhongyan@sunfield.mobi
EMAIL_PASSWORD=Zzyicn820828

# 阿里云百炼平台配置
DASHSCOPE_API_KEY=sk-a7d9d8e8ea2b407a8de842b1382c4dd9
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/api/v1/
DASHSCOPE_APP_ID=YOUR_APP_ID

# 日报配置
REPORT_RECIPIENTS=zhangzhongyan@sunfield.mobi
REPORT_FROM_EMAILS=shaoyunfeng@sunfield.mobi,chenxi@sunfield.mobi,xugenli@sunfield.mobi
REPORT_TIME=09:00
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✓ .env 文件创建成功")
        print("\n注意：你需要将 YOUR_APP_ID 替换为实际的阿里云百炼应用ID")
        return True
    except Exception as e:
        print(f"✗ 创建 .env 文件失败: {e}")
        return False

if __name__ == "__main__":
    create_env_file() 