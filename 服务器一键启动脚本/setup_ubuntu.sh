#!/bin/bash

# Ubuntu 24.04 环境搭建脚本
# 用于部署 CreditHourSystem 项目

set -e  # 遇到错误立即退出

echo "========================================="
echo "开始 Ubuntu 24.04 环境搭建"
echo "========================================="

# 更新系统包
echo ">>> 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 安装必要的工具
echo ">>> 安装必要工具..."
sudo apt install -y git python3 python3-pip python3-venv nginx

# 安装 PostgreSQL
echo ">>> 安装 PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

# 启动 PostgreSQL 服务
echo ">>> 启动 PostgreSQL 服务..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 配置 PostgreSQL
echo ">>> 配置 PostgreSQL..."
# 设置 postgres 用户密码
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'password';"

# 检查数据库是否存在
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw credithoursystem; then
    echo "数据库 credithoursystem 已存在，跳过创建"
else
    echo ">>> 创建数据库 credithoursystem..."
    sudo -u postgres psql -c "CREATE DATABASE credithoursystem;"
fi

echo ">>> PostgreSQL 配置完成"

# 克隆项目到 /opt 目录
echo ">>> 克隆项目到 /opt 目录..."
cd /opt
if [ -d "CreditHourSystem" ]; then
    echo "项目目录已存在，删除旧目录..."
    sudo rm -rf CreditHourSystem
fi

# 配置 Git 超时时间
git config --global http.connectTimeout 30
git config --global http.lowSpeedLimit 1000
git config --global http.lowSpeedTime 60

# 尝试从 GitHub 克隆
echo ">>> 尝试从 GitHub 克隆项目..."
if sudo git clone https://github.com/UPCInnovationTeam/CreditHourSystem.git; then
    echo "GitHub 克隆成功"
else
    echo "GitHub 克隆失败，尝试从 Gitee 镜像克隆..."
    if sudo git clone https://gitee.com/sudaowan/CreditHourSystem.git; then
        echo "Gitee 克隆成功"
    else
        echo "错误: 项目克隆失败，请检查网络连接"
        exit 1
    fi
fi

sudo chown -R $USER:$USER /opt/CreditHourSystem

# 进入 httpServer 目录
echo ">>> 进入 httpServer 目录..."
cd /opt/CreditHourSystem/httpServer

# 创建 Python 虚拟环境
echo ">>> 创建 Python 虚拟环境..."
python3 -m venv venv

# 激活虚拟环境并安装依赖
echo ">>> 安装项目依赖..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# 安装额外必需的依赖（处理文件上传）
pip install python-multipart
deactivate

# 修复 Python 3.12 兼容性问题
echo ">>> 修复 Python 3.12 兼容性问题..."
# 修复 deprecated 导入问题（warnings -> typing_extensions）
find /opt/CreditHourSystem/httpServer/app -name "*.py" -exec sed -i 's/from warnings import deprecated/from typing_extensions import deprecated/g' {} \;

# 复制配置文件
echo ">>> 复制配置文件到 app/core 目录..."
# config.py 位置: /opt/config.py
if [ -f "/opt/config.py" ]; then
    # 创建目标目录（如果不存在）
    sudo mkdir -p /opt/CreditHourSystem/httpServer/app/core
    # 复制配置文件
    sudo cp /opt/config.py /opt/CreditHourSystem/httpServer/app/core/config.py
    # 设置正确的权限
    sudo chown $USER:$USER /opt/CreditHourSystem/httpServer/app/core/config.py
    echo "配置文件已复制至: /opt/CreditHourSystem/httpServer/app/core/config.py"
else
    echo "错误: /opt/config.py 未找到"
    exit 1
fi

# 创建 systemd 服务文件
echo ">>> 创建 systemd 服务..."
sudo tee /etc/systemd/system/credithoursystem.service > /dev/null <<EOF
[Unit]
Description=Credit Hour System API Server
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/CreditHourSystem/httpServer
Environment="PATH=/opt/CreditHourSystem/httpServer/venv/bin"
ExecStart=/opt/CreditHourSystem/httpServer/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd 配置
echo ">>> 重新加载 systemd 配置..."
sudo systemctl daemon-reload

# 启用并启动服务
echo ">>> 启用并启动 credithoursystem 服务..."
sudo systemctl enable credithoursystem
sudo systemctl start credithoursystem

# 等待服务启动
sleep 3

# 检查服务状态
echo ">>> 检查服务状态..."
sudo systemctl status credithoursystem --no-pager

# 配置 Nginx 反向代理
echo ">>> 配置 Nginx 反向代理..."
# 创建 Nginx 配置文件
NGINX_CONFIG=$(cat <<'NGINX_EOF'
server {
    listen 80;
    server_name _;

    # 安全头部
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # 客户端最大请求体大小
    client_max_body_size 50M;

    # 代理到后端服务
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        
        # 转发真实客户端信息
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲区设置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }

    # 访问日志
    access_log /var/log/nginx/credithoursystem_access.log;
    error_log /var/log/nginx/credithoursystem_error.log;
}
NGINX_EOF
)

# 写入 Nginx 配置文件
sudo bash -c "echo '$NGINX_CONFIG' > /etc/nginx/sites-available/credithoursystem"

# 创建软链接启用站点
echo ">>> 启用 Nginx 站点配置..."
sudo ln -sf /etc/nginx/sites-available/credithoursystem /etc/nginx/sites-enabled/

# 删除默认站点配置
if [ -f /etc/nginx/sites-enabled/default ]; then
    sudo rm /etc/nginx/sites-enabled/default
fi

# 测试 Nginx 配置
echo ">>> 测试 Nginx 配置..."
sudo nginx -t

# 重启 Nginx 服务
echo ">>> 重启 Nginx 服务..."
sudo systemctl restart nginx
sudo systemctl enable nginx

# 配置防火墙（如果安装了 ufw）
if command -v ufw &> /dev/null; then
    echo ">>> 配置防火墙规则..."
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw allow 22/tcp
    echo "防火墙规则已添加（需要手动启用 ufw）"
fi

# 等待服务启动
sleep 2

# 检查 Nginx 状态
echo ">>> 检查 Nginx 状态..."
sudo systemctl status nginx --no-pager

echo ""
echo "========================================="
echo "环境搭建完成！"
echo "========================================="
echo ""
echo "服务信息："
echo "  - 外部访问地址: http://服务器IP"
echo "  - API 文档: http://服务器IP/docs"
echo "  - Nginx 端口: 80"
echo "  - 后端 API 端口: 8000 (仅内部访问)"
echo "  - 数据库名: credithoursystem"
echo "  - 数据库用户: postgres"
echo "  - 数据库密码: password"
echo ""
echo "安全特性："
echo "  ✓ Nginx 反向代理隐藏后端端口"
echo "  ✓ 添加安全 HTTP 头部"
echo "  ✓ 限制请求体大小（50MB）"
echo "  ✓ 转发真实客户端 IP"
echo "  ✓ WebSocket 支持"
echo ""
echo "已安装的关键依赖："
echo "  ✓ Python 虚拟环境"
echo "  ✓ FastAPI + Uvicorn"
echo "  ✓ python-multipart（文件上传）"
echo "  ✓ PostgreSQL 驱动"
echo ""
echo "常用命令："
echo "  - 查看后端服务状态: sudo systemctl status credithoursystem"
echo "  - 查看 Nginx 状态: sudo systemctl status nginx"
echo "  - 重启后端服务: sudo systemctl restart credithoursystem"
echo "  - 重启 Nginx: sudo systemctl restart nginx"
echo "  - 查看后端日志: sudo journalctl -u credithoursystem -f"
echo "  - 查看 Nginx 访问日志: sudo tail -f /var/log/nginx/credithoursystem_access.log"
echo "  - 查看 Nginx 错误日志: sudo tail -f /var/log/nginx/credithoursystem_error.log"
echo ""
echo "提示："
echo "  - 后端服务监听在 127.0.0.1:8000，仅本地访问"
echo "  - 外部请求通过 Nginx 80 端口访问"
echo "  - 如需启用防火墙: sudo ufw enable"
echo "  - 配置文件位置: /opt/CreditHourSystem/httpServer/app/core/config.py"
echo ""
