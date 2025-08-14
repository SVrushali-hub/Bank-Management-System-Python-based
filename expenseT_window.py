import tkinter as tk
from tkinter import messagebox
import subprocess
import sys


# Get username from the dashboard
if len(sys.argv) > 1:
    logged_in_username = sys.argv[1].strip()
else:
    logged_in_username = None


def open_show_expenses():
    if not logged_in_username:
        messagebox.showerror("Error", "User not logged in!")
        return
    try:
        subprocess.Popen(["python", "expense_tracker.py", logged_in_username])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open Expense Tracker: {e}")


def open_monthly_expense():
    if not logged_in_username:
        messagebox.showerror("Error", "User not logged in!")
        return
    try:
        subprocess.Popen(["python", "monthly_expense.py", logged_in_username])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open Monthly Expense: {e}")


# Function to create a purple gradient background
def draw_gradient(canvas, width, height):
    for i in range(height):
        color = f'#{int(100 + (i / height) * 100):02x}{int(50 + (i / height) * 50):02x}{int(150 + (i / height) * 100):02x}'
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")


def resize_canvas(event):
    canvas.delete("gradient")
    draw_gradient(canvas, event.width, event.height)
    canvas.config(width=event.width, height=event.height)


# GUI Window
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("500x400")
root.state("zoomed")
root.minsize(400, 300)  # Allow resizing
root.resizable(True, True)

# Canvas for gradient
canvas = tk.Canvas(root)
canvas.pack(fill="both", expand=True)
draw_gradient(canvas, 500, 400)
canvas.bind("<Configure>", resize_canvas)

# Main frame for UI elements
frame = tk.Frame(root, bg="lavender", bd=5, relief="ridge")
frame.place(relx=0.5, rely=0.5, anchor="center", width=350, height=250)

tk.Label(frame, text="💰 Expense Tracker", font=("Arial", 16, "bold"), fg="purple", bg="lavender").pack(pady=10)

tk.Button(frame, text="📜 Show Expenses", font=("Arial", 12, "bold"), bg="purple", fg="white",
          activebackground="darkviolet", activeforeground="white", width=20, command=open_show_expenses).pack(pady=10)

tk.Button(frame, text="📅 Monthly Expense", font=("Arial", 12, "bold"), bg="indigo", fg="white",
          activebackground="darkslateblue", activeforeground="white", width=20, command=open_monthly_expense).pack(pady=10)

tk.Button(frame, text="⬅ Back", font=("Arial", 12, "bold"), bg="gray", fg="white", width=20,
          activebackground="black", activeforeground="white", command=root.destroy).pack(pady=10)

root.mainloop()
