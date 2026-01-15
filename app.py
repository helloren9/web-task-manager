from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
TASKS_FILE = "tasks.json"

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    
    with open(TASKS_FILE, "r") as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

def calculate_urgency_score(task):
    """Calculate urgency score for sorting (lower = more urgent)"""
    if task.get("completed"):
        return 9999  # Completed tasks are least urgent
    
    priority_scores = {"High": 1, "Medium": 2, "Low": 3}
    priority_score = priority_scores.get(task.get("priority", "Medium"), 2)
    
    due_date = task.get("due_date")
    if not due_date:
        return priority_score * 100  # No due date = less urgent than tasks with due dates
    
    try:
        due = datetime.fromisoformat(due_date)
        now = datetime.now()
        days_until_due = (due - now).days
        
        # Overdue tasks are most urgent
        if days_until_due < 0:
            return priority_score - abs(days_until_due) * 0.1
        # Due soon tasks are very urgent
        elif days_until_due <= 3:
            return priority_score + (days_until_due * 0.5)
        else:
            return priority_score + days_until_due
    except:
        return priority_score * 100

@app.route("/")
def home():
    tasks = load_tasks()
    
    # Get filter and sort parameters
    filter_priority = request.args.get("filter_priority", "all")
    filter_status = request.args.get("filter_status", "all")
    filter_due = request.args.get("filter_due", "all")
    sort_by = request.args.get("sort_by", "urgency")
    
    # Apply filters
    filtered_tasks = tasks
    
    if filter_priority != "all":
        filtered_tasks = [t for t in filtered_tasks if t["priority"].lower() == filter_priority.lower()]
    
    if filter_status == "completed":
        filtered_tasks = [t for t in filtered_tasks if t["completed"]]
    elif filter_status == "active":
        filtered_tasks = [t for t in filtered_tasks if not t["completed"]]
    
    # Filter by due date
    if filter_due == "overdue":
        now = datetime.now()
        filtered_tasks = [t for t in filtered_tasks 
                         if t.get("due_date") and datetime.fromisoformat(t["due_date"]) < now 
                         and not t.get("completed")]
    elif filter_due == "today":
        today = datetime.now().date()
        filtered_tasks = [t for t in filtered_tasks 
                         if t.get("due_date") and datetime.fromisoformat(t["due_date"]).date() == today]
    elif filter_due == "upcoming":
        now = datetime.now()
        week_later = now + timedelta(days=7)
        filtered_tasks = [t for t in filtered_tasks 
                         if t.get("due_date") and now <= datetime.fromisoformat(t["due_date"]) <= week_later]
    elif filter_due == "no_date":
        filtered_tasks = [t for t in filtered_tasks if not t.get("due_date")]
    
    # Apply sorting
    if sort_by == "urgency":
        filtered_tasks.sort(key=calculate_urgency_score)
    elif sort_by == "due_date":
        filtered_tasks.sort(key=lambda t: t.get("due_date") or "9999-12-31")
    elif sort_by == "due_date_desc":
        filtered_tasks.sort(key=lambda t: t.get("due_date") or "0000-01-01", reverse=True)
    elif sort_by == "priority":
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        filtered_tasks.sort(key=lambda t: priority_order.get(t["priority"], 3))
    elif sort_by == "priority_desc":
        priority_order = {"High": 2, "Medium": 1, "Low": 0}
        filtered_tasks.sort(key=lambda t: priority_order.get(t["priority"], -1))
    elif sort_by == "description":
        filtered_tasks.sort(key=lambda t: t["description"].lower())
    elif sort_by == "description_desc":
        filtered_tasks.sort(key=lambda t: t["description"].lower(), reverse=True)
    elif sort_by == "date_added":
        filtered_tasks.sort(key=lambda t: t.get("created_at", ""))
    elif sort_by == "date_added_desc":
        filtered_tasks.sort(key=lambda t: t.get("created_at", ""), reverse=True)
    else:  # default: sort by id
        filtered_tasks.sort(key=lambda t: t["id"])
    
    return render_template("index.html", 
                         tasks=filtered_tasks,
                         filter_priority=filter_priority,
                         filter_status=filter_status,
                         filter_due=filter_due,
                         sort_by=sort_by)

@app.route("/add", methods=["POST"])
def add_task():
    description = request.form.get("description")
    priority = request.form.get("priority")
    due_date = request.form.get("due_date")

    if not description or not description.strip():
        return redirect(url_for("home"))
    
    tasks = load_tasks()
    new_id = max([t["id"] for t in tasks], default=0) + 1

    new_task = {
        "id": new_id,
        "description": description,
        "completed": False,
        "priority": priority,
        "created_at": datetime.now().isoformat()
    }
    
    if due_date:
        new_task["due_date"] = due_date

    tasks.append(new_task)
    save_tasks(tasks)
    return redirect(url_for("home"))

@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    tasks = load_tasks()

    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = not task['completed']
            if task["completed"]:
                task["completed_at"] = datetime.now().isoformat()
            else:
                task.pop("completed_at", None)
            break
    
    save_tasks(tasks)
    return redirect(url_for("home"))

@app.route("/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    data = request.get_json()
    description = data.get("description")
    priority = data.get("priority")
    due_date = data.get("due_date")

    if not description or not description.strip():
        return jsonify({"success": False, "error": "Invalid description"}), 400
    
    tasks = load_tasks()
    task_found = False

    for task in tasks:
        if task["id"] == task_id:
            task["description"] = description
            task["priority"] = priority
            if due_date:
                task["due_date"] = due_date
            else:
                task.pop("due_date", None)
            task_found = True
            break

    if not task_found:
        return jsonify({"success": False, "error": "Task not found"}), 404
    
    save_tasks(tasks)
    return jsonify({"success": True, "due_date": task.get("due_date")})

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [task for task in tasks if task["id"] != task_id]

    save_tasks(tasks)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)