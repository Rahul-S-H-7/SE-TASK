"""
Flask Web Application for the Smart Attendance Management System.
"""
import os
from flask import Flask, render_template, request, redirect, url_for, flash
import db

app = Flask(__name__)
app.config["SECRET_KEY"] = "smart-attendance-secret-key-2026"
app.config["DB_PATH"] = os.path.join(os.path.dirname(__file__), "attendance.db")


@app.before_request
def setup_database():
    if not hasattr(app, "_db_initialized"):
        db.init_db(app.config["DB_PATH"])
        app._db_initialized = True


@app.route("/")
def dashboard():
    summary = db.get_dashboard_summary(app.config["DB_PATH"])
    return render_template("dashboard.html", summary=summary)


@app.route("/students", methods=["GET", "POST"])
def students():
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        name = request.form.get("name", "").strip()
        course = request.form.get("course", "").strip()

        if not student_id or not name or not course:
            flash("All student fields (Student ID, Name, Course) are required.", "danger")
            return redirect(url_for("students"))

        try:
            db.add_student(student_id, name, course, app.config["DB_PATH"])
            flash(f"Student '{name}' ({student_id}) enrolled successfully!", "success")
        except Exception as e:
            flash(f"Error adding student: {str(e)}", "danger")

        return redirect(url_for("students"))

    all_students = db.get_all_students(app.config["DB_PATH"])
    return render_template("students.html", students=all_students)


@app.route("/sessions", methods=["GET", "POST"])
def sessions():
    if request.method == "POST":
        session_date = request.form.get("session_date", "").strip()
        subject = request.form.get("subject", "").strip()
        course = request.form.get("course", "").strip()
        topic = request.form.get("topic", "").strip()

        if not session_date or not subject or not course:
            flash("Date, Subject, and Course are required fields.", "danger")
            return redirect(url_for("sessions"))

        try:
            db.create_session(session_date, subject, course, topic, app.config["DB_PATH"])
            flash(f"Session for '{subject}' ({course}) scheduled successfully!", "success")
        except Exception as e:
            flash(f"Error creating session: {str(e)}", "danger")

        return redirect(url_for("sessions"))

    all_sessions = db.get_all_sessions(app.config["DB_PATH"])
    return render_template("sessions.html", sessions=all_sessions)


@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    all_sessions = db.get_all_sessions(app.config["DB_PATH"])
    all_students = db.get_all_students(app.config["DB_PATH"])

    selected_session_id = request.args.get("session_id", type=int)
    if not selected_session_id and all_sessions:
        selected_session_id = all_sessions[0]["id"]

    if request.method == "POST":
        session_id = request.form.get("session_id", type=int)
        student_id_ref = request.form.get("student_id_ref", type=int)
        status = request.form.get("status", "").strip()

        if not session_id or not student_id_ref or not status:
            flash("Session, Student, and Status are all required.", "danger")
            return redirect(url_for("attendance", session_id=session_id))

        try:
            db.mark_attendance(session_id, student_id_ref, status, app.config["DB_PATH"])
            flash("Attendance marked successfully!", "success")
        except ValueError as ve:
            flash(f"Validation error: {str(ve)}", "danger")
        except Exception as e:
            flash(f"Error recording attendance: {str(e)}", "danger")

        return redirect(url_for("attendance", session_id=session_id))

    session_records = []
    selected_session = None
    if selected_session_id:
        session_records = db.get_session_attendance(selected_session_id, app.config["DB_PATH"])
        for s in all_sessions:
            if s["id"] == selected_session_id:
                selected_session = s
                break

    return render_template(
        "attendance.html",
        sessions=all_sessions,
        students=all_students,
        selected_session_id=selected_session_id,
        selected_session=selected_session,
        session_records=session_records
    )


@app.route("/report/<int:student_id>")
def student_report(student_id: int):
    report = db.get_student_report(student_id, app.config["DB_PATH"])
    if not report:
        flash("Student record not found.", "warning")
        return redirect(url_for("dashboard"))
    return render_template("report.html", report=report)


if __name__ == "__main__":
    db.init_db(app.config["DB_PATH"])
    app.run(debug=True, port=5000)
