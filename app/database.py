import sqlite3
import json
import os
from typing import List, Dict, Any, Optional

DB_FILE = "digital_twin.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the SQLite database schema."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # User Profile table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # Goals table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT,
        target_date TEXT,
        status TEXT DEFAULT 'in_progress',
        progress INTEGER DEFAULT 0
    )
    """)

    # Tasks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goal_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        due_date TEXT,
        priority TEXT DEFAULT 'medium',
        status TEXT DEFAULT 'todo',
        FOREIGN KEY (goal_id) REFERENCES goals (id) ON DELETE SET NULL
    )
    """)

    # Calendar Events table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS calendar_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL
    )
    """)

    # Learning Plans table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS learning_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        topic TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        progress INTEGER DEFAULT 0,
        resources TEXT
    )
    """)

    # Quizzes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quizzes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_id INTEGER,
        question TEXT NOT NULL,
        options TEXT NOT NULL, -- JSON array of options
        correct_answer TEXT NOT NULL,
        FOREIGN KEY (plan_id) REFERENCES learning_plans (id) ON DELETE CASCADE
    )
    """)

    # Wellness Logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wellness_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT UNIQUE NOT NULL, -- YYYY-MM-DD
        sleep_hours REAL,
        exercise_minutes INTEGER,
        calories_burned INTEGER,
        mood TEXT,
        habits TEXT -- JSON list of habits checked
    )
    """)

    # Finance Logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS finance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        category TEXT,
        amount REAL NOT NULL,
        type TEXT NOT NULL, -- 'expense' or 'income'
        description TEXT
    )
    """)

    # Career Skills table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS career_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_name TEXT UNIQUE NOT NULL,
        proficiency TEXT, -- 'beginner', 'intermediate', 'advanced'
        certifications TEXT,
        roadmap TEXT -- JSON list of steps
    )
    """)

    conn.commit()
    
    # Insert default profile if not present
    cursor.execute("SELECT COUNT(*) FROM user_profile")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO user_profile (key, value) VALUES (?, ?)", ("name", "Alex Mercer"))
        cursor.execute("INSERT INTO user_profile (key, value) VALUES (?, ?)", ("work_style", "Deep Focus, async preferred, 45-minute blocks"))
        cursor.execute("INSERT INTO user_profile (key, value) VALUES (?, ?)", ("learning_goals", "Master Advanced Machine Learning, Learn Rust"))
        cursor.execute("INSERT INTO user_profile (key, value) VALUES (?, ?)", ("habits", json.dumps(["Sleep at 11PM", "Drink 3L Water", "Exercise 30m"])))
        conn.commit()

    conn.close()

class DatabaseRepository:
    def __init__(self):
        init_db()

    # --- User Profile Methods ---
    def get_profile(self) -> Dict[str, str]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM user_profile")
        rows = cursor.fetchall()
        conn.close()
        return {row['key']: row['value'] for row in rows}

    def update_profile(self, key: str, value: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO user_profile (key, value) VALUES (?, ?)", (key, value))
        conn.commit()
        conn.close()

    # --- Goals Methods ---
    def list_goals(self) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM goals")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def add_goal(self, title: str, description: str = "", category: str = "personal", target_date: str = "", status: str = "in_progress", progress: int = 0) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO goals (title, description, category, target_date, status, progress)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (title, description, category, target_date, status, progress))
        conn.commit()
        goal_id = cursor.lastrowid
        conn.close()
        return goal_id

    def update_goal(self, goal_id: int, updates: Dict[str, Any]):
        conn = get_db_connection()
        cursor = conn.cursor()
        keys = [f"{k} = ?" for k in updates.keys()]
        values = list(updates.values())
        values.append(goal_id)
        cursor.execute(f"UPDATE goals SET {', '.join(keys)} WHERE id = ?", values)
        conn.commit()
        conn.close()

    def delete_goal(self, goal_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        conn.commit()
        conn.close()

    # --- Tasks Methods ---
    def list_tasks(self, goal_id: Optional[int] = None) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        if goal_id:
            cursor.execute("SELECT * FROM tasks WHERE goal_id = ?", (goal_id,))
        else:
            cursor.execute("SELECT * FROM tasks")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def add_task(self, title: str, description: str = "", goal_id: Optional[int] = None, due_date: str = "", priority: str = "medium", status: str = "todo") -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO tasks (title, description, goal_id, due_date, priority, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (title, description, goal_id, due_date, priority, status))
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()
        return task_id

    def update_task(self, task_id: int, updates: Dict[str, Any]):
        conn = get_db_connection()
        cursor = conn.cursor()
        keys = [f"{k} = ?" for k in updates.keys()]
        values = list(updates.values())
        values.append(task_id)
        cursor.execute(f"UPDATE tasks SET {', '.join(keys)} WHERE id = ?", values)
        conn.commit()
        conn.close()

    def delete_task(self, task_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

    # --- Calendar Methods ---
    def list_calendar_events(self) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM calendar_events ORDER BY start_time ASC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def add_calendar_event(self, title: str, description: str, start_time: str, end_time: str) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO calendar_events (title, description, start_time, end_time)
        VALUES (?, ?, ?, ?)
        """, (title, description, start_time, end_time))
        conn.commit()
        event_id = cursor.lastrowid
        conn.close()
        return event_id

    def delete_calendar_event(self, event_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
        conn.commit()
        conn.close()

    # --- Learning Methods ---
    def list_learning_plans(self) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM learning_plans")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def add_learning_plan(self, title: str, topic: str, status: str = "active", progress: int = 0, resources: str = "") -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO learning_plans (title, topic, status, progress, resources)
        VALUES (?, ?, ?, ?, ?)
        """, (title, topic, status, progress, resources))
        conn.commit()
        plan_id = cursor.lastrowid
        conn.close()
        return plan_id

    def update_learning_plan(self, plan_id: int, updates: Dict[str, Any]):
        conn = get_db_connection()
        cursor = conn.cursor()
        keys = [f"{k} = ?" for k in updates.keys()]
        values = list(updates.values())
        values.append(plan_id)
        cursor.execute(f"UPDATE learning_plans SET {', '.join(keys)} WHERE id = ?", values)
        conn.commit()
        conn.close()

    def list_quizzes(self, plan_id: Optional[int] = None) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        if plan_id:
            cursor.execute("SELECT * FROM quizzes WHERE plan_id = ?", (plan_id,))
        else:
            cursor.execute("SELECT * FROM quizzes")
        rows = []
        for r in cursor.fetchall():
            row_dict = dict(r)
            row_dict['options'] = json.loads(row_dict['options'])
            rows.append(row_dict)
        conn.close()
        return rows

    def add_quiz(self, plan_id: int, question: str, options: List[str], correct_answer: str) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO quizzes (plan_id, question, options, correct_answer)
        VALUES (?, ?, ?, ?)
        """, (plan_id, question, json.dumps(options), correct_answer))
        conn.commit()
        quiz_id = cursor.lastrowid
        conn.close()
        return quiz_id

    # --- Wellness Methods ---
    def get_wellness_log(self, date: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wellness_logs WHERE date = ?", (date,))
        row = cursor.fetchone()
        conn.close()
        if row:
            row_dict = dict(row)
            row_dict['habits'] = json.loads(row_dict['habits']) if row_dict['habits'] else []
            return row_dict
        return None

    def list_wellness_logs(self, limit: int = 7) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wellness_logs ORDER BY date DESC LIMIT ?", (limit,))
        rows = []
        for r in cursor.fetchall():
            rd = dict(r)
            rd['habits'] = json.loads(rd['habits']) if rd['habits'] else []
            rows.append(rd)
        conn.close()
        return rows

    def log_wellness(self, date: str, sleep_hours: Optional[float] = None, exercise_minutes: Optional[int] = None, calories_burned: Optional[int] = None, mood: Optional[str] = None, habits: Optional[List[str]] = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if row exists
        cursor.execute("SELECT sleep_hours, exercise_minutes, calories_burned, mood, habits FROM wellness_logs WHERE date = ?", (date,))
        row = cursor.fetchone()
        
        if row:
            # Update
            new_sleep = sleep_hours if sleep_hours is not None else row['sleep_hours']
            new_exercise = exercise_minutes if exercise_minutes is not None else row['exercise_minutes']
            new_calories = calories_burned if calories_burned is not None else row['calories_burned']
            new_mood = mood if mood is not None else row['mood']
            new_habits = json.dumps(habits) if habits is not None else row['habits']
            
            cursor.execute("""
            UPDATE wellness_logs 
            SET sleep_hours = ?, exercise_minutes = ?, calories_burned = ?, mood = ?, habits = ?
            WHERE date = ?
            """, (new_sleep, new_exercise, new_calories, new_mood, new_habits, date))
        else:
            # Insert
            cursor.execute("""
            INSERT INTO wellness_logs (date, sleep_hours, exercise_minutes, calories_burned, mood, habits)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (date, sleep_hours, exercise_minutes, calories_burned, mood, json.dumps(habits or [])))
            
        conn.commit()
        conn.close()

    # --- Finance Methods ---
    def list_finance_logs(self) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM finance_logs ORDER BY date DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def add_finance_log(self, date: str, category: str, amount: float, type: str, description: str = "") -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO finance_logs (date, category, amount, type, description)
        VALUES (?, ?, ?, ?, ?)
        """, (date, category, amount, type, description))
        conn.commit()
        log_id = cursor.lastrowid
        conn.close()
        return log_id

    # --- Career Methods ---
    def list_career_skills(self) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM career_skills")
        rows = []
        for r in cursor.fetchall():
            rd = dict(r)
            rd['roadmap'] = json.loads(rd['roadmap']) if rd['roadmap'] else []
            rows.append(rd)
        conn.close()
        return rows

    def add_career_skill(self, skill_name: str, proficiency: str, certifications: str = "", roadmap: List[str] = None) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO career_skills (skill_name, proficiency, certifications, roadmap)
        VALUES (?, ?, ?, ?)
        """, (skill_name, proficiency, certifications, json.dumps(roadmap or [])))
        conn.commit()
        skill_id = cursor.lastrowid
        conn.close()
        return skill_id

    def update_career_skill(self, skill_name: str, updates: Dict[str, Any]):
        conn = get_db_connection()
        cursor = conn.cursor()
        keys = [f"{k} = ?" for k in updates.keys()]
        values = list(updates.values())
        if 'roadmap' in updates:
            # Serialize if roadmap is in updates
            idx = list(updates.keys()).index('roadmap')
            values[idx] = json.dumps(updates['roadmap'])
        values.append(skill_name)
        cursor.execute(f"UPDATE career_skills SET {', '.join(keys)} WHERE skill_name = ?", values)
        conn.commit()
        conn.close()
