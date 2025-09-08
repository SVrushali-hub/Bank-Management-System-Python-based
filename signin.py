import tkinter as tk
from tkinter import ttk, Canvas
from tkcalendar import Calendar
import mysql.connector
import re
import os
import hashlib

# Function to hash the PIN
def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

# PIN strength validation
def check_pin_strength(event=None):
    pin = entry_pin.get()
    if len(pin) == 6 and pin.isdigit():
        strength_label.config(text="✅", fg="green")
    else:
        strength_label.config(text="❌", fg="red")

# Account number validation
def validate_account_number(event=None):
    acc_no = entry_acc_no.get()
    if acc_no.isdigit() and len(acc_no) == 10:
        acc_status_label.config(text="✅", fg="green")
    else:
        acc_status_label.config(text="❌", fg="red")

# Holder name validation
def update_holder_name_status(event=None):
    name = entry_holder_name.get()
    if name == "" or not all(c.isalpha() or c.isspace() for c in name):
        holder_name_status.config(text="❌", fg="red")
    else:
        holder_name_status.config(text="✅", fg="green")

def validate_email(event=None):
    email = entry_email.get().strip()
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(email_regex, email):
        email_status_label.config(text="✅", fg="green")
    else:
        email_status_label.config(text="❌", fg="red")
        return

    try:
        conn = mysql.connector.connect(host="localhost", user="root", password="root@123", database="bankdb")
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            success_label.config(text="Email already registered ❌", fg="red")
        conn.close()
    except Exception as e:
        success_label.config(text=f"Error: {str(e)} ❌", fg="red")

# Limit inputs
def limit_account_number_input(P):
    return P == "" or (P.isdigit() and len(P) <= 10)

def validate_holder_name_input(P):
    return P == "" or (all(char.isalpha() or char.isspace() for char in P) and len(P) <= 50)

# DOB Calendar picker
def pick_date():
    top = tk.Toplevel(root)
    top.title("Select Date of Birth")
    cal = Calendar(top, selectmode="day", year=2000, month=1, day=1, date_pattern="yyyy-mm-dd")
    cal.pack(pady=20)

    def grab_date():
        entry_dob.delete(0, tk.END)
        entry_dob.insert(0, cal.get_date())
        top.destroy()

    tk.Button(top, text="Select", command=grab_date, font=("Arial", 12), bg="blue", fg="white").pack(pady=10)

# Gradient background
def draw_gradient(canvas, width, height):
    for i in range(height):
        color = f'#{int(75 + (i / height) * 100):02x}{int(0 + (i / height) * 50):02x}{int(130 + (i / height) * 100):02x}'
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")

def resize_canvas(event):
    draw_gradient(canvas, event.width, event.height)
    canvas.config(width=event.width, height=event.height)
    container.place(relx=0.5, rely=0.5, anchor="center")

# Submit user
def register_user():
    account_number = entry_acc_no.get().strip()
    account_holder_name = entry_holder_name.get().strip()
    username = entry_username.get().strip()
    email = entry_email.get().strip()
    dob = entry_dob.get().strip()
    pin = entry_pin.get().strip()
    gender = gender_var.get()

    if not account_number.isdigit() or len(account_number) != 10:
        success_label.config(text="Account number must be 10 digits ❌", fg="red")
        return

    if not account_holder_name.replace(" ", "").isalpha():
        success_label.config(text="Invalid Account Holder Name ❌", fg="red")
        return

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, email):
        success_label.config(text="Invalid email format ❌", fg="red")
        return

    if not (pin.isdigit() and len(pin) == 6):
        success_label.config(text="PIN must be 6 digits ❌", fg="red")
        return

    if gender == "Select Gender":
        success_label.config(text="Please select a valid gender ❌", fg="red")
        return

    hashed_pin = hash_pin(pin)

    try:
        conn = mysql.connector.connect(host="localhost", user="Vrushali", password="Vrushali@1220", database="bankdb")
        cursor = conn.cursor()

        cursor.execute("SELECT account_number FROM users WHERE account_number = %s", (account_number,))
        if cursor.fetchone():
            success_label.config(text="Account number already exists ❌", fg="red")
            conn.close()
            return

        cursor.execute(
            "INSERT INTO users (account_number, account_holder_name, username, email, dob, pin, gender) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (account_number, account_holder_name, username, email, dob, hashed_pin, gender)
        )
        conn.commit()
        conn.close()

        success_label.config(text="Registered Successfully ✅", fg="green")
        root.after(1000, open_login)
    except Exception as e:
        success_label.config(text=f"Error: {str(e)} ❌", fg="red")

def open_login():
    root.destroy()
    os.system("python login.py")

# GUI Setup
root = tk.Tk()
root.title("Bank Account Registration")
root.geometry("800x700")
root.state("zoomed")
root.resizable(True, True)

canvas = Canvas(root)
canvas.pack(fill="both", expand=True)
draw_gradient(canvas, 800, 700)

container = tk.Frame(root, bg="#E6E6FA", bd=5, relief="ridge")
container.place(relx=0.5, rely=0.5, anchor="center", width=500, height=700)

tk.Label(container, text="FinFlow Account Registration", font=("Arial", 16, "bold"), fg="#333", bg="#E6E6FA").pack(pady=10)

# === ACCOUNT NUMBER ===
tk.Label(container, text="Account Number:", font=("Arial", 12), bg="#E6E6FA").pack(pady=(10, 0))
acc_frame = tk.Frame(container, bg="#E6E6FA")
acc_frame.pack(pady=(0, 10))
vcmd_acc = (root.register(limit_account_number_input), '%P')
entry_acc_no = tk.Entry(acc_frame, font=("Arial", 12), width=25, bd=2, relief="solid", validate="key", validatecommand=vcmd_acc)
entry_acc_no.pack(side="left", padx=5)
entry_acc_no.bind("<KeyRelease>", validate_account_number)
acc_status_label = tk.Label(acc_frame, text="", font=("Arial", 12), bg="#E6E6FA")
acc_status_label.pack(side="left", padx=5)

# === ACCOUNT HOLDER NAME ===
tk.Label(container, text="Account Holder Name:", font=("Arial", 12), bg="#E6E6FA").pack(pady=(10, 0))
name_frame = tk.Frame(container, bg="#E6E6FA")
name_frame.pack(pady=(0, 10))
vcmd_name = (root.register(validate_holder_name_input), '%P')
entry_holder_name = tk.Entry(name_frame, font=("Arial", 12), width=25, bd=2, relief="solid", validate="key", validatecommand=vcmd_name)
entry_holder_name.pack(side="left", padx=5)
entry_holder_name.bind("<KeyRelease>", update_holder_name_status)
holder_name_status = tk.Label(name_frame, text="", font=("Arial", 12), bg="#E6E6FA")
holder_name_status.pack(side="left", padx=5)

# === USERNAME ===
tk.Label(container, text="Username:", font=("Arial", 12), bg="#E6E6FA").pack(pady=(10, 0))
entry_username = tk.Entry(container, font=("Arial", 12), width=25, bd=2, relief="solid")
entry_username.pack(pady=(0, 10))

# === EMAIL ===
tk.Label(container, text="Email ID:", font=("Arial", 12), bg="#E6E6FA").pack(pady=(10, 0))
email_frame = tk.Frame(container, bg="#E6E6FA")
email_frame.pack(pady=(0, 10))
entry_email = tk.Entry(email_frame, font=("Arial", 12), width=25, bd=2, relief="solid")
entry_email.pack(side="left", padx=5)
entry_email.bind("<KeyRelease>", validate_email)
email_status_label = tk.Label(email_frame, text="", font=("Arial", 12), bg="#E6E6FA")
email_status_label.pack(side="left", padx=5)

# === DOB ===
dob_frame = tk.Frame(container, bg="#E6E6FA")
dob_frame.pack(pady=(0, 10))
tk.Label(dob_frame, text="Date of Birth:", font=("Arial", 12), bg="#E6E6FA").pack(side="left")
entry_dob = tk.Entry(dob_frame, font=("Arial", 12), bd=2, relief="solid", width=15)
entry_dob.pack(side="left", padx=5)
tk.Button(dob_frame, text="📅", font=("Arial", 12), relief="flat", bg="#E6E6FA", command=pick_date).pack(side="left")

# === GENDER ===
tk.Label(container, text="Gender:", font=("Arial", 12), bg="#E6E6FA").pack(pady=5)
gender_var = tk.StringVar(value="Select Gender")
gender_dropdown = ttk.Combobox(container, textvariable=gender_var, font=("Arial", 12), state="readonly",
                               values=("Select Gender", "Male", "Female", "Other"))
gender_dropdown.pack(pady=5, ipadx=10, ipady=3)

# === PIN ===
tk.Label(container, text="PIN (6 digits):", font=("Arial", 12), bg="#E6E6FA").pack(pady=(10, 0))
pin_frame = tk.Frame(container, bg="#E6E6FA")
pin_frame.pack(pady=(0, 10))
entry_pin = tk.Entry(pin_frame, font=("Arial", 12), width=25, bd=2, relief="solid", show="*")
entry_pin.pack(side="left", padx=5)
entry_pin.bind("<KeyRelease>", check_pin_strength)
strength_label = tk.Label(pin_frame, text="", font=("Arial", 12), bg="#E6E6FA")
strength_label.pack(side="left", padx=5)

# === REGISTER BUTTON ===
tk.Button(container, text="Register", font=("Arial", 12, "bold"), bg="#6a0dad", fg="white", padx=20, pady=5,
          relief="raised", borderwidth=3, command=register_user).pack(pady=10)

tk.Button(container, text="Already have an account? Login here!", font=("Arial", 10, "underline"), fg="Purple",
          bg="#E6E6FA", relief="flat", command=open_login).pack(pady=5)

success_label = tk.Label(container, text="", font=("Arial", 12), fg="green", bg="#E6E6FA")
success_label.pack()

root.bind("<Configure>", resize_canvas)
root.mainloop()

