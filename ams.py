import os
import sys
import cv2
import time
import csv
import numpy as np
import datetime
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
import pandas as pd
from fpdf import FPDF
import subprocess

# Global attendance file
ATTENDANCE_FILE = "attendance.csv"

# Face recognition setup
mtcnn = MTCNN(image_size=160, margin=0)
resnet = InceptionResnetV1(pretrained='vggface2').eval()

# Load embeddings once

def process_dataset(path):
    embeddings = {}
    for img_name in os.listdir(path):
        if img_name.lower().endswith(('.png','jpg','jpeg')):
            img = Image.open(os.path.join(path, img_name))
            face = mtcnn(img)
            if face is not None:
                emb = resnet(face.unsqueeze(0))
                embeddings[os.path.splitext(img_name)[0]] = emb.detach().numpy()
    return embeddings

embeddings_dict = process_dataset("dataset")

# Recognition helper
def recognize_face(face_emb, db, threshold=0.9):
    best, dist = None, float('inf')
    for name, db_emb in db.items():
        d = np.linalg.norm(face_emb.detach().numpy() - db_emb)
        if d < dist:
            best, dist = name, d
    return (best, dist) if dist < threshold else (None, dist)

# Attendance logging
def mark_attendance(name, typ):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ATTENDANCE_FILE, 'a', newline='') as f:
        csv.writer(f).writerow([name, ts, typ])
    messagebox.showinfo("Recorded", f"{typ} for {name} at {ts}")

class FaceAttendanceApp:
    COLOR_HEADER_BG = "#3498DB"
    COLOR_BG        = "#F0F0F0"
    COLOR_BTN_IN    = "#27AE60"
    COLOR_BTN_OUT   = "#E74C3C"
    COLOR_BTN_AGAIN = "#B0B0B0"

    def __init__(self, root):
        self.root = root
        self.current_name = None

        self.root.title("Attendance Monitoring System")
        self.root.geometry("1280x720")
        # Header
        hdr = tk.Frame(root, bg=self.COLOR_HEADER_BG, height=60)
        hdr.pack(fill=tk.X)
        tk.Label(hdr,
                 text="ATTENDANCE MONITORING SYSTEM",
                 font=("Arial", 24),
                 fg="white",
                 bg=self.COLOR_HEADER_BG).pack(side=tk.LEFT, padx=20)
        tk.Button(hdr,
                  text="Back",
                  font=("Arial", 12),
                  command=self.open_admin).pack(side=tk.RIGHT, padx=20)

        # Date/time label
        self.dt_label = tk.Label(root,
                                 text=datetime.datetime.now().strftime("%B %d, %Y   %I:%M %p"),
                                 font=("Arial", 14))
        self.dt_label.pack(pady=10)
        self.update_clock()

        # Video frame (smaller)
        self.video_frame = tk.Frame(root, bg="black", height=360)
        self.video_frame.pack(fill=tk.X, padx=20, pady=10)
        self.video_label = tk.Label(self.video_frame)
        self.video_label.pack()

        # Name/info label
        self.name_label = tk.Label(root,
                                   text="No face detected",
                                   font=("Arial",16))
        self.name_label.pack(pady=10)

        # Buttons
        btn_f = tk.Frame(root)
        btn_f.pack(pady=20)
        tk.Button(btn_f,
                  text="Time In",
                  bg=self.COLOR_BTN_IN,
                  fg="white",
                  font=("Arial",14),
                  width=12,
                  command=lambda: self.record("Time In")).grid(row=0, column=0, padx=15)
        tk.Button(btn_f,
                  text="Time Out",
                  bg=self.COLOR_BTN_OUT,
                  fg="white",
                  font=("Arial",14),
                  width=12,
                  command=lambda: self.record("Time Out")).grid(row=0, column=1, padx=15)
        tk.Button(btn_f,
                  text="Again",
                  bg=self.COLOR_BTN_AGAIN,
                  fg="black",
                  font=("Arial",14),
                  width=12,
                  command=self.reset_detection).grid(row=0, column=2, padx=15)

        # Webcam init with smaller resolution
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

        self.update_video()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_clock(self):
        self.dt_label.config(text=datetime.datetime.now().strftime("%B %d, %Y   %I:%M %p"))
        self.root.after(60000, self.update_clock)

    def update_video(self):
        ret, frame = self.cap.read()
        if not ret:
            self.root.after(10, self.update_video)
            return
        # Resize frame to 640x360
        frame = cv2.resize(frame, (640, 360))

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        boxes, _ = mtcnn.detect(pil)

        if boxes is not None and len(boxes):
            face = mtcnn(pil)
            if face is not None:
                emb = resnet(face.unsqueeze(0))
                name, dist = recognize_face(emb, embeddings_dict)
                if name:
                    self.current_name = name
                    self.name_label.config(text=f"{name} detected")
                    x1,y1,x2,y2 = map(int, boxes[0])
                    cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
                else:
                    self.name_label.config(text="Unknown face")
            else:
                self.name_label.config(text="Face not aligned")
        else:
            self.current_name = None
            self.name_label.config(text="No face detected")

        imgtk = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk)
        self.root.after(10, self.update_video)

    def record(self, typ):
        if not self.current_name:
            messagebox.showwarning("No one","No recognized face to record.")
            return
        mark_attendance(self.current_name, typ)

    def reset_detection(self):
        self.current_name = None
        self.name_label.config(text="No face detected")

    def open_admin(self):
        script = os.path.join(os.path.dirname(__file__), "admin.py")
        subprocess.Popen([sys.executable, script])
        self.on_close()

    def on_close(self):
        self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    FaceAttendanceApp(root)
    root.mainloop()
