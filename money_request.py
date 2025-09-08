import tkinter as tk
from tkinter import Canvas
import mysql.connector
import sys

# Global variable for logged-in account number
LOGGED_IN_ACCOUNT = None

# Database connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root@123",
        database="bankdb"
    )

# Fetch logged-in account number based on username
def fetch_logged_in_account_from_dashboard(logged_in_username):
    global LOGGED_IN_ACCOUNT
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Fetch the account number based on the logged-in username
        cursor.execute("SELECT account_number FROM users WHERE username = %s", (logged_in_username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            LOGGED_IN_ACCOUNT = result[0]  # Store the logged-in account number globally
            print(f"Logged-in Account: {LOGGED_IN_ACCOUNT}")  # Debugging
        else:
            error_label.config(text="No logged-in account found! Please log in first.", fg="red")

    except mysql.connector.Error as e:
        error_label.config(text=f"Database Error: {e}", fg="red")

def draw_gradient(canvas, width, height):
    canvas.delete("gradient")  # Clear previous gradient
    for i in range(height):
        color = f'#{int(75 + (i / height) * 100):02x}{int(0 + (i / height) * 50):02x}{int(130 + (i / height) * 100):02x}'
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")

# Request money function
def request_money():
    if not LOGGED_IN_ACCOUNT:
        error_label.config(text="No logged-in account found!", fg="red")
        return

    receiver = receiver_entry.get().strip()
    amount = amount_entry.get().strip()
    category = category_entry.get().strip() if category_entry.get().strip() else None
    notes = notes_entry.get().strip() if notes_entry.get().strip() else None

    if not receiver or not amount:
        error_label.config(text="Receiver and Amount are required!", fg="red")
        return

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except ValueError:
        error_label.config(text="Enter a valid amount!", fg="red")
        return

    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """INSERT INTO money_requests_v2 
                   (request_sender, request_receiver, amount, category, notes, status, request_date) 
                   VALUES (%s, %s, %s, %s, %s, 'Pending', NOW())"""
        values = (LOGGED_IN_ACCOUNT, receiver, amount, category, notes)

        cursor.execute(query, values)
        conn.commit()
        success_label.config(text="Money request sent successfully!", fg="green")

    except mysql.connector.Error as e:
        error_label.config(text=f"Failed to insert: {e}", fg="red")

    finally:
        conn.close()

    receiver_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    notes_entry.delete(0, tk.END)

# UI for Request Money Window with gradient background
def request_money_ui(logged_in_username):
    global receiver_entry, amount_entry, category_entry, notes_entry, error_label, success_label

    # Fetch the logged-in account number based on the username passed from command-line arguments
    fetch_logged_in_account_from_dashboard(logged_in_username)

    if not LOGGED_IN_ACCOUNT:
        error_label.config(text="No logged-in account found!", fg="red")
        return

    root = tk.Tk()
    root.title("Request Money")
    root.geometry("400x500")
    root.state("zoomed")

    # Create a Canvas for the Gradient Background
    canvas = Canvas(root, width=400, height=500)
    canvas.pack(fill="both", expand=True)

    # Draw the purple gradient
    draw_gradient(canvas, 1920, 1080)

    # Transparent-like Frame for input fields
    frame = tk.Frame(root, bg="lavender", bd=3, relief="ridge")
    frame.place(relx=0.5, rely=0.5, anchor="center", width=320, height=450)

    # Labels & Input Fields
    tk.Label(frame, text="Receiver Account:", font=("Arial", 12, "bold"), bg="lavender").pack(pady=5)
    receiver_entry = tk.Entry(frame, font=("Arial", 12))
    receiver_entry.pack(pady=5, ipadx=5, ipady=3)

    tk.Label(frame, text="Amount:", font=("Arial", 12, "bold"), bg="lavender").pack(pady=5)
    amount_entry = tk.Entry(frame, font=("Arial", 12))
    amount_entry.pack(pady=5, ipadx=5, ipady=3)

    tk.Label(frame, text="Category (Optional):", font=("Arial", 12, "bold"), bg="lavender").pack(pady=5)
    category_entry = tk.Entry(frame, font=("Arial", 12))
    category_entry.pack(pady=5, ipadx=5, ipady=3)

    tk.Label(frame, text="Notes (Optional):", font=("Arial", 12, "bold"), bg="lavender").pack(pady=5)
    notes_entry = tk.Entry(frame, font=("Arial", 12))
    notes_entry.pack(pady=5, ipadx=5, ipady=3)

    # Error and Success Labels
    error_label = tk.Label(frame, text="", font=("Arial", 10, "italic"), bg="lavender", fg="red")
    error_label.pack(pady=5)

    success_label = tk.Label(frame, text="", font=("Arial", 10, "italic"), bg="lavender", fg="green")
    success_label.pack(pady=5)

    # Request Money Button
    tk.Button(frame, text="Request Money", font=("Arial", 12, "bold"), bg="#5A2EA3", fg="white",
              relief="raised", padx=10, pady=5, command=request_money).pack(pady=15)

    root.mainloop()

# Simulate fetching logged-in username from command-line arguments
if len(sys.argv) > 1:
    logged_in_username = sys.argv[1].strip()
else:
    logged_in_username = None

# Ensure the logged-in username is not None and proceed
if logged_in_username:
    request_money_ui(logged_in_username)
else:
    error_label.config(text="No logged-in username found!", fg="red")

