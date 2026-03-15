"""
青春回响 - 数据库模型
"""
from datetime import datetime
import sqlite3
import json
from typing import List, Dict, Optional


class DatabaseManager:
    def __init__(self, db_path: str = "game_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 学校表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schools (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 班级表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id TEXT PRIMARY KEY,
                school_id TEXT NOT NULL,
                name TEXT NOT NULL,
                capacity INTEGER DEFAULT 30,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools (id)
            )
        ''')
        
        # 学生表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                class_id TEXT NOT NULL,
                name TEXT NOT NULL,
                avatar TEXT,
                personality TEXT,  -- JSON string
                skills TEXT,       -- JSON string
                relationships TEXT, -- JSON string
                status TEXT,       -- JSON string (current state)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes (id)
            )
        ''')
        
        # 事件表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                target_id TEXT,
                data TEXT,         -- JSON string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 初始化示例数据
        self._init_sample_data(cursor)
        
        conn.commit()
        conn.close()
    
    def _init_sample_data(self, cursor):
        """初始化示例数据"""
        # 检查是否已有数据
        cursor.execute("SELECT COUNT(*) FROM schools")
        if cursor.fetchone()[0] == 0:
            # 添加示例学校
            schools = [
                ("school_001", "第一高中"),
                ("school_002", "第二高中"), 
                ("school_003", "第三高中")
            ]
            cursor.executemany("INSERT INTO schools (id, name) VALUES (?, ?)", schools)
            
            # 添加示例班级
            classes = [
                ("class_001", "school_001", "高一(1)班"),
                ("class_002", "school_001", "高一(2)班"),
                ("class_003", "school_002", "高二(1)班"),
                ("class_004", "school_003", "高三(1)班")
            ]
            cursor.executemany("INSERT INTO classes (id, school_id, name) VALUES (?, ?, ?)", classes)
            
            # 添加示例学生
            students = [
                ("student_001", "class_001", "李明", "avatar1.png", 
                 '{"traits": ["勤奋", "内向"], "mood": "normal"}',
                 '{"academics": 85, "social": 60, "creativity": 70}',
                 '{"friends": ["student_002"], "crushes": []}',
                 '{"location": "classroom", "activity": "studying"}'),
                ("student_002", "class_001", "王芳", "avatar2.png",
                 '{"traits": ["活泼", "外向"], "mood": "happy"}',
                 '{"academics": 75, "social": 90, "creativity": 80}',
                 '{"friends": ["student_001", "student_003"], "crushes": ["student_001"]}',
                 '{"location": "classroom", "activity": "chatting"}'),
                ("student_003", "class_001", "张伟", "avatar3.png",
                 '{"traits": ["调皮", "聪明"], "mood": "excited"}',
                 '{"academics": 80, "social": 70, "creativity": 85}',
                 '{"friends": ["student_002"], "crushes": []}',
                 '{"location": "classroom", "activity": "daydreaming"}')
            ]
            cursor.executemany('''INSERT INTO students 
                (id, class_id, name, avatar, personality, skills, relationships, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', students)


class SchoolModel:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_all_schools(self) -> List[Dict]:
        """获取所有学校"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM schools ORDER BY created_at")
        schools = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
        conn.close()
        return schools


class ClassModel:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_classes_by_school(self, school_id: str) -> List[Dict]:
        """根据学校ID获取班级"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.name, COUNT(s.id) as student_count
            FROM classes c
            LEFT JOIN students s ON c.id = s.class_id
            WHERE c.school_id = ?
            GROUP BY c.id, c.name
        """, (school_id,))
        classes = [{"id": row[0], "name": row[1], "student_count": row[2]} for row in cursor.fetchall()]
        conn.close()
        return classes


class StudentModel:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_students_by_class(self, class_id: str) -> List[Dict]:
        """根据班级ID获取学生"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, avatar, personality, skills, relationships, status
            FROM students
            WHERE class_id = ?
            ORDER BY name
        """, (class_id,))
        students = []
        for row in cursor.fetchall():
            student = {
                "id": row[0],
                "name": row[1],
                "avatar": row[2],
                "personality": json.loads(row[3]),
                "skills": json.loads(row[4]),
                "relationships": json.loads(row[5]),
                "status": json.loads(row[6])
            }
            students.append(student)
        conn.close()
        return students
    
    def get_student_by_id(self, student_id: str) -> Optional[Dict]:
        """根据学生ID获取学生详情"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, avatar, personality, skills, relationships, status
            FROM students
            WHERE id = ?
        """, (student_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "avatar": row[2],
                "personality": json.loads(row[3]),
                "skills": json.loads(row[4]),
                "relationships": json.loads(row[5]),
                "status": json.loads(row[6])
            }
        return None


class EventModel:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create_event(self, event_type: str, target_id: str, data: Dict):
        """创建事件"""
        import uuid
        event_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO events (id, event_type, target_id, data)
            VALUES (?, ?, ?, ?)
        """, (event_id, event_type, target_id, json.dumps(data)))
        conn.commit()
        conn.close()
        return event_id