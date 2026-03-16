"""
青春回响 - 事件系统
处理游戏中的各种事件触发和处理
"""
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from .event_templates import EVENT_TEMPLATES
from .student_behavior import StudentBehavior

class EventSystem:
    def __init__(self):
        self.events = []
        self.event_templates = EVENT_TEMPLATES
        self.student_behavior = StudentBehavior("temp", "temp")
        
    def generate_events_for_period(self, period: str, class_id: str, students: List[Dict]) -> List[Dict]:
        """为指定时间段生成事件"""
        if period not in self.event_templates:
            # 如果没有特定时间段的模板，使用通用模板
            period = "general"
            
        if period not in self.event_templates:
            return []
            
        events = []
        templates = self.event_templates[period]
        
        for event_key, template in templates.items():
            if random.random() < template.get("probability", 0.1):
                event = {
                    "id": f"{event_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "type": event_key,
                    "name": template["name"],
                    "description": template["description"],
                    "class_id": class_id,
                    "timestamp": datetime.now().isoformat(),
                    "affected_students": self._select_affected_students(students, template),
                    "effects": template.get("effects", []),
                    "icon": template.get("icon", "event"),
                    "category": template.get("category", "general")
                }
                events.append(event)
                
        return events
    
    def _select_affected_students(self, students: List[Dict], template: Dict) -> List[str]:
        """选择受影响的学生"""
        if not students:
            return []
            
        # 根据事件类型选择学生
        event_type = template.get("type", "general")
        
        if event_type == "confession":
            # 告白事件选择2个学生
            if len(students) >= 2:
                return [s["id"] for s in random.sample(students, 2)]
        elif event_type == "study_group":
            # 学习小组选择3-5个学生
            group_size = min(random.randint(3, 5), len(students))
            return [s["id"] for s in random.sample(students, group_size)]
        elif event_type == "broadcast":
            # 广播事件影响全班
            return [s["id"] for s in students]
        elif event_type == "individual":
            # 个人事件选择1个学生
            return [random.choice(students)["id"]]
        else:
            # 其他事件可能影响全班或随机学生
            if random.random() < 0.5:
                return [s["id"] for s in students]  # 全班
            else:
                affected_count = min(random.randint(1, 3), len(students))
                return [s["id"] for s in random.sample(students, affected_count)]
                
        return [random.choice(students)["id"]]  # 默认选择一个
    
    def process_event_effects(self, event: Dict, students: List[Dict]) -> List[Dict]:
        """处理事件对学生的影響"""
        updated_students = []
        
        for student in students:
            if student["id"] in event["affected_students"]:
                # 应用事件效果
                for effect in event.get("effects", []):
                    student = self._apply_effect(student, effect, event)
            updated_students.append(student)
            
        return updated_students
    
    def _apply_effect(self, student: Dict, effect: str, event: Dict) -> Dict:
        """应用具体效果到学生"""
        student_copy = student.copy()
        
        effect_mappings = {
            "students_silent": {"current_mood": "nervous", "activity_level": -20},
            "attention_increase": {"focus": 15},
            "stress_increase": {"stress": 25},
            "study_motivation": {"motivation": 15},
            "social_activity": {"social_energy": 15},
            "academic_improvement": {"academic_score": 5},
            "friendship_development": {"friendship_tendency": 10},
            "emotional_turbulence": {"emotional_stability": -30},
            "energy_restore": {"energy": 20},
            "mood_improve": {"current_mood": "happy"},
            "mood_decline": {"current_mood": "sad"}
        }
        
        if effect in effect_mappings:
            effect_data = effect_mappings[effect]
            for attr, value in effect_data.items():
                if isinstance(value, str):  # 直接设置值
                    student_copy[attr] = value
                else:  # 数值变化
                    current_val = student_copy.get(attr, 50)
                    new_val = max(0, min(100, current_val + value))
                    student_copy[attr] = new_val
        
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
    
    def get_daily_schedule(self, day_of_week: int) -> Dict[str, List[str]]:
        """获取每日时间表"""
        schedule = {
            0: ["morning", "class", "lunch", "class", "after_school", "evening"],  # Monday
            1: ["morning", "class", "lunch", "class", "club", "evening"],         # Tuesday  
            2: ["morning", "class", "lunch", "class", "experiment", "evening"],   # Wednesday
            3: ["morning", "class", "lunch", "class", "counseling", "evening"],   # Thursday
            4: ["morning", "class", "lunch", "class", "test", "celebration"],     # Friday
            5: ["weekend_morning", "weekend_afternoon", "weekend_evening"],       # Saturday
            6: ["weekend_morning", "weekend_afternoon", "weekend_evening"]        # Sunday
        }
        return {"periods": schedule.get(day_of_week, schedule[0])}