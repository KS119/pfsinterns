import socket
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import simpledialog, scrolledtext
import threading

# Encryption key
key = b"vzI4iHyZNDaYFZhGd3K49O6cx4FaH-7RGngGLHRmxuM="
cipher = Fernet(key)

# Create the client socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5555))


def send_message():
    message = message_entry.get()
    recipient = recipient_entry.get()

    if recipient:
        full_message = f"{recipient}: {message}"
    else:
        full_message = message

    # Encrypt and send the message
    encrypted_message = cipher.encrypt(full_message.encode())
    client.send(encrypted_message)
    message_entry.delete(0, tk.END)


def receive_messages():
    while True:
        try:
            encrypted_message = client.recv(1024)
            if not encrypted_message:
                print("Connection closed by server.")
                break

            # Decrypt and display the message
            message = cipher.decrypt(encrypted_message).decode("utf-8")

            # Debug print to check received message
            print(f"Received message: {message}")

            # Update chat area on the main thread
            root.after(0, lambda: update_chat_area(message))
        except Exception as e:
            print(f"Error receiving message: {e}")
            break


def update_chat_area(message):
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, message + "\n")
    chat_area.config(state=tk.DISABLED)
    chat_area.yview(tk.END)  # Scroll to the end of the chat area


# GUI setup
root = tk.Tk()
root.title("Secure Chat Application")

recipient_label = tk.Label(root, text="Recipient (leave empty for public):")
recipient_label.pack()

recipient_entry = tk.Entry(root)
recipient_entry.pack()

message_entry = tk.Entry(root, width=50)
message_entry.pack()

send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack()

chat_area = scrolledtext.ScrolledText(root, state=tk.DISABLED, width=50, height=20)
chat_area.pack()


# Request username and password
def request_credentials():
    username = simpledialog.askstring("Username", "Enter your username:")
    if not username:
        print("Username is required.")
        return
    client.send(username.encode())

    password = simpledialog.askstring("Password", "Enter your password:", show="*")
    if not password:
        print("Password is required.")
        return
    client.send(password.encode())


# Start thread to receive messages
thread = threading.Thread(target=receive_messages, daemon=True)
thread.start()

# Request credentials and start the GUI
request_credentials()
root.mainloop()
