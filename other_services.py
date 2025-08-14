import tkinter as tk
from tkinter import messagebox
import subprocess
import sys

# Get the logged-in username
if len(sys.argv) > 1:
    logged_in_username = sys.argv[1].strip()
else:
    logged_in_username = None

# Open Request Money Page
def open_request_money():
    if not logged_in_username:
        messagebox.showerror("Error", "User not logged in!")
        return
    try:
        subprocess.Popen(["python", "money_request.py", logged_in_username])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open Request Money page: {e}")

# Open Manage Requests Page
def open_manage_requests():
    if not logged_in_username:
        messagebox.showerror("Error", "User not logged in!")
        return
    try:
        subprocess.Popen(["python", "manage_request.py", logged_in_username])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open Manage Requests page: {e}")

def open_loan_management():
    if not logged_in_username:
        messagebox.showerror("Error", "User not logged in!")
        return
    try:
        subprocess.Popen(["python", "loan_management_window.py", logged_in_username])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open Loan Management page: {e}")

# Function to create a purple gradient background
def draw_gradient(canvas, width, height):
    canvas.delete("gradient")  # Clear previous gradient
    for i in range(height):
        color = f'#{int(75 + (i / height) * 100):02x}{int(0 + (i / height) * 50):02x}{int(130 + (i / height) * 100):02x}'
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")

# Hover effect for buttons
def on_enter(e):
    e.widget["bg"] = "#5A2EA3"

def on_leave(e):
    e.widget["bg"] = e.widget.default_bg

# Create the main window
root = tk.Tk()
root.title("Other Services")
root.geometry("600x400")
root.state("zoomed")  # Maximize window

# Create a canvas for the gradient background
canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight(), highlightthickness=0)
canvas.pack(fill="both", expand=True)
root.update_idletasks()
draw_gradient(canvas, root.winfo_width(), root.winfo_height())
# Create a centered container
container = tk.Frame(root, bg="lavender", bd=5, relief="ridge")
container.place(relx=0.5, rely=0.5, anchor="center", width=400, height=300)

# Header Label
header_label = tk.Label(container, text="💰 Other Services", font=("Arial", 16, "bold"), fg="#4A148C", bg="lavender")
header_label.pack(pady=10)

# Button styling
button_style = {"font": ("Arial", 12, "bold"), "fg": "white", "width": 20, "height": 2}

# Request Money Button
request_button = tk.Button(container, text="📜 Request Money", bg="orange", **button_style, command=open_request_money)
request_button.pack(pady=10)
request_button.default_bg = "orange"
request_button.bind("<Enter>", on_enter)
request_button.bind("<Leave>", on_leave)

# Manage Requests Button
manage_button = tk.Button(container, text="📅 Manage Requests", bg="purple", **button_style, command=open_manage_requests)
manage_button.pack(pady=10)
manage_button.default_bg = "Purple"
manage_button.bind("<Enter>", on_enter)
manage_button.bind("<Leave>", on_leave)

#Loan Management Button
loan_button = tk.Button(container, text="Loan Management", bg="Dark Blue", **button_style, command=open_loan_management)
loan_button.pack(pady=10)
loan_button.default_bg = "Dark Blue"
loan_button.bind("<Enter>", on_enter)
loan_button.bind("<Leave>", on_leave)

# Run the GUI
root.mainloop()
