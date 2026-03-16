"""
青春回响 - 校园广播黄金时段系统
实现18:30-19:30的校园广播功能，包含经典剧情模板和背景氛围
"""

from datetime import datetime, time
import random
from typing import List, Dict, Any
from .student_behavior import StudentBehavior
from .event_system import EventSystem

class BroadcastSystem:
    def __init__(self):
        self.broadcast_start = time(18, 30)  # 18:30
        self.broadcast_end = time(19, 30)    # 19:30
        self.event_system = EventSystem()
        self.classic_scenes = self._load_classic_scenes()
        
    def _load_classic_scenes(self) -> List[Dict[str, Any]]:
        """加载经典校园广播场景模板"""
        return [
            {
                "id": "couple_walking",
                "name": "情侣散步",
                "background_music": "同桌的你",
                "description": "夕阳下，一对学生在操场边散步，背景播放着《同桌的你》",
                "mood_effect": {"romance": 0.3, "nostalgia": 0.5},
                "probability": 0.25
            },
            {
                "id": "bookworm_reading", 
                "name": "学霸看书",
                "background_music": "英语听力",
                "description": "看台上，一个学生戴着耳机专注地看书，正在听英语听力",
                "mood_effect": {"focus": 0.4, "academic_motivation": 0.3},
                "probability": 0.2
            },
            {
                "id": "basketball_practice",
                "name": "篮球队加练",
                "background_music": "轻快背景音乐",
                "description": "篮球场上，队员们在夕阳下加练，汗水在余晖中闪光",
                "mood_effect": {"energy": 0.3, "team_spirit": 0.4},
                "probability": 0.2
            },
            {
                "id": "friends_sharing",
                "name": "好友分享",
                "background_music": "温暖轻音乐",
                "description": "草坪上，几个好友分享零食，讨论着未来的梦想",
                "mood_effect": {"friendship": 0.4, "hope": 0.3},
                "probability": 0.2
            },
            {
                "id": "lonely_student",
                "name": "孤独学生",
                "background_music": "忧伤钢琴曲",
                "description": "角落里，一个学生独自发呆，静静地听着校园广播",
                "mood_effect": {"melancholy": 0.3, "reflection": 0.4},
                "probability": 0.15
            }
        ]
    
    def is_broadcast_time(self, current_time: datetime = None) -> bool:
        """检查当前是否为广播时间"""
        if current_time is None:
            current_time = datetime.now()
            
        current_t = current_time.time()
        return self.broadcast_start <= current_t <= self.broadcast_end
    
    def generate_broadcast_content(self, class_id: str, students: List[Dict]) -> Dict[str, Any]:
        """生成广播内容"""
        if not self.is_broadcast_time():
            return {"active": False}
            
        # 选择当前时间段的节目
        current_minute = datetime.now().minute
        current_hour = datetime.now().hour
        
        program_schedule = {
            (18, 30): "新闻简报",
            (18, 40): "点歌台", 
            (19, 0): "校园故事分享",
            (19, 20): "天气预报和明日提醒"
        }
        
        current_program = "校园故事分享"  # 默认
        for (hour, minute), program in program_schedule.items():
            if current_hour == hour and current_minute >= minute:
                current_program = program
                
        # 生成具体的广播场景
        scene = self._select_broadcast_scene(students)
        
        broadcast_content = {
            "active": True,
            "program": current_program,
            "scene": scene,
            "timestamp": datetime.now().isoformat(),
            "class_id": class_id,
            "background_info": {
                "time": f"{current_hour}:{current_minute:02d}",
                "atmosphere": "夕阳余晖、操场剪影、教学楼灯光渐亮"
            }
        }
        
        return broadcast_content
    
    def _select_broadcast_scene(self, students: List[Dict]) -> Dict[str, Any]:
        """根据班级学生情况选择合适的广播场景"""
        # 计算班级整体状态
        avg_energy = sum(s.get('energy', 50) for s in students) / len(students)
        avg_social = sum(s.get('social_points', 50) for s in students) / len(students)
        
        # 根据班级状态调整场景概率
        weighted_scenes = []
        for scene in self.classic_scenes:
            base_prob = scene["probability"]
            
            # 能量高的班级更可能出现活跃场景
            if scene["id"] in ["basketball_practice", "friends_sharing"]:
                if avg_energy > 70:
                    base_prob *= 1.5
                    
            # 社交活跃的班级更可能出现互动场景  
            if scene["id"] in ["couple_walking", "friends_sharing"]:
                if avg_social > 60:
                    base_prob *= 1.3
                    
            weighted_scenes.append((scene, base_prob))
            
        # 随机选择场景
        total_weight = sum(weight for _, weight in weighted_scenes)
        rand = random.uniform(0, total_weight)
        current = 0
        
        for scene, weight in weighted_scenes:
            current += weight
            if rand <= current:
                return scene
                
        return weighted_scenes[0][0]  # fallback
    
    def trigger_broadcast_event(self, class_id: str, students: List[Dict]) -> Dict[str, Any]:
        """触发广播事件并返回详细信息"""
        broadcast_content = self.generate_broadcast_content(class_id, students)
        
        if broadcast_content["active"]:
            # 创建广播事件
            event = {
                "id": f"broadcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "type": "campus_broadcast",
                "name": "校园广播黄金时段",
                "description": f"正在播放: {broadcast_content['program']}",
                "class_id": class_id,
                "scene_details": broadcast_content["scene"],
                "timestamp": broadcast_content["timestamp"],
                "affected_students": [s["id"] for s in students]  # 全班受影响
            }
            
            return event
            
        return {"active": False}

# 全局广播系统实例
broadcast_system = BroadcastSystem()