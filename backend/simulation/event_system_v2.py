"""
青春回响 - 事件系统 v2
配置驱动 + 插件架构的混合方案
"""

import json
import os
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from .student_behavior import StudentBehavior

class EffectPlugin:
    """效果插件基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'unknown_effect')
        self.description = config.get('description', '')
    
    def apply(self, student: Dict, context: Dict) -> Dict:
        """应用效果到学生"""
        raise NotImplementedError("子类必须实现apply方法")

class AttributeChangeEffect(EffectPlugin):
    """属性变更效果插件"""
    
    def apply(self, student: Dict, context: Dict) -> Dict:
        student_copy = student.copy()
        changes = self.config.get('attribute_changes', {})
        
        for attr, change_config in changes.items():
            current_value = student_copy.get(attr, 0)
            
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
                
            student_copy[attr] = new_value
            
        return student_copy

class RelationshipEffect(EffectPlugin):
    """关系变更效果插件"""
    
    def apply(self, student: Dict, context: Dict) -> Dict:
        student_copy = student.copy()
        target_student_id = context.get('target_student_id')
        relationship_change = self.config.get('relationship_change', 0)
        
        if not target_student_id:
            return student_copy
            
        if 'relationships' not in student_copy:
            student_copy['relationships'] = {}
            
        current_relationship = student_copy['relationships'].get(target_student_id, 0)
        new_relationship = current_relationship + relationship_change
        student_copy['relationships'][target_student_id] = new_relationship
        
        return student_copy

class EventSystemV2:
    """事件系统 v2 - 配置驱动 + 插件架构"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.effect_plugins = self._load_effect_plugins()
        self.events_cache = {}
        self.last_reload = None
        
    def _load_effect_plugins(self) -> Dict[str, type]:
        """注册效果插件"""
        return {
            'attribute_change': AttributeChangeEffect,
            'relationship_update': RelationshipEffect
        }
    
    def _should_reload_configs(self) -> bool:
        """检查是否需要重新加载配置"""
        if self.last_reload is None:
            return True
            
        # 检查配置文件修改时间
        config_files = [
            os.path.join(self.config_dir, 'events.json'),
            os.path.join(self.config_dir, 'effects.json'),
            os.path.join(self.config_dir, 'scenarios.json')
        ]
        
        for file_path in config_files:
            if os.path.exists(file_path):
                mtime = os.path.getmtime(file_path)
                if mtime > self.last_reload.timestamp():
                    return True
                    
        return False
    
    def _load_config_file(self, filename: str) -> Dict:
        """安全加载配置文件"""
        file_path = os.path.join(self.config_dir, filename)
        if not os.path.exists(file_path):
            return {}
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"警告: 加载配置文件 {filename} 失败: {e}")
            return {}
    
    def reload_configs(self):
        """重新加载所有配置"""
        self.events_cache = self._load_config_file('events.json')
        self.effects_config = self._load_config_file('effects.json')
        self.scenarios_config = self._load_config_file('scenarios.json')
        self.last_reload = datetime.now()
    
    def get_available_events_for_scenario(self, scenario: str) -> List[Dict]:
        """获取指定场景可用的事件"""
        if self._should_reload_configs():
            self.reload_configs()
            
        events = []
        for event_key, event_config in self.events_cache.get('events', {}).items():
            if scenario in event_config.get('available_scenarios', []):
                events.append({
                    'id': event_key,
                    'config': event_config
                })
                
        return events
    
    def create_event_instance(self, event_template: Dict, context: Dict) -> Dict:
        """创建事件实例"""
        event_config = event_template['config']
        
        return {
            'id': f"{event_template['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'template_id': event_template['id'],
            'name': event_config.get('name', ''),
            'description': event_config.get('description', ''),
            'scenario': context.get('scenario'),
            'timestamp': datetime.now().isoformat(),
            'affected_students': self._select_affected_students(
                context.get('students', []), 
                event_config
            ),
            'effects': event_config.get('effects', []),
            'conditions': event_config.get('conditions', [])
        }
    
    def _select_affected_students(self, students: List[Dict], event_config: Dict) -> List[str]:
        """选择受影响的学生（简化版）"""
        selection_config = event_config.get('student_selection', {})
        selection_type = selection_config.get('type', 'random')
        
        if selection_type == 'all':
            return [s['id'] for s in students]
        elif selection_type == 'random':
            count = min(selection_config.get('count', 1), len(students))
            selected = []
            available_students = students.copy()
            for _ in range(count):
                if available_students:
                    student = available_students.pop(random.randint(0, len(available_students) - 1))
                    selected.append(student['id'])
            return selected
        else:
            # 默认选择第一个学生
            return [students[0]['id']] if students else []
    
    def process_event_effects(self, event: Dict, students: List[Dict]) -> List[Dict]:
        """处理事件效果"""
        updated_students = []
        
        # 获取效果配置
        effect_configs = self.effects_config.get('effects', {})
        
        for student in students:
            student_updated = student.copy()
            
            if student['id'] in event['affected_students']:
                for effect_name in event['effects']:
                    effect_config = effect_configs.get(effect_name, {})
                    if not effect_config:
                        continue
                        
                    # 创建效果插件实例
                    plugin_type = effect_config.get('plugin', 'attribute_change')
                    if plugin_type not in self.effect_plugins:
                        continue
                        
                    plugin_class = self.effect_plugins[plugin_type]
                    plugin = plugin_class(effect_config)
                    
                    # 应用效果
                    student_updated = plugin.apply(student_updated, {
                        'event': event,
                        'student': student
                    })
                    
            updated_students.append(student_updated)
            
        return updated_students