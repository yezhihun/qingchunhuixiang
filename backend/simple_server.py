#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青春回响 - 简化版后端服务器
单文件架构，避免模块导入问题
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
import random
import threading
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 Flask 应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-for-youth-echo'
app.config['DATABASE'] = 'youth_echo.db'

# 创建 SocketIO 实例
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ==================== 核心事件模板 ====================
CORE_EVENT_TEMPLATES = {
    # 课堂相关事件
    "classroom_quiz": {
        "name": "突然小测验",
        "description": "数学老师突然宣布进行10分钟小测验",
        "category": "academic",
        "probability": 0.25,
        "time_slots": ["08:00-12:00", "14:00-17:30"],
        "effects": {
            "stress": "+15",
            "academic_focus": "+10",
            "energy": "-5"
        }
    },
    "classroom_teacher_praise": {
        "name": "老师表扬",
        "description": "语文老师表扬了你的作文写得很好",
        "category": "academic",
        "probability": 0.2,
        "time_slots": ["08:00-12:00", "14:00-17:30"],
        "effects": {
            "mood": "happy",
            "confidence": "+20",
            "social_status": "+10"
        }
    },
    # 课间休息事件
    "break_time_gossip": {
        "name": "八卦传播",
        "description": "听说隔壁班的学霸和校花在交往",
        "category": "social",
        "probability": 0.3,
        "time_slots": ["10:00-10:20", "15:30-15:50"],
        "effects": {
            "social_activity": "+15",
            "gossip_level": "+10"
        }
    },
    "break_time_study_group": {
        "name": "学习小组",
        "description": "几个同学在讨论物理难题",
        "category": "academic",
        "probability": 0.25,
        "time_slots": ["10:00-10:20", "15:30-15:50", "19:30-21:30"],
        "effects": {
            "academic_knowledge": "+10",
            "friendship": "+15",
            "energy": "-5"
        }
    },
    # 午餐时间事件
    "lunch_cafeteria_meeting": {
        "name": "食堂偶遇",
        "description": "在食堂排队时遇到了暗恋的同学",
        "category": "social",
        "probability": 0.2,
        "time_slots": ["12:00-13:00"],
        "effects": {
            "heart_rate": "+20",
            "nervousness": "+15",
            "social_courage": "+10"
        }
    },
    "lunch_food_sharing": {
        "name": "分享午餐",
        "description": "同桌带了妈妈做的好吃的便当，分给你一些",
        "category": "social",
        "probability": 0.15,
        "time_slots": ["12:00-13:00"],
        "effects": {
            "happiness": "+20",
            "friendship": "+25",
            "energy": "+10"
        }
    },
    # 下午活动事件
    "afternoon_sports": {
        "name": "篮球训练",
        "description": "放学后和朋友一起打篮球",
        "category": "physical",
        "probability": 0.2,
        "time_slots": ["17:30-19:00"],
        "effects": {
            "physical_fitness": "+15",
            "energy": "-20",
            "friendship": "+20"
        }
    },
    "afternoon_library": {
        "name": "图书馆自习",
        "description": "在图书馆安静地复习功课",
        "category": "academic",
        "probability": 0.25,
        "time_slots": ["17:30-19:00"],
        "effects": {
            "academic_knowledge": "+20",
            "focus": "+25",
            "energy": "-15"
        }
    },
    # 晚自习事件
    "evening_confession": {
        "name": "晚自习告白",
        "description": "晚自习结束后，有人递给你一封情书",
        "category": "romantic",
        "probability": 0.1,
        "time_slots": ["21:30-22:00"],
        "effects": {
            "emotional_turbulence": "+30",
            "heart_rate": "+25",
            "sleep_quality": "-10"
        }
    },
    "evening_homework_help": {
        "name": "作业互助",
        "description": "同桌帮你解答了一道很难的数学题",
        "category": "academic",
        "probability": 0.3,
        "time_slots": ["19:30-21:30"],
        "effects": {
            "academic_understanding": "+25",
            "gratitude": "+20",
            "friendship": "+15"
        }
    }
}

# ==================== 数据库初始化 ====================
def init_database():
    """初始化数据库"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # 创建学校表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schools (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建班级表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS classes (
            id TEXT PRIMARY KEY,
            school_id TEXT NOT NULL,
            name TEXT NOT NULL,
            student_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (school_id) REFERENCES schools (id)
        )
    ''')
    
    # 创建学生表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            class_id TEXT NOT NULL,
            name TEXT NOT NULL,
            avatar TEXT,
            mood TEXT DEFAULT 'normal',
            energy INTEGER DEFAULT 100,
            social_points INTEGER DEFAULT 50,
            academic_points INTEGER DEFAULT 50,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES classes (id)
        )
    ''')
    
    # 创建事件表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            description TEXT,
            target_student_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES classes (id),
            FOREIGN KEY (target_student_id) REFERENCES students (id)
        )
    ''')
    
    # 插入示例数据
    cursor.execute("SELECT COUNT(*) FROM schools")
    if cursor.fetchone()[0] == 0:
        schools = [
            ('school_001', '第一高中'),
            ('school_002', '第二高中'), 
            ('school_003', '第三高中')
        ]
        cursor.executemany("INSERT INTO schools (id, name) VALUES (?, ?)", schools)
        
        classes = [
            ('class_001', 'school_001', '高一(1)班'),
            ('class_002', 'school_001', '高一(2)班'),
            ('class_003', 'school_002', '高二(1)班'),
            ('class_004', 'school_003', '高三(1)班')
        ]
        cursor.executemany("INSERT INTO classes (id, school_id, name) VALUES (?, ?, ?)", classes)
        
        students = [
            ('student_001', 'class_001', '李明', '/assets/avatars/student1.png'),
            ('student_002', 'class_001', '王芳', '/assets/avatars/student2.png'),
            ('student_003', 'class_001', '张伟', '/assets/avatars/student3.png'),
            ('student_004', 'class_002', '刘洋', '/assets/avatars/student4.png'),
            ('student_005', 'class_002', '陈静', '/assets/avatars/student5.png')
        ]
        cursor.executemany("INSERT INTO students (id, class_id, name, avatar) VALUES (?, ?, ?, ?)", students)
    
    conn.commit()
    conn.close()
    logger.info("数据库初始化完成")

# ==================== API路由 ====================
@app.route('/api/schools')
def get_schools():
    """获取学校列表"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.id, s.name, 
               COUNT(c.id) as class_count,
               COALESCE(SUM(c.student_count), 0) as total_students
        FROM schools s
        LEFT JOIN classes c ON s.id = c.school_id
        GROUP BY s.id, s.name
    ''')
    schools = []
    for row in cursor.fetchall():
        schools.append({
            'id': row[0],
            'name': row[1],
            'classes': row[2],
            'students': row[3]
        })
    conn.close()
    return jsonify(schools)

@app.route('/api/classes/<school_id>')
def get_classes(school_id):
    """获取指定学校的班级列表"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, student_count 
        FROM classes 
        WHERE school_id = ?
    ''', (school_id,))
    classes = []
    for row in cursor.fetchall():
        classes.append({
            'id': row[0],
            'name': row[1],
            'student_count': row[2]
        })
    conn.close()
    return jsonify(classes)

@app.route('/api/students/<class_id>')
def get_students(class_id):
    """获取班级学生列表"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, avatar, mood, energy, social_points, academic_points, last_active
        FROM students 
        WHERE class_id = ?
        ORDER BY name
    ''', (class_id,))
    students = []
    for row in cursor.fetchall():
        students.append({
            'id': row[0],
            'name': row[1],
            'avatar': row[2],
            'mood': row[3],
            'energy': row[4],
            'social_points': row[5],
            'academic_points': row[6],
            'last_active': row[7]
        })
    conn.close()
    return jsonify(students)

# ==================== WebSocket处理 ====================
@socketio.on('connect')
def handle_connect():
    """处理客户端连接"""
    logger.info(f"客户端连接: {request.sid}")
    emit('connected', {'message': 'Connected to Youth Echo server'})

@socketio.on('disconnect')
def handle_disconnect():
    """处理客户端断开"""
    logger.info(f"客户端断开: {request.sid}")

@socketio.on('join_class')
def handle_join_class(data):
    """加入班级房间"""
    class_id = data.get('class_id')
    if class_id:
        join_room(class_id)
        logger.info(f"用户 {request.sid} 加入班级房间: {class_id}")
        
        # 发送当前班级状态
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM classes WHERE id = ?', (class_id,))
        class_info = cursor.fetchone()
        if class_info:
            emit('class_joined', {
                'class_id': class_id,
                'class_name': class_info[0]
            }, room=request.sid)
        conn.close()

# ==================== 主函数 ====================
if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
    try:
        # 启动服务器
        logger.info("青春回响简化版服务器启动中...")
        logger.info("WebSocket 服务器地址: ws://localhost:5000")
        logger.info("HTTP API 地址: http://localhost:5000/api")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        logger.info("服务器正在关闭...")