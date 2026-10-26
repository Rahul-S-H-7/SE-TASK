"""
Attendance calculation and eligibility business logic.
Provides pure, standalone functions with zero web/database dependencies.
"""
from typing import Dict, Any

ELIGIBILITY_THRESHOLD = 75.0


def calculate_attendance(attended_classes: int, conducted_classes: int) -> Dict[str, Any]:
    """
    Calculate attendance percentage and exam eligibility.

    Business Rules:
    1. If conducted_classes is 0, percentage is 0.0% and eligibility is False.
    2. attended_classes cannot be negative.
    3. conducted_classes cannot be negative.
    4. attended_classes cannot exceed conducted_classes.
    5. Percentage equals (attended_classes / conducted_classes) * 100, rounded to 2 decimal places.
    6. Attendance percentage exactly >= 75.0% is eligible (is_eligible = True).
    7. Attendance percentage < 75.0% is not eligible (is_eligible = False).
    8. Valid percentages remain between 0.0% and 100.0%.
    """
    if not isinstance(attended_classes, int) or not isinstance(conducted_classes, int):
        raise TypeError("attended_classes and conducted_classes must be integers")

    if attended_classes < 0:
        raise ValueError("attended_classes cannot be negative")

    if conducted_classes < 0:
        raise ValueError("conducted_classes cannot be negative")

    if attended_classes > conducted_classes:
        raise ValueError("attended_classes cannot exceed conducted_classes")

    if conducted_classes == 0:
        return {
            "attended": 0,
            "total": 0,
            "percentage": 0.0,
            "is_eligible": False,
            "status_label": "Not Eligible (No Classes Conducted)"
        }

    percentage = round((attended_classes / conducted_classes) * 100.0, 2)
    is_eligible = percentage >= ELIGIBILITY_THRESHOLD

    return {
        "attended": attended_classes,
        "total": conducted_classes,
        "percentage": percentage,
        "is_eligible": is_eligible,
        "status_label": "Eligible" if is_eligible else "Not Eligible"
    }


def validate_status(status: str) -> str:
    """
    Validates attendance status string.
    Must be either 'Present' or 'Absent'.
    """
    if not isinstance(status, str):
        raise TypeError("status must be a string")

    normalized = status.strip().capitalize()
    if normalized not in ("Present", "Absent"):
        raise ValueError("status must be either 'Present' or 'Absent'")

    return normalized
