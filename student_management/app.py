"""
Student Management System
Tech stack: Python (Flask) + SQL (SQLite) + HTML + CSS + JavaScript
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_NAME = os.path.join(os.path.dirname(__file__), "students.db")


# ---------------------------------------------------------
# DATABASE SETUP
# ---------------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL UNIQUE,
            branch TEXT NOT NULL,
            semester INTEGER NOT NULL,
            email TEXT,
            phone TEXT,
            marks REAL
        )
    """)

    # Insert sample data only if table is empty
    cursor.execute("SELECT COUNT(*) FROM students")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_students = [
            ("Aarav Sharma", "CS101", "Computer Science", 3, "aarav.sharma@email.com", "9876543210", 88.5),
            ("Priya Verma", "CS102", "Computer Science", 3, "priya.verma@email.com", "9876543211", 92.0),
            ("Rohan Gupta", "EC101", "Electronics", 5, "rohan.gupta@email.com", "9876543212", 75.3),
            ("Sneha Reddy", "ME101", "Mechanical", 2, "sneha.reddy@email.com", "9876543213", 81.0),
            ("Vikram Singh", "CS103", "Computer Science", 1, "vikram.singh@email.com", "9876543214", 69.8),
            ("Anjali Nair", "CE101", "Civil", 4, "anjali.nair@email.com", "9876543215", 85.6),
            ("Karan Mehta", "EC102", "Electronics", 6, "karan.mehta@email.com", "9876543216", 78.2),
            ("Isha Kapoor", "ME102", "Mechanical", 3, "isha.kapoor@email.com", "9876543217", 90.1),
            ("Aditya Joshi", "CS104", "Computer Science", 7, "aditya.joshi@email.com", "9876543218", 94.4),
            ("Meera Iyer", "CE102", "Civil", 2, "meera.iyer@email.com", "9876543219", 73.9),
        ]
        cursor.executemany("""
            INSERT INTO students (name, roll_no, branch, semester, email, phone, marks)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, sample_students)

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# ROUTES - PAGES
# ---------------------------------------------------------
@app.route("/")
def index():
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students ORDER BY id").fetchall()
    conn.close()
    return render_template("index.html", students=students)


@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        name = request.form["name"]
        roll_no = request.form["roll_no"]
        branch = request.form["branch"]
        semester = request.form["semester"]
        email = request.form["email"]
        phone = request.form["phone"]
        marks = request.form["marks"]

        conn = get_db_connection()
        try:
            conn.execute("""
                INSERT INTO students (name, roll_no, branch, semester, email, phone, marks)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, roll_no, branch, semester, email, phone, marks))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("add.html", error="Roll number already exists!")
        conn.close()
        return redirect(url_for("index"))

    return render_template("add.html")


@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form["name"]
        roll_no = request.form["roll_no"]
        branch = request.form["branch"]
        semester = request.form["semester"]
        email = request.form["email"]
        phone = request.form["phone"]
        marks = request.form["marks"]

        conn.execute("""
            UPDATE students
            SET name=?, roll_no=?, branch=?, semester=?, email=?, phone=?, marks=?
            WHERE id=?
        """, (name, roll_no, branch, semester, email, phone, marks, student_id))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    student = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
    conn.close()
    return render_template("edit.html", student=student)


@app.route("/delete/<int:student_id>")
def delete_student(student_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/view/<int:student_id>")
def view_student(student_id):
    conn = get_db_connection()
    student = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
    conn.close()
    return render_template("view.html", student=student)


# ---------------------------------------------------------
# ROUTES - JSON API (used by JS for search / stats)
# ---------------------------------------------------------
@app.route("/api/students")
def api_students():
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students ORDER BY id").fetchall()
    conn.close()
    return jsonify([dict(s) for s in students])


@app.route("/api/search")
def api_search():
    query = request.args.get("q", "").strip()
    conn = get_db_connection()
    students = conn.execute("""
        SELECT * FROM students
        WHERE name LIKE ? OR roll_no LIKE ? OR branch LIKE ?
        ORDER BY id
    """, (f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()
    conn.close()
    return jsonify([dict(s) for s in students])


@app.route("/api/stats")
def api_stats():
    conn = get_db_connection()
    total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    avg_marks = conn.execute("SELECT AVG(marks) FROM students").fetchone()[0]
    branch_counts = conn.execute("""
        SELECT branch, COUNT(*) as count FROM students GROUP BY branch
    """).fetchall()
    conn.close()
    return jsonify({
        "total": total,
        "avg_marks": round(avg_marks, 2) if avg_marks else 0,
        "branch_counts": [dict(b) for b in branch_counts]
    })


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
