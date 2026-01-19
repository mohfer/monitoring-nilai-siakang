import subprocess
import os
import sys
import signal
import time
import json
from .database import get_db_connection

PYTHON_EXE = sys.executable
SCRIPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))

active_processes = {}

def restore_running_tasks():
    """Restores tasks that were marked as 'running' in the database."""
    print("🔄 Restoring running tasks...")
    conn = get_db_connection()
    tasks = conn.execute("SELECT * FROM tasks WHERE status = 'running'").fetchall()
    conn.close()
    
    for task in tasks:
        task_id = task['id']
        print(f"   ↳ Restarting task: {task['name']} (ID: {task_id})")
        start_process(task_id)

def start_process(task_id: int):
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    conn.close()
    
    if not task:
        return False, "Task not found"
        
    if task_id in active_processes and active_processes[task_id].poll() is None:
        return True, "Already running"

    env = os.environ.copy()
    env["LOGIN_ID"] = task['login_id']
    env["PASSWORD"] = task['password']
    env["CHAT_ID"] = task['chat_id']
    if task['target_semester_code']:
        env["TARGET_SEMESTER_CODE"] = task['target_semester_code']
    env["INTERVAL"] = str(task['interval'])
    env["PYTHONIOENCODING"] = "utf-8"
    
    data_dir = os.path.join(os.path.dirname(SCRIPT_PATH), "data", "value")
    os.makedirs(data_dir, exist_ok=True)

    env["FILE_DATA"] = os.path.join(data_dir, f"last_values_{task_id}.json")
    
    log_dir = os.path.join(os.path.dirname(SCRIPT_PATH), "data", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = open(os.path.join(log_dir, f"task_{task_id}.log"), "a", encoding="utf-8")
    
    try:
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        
        proc = subprocess.Popen(
            [PYTHON_EXE, "-u", SCRIPT_PATH],
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            cwd=os.path.dirname(SCRIPT_PATH), 
            creationflags=creationflags
        )
        
        active_processes[task_id] = proc
        
        conn = get_db_connection()
        conn.execute('UPDATE tasks SET status = ?, pid = ? WHERE id = ?', ('running', proc.pid, task_id))
        conn.commit()
        conn.close()
        
        return True, "Started"
    except Exception as e:
        return False, str(e)

def stop_process(task_id: int):
    proc = active_processes.get(task_id)
    
    if not proc:
        conn = get_db_connection()
        task = conn.execute('SELECT pid, status FROM tasks WHERE id = ?', (task_id,)).fetchone()
        conn.close()
        if task and task['status'] == 'running' and task['pid']:
            try:
                os.kill(task['pid'], signal.SIGTERM)
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(task['pid'])])
            except:
                pass 
    else:
        if os.name == 'nt':
             subprocess.call(['taskkill', '/F', '/T', '/PID', str(proc.pid)])
        else:
            proc.terminate()
        
        del active_processes[task_id]

    conn = get_db_connection()
    conn.execute('UPDATE tasks SET status = ?, pid = NULL WHERE id = ?', ('stopped', task_id))
    conn.commit()
    conn.close()
    return True, "Stopped"

def get_logs(task_id: int):
    log_path = os.path.join(os.path.dirname(SCRIPT_PATH), "data", "logs", f"task_{task_id}.log")
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8", errors='replace') as f:
            lines = f.readlines()
            return "".join(lines[-200:])
    return "No logs found."

def get_last_values(task_id: int):
    file_path = os.path.join(os.path.dirname(SCRIPT_PATH), "data", "value", f"last_values_{task_id}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    return None

def cleanup_task_files(task_id: int):
    """Deletes json data and log files associated with the task."""
    try:
        json_path = os.path.join(os.path.dirname(SCRIPT_PATH), "data", "value", f"last_values_{task_id}.json")
        if os.path.exists(json_path):
            os.remove(json_path)
            
        log_path = os.path.join(os.path.dirname(SCRIPT_PATH), "data", "logs", f"task_{task_id}.log")
        if os.path.exists(log_path):
            os.remove(log_path)
            
        return True
    except Exception as e:
        print(f"Error cleaning up files for task {task_id}: {e}")
        return False

def run_process_once(task_id: int):
    """Runs the scraper process once for the given task."""
    conn = get_db_connection()
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    conn.close()
    
    if not task:
        return False, "Task not found"
        
    if task_id in active_processes and active_processes[task_id].poll() is None:
        return False, "Task is currently running. Please stop it first."

    env = os.environ.copy()
    env["LOGIN_ID"] = task['login_id']
    env["PASSWORD"] = task['password']
    env["CHAT_ID"] = task['chat_id']
    if task['target_semester_code']:
        env["TARGET_SEMESTER_CODE"] = task['target_semester_code']
    env["INTERVAL"] = "0"
    env["PYTHONIOENCODING"] = "utf-8"
    
    data_dir = os.path.join(os.path.dirname(SCRIPT_PATH), "data", "value")
    env["FILE_DATA"] = os.path.join(data_dir, f"last_values_{task_id}.json")
    
    log_dir = os.path.join(os.path.dirname(SCRIPT_PATH), "data", "logs")
    log_path = os.path.join(log_dir, f"task_{task_id}.log")
    
    try:
        log_file = open(log_path, "a", encoding="utf-8")
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        
        proc = subprocess.Popen(
            [PYTHON_EXE, "-u", SCRIPT_PATH, "--run-once"],
            env=env,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            cwd=os.path.dirname(SCRIPT_PATH), 
            creationflags=creationflags
        )
        
        try:
            proc.wait(timeout=60)
            return True, "Data refreshed successfully"
        except subprocess.TimeoutExpired:
            proc.terminate()
            return False, "Refresh timed out"
            
    except Exception as e:
        return False, str(e)
