# 📝 Web Task Manager

A simple web-based task manager built with **Flask**, **Python**, **HTML/CSS**, and **JavaScript**.  
This project demonstrates CRUD operations, basic web architecture, and clean frontend/backend separation.

---

## 🚀 Features

- Add tasks with priority (Low / Medium / High)
- Color-coded priorities
- Edit tasks inline
- Mark tasks as completed
- Delete tasks
- Persistent storage using JSON
- Clean UI with CSS

---

## 🧰 Tech Stack

**Backend**
- Python
- Flask

**Frontend**
- HTML (Jinja2 templates)
- CSS
- JavaScript

**Storage**
- JSON file

---

## 🏗 Architecture Overview

```text
Browser (HTML / CSS / JS)
        |
        | HTTP Requests
        v
Flask Application (app.py)
        |
        | Read / Write
        v
tasks.json

📁 Project Structure
web_task_manager/
│
├── app.py
├── tasks.json
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── README.md

▶️ How to Run Locally
git clone https://github.com/YOUR_USERNAME/web_task_manager.git
cd web_task_manager
pip install flask
python app.py

Then open your browser and visit:
http://127.0.0.1:5000