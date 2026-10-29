"""
Student Management System
Tech stack: Python (Flask) + SQL (SQLite) + HTML + CSS + JavaScript
"""

import os
import re
import sqlite3

from flask import Flask, abort, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)

DB_NAME = os.path.join(os.path.dirname(__file__), "students.db")
VALID_BRANCHES = [
    "Computer Science",
    "Electronics",
    "Mechanical",
    "Civil",
    "Electrical",
]


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

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL UNIQUE,
            branch TEXT NOT NULL,
            semester INTEGER NOT NULL,
            email TEXT,
            phone TEXT,
            marks REAL NOT NULL
        )
    """
    )

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
        cursor.executemany(
            """
            INSERT INTO students (name, roll_no, branch, semester, email, phone, marks)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            sample_students,
        )

    conn.commit()
    conn.close()


def normalize_required_text(value, field_name, max_length=None):
    if value is None:
        raise ValueError(f"{field_name} is required.")

    text = " ".join(str(value).split()).strip()
    if not text:
        raise ValueError(f"{field_name} is required.")
    if max_length and len(text) > max_length:
        raise ValueError(f"{field_name} must be {max_length} characters or fewer.")
    return text


def validate_student_payload(form_data, student_id=None):
    name = normalize_required_text(form_data.get("name"), "Name", 100)
    roll_no = normalize_required_text(form_data.get("roll_no"), "Roll number", 30).upper()

    branch = normalize_required_text(form_data.get("branch"), "Branch").strip()
    if branch not in VALID_BRANCHES:
        raise ValueError("Please select a valid branch.")

    try:
        semester = int(form_data.get("semester", ""))
    except (TypeError, ValueError):
        raise ValueError("Semester must be a number from 1 to 8.") from None

    if semester < 1 or semester > 8:
        raise ValueError("Semester must be a number from 1 to 8.")

    email = (form_data.get("email") or "").strip()
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValueError("Please enter a valid email address.")

    phone = (form_data.get("phone") or "").strip()
    if phone:
        digits = re.sub(r"\D", "", phone)
        if len(digits) < 7 or len(digits) > 15:
            raise ValueError("Phone number must contain 7 to 15 digits.")
        phone = digits

    try:
        marks = float(form_data.get("marks", ""))
    except (TypeError, ValueError):
        raise ValueError("Marks must be a valid number between 0 and 100.") from None

    if marks < 0 or marks > 100:
        raise ValueError("Marks must be between 0 and 100.")

    duplicate_query = "SELECT id FROM students WHERE roll_no = ? AND id != ?"
    conn = get_db_connection()
    existing = conn.execute(duplicate_query, (roll_no, student_id or -1)).fetchone()
    conn.close()
    if existing:
        raise ValueError("Roll number already exists.")

    return {
        "name": name,
        "roll_no": roll_no,
        "branch": branch,
        "semester": semester,
        "email": email,
        "phone": phone,
        "marks": round(marks, 2),
    }


def fetch_student(student_id):
    conn = get_db_connection()
    student = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    conn.close()
    return student


# ---------------------------------------------------------
# ROUTES - PAGES
# ---------------------------------------------------------
@app.route("/")
def index():
    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students ORDER BY id").fetchall()
    conn.close()
    return render_template("index.html", students=students, valid_branches=VALID_BRANCHES)


@app.route("/add", methods=["GET", "POST"])
def add_student():
    if request.method == "POST":
        form_data = request.form.to_dict()
        try:
            student_data = validate_student_payload(form_data)
        except ValueError as exc:
            return render_template("add.html", error=str(exc), form_data=form_data, valid_branches=VALID_BRANCHES)

        conn = get_db_connection()
        try:
            conn.execute(
                """
                INSERT INTO students (name, roll_no, branch, semester, email, phone, marks)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    student_data["name"],
                    student_data["roll_no"],
                    student_data["branch"],
                    student_data["semester"],
                    student_data["email"],
                    student_data["phone"],
                    student_data["marks"],
                ),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            return render_template(
                "add.html",
                error="Roll number already exists.",
                form_data=form_data,
                valid_branches=VALID_BRANCHES,
            )
        finally:
            conn.close()

        return redirect(url_for("index"))

    return render_template("add.html", valid_branches=VALID_BRANCHES)


@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    student = fetch_student(student_id)
    if student is None:
        abort(404)

    if request.method == "POST":
        form_data = request.form.to_dict()
        try:
            student_data = validate_student_payload(form_data, student_id=student_id)
        except ValueError as exc:
            return render_template(
                "edit.html",
                student=dict(student),
                error=str(exc),
                form_data=form_data,
                valid_branches=VALID_BRANCHES,
            )

        conn = get_db_connection()
        try:
            conn.execute(
                """
                UPDATE students
                SET name=?, roll_no=?, branch=?, semester=?, email=?, phone=?, marks=?
                WHERE id=?
                """,
                (
                    student_data["name"],
                    student_data["roll_no"],
                    student_data["branch"],
                    student_data["semester"],
                    student_data["email"],
                    student_data["phone"],
                    student_data["marks"],
                    student_id,
                ),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            return render_template(
                "edit.html",
                student=dict(student),
                error="Roll number already exists.",
                form_data=form_data,
                valid_branches=VALID_BRANCHES,
            )
        finally:
            conn.close()

        return redirect(url_for("index"))

    return render_template("edit.html", student=student, valid_branches=VALID_BRANCHES)


@app.route("/delete/<int:student_id>")
def delete_student(student_id):
    if fetch_student(student_id) is None:
        abort(404)

    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/view/<int:student_id>")
def view_student(student_id):
    student = fetch_student(student_id)
    if student is None:
        abort(404)
    return render_template("view.html", student=student)


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


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
    students = conn.execute(
        """
        SELECT * FROM students
        WHERE name LIKE ? OR roll_no LIKE ? OR branch LIKE ?
        ORDER BY id
        """,
        (f"%{query}%", f"%{query}%", f"%{query}%"),
    ).fetchall()
    conn.close()
    return jsonify([dict(s) for s in students])


@app.route("/api/stats")
def api_stats():
    conn = get_db_connection()
    total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    avg_marks = conn.execute("SELECT AVG(marks) FROM students").fetchone()[0]
    branch_counts = conn.execute(
        """
        SELECT branch, COUNT(*) as count FROM students GROUP BY branch
        """
    ).fetchall()
    conn.close()
    return jsonify(
        {
            "total": total,
            "avg_marks": round(avg_marks, 2) if avg_marks is not None else 0,
            "branch_counts": [dict(b) for b in branch_counts],
        }
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
