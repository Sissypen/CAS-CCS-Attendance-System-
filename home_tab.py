import tkinter as tk
from tkinter import ttk, messagebox
from theme import PINK, CARD_BG, LIGHT_BG, mk_label
from data_store import students, classes, attendance_log, current_timestamp_str


class HomeTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=LIGHT_BG)
        self._build_ui()

    def _build_ui(self):
        # Left card - scanner
        left_card = tk.Frame(self, bg=CARD_BG, bd=0, relief="raised", highlightbackground="#ccc", highlightthickness=1)
        left_card.pack(side="left", padx=(16, 8), pady=16, ipadx=20, ipady=12, fill="y")

        mk_label(left_card, "PLACE YOUR FINGER TO SCANNER TO LOGIN",
                 font=("Segoe UI", 12, "bold"), bg=CARD_BG).pack(pady=(8, 6))

        scanner_box = tk.Frame(left_card, width=340, height=280, bg="#ffe8ec", bd=2, relief="ridge")
        scanner_box.pack_propagate(False)
        scanner_box.pack(padx=10, pady=8)

        mk_label(scanner_box, "FINGERPRINT SCANNER", font=("Segoe UI", 10, "bold"), bg="#ffe8ec").pack(pady=10)
        self.status_label = mk_label(scanner_box, "Welcome, ready to learn or pretend to!",
                                     font=("Segoe UI", 9), bg="#ffe8ec")
        self.status_label.pack(pady=6)

        tk.Button(left_card, text="Simulate Scan", bg=PINK, fg="white", relief="flat",
                  command=self.open_simulate_scan, font=("Segoe UI", 10, "bold")).pack(pady=8)

        # Right card - quick actions
        right_card = tk.Frame(self, bg=CARD_BG)
        right_card.pack(side="left", padx=8, pady=16, fill="both", expand=True)

        mk_label(right_card, "Active Class", font=("Segoe UI", 11, "bold"), bg=CARD_BG).grid(
            row=0, column=0, sticky="w", padx=10, pady=(12, 6))
        self.class_var = tk.StringVar(value=classes[0] if classes else "")
        class_cb = ttk.Combobox(right_card, textvariable=self.class_var, values=classes, state="readonly", width=36)
        class_cb.grid(row=0, column=1, padx=10, pady=(12, 6), sticky="w")

        mk_label(right_card, "Quick Actions", font=("Segoe UI", 11, "bold"), bg=CARD_BG).grid(
            row=1, column=0, sticky="w", padx=10, pady=(6, 6))
        btn_frame = tk.Frame(right_card, bg=CARD_BG)
        btn_frame.grid(row=1, column=1, padx=10, pady=(6, 6), sticky="w")

        tk.Button(btn_frame, text="View Attendance Log", bg="#ffa3b3", fg="white", relief="flat",
                  command=lambda: self.master.select(1)).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Generate Report", bg=PINK, fg="white", relief="flat",
                  command=lambda: messagebox.showinfo("Generate", "Generate report action")).pack(side="left", padx=6)

        # Bottom - recent attendance
        bottom = tk.Frame(self, bg=LIGHT_BG)
        bottom.pack(fill="both", padx=18, pady=12, expand=True)
        mk_label(bottom, "Recent Attendance", font=("Segoe UI", 12, "bold"), bg=LIGHT_BG).pack(anchor="w", padx=6, pady=(6, 8))

        cols = ("id", "name", "ys", "datetime", "status")
        self.rv = ttk.Treeview(bottom, columns=cols, show="headings", height=8)
        for c, t in zip(cols, ("Student ID", "Name", "Year & Section", "Date Time", "Status")):
            self.rv.heading(c, text=t)
            self.rv.column(c, anchor="w", width=160 if c != "status" else 100)
        self.rv.pack(fill="both", expand=True, padx=6, pady=6)

    def open_simulate_scan(self):
        dlg = tk.Toplevel(self)
        dlg.title("Simulate Fingerprint Scan")
        dlg.geometry("420x220")
        dlg.configure(bg=LIGHT_BG)

        mk_label(dlg, "Select Student to mark as Present", font=("Segoe UI", 11, "bold"), bg=LIGHT_BG).pack(pady=(12, 8))
        values = [f"{s['id']} - {s['last']}, {s['first']} ({s['year_section']})" for s in students]
        sel_var = tk.StringVar()
        cb = ttk.Combobox(dlg, textvariable=sel_var, values=values, width=56, state="readonly")
        cb.pack(pady=8)

        def do_mark_present():
            sel = sel_var.get()
            if not sel:
                messagebox.showwarning("No students", "Add students first in Classes tab.")
                return
            sid = sel.split(" - ")[0]
            student = next((x for x in students if x["id"] == sid), None)
            if student:
                record = {
                    "student_id": student["id"],
                    "last": student["last"],
                    "first": student["first"],
                    "year_section": student["year_section"],
                    "datetime": current_timestamp_str(),
                    "status": "Present"
                }
                attendance_log.append(record)
                self.status_label.config(text=f"{student['first']} {student['last']} marked PRESENT")
                dlg.destroy()

        tk.Button(dlg, text="Mark Present", bg=PINK, fg="white", relief="flat",
                  command=do_mark_present).pack(pady=10)

    def refresh_recent(self):
        for r in self.rv.get_children():
            self.rv.delete(r)
        for rec in attendance_log[-12:][::-1]:
            self.rv.insert("", "end", values=(rec["student_id"],
                                              f"{rec['last']}, {rec['first']}",
                                              rec["year_section"], rec["datetime"], rec["status"]))
