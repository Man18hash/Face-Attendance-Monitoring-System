import os
import sys
import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import datetime
import subprocess

# Color palette
COLOR_HEADER_BG   = "#3498DB"
COLOR_BG          = "#FFFFFF"
COLOR_BUTTON      = "#3498DB"
COLOR_BUTTON_TEXT = "#FFFFFF"
COLOR_SAVE_BG     = "#2ECC71"

class UserRegistration:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Monitoring System")
        # Increase window height to accommodate bottom buttons
        self.root.geometry("1000x700")
        self.root.configure(bg=COLOR_BG)

        # Header bar
        header = tk.Frame(self.root, bg=COLOR_HEADER_BG, height=80)
        # Fix header size to ensure buttons are fully visible
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(
            header,
            text="ATTENDANCE MONITORING SYSTEM",
            font=("Arial", 20, "bold"),
            bg=COLOR_HEADER_BG,
            fg=COLOR_BUTTON_TEXT
        ).pack(side=tk.LEFT, padx=20)
        # User List button
        tk.Button(
            header,
            text="",
            font=("Arial", 12),
            bg=COLOR_HEADER_BG,
            fg=COLOR_BUTTON_TEXT,
            relief=tk.FLAT,
            command=self.open_user_list
        ).pack(side=tk.RIGHT, padx=10, pady=10)
        # Back button
        tk.Button(
            header,
            text="Back",
            font=("Arial", 12),
            bg=COLOR_HEADER_BG,
            fg=COLOR_BUTTON_TEXT,
            relief=tk.FLAT,
            command=self.go_admin
        ).pack(side=tk.RIGHT, padx=10, pady=10)

        # Video preview frame
        self.video_frame = tk.Frame(self.root, bg="#DDDDDD", width=800, height=300)
        self.video_frame.pack(pady=20)
        self.video_frame.pack_propagate(False)
        self.video_label = tk.Label(self.video_frame)
        self.video_label.pack(fill=tk.BOTH, expand=True)

        # Capture / Retake buttons
        btn_frame = tk.Frame(self.root, bg=COLOR_BG)
        btn_frame.pack(pady=10)
        tk.Button(
            btn_frame,
            text="Take",
            font=("Arial", 12),
            bg=COLOR_BUTTON,
            fg=COLOR_BUTTON_TEXT,
            width=12,
            command=self.capture
        ).grid(row=0, column=0, padx=20)
        tk.Button(
            btn_frame,
            text="Retake",
            font=("Arial", 12),
            bg=COLOR_BUTTON,
            fg=COLOR_BUTTON_TEXT,
            width=12,
            command=self.retake
        ).grid(row=0, column=1, padx=20)

        # Entry fields
        entry_frame = tk.Frame(self.root, bg=COLOR_BG)
        entry_frame.pack(pady=20)
        tk.Label(
            entry_frame,
            text="Name:",
            font=("Arial", 14),
            bg=COLOR_BG
        ).grid(row=0, column=0, sticky=tk.E, padx=10, pady=5)
        self.name_entry = tk.Entry(entry_frame, font=("Arial", 14), width=30)
        self.name_entry.grid(row=0, column=1, pady=5)

        tk.Label(
            entry_frame,
            text="Position:",
            font=("Arial", 14),
            bg=COLOR_BG
        ).grid(row=1, column=0, sticky=tk.E, padx=10, pady=5)
        self.position_entry = tk.Entry(entry_frame, font=("Arial", 14), width=30)
        self.position_entry.grid(row=1, column=1, pady=5)

        # Save button
        tk.Button(
            self.root,
            text="Save",
            font=("Arial", 14),
            bg=COLOR_SAVE_BG,
            fg=COLOR_BUTTON_TEXT,
            width=40,
            command=self.save
        ).pack(pady=20)

        # User List button at bottom
        tk.Button(
            self.root,
            text="User List",
            font=("Arial", 14),
            bg=COLOR_BUTTON,
            fg=COLOR_BUTTON_TEXT,
            width=40,
            command=self.open_user_list
        ).pack(pady=5)

        # Initialize webcam
        self.video_capture = cv2.VideoCapture(0)
        self.current_frame = None
        self.captured_image = None
        self.update_video()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_video(self):
        if self.captured_image is None:
            ret, frame = self.video_capture.read()
            if ret:
                self.current_frame = frame
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
        self.root.after(10, self.update_video)

    def capture(self):
        if self.current_frame is not None:
            self.captured_image = self.current_frame.copy()
            cv2image = cv2.cvtColor(self.captured_image, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        else:
            messagebox.showwarning("Capture Error", "No frame available")

    def retake(self):
        self.captured_image = None

    def save(self):
        if self.captured_image is None:
            messagebox.showwarning("No Image", "Capture first.")
            return
        name = self.name_entry.get().strip()
        pos = self.position_entry.get().strip()
        if not name:
            messagebox.showwarning("No Name", "Enter name.")
            return
        if not pos:
            messagebox.showwarning("No Position", "Enter position.")
            return
        folder = "dataset"
        os.makedirs(folder, exist_ok=True)
        filename = f"{name}, {pos}.jpg"
        path = os.path.join(folder, filename)
        cv2.imwrite(path, self.captured_image)
        messagebox.showinfo("Saved", f"Image saved to {path}")
        self.captured_image = None
        self.name_entry.delete(0, tk.END)
        self.position_entry.delete(0, tk.END)

    def open_user_list(self):
        script = os.path.join(os.path.dirname(__file__), "userlist.py")
        subprocess.Popen([sys.executable, script])

    def go_admin(self):
        self.close()
        subprocess.Popen([sys.executable, "admin.py"])

    def on_close(self):
        self.close()

    def close(self):
        if self.video_capture.isOpened():
            self.video_capture.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = UserRegistration(root)
    root.mainloop()