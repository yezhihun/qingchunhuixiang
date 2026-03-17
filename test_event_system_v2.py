#!/usr/bin/env python3
"""
测试事件系统 v2
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from simulation.event_system_v2 import EventSystemV2

def test_event_system():
    """测试事件系统"""
    # 创建测试学生数据
    test_students = [
        {
            'id': 'student_001',
            'name': '张三',
            'current_mood': 'normal',
            'activity_level': 50,
            'focus': 60,
            'stress': 30,
            'motivation': 70,
            'social_energy': 80,
            'academic_score': 75,
            'emotional_stability': 80
        },
        {
            'id': 'student_002', 
            'name': '李四',
            'current_mood': 'happy',
            'activity_level': 70,
            'focus': 55,
            'stress': 20,
            'motivation': 65,
            'social_energy': 90,
            'academic_score': 80,
            'emotional_stability': 85
        }
    ]
    
    # 初始化事件系统
    event_system = EventSystemV2(config_dir='config')
    
    # 获取教室场景的可用事件
    classroom_events = event_system.get_available_events_for_scenario('classroom')
    print(f"教室场景可用事件数量: {len(classroom_events)}")
    
    if classroom_events:
        # 创建事件实例
        event_instance = event_system.create_event_instance(
            classroom_events[0], 
            {'scenario': 'classroom', 'students': test_students}
        )
        print(f"创建事件: {event_instance['name']}")
        print(f"受影响学生: {event_instance['affected_students']}")
        
        # 处理事件效果
        updated_students = event_system.process_event_effects(event_instance, test_students)
        print("事件处理后的学生状态:")
        for student in updated_students:
            print(f"  {student['name']}: mood={student.get('current_mood', 'unknown')}, "
                  f"stress={student.get('stress', 0)}, focus={student.get('focus', 0)}")
    else:
        print("没有找到可用的教室事件")
        print("请检查 config/events.json 配置文件")

if __name__ == "__main__":
    test_event_system()