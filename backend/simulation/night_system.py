"""
青春回响 - 夜间决策系统
处理22:00-06:00时间段的特殊事件和学生状态
"""

import json
import random
from datetime import datetime, time
from typing import Dict, List, Any
from .student_behavior import StudentBehavior

class NightSystem:
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = "config"
        self.config_dir = config_dir
        self.night_events = self._load_config("night_events.json")
        self.replay_templates = self._load_config("replay_templates_json")
        
    def _load_config(self, filename: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(f"{self.config_dir}/{filename}", 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告: 配置文件 {filename} 未找到")
            return {}
    
    def is_night_time(self, current_time: time = None) -> bool:
        """检查是否为夜间时间（22:00-06:00）"""
        if current_time is None:
            current_time = datetime.now().time()
            
        night_start = time(22, 0)  # 22:00
        night_end = time(6, 0)    # 06:00
        
        return current_time >= night_start or current_time <= night_end
    
    def generate_night_events(self, students: List[Dict], current_time: time = None) -> List[Dict]:
        """生成夜间事件"""
        if not self.is_night_time(current_time):
            return []
            
        events = []
        
        # 梦境和反思事件（每个学生都有）
        for student in students:
            if random.random() < 0.8:  # 80%概率有梦境
                dream_event = {
                    "type": "dream_reflection",
                    "student_id": student["id"],
                    "content": self._generate_dream_content(student),
                    "impact": {"mood_change": random.randint(-10, 15)}
                }
                events.append(dream_event)
        
        # 深夜活动事件（特定类型学生）
        for student in students:
            if self._should_have_late_activity(student):
                activity_event = {
                    "type": "late_night_activity",
                    "student_id": student["id"], 
                    "activity": self._get_late_activity(student),
                    "risk_level": random.choice(["low", "medium", "high"]),
                    "energy_cost": random.randint(10, 30)
                }
                events.append(activity_event)
                
        return events
    
    def _generate_dream_content(self, student: Dict) -> str:
        """生成梦境内容"""
        personality = student.get("personality", {})
        academic_score = student.get("attributes", {}).get("academic_score", 70)
        
        if academic_score < 50:
            return "梦见考试不及格，被老师和家长责备..."
        elif academic_score > 90:
            return "梦见自己考上了理想的大学，全家人都很开心！"
        else:
            interests = student.get("background_profile", {}).get("current_situation", {}).get("secret_dreams", [])
            if interests:
                return f"梦见自己实现了梦想：{interests[0]}"
            else:
                return "做了一个模糊但温暖的梦，醒来感觉很安心"
    
    def _should_have_late_activity(self, student: Dict) -> bool:
        """判断学生是否会有深夜活动"""
        traits = student.get("personality", {}).get("traits", {})
        energy = student.get("attributes", {}).get("energy", 50)
        
        # 学霸、失眠者、叛逆者更可能熬夜
        if (traits.get("bookworm") or traits.get("rebel") or 
            student.get("attributes", {}).get("stress", 0) > 80):
            return random.random() < 0.4
        return False
    
    def _get_late_activity(self, student: Dict) -> str:
        """获取深夜活动类型"""
        traits = student.get("personality", {}).get("traits", {})
        
        if traits.get("bookworm"):
            return "熬夜复习功课，准备明天的考试"
        elif traits.get("rebel"):
            return "偷偷玩手机游戏，和网友聊天"
        elif student.get("attributes", {}).get("stress", 0) > 80:
            return "辗转反侧睡不着，思考人生问题"
        else:
            return "写日记记录今天的感受"
    
    def generate_daily_summary(self, day_events: List[Dict], students: List[Dict]) -> Dict:
        """生成每日总结回放"""
        template = self.replay_templates.get("daily_summary", {})
        
        summary = {
            "title": template.get("title_template", "").format(date=datetime.now().strftime("%Y-%m-%d")),
            "sections": {}
        }
        
        # 重要事件
        important_events = [e for e in day_events if e.get("importance", 0) > 5]
        summary["sections"]["重要事件"] = [
            template["sections"][0]["format"].format(event_description=e.get("description", ""))
            for e in important_events[:3]
        ]
        
        # 成长亮点
        growth_moments = []
        for student in students:
            if student.get("attributes", {}).get("academic_score", 0) > 85:
                growth_moments.append(template["sections"][1]["format"].format(
                    student_name=student["name"], 
                    achievement="学业成绩优秀"
                ))
        summary["sections"]["成长亮点"] = growth_moments[:2]
        
        # 关系变化（简化版）
        summary["sections"]["关系变化"] = ["同学们的关系在慢慢发展中..."]
        
        # 明日预告
        tomorrow_preview = "明天是新的一天，继续关注同学们的成长吧！"
        summary["sections"]["明日预告"] = [template["sections"][3]["format"].format(
            next_day_preview=tomorrow_preview
        )]
        
        return summary