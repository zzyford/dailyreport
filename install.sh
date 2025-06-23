#!/bin/bash

echo "=== 日报系统安装脚本 ==="

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
echo "检测到Python版本: $python_version"

if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
    echo "错误: 需要Python 3.8或更高版本"
    exit 1
fi

# 创建虚拟环境
echo "创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt

# 创建logs目录
echo "创建日志目录..."
mkdir -p logs

# 复制配置文件
if [ ! -f .env ]; then
    echo "复制配置文件模板..."
    cp env.example .env
    echo "请编辑 .env 文件配置您的邮箱和API信息"
else
    echo ".env 文件已存在，跳过复制"
fi

# 设置执行权限
chmod +x main.py

echo ""
echo "=== 安装完成 ==="
echo "下一步操作："
echo "1. 编辑 .env 文件，配置邮箱和API信息"
echo "2. 测试连接: python main.py --test"
echo "3. 手动执行一次: python main.py --run-once"
echo "4. 启动定时服务: python main.py --start"
echo ""
echo "注意: 请确保已激活虚拟环境 (source venv/bin/activate)" 