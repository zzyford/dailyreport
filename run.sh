#!/bin/bash

# 智能日报系统 - 一键启动脚本
# 功能：创建虚拟环境、安装依赖、运行服务

# 不设置 set -e，以便更好地处理错误

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  智能日报系统 - 一键启动脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 Python 版本
echo -e "${YELLOW}[1/4] 检查 Python 环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误：未找到 python3，请先安装 Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python 版本: $PYTHON_VERSION${NC}"

# 检查 Python 版本是否 >= 3.8
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}❌ 错误：需要 Python 3.8 或更高版本，当前版本: $PYTHON_VERSION${NC}"
    exit 1
fi

# Python 3.13 兼容性提示
if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 13 ]; then
    echo -e "${YELLOW}ℹ️  检测到 Python 3.13，已更新依赖包版本以支持${NC}"
fi

# 创建虚拟环境
echo ""
echo -e "${YELLOW}[2/4] 设置虚拟环境...${NC}"
VENV_DIR="venv"

if [ -d "$VENV_DIR" ]; then
    echo -e "${GREEN}✅ 虚拟环境已存在，跳过创建${NC}"
else
    echo -e "${BLUE}📦 创建虚拟环境...${NC}"
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✅ 虚拟环境创建成功${NC}"
fi

# 激活虚拟环境
echo -e "${BLUE}🔌 激活虚拟环境...${NC}"
source "$VENV_DIR/bin/activate"

# 升级 pip
echo ""
echo -e "${YELLOW}[3/4] 安装依赖包...${NC}"
echo -e "${BLUE}📦 升级 pip...${NC}"
pip install --quiet --upgrade pip

# 安装依赖
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}📦 安装项目依赖...${NC}"
    if pip install -r requirements.txt; then
        echo -e "${GREEN}✅ 依赖安装完成${NC}"
    else
        echo ""
        echo -e "${RED}❌ 依赖安装失败！${NC}"
        echo -e "${YELLOW}💡 可能的解决方案：${NC}"
        echo -e "${YELLOW}   1. 如果使用 Python 3.13，某些包可能需要更新版本${NC}"
        echo -e "${YELLOW}   2. 尝试使用 Python 3.11 或 3.12：${NC}"
        echo -e "${YELLOW}      python3.11 -m venv venv${NC}"
        echo -e "${YELLOW}   3. 检查网络连接和 pip 源配置${NC}"
        echo ""
        exit 1
    fi
else
    echo -e "${RED}❌ 错误：未找到 requirements.txt 文件${NC}"
    exit 1
fi

# 检查配置文件
echo ""
echo -e "${YELLOW}[4/4] 检查配置文件...${NC}"
if [ ! -f ".env" ]; then
    if [ -f "env.example" ]; then
        echo -e "${YELLOW}⚠️  未找到 .env 文件，从 env.example 复制模板...${NC}"
        cp env.example .env
        echo -e "${YELLOW}⚠️  请编辑 .env 文件配置您的邮箱和AI密钥${NC}"
    else
        echo -e "${YELLOW}⚠️  警告：未找到 .env 配置文件，系统可能无法正常运行${NC}"
    fi
else
    echo -e "${GREEN}✅ 配置文件检查通过${NC}"
fi

# 启动服务
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  🚀 启动智能日报系统...${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📱 Web界面地址：${GREEN}http://localhost:5002${NC}"
echo -e "${BLUE}⏹️  停止服务：按 ${YELLOW}Ctrl+C${NC}"
echo ""
echo -e "${BLUE}----------------------------------------${NC}"
echo ""

# 使用 start.py 启动（包含环境检查）
if [ -f "start.py" ]; then
    python start.py
else
    # 如果没有 start.py，直接运行 web_app.py
    python web_app.py
fi
