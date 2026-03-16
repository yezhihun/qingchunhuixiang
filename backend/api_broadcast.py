"""
青春回响 - 广播系统API
提供校园广播黄金时段的相关接口
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, time
import json
from .simulation.broadcast_system import BroadcastSystem

# 创建广播API蓝图
broadcast_bp = Blueprint('broadcast', __name__)
broadcast_system = BroadcastSystem()

@broadcast_bp.route('/api/broadcast/current', methods=['GET'])
def get_current_broadcast():
    """获取当前广播内容"""
    try:
        current_time = datetime.now().time()
        broadcast_data = broadcast_system.get_current_program(current_time)
        
        return jsonify({
            'success': True,
            'data': broadcast_data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broadcast_bp.route('/api/broadcast/schedule', methods=['GET'])
def get_broadcast_schedule():
    """获取广播时间表"""
    try:
        schedule = broadcast_system.get_daily_schedule()
        return jsonify({
            'success': True,
            'data': schedule,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broadcast_bp.route('/api/broadcast/student-activities', methods=['GET'])
def get_student_activities():
    """获取学生实时活动"""
    try:
        class_id = request.args.get('class_id', 'class_001')
        activities = broadcast_system.get_student_activities(class_id)
        
        return jsonify({
            'success': True,
            'data': activities,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@broadcast_bp.route('/api/broadcast/classic-scenes', methods=['GET'])
def get_classic_scenes():
    """获取经典剧情场景"""
    try:
        scenes = broadcast_system.get_classic_scenes()
        return jsonify({
            'success': True,
            'data': scenes,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# WebSocket事件处理
def handle_broadcast_update(socketio):
    """处理广播更新事件"""
    @socketio.on('request_broadcast_update')
    def on_broadcast_request(data):
        class_id = data.get('class_id', 'class_001')
        current_time = datetime.now().time()
        
        # 获取当前广播内容
        current_program = broadcast_system.get_current_program(current_time)
        student_activities = broadcast_system.get_student_activities(class_id)
        classic_scenes = broadcast_system.get_classic_scenes()
        
        # 广播更新到所有连接的客户端
        socketio.emit('broadcast_update', {
            'current_program': current_program,
            'student_activities': student_activities,
            'classic_scenes': classic_scenes,
            'timestamp': datetime.now().isoformat()
        }, room=class_id)