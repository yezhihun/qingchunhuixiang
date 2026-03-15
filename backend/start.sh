#!/bin/bash

# 安装依赖
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# 初始化数据库
echo "Initializing database..."
python3 init_db.py

# 启动服务器
echo "Starting server..."
python3 server.py