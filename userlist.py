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
COLOR_BTN_EDIT  = "#F39C12"
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
                  font=("Arial", 12),
                  bg=COLOR_BTN_BACK,
                  fg=COLOR_BTN_TEXT,
                  command=self.go_back).pack(side=tk.RIGHT, padx=20, pady=10)

        # Treeview for listing
        cols = ("Name", "Position")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=350 if c == "Name" else 200, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Buttons
        btn_frame = tk.Frame(self.root, bg=COLOR_BG)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame,
                  text="Edit Selected",
                  font=("Arial", 14),
                  bg=COLOR_BTN_EDIT,
                  fg=COLOR_BTN_TEXT,
                  command=self.edit_selected).pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame,
                  text="Delete Selected",
                  font=("Arial", 14),
                  bg=COLOR_BTN_DEL,
                  fg=COLOR_BTN_TEXT,
                  command=self.delete_selected).pack(side=tk.LEFT, padx=10)

        self.load_users()

    def load_users(self):
        # clear existing
        for i in self.tree.get_children():
            self.tree.delete(i)
        os.makedirs(dataset_folder, exist_ok=True)
        for fname in sorted(os.listdir(dataset_folder)):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                name, pos = os.path.splitext(fname)[0].split(',', 1) if ',' in fname else (fname, '')
                self.tree.insert('', tk.END, iid=fname, values=(name.strip(), pos.strip()))

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

    def edit_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a user to edit.")
            return
        old_filename = sel[0]
        old_name, old_position = self.tree.item(old_filename)['values']
        extension = os.path.splitext(old_filename)[1]

        # Pop-up window for editing
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit User")
        edit_win.geometry("300x200")
        tk.Label(edit_win, text="Name:").pack(pady=5)
        name_entry = tk.Entry(edit_win)
        name_entry.insert(0, old_name)
        name_entry.pack(pady=5)

        tk.Label(edit_win, text="Position:").pack(pady=5)
        pos_entry = tk.Entry(edit_win)
        pos_entry.insert(0, old_position)
        pos_entry.pack(pady=5)

        def save_changes():
            new_name = name_entry.get().strip()
            new_position = pos_entry.get().strip()
            if not new_name:
                messagebox.showerror("Invalid Input", "Name cannot be empty.")
                return
            new_filename = f"{new_name}, {new_position}{extension}" if new_position else f"{new_name}{extension}"
            old_path = os.path.join(dataset_folder, old_filename)
            new_path = os.path.join(dataset_folder, new_filename)
            try:
                os.rename(old_path, new_path)
                edit_win.destroy()
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to rename: {e}")

        tk.Button(edit_win, text="Save", command=save_changes, bg="#2ECC71", fg="white", font=("Arial", 12)).pack(pady=15)

    def go_back(self):
        script = os.path.join(os.path.dirname(__file__), "user.py")
        subprocess.Popen([sys.executable, script])
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = UserListApp(root)
    root.mainloop()
