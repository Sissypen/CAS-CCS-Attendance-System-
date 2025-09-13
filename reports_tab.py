# reports_tab.py  (MySQL-integrated)
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from theme import PINK, CARD_BG, LIGHT_BG, mk_label
# Fallback in-memory lists (used only if DB is unavailable)
from data_store import attendance_log as MEM_ATTENDANCE, classes as MEM_CLASSES, academic_years as MEM_YEARS  # fallback

# DB helpers you already have
from database import get_connection, get_academic_years, get_sections  # school_years/sections for filters

class ReportsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=LIGHT_BG)

        # UI state
        self.semester_choice = tk.StringVar(value="")
        self.academic_year_choice = tk.StringVar()   # ✅ fixed name
        self.section_choice = tk.StringVar()         # ✅ fixed name
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()

        # Data for dropdowns
        self.sections = []        # [(id, name)]
        self.school_years = []    # [(id, year_name)]

        self._build_ui()
        self._load_filters_from_db()


    # -----------------------
    # UI
    # -----------------------
    def _build_ui(self):
        main_frame = tk.Frame(self, bg=LIGHT_BG)
        main_frame.pack(fill="both", expand=True, padx=16, pady=(10, 16))

        # Left — Filters
        left = tk.Frame(main_frame, bg=LIGHT_BG, width=380)
        left.pack(side="left", fill="y", padx=8, pady=8)
        mk_label(left, "Reports Filters", font=("Segoe UI", 14, "bold"), bg=LIGHT_BG).pack(side="top", padx=12, pady=8)

        f = tk.Frame(left, bg=LIGHT_BG)
        f.pack(padx=12, pady=8, fill="x")

        # Section filter (from DB sections)
        mk_label(f, "Select Section:", bg=LIGHT_BG).grid(row=0, column=0, sticky="w", pady=4)
        self.section_cb = ttk.Combobox(f, textvariable=self.section_choice, state="readonly", width=30)
        self.section_cb.grid(row=0, column=1, pady=4)

        # Academic Year filter (from DB school_years)
        mk_label(f, "Select Academic Year:", bg=LIGHT_BG).grid(row=1, column=0, sticky="w", pady=4)
        self.academic_year_cb = ttk.Combobox(f, textvariable=self.academic_year_choice, state="readonly", width=30)
        self.academic_year_cb.grid(row=1, column=1, pady=4)

        # Semester (optional free choice — only useful if you track it)
        mk_label(f, "Select Semester (optional):", bg=LIGHT_BG).grid(row=2, column=0, sticky="w", pady=4)
        self.semester_cb = ttk.Combobox(
            f, textvariable=self.semester_choice, state="readonly", width=30,
            values=["", "1st Semester", "2nd Semester"]
        )
        self.semester_cb.grid(row=2, column=1, pady=4)

        # Date range
        mk_label(f, "Start Date:", bg=LIGHT_BG).grid(row=3, column=0, sticky="w", pady=4)
        self.start_date_entry = DateEntry(f, textvariable=self.start_date_var, width=18,
                                          background="darkblue", foreground="white", borderwidth=2)
        self.start_date_entry.grid(row=3, column=1, sticky="w", pady=4)

        mk_label(f, "End Date:", bg=LIGHT_BG).grid(row=4, column=0, sticky="w", pady=4)
        self.end_date_entry = DateEntry(f, textvariable=self.end_date_var, width=18,
                                        background="darkblue", foreground="white", borderwidth=2)
        self.end_date_entry.grid(row=4, column=1, sticky="w", pady=4)

        # Buttons
        btns = tk.Frame(f, bg=LIGHT_BG)
        btns.grid(row=5, column=0, columnspan=2, pady=(8, 0), sticky="w")
        tk.Button(btns, text="Filter", bg=PINK, fg="white", relief="flat", command=self.refresh_preview).pack(side="left", padx=6)
        tk.Button(btns, text="Export to CSV", bg=PINK, fg="white", relief="flat", command=self.export_to_csv).pack(side="left", padx=6)
        tk.Button(btns, text="Export to PDF", bg=PINK, fg="white", relief="flat", command=self.export_to_pdf).pack(side="left", padx=6)

        # Right — Preview table + summary
        right = tk.Frame(main_frame, bg=LIGHT_BG)
        right.pack(side="right", fill="both", expand=True, padx=8, pady=8)

        mk_label(right, "Attendance Summary", font=("Segoe UI", 14, "bold"), bg=LIGHT_BG).pack(side="top", padx=12, pady=8)

        self.tree = ttk.Treeview(
            right,
            columns=("datetime", "student_id", "last", "first", "year_section", "status"),
            show="headings"
        )
        self.tree.heading("datetime", text="DateTime")
        self.tree.heading("student_id", text="Student ID")
        self.tree.heading("last", text="Last Name")
        self.tree.heading("first", text="First Name")
        self.tree.heading("year_section", text="Year & Section")
        self.tree.heading("status", text="Status")

        for c in ("datetime", "student_id", "last", "first", "year_section", "status"):
            self.tree.column(c, anchor="w", width=140 if c != "datetime" else 180)
        self.tree.pack(fill="both", expand=True, padx=12, pady=(8, 12))

        self.summary_box = tk.Label(right, text="Attendance Summary will appear here.", bg=CARD_BG, font=("Segoe UI", 10))
        self.summary_box.pack(fill="x", padx=12, pady=(0, 6))

        tk.Button(right, text="Preview Report", bg=PINK, fg="white", relief="flat",
                  command=self.refresh_preview).pack(pady=6)

    # -----------------------
    # Load filters from DB
    # -----------------------
    def _load_filters_from_db(self):
        try:
            # Academic Years
            years = get_academic_years()  # [{'id':..., 'year_name':...}]
            self.school_years = [(y["id"], y["year_name"]) for y in years]
            self.academic_year_cb["values"] = [y[1] for y in self.school_years]
            if self.school_years:
                self.academic_year_choice.set(self.school_years[0][1])

            # Sections
            secs = get_sections()  # [{'id':..., 'name':...}]
            self.sections = [(s["id"], s["name"]) for s in secs]
            self.section_cb["values"] = [s[1] for s in self.sections]
            if self.sections:
                self.section_choice.set(self.sections[0][1])

        except Exception:
            # Fallback to memory lists if DB not reachable
            self.academic_year_cb["values"] = MEM_YEARS
            self.section_cb["values"] = MEM_CLASSES  # old UI used "classes" but DB uses "sections"

    # -----------------------
    # Data fetchers
    # -----------------------
    def fetch_attendance_from_db(self, section_name, academic_year_name, start_date, end_date, semester):
        """
        Returns list of dicts with keys:
        datetime, student_id, last, first, year_section, status
        Adjust table/column names if needed to match your schema.
        """
        sql = """
            SELECT
                a.datetime      AS datetime,
                a.student_id    AS student_id,
                a.last_name     AS last,
                a.first_name    AS first,
                CONCAT(sec.name) AS year_section,
                a.status        AS status
            FROM attendance a
            JOIN sections sec ON a.section_id = sec.id
            JOIN school_years sy ON a.school_year_id = sy.id
            WHERE 1=1
        """
        params = []

        if section_name:
            sql += " AND sec.name = %s"
            params.append(section_name)

        if academic_year_name:
            sql += " AND sy.year_name = %s"
            params.append(academic_year_name)

        if start_date:
            sql += " AND DATE(a.datetime) >= %s"
            params.append(start_date)

        if end_date:
            sql += " AND DATE(a.datetime) <= %s"
            params.append(end_date)

        # Optional: if you actually store semester on attendance rows (e.g., a.semester)
        if semester:
            sql += " AND (a.semester = %s)"
            params.append(semester)

        sql += " ORDER BY a.datetime DESC"

        conn = None
        try:
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute(sql, tuple(params))
                rows = cur.fetchall()
            return rows
        finally:
            if conn:
                conn.close()

    def fetch_attendance_from_memory(self, section_name, academic_year_name, start_date, end_date, semester):
        data = []
        for r in MEM_ATTENDANCE:
            if section_name and r.get("year_section") != section_name:
                continue
            if academic_year_name and r.get("academic_year") != academic_year_name:
                continue
            if semester and r.get("semester") != semester:
                continue
            if start_date and (r.get("datetime", "") < start_date):
                continue
            if end_date and (r.get("datetime", "") > end_date):
                continue
            data.append(r)
        return data

    # -----------------------
    # Actions
    # -----------------------
    def _collect_filters(self):
        return {
            "section": self.section_choice.get().strip(),
            "academic_year": self.academic_year_choice.get().strip(),
            "semester": self.semester_choice.get().strip(),
            "start_date": self.start_date_var.get().strip(),
            "end_date": self.end_date_var.get().strip(),
        }

    def _get_filtered_data(self):
        f = self._collect_filters()
        try:
            data = self.fetch_attendance_from_db(
                f["section"], f["academic_year"], f["start_date"], f["end_date"], f["semester"]
            )
            # Normalize to expected keys if DB columns differ
            norm = []
            for r in data:
                norm.append({
                    "datetime": r.get("datetime", ""),
                    "student_id": r.get("student_id", ""),
                    "last": r.get("last", ""),
                    "first": r.get("first", ""),
                    "year_section": r.get("year_section", ""),
                    "status": r.get("status", ""),
                })
            return norm
        except Exception:
            # Fall back to memory
            return self.fetch_attendance_from_memory(
                f["section"], f["academic_year"], f["start_date"], f["end_date"], f["semester"]
            )

    def refresh_preview(self):
        data = self._get_filtered_data()

        # table
        for it in self.tree.get_children():
            self.tree.delete(it)
        for r in data:
            self.tree.insert("", "end", values=(
                r.get("datetime", ""),
                r.get("student_id", ""),
                r.get("last", ""),
                r.get("first", ""),
                r.get("year_section", ""),
                r.get("status", ""),
            ))

        # summary
        total = len(data)
        present = sum(1 for r in data if str(r.get("status", "")).lower() == "present")
        absent = total - present
        self.summary_box.config(text=f"Total records: {total}\nPresent: {present}\nAbsent: {absent}")

    def export_to_csv(self):
        data = self._get_filtered_data()
        if not data:
            messagebox.showinfo("No Data", "No attendance records to export.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["DateTime", "Student ID", "Last Name", "First Name", "Year & Section", "Status"])
            for r in data:
                w.writerow([r.get("datetime",""), r.get("student_id",""), r.get("last",""),
                            r.get("first",""), r.get("year_section",""), r.get("status","")])
        messagebox.showinfo("Exported", f"Report has been successfully exported to {path}")

    def export_to_pdf(self):
        data = self._get_filtered_data()
        if not data:
            messagebox.showinfo("No Data", "No attendance records to export.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not path:
            return

        # header info
        f = self._collect_filters()
        pdf = canvas.Canvas(path, pagesize=letter)
        pdf.setFont("Helvetica", 10)

        y = 750
        pdf.drawString(30, y, "Attendance Report"); y -= 20
        pdf.drawString(30, y, f"Section: {f['section']}"); y -= 15
        pdf.drawString(30, y, f"Academic Year: {f['academic_year']}"); y -= 15
        if f["semester"]:
            pdf.drawString(30, y, f"Semester: {f['semester']}"); y -= 15
        pdf.drawString(30, y, f"Date Range: {f['start_date']} to {f['end_date']}"); y -= 30

        # columns
        pdf.drawString(30, y, "DateTime")
        pdf.drawString(120, y, "Student ID")
        pdf.drawString(200, y, "Last")
        pdf.drawString(280, y, "First")
        pdf.drawString(360, y, "Year & Section")
        pdf.drawString(480, y, "Status")
        y -= 15

        # rows (simple pagination)
        for r in data:
            if y < 60:
                pdf.showPage()
                pdf.setFont("Helvetica", 10)
                y = 750
            pdf.drawString(30, y, str(r.get("datetime","")))
            pdf.drawString(120, y, str(r.get("student_id","")))
            pdf.drawString(200, y, str(r.get("last","")))
            pdf.drawString(280, y, str(r.get("first","")))
            pdf.drawString(360, y, str(r.get("year_section","")))
            pdf.drawString(480, y, str(r.get("status","")))
            y -= 15

        # summary
        total = len(data)
        present = sum(1 for x in data if str(x.get("status","")).lower() == "present")
        absent = total - present
        y -= 20
        pdf.drawString(30, y, f"Total records: {total}"); y -= 15
        pdf.drawString(30, y, f"Present: {present}"); y -= 15
        pdf.drawString(30, y, f"Absent: {absent}")

        pdf.save()
        messagebox.showinfo("Exported", f"Report has been successfully exported to {path}")
