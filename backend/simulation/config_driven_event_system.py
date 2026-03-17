"""
青春回响 - 配置驱动的事件系统
所有事件、效果、场景都从配置文件加载，支持动态更新
"""
import json
import random
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

class ConfigDrivenEventSystem:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.events_config = self._load_config("events.json")
        self.effects_config = self._load_config("effects.json")
        self.scenarios_config = self._load_config("scenarios.json")
        self.loaded_events = {}
        self.loaded_effects = {}
        self.loaded_scenarios = {}
        
        self._parse_configs()
        
    def _load_config(self, filename: str) -> Dict:
        """从配置文件加载数据"""
        config_path = self.config_dir / filename
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
            
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _parse_configs(self):
        """解析配置文件到内部数据结构"""
        # 解析事件配置
        for category, events in self.events_config.get("events", {}).items():
            for event_key, event_data in events.items():
                self.loaded_events[event_key] = {
                    "category": category,
                    "name": event_data["name"],
                    "description": event_data["description"],
                    "base_probability": event_data["base_probability"],
                    "conditions": event_data.get("conditions", {}),
                    "effects": event_data.get("effects", []),
                    "affected_students_rule": event_data.get("affected_students_rule", "random"),
                    "affected_count_range": event_data.get("affected_count_range", [1, 3])
                }
        
        # 解析效果配置
        for effect_key, effect_data in self.effects_config.get("effects", {}).items():
            self.loaded_effects[effect_key] = {
                "name": effect_data["name"],
                "description": effect_data["description"],
                "attribute_changes": effect_data.get("attribute_changes", {})
            }
        
        # 解析场景配置
        for scenario_key, scenario_data in self.scenarios_config.get("scenarios", {}).items():
            self.loaded_scenarios[scenario_key] = {
                "name": scenario_data["name"],
                "description": scenario_data["description"],
                "time_slots": scenario_data["time_slots"],
                "base_probability_multiplier": scenario_data["base_probability_multiplier"],
                "available_events": scenario_data["available_events"]
            }
    
    def get_active_scenario(self, current_time: str) -> Optional[str]:
        """根据当前时间确定活跃场景"""
        current_hour = int(current_time.split(':')[0])
        current_minute = int(current_time.split(':')[1])
        current_total_minutes = current_hour * 60 + current_minute
        
        for scenario_key, scenario_data in self.loaded_scenarios.items():
            for time_slot in scenario_data["time_slots"]:
                start_time, end_time = time_slot.split('-')
                start_hour, start_minute = map(int, start_time.split(':'))
                end_hour, end_minute = map(int, end_time.split(':'))
                
                start_total = start_hour * 60 + start_minute
                end_total = end_hour * 60 + end_minute
                
                if start_total <= current_total_minutes <= end_total:
                    return scenario_key
                    
        return None
    
    def calculate_event_probability(self, event_key: str, scenario_key: str, context: Dict = None) -> float:
        """计算事件在特定场景下的实际概率"""
        if event_key not in self.loaded_events or scenario_key not in self.loaded_scenarios:
            return 0.0
            
        event_data = self.loaded_events[event_key]
        scenario_data = self.loaded_scenarios[scenario_key]
        
        # 基础概率
        base_prob = event_data["base_probability"]
        
        # 场景乘数
        scenario_multiplier = scenario_data["base_probability_multiplier"]
        
        # 检查条件
        conditions_met = self._check_conditions(event_data["conditions"], context or {})
        if not conditions_met:
            return 0.0
            
        # 最终概率
        final_prob = min(1.0, base_prob * scenario_multiplier)
        return final_prob
    
    def _check_conditions(self, conditions: Dict, context: Dict) -> bool:
        """检查事件触发条件"""
        # 这里可以实现复杂的条件逻辑
        # 例如：学生压力值 > 80, 天气晴朗, 特定日期等
        for condition_key, condition_value in conditions.items():
            if condition_key in context:
                if isinstance(condition_value, dict):
                    # 支持范围条件 { "min": 50, "max": 80 }
                    if "min" in condition_value and context[condition_key] < condition_value["min"]:
                        return False
                    if "max" in condition_value and context[condition_key] > condition_value["max"]:
                        return False
                elif context[condition_key] != condition_value:
                    return False
            else:
                # 条件上下文中没有这个键，可能需要默认处理
                pass
                
        return True
    
    def generate_events_for_scenario(self, scenario_key: str, class_id: str, students: List[Dict], context: Dict = None) -> List[Dict]:
        """为指定场景生成事件"""
        if scenario_key not in self.loaded_scenarios:
            return []
            
        scenario_data = self.loaded_scenarios[scenario_key]
        events = []
        
        # 为每个可用事件计算概率并决定是否触发
        for event_key in scenario_data["available_events"]:
            if event_key not in self.loaded_events:
                continue
                
            probability = self.calculate_event_probability(event_key, scenario_key, context)
            
            if random.random() < probability:
                event_template = self.loaded_events[event_key]
                event = {
                    "id": f"{event_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "type": event_key,
                    "name": event_template["name"],
                    "description": event_template["description"],
                    "class_id": class_id,
                    "timestamp": datetime.now().isoformat(),
                    "affected_students": self._select_affected_students(students, event_template),
                    "effects": event_template["effects"],
                    "scenario": scenario_key
                }
                events.append(event)
                
        return events
    
    def _select_affected_students(self, students: List[Dict], event_template: Dict) -> List[str]:
        """根据事件规则选择受影响的学生"""
        rule = event_template["affected_students_rule"]
        count_range = event_template["affected_count_range"]
        
        if rule == "all":
            return [s["id"] for s in students]
        elif rule == "random":
            min_count, max_count = count_range
            actual_count = min(random.randint(min_count, max_count), len(students))
            return [s["id"] for s in random.sample(students, actual_count)]
        elif rule == "specific":
            # 可以根据学生属性选择特定学生
            # 例如：选择学业成绩最高的学生，或社交能力最强的学生
            return self._select_specific_students(students, event_template)
        else:
            # 默认随机选择
            min_count, max_count = count_range
            actual_count = min(random.randint(min_count, max_count), len(students))
            return [s["id"] for s in random.sample(students, actual_count)]
    
    def _select_specific_students(self, students: List[Dict], event_template: Dict) -> List[str]:
        """根据特定规则选择学生"""
        # 这里可以实现更复杂的逻辑
        # 例如：按属性排序后选择前N个
        return [s["id"] for s in students[:2]]  # 默认选择前2个
    
    def process_event_effects(self, event: Dict, students: List[Dict]) -> List[Dict]:
        """处理事件对学生的影響"""
        updated_students = []
        
        for student in students:
            if student["id"] in event["affected_students"]:
                # 应用事件效果
                for effect_key in event["effects"]:
                    if effect_key in self.loaded_effects:
                        student = self._apply_effect_from_config(student, effect_key)
            updated_students.append(student)
            
        return updated_students
    
    def _apply_effect_from_config(self, student: Dict, effect_key: str) -> Dict:
        """从配置应用效果到学生"""
        if effect_key not in self.loaded_effects:
            return student
            
        effect_config = self.loaded_effects[effect_key]
        student_copy = student.copy()
        
        # 应用属性变化
        for attr_name, change_config in effect_config["attribute_changes"].items():
            if "set" in change_config:
                student_copy[attr_name] = change_config["set"]
            elif "change" in change_config:
                current_value = student_copy.get(attr_name, 0)
                new_value = current_value + change_config["change"]
                
                # 应用最小/最大限制
                if "min" in change_config:
                    new_value = max(change_config["min"], new_value)
                if "max" in change_config:
                    new_value = min(change_config["max"], new_value)
                    
                student_copy[attr_name] = new_value
                
        return student_copy
    
    def reload_configs(self):
        """重新加载配置文件（支持热更新）"""
        try:
            self.events_config = self._load_config("events.json")
            self.effects_config = self._load_config("effects.json")
            self.scenarios_config = self._load_config("scenarios.json")
            self._parse_configs()
            return True
        except Exception as e:
            print(f"重载配置失败: {e}")
            return False