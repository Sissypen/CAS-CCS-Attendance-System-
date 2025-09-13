import pymysql
from datetime import datetime

def get_connection():
    """Establishes a connection to the MySQL database."""
    return pymysql.connect(
        host="localhost",
        user="cas_user",
        password="Ccs@1234",
        database="cas_attendance",
        cursorclass=pymysql.cursors.DictCursor
    )

# ---------------- SCHOOL YEARS ----------------
def add_academic_year(year_name):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO school_years (year_name) VALUES (%s)", (year_name,))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def get_academic_years():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, year_name FROM school_years ORDER BY year_name DESC")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def delete_academic_year(academic_year_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM school_years WHERE id = %s", (academic_year_id,))
        conn.commit()
    finally:
        cur.close()
        conn.close()

# ---------------- SECTIONS ----------------
def add_sections(section_name, school_year_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO sections (section_name, school_year_id) VALUES (%s, %s)",
            (section_name, school_year_id)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

def get_sections(school_year_id=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if school_year_id:
            cur.execute(
                "SELECT id, section_name AS name FROM sections WHERE school_year_id=%s",
                (school_year_id,)
            )
        else:
            cur.execute("SELECT id, section_name AS name FROM sections")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def delete_section(section_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM sections WHERE id = %s", (section_id,))
        conn.commit()
    finally:
        cur.close()
        conn.close()

# ---------------- SCHEDULES ----------------
def add_schedule(section_name, subject, instructor, day, start_time, end_time, room, academic_year_id, semester):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM sections WHERE section_name = %s AND school_year_id = %s",
                    (section_name, academic_year_id))
        sec = cur.fetchone()
        if not sec:
            raise Exception("Section not found for this academic year.")

        cur.execute("""
            INSERT INTO schedules (subject, instructor, day, start_time, end_time, room, section_id, school_year_id, semester)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (subject, instructor, day, start_time, end_time, room, sec["id"], academic_year_id, semester))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def get_schedules(section_name=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if section_name:
            cur.execute("""
                SELECT s.id, s.subject, s.instructor, s.day, s.start_time, s.end_time, s.room,
                       sec.id AS section_id, sec.section_name AS section, sy.year_name AS academic_year, s.semester
                FROM schedules s
                JOIN sections sec ON s.section_id = sec.id
                JOIN school_years sy ON s.school_year_id = sy.id
                WHERE sec.section_name = %s
                ORDER BY s.day, s.start_time
            """, (section_name,))
        else:
            cur.execute("""
                SELECT s.id, s.subject, s.instructor, s.day, s.start_time, s.end_time, s.room,
                       sec.id AS section_id, sec.section_name AS section, sy.year_name AS academic_year, s.semester
                FROM schedules s
                JOIN sections sec ON s.section_id = sec.id
                JOIN school_years sy ON s.school_year_id = sy.id
                ORDER BY s.day, s.start_time
            """)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def update_schedule(schedule_id, subject, instructor, day, start_time, end_time, room, semester):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE schedules
            SET subject=%s, instructor=%s, day=%s, start_time=%s, end_time=%s, room=%s, semester=%s
            WHERE id=%s
        """, (subject, instructor, day, start_time, end_time, room, semester, schedule_id))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def delete_schedule(schedule_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM schedules WHERE id=%s", (schedule_id,))
        conn.commit()
    finally:
        cur.close()
        conn.close()

# ---------------- STUDENTS ----------------
def add_student(student_id, last_name, first_name, middle_name, year_section, class_name, school_year_id, section_id=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO students (student_id, last_name, first_name, middle_name, year_section, class, school_year_id, section_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (student_id, last_name, first_name, middle_name, year_section, class_name, school_year_id, section_id))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def get_students(section_filter=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if section_filter:
            cur.execute("SELECT * FROM students WHERE year_section = %s", (section_filter,))
        else:
            cur.execute("SELECT * FROM students")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def get_students_by_section(section_id):
    """Return all students belonging to a section (by section_id)."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM students WHERE section_id = %s", (section_id,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

# ---------------- ATTENDANCE ----------------
def add_attendance(student_id, year_section, status):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO attendance_log (student_id, year_section, datetime, status)
            VALUES (%s,%s,%s,%s)
        """, (student_id, year_section, datetime.now(), status))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def get_attendance(section_filter=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if section_filter:
            cur.execute("SELECT * FROM attendance_log WHERE year_section = %s", (section_filter,))
        else:
            cur.execute("SELECT * FROM attendance_log")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()
