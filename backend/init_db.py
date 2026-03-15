#!/usr/bin/env python3
"""
Database initialization script for 青春回响 game.
Creates tables and inserts initial data.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, Student, Class, School, Skill, Event
from simulation.student_behavior import StudentGenerator

def init_database():
    """Initialize database with tables and sample data."""
    print("Initializing database...")
    
    # Create all tables
    db.create_all()
    print("✓ Tables created")
    
    # Insert sample schools
    schools = [
        {'id': 'school_001', 'name': '第一高中', 'location': '北京市朝阳区'},
        {'id': 'school_002', 'name': '第二高中', 'location': '上海市浦东新区'},
        {'id': 'school_003', 'name': '第三高中', 'location': '广州市天河区'}
    ]
    
    for school_data in schools:
        school = School(**school_data)
        db.session.add(school)
    
    db.session.commit()
    print("✓ Sample schools added")
    
    # Insert sample classes
    classes = [
        {'id': 'class_001', 'school_id': 'school_001', 'grade': 10, 'name': '高一(1)班'},
        {'id': 'class_002', 'school_id': 'school_001', 'grade': 10, 'name': '高一(2)班'},
        {'id': 'class_003', 'school_id': 'school_002', 'grade': 11, 'name': '高二(1)班'},
        {'id': 'class_004', 'school_id': 'school_003', 'grade': 12, 'name': '高三(1)班'}
    ]
    
    for class_data in classes:
        class_obj = Class(**class_data)
        db.session.add(class_obj)
    
    db.session.commit()
    print("✓ Sample classes added")
    
    # Generate AI students
    print("Generating AI students...")
    generator = StudentGenerator()
    
    # Add students to each class
    for class_obj in Class.query.all():
        students = generator.generate_students_for_class(class_obj.id, 25)
        for student in students:
            db.session.add(student)
    
    db.session.commit()
    print("✓ AI students generated")
    
    # Insert sample skills
    skills = [
        {'name': '学习能力', 'category': 'academic', 'description': '影响学习成绩和知识获取速度'},
        {'name': '社交能力', 'category': 'social', 'description': '影响人际关系和社交活动'},
        {'name': '运动能力', 'category': 'physical', 'description': '影响体育成绩和身体素质'},
        {'name': '艺术天赋', 'category': 'artistic', 'description': '影响艺术类活动表现'},
        {'name': '领导力', 'category': 'leadership', 'description': '影响班级管理和组织能力'}
    ]
    
    for skill_data in skills:
        skill = Skill(**skill_data)
        db.session.add(skill)
    
    db.session.commit()
    print("✓ Sample skills added")
    
    print("Database initialization completed successfully!")

if __name__ == '__main__':
    init_database()