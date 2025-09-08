import tkinter as tk
from tkinter import messagebox, Canvas
import mysql.connector
import sys
import subprocess
from datetime import datetime

# Get logged-in username from command-line arguments
logged_in_username = sys.argv[1].strip() if len(sys.argv) > 1 else None

# Function to calculate age from DOB
def calculate_age(dob):
    today = datetime.today()
    birth_date = datetime.strptime(str(dob), "%Y-%m-%d")
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# Function to create a full-screen purple gradient background
def draw_gradient(canvas, width, height):
    canvas.delete("gradient")  # Clear previous gradient
    for i in range(height):
        color = f'#{int(75 + (i / height) * 100):02x}{int(0 + (i / height) * 50):02x}{int(130 + (i / height) * 100):02x}'
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")

# Function to update gradient when window resizes


# Function to open the profile window
def open_profile():
    if not logged_in_username:
        messagebox.showerror("Error", "User not logged in!")
        return

    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root@123", database="bankdb")
        cursor = conn.cursor()
        cursor.execute("SELECT account_number, account_holder_name, username, email, gender, dob FROM users WHERE username = %s", (logged_in_username,))
        user_data = cursor.fetchone()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Error: {e}")
        return
    finally:
        if conn.is_connected():
            conn.close()

    if user_data:
        account_number, account_holder_name, username, email, gender, dob = user_data
        age = calculate_age(dob)

        profile_window = tk.Toplevel(root)
        profile_window.title("Profile Details")
        profile_window.state("zoomed")

        # Create a canvas for the gradient background
        profile_canvas = Canvas(profile_window)
        profile_canvas.pack(fill="both", expand=True)

        # Draw the purple gradient
        draw_gradient(profile_canvas, 1920, 1080)

        # Profile Frame (White background on top of gradient)
        frame = tk.Frame(profile_canvas, bg="white", bd=2, relief="ridge", padx=20, pady=15)
        frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=600)

        # Profile Information
        details = [
            ("📌 Account Number:", account_number),
            ("👤 Account Holder:", account_holder_name),
            ("🔑 Username:", username),
            ("📧 Email:", email),
            ("🚻 Gender:", gender),
            ("🎂 Date of Birth:", dob),
            ("📅 Age:", f"{age} years")
        ]

        for label, value in details:
            tk.Label(frame, text=label, font=("Arial", 12, "bold"), bg="white", fg="#222").pack(anchor="center", pady=3)
            tk.Label(frame, text=value, font=("Arial", 12), bg="white", fg="#444").pack(anchor="center", pady=1)

        # Buttons Container
        btn_frame = tk.Frame(frame, bg="white")
        btn_frame.pack(pady=15)

        logout_btn = tk.Button(btn_frame, text="🚪 Logout", font=("Arial", 12, "bold"), bg="#D32F2F", fg="white",
                               width=12, padx=5, pady=3, relief="ridge", command=root.quit)
        logout_btn.pack(side="left", padx=10)

        back_btn = tk.Button(btn_frame, text="🔙 Back", font=("Arial", 12, "bold"), bg="#007BFF", fg="white", width=12,
                             padx=5, pady=3, relief="ridge", command=profile_window.destroy)
        back_btn.pack(side="left", padx=10)

    else:
        messagebox.showerror("Error", "User details not found!")

# Functions for different windows
def open_expense_tracker():
    if not logged_in_username:
        messagebox.showerror("Error", "User not logged in!")
        return
    subprocess.Popen(["python", "expenseT_window.py", logged_in_username])

def open_transaction():
    if not logged_in_username:
        messagebox.showerror("Error", "User not logged in!")
        return
    subprocess.Popen(["python", "transaction.py", logged_in_username])

def open_set_tpin():
    if not logged_in_username:
        messagebox.showerror("Error", "User not logged in!")
        return
    subprocess.Popen(["python", "set_tpin.py", logged_in_username])

def open_money_request_window():
    if not logged_in_username:
        messagebox.showerror("Error", "User not logged in!")
        return
    subprocess.Popen(["python", "other_services.py", logged_in_username])

# Main Window
root = tk.Tk()
root.title("Bank Dashboard")
root.geometry("1280x720")
root.state("zoomed")  # Full-screen mode
root.resizable(True, True)

# Create a Canvas for the Gradient Background
canvas = Canvas(root)
canvas.pack(fill="both", expand=True)

# Draw the purple gradient
root.update_idletasks()
draw_gradient(canvas, root.winfo_width(), root.winfo_height())

# Bind resizing event to redraw gradient dynamically


# Main Container (Updated Lavender Background)
container = tk.Frame(root, bg="#D8BFD8", bd=5, relief="ridge")
container.place(relx=0.5, rely=0.5, anchor="center", width=900, height=650)

# Welcome Label
tk.Label(container, text=f"Welcome, {logged_in_username}!", font=("Arial", 18, "bold"), bg="#D8BFD8").pack(pady=15)

# Function to create buttons with styling
def create_button(text, bg_color, command):
    btn = tk.Button(container, text=text, font=("Arial", 14, "bold"), bg=bg_color, fg="white", padx=20, pady=10, relief="raised", borderwidth=3, width=30, command=command)
    btn.pack(pady=10)
    return btn

# Dashboard Buttons
create_button("👤 Profile", "blue", open_profile)
create_button("💰 Transactions", "green", open_transaction)
create_button("📊 Expense Tracker", "purple", open_expense_tracker)
create_button("⚙️ Set TPIN", "orange", open_set_tpin)
create_button("🔁 Other Services", "navy", open_money_request_window)

root.mainloop()

