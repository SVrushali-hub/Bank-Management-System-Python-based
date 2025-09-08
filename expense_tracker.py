import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import sys
sys.path.append(r"C:\Users\Pranali\PycharmProjects\bank_management\.venv\Lib\site-packages")
from tkcalendar import DateEntry

# Get logged-in username from command-line argument (passed by dashboard)
if len(sys.argv) > 1:
    logged_in_username = sys.argv[1].strip()
else:
    logged_in_username = None

# GUI Window
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("900x600")  # Increased size for zoomed effect
root.state("zoomed")
root.configure(bg="#5B2C6F")  # Purple gradient background (solid color)

if not logged_in_username:
    messagebox.showerror("Error", "No logged-in user!")
    root.destroy()
    sys.exit()

# Connect to MySQL
def connect_db():
    return mysql.connector.connect(host="localhost", user="root", password="root@123", database="bankdb")

# Function to fetch the logged-in user's account number
def get_logged_in_account():
    if not logged_in_username:
        return None

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT account_number FROM users WHERE username = %s", (logged_in_username,))
    user_data = cursor.fetchone()
    conn.close()

    return user_data[0] if user_data else None

# Store logged-in user's account number
logged_in_account = get_logged_in_account()

if not logged_in_account:
    messagebox.showerror("Error", f"No account found for user '{logged_in_username}'")
    root.destroy()
    sys.exit()

# Fetch and display expenses with optional filtering
def fetch_expenses():
    if not logged_in_account:
        return

    # Get filter values
    selected_date = date_filter.get_date().strftime("%Y-%m-%d") if date_var.get() else None
    selected_category = category_filter.get()

    # SQL query to fetch transactions where the logged-in user is the sender
    query = """
    SELECT t.transaction_date, 
           COALESCE(u.account_holder_name, 'Unknown') AS recipient_name,
           t.category, 
           t.amount, 
           t.notes
    FROM transactions t
    LEFT JOIN users u ON t.receiver_account = u.account_number
    WHERE t.sender_account = %s
    """
    params = [logged_in_account]

    # Apply filters
    if selected_category and selected_category != "All":
        query += " AND t.category = %s"
        params.append(selected_category)

    if selected_date:
        query += " AND DATE(t.transaction_date) = %s"
        params.append(selected_date)

    # Fetch expense data from the database
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    # Clear existing rows in Treeview
    for row in expense_table.get_children():
        expense_table.delete(row)

    # Insert fetched data into Treeview
    for row in rows:
        expense_table.insert("", "end", values=row)

# Header Label
header_label = tk.Label(root, text="Expense Tracker", font=("Arial", 18, "bold"), fg="white", bg="#5B2C6F")
header_label.pack(pady=15)

# Filters Frame
filters_frame = tk.Frame(root, bg="#5B2C6F")
filters_frame.pack(pady=10)

# Date Filter
tk.Label(filters_frame, text="Select Date:", fg="white", bg="#5B2C6F", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5)
date_var = tk.BooleanVar()  # Checkbox to enable/disable date filter
date_filter = DateEntry(filters_frame, width=12, background="blue", foreground="white", borderwidth=2)
date_filter.grid(row=0, column=1, padx=5)
date_check = tk.Checkbutton(filters_frame, variable=date_var, bg="#5B2C6F")  # Checkbox to toggle date filter
date_check.grid(row=0, column=2, padx=5)

# Category Filter
tk.Label(filters_frame, text="Category:", fg="white", bg="#5B2C6F", font=("Arial", 12, "bold")).grid(row=0, column=3, padx=5)
category_filter = ttk.Combobox(filters_frame, values=["All", "Food", "Transport", "Shopping", "Bills", "Other"], state="readonly")
category_filter.grid(row=0, column=4, padx=5)
category_filter.set("All")

# Fetch Button
fetch_button = tk.Button(filters_frame, text="Filter", bg="#6A1B9A", fg="white", font=("Arial", 10, "bold"), command=fetch_expenses)
fetch_button.grid(row=0, column=5, padx=5)

# Expense Table (Now shows "Recipient Name" instead of "Receiver's Account")
columns = ("Date", "Recipient Name", "Category", "Amount", "Notes")
expense_table = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    expense_table.heading(col, text=col)
    expense_table.column(col, width=150)

# Scrollbars for Table
scroll_x = ttk.Scrollbar(root, orient="horizontal", command=expense_table.xview)
scroll_y = ttk.Scrollbar(root, orient="vertical", command=expense_table.yview)
expense_table.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

scroll_x.pack(side="bottom", fill="x")
scroll_y.pack(side="right", fill="y")
expense_table.pack(pady=20, fill="both", expand=True)

# Refresh Button
refresh_button = tk.Button(root, text="🔄 Refresh", font=("Arial", 12, "bold"), bg="#4A148C", fg="white", command=fetch_expenses)
refresh_button.pack(pady=10)

# Make Window Resizable
root.resizable(True, True)

# Fetch and Display Expenses initially
fetch_expenses()

root.mainloop()

