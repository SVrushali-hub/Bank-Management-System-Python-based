import tkinter as tk
import mysql.connector
import os
import hashlib

# Function to hash the PIN using SHA-256
def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

# Function to authenticate user
def login_user():
    username = entry_username.get().strip()
    pin = entry_pin.get().strip()

    # Validate input fields
    if not username or not pin:
        error_label.config(text="Fields cannot be empty ❌", fg="red")
        success_label.config(text="")
        return

    if not (pin.isdigit() and len(pin) == 6):
        error_label.config(text="Invalid PIN (6 digits required) ❌", fg="red")
        success_label.config(text="")
        return

    try:
        conn = mysql.connector.connect(host="localhost", user="Vrushali", password="Vrushali@1220", database="bankdb")
        cursor = conn.cursor()
        cursor.execute("SELECT pin FROM users WHERE BINARY username = %s", (username,))
        user = cursor.fetchone()

        if user and hash_pin(pin) == user[0]:
            success_label.config(text="Login Successful ✅", fg="green")
            error_label.config(text="")
            root.after(1000, lambda: open_dashboard(username))
        else:
            error_label.config(text="Incorrect username or PIN ❌", fg="red")
            success_label.config(text="")

    except mysql.connector.Error:
        error_label.config(text="Database error ❌", fg="red")
    finally:
        if 'conn' in locals():
            conn.close()

# Function to open the dashboard after successful login
def open_dashboard(username):
    root.destroy()
    os.system(f"python dashboard.py {username}")

# Redirect to Registration
def open_signin():
    root.destroy()
    os.system("python signin.py")

# Function to create Forgot PIN window
def open_forgot_pin():
    forgot_win = tk.Toplevel(root)
    forgot_win.title("Forgot PIN")
    forgot_win.geometry("400x300")
    forgot_win.configure(bg="lavender")

    tk.Label(forgot_win, text="Reset PIN", font=("Arial", 14, "bold"), fg="#4A148C", bg="lavender").pack(pady=10)

    tk.Label(forgot_win, text="Enter your Email:", font=("Arial", 12), bg="lavender").pack()
    entry_email = tk.Entry(forgot_win, font=("Arial", 12), bd=2, relief="solid")
    entry_email.pack(pady=5, ipadx=10, ipady=3)

    error_label_fp = tk.Label(forgot_win, text="", fg="red", font=("Arial", 10, "bold"), bg="lavender")
    error_label_fp.pack()

    success_label_fp = tk.Label(forgot_win, text="", fg="green", font=("Arial", 10, "bold"), bg="lavender")
    success_label_fp.pack()

    def verify_email():
        email = entry_email.get().strip()
        if not email:
            error_label_fp.config(text="Email cannot be empty ❌")
            success_label_fp.config(text="")
            return

        try:
            conn = mysql.connector.connect(host="localhost", user="Vrushali", password="Vrushali@1220", database="bankdb")
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user:
                error_label_fp.config(text="")
                success_label_fp.config(text="Email verified ✅")

                tk.Label(forgot_win, text="Enter New PIN (6 digits):", font=("Arial", 12), bg="lavender").pack()
                entry_new_pin = tk.Entry(forgot_win, font=("Arial", 12), bd=2, relief="solid", show="*")
                entry_new_pin.pack(pady=5, ipadx=10, ipady=3)

                def reset_pin():
                    new_pin = entry_new_pin.get().strip()
                    if not (new_pin.isdigit() and len(new_pin) == 6):
                        error_label_fp.config(text="Invalid PIN (6 digits required) ❌")
                        success_label_fp.config(text="")
                        return

                    hashed_pin = hash_pin(new_pin)

                    try:
                        conn2 = mysql.connector.connect(host="localhost", user="Vrushali", password="Vrushali@1220", database="bankdb")
                        cursor2 = conn2.cursor()
                        cursor2.execute("UPDATE users SET pin = %s WHERE email = %s", (hashed_pin, email))
                        conn2.commit()

                        if cursor2.rowcount > 0:
                            success_label_fp.config(text="PIN updated successfully ✅")
                            error_label_fp.config(text="")
                            forgot_win.after(1500, forgot_win.destroy)
                        else:
                            error_label_fp.config(text="Error updating PIN ❌")
                            success_label_fp.config(text="")

                    except mysql.connector.Error as e:
                        error_label_fp.config(text=f"Database error: {e}")
                    finally:
                        if 'conn2' in locals():
                            conn2.close()

                tk.Button(forgot_win, text="Reset PIN", font=("Arial", 12, "bold"), bg="#6A1B9A", fg="white",
                          relief="raised", padx=20, pady=5, borderwidth=3, command=reset_pin).pack(pady=10)

            else:
                error_label_fp.config(text="Email not found ❌")
                success_label_fp.config(text="")

        except mysql.connector.Error:
            error_label_fp.config(text="Database error ❌")
        finally:
            if 'conn' in locals():
                conn.close()

    tk.Button(forgot_win, text="Verify Email", font=("Arial", 12, "bold"), bg="#6A1B9A", fg="white",
              relief="raised", padx=20, pady=5, borderwidth=3, command=verify_email).pack(pady=10)

# Function to create a gradient background
def draw_gradient(canvas, width, height):
    canvas.delete("gradient")  # Clear previous gradient
    for i in range(height):
        color = f'#{int(75 + (i / height) * 100):02x}{int(0 + (i / height) * 50):02x}{int(130 + (i / height) * 100):02x}'
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")

# Function to update canvas on resize
def resize_canvas(event):
    draw_gradient(canvas, event.width, event.height)
    canvas.config(width=event.width, height=event.height)
    frame.place(relx=0.5, rely=0.5, anchor="center")  # Keep frame centered

# GUI Window
root = tk.Tk()
root.title("Bank Login")
root.geometry("450x500")
root.state("zoomed")
root.resizable(True, True)

# Create Canvas for Gradient Background
canvas = tk.Canvas(root)
canvas.pack(fill="both", expand=True)

# Draw the Purple Gradient
draw_gradient(canvas, 450, 500)

# Login Frame
frame = tk.Frame(root, bg="lavender", bd=5, relief="ridge")
frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=350)

# Header
tk.Label(frame, text="FinFlow Account Login", font=("Arial", 16, "bold"), fg="#4A148C", bg="lavender").pack(pady=10)

# Username
tk.Label(frame, text="Username:", font=("Arial", 12), bg="lavender").pack()
entry_username = tk.Entry(frame, font=("Arial", 12), bd=2, relief="solid")
entry_username.pack(pady=5, ipadx=10, ipady=3)

# PIN
tk.Label(frame, text="PIN (6 digits):", font=("Arial", 12), bg="lavender").pack()
entry_pin = tk.Entry(frame, font=("Arial", 12), bd=2, relief="solid", show="*")
entry_pin.pack(pady=(5, 2), ipadx=10, ipady=3)

# Success & Error Messages
success_label = tk.Label(frame, text="", fg="green", font=("Arial", 10, "bold"), bg="lavender")
success_label.pack()
error_label = tk.Label(frame, text="", fg="red", font=("Arial", 10, "bold"), bg="lavender")
error_label.pack()

# Login Button
tk.Button(frame, text="Login", font=("Arial", 12, "bold"), bg="#6A1B9A", fg="white", relief="raised",
          padx=20, pady=5, borderwidth=3, command=login_user).pack(pady=5)

# Forgot PIN & Register Buttons
tk.Button(frame, text="Forgot PIN?", font=("Arial", 10, "underline"), fg="#6A1B9A", bg="lavender", relief="flat",
          command=open_forgot_pin).pack(pady=2)

tk.Button(frame, text="Don't have an account? Register here!", font=("Arial", 10, "underline"),
          fg="#6A1B9A", bg="lavender", relief="flat", command=open_signin).pack(pady=2)

# Attach resize event
root.bind("<Configure>", resize_canvas)

root.mainloop()
