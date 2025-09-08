import tkinter as tk
from tkinter import ttk
import mysql.connector
import hashlib
import sys
if len(sys.argv) > 1:
    logged_in_username = sys.argv[1].strip()
else:
    logged_in_username = None

def open_check_balance():
    import check_balance


def open_transfer_money():
    import transfer_money


def open_transaction_history_window():
    def verify_tpin():
        entered_tpin = entry_tpin.get().strip()

        if not entered_tpin.isdigit() or len(entered_tpin) != 6:
            error_label.config(text="Invalid TPIN! Please enter a 6-digit number.", fg="red")
            return

        hashed_tpin = hashlib.sha256(entered_tpin.encode()).hexdigest()

        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="root@123",
                                           database="bankdb")
            cursor = conn.cursor()

            # Get account number from username
            cursor.execute("SELECT account_number FROM users WHERE username = %s AND tpin = %s",
                           (logged_in_username, hashed_tpin))
            result = cursor.fetchone()

            if result:
                logged_in_account = result[0]  # Fetch the account number
                error_label.config(text="TPIN Verified!", fg="green")
                display_transaction_history(logged_in_account)
            else:
                error_label.config(text="Incorrect TPIN!", fg="red")

            cursor.close()
            conn.close()
        except Exception as e:
            error_label.config(text=f"Database error: {e}", fg="red")

    def display_transaction_history(sender_account):
        for widget in history_frame.winfo_children():
            widget.destroy()

        tk.Label(history_frame, text="Transaction History", font=("Arial", 14, "bold"), fg="black", bg="lavender").pack(pady=5)

        tree_frame = tk.Frame(history_frame, bg="lavender")
        tree_frame.pack(pady=5, fill="both", expand=True)

        tree_scroll = tk.Scrollbar(tree_frame)
        tree_scroll.pack(side="right", fill="y")

        tree = ttk.Treeview(tree_frame, columns=("ID", "Type", "Recipient", "Amount", "Date"), show="headings",
                            yscrollcommand=tree_scroll.set)
        tree.pack(fill="both", expand=True)
        tree_scroll.config(command=tree.yview)

        tree.heading("ID", text="Transaction ID")
        tree.heading("Type", text="Type")  # "Debited" or "Credited"
        tree.heading("Recipient", text="Recipient Name")
        tree.heading("Amount", text="Amount")
        tree.heading("Date", text="Transaction Date")

        tree.column("ID", anchor="center", width=50)
        tree.column("Type", anchor="center", width=100)
        tree.column("Recipient", anchor="center", width=200)
        tree.column("Amount", anchor="center", width=100)
        tree.column("Date", anchor="center", width=150)

        try:
            conn = mysql.connector.connect(host="localhost", user="Vrushali", password="Vrushali@1220", database="bankdb")
            cursor = conn.cursor()

            query = """
            SELECT t.id, 
                   CASE 
                       WHEN t.sender_account = %s THEN 'Debited' 
                       WHEN t.receiver_account = %s THEN 'Credited' 
                   END AS transaction_type,
                   COALESCE(u.account_holder_name, 'Unknown') AS recipient_name,
                   t.amount, t.transaction_date
            FROM transactions t
            LEFT JOIN users u ON t.receiver_account = u.account_number
            WHERE t.sender_account = %s OR t.receiver_account = %s
            ORDER BY t.transaction_date Asc
            """
            cursor.execute(query, (sender_account, sender_account, sender_account, sender_account))

            transactions = cursor.fetchall()
            conn.close()

            if transactions:
                for transaction in transactions:
                    transaction_id, transaction_type, recipient_name, amount, date = transaction
                    tree.insert("", "end", values=(transaction_id, transaction_type, recipient_name, amount, date))
            else:
                tk.Label(history_frame, text="No Transactions Found!", font=("Arial", 12), bg="lavender", fg="black").pack(pady=10)

        except Exception as e:
            tk.Label(history_frame, text=f"Database error: {e}", font=("Arial", 10), fg="red", bg="lavender").pack()

    tpin_window = tk.Toplevel(root)
    tpin_window.title("Enter TPIN")
    tpin_window.geometry("800x600")
    tpin_window.configure(bg="lavender")

    tk.Label(tpin_window, text="Enter TPIN", font=("Arial", 14, "bold"), fg="purple", bg="lavender").pack(pady=10)

    entry_tpin = tk.Entry(tpin_window, font=("Arial", 12), show="*")
    entry_tpin.pack(pady=5)

    error_label = tk.Label(tpin_window, text="", font=("Arial", 10), fg="red", bg="lavender")
    error_label.pack()

    submit_button = tk.Button(tpin_window, text="Submit", font=("Arial", 12), bg="blue", fg="white",
                              command=verify_tpin)
    submit_button.pack(pady=10)

    history_frame = tk.Frame(tpin_window, bg="lavender")
    history_frame.pack(fill="both", expand=True, pady=20)

def draw_gradient(canvas, width, height):
    canvas.delete("gradient")  # Clear previous gradient
    for i in range(height):
        color = f'#{int(75 + (i / height) * 100):02x}{int(0 + (i / height) * 50):02x}{int(130 + (i / height) * 100):02x}'
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")

def resize_canvas(event):
    #canvas.delete("gradient")
    draw_gradient(canvas, event.width, event.height)
    canvas.config(width=event.width, height=event.height)



root = tk.Tk()
root.title("Bank Transaction")
root.geometry("800x500")
root.configure(bg="#f0f0f0")

canvas = tk.Canvas(root)
canvas.pack(fill="both", expand=True)

draw_gradient(canvas, 1920, 1080)
canvas.bind("<Configure>", resize_canvas)

frame = tk.Frame(root, bg="lavender", bd=5, relief="ridge")
frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=250)

tk.Label(frame, text="Transaction", font=("Arial", 16, "bold"), fg="black", bg="lavender").pack(pady=10)

tk.Button(frame, text="Check Balance", font=("Arial", 12), bg="blue", fg="white", command=open_check_balance).pack(
    pady=5)
tk.Button(frame, text="Transfer Money", font=("Arial", 12), bg="green", fg="white", command=open_transfer_money).pack(
    pady=5)
history_button = tk.Button(frame, text="View Transaction History", font=("Arial", 12), bg="purple", fg="white",
                           command=open_transaction_history_window)
history_button.pack(pady=5)

back_button = tk.Button(frame, text="⬅ Back", font=("Arial", 12), bg="gray", fg="white", command=root.destroy)
back_button.pack(pady=5)

root.mainloop()

