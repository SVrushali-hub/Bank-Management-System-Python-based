import tkinter as tk
import mysql.connector
import hashlib
import sys

# Get the logged-in username from the dashboard
if len(sys.argv) > 1:
    logged_in_username = sys.argv[1].strip()
else:
    logged_in_username = None

# Function to hash a PIN using SHA-256
def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

# Function to connect to MySQL database
def connect_db():
    return mysql.connector.connect(host="localhost", user="root", password="root@123", database="bankdb")

# Function to fetch user's balance
def check_balance():
    entered_pin = pin_entry.get()

    if not logged_in_username:
        balance_label.config(text="User not logged in!", fg="red")
        return

    if not entered_pin.isdigit() or len(entered_pin) != 6:
        balance_label.config(text="Invalid PIN! Enter a 6-digit number.", fg="red")
        return

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT balance, pin FROM users WHERE username = %s", (logged_in_username,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data:
        balance, correct_hashed_pin = user_data
        if hash_pin(entered_pin) == correct_hashed_pin:
            balance_label.config(text=f"Your Current Balance: ₹{balance}", fg="green")
        else:
            balance_label.config(text="Incorrect PIN!", fg="red")
    else:
        balance_label.config(text="User details not found!", fg="red")

def draw_gradient(canvas, width, height):
    canvas.delete("gradient")  # Clear previous gradient
    for i in range(height):
        color = f'#{int(75 + (i / height) * 100):02x}{int(0 + (i / height) * 50):02x}{int(130 + (i / height) * 100):02x}'
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")

# Function to resize canvas when window is resized
def resize_canvas(event):
    canvas.delete("gradient")
    draw_gradient(canvas, event.width, event.height)
    canvas.config(width=event.width, height=event.height)
    frame.place(relx=0.5, rely=0.5, anchor="center")  # Keep frame centered

# GUI for Check Balance
balance_root = tk.Tk()
balance_root.title("Check Balance")
balance_root.geometry("350x250")
balance_root.configure(bg="#f0f0f0")

# Create Canvas for Gradient Background
canvas = tk.Canvas(balance_root)
canvas.pack(fill="both", expand=True)

draw_gradient(canvas, 1920, 1080)

# Main content inside a container frame
frame = tk.Frame(balance_root, bg="lavender", bd=5, relief="ridge")
frame.place(relx=0.5, rely=0.5, anchor="center", width=300, height=200)

# Content inside the frame
tk.Label(frame, text="Enter Your 6-digit Login PIN:", font=("Arial", 12), bg="lavender").pack(pady=10)
pin_entry = tk.Entry(frame, font=("Arial", 12), show="*")
pin_entry.pack(pady=5)

tk.Button(frame, text="Check Balance", font=("Arial", 12), bg="blue", fg="white", command=check_balance).pack(pady=10)

# Label to display balance message
balance_label = tk.Label(frame, text="", font=("Arial", 12, "bold"), bg="lavender")
balance_label.pack(pady=10)

balance_root.mainloop()

