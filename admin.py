import os
import sys
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from fpdf import FPDF
import subprocess
import platform

# tkcalendar for date pickers
from tkcalendar import DateEntry

# Global attendance file; both modules use the same file.
ATTENDANCE_FILE = "attendance.csv"

# Admin credentials
ADMIN_EMAIL = "admin"
ADMIN_PASSWORD = "123"

# Color palette
COLOR_PRIMARY       = "#2C3E50"
COLOR_SECONDARY     = "#3498DB"
COLOR_LIGHT_BG      = "#ECF0F1"
COLOR_WHITE         = "#FFFFFF"
COLOR_TEXT_DARK     = "#000000"
COLOR_BUTTON_RED    = "#E74C3C"
COLOR_BUTTON_GREEN  = "#27AE60"

class AdminApp:
    def __init__(self, root):
        self.root = root
        # DataFrame currently displayed (full or filtered)
        self.displayed_df = pd.DataFrame(columns=["Name", "Timestamp", "Type"])

        self.root.title("Admin Login")
        self.root.geometry("800x500")
        self.root.configure(bg=COLOR_PRIMARY)
        self.create_header()
        self.create_login_frame()

    def create_header(self):
        header = tk.Frame(self.root, bg=COLOR_SECONDARY, height=50)
        header.pack(fill=tk.X)
        tk.Label(header, text="AMS", font=("Arial", 24, "bold"), fg=COLOR_WHITE, bg=COLOR_SECONDARY).pack(side=tk.LEFT, padx=20)
        tk.Label(header, text="ATTENDANCE MONITORING SYSTEM", font=("Arial", 14), fg=COLOR_WHITE, bg=COLOR_SECONDARY).pack(side=tk.LEFT)

    def create_login_frame(self):
        frame = tk.Frame(self.root, bg=COLOR_LIGHT_BG, padx=30, pady=30)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(frame, text="Admin Login", font=("Arial", 18, "bold"), bg=COLOR_LIGHT_BG).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        tk.Label(frame, text="Email:", bg=COLOR_LIGHT_BG).grid(row=1, column=0, sticky=tk.W)
        self.email_entry = tk.Entry(frame)
        self.email_entry.grid(row=1, column=1, pady=5)
        tk.Label(frame, text="Password:", bg=COLOR_LIGHT_BG).grid(row=2, column=0, sticky=tk.W)
        self.password_entry = tk.Entry(frame, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)

        login_btn = tk.Button(frame, text="Login", bg=COLOR_BUTTON_RED, fg=COLOR_WHITE, font=("Arial", 12), command=self.login)
        login_btn.grid(row=3, column=0, columnspan=2, pady=15, ipadx=20)

    def login(self):
        if self.email_entry.get() == ADMIN_EMAIL and self.password_entry.get() == ADMIN_PASSWORD:
            self.show_admin_panel()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")

    def show_admin_panel(self):
        for w in self.root.winfo_children():
            w.destroy()

        self.root.title("Admin Panel")
        self.root.configure(bg=COLOR_PRIMARY)

        side = tk.Frame(self.root, bg=COLOR_SECONDARY, width=180)
        side.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(side, text="AMS", font=("Arial", 20, "bold"), fg=COLOR_WHITE, bg=COLOR_SECONDARY).pack(pady=20)
        tk.Button(side, text="Attendance", width=16, bg=COLOR_SECONDARY, fg=COLOR_WHITE, command=self.open_attendance).pack(pady=5)
        tk.Button(side, text="User", width=16, bg=COLOR_SECONDARY, fg=COLOR_WHITE, command=self.open_user).pack(pady=5)
        tk.Button(side, text="Logout", width=16, bg=COLOR_BUTTON_RED, fg=COLOR_WHITE, command=self.root.destroy).pack(side=tk.BOTTOM, pady=20)

        main = tk.Frame(self.root, bg=COLOR_LIGHT_BG)
        main.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(main, text="Attendance Records", font=("Arial", 16, "bold"), bg=COLOR_LIGHT_BG).pack(pady=10)

        # Treeview
        self.tree = ttk.Treeview(main, columns=("Name", "Timestamp", "Type"), show="headings")
        for col in ("Name", "Timestamp", "Type"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Date filter
        f = tk.Frame(main, bg=COLOR_LIGHT_BG)
        f.pack(pady=5)
        tk.Label(f, text="Start Date:", bg=COLOR_LIGHT_BG).grid(row=0, column=0)
        self.start_cal = DateEntry(f, date_pattern='yyyy-mm-dd')
        self.start_cal.grid(row=0, column=1, padx=5)
        tk.Label(f, text="End Date:", bg=COLOR_LIGHT_BG).grid(row=0, column=2)
        self.end_cal = DateEntry(f, date_pattern='yyyy-mm-dd')
        self.end_cal.grid(row=0, column=3, padx=5)
        tk.Button(f, text="Filter", bg=COLOR_SECONDARY, fg=COLOR_WHITE, command=self.apply_date_filter).grid(row=0, column=4, padx=5)
        tk.Button(f, text="Reset", bg=COLOR_BUTTON_GREEN, fg=COLOR_WHITE, command=self.load_attendance).grid(row=0, column=5, padx=5)

        # Load and export frame
        self.load_attendance()
        ef = tk.Frame(main, bg=COLOR_LIGHT_BG)
        ef.pack(pady=10)
        tk.Button(ef, text="Export CSV", bg=COLOR_BUTTON_RED, fg=COLOR_WHITE, command=self.export_csv).pack(side=tk.LEFT, padx=5)
        tk.Button(ef, text="Export Excel", bg=COLOR_BUTTON_RED, fg=COLOR_WHITE, command=self.export_excel).pack(side=tk.LEFT, padx=5)
        tk.Button(ef, text="Export PDF", bg=COLOR_BUTTON_RED, fg=COLOR_WHITE, command=self.export_pdf).pack(side=tk.LEFT, padx=5)

    def load_attendance(self):
        # Populate tree with full data and store it
        for item in self.tree.get_children():
            self.tree.delete(item)
        if not os.path.exists(ATTENDANCE_FILE):
            self.displayed_df = pd.DataFrame(columns=["Name","Timestamp","Type"])
            return
        df = pd.read_csv(ATTENDANCE_FILE, header=None, names=["Name","Timestamp","Type"] )
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        self.displayed_df = df.copy()
        for _, row in df.iterrows():
            ts = row["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            self.tree.insert("", tk.END, values=(row["Name"], ts, row["Type"]))

    def apply_date_filter(self):
        # Filter underlying data and update tree & displayed_df
        start = pd.Timestamp(self.start_cal.get_date())
        end = pd.Timestamp(self.end_cal.get_date()) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        if not os.path.exists(ATTENDANCE_FILE):
            return
        df = pd.read_csv(ATTENDANCE_FILE, header=None, names=["Name","Timestamp","Type"] )
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        mask = (df["Timestamp"] >= start) & (df["Timestamp"] <= end)
        filtered = df.loc[mask]
        self.displayed_df = filtered.copy()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for _, row in filtered.iterrows():
            ts = row["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            self.tree.insert("", tk.END, values=(row["Name"], ts, row["Type"]))

    def export_csv(self):
        # Export only displayed_df
        if self.displayed_df is None or self.displayed_df.empty:
            messagebox.showwarning("No Data", "Nothing to export.")
            return
        path = os.path.join(os.path.expanduser("~"), "Desktop",
                            f"Attendance_{datetime.datetime.now():%Y%m%d_%H%M%S}.csv")
        self.displayed_df.to_csv(path, index=False)
        messagebox.showinfo("Export", f"CSV saved to {path}")

    def export_excel(self):
        # Export only displayed_df
        if self.displayed_df is None or self.displayed_df.empty:
            messagebox.showwarning("No Data", "Nothing to export.")
            return
        path = os.path.join(os.path.expanduser("~"), "Desktop",
                            f"Attendance_{datetime.datetime.now():%Y%m%d_%H%M%S}.xlsx")
        self.displayed_df.to_excel(path, index=False)
        messagebox.showinfo("Export", f"Excel saved to {path}")

    def export_pdf(self):
        # Export only displayed_df
        if self.displayed_df is None or self.displayed_df.empty:
            messagebox.showwarning("No Data", "Nothing to export.")
            return
        path = os.path.join(os.path.expanduser("~"), "Desktop",
                            f"Attendance_{datetime.datetime.now():%Y%m%d_%H%M%S}.pdf")
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        col_w = pdf.w / 3
        for col in ["Name", "Timestamp", "Type"]:
            pdf.cell(col_w, 10, col, 1)
        pdf.ln()
        for _, row in self.displayed_df.iterrows():
            pdf.cell(col_w, 10, str(row["Name"]), 1)
            pdf.cell(col_w, 10, row["Timestamp"].strftime("%Y-%m-%d %H:%M:%S"), 1)
            pdf.cell(col_w, 10, str(row["Type"]), 1)
            pdf.ln()
        pdf.output(path)
        messagebox.showinfo("Export", f"PDF saved to {path}")

    def open_attendance(self):
        subprocess.Popen([sys.executable, "ams.py"])
        self.root.destroy()

    def open_user(self):
        subprocess.Popen([sys.executable, "user.py"])
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    AdminApp(root)
    root.mainloop()
