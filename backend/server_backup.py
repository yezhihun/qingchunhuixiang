#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青春回响 - 后端服务器
使用 Flask + SocketIO 实现实时高中生活模拟游戏服务
"""

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
import eventlet

# 导入广播系统
from .broadcast_system import BroadcastSystem

# 使用 eventlet 作为异步模式
eventlet.monkey_patch()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 Flask 应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-for-youth-echo'
app.config['DATABASE'] = 'youth_echo.db'

# 创建 SocketIO 实例
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 全局变量
scheduler = None

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
        # 插入示例学校
        schools = [
            ('school_001', '第一高中'),
            ('school_002', '第二高中'), 
            ('school_003', '第三高中')
        ]
        cursor.executemany("INSERT INTO schools (id, name) VALUES (?, ?)", schools)
        
        # 插入示例班级
        classes = [
            ('class_001', 'school_001', '高一(1)班'),
            ('class_002', 'school_001', '高一(2)班'),
            ('class_003', 'school_002', '高二(1)班'),
            ('class_004', 'school_003', '高三(1)班')
        ]
        cursor.executemany("INSERT INTO classes (id, school_id, name) VALUES (?, ?, ?)", classes)
        
        # 插入示例学生
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

@socketio.on('leave_class')
def handle_leave_class(data):
    """离开班级房间"""
    class_id = data.get('class_id')
    if class_id:
        leave_room(class_id)
        logger.info(f"用户 {request.sid} 离开班级房间: {class_id}")

def simulate_student_behavior():
    """模拟学生行为（定时任务）"""
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        
        # 更新学生状态
        cursor.execute('''
            UPDATE students 
            SET energy = MAX(0, MIN(100, energy + CAST((RANDOM() % 21) - 10 AS INTEGER))),
                social_points = MAX(0, MIN(100, social_points + CAST((RANDOM() % 11) - 5 AS INTEGER))),
                academic_points = MAX(0, MIN(100, academic_points + CAST((RANDOM() % 11) - 5 AS INTEGER))),
                last_active = CURRENT_TIMESTAMP
        ''')
        
        # 随机生成事件
        cursor.execute('SELECT id, class_id FROM students ORDER BY RANDOM() LIMIT 1')
        student = cursor.fetchone()
        if student:
            student_id, class_id = student
            event_types = ['chat', 'study', 'rest', 'activity']
            event_type = event_types[hash(student_id) % len(event_types)]
            
            cursor.execute('''
                INSERT INTO events (class_id, event_type, description, target_student_id)
                VALUES (?, ?, ?, ?)
            ''', (class_id, event_type, f'学生行为事件: {event_type}', student_id))
            
            # 广播事件到班级房间
            socketio.emit('class_update', {
                'type': 'student_behavior',
                'student_id': student_id,
                'event_type': event_type,
                'timestamp': datetime.now().isoformat()
            }, room=class_id)
        
        conn.commit()
        conn.close()
        logger.info("学生行为模拟完成")
        
    except Exception as e:
        logger.error(f"模拟学生行为出错: {e}")

def start_scheduler():
    """启动定时任务调度器"""
    global scheduler
    if scheduler is None:
        scheduler = BackgroundScheduler()
        # 每30秒模拟一次学生行为
        scheduler.add_job(simulate_student_behavior, 'interval', seconds=30)
        scheduler.start()
        logger.info("定时任务调度器已启动")

def stop_scheduler():
    """停止定时任务调度器"""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
        logger.info("定时任务调度器已停止")

if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
    # 启动定时任务
    start_scheduler()
    
    try:
        # 启动服务器
        logger.info("青春回响服务器启动中...")
        logger.info("WebSocket 服务器地址: ws://localhost:5000")
        logger.info("HTTP API 地址: http://localhost:5000/api")
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        logger.info("服务器正在关闭...")
    finally:
        stop_scheduler()