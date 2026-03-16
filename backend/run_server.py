#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青春回响 - 服务器启动脚本
直接运行此文件启动后端服务
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    try:
        from server import app, socketio
        print("青春回响服务器启动中...")
        print("HTTP API: http://localhost:5000/api")
        print("WebSocket: ws://localhost:5000")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"服务器启动失败: {e}")
        sys.exit(1)