#!/bin/bash

# 确保脚本在错误时退出
set -e

echo "开始部署HEIC链接转图片服务..."

# 创建所需目录
mkdir -p data
mkdir -p uploads
mkdir -p outputs
echo "已创建必要目录"

# 检查Docker是否已安装
if ! command -v docker &> /dev/null; then
    echo "Docker未安装，正在安装..."
    # 安装Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    echo "Docker安装完成"
else
    echo "Docker已安装"
fi

# 检查Docker Compose是否已安装
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose未安装，正在安装..."
    # 安装Docker Compose
    curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "Docker Compose安装完成"
else
    echo "Docker Compose已安装"
fi

# 赋予当前用户执行权限
chmod +x /usr/local/bin/docker-compose 2>/dev/null || true

# 构建并启动服务
echo "构建并启动服务..."
docker-compose up -d --build
echo "构建完成"

# 获取服务器IP地址（兼容不同操作系统）
SERVER_IP="localhost"
OS_TYPE=$(uname -s)
if [ "$OS_TYPE" = "Linux" ]; then
    # Linux系统
    SERVER_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")
elif [ "$OS_TYPE" = "Darwin" ]; then
    # macOS系统
    SERVER_IP=$(ipconfig getifaddr en0 2>/dev/null || echo "localhost")
fi

echo ""
echo "部署完成！"
echo "-------------------------------------------"
echo "Web服务已启动！"
echo "访问地址: http://${SERVER_IP}:5010"
echo ""
echo "您可以执行以下命令管理服务："
echo "  - 查看日志: docker-compose logs -f"
echo "  - 停止服务: docker-compose down"
echo "  - 重启服务: docker-compose restart"
echo "-------------------------------------------"
echo "" 