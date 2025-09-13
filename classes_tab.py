import tkinter as tk
from tkinter import ttk, messagebox
from theme import PINK, CARD_BG, LIGHT_BG, mk_label
from database import (get_academic_years, get_sections, add_academic_year, add_sections, add_student as db_add_student, get_students)

class ClassesTab(tk.Frame):
    def __init__(self, parent, update_dropdowns_callback):
        super().__init__(parent, bg=LIGHT_BG)
        self.update_dropdowns_callback = update_dropdowns_callback  # Callback for refreshing dropdowns
        self.selected_class = tk.StringVar(value="")
        self.academic_year_var = tk.StringVar()
        self.section_var = tk.StringVar()
        self._build_ui()
        self.load_years_and_sections()

    def load_years_and_sections(self):
        """Fetch the school years and sections from the database to populate comboboxes."""
        academic_years = get_academic_years()
        self.academic_year_cb['values'] = [ay['year_name'] for ay in academic_years]
        if academic_years:
            self.academic_year_var.set(academic_years[0]['year_name'])  # Set default

        sections = get_sections()  # Fetch sections from the database
        self.class_cb['values'] = [sec['name'] for sec in sections]
        if sections:
            self.section_var.set(sections[0]['name'])  # Set default

    def _build_ui(self):
        header = tk.Frame(self, bg=LIGHT_BG)
        header.pack(fill="x", padx=12, pady=(12, 8))
        mk_label(header, "Classes", font=("Segoe UI", 14, "bold"), bg=LIGHT_BG).pack(side="left")

        body = tk.Frame(self, bg=LIGHT_BG)
        body.pack(fill="both", expand=True, padx=12, pady=8)

        left = tk.Frame(body, bg=LIGHT_BG)
        left.pack(side="left", fill="both", expand=True, padx=(0, 12))

        middle = tk.Frame(body, bg=LIGHT_BG)
        middle.pack(side="left", fill="y")

        right = tk.Frame(body, bg=LIGHT_BG)
        right.pack(side="right", fill="y")

        mk_label(left, "List of Students", font=("Segoe UI", 11, "bold"), bg=CARD_BG).pack(anchor="w", padx=8, pady=6)
        cols = ("id", "last", "first", "middle", "year_section", "fingerprint_registered")
        self.student_tree = ttk.Treeview(left, columns=cols, show="headings")
        for c, t in zip(cols, ("Student ID", "Last Name", "First Name", "Middle Name", "Year & Section", "Fingerprint Registered")):
            self.student_tree.heading(c, text=t)
            self.student_tree.column(c, anchor="w", width=120)
        self.student_tree.pack(fill="both", expand=True, padx=8, pady=8)

        mk_label(middle, "Add Student", font=("Segoe UI", 11, "bold"), bg=LIGHT_BG).pack(anchor="w")

        self.sid_var = tk.StringVar()
        self.last_var = tk.StringVar()
        self.first_var = tk.StringVar()
        self.middle_var = tk.StringVar()
        self.ys_var = tk.StringVar()

        form = tk.Frame(middle, bg=LIGHT_BG)
        form.pack(padx=6, pady=6)

        # Academic Year row
        mk_label(form, "Academic Year:", bg=LIGHT_BG).grid(row=0, column=0, sticky="w", pady=4)
        self.academic_year_cb = ttk.Combobox(form, textvariable=self.academic_year_var, state="readonly", width=26)
        self.academic_year_cb.grid(row=0, column=1, pady=4, sticky="w")
        tk.Button(form, text="Add Academic Year", bg=PINK, fg="white", relief="flat",
                  command=self.add_academic_year_dialog).grid(row=0, column=2, padx=6, pady=4, sticky="w")

        mk_label(form, "Student ID:", bg=LIGHT_BG).grid(row=1, column=0, sticky="w", pady=4)
        tk.Entry(form, textvariable=self.sid_var, width=28).grid(row=1, column=1, pady=4, sticky="w")

        mk_label(form, "Last Name:", bg=LIGHT_BG).grid(row=2, column=0, sticky="w", pady=4)
        tk.Entry(form, textvariable=self.last_var, width=28).grid(row=2, column=1, pady=4, sticky="w")

        mk_label(form, "First Name:", bg=LIGHT_BG).grid(row=3, column=0, sticky="w", pady=4)
        tk.Entry(form, textvariable=self.first_var, width=28).grid(row=3, column=1, pady=4, sticky="w")

        mk_label(form, "Middle Name:", bg=LIGHT_BG).grid(row=4, column=0, sticky="w", pady=4)
        tk.Entry(form, textvariable=self.middle_var, width=28).grid(row=4, column=1, pady=4, sticky="w")

        mk_label(form, "Year & Section:", bg=LIGHT_BG).grid(row=5, column=0, sticky="w", pady=4)
        tk.Entry(form, textvariable=self.ys_var, width=28).grid(row=5, column=1, pady=4, sticky="w")

        # Choose Class (Section) row
        mk_label(form, "Choose Class (Section):", bg=LIGHT_BG).grid(row=6, column=0, sticky="w", pady=4)
        self.class_cb = ttk.Combobox(form, textvariable=self.section_var, state="readonly", width=26)
        self.class_cb.grid(row=6, column=1, pady=4, sticky="w")
        tk.Button(form, text="Add Section", bg=PINK, fg="white", relief="flat",
                  command=self.add_section_dialog).grid(row=6, column=2, padx=6, pady=4, sticky="w")

        actions = tk.Frame(middle, bg=LIGHT_BG)
        actions.pack(padx=6, pady=(4, 8), anchor="w")

        tk.Button(actions, text="Save Student", bg=PINK, fg="white", relief="flat",
                  command=self.save_student).pack(side="left", padx=(0, 10))

        fingerprint_frame = tk.Frame(actions, bg=LIGHT_BG, width=220, height=160, relief="solid", bd=2)
        fingerprint_frame.pack(side="left")
        fingerprint_frame.pack_propagate(False)

        mk_label(fingerprint_frame, "Fingerprint Scanner", bg=LIGHT_BG).pack(pady=6)

        fingerprint_sim = tk.Label(
            fingerprint_frame, text="Place Finger Here", font=("Segoe UI", 10, "bold"),
            bg="lightgray", relief="ridge", width=18, height=4
        )
        fingerprint_sim.pack(padx=5, pady=5)

        tk.Button(
            fingerprint_frame, text="Register Fingerprint", bg=PINK, fg="white", relief="flat",
            command=self.register_fingerprint
        ).pack(pady=6)

        form.grid_columnconfigure(0, weight=0)
        form.grid_columnconfigure(1, weight=0)
        form.grid_columnconfigure(2, weight=0)

    def refresh_students_list(self):
        """Refreshes the list of students in the treeview."""
        for r in self.student_tree.get_children():
            self.student_tree.delete(r)
        rows = get_students(self.section_var.get().strip() or None)
        for s in rows:
            self.student_tree.insert("", "end",
                                     values=(s["id"], s["last"], s["first"], s["middle"], s["year_section"], s["fingerprint_registered"]))

    def add_academic_year_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Add Academic Year")
        dlg.geometry("420x160")
        dlg.configure(bg=LIGHT_BG)
        mk_label(dlg, "Enter New Academic Year", bg=LIGHT_BG).pack(pady=(12, 6))
        yvar = tk.StringVar()
        tk.Entry(dlg, textvariable=yvar, width=40).pack(pady=6)

        def add_it():
            academic_year = yvar.get().strip()
            if not academic_year:
                messagebox.showwarning("Empty", "Please enter an academic year.")
                return
            add_academic_year(academic_year)
            self.load_years_and_sections()  # Refresh this tab
            self.update_dropdowns_callback()  # Refresh ScheduleTab too
            dlg.destroy()

        tk.Button(dlg, text="Add", bg=PINK, fg="white", relief="flat", command=add_it).pack(pady=8)

    def add_section_dialog(self):
        dlg = tk.Toplevel(self)
        dlg.title("Add Section")
        dlg.geometry("420x160")
        dlg.configure(bg=LIGHT_BG)

        mk_label(dlg, "Enter New Section", bg=LIGHT_BG).pack(pady=(12, 6))
        svar = tk.StringVar()
        tk.Entry(dlg, textvariable=svar, width=40).pack(pady=6)

        def add_it():
            section_name = svar.get().strip()
            if not section_name:
                messagebox.showwarning("Empty", "Please enter a section name.")
                return

            # Use currently selected Academic Year
            years = get_academic_years()
            sy_row = next((ay for ay in years if ay['year_name'] == self.academic_year_var.get()), None)
            if not sy_row:
                messagebox.showwarning("Invalid AY", "Please select an academic year first.")
                return

            add_sections(section_name, sy_row['id'])  # ✅ Save to DB
            self.load_years_and_sections()  # Refresh this tab
            self.update_dropdowns_callback()  # Refresh ScheduleTab
            dlg.destroy()
            messagebox.showinfo("Section Added", f"Section {section_name} added successfully.")

        tk.Button(dlg, text="Add", bg=PINK, fg="white", relief="flat", command=add_it).pack(pady=8)

    def save_student(self):
        sid = self.sid_var.get().strip()
        last = self.last_var.get().strip()
        first = self.first_var.get().strip()
        middle = self.middle_var.get().strip()
        ys = self.ys_var.get().strip()
        sec_name = self.section_var.get().strip()
        if not (sid and last and first and ys and sec_name and self.academic_year_var.get()):
            messagebox.showwarning("Missing fields", "Please fill all fields including Academic Year and Section.")
            return

        years = get_academic_years()
        sy_row = next((ay for ay in years if ay['year_name'] == self.academic_year_var.get()), None)
        school_year_id = sy_row['id'] if sy_row else None

        db_add_student(sid, last, first, middle, ys, sec_name, school_year_id)
        self.sid_var.set(""); self.last_var.set(""); self.first_var.set(""); self.middle_var.set(""); self.ys_var.set("")
        self.refresh_students_list()
        messagebox.showinfo("Saved", f"Student {first} {last} saved to {sec_name}.")

    def register_fingerprint(self):
        # Simulate registering a fingerprint for a student (plug in your SDK as needed)
        sid = self.sid_var.get().strip()
        if not sid:
            messagebox.showwarning("No Student ID", "Please select a student to register their fingerprint.")
            return
        # In a real app, capture bytes from scanner SDK:
        fake_bytes = f"Fingerprint data for {sid}".encode("utf-8")
        from db_helper import register_fingerprint
        register_fingerprint(sid, fake_bytes)
        messagebox.showinfo("Fingerprint Registered", f"Fingerprint registered for Student ID: {sid}")
        self.refresh_students_list()
