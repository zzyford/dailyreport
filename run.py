#!/usr/bin/env python3
"""
智能日报系统 - 快速启动脚本
"""

import subprocess
import sys
import os

def main():
    """主函数"""
    print("🚀 智能日报系统快速启动")
    print("=" * 40)
    
    # 检查.env文件
    if not os.path.exists('.env'):
        print("⚠️  未找到.env配置文件")
        choice = input("是否现在配置？(y/N): ").strip().lower()
        if choice == 'y':
            try:
                subprocess.run([sys.executable, 'setup_env.py'], check=True)
            except subprocess.CalledProcessError:
                print("❌ 配置失败")
                return
        else:
            print("请先运行: python setup_env.py")
            return
    
    # 启动Web应用
    print("🔄 正在启动智能日报系统...")
    try:
        subprocess.run([sys.executable, 'web_app.py'], check=True)
    except KeyboardInterrupt:
        print("\n✅ 系统已安全关闭")
    except subprocess.CalledProcessError:
        print("❌ 启动失败")

if __name__ == "__main__":
    main() 