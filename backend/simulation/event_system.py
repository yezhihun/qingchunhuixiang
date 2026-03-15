"""
青春回响 - 事件系统
处理游戏中的各种事件触发和处理
"""
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from .student_behavior import StudentBehavior

class EventSystem:
    def __init__(self):
        self.events = []
        self.event_templates = self._load_event_templates()
        self.student_behavior = StudentBehavior()
        
    def _load_event_templates(self) -> Dict[str, Any]:
        """加载事件模板"""
        return {
            "classroom": {
                "teacher_comes": {
                    "name": "老师来了",
                    "description": "班主任突然进入教室",
                    "probability": 0.3,
                    "effects": ["students_silent", "attention_increase"]
                },
                "quiz_announcement": {
                    "name": "小测验通知",
                    "description": "老师宣布明天有小测验",
                    "probability": 0.2,
                    "effects": ["stress_increase", "study_motivation"]
                }
            },
            "break_time": {
                "gossip_spread": {
                    "name": "八卦传播",
                    "description": "某个八卦消息在班级中传播",
                    "probability": 0.4,
                    "effects": ["social_activity", "relationship_change"]
                },
                "club_recruitment": {
                    "name": "社团招新",
                    "description": "社团成员来班级招新",
                    "probability": 0.25,
                    "effects": ["interest_discovery", "social_expansion"]
                }
            },
            "after_school": {
                "study_group": {
                    "name": "学习小组",
                    "description": "几个同学组织学习小组",
                    "probability": 0.35,
                    "effects": ["academic_improvement", "friendship_development"]
                },
                "confession": {
                    "name": "告白事件",
                    "description": "某位同学鼓起勇气告白",
                    "probability": 0.15,
                    "effects": ["emotional_turbulence", "relationship_drama"]
                }
            }
        }
    
    def generate_events_for_period(self, period: str, class_id: str, students: List[Dict]) -> List[Dict]:
        """为指定时间段生成事件"""
        if period not in self.event_templates:
            return []
            
        events = []
        templates = self.event_templates[period]
        
        for event_key, template in templates.items():
            if random.random() < template["probability"]:
                event = {
                    "id": f"{event_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "type": event_key,
                    "name": template["name"],
                    "description": template["description"],
                    "class_id": class_id,
                    "timestamp": datetime.now().isoformat(),
                    "affected_students": self._select_affected_students(students, template),
                    "effects": template["effects"]
                }
                events.append(event)
                
        return events
    
    def _select_affected_students(self, students: List[Dict], template: Dict) -> List[str]:
        """选择受影响的学生"""
        # 根据事件类型选择学生
        if "confession" in template.get("name", ""):
            # 告白事件选择2个学生
            if len(students) >= 2:
                return [s["id"] for s in random.sample(students, 2)]
        elif "study_group" in template.get("name", ""):
            # 学习小组选择3-5个学生
            group_size = min(random.randint(3, 5), len(students))
            return [s["id"] for s in random.sample(students, group_size)]
        else:
            # 其他事件可能影响全班或随机学生
            if random.random() < 0.5:
                return [s["id"] for s in students]  # 全班
            else:
                affected_count = min(random.randint(1, 3), len(students))
                return [s["id"] for s in random.sample(students, affected_count)]
                
        return []
    
    def process_event_effects(self, event: Dict, students: List[Dict]) -> List[Dict]:
        """处理事件对学生的影響"""
        updated_students = []
        
        for student in students:
            if student["id"] in event["affected_students"]:
                # 应用事件效果
                for effect in event["effects"]:
                    student = self._apply_effect(student, effect, event)
            updated_students.append(student)
            
        return updated_students
    
    def _apply_effect(self, student: Dict, effect: str, event: Dict) -> Dict:
        """应用具体效果到学生"""
        student_copy = student.copy()
        
        if effect == "students_silent":
            student_copy["current_mood"] = "nervous"
            student_copy["activity_level"] = max(0, student_copy.get("activity_level", 50) - 20)
            
        elif effect == "attention_increase":
            student_copy["focus"] = min(100, student_copy.get("focus", 50) + 15)
            
        elif effect == "stress_increase":
            student_copy["stress"] = min(100, student_copy.get("stress", 30) + 25)
            
        elif effect == "study_motivation":
            student_copy["motivation"] = min(100, student_copy.get("motivation", 50) + 20)
            
        elif effect == "social_activity":
            student_copy["social_energy"] = min(100, student_copy.get("social_energy", 60) + 15)
            
        elif effect == "relationship_change":
            # 随机改变一些关系值
            if "relationships" not in student_copy:
                student_copy["relationships"] = {}
            # 这里可以更复杂的逻辑
            
        elif effect == "academic_improvement":
            student_copy["academic_score"] = min(100, student_copy.get("academic_score", 70) + 5)
            
        elif effect == "friendship_development":
            student_copy["friendship_tendency"] = min(100, student_copy.get("friendship_tendency", 50) + 10)
            
        elif effect == "emotional_turbulence":
            student_copy["emotional_stability"] = max(0, student_copy.get("emotional_stability", 70) - 30)
            
        elif effect == "relationship_drama":
            student_copy["drama_level"] = min(100, student_copy.get("drama_level", 20) + 40)
            
        return student_copy
    
    def get_active_events(self, class_id: str) -> List[Dict]:
        """获取指定班级的活跃事件"""
        return [event for event in self.events if event["class_id"] == class_id]
    
    def add_event(self, event: Dict):
        """添加事件到系统"""
        self.events.append(event)
    
    def clear_old_events(self, hours: int = 24):
        """清理过期事件"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        self.events = [
            event for event in self.events 
            if datetime.fromisoformat(event["timestamp"].replace('Z', '+00:00')) > cutoff_time
        ]