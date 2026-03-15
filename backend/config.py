import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-for-youth-echo'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///youth_echo.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SOCKETIO_ASYNC_MODE = 'eventlet'
    DEBUG = True
    
    # 游戏配置
    GAME_TIME_SPEED = 1.0  # 游戏时间速度倍数
    MAX_STUDENTS_PER_CLASS = 30
    MAX_CLASSES_PER_SCHOOL = 10