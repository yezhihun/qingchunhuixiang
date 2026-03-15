from flask import Blueprint, jsonify, request
from .models import db, School, Classroom, Student, Event
from .events import broadcast_class_update, broadcast_event_notification

api = Blueprint('api', __name__)

@api.route('/schools', methods=['GET'])
def get_schools():
    """获取所有学校列表"""
    schools = School.query.all()
    return jsonify([{
        'id': school.id,
        'name': school.name,
        'classes_count': len(school.classrooms),
        'students_count': sum(len(cls.students) for cls in school.classrooms)
    } for school in schools])

@api.route('/classrooms/<school_id>', methods=['GET'])
def get_classrooms(school_id):
    """获取指定学校的班级列表"""
    classrooms = Classroom.query.filter_by(school_id=school_id).all()
    return jsonify([{
        'id': cls.id,
        'name': cls.name,
        'grade': cls.grade,
        'students_count': len(cls.students)
    } for cls in classrooms])

@api.route('/students/<classroom_id>', methods=['GET'])
def get_students(classroom_id):
    """获取指定班级的学生列表"""
    students = Student.query.filter_by(classroom_id=classroom_id).all()
    return jsonify([{
        'id': student.id,
        'name': student.name,
        'avatar': student.avatar,
        'mood': student.mood,
        'energy': student.energy,
        'relationships': student.relationships,
        'skills': student.skills,
        'personality': student.personality
    } for student in students])

@api.route('/student/<student_id>', methods=['GET'])
def get_student(student_id):
    """获取指定学生的详细信息"""
    student = Student.query.get_or_404(student_id)
    return jsonify({
        'id': student.id,
        'name': student.name,
        'avatar': student.avatar,
        'mood': student.mood,
        'energy': student.energy,
        'relationships': student.relationships,
        'skills': student.skills,
        'personality': student.personality,
        'classroom_id': student.classroom_id,
        'school_id': student.school_id
    })

@api.route('/events/<classroom_id>', methods=['GET'])
def get_events(classroom_id):
    """获取指定班级的事件列表"""
    events = Event.query.filter_by(classroom_id=classroom_id).order_by(Event.created_at.desc()).limit(20).all()
    return jsonify([{
        'id': event.id,
        'type': event.type,
        'title': event.title,
        'description': event.description,
        'student_ids': event.student_ids,
        'created_at': event.created_at.isoformat(),
        'priority': event.priority
    } for event in events])

@api.route('/interact', methods=['POST'])
def interact_with_student():
    """与学生互动"""
    data = request.json
    student_id = data.get('student_id')
    interaction_type = data.get('type')  # 'talk', 'help', 'gift', etc.
    
    # 这里会调用AI模拟系统来处理互动
    # 暂时返回模拟响应
    response_data = {
        'success': True,
        'message': f'成功与学生互动 ({interaction_type})',
        'student_id': student_id,
        'new_mood': 'happy',
        'relationship_change': 5
    }
    
    # 广播更新
    broadcast_class_update(student_id)
    
    return jsonify(response_data)

@api.route('/initialize_demo', methods=['POST'])
def initialize_demo_data():
    """初始化演示数据"""
    from .models import init_demo_data
    init_demo_data()
    return jsonify({'success': True, 'message': '演示数据初始化完成'})