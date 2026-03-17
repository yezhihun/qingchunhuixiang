"""
青春回响 - 配置驱动的事件系统
处理游戏中的各种事件触发和处理，完全基于外部配置文件
"""
import os
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from .student_behavior import StudentBehavior

class EventSystem:
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        
        self.config_dir = config_dir
        self.events = []
        
        # 加载所有配置文件
        self.event_templates = self._load_json_config('events.json')
        self.effects_config = self._load_json_config('effects.json')
        self.scenarios_config = self._load_json_config('scenarios.json')
        
        self.student_behavior = StudentBehavior()
        
    def _load_json_config(self, filename: str) -> Dict[str, Any]:
        """从配置目录加载JSON配置文件"""
        config_path = os.path.join(self.config_dir, filename)
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告: 配置文件 {config_path} 未找到，使用空配置")
            return {}
        except json.JSONDecodeError as e:
            print(f"错误: 配置文件 {config_path} JSON格式错误: {e}")
            return {}
    
    def get_current_scenario(self, current_time: str = None) -> str:
        """根据当前时间确定场景"""
        if current_time is None:
            current_time = datetime.now().strftime('%H:%M')
            
        for scenario_name, scenario_data in self.scenarios_config.get('scenarios', {}).items():
            for time_slot in scenario_data.get('time_slots', []):
                start_time, end_time = time_slot.split('-')
                if self._is_time_in_range(current_time, start_time, end_time):
                    return scenario_name
        return "default"
    
    def _is_time_in_range(self, current: str, start: str, end: str) -> bool:
        """检查当前时间是否在指定范围内"""
        current_parts = list(map(int, current.split(':')))
        start_parts = list(map(int, start.split(':')))
        end_parts = list(map(int, end.split(':')))
        
        current_minutes = current_parts[0] * 60 + current_parts[1]
        start_minutes = start_parts[0] * 60 + start_parts[1]
        end_minutes = end_parts[0] * 60 + end_parts[1]
        
        return start_minutes <= current_minutes <= end_minutes
    
    def generate_events_for_period(self, period: str, class_id: str, students: List[Dict], 
                                 current_time: str = None) -> List[Dict]:
        """为指定时间段生成事件"""
        if current_time is None:
            current_time = datetime.now().strftime('%H:%M')
            
        # 获取当前场景
        current_scenario = self.get_current_scenario(current_time)
        if current_scenario not in self.scenarios_config.get('scenarios', {}):
            return []
        
        scenario_data = self.scenarios_config['scenarios'][current_scenario]
        available_events = scenario_data.get('available_events', [])
        base_multiplier = scenario_data.get('base_probability_multiplier', 1.0)
        
        events = []
        
        for event_key in available_events:
            if event_key not in self.event_templates.get('events', {}):
                continue
                
            template = self.event_templates['events'][event_key]
            # 应用场景概率倍数
            adjusted_probability = min(1.0, template.get('probability', 0.1) * base_multiplier)
            
            if random.random() < adjusted_probability:
                event = {
                    "id": f"{event_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "type": event_key,
                    "name": template["name"],
                    "description": template["description"],
                    "class_id": class_id,
                    "timestamp": datetime.now().isoformat(),
                    "affected_students": self._select_affected_students(students, template),
                    "effects": template.get("effects", []),
                    "scenario": current_scenario
                }
                events.append(event)
                
        return events
    
    def _select_affected_students(self, students: List[Dict], template: Dict) -> List[str]:
        """选择受影响的学生"""
        selection_method = template.get('selection_method', 'random')
        count_range = template.get('affected_count', [1, 3])
        
        if selection_method == 'all':
            return [s["id"] for s in students]
        elif selection_method == 'specific':
            # 可以根据学生属性选择特定学生
            specific_ids = template.get('specific_student_ids', [])
            return [sid for sid in specific_ids if any(s["id"] == sid for s in students)]
        else:  # random
            min_count, max_count = count_range
            affected_count = min(random.randint(min_count, max_count), len(students))
            if affected_count <= 0:
                return []
            return [s["id"] for s in random.sample(students, affected_count)]
    
    def process_event_effects(self, event: Dict, students: List[Dict]) -> List[Dict]:
        """处理事件对学生的影響"""
        updated_students = []
        
        for student in students:
            if student["id"] in event["affected_students"]:
                # 应用事件效果
                for effect_key in event["effects"]:
                    student = self._apply_effect_from_config(student, effect_key)
            updated_students.append(student)
            
        return updated_students
    
    def _apply_effect_from_config(self, student: Dict, effect_key: str) -> Dict:
        """从配置文件应用效果到学生"""
        if effect_key not in self.effects_config.get('effects', {}):
            return student
            
        effect_config = self.effects_config['effects'][effect_key]
        student_copy = student.copy()
        
        # 应用属性变化
        for attr_name, change_config in effect_config.get('attribute_changes', {}).items():
            current_value = student_copy.get(attr_name, 50)  # 默认值50
            
            if 'set' in change_config:
                # 直接设置值
                new_value = change_config['set']
            elif 'change' in change_config:
                # 相对变化
                change_amount = change_config['change']
                new_value = current_value + change_amount
                
                # 应用边界限制
                if 'min' in change_config:
                    new_value = max(change_config['min'], new_value)
                if 'max' in change_config:
                    new_value = min(change_config['max'], new_value)
            else:
                continue
                
            student_copy[attr_name] = new_value
            
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