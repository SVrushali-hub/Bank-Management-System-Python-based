import tkinter as tk
import mysql.connector
import hashlib
import random
import string
from tkinter import Canvas


# MySQL database connection setup
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # Host where MySQL is running
        user="root",  # Your MySQL username
        password="root@123",  # Your MySQL password
        database="bankdb"  # Your database name
    )


# Verify email from MySQL database
def verify_email(email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        conn.close()
        return user
    except mysql.connector.Error as err:
        error_label.config(text=f"Database Error: {err}", fg="red",bg='lavender')
        success_label.config(text="")  # Clear any success label
        return None


# Function to hash the TPIN (using SHA-256 for secure storage)
def hash_tpin(tpin):
    return hashlib.sha256(tpin.encode('utf-8')).hexdigest()


# Function to save TPIN (hashed) to the database
def save_tpin(email, tpin):
    try:
        # Hash the TPIN before saving
        hashed_tpin = hash_tpin(tpin)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET tpin = %s WHERE email = %s", (hashed_tpin, email))
        conn.commit()
        conn.close()

        # Replace error label with success label
        success_label.config(text="TPIN has been successfully set!", fg="purple",bg='lavender')
        error_label.config(text="")  # Clear any error label
        success_label.pack(pady=10)  # Make sure the success label is packed after it's updated
    except mysql.connector.Error as err:
        error_label.config(text=f"Database Error: {err}", fg="red",bg='lavender')
        success_label.config(text="")  # Clear any success label


# Function to generate a random CAPTCHA string
def generate_captcha():
    # Generate a random 6-character CAPTCHA string
    captcha = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return captcha


# Function to handle CAPTCHA validation
def verify_captcha():
    captcha_input = captcha_entry.get().strip()

    # Only replace the label if there's a change in the CAPTCHA status
    if captcha_input == captcha:
        error_label.config(text="")  # Clear error label
        verified_label.config(text="CAPTCHA Verified!", fg="purple", bg='lavender')
        success_label.config(text="")  # Clear success label
        show_verified_and_email_input()
    else:
        verified_label.config(text="")
        error_label.config(text="Incorrect CAPTCHA. Please try again.", fg="red",bg='lavender')
        success_label.config(text="")  # Clear success label


# Function to show "Verified" label and email input fields
def show_verified_and_email_input():
    # Display "Verified" label below CAPTCHA
    verified_label.pack(pady=5)

    # Show email input form directly below the "Verified" label
    email_label.pack(pady=5)
    email_entry.pack(pady=5)
    verify_button.pack(pady=20)


# Function to handle email verification and move to TPIN setup
def verify_and_proceed():
    email = email_entry.get()

    # Only replace the label if there's a change in email verification status
    if not email:
        error_label.config(text="Please enter an email address.", fg="red",bg='lavender')
        verified_label.config(text="")
        success_label.config(text="")  # Clear any success label
        return

    user = verify_email(email)
    if user:
        verified_label.config(text="Email Verified!", fg="purple",bg='lavender')
        error_label.config(text="")  # Clear error label
        success_label.config(text="")  # Clear any success label
        show_tpin_input(email)
    else:
        error_label.config(text="The email address is not registered.", fg="red",bg='lavender')
        verified_label.config(text="")
        success_label.config(text="")  # Clear any success label


# Function to show the TPIN setup form
def show_tpin_input(email):
    global tpin_entry, confirm_tpin_entry  # Declare tpin_entry and confirm_tpin_entry as global variables

    # TPIN setup title
    tpin_label = tk.Label(frame, text="Set New TPIN ",bd=2,font=("Arial", 16,"bold"),fg="purple",bg='lavender')
    tpin_label.pack(pady=10)

    # TPIN input field
    tpin_label = tk.Label(frame, text="Enter a 6-digit TPIN:",bg='lavender',font=("Arial",14,"bold"))
    tpin_label.pack(pady=5)
    tpin_entry = tk.Entry(frame, show="*", font=("Arial", 14),bg='lavender')  # Declare tpin_entry here
    tpin_entry.pack(pady=5)

    # Confirm TPIN input field
    confirm_tpin_label = tk.Label(frame, text="Confirm TPIN:",bg='lavender',font=("Arial",14))
    confirm_tpin_label.pack(pady=5)
    confirm_tpin_entry = tk.Entry(frame, show="*", font=("Arial", 14),fg='black',bg='lavender')  # Declare confirm_tpin_entry here
    confirm_tpin_entry.pack(pady=5)

    # Button to save TPIN
    save_button = tk.Button(frame, text="Save TPIN", font=("Arial", 14), bg='Purple',fg='white',command=lambda: save_tpin_and_notify(email))
    save_button.pack(pady=20)


# Function to save TPIN and show confirmation
def save_tpin_and_notify(email):
    tpin = tpin_entry.get()
    confirm_tpin = confirm_tpin_entry.get()

    if len(tpin) != 6 or not tpin.isdigit():
        error_label.config(text="Please enter a valid 6-digit TPIN.", fg="red",bg='lavender')
        success_label.config(text="")  # Clear any success label
        return

    if tpin != confirm_tpin:
        error_label.config(text="The TPIN and Confirm TPIN do not match.", fg="red",bg='lavender')
        success_label.config(text="")  # Clear any success label
        return

    save_tpin(email, tpin)
    # Success will be handled in the save_tpin function
def draw_gradient(canvas, width, height):
    canvas.delete("gradient")  # Clear previous gradient
    for i in range(height):
        color = f'#{int(75 + (i / height) * 100):02x}{int(0 + (i / height) * 50):02x}{int(130 + (i / height) * 100):02x}'
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")


# Create the main window
root = tk.Tk()
root.title("Email Verification and TPIN Setup")
root.geometry("1920x1080")  # Set the window size to 1920x1080
root.configure(bg="#D8BFD8")

canvas = Canvas(root)
canvas.pack(fill="both", expand=True)

root.update_idletasks()
draw_gradient(canvas, root.winfo_width(), root.winfo_height())

# Create a frame to hold all widgets and center them inside the main window
frame = tk.Frame(root, width=400, height=700, bd=2, relief="solid", bg="#E6E6FA")  # Lavender color
frame.pack_propagate(False)  # Prevent the frame from resizing based on its contents
frame.place(relx=0.5, rely=0.5, anchor="center")  # Position the frame at the center of the window

# Generate CAPTCHA
captcha = generate_captcha()

# CAPTCHA verification section
captcha_label = tk.Label(frame, text=f"Enter the CAPTCHA: {captcha}", font=("Arial", 14,"bold"),fg="purple",bg='Lavender')
captcha_label.pack(pady=20)

captcha_entry = tk.Entry(frame, font=("Arial", 14),bg='Lavender')
captcha_entry.pack(pady=5)

captcha_button = tk.Button(frame, text="Verify CAPTCHA", font=("Arial", 14), bg='Purple',fg='white',command=verify_captcha)
captcha_button.pack(pady=20)

# Verified label (hidden initially, now just displayed after CAPTCHA verification)
verified_label = tk.Label(frame, text="", font=("Arial", 14), fg="purple")

# Error and Success Labels (hidden initially)
error_label = tk.Label(frame, text="", font=("Arial", 14), fg="red",bg='lavender')
success_label = tk.Label(frame, text="", font=("Arial", 14), fg="purple",bg='lavender')

# Email verification section (hidden initially)
email_label = tk.Label(frame, text="Enter your registered email:", font=("Arial", 14,"bold"),fg="purple",bg='lavender')
email_entry = tk.Entry(frame, font=("Arial", 14))
verify_button = tk.Button(frame, text="Verify Email", font=("Arial", 14),bg='Purple',fg='lavender', command=verify_and_proceed)

# Start the Tkinter main loop
root.mainloop()

