"""
青春回响 - 时间系统
管理游戏内的时间流逝和事件调度
"""

from datetime import datetime, timedelta
import threading
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

class GameTimeSystem:
    def __init__(self):
        self.game_time = datetime.now()  # 游戏内时间
        self.real_time_factor = 60  # 1秒现实时间 = 60秒游戏时间 (1分钟)
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        
    def start(self):
        """启动时间系统"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            # 启动时间推进线程
            self.time_thread = threading.Thread(target=self._advance_time, daemon=True)
            self.time_thread.start()
            
    def stop(self):
        """停止时间系统"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            
    def _advance_time(self):
        """推进游戏时间"""
        while self.is_running:
            time.sleep(1)  # 每秒更新一次
            self.game_time += timedelta(seconds=self.real_time_factor)
            
    def get_current_time(self):
        """获取当前游戏时间"""
        return self.game_time
        
    def schedule_event(self, trigger_time, callback, args=None):
        """
        调度游戏事件
        :param trigger_time: 触发时间 (datetime)
        :param callback: 回调函数
        :param args: 回调参数
        """
        # 计算现实时间的触发点
        real_trigger = datetime.now() + (trigger_time - self.game_time)
        self.scheduler.add_job(
            callback,
            'date',
            run_date=real_trigger,
            args=args or []
        )
        
    def schedule_recurring_event(self, hour, minute, callback, args=None):
        """
        调度重复事件（每天固定时间）
        :param hour: 小时 (0-23)
        :param minute: 分钟 (0-59)
        :param callback: 回调函数
        :param args: 回调参数
        """
        trigger = CronTrigger(hour=hour, minute=minute)
        self.scheduler.add_job(
            callback,
            trigger,
            args=args or []
        )

# 全局时间系统实例
game_time_system = GameTimeSystem()