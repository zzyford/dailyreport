#!/usr/bin/env python3
"""
智能日报系统 - 快速启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误：需要Python 3.8或更高版本")
        print(f"   当前版本：{sys.version}")
        return False
    print(f"✅ Python版本检查通过：{sys.version.split()[0]}")
    return True

def check_dependencies():

    """检查依赖包"""
    # 包名到模块名的映射
    package_mapping = {
        'flask': 'flask',
        'schedule': 'schedule',  # 使用 schedule 而不是 apscheduler
        'dashscope': 'dashscope',
        'pydantic': 'pydantic',
        'python-dotenv': 'dotenv',  # python-dotenv 的模块名是 dotenv
        'beautifulsoup4': 'bs4',  # beautifulsoup4 的模块名是 bs4
        'lxml': 'lxml',
        'requests': 'requests',
        'loguru': 'loguru',
    }
    
    missing_packages = []
    for package_name, module_name in package_mapping.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("❌ 缺少依赖包：")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n📦 请运行以下命令安装依赖：")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ 依赖包检查通过")
    return True

def check_config():
    """检查配置文件"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ 缺少配置文件：.env")
        print("📝 请按照以下步骤配置：")
        print("   1. 复制模板：cp env.example .env")
        print("   2. 编辑配置：vim .env")
        print("   3. 或运行配置脚本：python create_env.py")
        return False
    
    print("✅ 配置文件检查通过")
    return True

def check_directories():
    """检查必要目录"""
    directories = ['logs', 'templates', 'static']
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"❌ 缺少目录：{directory}")
            return False
    
    print("✅ 目录结构检查通过")
    return True

def start_application():
    """启动应用"""
    print("\n🚀 启动智能日报系统...")
    print("📱 Web界面地址：http://localhost:5002")
    print("⏹️  停止服务：按 Ctrl+C")
    print("-" * 50)
    
    try:
        # 启动主程序
        subprocess.run([sys.executable, 'web_app.py'], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 系统已停止")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 启动失败：{e}")
        return False
    except FileNotFoundError:
        print("\n❌ 找不到主程序文件：web_app.py")
        return False
    
    return True

def main():
    """主函数"""
    print("🎯 智能日报系统 - 启动检查")
    print("=" * 50)
    
    # 检查系统环境
    checks = [
        ("Python版本", check_python_version),
        ("依赖包", check_dependencies),
        ("配置文件", check_config),
        ("目录结构", check_directories),
    ]
    
    for check_name, check_func in checks:
        print(f"\n🔍 检查{check_name}...")
        if not check_func():
            print(f"\n💥 {check_name}检查失败，请解决后重试")
            return 1
    
    print("\n✅ 所有检查通过！")
    
    # 启动应用
    if not start_application():
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 