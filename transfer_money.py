import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import hashlib
import sys

# Global variables for receiver account and amount to be passed into the window
receiver_acc = None
amount = None

# Function to hash a PIN using SHA-256
def hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()

# Function to connect to MySQL database
def connect_db():
    return mysql.connector.connect(host="localhost", user="Vrushali", password="Vrushali@1220", database="bankdb")

# Function to fetch the logged-in user's account details
def get_user_details(logged_in_username):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT account_number, username, tpin FROM users WHERE username = %s", (logged_in_username,))
        result = cursor.fetchone()
        return result if result else (None, None, None)
    except mysql.connector.Error as e:
        print("Database Error:", e)
        return None, None, None
    finally:
        conn.close()

# Function to transfer money
def transfer_money(sender_acc, receiver_acc, amount, tpin, category, notes):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Check if receiver exists
        cursor.execute("SELECT account_number FROM users WHERE account_number = %s", (receiver_acc,))
        if not cursor.fetchone():
            error_label.config(text="Receiver account not found!", fg="red")
            return False

        # Check sender balance & TPIN
        cursor.execute("SELECT balance, tpin FROM users WHERE account_number = %s", (sender_acc,))
        sender_data = cursor.fetchone()
        if not sender_data:
            error_label.config(text="Sender account not found!", fg="red")
            return False

        sender_balance, stored_hashed_tpin = sender_data

        if stored_hashed_tpin.strip() != tpin.strip():
            error_label.config(text="Invalid TPIN!", fg="red")
            return False

        if sender_balance < amount:
            error_label.config(text="Insufficient Balance.", fg="red")
            return False

        # Deduct from sender and add to receiver
        cursor.execute("UPDATE users SET balance = balance - %s WHERE account_number = %s", (amount, sender_acc))
        cursor.execute("UPDATE users SET balance = balance + %s WHERE account_number = %s", (amount, receiver_acc))

        # Insert into transactions
        cursor.execute(
            "INSERT INTO transactions (sender_account, receiver_account, amount, transaction_date, transaction_type, category, notes) "
            "VALUES (%s, %s, %s, NOW(), %s, %s, %s)",
            (sender_acc, receiver_acc, amount, "Transfer", category, notes)
        )
        transaction_id = cursor.lastrowid

        # Record expense for sender (only if sending to another account)
        if sender_acc != receiver_acc:
            cursor.execute(
                "INSERT INTO expenses (account_number, transaction_id, category, amount, expense_date, notes) "
                "VALUES (%s, %s, %s, %s, NOW(), %s)",
                (sender_acc, transaction_id, category, amount, notes)
            )

        conn.commit()
        error_label.config(text="Money Transferred Successfully!", fg="green")
        return True
    except mysql.connector.Error as e:
        conn.rollback()
        error_label.config(text="Database Error: " + str(e), fg="red")
        return False
    finally:
        conn.close()

# Function to initiate transfer
def initiate_transfer():
    # Fetch user details
    sender_acc, _, stored_hashed_tpin = get_user_details(logged_in_username)

    # Get the input values
    receiver_acc = receiver_entry.get().strip()
    amount = amount_entry.get().strip()
    tpin = tpin_entry.get().strip()
    category = category_var.get()
    notes = notes_entry.get().strip()

    # Check for required fields
    if not sender_acc or not receiver_acc or not amount or not tpin or category == "Select Category":
        error_label.config(text="All fields except Notes are required!", fg="red")
        return

    # Check if the sender is not transferring money to themselves
    if sender_acc == receiver_acc:
        error_label.config(text="You cannot transfer money to yourself!", fg="red")
        return

    # Validate the amount (ensure it's a valid number and greater than 0)
    try:
        amount = float(amount)
        if amount <= 0:
            error_label.config(text="Enter a valid amount!", fg="red")
            return
    except ValueError:
        error_label.config(text="Amount must be a number!", fg="red")
        return

    # Hash the TPIN
    hashed_tpin = hash_pin(tpin)

    # Call the function to process the transfer
    success = transfer_money(sender_acc, receiver_acc, amount, hashed_tpin, category, notes)
    if success:
        error_label.config(text="Money transferred successfully!", fg="green")
    else:
        error_label.config(text="Transaction failed! Check details and try again.", fg="red")


# Function to draw a gradient background
def draw_gradient(canvas, width, height):
    for i in range(height):
        color = f'#{int(75 + (i / height) * 80):02x}{int(0 + (i / height) * 100):02x}{int(130 + (i / height) * 100):02x}'
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")

# Function to resize canvas when window is resized
def resize_canvas(event):
    #canvas.delete("gradient")
    draw_gradient(canvas, event.width, event.height)
    canvas.config(width=event.width, height=event.height)
    frame.place(relx=0.5, rely=0.5, anchor="center")  # Keep frame centered

# GUI for Transfer Money
transfer_window = tk.Tk()
transfer_window.title("Transfer Money")
transfer_window.geometry("350x500")
transfer_window.configure(bg="#f0f0f0")

# Get the logged-in username and transfer details (receiver_account, amount) from the command-line arguments
logged_in_username = sys.argv[1].strip() if len(sys.argv) > 1 else None

# Create Canvas for Gradient Background
canvas = tk.Canvas(transfer_window)
canvas.pack(fill="both", expand=True)

draw_gradient(canvas, 1920, 1080)

# Main content inside a container frame
frame = tk.Frame(transfer_window, bg="lavender", bd=5, relief="ridge")
frame.place(relx=0.5, rely=0.5, anchor="center", width=300, height=500)

# Content inside the frame
tk.Label(frame, text="Receiver's Account No:", font=("Arial", 12), bg="lavender").pack(pady=10)
receiver_entry = tk.Entry(frame, font=("Arial", 12))
receiver_entry.insert(0, receiver_acc if receiver_acc else '')
receiver_entry.pack(pady=5)

tk.Label(frame, text="Amount (₹):", font=("Arial", 12), bg="lavender").pack(pady=10)
amount_entry = tk.Entry(frame, font=("Arial", 12))
amount_entry.insert(0, amount if amount else '')
amount_entry.pack(pady=5)

tk.Label(frame, text="Category:", font=("Arial", 12), bg="lavender").pack(pady=10)
categories = ["Food", "Shopping", "Bills", "Entertainment", "Other"]
category_var = tk.StringVar(transfer_window)
category_var.set("Select Category")
category_dropdown = tk.OptionMenu(frame, category_var, *categories)
category_dropdown.pack(pady=5)

tk.Label(frame, text="Notes (Optional):", font=("Arial", 12), bg="lavender").pack(pady=10)
notes_entry = tk.Entry(frame, font=("Arial", 12))
notes_entry.pack(pady=5)

tk.Label(frame, text="Enter Your 6-digit TPIN:", font=("Arial", 12), bg="lavender").pack(pady=10)
tpin_entry = tk.Entry(frame, font=("Arial", 12), show="*")
tpin_entry.pack(pady=5)

# Error Label
error_label = tk.Label(frame, text="", font=("Arial", 10), fg="red", bg="lavender")
error_label.pack(pady=5)

# Buttons
tk.Button(frame, text="Transfer Money", font=("Arial", 12), bg="green", fg="white", command=initiate_transfer).pack(pady=10)
tk.Button(frame, text="🔙 Back", font=("Arial", 12), bg="grey", fg="black", command=transfer_window.destroy).pack(pady=10)

transfer_window.mainloop()
