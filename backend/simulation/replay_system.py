"""
青春回响 - 回放系统
生成每日总结、周报和特殊时刻回忆
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

class ReplaySystem:
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        
        self.config_dir = config_dir
        self.replay_templates = self._load_json_config('replay_templates.json')
        self.event_history = []  # 存储历史事件
        
    def _load_json_config(self, filename: str) -> Dict[str, Any]:
        """从配置目录加载JSON配置文件"""
        config_path = os.path.join(self.config_dir, filename)
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告: 配置文件 {config_path} 未找到")
            return {}
        except json.JSONDecodeError as e:
            print(f"错误: 配置文件 {config_path} JSON格式错误: {e}")
            return {}
    
    def add_event_to_history(self, event: Dict):
        """添加事件到历史记录"""
        self.event_history.append({
            'event': event,
            'timestamp': datetime.now().isoformat()
        })
        
        # 保持历史记录在合理大小
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-500:]
    
    def generate_daily_summary(self, date: str, events: List[Dict], students: List[Dict]) -> Dict:
        """生成每日总结"""
        template = self.replay_templates.get('replay_templates', {}).get('daily_summary', {})
        
        # 提取重要事件
        important_events = [e for e in events if e.get('importance', 0) >= 5]
        achievements = []
        relationship_changes = []
        
        for student in students:
            # 检查学生成就
            if student.get('recent_achievement'):
                achievements.append({
                    'student_name': student['name'],
                    'achievement': student['recent_achievement']
                })
            
            # 检查关系变化
            if student.get('recent_relationship_change'):
                relationship_changes.append(student['recent_relationship_change'])
        
        # 构建明日预告
        next_day_preview = self._generate_next_day_preview(date)
        
        summary = {
            'title': template.get('title_template', '').format(date=date),
            'sections': {
                'important_events': [e.get('description', '') for e in important_events],
                'achievements': achievements,
                'relationship_changes': relationship_changes,
                'next_day_preview': next_day_preview
            },
            'generation_time': datetime.now().isoformat(),
            'type': 'daily_summary'
        }
        
        return summary
    
    def generate_weekly_digest(self, week_number: int, week_events: List[Dict], students: List[Dict]) -> Dict:
        """生成周报"""
        template = self.replay_templates.get('replay_templates', {}).get('weekly_digest', {})
        
        # 提取本周亮点
        highlights = [e for e in week_events if e.get('highlight', False)]
        growth_progress = []
        class_dynamics = []
        
        for student in students:
            if student.get('weekly_growth'):
                growth_progress.append(f"{student['name']}: {student['weekly_growth']}")
                
        # 班级动态（基于事件统计）
        event_types = {}
        for event in week_events:
            event_type = event.get('type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
        for event_type, count in event_types.items():
            if count > 1:
                class_dynamics.append(f"本周发生了{count}次{event_type}事件")
        
        next_week_preview = self._generate_next_week_preview(week_number)
        
        digest = {
            'title': template.get('title_template', '').format(week_number=week_number),
            'sections': {
                'highlights': [h.get('description', '') for h in highlights],
                'growth_progress': growth_progress,
                'class_dynamics': class_dynamics,
                'next_week_preview': next_week_preview
            },
            'generation_time': datetime.now().isoformat(),
            'type': 'weekly_digest'
        }
        
        return digest
    
    def generate_memory_moment(self, moment_type: str, story_content: str, trigger_data: Dict) -> Dict:
        """生成特殊时刻回忆"""
        template = self.replay_templates.get('replay_templates', {}).get('memory_moment', {})
        
        memory = {
            'title': template.get('title_template', '').format(moment_type=moment_type),
            'content': story_content,
            'trigger_data': trigger_data,
            'generation_time': datetime.now().isoformat(),
            'type': 'memory_moment',
            'shareable': True
        }
        
        return memory
    
    def _generate_next_day_preview(self, current_date: str) -> str:
        """生成明日预告"""
        tomorrow = datetime.strptime(current_date, '%Y-%m-%d') + timedelta(days=1)
        day_of_week = tomorrow.weekday()
        
        if day_of_week == 0:  # 周一
            return "新的一周开始了！可能会有班会和新的课程安排。"
        elif day_of_week == 4:  # 周五
            return "周末即将到来，同学们都在期待放松时光！"
        elif day_of_week == 5 or day_of_week == 6:  # 周末
            return "周末时间！同学们可能会有不同的安排。"
        else:
            return "明天是普通的上课日，继续关注同学们的成长吧！"
    
    def _generate_next_week_preview(self, current_week: int) -> str:
        """生成下周预告"""
        # 这里可以根据学期进度生成更具体的预告
        if current_week <= 4:
            return "新学期刚开始，同学们还在适应中。"
        elif current_week <= 12:
            return "期中考试临近，学习压力可能会增加。"
        elif current_week <= 20:
            return "期末考试准备阶段，需要更多关注学生状态。"
        else:
            return "学期接近尾声，同学们在为假期做准备。"
    
    def get_recent_replays(self, limit: int = 10) -> List[Dict]:
        """获取最近的回放记录"""
        # 这里应该从持久化存储中读取
        # 简化实现：返回空列表
        return []