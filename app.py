from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

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

@app.route("/")
def home():
    tasks = load_tasks()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    description = request.form.get("description")
    priority = request.form.get("priority")

    if not description or not description.strip():
        return redirect(url_for("home"))
    
    tasks = load_tasks()
    new_id = max([t["id"] for t in tasks], default=0) + 1

    tasks.append({
        "id": new_id,
        "description": description,
        "completed": False,
        "priority": priority
    })

    save_tasks(tasks)
    return redirect(url_for("home"))

@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    tasks = load_tasks()

    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            break
    
    save_tasks(tasks)
    return redirect(url_for("home"))

@app.route("/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    data = request.get_json()

    new_description = data.get("description")
    new_priority = data.get("priority")

    if not new_description or not new_description.strip():
        return jsonify({"error": "Invalid description"}), 400
    
    tasks = load_tasks()
    
    for task in tasks:
        if task["id"] == task_id:
            task["description"] = new_description
            task["priority"] = new_priority
            break

    save_tasks(tasks)

    return jsonify({"success": True})

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [task for task in tasks if task["id"] != task_id]

    save_tasks(tasks)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)