from flask import Flask, render_template, redirect, request, session
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

# App initialization
app = Flask(__name__)
Scss(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.secret_key = '69d798e30204315a0b34207bf1b96d12'  # Set your secret key

db = SQLAlchemy(app)

# Data model
class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Task {self.id}"

with app.app_context():
    db.create_all()

# Home Page
@app.route("/", methods=["POST", "GET"])
def index():
    # Create a unique visitor_id if not already in session
    if 'visitor_id' not in session:
        session['visitor_id'] = str(uuid.uuid4())

    visitor_id = session['visitor_id']

    # Add Task
    if request.method == "POST":
        current_task = request.form['content']
        new_task = MyTask(content=current_task, visitor_id=visitor_id)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return f"ERROR: {e}"

    # Show Only Tasks for This Visitor
    else:
        tasks = MyTask.query.filter_by(visitor_id=visitor_id).order_by(MyTask.created).all()
        return render_template("index.html", tasks=tasks)

# Delete Task
@app.route("/delete/<int:id>")
def delete(id: int):
    task = MyTask.query.get_or_404(id)
    if task.visitor_id != session.get('visitor_id'):
        return "Unauthorized", 403

    try:
        db.session.delete(task)
        db.session.commit()
        return redirect("/")
    except Exception as e:
        return f"ERROR: {e}"

# Edit Task
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id: int):
    task = MyTask.query.get_or_404(id)
    if task.visitor_id != session.get('visitor_id'):
        return "Unauthorized", 403

    if request.method == "POST":
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return f"ERROR: {e}"
    else:
        return render_template("edit.html", task=task)

if __name__ == "__main__":
    app.run(debug=True)
