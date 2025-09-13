import tkinter as tk
from tkinter import ttk
from home_tab import HomeTab
from attendance_tab import AttendanceTab
from classes_tab import ClassesTab
from schedule_tab import ScheduleTab
from reports_tab import ReportsTab
from db_helper import add_school_year, add_section, add_schedule, add_student, get_school_years, get_sections


class CASApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CCS Attendance System")
        self.geometry("1100x700")
        self.configure(bg="#f1f2f6")  # Light background color

        # Add CCS Attendance System label above the app UI with black background
        header_label = tk.Label(self, text="CCS ATTENDANCE SYSTEM", font=("Segoe UI", 24, "bold"), fg="white",
                                bg="black")
        header_label.pack(fill="x", pady=10)  # Position it at the top of the window

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=(10, 16))

        self._build_navbar()  # Build the navbar (header)

        # Initialize the tabs
        self.home_tab = HomeTab(self.notebook)
        self.attendance_tab = AttendanceTab(self.notebook)

        # Pass the callback method to both tabs to update dropdowns
        self.classes_tab = ClassesTab(self.notebook, self.update_dropdowns)
        self.schedule_tab = ScheduleTab(self.notebook, self.update_dropdowns)

        self.reports_tab = ReportsTab(self.notebook)

        # Add the tabs to the notebook
        self.notebook.add(self.home_tab, text="Home")
        self.notebook.add(self.attendance_tab, text="Attendance Log")
        self.notebook.add(self.classes_tab, text="Classes")
        self.notebook.add(self.schedule_tab, text="Class Schedule")
        self.notebook.add(self.reports_tab, text="Reports")

        # Customizing tab labels
        self._style_tabs()

    def update_dropdowns(self):
        self.classes_tab.load_years_and_sections()
        self.schedule_tab.load_data()
        self.reports_tab._load_filters_from_db()  # ✅ refresh reports dropdowns too

    # ✅ refresh reports tab immediately

    def _build_navbar(self):
        """Create the header navbar with the title and the 'HOME' button."""
        nav = tk.Frame(self, bg="#2f3542", height=64)
        nav.pack(fill="x", side="top")
        nav.pack_propagate(False)  # Prevent resizing based on content

        # Right side of the navbar (for "HOME" button)
        right = tk.Frame(nav, bg="#2f3542")
        right.pack(side="right", padx=12)


    def _style_tabs(self):
        """Apply artistic styles to the tab labels."""
        style = ttk.Style(self)

        # Define style for the notebook tabs
        style.configure("TNotebook.Tab",
                        font=("Segoe UI", 12, "bold"),  # Font for tab labels
                        padding=[10, 5],  # Padding to make tabs bigger
                        background="black",  # Default background color for tabs
                        foreground="black",  # Default text color
                        relief="flat")

        # Active tab style
        style.map("TNotebook.Tab",
                  background=[("selected", "#2f3542")],  # Dark background when selected
                  foreground=[("selected", "black")])  # White text for active tab

        # Hover effect: Change background color when mouse is over the tab
        style.map("TNotebook.Tab",
                  background=[("active", "#f1c40f")])  # Yellow color on hover


if __name__ == "__main__":
    app = CASApp()
    app.mainloop()
