import tkinter as tk
from tkinter import messagebox
import mysql.connector
import hashlib
import subprocess

def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

def connect_db():
    return mysql.connector.connect(host="localhost", user="Vrushali", password="Vrushali@1220", database="bankdb")

def reset_tpin():
    email = email_entry.get().strip()
    new_tpin = new_tpin_entry.get().strip()

    if not email or not new_tpin:
        messagebox.showerror("Error", "All fields are required!")
        return

    if not (new_tpin.isdigit() and len(new_tpin) == 6):
        messagebox.showerror("Error", "TPIN must be exactly 6 digits!")
        return

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if not user:
        messagebox.showerror("Error", "Email not found!")
        conn.close()
        return

    hashed_tpin = hash_pin(new_tpin)
    cursor.execute("UPDATE users SET tpin = %s WHERE email = %s", (hashed_tpin, email))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "TPIN reset successfully!")
    reset_window.destroy()

def open_forgot_tpin():
    subprocess.Popen(["python", "forgot_tpin.py"])

# GUI for Reset TPIN
reset_window = tk.Tk()
reset_window.title("Reset TPIN")
reset_window.geometry("350x300")
reset_window.configure(bg="#f0f0f0")

tk.Label(reset_window, text="Enter your Email:", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
email_entry = tk.Entry(reset_window, font=("Arial", 12))
email_entry.pack(pady=5)

tk.Label(reset_window, text="Enter New TPIN:", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)
new_tpin_entry = tk.Entry(reset_window, font=("Arial", 12), show="*")
new_tpin_entry.pack(pady=5)

tk.Button(reset_window, text="Reset TPIN", font=("Arial", 12), bg="blue", fg="white", command=reset_tpin).pack(pady=10)


reset_window.mainloop()
