"""
Automated unit and integration tests for the Smart Attendance Management System.
Covers business logic, edge conditions, database operations, and duplicate prevention.
"""
import os
import pytest
import sqlite3
from attendance_logic import calculate_attendance, validate_status, ELIGIBILITY_THRESHOLD
import db


# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

@pytest.fixture
def temp_db(tmp_path):
    """Provides a fresh, temporary SQLite database for test isolation."""
    db_file = str(tmp_path / "test_attendance.db")
    db.init_db(db_file)
    return db_file


# --------------------------------------------------------------------------
# Business Logic Tests (Pure Unit Tests)
# --------------------------------------------------------------------------

def test_zero_classes_conducted():
    """Rule 5 & 1: If 0 conducted classes, percentage must be 0.0% and ineligible."""
    result = calculate_attendance(0, 0)
    assert result["percentage"] == 0.0
    assert result["is_eligible"] is False
    assert result["attended"] == 0
    assert result["total"] == 0


def test_100_percent_attendance():
    """Rule 4, 6 & 8: All conducted sessions attended yields 100% and eligible."""
    result = calculate_attendance(20, 20)
    assert result["percentage"] == 100.0
    assert result["is_eligible"] is True


def test_exactly_75_percent_boundary():
    """Rule 6: Exactly 75.0% attendance qualifies as eligible."""
    result = calculate_attendance(3, 4)
    assert result["percentage"] == 75.0
    assert result["is_eligible"] is True


def test_just_below_75_percent_ineligible():
    """Rule 7: Below 75% does not qualify."""
    # 74 out of 100 = 74.0%
    result = calculate_attendance(74, 100)
    assert result["percentage"] == 74.0
    assert result["is_eligible"] is False


def test_correct_percentage_rounding():
    """Rule 4: Percentage rounded to 2 decimal places (2/3 = 66.67%)."""
    result = calculate_attendance(2, 3)
    assert result["percentage"] == 66.67
    assert result["is_eligible"] is False


def test_boundary_just_above_75_percent():
    """Attendance just above 75% is eligible."""
    # 38 out of 50 = 76.0%
    result = calculate_attendance(38, 50)
    assert result["percentage"] == 76.0
    assert result["is_eligible"] is True


def test_invalid_negative_attended_classes():
    """Negative attended classes must raise ValueError."""
    with pytest.raises(ValueError, match="attended_classes cannot be negative"):
        calculate_attendance(-1, 10)


def test_invalid_negative_conducted_classes():
    """Negative conducted classes must raise ValueError."""
    with pytest.raises(ValueError, match="conducted_classes cannot be negative"):
        calculate_attendance(5, -10)


def test_attended_exceeds_conducted_classes():
    """Attended cannot exceed conducted classes."""
    with pytest.raises(ValueError, match="attended_classes cannot exceed conducted_classes"):
        calculate_attendance(15, 10)


def test_invalid_types_raise_type_error():
    """Non-integer types must raise TypeError."""
    with pytest.raises(TypeError):
        calculate_attendance("10", 20)  # type: ignore
    with pytest.raises(TypeError):
        calculate_attendance(10, "20")  # type: ignore


def test_validate_status_valid_values():
    """Status validation handles Present and Absent case-insensitively."""
    assert validate_status("Present") == "Present"
    assert validate_status("absent") == "Absent"
    assert validate_status(" PRESENT ") == "Present"


def test_validate_status_invalid_value():
    """Invalid status values raise ValueError."""
    with pytest.raises(ValueError, match="status must be either 'Present' or 'Absent'"):
        validate_status("Late")
    with pytest.raises(ValueError):
        validate_status("Excused")


# --------------------------------------------------------------------------
# Database and Integration Tests
# --------------------------------------------------------------------------

def test_database_persistence_and_student_addition(temp_db):
    """Students can be added and persisted in the SQLite database."""
    sid = db.add_student("NU24UCA001", "Alice Sharma", "BCA 5th Sem", db_path=temp_db)
    assert sid > 0

    students = db.get_all_students(db_path=temp_db)
    assert len(students) == 1
    assert students[0]["student_id"] == "NU24UCA001"
    assert students[0]["name"] == "Alice Sharma"
    assert students[0]["course"] == "BCA 5th Sem"


def test_student_unique_id_constraint(temp_db):
    """Rule 1: Student IDs must be unique; duplicate insertion must fail."""
    db.add_student("NU24UCA001", "Alice", "BCA 5th Sem", db_path=temp_db)
    with pytest.raises(sqlite3.IntegrityError):
        db.add_student("NU24UCA001", "Bob", "BCA 5th Sem", db_path=temp_db)


def test_duplicate_attendance_prevention(temp_db):
    """Rule 3 & 10: Each student can have only one attendance record per session."""
    st_id = db.add_student("NU24UCA001", "Alice", "BCA 5th Sem", db_path=temp_db)
    ses_id = db.create_session("2026-10-26", "Software Engineering", "BCA 5th Sem", db_path=temp_db)

    # First marking succeeds
    rec_id = db.mark_attendance(ses_id, st_id, "Present", db_path=temp_db)
    assert rec_id > 0

    # Second marking for identical session + student must raise duplicate error
    with pytest.raises(ValueError, match="already recorded"):
        db.mark_attendance(ses_id, st_id, "Absent", db_path=temp_db)


def test_nonexistent_student_attendance_rejected(temp_db):
    """Marking attendance for nonexistent student ID raises ValueError."""
    ses_id = db.create_session("2026-10-26", "Software Engineering", "BCA 5th Sem", db_path=temp_db)
    with pytest.raises(ValueError, match="Student with ID 999 does not exist"):
        db.mark_attendance(ses_id, 999, "Present", db_path=temp_db)


def test_nonexistent_session_attendance_rejected(temp_db):
    """Marking attendance for nonexistent session ID raises ValueError."""
    st_id = db.add_student("NU24UCA001", "Alice", "BCA 5th Sem", db_path=temp_db)
    with pytest.raises(ValueError, match="Session with ID 999 does not exist"):
        db.mark_attendance(999, st_id, "Present", db_path=temp_db)


def test_missing_student_details_rejected(temp_db):
    """Empty student details must be rejected."""
    with pytest.raises(ValueError, match="Student ID cannot be empty"):
        db.add_student("", "Alice", "BCA", db_path=temp_db)
    with pytest.raises(ValueError, match="Student name cannot be empty"):
        db.add_student("NU24UCA001", "   ", "BCA", db_path=temp_db)
    with pytest.raises(ValueError, match="Course cannot be empty"):
        db.add_student("NU24UCA001", "Alice", "", db_path=temp_db)


def test_independent_calculations_multiple_students(temp_db):
    """Attendance and eligibility are calculated independently for multiple students."""
    # Enrolling two students
    s1 = db.add_student("NU24UCA001", "Alice", "BCA 5th Sem", db_path=temp_db)
    s2 = db.add_student("NU24UCA002", "Bob", "BCA 5th Sem", db_path=temp_db)

    # Creating 4 sessions for BCA 5th Sem
    ses1 = db.create_session("2026-10-20", "SE", "BCA 5th Sem", db_path=temp_db)
    ses2 = db.create_session("2026-10-21", "SE", "BCA 5th Sem", db_path=temp_db)
    ses3 = db.create_session("2026-10-22", "SE", "BCA 5th Sem", db_path=temp_db)
    ses4 = db.create_session("2026-10-23", "SE", "BCA 5th Sem", db_path=temp_db)

    # Alice attends 3 out of 4 sessions -> 75.0% -> Eligible
    db.mark_attendance(ses1, s1, "Present", db_path=temp_db)
    db.mark_attendance(ses2, s1, "Present", db_path=temp_db)
    db.mark_attendance(ses3, s1, "Present", db_path=temp_db)
    db.mark_attendance(ses4, s1, "Absent", db_path=temp_db)

    # Bob attends 2 out of 4 sessions -> 50.0% -> Ineligible
    db.mark_attendance(ses1, s2, "Present", db_path=temp_db)
    db.mark_attendance(ses2, s2, "Present", db_path=temp_db)
    db.mark_attendance(ses3, s2, "Absent", db_path=temp_db)
    db.mark_attendance(ses4, s2, "Absent", db_path=temp_db)

    report_alice = db.get_student_report(s1, db_path=temp_db)
    report_bob = db.get_student_report(s2, db_path=temp_db)

    assert report_alice["stats"]["attended"] == 3
    assert report_alice["stats"]["total"] == 4
    assert report_alice["stats"]["percentage"] == 75.0
    assert report_alice["stats"]["is_eligible"] is True

    assert report_bob["stats"]["attended"] == 2
    assert report_bob["stats"]["total"] == 4
    assert report_bob["stats"]["percentage"] == 50.0
    assert report_bob["stats"]["is_eligible"] is False
