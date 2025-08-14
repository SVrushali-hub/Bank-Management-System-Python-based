import tkinter as tk
from tkinter import Canvas, ttk
import mysql.connector
from decimal import Decimal
import hashlib
from datetime import datetime  # Import datetime

# MySQL Connection
conn = mysql.connector.connect(
    host="localhost",
    user="Vrushali",
    password="Vrushali@1220",
    database="bankdb"
)
cursor = conn.cursor()

# Create necessary tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS loans (
                    loan_id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_name VARCHAR(100),
                    account_number VARCHAR(20),
                    loan_amount DECIMAL(10,2),
                    loan_duration INT,
                    loan_status VARCHAR(50),
                    application_date DATE)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS loan_repayments (
                    repayment_id INT AUTO_INCREMENT PRIMARY KEY,
                    loan_id INT,
                    amount_paid DECIMAL(10,2),
                    remaining_balance DECIMAL(10,2),
                    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

conn.commit()

# Function to create a full-screen gradient background
def draw_gradient(canvas, width, height):
    canvas.delete("gradient")  # Clear previous gradient
    for i in range(height):
        color = f'#{int(75 + (i / height) * 100):02x}{int(0 + (i / height) * 50):02x}{int(130 + (i / height) * 100):02x}'
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")

# Function to update gradient when window resizes
def on_resize(event):
    draw_gradient(canvas, event.width, event.height)

# Function to create a new window with a consistent theme
def create_window(title, content_func):
    window = tk.Toplevel(root)
    window.title(title)
    window.configure(bg="#D8BFD8")
    window.geometry("800x600")  # Set a larger size for the window
    window.state("zoomed")  # Set child window to zoomed mode

    frame = tk.Frame(window, bg="#D8BFD8")
    frame.pack(padx=20, pady=20)

    content_func(frame)  # Call the content function to populate the frame

    return window

# ========== Loan Management Functions ==========

def open_check_credit_loan(frame):
    tk.Label(frame, text="Enter Loan ID:", bg="#D8BFD8", fg="#333333", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=5)
    loan_id_entry = tk.Entry(frame)
    loan_id_entry.grid(row=0, column=1, padx=10, pady=5)

    result_label = tk.Label(frame, text="", bg="#D8BFD8", fg="#333333", font=("Arial", 12))
    result_label.grid(row=2, columnspan=2, pady=10)

    def credit_loan():
        loan_id = loan_id_entry.get()
        if not loan_id:
            result_label.config(text="Loan ID is required.", fg="red")
            return

        cursor.execute("SELECT account_number, loan_amount, loan_status FROM loans WHERE loan_id = %s", (loan_id,))
        loan = cursor.fetchone()

        if not loan:
            result_label.config(text="Loan ID not found.", fg="red")
            return

        account_number, loan_amount, loan_status = loan

        if loan_status.lower() == "approved & credited":
            result_label.config(text="Loan has already been credited.", fg="red")
            return

        if loan_status.lower() != "approved":
            result_label.config(text="Loan is not approved yet.", fg="red")
            return

        # Credit the loan amount to user's balance
        cursor.execute("UPDATE users SET balance = balance + %s WHERE account_number = %s", (loan_amount, account_number))

        # Update loan status to 'credited'
        cursor.execute("UPDATE loans SET loan_status = %s WHERE loan_id = %s", ('Approved & Credited', loan_id))

        conn.commit()
        result_label.config(text="Loan amount credited to account.", fg="green")

    tk.Button(frame, text="Check & Credit Loan", command=credit_loan, bg="#4CAF50", fg="white", font=("Arial", 12, "bold")).grid(row=1, columnspan=2, pady=10)

def open_loan_application(frame):
    tk.Label(frame, text="Customer Name:", bg="#D8BFD8", fg="#333333", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=5)
    customer_entry = tk.Entry(frame)
    customer_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(frame, text="Account Number:", bg="#D8BFD8", fg="#333333", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=5)
    account_entry = tk.Entry(frame)
    account_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(frame, text="Loan Amount:", bg="#D8BFD8", fg="#333333", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=5)
    amount_entry = tk.Entry(frame)
    amount_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(frame, text="Duration (Months):", bg="#D8BFD8", fg="#333333", font=("Arial", 14)).grid(row=3, column=0, padx=10, pady=5)
    duration_entry = tk.Entry(frame)
    duration_entry.grid(row=3, column=1, padx=10, pady=5)

    # Labels to show loan details after submission
    loan_details_label = tk.Label(frame, text="", bg="#D8BFD8", fg="#333333", font=("Arial", 12))
    loan_details_label.grid(row=6, columnspan=2, pady=10)

    def submit_loan():
        customer_name = customer_entry.get()
        account_number = account_entry.get()
        loan_amount = amount_entry.get()
        loan_duration = duration_entry.get()

        if not account_number or not loan_amount or not loan_duration or not customer_name:
            loan_details_label.config(text="All fields are required.", fg="red")
            return

        try:
            loan_amount = float(loan_amount)
            loan_duration = int(loan_duration)
        except ValueError:
            loan_details_label.config(text="Invalid amount or duration.", fg="red")
            return

        application_date = datetime.now().date()  # Get the current date

        cursor.execute("INSERT INTO loans (customer_name, account_number, loan_amount, loan_duration, loan_status, application_date) VALUES (%s, %s, %s, %s, %s, %s)",
                       (customer_name, account_number, loan_amount, loan_duration, 'Pending', application_date))
        conn.commit()

        # Show loan details below the form
        loan_details_label.config(text=f"Loan Application Submitted:\n\n"
                                       f"Customer Name: {customer_name}\n\n"
                                       f"Account Number: {account_number}\n\n"
                                       f"Loan Amount: ₹{loan_amount:.2f}\n\n"
                                       f"Duration: {loan_duration} months\n\n"
                                       f"Application Date: {application_date}", fg="#FF5733")

    tk.Button(frame, text="Apply for Loan", command=submit_loan, bg="#FF5733", fg="white", font=("Arial", 12, "bold")).grid(row=5, columnspan=2, pady=10)

def open_loan_payment_history(frame):
    tk.Label(frame, text="Enter Loan ID:", bg="#D8BFD8", fg="#333333", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=5)
    loan_id_entry = tk.Entry(frame)
    loan_id_entry.grid(row=0, column=1, padx=10, pady=5)

    # Label to show loan history
    history_label = tk.Label(frame, text="", bg="#D8BFD8", fg="#333333", font=("Arial", 12))
    history_label.grid(row=2, columnspan=2, pady=10)

    # Treeview for displaying loan repayment history
    columns = ("Repayment ID", "Amount Paid", "Payment Date", "Remaining Balance")
    history_tree = ttk.Treeview(frame, columns=columns, show='headings')
    history_tree.grid(row=3, columnspan=2, pady=10)

    for col in columns:
        history_tree.heading(col, text=col)

    def show_payment_history():
        loan_id = loan_id_entry.get()
        if not loan_id:
            history_label.config(text="Loan ID is required.", fg="red")
            return

        # Fetch loan amount (credited) from loans table
        cursor.execute("SELECT loan_amount FROM loans WHERE loan_id = %s", (loan_id,))
        loan = cursor.fetchone()

        if not loan:
            history_label.config(text="Loan ID not found.", fg="red")
            return

        loan_amount = loan[0]

        # Clear previous entries in the treeview
        for row in history_tree.get_children():
            history_tree.delete(row)

        # Fetch loan repayment records
        cursor.execute("SELECT repayment_id, amount_paid, payment_date, remaining_balance FROM loan_repayments WHERE loan_id = %s",
                       (loan_id,))
        repayments = cursor.fetchall()

        # Insert repayment records into the treeview
        if repayments:
            for repayment in repayments:
                history_tree.insert("", "end", values=repayment)
        else:
            history_label.config(text="No repayments yet.", fg="blue")

    tk.Button(frame, text="Show Payment History", command=show_payment_history, bg="#FFC300", fg="white", font=("Arial", 12, "bold")).grid(row=1, columnspan=2, pady=10)

def calculate_interest(frame):
    tk.Label(frame, text="Enter Loan ID:", bg="#D8BFD8", fg="#333333", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=5)
    interest_loan_id_entry = tk.Entry(frame)
    interest_loan_id_entry.grid(row=0, column=1, padx=10, pady=5)

    # Label to show interest calculation results
    interest_label = tk.Label(frame, text="", bg="#D8BFD8", fg="#333333", font=("Arial", 12))
    interest_label.grid(row=3, columnspan=2, pady=10)

    def calculate():
        loan_id = interest_loan_id_entry.get()

        if not loan_id:
            interest_label.config(text="Please enter a Loan ID.", fg="red")
            return

        try:
            cursor.execute("SELECT loan_amount, loan_duration, interest_rate FROM loans WHERE loan_id = %s", (loan_id,))
            result = cursor.fetchone()

            if result is None:
                interest_label.config(text="Loan ID not found.", fg="red")
                return  # Exit function if no loan is found

            loan_amount, duration, interest_rate = result

            # Ensure values are valid numbers
            loan_amount = float(loan_amount)
            duration = int(duration)
            interest_rate = float(interest_rate)

            total_repayment = loan_amount + (loan_amount * (interest_rate / 100) * (duration / 12))

            interest_label.config(text=f"Loan Amount: ₹{loan_amount:.2f}\n\nDuration: {duration} months\n\nInterest Rate: {interest_rate}% per year\n\nTotal Repayment: ₹{total_repayment:.2f}", fg="#FF5733")
        except Exception as e:
            interest_label.config(text=f"An error occurred: {str(e)}", fg="red")

    tk.Button(frame, text="Calculate Interest", command=calculate, bg="#FF33A1", fg="white").grid(row=2, columnspan=2, pady=10)

def open_loan_repayment(frame):
    tk.Label(frame, text="Loan ID:", bg="#D8BFD8", fg="#333333", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=5)
    loan_id_entry = tk.Entry(frame)
    loan_id_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(frame, text="Repayment Amount:", bg="#D8BFD8", fg="#333333", font=("Arial", 14)).grid(row=1, column=0, padx=10, pady=5)
    amount_entry = tk.Entry(frame)
    amount_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(frame, text="Enter TPIN:", bg="#D8BFD8", fg="#333333", font=("Arial", 14)).grid(row=2, column=0, padx=10, pady=5)
    tpin_entry = tk.Entry(frame, show='*')
    tpin_entry.grid(row=2, column=1, padx=10, pady=5)

    result_label = tk.Label(frame, text="", bg="#D8BFD8", fg="#333333", font=("Arial", 12))
    result_label.grid(row=5, columnspan=2, pady=10)

    def validate_tpin():
        loan_id = loan_id_entry.get()
        amount_paid = amount_entry.get()
        tpin = tpin_entry.get()

        if not loan_id or not amount_paid or not tpin:
            result_label.config(text="All fields are required.", fg="red")
            return

        try:
            amount_paid = Decimal(amount_paid)
        except:
            result_label.config(text="Invalid amount.", fg="red")
            return

        # Verify TPIN
        cursor.execute("SELECT account_number FROM loans WHERE loan_id = %s", (loan_id,))
        loan = cursor.fetchone()

        if not loan:
            result_label.config(text="Loan ID not found.", fg="red")
            return

        account_number = loan[0]  # Extract the account number

        # Now, fetch the hashed TPIN for the corresponding account number
        cursor.execute("SELECT tpin FROM users WHERE account_number = %s", (account_number,))
        user = cursor.fetchone()

        if not user:
            result_label.config(text="Account not found.", fg="red")
            return

        stored_hashed_tpin = user[0]  # The stored hashed TPIN
        hashed_entered_tpin = hashlib.sha256(tpin.encode()).hexdigest()

        # Compare the hashed entered TPIN with the stored hashed TPIN
        if hashed_entered_tpin != stored_hashed_tpin:
            result_label.config(text="Invalid TPIN.", fg="red")
            return

        # If TPIN is valid, proceed with repayment
        cursor.execute("SELECT loan_amount FROM loans WHERE loan_id = %s", (loan_id,))
        loan = cursor.fetchone()

        if not loan:
            result_label.config(text="Loan ID not found.", fg="red")
            return

        loan_amount = loan[0]

        cursor.execute("SELECT SUM(amount_paid) FROM loan_repayments WHERE loan_id = %s", (loan_id,))
        total_repaid = cursor.fetchone()[0] or 0  # If no repayments, default to 0

        remaining_balance = loan_amount - total_repaid - amount_paid

        # Insert repayment into the loan_repayments table with the remaining balance
        cursor.execute("INSERT INTO loan_repayments (loan_id, amount_paid, remaining_balance) VALUES (%s, %s, %s)",
                       (loan_id, amount_paid, remaining_balance))
        conn.commit()

        result_label.config(text=f"Repayment of ₹{amount_paid:.2f} successful! Remaining loan balance: ₹{remaining_balance:.2f}", fg="green")

    tk.Button(frame, text="Make Repayment", command=validate_tpin, bg="#4CAF50", fg="white").grid(row=4, columnspan=2, pady=10)

def open_loan_history(frame):
    tk.Label(frame, text="Enter Account Number:", bg="#D8BFD8", fg="#333333", font=("Arial", 14)).grid(row=0, column=0, padx=10, pady=5)
    account_number_entry = tk.Entry(frame)
    account_number_entry.grid(row=0, column=1, padx=10, pady=5)

    # Label to show loan history
    history_label = tk.Label(frame, text="", bg="#D8BFD8", fg="#333333", font=("Arial", 12))
    history_label.grid(row=2, columnspan=2, pady=10)

    # Treeview for displaying loan history
    columns = ("Loan ID", "Customer Name", "Account Number", "Loan Amount", "Duration (Months)", "Status", "Application Date")
    history_tree = ttk.Treeview(frame, columns=columns, show='headings')
    history_tree.grid(row=3, columnspan=2, pady=10)

    for col in columns:
        history_tree.heading(col, text=col)

    def show_loan_history():
        account_number = account_number_entry.get()
        if not account_number:
            history_label.config(text="Account Number is required.", fg="red")
            return

        # Clear previous entries in the treeview
        for row in history_tree.get_children():
            history_tree.delete(row)

        # Fetch loan details
        cursor.execute("SELECT loan_id, customer_name, account_number, loan_amount, loan_duration, loan_status, application_date FROM loans WHERE account_number = %s", (account_number,))
        loans = cursor.fetchall()

        if not loans:
            history_label.config(text="No loans found for this account number.", fg="red")
            return

        # Insert loan details into the treeview
        for loan in loans:
            history_tree.insert("", "end", values=loan)

    tk.Button(frame, text="Show Loan History", command=show_loan_history, bg="#FFC300", fg="white", font=("Arial", 12, "bold")).grid(row=1, columnspan=2, pady=10)

# Main menu window
root = tk.Tk()
root.title("Loan Management System")
root.geometry("1280x720")
root.state("zoomed")  # Full-screen mode
root.resizable(True, True)

# Create a Canvas for the Gradient Background
canvas = Canvas(root)
canvas.pack(fill="both", expand=True)

# Draw the gradient
draw_gradient(canvas, 1920, 1080)

# Main Container (Updated Lavender Background)
container = tk.Frame(root, bg="#D8BFD8", bd=5, relief="ridge")
container.place(relx=0.5, rely=0.5, anchor="center", width=900, height=650)

# Welcome Label
tk.Label(container, text="Loan Management System", font=("Arial", 24, "bold"), bg="#D8BFD8").pack(pady=15)

# Function to create buttons with styling
def create_button(text, command, color):
    btn = tk.Button(container, text=text, font=("Arial", 14, "bold"), bg=color, fg="white", padx=20, pady=10, relief="raised", borderwidth=3, width=30, command=command)
    btn.pack(pady=10)
    return btn

# Dashboard Buttons with different colors
create_button("📄 Apply for Loan", lambda: create_window("Loan Application", open_loan_application), "#FF5733")  # Red
create_button("✅ Check & Credit Approved Loan", lambda: create_window("Check & Credit Loan", open_check_credit_loan), "#33FF57")  # Green
create_button("📊 Loan Payment History", lambda: create_window("Loan Payment History", open_loan_payment_history), "#3357FF")  # Blue
create_button("💰 Calculate Interest", lambda: create_window("Calculate Interest", calculate_interest), "#FF33A1")  # Pink
create_button("🔄 Loan Repayment", lambda: create_window("Loan Repayment", open_loan_repayment), "#FFC300")  # Yellow
create_button("📜 Loan History", lambda: create_window("Loan History", open_loan_history), "#FF8C00")  # Orange

root.mainloop()