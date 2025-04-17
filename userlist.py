import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess

# Folder where user images are stored
dataset_folder = "dataset"

# Color palette
COLOR_HEADER_BG = "#3498DB"
COLOR_BG        = "#FFFFFF"
COLOR_BTN_DEL   = "#E74C3C"
COLOR_BTN_BACK  = "#3498DB"
COLOR_BTN_TEXT  = "#FFFFFF"

class UserListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("User List")
        self.root.geometry("800x600")
        self.root.configure(bg=COLOR_BG)

        # Header bar
        header = tk.Frame(self.root, bg=COLOR_HEADER_BG, height=50)
        header.pack(fill=tk.X)
        tk.Label(header,
                 text="Registered Users",
                 font=("Arial", 20, "bold"),
                 bg=COLOR_HEADER_BG,
                 fg=COLOR_BTN_TEXT).pack(side=tk.LEFT, padx=20)
        tk.Button(header,
                  text="Back",
                  font=("Arial",12),
                  bg=COLOR_BTN_BACK,
                  fg=COLOR_BTN_TEXT,
                  command=self.go_back).pack(side=tk.RIGHT, padx=20, pady=10)

        # Treeview for listing
        cols = ("Name","Position")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=350 if c=="Name" else 200, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Delete button
        btn_frame = tk.Frame(self.root, bg=COLOR_BG)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame,
                  text="Delete Selected",
                  font=("Arial",14),
                  bg=COLOR_BTN_DEL,
                  fg=COLOR_BTN_TEXT,
                  command=self.delete_selected).pack()

        self.load_users()

    def load_users(self):
        # clear existing
        for i in self.tree.get_children():
            self.tree.delete(i)
        # ensure folder exists
        os.makedirs(dataset_folder, exist_ok=True)
        # list files
        for fname in sorted(os.listdir(dataset_folder)):
            if fname.lower().endswith(('.png','.jpg','.jpeg')):
                name, pos = os.path.splitext(fname)[0].split(',',1) if ',' in fname else (fname, '')
                name = name.strip()
                pos = pos.strip()
                # use filename as iid to delete file later
                self.tree.insert('', tk.END, iid=fname, values=(name,pos))

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a user to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Delete selected user(s)?")
        if not confirm:
            return
        for iid in sel:
            path = os.path.join(dataset_folder, iid)
            try:
                os.remove(path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete {iid}: {e}")
        self.load_users()

    def go_back(self):
        # Return to user registration
        script = os.path.join(os.path.dirname(__file__), "user.py")
        subprocess.Popen([sys.executable, script])
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = UserListApp(root)
    root.mainloop()
