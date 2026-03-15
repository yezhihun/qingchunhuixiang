"""
学生关系管理系统
处理学生之间的好感度、友谊、竞争等关系
"""

from datetime import datetime, timedelta
import random
import json
from typing import Dict, List, Tuple, Optional
from ..models import Student, Relationship

class RelationshipManager:
    def __init__(self, db_session):
        self.db = db_session
        self.relationship_types = ['friendship', 'romance', 'rivalry', 'mentorship']
        
    def get_relationship(self, student1_id: str, student2_id: str) -> Optional[Relationship]:
        """获取两个学生之间的关系"""
        return self.db.query(Relationship).filter(
            ((Relationship.student1_id == student1_id) & 
             (Relationship.student2_id == student2_id)) |
            ((Relationship.student1_id == student2_id) & 
             (Relationship.student2_id == student1_id))
        ).first()
    
    def create_relationship(self, student1_id: str, student2_id: str, 
                          relationship_type: str = 'friendship') -> Relationship:
        """创建学生关系"""
        if student1_id == student2_id:
            return None
            
        existing = self.get_relationship(student1_id, student2_id)
        if existing:
            return existing
            
        relationship = Relationship(
            student1_id=student1_id,
            student2_id=student2_id,
            relationship_type=relationship_type,
            strength=0.0,  # 初始关系强度
            last_interaction=datetime.now()
        )
        self.db.add(relationship)
        self.db.commit()
        return relationship
    
    def update_relationship_strength(self, student1_id: str, student2_id: str, 
                                   change: float, interaction_type: str = 'neutral'):
        """更新关系强度"""
        relationship = self.get_relationship(student1_id, student2_id)
        if not relationship:
            relationship = self.create_relationship(student1_id, student2_id)
            
        # 根据互动类型调整变化幅度
        multipliers = {
            'positive': 1.5,
            'negative': -1.0,
            'neutral': 1.0,
            'romantic': 2.0,
            'competitive': 0.8
        }
        multiplier = multipliers.get(interaction_type, 1.0)
        actual_change = change * multiplier
        
        relationship.strength = max(-1.0, min(1.0, relationship.strength + actual_change))
        relationship.last_interaction = datetime.now()
        relationship.interaction_count = (relationship.interaction_count or 0) + 1
        
        self.db.commit()
        return relationship
    
    def get_closest_friends(self, student_id: str, limit: int = 5) -> List[Tuple[str, float]]:
        """获取最亲密的朋友列表"""
        relationships = self.db.query(Relationship).filter(
            ((Relationship.student1_id == student_id) | 
             (Relationship.student2_id == student_id)) &
            (Relationship.relationship_type == 'friendship')
        ).order_by(Relationship.strength.desc()).limit(limit).all()
        
        friends = []
        for rel in relationships:
            other_id = rel.student2_id if rel.student1_id == student_id else rel.student1_id
            friends.append((other_id, rel.strength))
            
        return friends
    
    def calculate_compatibility(self, student1_id: str, student2_id: str) -> float:
        """计算两个学生的兼容性"""
        student1 = self.db.query(Student).get(student1_id)
        student2 = self.db.query(Student).get(student2_id)
        
        if not student1 or not student2:
            return 0.0
            
        # 基于性格、兴趣、价值观的兼容性计算
        personality_match = self._calculate_personality_match(student1, student2)
        interest_overlap = self._calculate_interest_overlap(student1, student2)
        values_alignment = self._calculate_values_alignment(student1, student2)
        
        # 加权平均
        compatibility = (
            personality_match * 0.4 +
            interest_overlap * 0.3 +
            values_alignment * 0.3
        )
        
        return max(0.0, min(1.0, compatibility))
    
    def _calculate_personality_match(self, s1: Student, s2: Student) -> float:
        """计算性格匹配度"""
        # 简化的性格匹配算法
        # extroversion, agreeableness, conscientiousness, neuroticism, openness
        traits1 = [s1.extroversion, s1.agreeableness, s1.conscientiousness, 
                  s1.neuroticism, s1.openness]
        traits2 = [s2.extroversion, s2.agreeableness, s2.conscientiousness, 
                  s2.neuroticism, s2.openness]
        
        # 计算相似度（越相似分数越高）
        similarity = sum(abs(t1 - t2) for t1, t2 in zip(traits1, traits2))
        match_score = 1.0 - (similarity / 5.0)  # 归一化到0-1
        
        return match_score
    
    def _calculate_interest_overlap(self, s1: Student, s2: Student) -> float:
        """计算兴趣重叠度"""
        interests1 = set(s1.interests.split(',')) if s1.interests else set()
        interests2 = set(s2.interests.split(',')) if s2.interests else set()
        
        if not interests1 and not interests2:
            return 0.5  # 默认中等重叠
            
        if not interests1 or not interests2:
            return 0.2  # 一方无兴趣
            
        overlap = len(interests1.intersection(interests2))
        total = len(interests1.union(interests2))
        
        return overlap / total if total > 0 else 0.0
    
    def _calculate_values_alignment(self, s1: Student, s2: Student) -> float:
        """计算价值观一致性"""
        # 基于学术态度、社交偏好、未来规划等
        academic_diff = abs(s1.academic_performance - s2.academic_performance)
        social_diff = abs(s1.social_activity_level - s2.social_activity_level)
        future_diff = abs(s1.career_aspirations - s2.career_aspirations)
        
        total_diff = (academic_diff + social_diff + future_diff) / 3.0
        alignment = 1.0 - total_diff
        
        return max(0.0, alignment)
    
    def simulate_daily_interactions(self, class_id: str):
        """模拟班级内每日互动"""
        students = self.db.query(Student).filter(Student.class_id == class_id).all()
        
        if len(students) < 2:
            return
            
        # 随机配对进行互动
        for _ in range(len(students) * 2):  # 每人平均2次互动
            s1, s2 = random.sample(students, 2)
            
            # 决定互动类型
            interaction_type = self._determine_interaction_type(s1, s2)
            
            # 计算关系变化
            base_change = random.uniform(-0.1, 0.2)  # 基础变化范围
            if interaction_type == 'romantic' and random.random() < 0.3:
                base_change += 0.3  # 浪漫互动有额外加成
                
            self.update_relationship_strength(
                s1.id, s2.id, base_change, interaction_type
            )
    
    def _determine_interaction_type(self, s1: Student, s2: Student) -> str:
        """决定互动类型"""
        # 基于当前关系强度和学生特征
        current_rel = self.get_relationship(s1.id, s2.id)
        current_strength = current_rel.strength if current_rel else 0.0
        
        # 随机决定，但受当前关系影响
        rand = random.random()
        
        if rand < 0.1:  # 10% 竞争
            return 'competitive'
        elif rand < 0.3 and current_strength > 0.5:  # 20% 浪漫（需要一定好感）
            return 'romantic'
        elif rand < 0.7:  # 40% 积极
            return 'positive'
        else:  # 30% 中性
            return 'neutral'

# 全局关系管理器实例
_relationship_manager = None

def get_relationship_manager(db_session):
    """获取关系管理器单例"""
    global _relationship_manager
    if _relationship_manager is None:
        _relationship_manager = RelationshipManager(db_session)
    return _relationship_manager