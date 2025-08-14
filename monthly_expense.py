import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import sys

# Get logged-in username from command-line arguments
if len(sys.argv) > 1:
    logged_in_username = sys.argv[1].strip()
else:
    logged_in_username = None

# Connect to MySQL and fetch the correct account number
def get_account_number():
    try:
        conn = mysql.connector.connect(host="localhost", user="Vrushali", password="Vrushali@1220", database="bankdb")
        cursor = conn.cursor()
        cursor.execute("SELECT account_number FROM users WHERE username = %s", (logged_in_username,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return str(result[0])  # Convert to string to avoid integer mismatch
        else:
            messagebox.showerror("Error", "Account number not found for the logged-in user!")
            return None

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Error fetching account number: {e}")
        return None

# Fetch Monthly Expenses with Receiver's Account
def fetch_monthly_expenses():
    account_number = get_account_number()
    if not account_number:
        return

    selected_month = month_var.get()
    if not selected_month:
        messagebox.showerror("Error", "Please select a month!")
        return

    month_mapping = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }
    selected_month_number = month_mapping[selected_month]

    try:
        conn = mysql.connector.connect(
            host="localhost", user="Vrushali", password="Vrushali@1220", database="bankdb"
        )
        cursor = conn.cursor()

        query = """
        SELECT e.expense_date, u.account_holder_name, e.category, e.amount 
        FROM expenses e
        JOIN transactions t ON e.transaction_id = t.id
        JOIN users u ON t.receiver_account = u.account_number  -- Fetch recipient name
        WHERE e.account_number = %s AND MONTH(e.expense_date) = %s
        ORDER BY e.expense_date ASC;
        """
        cursor.execute(query, (account_number, selected_month_number))
        expenses = cursor.fetchall()

        expense_list.delete(*expense_list.get_children())

        if expenses:
            for expense in expenses:
                expense_list.insert("", "end", values=expense)
        else:
            messagebox.showinfo("Info", "No expenses found for the selected month.")

    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

# Function to create a gradient background
def draw_gradient(canvas, width, height):
    canvas.delete("gradient")  # Clear previous gradient
    for i in range(height):
        color = f'#{int(75 + (i / height) * 100):02x}{int(0 + (i / height) * 50):02x}{int(130 + (i / height) * 100):02x}'
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")

# Function to center UI elements dynamically
def center_elements():
    root.update_idletasks()  # Ensure updated window size
    width = root.winfo_width()
    height = root.winfo_height()
    center_x = width // 2
    center_y = height // 2

    canvas.config(width=width, height=height)  # Resize canvas
    draw_gradient(canvas, width, height)  # Redraw gradient

    # Position elements dynamically
    canvas.coords(header_window, center_x, 60)
    canvas.coords(filters_window, center_x, 120)
    canvas.coords(expense_table_window, center_x, center_y - 50)
    canvas.coords(refresh_window, center_x, center_y + 180)

# GUI Window
root = tk.Tk()
root.title("Monthly Expenses")
root.geometry("1280x720")  # Default size (Fullscreen adjusts automatically)
root.state("zoomed")

# Create Canvas for Gradient Background
canvas = tk.Canvas(root, width=1920, height=1080)
canvas.pack(fill="both", expand=True)

# Apply Initial Gradient
draw_gradient(canvas, 1920, 1080)

# Header Label
header_label = tk.Label(root, text="📅 Monthly Expenses", font=("Arial", 18, "bold"), fg="purple", bg="lavender")
header_window = canvas.create_window(640, 50, window=header_label)

# Filters Frame
filters_frame = tk.Frame(root, bg="lavender")
filters_window = canvas.create_window(640, 120, window=filters_frame)

# Month Selector
tk.Label(filters_frame, text="Select Month:", fg="purple", bg="lavender", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5)
month_var = tk.StringVar()
month_dropdown = ttk.Combobox(filters_frame, textvariable=month_var, state="readonly")
month_dropdown['values'] = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
month_dropdown.grid(row=0, column=1, padx=5)

# Fetch Button
fetch_button = tk.Button(filters_frame, text="🔍 Show Expenses", bg="lavender", fg="purple", font=("Arial", 10, "bold"), command=fetch_monthly_expenses)
fetch_button.grid(row=0, column=2, padx=5)

# Expense List Table
columns = ("Date", "Recipient Name", "Category", "Amount")
expense_list = ttk.Treeview(root, columns=columns, show="headings")

for col in columns:
    expense_list.heading(col, text=col)
    expense_list.column(col, width=180)

# Scrollbars for Table
scroll_x = ttk.Scrollbar(root, orient="horizontal", command=expense_list.xview)
scroll_y = ttk.Scrollbar(root, orient="vertical", command=expense_list.yview)
expense_list.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

expense_table_window = canvas.create_window(640, 400, window=expense_list, width=700, height=250)

# Refresh Button
refresh_button = tk.Button(root, text="🔄 Refresh", font=("Arial", 12, "bold"), bg="lavender", fg="Purple", command=fetch_monthly_expenses)
refresh_window = canvas.create_window(640, 650, window=refresh_button)

# Make Window Resizable & Center Elements on Resize
root.resizable(True, True)
root.bind("<Configure>", lambda event: center_elements())

# Initial Centering
root.after(100, center_elements)

root.mainloop()
