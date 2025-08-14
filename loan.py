import tkinter as tk
from tkinter import messagebox

# Create the main application window
root = tk.Tk()
root.title("Loan Management System")
root.geometry("600x400")


# Loan Application Form
def submit_loan_application():
    customer_name = name_entry.get()
    loan_amount = amount_entry.get()
    loan_duration = duration_entry.get()

    if customer_name == "" or loan_amount == "" or loan_duration == "":
        messagebox.showerror("Input Error", "Please fill in all fields.")
    else:
        loan_data = {
            "customer_name": customer_name,
            "loan_amount": loan_amount,
            "loan_duration": loan_duration
        }
        # For demonstration, we'll just show a message box
        messagebox.showinfo("Loan Application Submitted",
                            f"Loan for {customer_name} submitted successfully!\nLoan Amount: {loan_amount}\nDuration: {loan_duration} months.")

        # Here, you can implement saving data to a database or file
        # For now, we will print to console (simulating data storage)
        print(loan_data)


# Create a loan application form
frame = tk.Frame(root)
frame.pack(pady=20)

tk.Label(frame, text="Customer Name:").grid(row=0, column=0, padx=10, pady=5)
name_entry = tk.Entry(frame)
name_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame, text="Loan Amount:").grid(row=1, column=0, padx=10, pady=5)
amount_entry = tk.Entry(frame)
amount_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame, text="Loan Duration (Months):").grid(row=2, column=0, padx=10, pady=5)
duration_entry = tk.Entry(frame)
duration_entry.grid(row=2, column=1, padx=10, pady=5)

submit_button = tk.Button(frame, text="Submit Loan Application", command=submit_loan_application)
submit_button.grid(row=3, columnspan=2, pady=20)


# Loan Status Tracking (Admin feature)
def check_loan_status():
    loan_id = loan_id_entry.get()

    if loan_id == "":
        messagebox.showerror("Input Error", "Please enter the loan ID.")
    else:
        # For now, simulate loan data (in a real system, you'd query a database)
        loan_data = {
            "12345": "Approved",
            "67890": "Pending",
            "11223": "Rejected"
        }

        status = loan_data.get(loan_id, "Loan ID not found.")
        messagebox.showinfo("Loan Status", f"Loan Status for ID {loan_id}: {status}")


# Loan Status Section
status_frame = tk.Frame(root)
status_frame.pack(pady=20)

tk.Label(status_frame, text="Enter Loan ID to Check Status:").grid(row=0, column=0, padx=10, pady=5)
loan_id_entry = tk.Entry(status_frame)
loan_id_entry.grid(row=0, column=1, padx=10, pady=5)

check_button = tk.Button(status_frame, text="Check Loan Status", command=check_loan_status)
check_button.grid(row=1, columnspan=2, pady=10)

# Main loop to run the application
root.mainloop()