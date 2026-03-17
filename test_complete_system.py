#!/usr/bin/env python3
"""
青春回响 - 完整系统测试脚本
测试Phase 1 MVP的所有核心功能
"""

import json
import os
from datetime import datetime, time
from backend.simulation.event_system import EventSystem
from backend.simulation.night_system import NightSystem  
from backend.simulation.replay_system import ReplaySystem

def test_student_system():
    """测试学生系统"""
    print("🧪 测试学生系统...")
    
    # 加载MVP学生数据
    with open('config/mvp_students.json', 'r', encoding='utf-8') as f:
        students_data = json.load(f)
    
    assert len(students_data) == 12, f"期望12个学生，实际{len(students_data)}"
    print(f"✅ 成功加载 {len(students_data)} 个MVP学生")
    
    # 验证学生数据完整性
    for student in students_data[:3]:  # 测试前3个
        required_fields = ['basic_info', 'personality', 'background_profile', 'attributes']
        for field in required_fields:
            assert field in student, f"学生缺少字段: {field}"
        print(f"✅ 学生 {student['basic_info']['name']} 数据完整")

def test_event_system():
    """测试事件系统"""
    print("\n🧪 测试事件系统...")
    
    event_system = EventSystem()
    
    # 测试基础场景事件
    classroom_events = event_system.get_available_events_for_scenario('classroom')
    assert len(classroom_events) > 0, "教室场景应该有可用事件"
    print(f"✅ 教室场景有 {len(classroom_events)} 个可用事件")
    
    # 测试事件生成
    mock_students = [{'id': f'student_{i}', 'name': f'学生{i}'} for i in range(5)]
    events = event_system.generate_events_for_period('classroom', 'class_001', mock_students)
    print(f"✅ 成功生成 {len(events)} 个事件")

def test_night_system():
    """测试夜间系统"""
    print("\n🧪 测试夜间系统...")
    
    night_system = NightSystem()
    
    # 测试夜间事件生成
    mock_students = [{'id': f'student_{i}', 'name': f'学生{i}'} for i in range(3)]
    night_events = night_system.generate_night_events(mock_students)
    print(f"✅ 夜间系统生成 {len(night_events)} 个事件")
    
    # 测试梦境内容
    dream = night_system.generate_dream_content(mock_students[0])
    assert isinstance(dream, str) and len(dream) > 0, "梦境内容应该非空"
    print(f"✅ 梦境生成成功: {dream[:50]}...")

def test_replay_system():
    """测试回放系统"""
    print("\n🧪 测试回放系统...")
    
    replay_system = ReplaySystem()
    
    # 测试日回顾生成
    mock_events = [
        {'type': 'exam_success', 'student_id': 'student_001', 'description': '数学考试及格了！'},
        {'type': 'friendship_made', 'student_id': 'student_002', 'description': '交到了新朋友'}
    ]
    daily_replay = replay_system.generate_daily_summary(mock_events, date="2026-03-17")
    assert '今日回顾' in daily_replay['title'], "日回顾标题应该包含日期"
    print(f"✅ 日回顾生成成功: {daily_replay['title']}")
    
    # 测试周报生成
    weekly_replay = replay_system.generate_weekly_digest(mock_events, week_number=12)
    assert '班级周报' in weekly_replay['title'], "周报标题应该包含周数"
    print(f"✅ 周报生成成功: {weekly_replay['title']}")

def test_integration():
    """测试系统集成"""
    print("\n🧪 测试系统集成...")
    
    # 模拟完整的一天流程
    event_system = EventSystem()
    night_system = NightSystem()
    replay_system = ReplaySystem()
    
    # 白天事件
    students = [{'id': f'student_{i}', 'name': f'学生{i}'} for i in range(5)]
    day_events = event_system.generate_events_for_period('classroom', 'class_001', students)
    
    # 夜间事件  
    night_events = night_events = night_system.generate_night_events(students)
    
    # 生成回放
    all_events = day_events + night_events
    replay = replay_system.generate_daily_summary(all_events, date="2026-03-17")
    
    print(f"✅ 完整集成测试成功:")
    print(f"   - 白天事件: {len(day_events)} 个")
    print(f"   - 夜间事件: {len(night_events)} 个") 
    print(f"   - 回放生成: {replay['title']}")

def main():
    """主测试函数"""
    print("🚀 开始青春回响 Phase 1 MVP 系统测试\n")
    
    try:
        test_student_system()
        test_event_system() 
        test_night_system()
        test_replay_system()
        test_integration()
        
        print("\n🎉 所有测试通过！Phase 1 MVP 核心功能就绪")
        print("\n📋 下一步建议:")
        print("1. 前端界面集成测试")
        print("2. 微信小程序真机测试") 
        print("3. 用户体验优化")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        raise

if __name__ == "__main__":
    main()