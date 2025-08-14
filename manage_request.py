import tkinter as tk
from tkinter import ttk
import mysql.connector
import sys
from tkinter import Canvas
# Get logged-in username from command-line arguments
if len(sys.argv) > 1:
    logged_in_username = sys.argv[1].strip()
else:
    print("Error: No user logged in!")
    sys.exit()

# Database connection function
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="Vrushali",
        password="Vrushali@1220",
        database="bankdb"
    )

# Fetch the account number of the logged-in user
def get_logged_in_account():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT account_number FROM users WHERE username = %s", (logged_in_username,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except mysql.connector.Error as e:
        print(f"Database Error: Failed to fetch account number: {e}")
        sys.exit()

LOGGED_IN_ACCOUNT = get_logged_in_account()

# Fetch received money requests (updated query to reflect new table schema)
def fetch_received_requests():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """SELECT request_sender, amount, category, notes, status, request_date FROM money_requests_v2 WHERE request_receiver = %s"""
        cursor.execute(query, (LOGGED_IN_ACCOUNT,))
        requests = cursor.fetchall()
        conn.close()
        return requests
    except mysql.connector.Error as e:
        print(f"Database Error: Failed to fetch requests: {e}")
        return []

# Fetch sent money requests (updated query to reflect new table schema)
def fetch_sent_requests():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """SELECT request_receiver, amount, category, notes, status, request_date FROM money_requests_v2 WHERE request_sender = %s"""
        cursor.execute(query, (LOGGED_IN_ACCOUNT,))
        requests = cursor.fetchall()
        conn.close()
        return requests
    except mysql.connector.Error as e:
        print(f"Database Error: Failed to fetch requests: {e}")
        return []

# Function to update request status (Accept & Pay / Decline) (updated query)
def update_request_status(sender_account, amount, new_status):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = """UPDATE money_requests_v2 SET status = %s WHERE request_receiver = %s AND request_sender = %s AND amount = %s AND status = 'Pending'"""
        cursor.execute(query, (new_status, LOGGED_IN_ACCOUNT, sender_account, amount))
        conn.commit()
        conn.close()
        # Update the label to show payment info instead of a messagebox
        payment_label.config(text=f"Request {new_status}. You will pay ₹{amount} to {sender_account}.")
        refresh_requests()
    except mysql.connector.Error as e:
        print(f"Database Error: Failed to update status: {e}")

# Function to refresh request lists
def refresh_requests():
    for item in received_tree.get_children():
        received_tree.delete(item)
    for item in sent_tree.get_children():
        sent_tree.delete(item)

    for row in fetch_received_requests():
        received_tree.insert("", "end", values=row)
    for row in fetch_sent_requests():
        sent_tree.insert("", "end", values=row)

# Function to handle the selected request for Accept/Decline
def handle_selected_request():
    selected_item = received_tree.selection()
    if selected_item:
        item_values = received_tree.item(selected_item[0])['values']
        sender_account = item_values[0]
        amount = item_values[1]
        status = item_values[4]

        if status == 'Pending':
            # Enable Accept/Decline buttons for Pending requests
            accept_button.config(state="normal", command=lambda: update_request_status(sender_account, amount, "Accepted"))
            decline_button.config(state="normal", command=lambda: update_request_status(sender_account, amount, "Declined"))
        elif status == 'Accepted':
            # Disable both buttons if request is already accepted
            accept_button.config(state="disabled")
            decline_button.config(state="disabled")
        elif status == 'Declined':
            # Disable both buttons if request is already declined
            accept_button.config(state="disabled")
            decline_button.config(state="disabled")
        else:
            print("Invalid request status.")
    else:
        print("Please select a request.")


# GUI Setup
root = tk.Tk()
root.title("Manage Money Requests")
root.attributes('-fullscreen', True)
root.configure(bg="lavender")

# Header
header = tk.Label(root, text="Manage Requests", font=("Arial", 16, "bold"),fg="purple",bg="lavender")
header.pack(pady=10)

# Received Requests Section
received_label = tk.Label(root, text="Received Requests", font=("Arial", 12, "bold"),fg="purple",bg="Lavender")
received_label.pack()
received_frame = tk.Frame(root)
received_frame = tk.Frame(root, bg="Lavender")
received_frame.pack(fill="both", expand=True, padx=10)
received_tree = ttk.Treeview(received_frame, columns=("Sender", "Amount", "Category", "Notes", "Status", "Date"),
                             show="headings")
for col in received_tree['columns']:
    received_tree.heading(col, text=col)
    received_tree.column(col, width=100)
received_tree.pack(side="left", fill="both", expand=True)
scroll_received = ttk.Scrollbar(received_frame, orient="vertical", command=received_tree.yview)
received_tree.configure(yscroll=scroll_received.set)
scroll_received.pack(side="right", fill="y")

# Sent Requests Section
sent_label = tk.Label(root, text="Sent Requests", font=("Arial", 12, "bold"),fg="purple",bg="lavender")
sent_label.pack()
sent_frame = tk.Frame(root)
received_frame = tk.Frame(root, bg="Lavender")
sent_frame.pack(fill="both", expand=True, padx=10)
sent_tree = ttk.Treeview(sent_frame, columns=("Receiver", "Amount", "Category", "Notes", "Status", "Date"),
                         show="headings")
for col in sent_tree['columns']:
    sent_tree.heading(col, text=col)
    sent_tree.column(col, width=100)
sent_tree.pack(side="left", fill="both", expand=True)
scroll_sent = ttk.Scrollbar(sent_frame, orient="vertical", command=sent_tree.yview)
sent_tree.configure(yscroll=scroll_sent.set)
scroll_sent.pack(side="right", fill="y")

# Accept and Decline Buttons (initially disabled)
button_frame = tk.Frame(root)
button_frame=tk.Frame(root,bg="lavender")
button_frame.pack(pady=10)

accept_button = tk.Button(button_frame, text="Accept", font=("Arial", 12),fg="purple",bg="lavender", state="disabled")
accept_button.grid(row=0, column=0, padx=10)

decline_button = tk.Button(button_frame, text="Decline", font=("Arial", 12),fg="purple",bg="lavender", state="disabled")
decline_button.grid(row=0, column=1, padx=10)

# Label to show payment information instead of message box
payment_label = tk.Label(root, text="", font=("Arial", 12), fg="purple",bg="lavender")
payment_label.pack(pady=10)

# Load Data and Add functionality
refresh_requests()

# Button to handle selected request
handle_button = tk.Button(root, text="Handle Selected Request", font=("Arial", 12),fg="purple",bg="lavender", command=handle_selected_request)
handle_button.pack(pady=10)

# Exit Button
exit_btn = tk.Button(root, text="Exit", font=("Arial", 12), bg="red", fg="white", command=root.destroy)
exit_btn.pack(pady=10)

root.mainloop()
