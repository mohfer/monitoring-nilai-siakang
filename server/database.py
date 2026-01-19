import sqlite3
import os
from pydantic import BaseModel
from typing import Optional, List

DATA_DIR = os.path.join(os.getcwd(), 'data', 'db')
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "tasks.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  login_id TEXT,
                  password TEXT,
                  chat_id TEXT,
                  target_semester_code TEXT,
                  interval INTEGER DEFAULT 300,
                  status TEXT DEFAULT 'stopped', 
                  pid INTEGER,
                  position INTEGER DEFAULT 0)''')
    ensure_position_column()
    conn.commit()
    conn.close()

def ensure_position_column():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("PRAGMA table_info(tasks)")
    columns = [info[1] for info in c.fetchall()]
    if 'position' not in columns:
        print("Migrating database: Adding 'position' column...")
        c.execute("ALTER TABLE tasks ADD COLUMN position INTEGER DEFAULT 0")
        c.execute("UPDATE tasks SET position = id")
        conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
