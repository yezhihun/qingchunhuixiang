"""
青春回响 - 后端API
包含班级、学生、事件、夜间、回放等核心接口
"""
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit, join_room
import json
import os
from datetime import datetime, timedelta
from .simulation.event_system import EventSystem
from .simulation.student_behavior import StudentBehavior  
from .simulation.night_system import NightSystem
from .simulation.replay_system import ReplaySystem

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 初始化系统
event_system = EventSystem()
night_system = NightSystem()
replay_system = ReplaySystem()

# 加载MVP学生数据
def load_mvp_students():
    students_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'mvp_students.json')
    try:
        with open(students_file, 'r', encoding='utf-8') as f:
            return json.load(f)['students']
    except FileNotFoundError:
        # 返回默认学生数据
        return [
            {
                "id": "student_001",
                "name": "李明",
                "age": 16,
                "gender": "male",
                "personality": {"extroversion": 0.3, "agreeableness": 0.7, "conscientiousness": 0.8},
                "attributes": {"academic_score": 85, "social_skills": 60, "energy": 75},
                "background": {"family_background": "普通家庭", "academic_history": "理科优秀"},
                "current_mood": "neutral"
            }
        ]

STUDENTS = load_mvp_students()

@app.route('/api/classes/<class_id>')
def get_class(class_id):
    """获取班级信息"""
    return jsonify([{"id": class_id, "name": "高一(1)班", "student_count": len(STUDENTS)}])

@app.route('/api/students/<class_id>')
def get_students(class_id):
    """获取班级学生列表"""
    return jsonify(STUDENTS)

@app.route('/api/students/<student_id>')
def get_student(student_id):
    """获取单个学生详情"""
    student = next((s for s in STUDENTS if s["id"] == student_id), None)
    if student:
        return jsonify(student)
    return jsonify({"error": "Student not found"}), 404

@app.route('/api/interaction', methods=['POST'])
def handle_interaction():
    """处理玩家互动"""
    data = request.json
    student_id = data.get('studentId')
    action = data.get('action')
    
    # 找到对应学生并应用互动效果
    for student in STUDENTS:
        if student["id"] == student_id:
            # 简单的互动效果应用
            if action == "encourage":
                student["attributes"]["motivation"] = min(100, student["attributes"].get("motivation", 50) + 20)
                student["current_mood"] = "happy"
            elif action == "comfort":
                student["attributes"]["stress"] = max(0, student["attributes"].get("stress", 30) - 15)
                student["current_mood"] = "calm"
            elif action == "guide":
                student["attributes"]["academic_score"] = min(100, student["attributes"].get("academic_score", 70) + 5)
            
            # 通过WebSocket通知前端更新
            socketio.emit('student_update', {
                'student_id': student_id,
                'updates': student
            }, room=f"class_{data.get('classId', 'default')}")
            
            return jsonify({"success": True})
    
    return jsonify({"success": False, "error": "Student not found"}), 404

@app.route('/api/night/events')
def get_night_events():
    """获取夜间事件"""
    current_time = datetime.now().strftime('%H:%M')
    if '22' <= current_time[:2] or current_time[:2] < '06':
        # 夜间时段返回夜间事件
        night_events = night_system.get_current_night_events(STUDENTS)
        return jsonify(night_events)
    else:
        return jsonify([])

@app.route('/api/replay/<replay_type>')
def get_replay(replay_type):
    """获取回放数据"""
    replay_data = replay_system.generate_replay(replay_type, STUDENTS)
    return jsonify(replay_data)

@socketio.on('join_class')
def on_join_class(data):
    """加入班级房间"""
    class_id = data['class_id']
    join_room(f"class_{class_id}")
    
    # 发送当前班级状态
    emit('class_update', {
        'students': STUDENTS,
        'timeInfo': {
            'day': datetime.now().day,
            'period': get_current_period(),
            'time': datetime.now().strftime('%H:%M')
        }
    })

@socketio.on('connect')
def on_connect():
    print('Client connected')

@socketio.on('disconnect')
def on_disconnect():
    print('Client disconnected')

def get_current_period():
    """获取当前时段"""
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return '上午'
    elif 12 <= hour < 18:
        return '下午'
    elif 18 <= hour < 22:
        return '晚上'
    else:
        return '深夜'

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)