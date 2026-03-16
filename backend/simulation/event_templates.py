"""
青春回响 - 核心事件模板
包含10个高中生活核心事件，用于可试用版本
"""

CORE_EVENT_TEMPLATES = {
    # 课堂相关事件
    "classroom_quiz": {
        "name": "突然小测验",
        "description": "数学老师突然宣布进行10分钟小测验",
        "category": "academic",
        "probability": 0.25,
        "time_slots": ["08:00-12:00", "14:00-17:30"],
        "effects": {
            "stress": "+15",
            "academic_focus": "+10",
            "energy": "-5"
        },
        "student_reactions": {
            "prepared": "自信满满地开始答题",
            "unprepared": "慌张地翻找笔记",
            "average": "认真思考题目"
        }
    },
    
    "classroom_teacher_praise": {
        "name": "老师表扬",
        "description": "语文老师表扬了你的作文写得很好",
        "category": "academic",
        "probability": 0.2,
        "time_slots": ["08:00-12:00", "14:00-17:30"],
        "effects": {
            "mood": "happy",
            "confidence": "+20",
            "social_status": "+10"
        },
        "student_reactions": {
            "shy": "脸红地低下头",
            "confident": "微笑着接受表扬",
            "modest": "谦虚地说'还可以'"
        }
    },
    
    # 课间休息事件
    "break_time_gossip": {
        "name": "八卦传播",
        "description": "听说隔壁班的学霸和校花在交往",
        "category": "social",
        "probability": 0.3,
        "time_slots": ["10:00-10:20", "15:30-15:50"],
        "effects": {
            "social_activity": "+15",
            "gossip_level": "+10"
        },
        "student_reactions": {
            "gossiper": "兴奋地传播消息",
            "listener": "好奇地打听细节",
            "indifferent": "觉得与自己无关"
        }
    },
    
    "break_time_study_group": {
        "name": "学习小组",
        "description": "几个同学在讨论物理难题",
        "category": "academic",
        "probability": 0.25,
        "time_slots": ["10:00-10:20", "15:30-15:50", "19:30-21:30"],
        "effects": {
            "academic_knowledge": "+10",
            "friendship": "+15",
            "energy": "-5"
        },
        "student_reactions": {
            "active": "积极提出解题思路",
            "passive": "认真听别人讲解",
            "confused": "努力理解但还是不懂"
        }
    },
    
    # 午餐时间事件
    "lunch_cafeteria_meeting": {
        "name": "食堂偶遇",
        "description": "在食堂排队时遇到了暗恋的同学",
        "category": "social",
        "probability": 0.2,
        "time_slots": ["12:00-13:00"],
        "effects": {
            "heart_rate": "+20",
            "nervousness": "+15",
            "social_courage": "+10"
        },
        "student_reactions": {
            "shy": "假装没看见，低头看手机",
            "bold": "主动打招呼聊天",
            "awkward": "结结巴巴说不出话"
        }
    },
    
    "lunch_food_sharing": {
        "name": "分享午餐",
        "description": "同桌带了妈妈做的好吃的便当，分给你一些",
        "category": "social",
        "probability": 0.15,
        "time_slots": ["12:00-13:00"],
        "effects": {
            "happiness": "+20",
            "friendship": "+25",
            "energy": "+10"
        },
        "student_reactions": {
            "grateful": "真诚地道谢",
            "surprised": "没想到会分享给自己",
            "warm": "感觉心里暖暖的"
        }
    },
    
    # 下午活动事件
    "afternoon_sports": {
        "name": "篮球训练",
        "description": "放学后和朋友一起打篮球",
        "category": "physical",
        "probability": 0.2,
        "time_slots": ["17:30-19:00"],
        "effects": {
            "physical_fitness": "+15",
            "energy": "-20",
            "friendship": "+20"
        },
        "student_reactions": {
            "competitive": "全力投入比赛",
            "casual": "轻松地玩玩就好",
            "tired": "体力不支但坚持"
        }
    },
    
    "afternoon_library": {
        "name": "图书馆自习",
        "description": "在图书馆安静地复习功课",
        "category": "academic",
        "probability": 0.25,
        "time_slots": ["17:30-19:00"],
        "effects": {
            "academic_knowledge": "+20",
            "focus": "+25",
            "energy": "-15"
        },
        "student_reactions": {
            "focused": "完全沉浸在学习中",
            "distracted": "偶尔看看窗外",
            "efficient": "高效完成所有任务"
        }
    },
    
    # 晚自习事件
    "evening_confession": {
        "name": "晚自习告白",
        "description": "晚自习结束后，有人递给你一封情书",
        "category": "romantic",
        "probability": 0.1,
        "time_slots": ["21:30-22:00"],
        "effects": {
            "emotional_turbulence": "+30",
            "heart_rate": "+25",
            "sleep_quality": "-10"
        },
        "student_reactions": {
            "shocked": "完全没想到会发生这种事",
            "happy": "心里暗自窃喜",
            "confused": "不知道该如何回应"
        }
    },
    
    "evening_homework_help": {
        "name": "作业互助",
        "description": "同桌帮你解答了一道很难的数学题",
        "category": "academic",
        "probability": 0.3,
        "time_slots": ["19:30-21:30"],
        "effects": {
            "academic_understanding": "+25",
            "gratitude": "+20",
            "friendship": "+15"
        },
        "student_reactions": {
            "grateful": "真心感谢对方的帮助",
            "inspired": "决定以后也要帮助别人",
            "motivated": "更有动力学习了"
        }
    }
}

def get_event_template(event_type):
    """获取指定类型的事件模板"""
    return CORE_EVENT_TEMPLATES.get(event_type)

def get_all_templates():
    """获取所有事件模板"""
    return CORE_EVENT_TEMPLATES

def filter_templates_by_time(current_time):
    """根据当前时间筛选可用的事件模板"""
    available_templates = {}
    current_hour = int(current_time.split(':')[0]) if ':' in current_time else current_time
    
    for event_type, template in CORE_EVENT_TEMPLATES.items():
        available = False
        for time_slot in template['time_slots']:
            start_time, end_time = time_slot.split('-')
            start_hour = int(start_time.split(':')[0])
            end_hour = int(end_time.split(':')[0])
            
            if start_hour <= current_hour <= end_hour:
                available = True
                break
                
        if available:
            available_templates[event_type] = template
            
    return available_templates