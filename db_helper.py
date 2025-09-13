import pymysql

from data import fingerprints


def get_connection():
    """Establishes a connection to the MySQL database."""
    try:
        return pymysql.connect(
            host="localhost",  # Your MySQL hostname
            user="cas_user",  # Your MySQL username
            password="Ccs@1234",  # Your MySQL password
            database="cas_attendance",  # Database name
            cursorclass=pymysql.cursors.DictCursor  # Always return dict rows
        )
    except pymysql.MySQLError as e:
        print(f"Error connecting to the database: {e}")
        raise

def add_school_year(year_name):
    """Adds a new school year to the database."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO school_years (year_name) VALUES (%s)", (year_name,))
        conn.commit()
    except Exception as e:
        print(f"Error adding school year: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def add_section(name, school_year_id):
    """Adds a new section for a specific school year."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO sections (name, school_year_id) VALUES (%s, %s)", (name, school_year_id))
        conn.commit()
    except Exception as e:
        print(f"Error adding section: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def add_schedule(subject, instructor, day, start_time, end_time, room, section_name, school_year_id):
    """Adds a new schedule to the database."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO schedules (subject, instructor, day, start_time, end_time, room, section_id, school_year_id)
            VALUES (%s,%s,%s,%s,%s,%s,
                    (SELECT id FROM sections WHERE name=%s AND school_year_id=%s LIMIT 1),
                    %s)
        """, (subject, instructor, day, start_time, end_time, room, section_name, school_year_id, school_year_id))
        conn.commit()
    except Exception as e:
        print(f"Error adding schedule: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def add_student(student_id, last_name, first_name, middle_name, year_section, class_name):
    """Adds a new student to the database."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO students (student_id, last_name, first_name, middle_name, year_section, class)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (student_id, last_name, first_name, middle_name, year_section, class_name))
        conn.commit()
    except Exception as e:
        print(f"Error adding student: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def get_school_years():
    """Fetches all school years from the database."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, year_name FROM school_years ORDER BY year_name DESC")
        result = cur.fetchall()
        return result  # Return the result as a list of dictionaries
    finally:
        cur.close()
        conn.close()

def get_sections(school_year_id=None):
    """Fetches sections, optionally filtered by school year ID."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        if school_year_id:
            cur.execute("SELECT id, name FROM sections WHERE school_year_id=%s", (school_year_id,))
        else:
            cur.execute("SELECT id, name FROM sections")
        result = cur.fetchall()
        return result
    finally:
        cur.close()
        conn.close()

def register_fingerprint(student_id, fingerprint_data):
    """Registers a fingerprint for a student."""
    # In this case, we store fingerprint data in memory (as a dictionary)
    # Ideally, you should store fingerprint data in a secure manner (database or specialized storage)
    fingerprints[student_id] = fingerprint_data
    print(f"Fingerprint registered for student ID: {student_id}")
