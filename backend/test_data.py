#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据生成脚本
"""

from models import db, Student, Class, School
from simulation.student_behavior import StudentPersonality
import random

def generate_test_data():
    """生成测试数据"""
    # 创建学校
    school1 = School(name="第一高中", location="市中心")
    school2 = School(name="第二高中", location="城东区")
    db.session.add_all([school1, school2])
    db.session.commit()
    
    # 创建班级
    class1 = Class(name="高一(1)班", school_id=school1.id)
    class2 = Class(name="高一(2)班", school_id=school1.id)
    class3 = Class(name="高二(1)班", school_id=school2.id)
    db.session.add_all([class1, class2, class3])
    db.session.commit()
    
    # 生成学生数据
    personalities = [
        StudentPersonality.STUDIOUS,
        StudentPersonality.SOCIAL,
        StudentPersonality.ARTISTIC,
        StudentPersonality.ATHLETIC,
        StudentPersonality.INTROVERTED
    ]
    
    students = []
    for i in range(30):
        name = f"学生{i+1:02d}"
        personality = random.choice(personalities)
        student = Student(
            name=name,
            class_id=random.choice([class1.id, class2.id, class3.id]),
            personality=personality.value,
            mood=random.randint(60, 100),
            energy=random.randint(70, 100),
            social_energy=random.randint(50, 100)
        )
        students.append(student)
    
    db.session.add_all(students)
    db.session.commit()
    print(f"成功生成 {len(students)} 名学生数据")

if __name__ == "__main__":
    from server import app
    with app.app_context():
        generate_test_data()