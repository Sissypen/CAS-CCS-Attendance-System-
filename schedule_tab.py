import tkinter as tk
from tkinter import ttk, messagebox

from theme import PINK, LIGHT_BG, mk_label
from database import (
    get_academic_years, get_sections,
    add_sections, add_academic_year, get_schedules,
    add_schedule, delete_schedule, delete_section,
    get_students_by_section
)


class ScheduleTab(tk.Frame):
    def __init__(self, parent, update_dropdowns_callback):
        super().__init__(parent, bg=LIGHT_BG)
        self.update_dropdowns_callback = update_dropdowns_callback
        self._build_ui()
        self.load_data()
        self.update_schedule_table()   # Auto load schedules on startup

    def load_data(self):
        """Fetch the school years and sections from the database."""
        school_years = get_academic_years()
        self.academic_year_cb['values'] = [sy['year_name'] for sy in school_years]
        if school_years:
            self.academic_year_var.set(school_years[0]['year_name'])

        sections = get_sections()
        self.section_cb['values'] = [sec['name'] for sec in sections]
        if sections:
            self.section_var.set(sections[0]['name'])

    def update_schedule_table(self):
        """Refresh the schedule table with latest data."""
        section_name = self.section_var.get()
        schedules = get_schedules(section_name)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for schedule in schedules:
            self.tree.insert("", "end", values=(
                schedule['id'], schedule['subject'], schedule['instructor'], schedule['day'],
                schedule['start_time'], schedule['end_time'], schedule['room'],
                schedule['section'], schedule['academic_year'], schedule.get('semester', '')
            ))

    def _build_ui(self):
        main_frame = tk.Frame(self, bg=LIGHT_BG)
        main_frame.pack(fill="both", expand=True, padx=16, pady=(10, 16))

        # Left side - form
        left_frame = tk.Frame(main_frame, bg=LIGHT_BG, width=400)
        left_frame.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        mk_label(left_frame, "Add Class Schedule", font=("Segoe UI", 14, "bold"), bg=LIGHT_BG).pack(pady=6)

        f = tk.Frame(left_frame, bg=LIGHT_BG)
        f.pack(padx=12, pady=6)

        # Section
        mk_label(f, "Section:", bg=LIGHT_BG).grid(row=0, column=0, sticky="w", pady=4)
        self.section_var = tk.StringVar()
        self.section_cb = ttk.Combobox(f, textvariable=self.section_var, state="readonly", width=30)
        self.section_cb.grid(row=0, column=1, pady=4)
        self.section_cb.bind("<<ComboboxSelected>>", lambda e: self.update_schedule_table())
        tk.Button(f, text="Add Section", bg=PINK, fg="white", relief="flat", command=self.add_section).grid(row=0, column=2, padx=4)

        # Academic Year
        mk_label(f, "Academic Year:", bg=LIGHT_BG).grid(row=1, column=0, sticky="w", pady=4)
        self.academic_year_var = tk.StringVar()
        self.academic_year_cb = ttk.Combobox(f, textvariable=self.academic_year_var, state="readonly", width=30)
        self.academic_year_cb.grid(row=1, column=1, pady=4)
        tk.Button(f, text="Add Academic Year", bg=PINK, fg="white", relief="flat", command=self.add_academic_year).grid(row=1, column=2, padx=4)

        # Semester
        mk_label(f, "Semester:", bg=LIGHT_BG).grid(row=2, column=0, sticky="w", pady=4)
        self.semester_var = tk.StringVar()
        self.semester_cb = ttk.Combobox(f, textvariable=self.semester_var, values=["First Semester", "Second Semester"], state="readonly", width=30)
        self.semester_cb.grid(row=2, column=1, pady=4)

        # Subject, Instructor, Room
        fields = [("Subject", "subject"), ("Instructor", "instructor"), ("Room", "room")]
        self.vars = {}
        for i, (label, name) in enumerate(fields):
            mk_label(f, label + ":", bg=LIGHT_BG).grid(row=i + 3, column=0, sticky="w", pady=4)
            v = tk.StringVar()
            self.vars[name] = v
            tk.Entry(f, textvariable=v, width=30).grid(row=i + 3, column=1, pady=4)

        # Day
        mk_label(f, "Day:", bg=LIGHT_BG).grid(row=6, column=0, sticky="w", pady=4)
        self.day_var = tk.StringVar()
        day_cb = ttk.Combobox(f, textvariable=self.day_var,
                              values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                              state="readonly", width=30)
        day_cb.grid(row=6, column=1, pady=4)

        # Times
        self.start_time_var = tk.StringVar()
        self.end_time_var = tk.StringVar()
        self.start_am_pm_var = tk.StringVar(value="AM")
        self.end_am_pm_var = tk.StringVar(value="AM")

        tk.Label(f, text="Start Time:", bg=LIGHT_BG).grid(row=7, column=0, sticky="w", pady=4)
        tk.Entry(f, textvariable=self.start_time_var, width=15).grid(row=7, column=1, pady=4)
        ttk.Combobox(f, textvariable=self.start_am_pm_var, values=["AM", "PM"], state="readonly", width=5).grid(row=7, column=2, pady=4)

        tk.Label(f, text="End Time:", bg=LIGHT_BG).grid(row=8, column=0, sticky="w", pady=4)
        tk.Entry(f, textvariable=self.end_time_var, width=15).grid(row=8, column=1, pady=4)
        ttk.Combobox(f, textvariable=self.end_am_pm_var, values=["AM", "PM"], state="readonly", width=5).grid(row=8, column=2, pady=4)

        tk.Button(left_frame, text="Add Schedule", bg=PINK, fg="white", relief="flat", command=self.add_schedule).pack(pady=8)

        # Right side - table
        right_frame = tk.Frame(main_frame, bg=LIGHT_BG, width=600)
        right_frame.pack(side="right", fill="both", expand=True, padx=8, pady=8)

        mk_label(right_frame, "Class Schedules", font=("Segoe UI", 14, "bold"), bg=LIGHT_BG).pack(pady=8)

        cols = ("id", "subject", "instructor", "day", "start", "end", "room", "section", "academic_year", "semester")
        self.tree = ttk.Treeview(right_frame, columns=cols, show="headings")
        for c, t in zip(cols, ("ID", "Subject", "Instructor", "Day", "Start Time", "End Time", "Room", "Section", "Academic Year", "Semester")):
            self.tree.heading(c, text=t)
            self.tree.column(c, anchor="w", width=100)

        # hide ID column
        self.tree.column("id", width=0, stretch=False)

        self.tree.pack(fill="both", expand=True, padx=12, pady=12)

        # Buttons under the table
        tk.Button(right_frame, text="Edit Selected", bg=PINK, fg="white", relief="flat",
                  command=self.edit_selected_schedule).pack(pady=4)

        tk.Button(right_frame, text="Delete Selected Schedule", bg="red", fg="white", relief="flat",
                  command=self.delete_selected_schedule).pack(pady=4)

        tk.Button(right_frame, text="Delete Selected Section", bg="red", fg="white", relief="flat",
                  command=self.delete_selected_section).pack(pady=4)

    def add_section(self):
        dlg = tk.Toplevel(self)
        dlg.title("Add Section")
        dlg.geometry("420x160")
        dlg.configure(bg=LIGHT_BG)

        mk_label(dlg, "Section Name (e.g., BSIT 4A - SHANNON)", bg=LIGHT_BG).pack(pady=(12, 6))

        section_name_var = tk.StringVar()
        tk.Entry(dlg, textvariable=section_name_var, width=40).pack(pady=6)

        def add_it():
            section_name = section_name_var.get().strip()
            if not section_name:
                messagebox.showwarning("Empty", "Please enter a section name.")
                return

            ay_name = self.academic_year_var.get().strip()
            if not ay_name:
                messagebox.showwarning("Missing Academic Year", "Please select an academic year.")
                return

            years = get_academic_years()
            sy_row = next((y for y in years if y["year_name"] == ay_name), None)
            if not sy_row:
                messagebox.showerror("Not Found", f"Academic year '{ay_name}' not found.")
                return

            try:
                add_sections(section_name, sy_row["id"])
            except Exception as e:
                messagebox.showerror("DB Error", f"Could not add section.\n\n{e}")
                return

            self.load_data()
            self.update_dropdowns_callback()
            dlg.destroy()
            messagebox.showinfo("Section Added", f"Section {section_name} added for {ay_name}.")

        tk.Button(dlg, text="Add Section", bg=PINK, fg="white", relief="flat", command=add_it).pack(pady=8)

    def add_academic_year(self):
        dlg = tk.Toplevel(self)
        dlg.title("Add Academic Year")
        dlg.geometry("420x160")
        dlg.configure(bg=LIGHT_BG)

        mk_label(dlg, "Academic Year Name (e.g., 2023-2024)", bg=LIGHT_BG).pack(pady=(12, 6))
        yvar = tk.StringVar()
        tk.Entry(dlg, textvariable=yvar, width=40).pack(pady=6)

        def add_it():
            academic_year = yvar.get().strip()
            if not academic_year:
                messagebox.showwarning("Empty", "Please enter an academic year.")
                return
            add_academic_year(academic_year)
            self.load_data()
            self.update_dropdowns_callback()
            dlg.destroy()

        tk.Button(dlg, text="Add", bg=PINK, fg="white", relief="flat", command=add_it).pack(pady=8)

    def add_schedule(self):
        """Add schedule to DB."""
        if not all([
            self.section_var.get(), self.academic_year_var.get(), self.semester_var.get(),
            self.vars['subject'].get(), self.vars['instructor'].get(),
            self.vars['room'].get(), self.day_var.get(),
            self.start_time_var.get(), self.end_time_var.get()
        ]):
            messagebox.showwarning("Missing Fields", "Please fill out all fields.")
            return

        ay_name = self.academic_year_var.get().strip()
        years = get_academic_years()
        sy_row = next((y for y in years if y["year_name"] == ay_name), None)
        if not sy_row:
            messagebox.showerror("Invalid AY", f"Academic Year '{ay_name}' not found.")
            return

        school_year_id = sy_row["id"]
        section = self.section_var.get().strip()
        subject = self.vars['subject'].get().strip()
        instructor = self.vars['instructor'].get().strip()
        room = self.vars['room'].get().strip()
        day = self.day_var.get().strip()
        start_time = self.start_time_var.get().strip()
        end_time = self.end_time_var.get().strip()
        semester = self.semester_var.get().strip()

        try:
            add_schedule(section, subject, instructor, day, start_time, end_time, room, school_year_id, semester)
            self.update_schedule_table()

            for v in self.vars.values():
                v.set("")
            self.day_var.set("")
            self.start_time_var.set("")
            self.end_time_var.set("")
            self.start_am_pm_var.set("AM")
            self.end_am_pm_var.set("AM")
            self.semester_var.set("")

            messagebox.showinfo("Saved", f"Schedule added for {section} • {ay_name} • {semester}.")
        except Exception as e:
            messagebox.showerror("DB Error", f"Could not add schedule.\n\n{e}")

    def edit_selected_schedule(self):
        """Open dialog to edit schedule."""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a schedule to edit.")
            return

        values = self.tree.item(selected, "values")
        schedule_id = values[0]  # first column is ID

        dlg = tk.Toplevel(self)
        dlg.title("Edit Schedule")
        dlg.geometry("420x400")
        dlg.configure(bg=LIGHT_BG)

        fields = ["Subject", "Instructor", "Day", "Start Time", "End Time", "Room", "Semester"]
        vars = {}
        for i, field in enumerate(fields):
            mk_label(dlg, field + ":", bg=LIGHT_BG).grid(row=i, column=0, sticky="w", pady=4, padx=6)
            v = tk.StringVar(value=values[i+1])  # skip ID
            vars[field.lower().replace(" ", "_")] = v
            tk.Entry(dlg, textvariable=v, width=30).grid(row=i, column=1, pady=4)

        def save_changes():
            from database import update_schedule
            update_schedule(
                schedule_id,
                vars["subject"].get(),
                vars["instructor"].get(),
                vars["day"].get(),
                vars["start_time"].get(),
                vars["end_time"].get(),
                vars["room"].get(),
                vars["semester"].get(),
            )
            self.update_schedule_table()
            dlg.destroy()
            messagebox.showinfo("Updated", "Schedule updated successfully.")

        tk.Button(dlg, text="Save", bg=PINK, fg="white", relief="flat", command=save_changes).grid(row=len(fields), columnspan=2, pady=12)

    def delete_selected_schedule(self):
        """Delete selected schedule from DB."""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a schedule to delete.")
            return

        values = self.tree.item(selected, "values")
        schedule_id = values[0]

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this schedule?"):
            delete_schedule(schedule_id)
            self.update_schedule_table()
            messagebox.showinfo("Deleted", "Schedule deleted successfully.")

    def delete_selected_section(self):
        """Delete selected section safely."""
        section_name = self.section_var.get().strip()
        if not section_name:
            messagebox.showwarning("No Section", "Please select a section first.")
            return

        # Find section row
        sections = get_sections()
        sec_row = next((s for s in sections if s["name"] == section_name), None)
        if not sec_row:
            messagebox.showerror("Error", f"Section '{section_name}' not found.")
            return

        section_id = sec_row["id"]

        # Check if students exist
        students = get_students_by_section(section_id)
        if students:
            messagebox.showerror("Delete Blocked", f"Cannot delete section '{section_name}' because it has students enrolled.")
            return

        # Check if schedules exist
        schedules = get_schedules(section_name)
        if schedules:
            messagebox.showerror("Delete Blocked", f"Cannot delete section '{section_name}' because it has schedules assigned.")
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete section '{section_name}'?"):
            delete_section(section_id)
            self.load_data()
            self.update_dropdowns_callback()
            messagebox.showinfo("Deleted", f"Section '{section_name}' deleted successfully.")
