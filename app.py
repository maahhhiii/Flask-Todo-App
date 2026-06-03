from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# -----------------------------
# Database Model
# -----------------------------
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

    complete = db.Column(db.Boolean, default=False)

    priority = db.Column(db.String(20), default="Medium")

    category = db.Column(db.String(50), default="Personal")

    due_date = db.Column(db.Date)

    def __repr__(self):
        return f"<Task {self.id}>"


# -----------------------------
# Home Page
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        title = request.form["title"]

        priority = request.form["priority"]

        category = request.form["category"]

        due_date_str = request.form["due_date"]

        due_date = (
            datetime.strptime(due_date_str, "%Y-%m-%d").date()
            if due_date_str
            else None
        )

        new_task = Todo(
            title=title,
            priority=priority,
            category=category,
            due_date=due_date,
        )

        db.session.add(new_task)
        db.session.commit()

        return redirect("/")

    search = request.args.get("search")

    if search:
        tasks = Todo.query.filter(
            Todo.title.contains(search)
        ).all()
    else:
        tasks = Todo.query.all()

    total = Todo.query.count()

    completed = Todo.query.filter_by(
        complete=True
    ).count()

    pending = total - completed

    progress = 0

    if total > 0:
        progress = round((completed / total) * 100)

    return render_template(
        "index.html",
        tasks=tasks,
        total=total,
        completed=completed,
        pending=pending,
        progress=progress,
    )


# -----------------------------
# Complete Task
# -----------------------------
@app.route("/complete/<int:id>")
def complete(id):

    task = Todo.query.get_or_404(id)

    task.complete = not task.complete

    db.session.commit()

    return redirect("/")


# -----------------------------
# Delete Task
# -----------------------------
@app.route("/delete/<int:id>")
def delete(id):

    task = Todo.query.get_or_404(id)

    db.session.delete(task)

    db.session.commit()

    return redirect("/")


# -----------------------------
# Edit Task
# -----------------------------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    task = Todo.query.get_or_404(id)

    if request.method == "POST":

        task.title = request.form["title"]

        task.priority = request.form["priority"]

        task.category = request.form["category"]

        due_date_str = request.form["due_date"]

        task.due_date = (
            datetime.strptime(
                due_date_str,
                "%Y-%m-%d"
            ).date()
            if due_date_str
            else None
        )

        db.session.commit()

        return redirect("/")

    return render_template(
        "edit.html",
        task=task
    )


# -----------------------------
# Create Database
# -----------------------------
with app.app_context():
    db.create_all()


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)