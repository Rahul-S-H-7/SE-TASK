"""
Database operations for the Smart Attendance Management System using SQLite.
"""
import sqlite3
from typing import List, Dict, Any, Optional
from attendance_logic import calculate_attendance, validate_status


def get_db_connection(db_path: str = "attendance.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str = "attendance.db") -> None:
    conn = get_db_connection(db_path)
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                course TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_date TEXT NOT NULL,
                subject TEXT NOT NULL,
                course TEXT NOT NULL,
                topic TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                student_id_ref INTEGER NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Present', 'Absent')),
                marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE,
                FOREIGN KEY (student_id_ref) REFERENCES students (id) ON DELETE CASCADE,
                UNIQUE (session_id, student_id_ref)
            );
        """)
    conn.close()


def add_student(student_id: str, name: str, course: str, db_path: str = "attendance.db") -> int:
    if not student_id or not student_id.strip():
        raise ValueError("Student ID cannot be empty")
    if not name or not name.strip():
        raise ValueError("Student name cannot be empty")
    if not course or not course.strip():
        raise ValueError("Course cannot be empty")

    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO students (student_id, name, course) VALUES (?, ?, ?)",
                (student_id.strip().upper(), name.strip(), course.strip())
            )
            return cursor.lastrowid
    finally:
        conn.close()


def create_session(session_date: str, subject: str, course: str, topic: str = "", db_path: str = "attendance.db") -> int:
    if not session_date or not session_date.strip():
        raise ValueError("Session date cannot be empty")
    if not subject or not subject.strip():
        raise ValueError("Subject cannot be empty")
    if not course or not course.strip():
        raise ValueError("Course cannot be empty")

    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sessions (session_date, subject, course, topic) VALUES (?, ?, ?, ?)",
                (session_date.strip(), subject.strip(), course.strip(), topic.strip())
            )
            return cursor.lastrowid
    finally:
        conn.close()


def mark_attendance(session_id: int, student_id_ref: int, status: str, db_path: str = "attendance.db") -> int:
    validated_status = validate_status(status)

    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            # Verify session exists
            cursor.execute("SELECT id FROM sessions WHERE id = ?", (session_id,))
            if not cursor.fetchone():
                raise ValueError(f"Session with ID {session_id} does not exist")

            # Verify student exists
            cursor.execute("SELECT id FROM students WHERE id = ?", (student_id_ref,))
            if not cursor.fetchone():
                raise ValueError(f"Student with ID {student_id_ref} does not exist")

            cursor.execute(
                "INSERT INTO attendance (session_id, student_id_ref, status) VALUES (?, ?, ?)",
                (session_id, student_id_ref, validated_status)
            )
            return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        if "UNIQUE" in str(e).upper():
            raise ValueError(f"Attendance for student {student_id_ref} in session {session_id} is already recorded")
        raise
    finally:
        conn.close()


def get_all_students(db_path: str = "attendance.db") -> List[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students ORDER BY student_id ASC")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_all_sessions(db_path: str = "attendance.db") -> List[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions ORDER BY session_date DESC, id DESC")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_session_attendance(session_id: int, db_path: str = "attendance.db") -> List[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, a.session_id, a.student_id_ref, a.status, a.marked_at,
                   s.student_id, s.name, s.course
            FROM attendance a
            JOIN students s ON a.student_id_ref = s.id
            WHERE a.session_id = ?
            ORDER BY s.student_id ASC
        """, (session_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_student_report(student_db_id: int, db_path: str = "attendance.db") -> Optional[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_db_id,))
        student = cursor.fetchone()
        if not student:
            return None

        course = student["course"]

        # Applicable conducted sessions for this student's course
        cursor.execute("SELECT COUNT(*) as total FROM sessions WHERE course = ?", (course,))
        total_sessions = cursor.fetchone()["total"]

        # Number of sessions attended (Present)
        cursor.execute("""
            SELECT COUNT(*) as attended
            FROM attendance a
            JOIN sessions s ON a.session_id = s.id
            WHERE a.student_id_ref = ? AND s.course = ? AND a.status = 'Present'
        """, (student_db_id, course))
        attended_sessions = cursor.fetchone()["attended"]

        calc = calculate_attendance(attended_sessions, total_sessions)

        # Full attendance history
        cursor.execute("""
            SELECT a.id, a.status, a.marked_at, s.session_date, s.subject, s.topic
            FROM attendance a
            JOIN sessions s ON a.session_id = s.id
            WHERE a.student_id_ref = ?
            ORDER BY s.session_date DESC, s.id DESC
        """, (student_db_id,))
        history = [dict(row) for row in cursor.fetchall()]

        return {
            "student": dict(student),
            "stats": calc,
            "history": history
        }
    finally:
        conn.close()


def get_dashboard_summary(db_path: str = "attendance.db") -> Dict[str, Any]:
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM students")
        student_count = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as total FROM sessions")
        session_count = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as total FROM attendance WHERE status = 'Present'")
        total_present = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) as total FROM attendance")
        total_records = cursor.fetchone()["total"]

        students = get_all_students(db_path)
        student_summaries = []
        for s in students:
            report = get_student_report(s["id"], db_path)
            if report:
                student_summaries.append({
                    "id": s["id"],
                    "student_id": s["student_id"],
                    "name": s["name"],
                    "course": s["course"],
                    "attended": report["stats"]["attended"],
                    "total": report["stats"]["total"],
                    "percentage": report["stats"]["percentage"],
                    "is_eligible": report["stats"]["is_eligible"],
                    "status_label": report["stats"]["status_label"]
                })

        return {
            "student_count": student_count,
            "session_count": session_count,
            "total_records": total_records,
            "total_present": total_present,
            "students": student_summaries
        }
    finally:
        conn.close()
