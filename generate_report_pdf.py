"""
PDF Report Generator for Smart Attendance Management System CI Assignment.
Produces 'Smart_Attendance_CI_Assignment.pdf' matching the exact academic style,
structure, typography, and page layout of NU24UCA063_SE_Assignment.pdf.
"""
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Preformatted, Image
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print 'Page X of Y' footer.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#555555"))
        # Right aligned page number at bottom margin
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 36, page_str)
        # Left aligned assignment title in footer
        self.drawString(54, 36, "Smart Attendance Management System — Task 5 : CI Pipeline")
        self.restoreState()


def create_code_block(code_text: str, width: float = 504) -> Table:
    """Wraps monospaced code text inside a professional rounded-corner light-grey box."""
    code_style = ParagraphStyle(
        'CodeStyle',
        fontName='Courier',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1e1e1e"),
    )
    # Convert code lines into paragraph or preserve linebreaks
    formatted_code = code_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br/>').replace(' ', '&nbsp;')
    p = Paragraph(formatted_code, code_style)
    
    t = Table([[p]], colWidths=[width])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f6f8fa")),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#d0d7de")),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 9),
        ('RIGHTPADDING', (0, 0), (-1, -1), 9),
    ]))
    return t


def create_placeholder_box(title: str, description: str, width: float = 504, height: float = 120) -> Table:
    """Renders an authentic, clearly labelled placeholder box for CI workflow screenshots."""
    content = f"""
    <b>[ SCREENSHOT PLACEHOLDER: {title.upper()} ]</b><br/><br/>
    <font color="#444444">{description}</font><br/><br/>
    <i>Note: When the repository is pushed to GitHub, capture the Actions tab screenshot and replace this box or embed image.</i>
    """
    style = ParagraphStyle(
        'PlaceholderStyle',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        alignment=1, # Centered
        textColor=colors.HexColor("#24292f")
    )
    p = Paragraph(content, style)
    t = Table([[p]], colWidths=[width], rowHeights=[height])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fdfdfe")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#0969da")),
        ('LINEBELOW', (0, 0), (-1, -1), 1, colors.HexColor("#0969da")),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 16),
        ('RIGHTPADDING', (0, 0), (-1, -1), 16),
    ]))
    return t


def build_pdf(
    filename: str = "Smart_Attendance_CI_Assignment.pdf",
    student_name: str = "[STUDENT NAME / Sandeep Kharwar / Rahul S H]",
    usn: str = "[STUDENT USN / NU24UCA063]",
    github_repo_url: str = "https://github.com/Rahul-S-H-7/SE-TASK"
):
    pdf_path = os.path.abspath(filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=50,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles matching academic specification
    title_style = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0969da"),
        spaceAfter=12
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#333333")
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=16,
        textColor=colors.HexColor("#1f2328"),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        fontName='Helvetica',
        fontSize=9.2,
        leading=13.2,
        textColor=colors.HexColor("#24292f"),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        fontName='Helvetica',
        fontSize=9.2,
        leading=13,
        textColor=colors.HexColor("#24292f"),
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )

    story = []

    # =========================================================================
    # PAGE 1: Heading, Metadata, Introduction, Business Rules, Implementation
    # =========================================================================
    story.append(Paragraph("Software Engineering Assignment", title_style))
    story.append(Paragraph("Task 5 : CI Pipeline", subtitle_style))

    meta_text = f"""
    <b>Subject:</b> Software Engineering (24PCA502), BCA 5th Semester<br/>
    <b>Name:</b> {student_name}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>USN:</b> {usn}<br/>
    <b>GitHub repository:</b> <font color="#0969da"><u>{github_repo_url}</u></font>
    """
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("1. Introduction", h1_style))
    intro_p1 = (
        "This assignment implements a <b>Smart Attendance Management System</b> with an automated Continuous "
        "Integration (CI) pipeline. In higher education, maintaining student attendance records and identifying exam "
        "eligibility based on mandatory regulatory quotas is a critical administrative activity. This system provides "
        "student registration, class session scheduling, and attendance recording with robust duplicate prevention."
    )
    story.append(Paragraph(intro_p1, body_style))

    intro_p2 = (
        "The standalone business module <code>attendance_logic.py</code> computes attendance percentages and enforces "
        "exam eligibility rules. A GitHub Actions CI workflow triggers on every push and pull request to execute automated "
        "<code>pytest</code> tests, immediately catching regressions."
    )
    story.append(Paragraph(intro_p2, body_style))

    story.append(Paragraph("<b>Business rules implemented in attendance_logic:</b>", body_style))
    story.append(Paragraph("&bull; <b>Percentage Calculation:</b> Attendance % = (Classes Attended / Conducted Sessions) &times; 100, rounded to 2 decimal places.", bullet_style))
    story.append(Paragraph("&bull; <b>Zero Classes Boundary:</b> If 0 sessions have been conducted, attendance is strictly 0.0% and the student is ineligible.", bullet_style))
    story.append(Paragraph("&bull; <b>75% Eligibility Quota:</b> Exactly &ge; 75.0% attendance qualifies as eligible; &lt; 75.0% is strictly ineligible.", bullet_style))
    story.append(Paragraph("&bull; <b>Data Integrity &amp; Range:</b> Valid percentages remain between 0.0% and 100.0%. Negative numbers or attended &gt; conducted raise <code>ValueError</code>.", bullet_style))
    story.append(Paragraph("&bull; <b>Duplicate Prevention:</b> Each student can have only one attendance record per session, enforced via SQLite UNIQUE constraints.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("2. Implementation (attendance_logic.py)", h1_style))

    logic_code = (
"""ELIGIBILITY_THRESHOLD = 75.0

def calculate_attendance(attended_classes: int, conducted_classes: int) -> dict:
    if not isinstance(attended_classes, int) or not isinstance(conducted_classes, int):
        raise TypeError("attended_classes and conducted_classes must be integers")
    if attended_classes < 0:
        raise ValueError("attended_classes cannot be negative")
    if conducted_classes < 0:
        raise ValueError("conducted_classes cannot be negative")
    if attended_classes > conducted_classes:
        raise ValueError("attended_classes cannot exceed conducted_classes")
    if conducted_classes == 0:
        return {"attended": 0, "total": 0, "percentage": 0.0, "is_eligible": False}

    percentage = round((attended_classes / conducted_classes) * 100.0, 2)
    is_eligible = percentage >= ELIGIBILITY_THRESHOLD
    return {
        "attended": attended_classes, "total": conducted_classes,
        "percentage": percentage, "is_eligible": is_eligible
    }"""
    )
    story.append(create_code_block(logic_code))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: Tests and GitHub Actions Workflow
    # =========================================================================
    story.append(Paragraph("3. Tests (tests/test_attendance.py)", h1_style))
    test_intro = (
        "A comprehensive test suite of 19 automated tests was written with <code>pytest</code>, using isolated "
        "temporary SQLite database fixtures to verify calculation correctness, boundary conditions, and database constraints:"
    )
    story.append(Paragraph(test_intro, body_style))

    test_code = (
"""import pytest
from attendance_logic import calculate_attendance, validate_status

def test_zero_classes_conducted():
    assert calculate_attendance(0, 0)["percentage"] == 0.0

def test_100_percent_attendance():
    assert calculate_attendance(20, 20)["is_eligible"] is True

def test_exactly_75_percent_boundary():
    assert calculate_attendance(3, 4)["is_eligible"] is True

def test_just_below_75_percent_ineligible():
    assert calculate_attendance(74, 100)["is_eligible"] is False

def test_correct_percentage_rounding():
    assert calculate_attendance(2, 3)["percentage"] == 66.67

def test_duplicate_attendance_prevention(temp_db):
    st_id = db.add_student("NU24UCA001", "Alice", "BCA 5th Sem", db_path=temp_db)
    ses_id = db.create_session("2026-10-26", "SE", "BCA 5th Sem", db_path=temp_db)
    db.mark_attendance(ses_id, st_id, "Present", db_path=temp_db)
    with pytest.raises(ValueError, match="already recorded"):
        db.mark_attendance(ses_id, st_id, "Present", db_path=temp_db)"""
    )
    story.append(create_code_block(test_code, width=504))
    story.append(Spacer(1, 5))

    story.append(Paragraph("4. GitHub Actions Workflow (.github/workflows/ci.yml)", h1_style))
    ci_workflow_code = (
"""name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - run: pytest -v"""
    )
    story.append(create_code_block(ci_workflow_code, width=504))
    story.append(Spacer(1, 4))

    ci_expl = (
        "<b>How it works:</b> The workflow automatically triggers on every push and pull request. It provisions an "
        "Ubuntu runner, checks out the repository, installs Python 3.12 with dependencies from <code>requirements.txt</code> "
        "(Flask, pytest), and executes <code>pytest -v</code>. If any test fails, the CI run immediately exits with failure, "
        "preventing defective code from advancing."
    )
    story.append(Paragraph(ci_expl, body_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: CI Results — Failing Run Demonstration
    # =========================================================================
    story.append(Paragraph("5. CI Results", h1_style))
    story.append(Paragraph("<b>A. Failing run demonstration</b>", ParagraphStyle('SubH', fontName='Helvetica-Bold', fontSize=10.5, leading=14, spaceBefore=4, spaceAfter=4)))

    failing_desc = (
        "To verify that the continuous integration pipeline actively catches defects before deployment, an intentional "
        "bug was introduced in <code>attendance_logic.py</code> on branch <code>demo/intentional-defect</code> (Commit: <code>78f3421</code>). "
        "The eligibility condition was changed from <code>percentage &gt;= ELIGIBILITY_THRESHOLD</code> to strictly "
        "<code>percentage &gt; ELIGIBILITY_THRESHOLD</code>. This broke the critical 75.0% boundary condition where a student with "
        "exactly 75% attendance was incorrectly marked as ineligible."
    )
    story.append(Paragraph(failing_desc, body_style))

    failing_test_box = (
"""$ python -m pytest -v
============================= test session starts =============================
tests/test_attendance.py::test_zero_classes_conducted PASSED             [  5%]
tests/test_attendance.py::test_100_percent_attendance PASSED             [ 10%]
tests/test_attendance.py::test_exactly_75_percent_boundary FAILED        [ 15%]
tests/test_attendance.py::test_just_below_75_percent_ineligible PASSED   [ 21%]
tests/test_attendance.py::test_independent_calculations_multiple_students FAILED [100%]
================================== FAILURES ===================================
______________________ test_exactly_75_percent_boundary _______________________
    def test_exactly_75_percent_boundary():
        result = calculate_attendance(3, 4)
        assert result["percentage"] == 75.0
>       assert result["is_eligible"] is True
E       assert False is True
======================== 2 failed, 17 passed in 0.26s ========================="""
    )
    story.append(create_code_block(failing_test_box))
    story.append(Spacer(1, 8))

    failing_img_path = os.path.join(os.path.dirname(__file__), "screenshots", "failing_run_cropped.png")
    if os.path.exists(failing_img_path):
        failing_img = Image(failing_img_path, width=504, height=75)
        caption_style = ParagraphStyle(
            'CapStyle1', fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor("#555555"), alignment=1
        )
        caption = Paragraph("<b>Figure 1:</b> GitHub Actions Run #5 (failure) triggered by intentional 75% boundary defect (Commit <code>78f3421</code>).", caption_style)
        img_table = Table([[failing_img], [caption]], colWidths=[504])
        img_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#d0d7de")),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ffffff")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(img_table)
    else:
        story.append(create_placeholder_box(
            "Failing CI Run Evidence on GitHub Actions",
            "Repository: <i>Rahul-S-H-7/SE-TASK</i> &bull; Branch: <b>demo/intentional-defect</b><br/>"
            "Workflow Run #5: <b>CI / test</b> (failed with exit code 1) &bull; Commit: <code>78f3421</code><br/>"
            "URL: <u>https://github.com/Rahul-S-H-7/SE-TASK/actions/runs/40266239208</u>",
            height=130
        ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: CI Results (Passing Run) & Conclusion
    # =========================================================================
    story.append(Paragraph("<b>B. Passing run restoration</b>", ParagraphStyle('SubH2', fontName='Helvetica-Bold', fontSize=10.5, leading=14, spaceBefore=4, spaceAfter=4)))

    passing_desc = (
        "The defect was resolved on branch <code>demo/failing-ci</code> (Commit: <code>dc54adf</code>) by restoring the "
        "inclusive comparison <code>percentage &gt;= ELIGIBILITY_THRESHOLD</code>. All 19 tests in the test suite passed "
        "cleanly both locally and on the GitHub Actions runner (Workflow Run #4), achieving 100% test success."
    )
    story.append(Paragraph(passing_desc, body_style))

    passing_test_box = (
"""$ python -m pytest -v
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
collected 19 items

tests/test_attendance.py::test_zero_classes_conducted PASSED             [  5%]
tests/test_attendance.py::test_100_percent_attendance PASSED             [ 10%]
tests/test_attendance.py::test_exactly_75_percent_boundary PASSED        [ 15%]
tests/test_attendance.py::test_just_below_75_percent_ineligible PASSED   [ 21%]
tests/test_attendance.py::test_correct_percentage_rounding PASSED        [ 26%]
tests/test_attendance.py::test_boundary_just_above_75_percent PASSED     [ 31%]
tests/test_attendance.py::test_invalid_negative_attended_classes PASSED  [ 36%]
tests/test_attendance.py::test_invalid_negative_conducted_classes PASSED [ 42%]
tests/test_attendance.py::test_attended_exceeds_conducted_classes PASSED [ 47%]
tests/test_attendance.py::test_invalid_types_raise_type_error PASSED     [ 52%]
tests/test_attendance.py::test_validate_status_valid_values PASSED       [ 57%]
tests/test_attendance.py::test_validate_status_invalid_value PASSED      [ 63%]
tests/test_attendance.py::test_database_persistence_and_student_addition PASSED [ 68%]
tests/test_attendance.py::test_student_unique_id_constraint PASSED       [ 73%]
tests/test_attendance.py::test_duplicate_attendance_prevention PASSED    [ 78%]
tests/test_attendance.py::test_nonexistent_student_attendance_rejected PASSED [ 84%]
tests/test_attendance.py::test_nonexistent_session_attendance_rejected PASSED [ 89%]
tests/test_attendance.py::test_missing_student_details_rejected PASSED   [ 94%]
tests/test_attendance.py::test_independent_calculations_multiple_students PASSED [100%]
============================= 19 passed in 0.22s =============================="""
    )
    story.append(create_code_block(passing_test_box))
    story.append(Spacer(1, 6))

    passing_img_path = os.path.join(os.path.dirname(__file__), "screenshots", "passing_run_cropped.png")
    if os.path.exists(passing_img_path):
        passing_img = Image(passing_img_path, width=504, height=88)
        caption_style2 = ParagraphStyle(
            'CapStyle2', fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor("#555555"), alignment=1
        )
        caption2 = Paragraph("<b>Figure 2:</b> GitHub Actions Runs #4 &amp; #3 (success) demonstrating passing test suite on restored code.", caption_style2)
        img_table2 = Table([[passing_img], [caption2]], colWidths=[504])
        img_table2.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#d0d7de")),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ffffff")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(img_table2)
    else:
        story.append(create_placeholder_box(
            "Passing CI Run Evidence on GitHub Actions",
            "Repository: <i>Rahul-S-H-7/SE-TASK</i> &bull; Branch: <b>main & demo/failing-ci</b><br/>"
            "Workflow Run #3 & #4: <b>CI / test</b> (completed successfully with green checkmark)<br/>"
            "URL: <u>https://github.com/Rahul-S-H-7/SE-TASK/actions/runs/40266133292</u>",
            height=125
        ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("6. Conclusion", h1_style))
    conclusion_text = (
        "The automated Continuous Integration pipeline runs the comprehensive unit and integration test suite "
        "automatically on every Git push and pull request. Any accidental regression—such as changing an attendance "
        "threshold or mishandling edge cases—is caught within seconds on the GitHub Actions runner before defective code "
        "can reach production or corrupt student academic standing records. This guarantees consistent software reliability, "
        "traceability, and high engineering quality."
    )
    story.append(Paragraph(conclusion_text, body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report successfully compiled: {pdf_path}")


if __name__ == "__main__":
    build_pdf()
