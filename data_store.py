# data_store.py
from data import attendance_log, classes, academic_years, students, schedules  # Import data from data.py

def current_timestamp_str():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Example function to get attendance
def get_attendance_log():
    return attendance_log

# Example function to get classes
def get_classes():
    return classes

# Example function to get academic years
def get_academic_years():
    return academic_years

# Example function to add a new student
def add_student(student):
    students.append(student)

# Example function to add a schedule
def add_schedule(schedule):
    schedules.append(schedule)
