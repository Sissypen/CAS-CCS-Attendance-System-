import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
from theme import PINK, LIGHT_BG, mk_label
from database import get_attendance, get_sections

class AttendanceTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=LIGHT_BG)
        self.filter_var = tk.StringVar(value="")
        self._build_ui()
        self._init_sections()
        self.refresh_table()

    def _build_ui(self):
        top = tk.Frame(self, bg=LIGHT_BG)
        top.pack(fill="x", padx=12, pady=(12, 8))
        mk_label(top, "Attendance Log", font=("Segoe UI", 14, "bold"), bg=LIGHT_BG).pack(side="left")

        filter_frame = tk.Frame(self, bg=LIGHT_BG)
        filter_frame.pack(fill="x", padx=12, pady=(6, 12))
        mk_label(filter_frame, "Filter by Section:", bg=LIGHT_BG).pack(side="left", padx=(0, 6))
        self.filter_cb = ttk.Combobox(filter_frame, textvariable=self.filter_var, values=[""], state="readonly", width=36)
        self.filter_cb.pack(side="left")
        tk.Button(filter_frame, text="Filter", bg=PINK, fg="white", relief="flat",
                  command=self.refresh_table).pack(side="left", padx=8)
        tk.Button(filter_frame, text="Export CSV", bg="#ffa3b3", fg="white", relief="flat",
                  command=self.export_csv).pack(side="left", padx=8)

        cols = ("id", "last", "first", "year_section", "datetime", "status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings")
        for c, t in zip(cols, ("Student ID", "Last Name", "First Name", "Year & Section", "Date Time", "Status")):
            self.tree.heading(c, text=t)
            self.tree.column(c, anchor="w", width=140 if c != "datetime" else 200)
        self.tree.pack(fill="both", expand=True, padx=12, pady=(6, 12))

    def _init_sections(self):
        """Initializes the section dropdown with available sections."""
        secs = get_sections()
        vals = [""] + [s['name'] for s in secs]
        self.filter_cb.config(values=vals)
        if len(vals) > 1:
            self.filter_var.set("")  # Default to no section filter

    def refresh_table(self):
        """Refreshes the attendance table with filtered data."""
        for r in self.tree.get_children():
            self.tree.delete(r)
        section_filter = self.filter_var.get() or None  # Get filter value or None
        rows = get_attendance(section_filter=section_filter)  # Fetch data with section filter
        for rec in rows:
            self.tree.insert("", "end", values=(
                rec["student_id"], rec["last"], rec["first"],
                rec["year_section"], rec["datetime"].strftime("%Y-%m-%d %H:%M:%S"), rec["status"]
            ))

    def export_csv(self):
        """Exports the attendance data to a CSV file."""
        rows = get_attendance(section_filter=self.filter_var.get() or None)
        if not rows:
            messagebox.showinfo("No Data", "No attendance records to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV file", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(("Student ID", "Last Name", "First Name", "Year & Section", "Date Time", "Status"))
            for rec in rows:
                w.writerow((rec["student_id"], rec["last"], rec["first"],
                            rec["year_section"], rec["datetime"].strftime("%Y-%m-%d %H:%M:%S"), rec["status"]))
        messagebox.showinfo("Exported", f"Attendance exported to {path}")
