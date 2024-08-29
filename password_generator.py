import tkinter as tk
from tkinter import messagebox
import pyperclip
from password_utils import generate_password


def generate():
    length = int(length_entry.get())
    use_uppercase = uppercase_var.get()
    use_digits = digits_var.get()
    use_special_chars = special_var.get()

    password = generate_password(length, use_uppercase, use_digits, use_special_chars)
    password_entry.delete(0, tk.END)
    password_entry.insert(0, password)


def copy_to_clipboard():
    pyperclip.copy(password_entry.get())
    messagebox.showinfo("Copied", "Password copied to clipboard.")


# GUI setup
root = tk.Tk()
root.title("Password Generator")

tk.Label(root, text="Password Length:").grid(row=0, column=0)
length_entry = tk.Entry(root)
length_entry.grid(row=0, column=1)
length_entry.insert(0, "12")

uppercase_var = tk.BooleanVar()
digits_var = tk.BooleanVar()
special_var = tk.BooleanVar()

tk.Checkbutton(root, text="Include Uppercase", variable=uppercase_var).grid(
    row=1, column=0, sticky="w"
)
tk.Checkbutton(root, text="Include Digits", variable=digits_var).grid(
    row=2, column=0, sticky="w"
)
tk.Checkbutton(root, text="Include Special Characters", variable=special_var).grid(
    row=3, column=0, sticky="w"
)

tk.Button(root, text="Generate", command=generate).grid(row=4, column=0, columnspan=2)
password_entry = tk.Entry(root)
password_entry.grid(row=5, column=0, columnspan=2)

tk.Button(root, text="Copy", command=copy_to_clipboard).grid(
    row=6, column=0, columnspan=2
)

root.mainloop()
