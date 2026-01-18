from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db, get_db_connection
from .models import TaskCreate, TaskUpdate, TaskResponse
from .manager import start_process, stop_process, get_logs, restore_running_tasks, get_last_values, cleanup_task_files
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from scraper_lib import SiakangScraper
except ImportError:
    SiakangScraper = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()
    restore_running_tasks()

@app.get("/tasks")
def list_tasks():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return tasks

@app.post("/tasks")
def create_task(task: TaskCreate):
    conn = get_db_connection()
    c = conn.execute(
        'INSERT INTO tasks (name, login_id, password, chat_id, target_semester_code, interval) VALUES (?, ?, ?, ?, ?, ?)',
        (task.name, task.login_id, task.password, task.chat_id, task.target_semester_code, task.interval)
    )
    task_id = c.lastrowid
    conn.commit()
    conn.close()
    return {"id": task_id, **task.dict(), "status": "stopped"}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    conn = get_db_connection()
    
    fields = task.dict(exclude_unset=True)
    if not fields:
        return {"message": "No fields to update"}
        
    query = "UPDATE tasks SET " + ", ".join(f"{k} = ?" for k in fields.keys()) + " WHERE id = ?"
    values = list(fields.values()) + [task_id]
    
    conn.execute(query, values)
    conn.commit()
    conn.close()
    
    return {"message": "Updated"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    stop_process(task_id)
    cleanup_task_files(task_id)
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return {"message": "Deleted"}

@app.post("/tasks/{task_id}/start")
def start_task_endpoint(task_id: int):
    success, msg = start_process(task_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": msg}

@app.post("/tasks/{task_id}/stop")
def stop_task_endpoint(task_id: int):
    success, msg = stop_process(task_id)
    return {"message": msg}

@app.get("/tasks/{task_id}/logs")
def get_logs_endpoint(task_id: int):
    return {"logs": get_logs(task_id)}

@app.get("/tasks/{task_id}/data")
def get_data_endpoint(task_id: int):
    data = get_last_values(task_id)
    return {"data": data if data else []}

@app.post("/check-semesters")
def check_semesters(credentials: dict = Body(...)):
    login_id = credentials.get("login_id")
    password = credentials.get("password")
    
    if not login_id or not password:
        raise HTTPException(status_code=400, detail="Missing login_id or password")
        
    if not SiakangScraper:
        raise HTTPException(status_code=500, detail="Scraper library not loaded")
        
    scraper = SiakangScraper(login_id, password)
    success, msg = scraper.login()
    
    if not success:
        raise HTTPException(status_code=401, detail=f"Login failed: {msg}")
        
    semesters = scraper.get_semesters()
    return {"semesters": semesters}
