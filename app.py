from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

tasks = [
    {"id": 1, "description": "Learn Flask basics", "completed": False},
    {"id": 2, "description": "Build web task manager", "completed": False},
    {"id": 3, "description": "Apply to jobs", "completed": True},
]

@app.route("/")
def home():
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    description = request.form.get("description")

    if not description or not description.strip():
        return redirect(url_for("home"))
    
    new_id = len(tasks) + 1
    tasks.append({
        "id": new_id,
        "description": description,
        "completed": False
    })
    return redirect(url_for("home"))

@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            break
    
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)