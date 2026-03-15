"""
AI学生行为系统 - 青春回响
基于高中生活模拟游戏的AI行为逻辑
"""

import random
import json
from datetime import datetime, timedelta
from enum import Enum

class StudentMood(Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    NEUTRAL = "neutral"
    EXCITED = "excited"
    TIRED = "tired"

class StudentRelationship(Enum):
    STRANGER = "stranger"
    ACQUAINTANCE = "acquaintance"
    FRIEND = "friend"
    BEST_FRIEND = "best_friend"
    ENEMY = "enemy"

class StudentBehavior:
    def __init__(self, student_id, name, personality_traits=None):
        self.student_id = student_id
        self.name = name
        self.personality_traits = personality_traits or self._generate_personality()
        self.mood = StudentMood.NEUTRAL
        self.energy = 100  # 0-100
        self.stress = 0    # 0-100
        self.relationships = {}  # {student_id: relationship_level}
        self.skills = {}     # {skill_name: level}
        self.last_action_time = datetime.now()
        
    def _generate_personality(self):
        """生成随机性格特征"""
        traits = {
            'extroversion': random.uniform(0, 1),      # 外向性
            'agreeableness': random.uniform(0, 1),     # 宜人性
            'conscientiousness': random.uniform(0, 1), # 尽责性
            'neuroticism': random.uniform(0, 1),       # 神经质
            'openness': random.uniform(0, 1)           # 开放性
        }
        return traits
    
    def update_state(self, current_time):
        """更新学生状态"""
        time_diff = (current_time - self.last_action_time).total_seconds()
        
        # 能量随时间自然恢复（睡眠）
        if time_diff > 3600:  # 1小时以上
            self.energy = min(100, self.energy + 10)
            
        # 压力随时间自然缓解
        self.stress = max(0, self.stress - 5)
        
        # 根据压力和能量更新心情
        self._update_mood()
        
        self.last_action_time = current_time
    
    def _update_mood(self):
        """根据状态更新心情"""
        if self.energy < 30:
            self.mood = StudentMood.TIRED
        elif self.stress > 70:
            self.mood = StudentMood.SAD
        elif self.energy > 80 and self.stress < 20:
            self.mood = StudentMood.HAPPY
        else:
            self.mood = StudentMood.NEUTRAL
    
    def interact_with(self, other_student, interaction_type="casual"):
        """与其他学生互动"""
        if other_student.student_id not in self.relationships:
            self.relationships[other_student.student_id] = StudentRelationship.STRANGER
        
        current_relationship = self.relationships[other_student.student_id]
        
        # 根据性格和互动类型计算关系变化
        relationship_change = self._calculate_relationship_change(
            other_student, interaction_type
        )
        
        # 更新关系
        new_relationship = self._update_relationship_level(
            current_relationship, relationship_change
        )
        self.relationships[other_student.student_id] = new_relationship
        
        # 更新状态
        self.energy -= random.randint(5, 15)
        self.stress += random.randint(-5, 10)
        
        return {
            'interaction_result': 'success',
            'relationship_change': relationship_change,
            'new_relationship': new_relationship.value,
            'mood_before': self.mood.value,
            'mood_after': self.mood.value
        }
    
    def _calculate_relationship_change(self, other_student, interaction_type):
        """计算关系变化"""
        base_change = 0
        
        if interaction_type == "casual":
            base_change = random.uniform(-0.1, 0.3)
        elif interaction_type == "helpful":
            base_change = random.uniform(0.2, 0.6)
        elif interaction_type == "conflict":
            base_change = random.uniform(-0.6, -0.1)
        
        # 性格匹配度影响
        compatibility = self._calculate_compatibility(other_student)
        final_change = base_change * (1 + compatibility)
        
        return final_change
    
    def _calculate_compatibility(self, other_student):
        """计算性格兼容性"""
        # 简化的兼容性计算
        extro_match = abs(self.personality_traits['extroversion'] - 
                         other_student.personality_traits['extroversion'])
        agree_match = abs(self.personality_traits['agreeableness'] - 
                         other_student.personality_traits['agreeableness'])
        
        compatibility = (1 - extro_match) * 0.6 + (1 - agree_match) * 0.4
        return compatibility - 0.5  # 范围 -0.5 到 0.5
    
    def _update_relationship_level(self, current_level, change):
        """更新关系等级"""
        relationship_values = {
            StudentRelationship.STRANGER: 0,
            StudentRelationship.ACQUAINTANCE: 1,
            StudentRelationship.FRIEND: 2,
            StudentRelationship.BEST_FRIEND: 3,
            StudentRelationship.ENEMY: -1
        }
        
        current_value = relationship_values[current_level]
        new_value = current_value + change
        
        if new_value >= 2.5:
            return StudentRelationship.BEST_FRIEND
        elif new_value >= 1.5:
            return StudentRelationship.FRIEND
        elif new_value >= 0.5:
            return StudentRelationship.ACQUAINTANCE
        elif new_value >= -0.5:
            return StudentRelationship.STRANGER
        else:
            return StudentRelationship.ENEMY
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'student_id': self.student_id,
            'name': self.name,
            'personality_traits': self.personality_traits,
            'mood': self.mood.value,
            'energy': self.energy,
            'stress': self.stress,
            'relationships': {k: v.value for k, v in self.relationships.items()},
            'skills': self.skills,
            'last_action_time': self.last_action_time.isoformat()
        }

# 测试代码
if __name__ == "__main__":
    student1 = StudentBehavior("stu_001", "张三")
    student2 = StudentBehavior("stu_002", "李四")
    
    print("初始状态:")
    print(f"{student1.name}: {student1.mood.value}, energy={student1.energy}")
    print(f"{student2.name}: {student2.mood.value}, energy={student2.energy}")
    
    result = student1.interact_with(student2, "casual")
    print(f"\n互动结果: {result}")
    
    print(f"\n互动后状态:")
    print(f"{student1.name}: {student1.mood.value}, energy={student1.energy}")
    print(f"{student2.name}: {student2.mood.value}, energy={student2.energy}")