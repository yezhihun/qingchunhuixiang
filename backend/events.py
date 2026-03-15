#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
青春回响 - WebSocket事件处理器
处理客户端连接、消息和广播
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from backend.models import db, Student, ClassRoom, Event
from backend.simulation import SimulationSystem
import logging

logger = logging.getLogger(__name__)

def init_socket_events(socketio, app):
    """初始化WebSocket事件处理器"""
    
    @socketio.on('connect')
    def handle_connect():
        """处理客户端连接"""
        logger.info(f"Client connected: {request.sid}")
        emit('connection_response', {'status': 'connected'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """处理客户端断开连接"""
        logger.info(f"Client disconnected: {request.sid}")
    
    @socketio.on('join_class')
    def handle_join_class(data):
        """处理加入班级请求"""
        class_id = data.get('class_id')
        if not class_id:
            emit('error', {'message': 'Missing class_id'})
            return
        
        # 加入班级房间
        join_room(f"class_{class_id}")
        
        # 获取班级信息
        classroom = ClassRoom.query.get(class_id)
        if classroom:
            students = Student.query.filter_by(class_id=class_id).all()
            emit('class_data', {
                'classroom': classroom.to_dict(),
                'students': [s.to_dict() for s in students]
            })
        else:
            emit('error', {'message': 'Class not found'})
    
    @socketio.on('get_student')
    def handle_get_student(data):
        """获取学生详情"""
        student_id = data.get('student_id')
        student = Student.query.get(student_id)
        if student:
            emit('student_data', student.to_dict())
        else:
            emit('error', {'message': 'Student not found'})
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """处理发送消息"""
        sender_id = data.get('sender_id')
        target_id = data.get('target_id')
        message = data.get('message')
        
        if not all([sender_id, target_id, message]):
            emit('error', {'message': 'Missing required fields'})
            return
        
        # 保存消息到数据库（如果需要）
        # 这里可以添加消息处理逻辑
        
        # 广播给目标学生
        emit('new_message', {
            'sender_id': sender_id,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }, room=f"student_{target_id}")
    
    @socketio.on('trigger_event')
    def handle_trigger_event(data):
        """触发游戏事件"""
        event_type = data.get('event_type')
        class_id = data.get('class_id')
        
        if not event_type or not class_id:
            emit('error', {'message': 'Missing event_type or class_id'})
            return
        
        # 触发模拟系统事件
        simulation = SimulationSystem.get_instance()
        result = simulation.trigger_event(event_type, class_id)
        
        # 广播事件结果
        emit('event_result', result, room=f"class_{class_id}")
