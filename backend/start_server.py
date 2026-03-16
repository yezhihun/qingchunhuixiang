#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动青春回响服务器的正确方式
"""

import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 设置工作目录
os.chdir(current_dir)

# 导入并启动服务器
from server import app, socketio

if __name__ == '__main__':
    print("青春回响服务器启动中...")
    print("WebSocket 服务器地址: ws://localhost:5000")
    print("HTTP API 地址: http://localhost:5000/api")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)