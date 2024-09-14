import socket
import threading
import hashlib
import sqlite3
from cryptography.fernet import Fernet

# Static encryption key to ensure the same key is used between server and clients
key = b"vzI4iHyZNDaYFZhGd3K49O6cx4FaH-7RGngGLHRmxuM="
cipher = Fernet(key)

# Setup server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 5555))
server.listen()

clients = []
usernames = {}
client_socket_map = {}

# Database setup
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)""")
conn.commit()


def register_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    c.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, hashed_password),
    )
    conn.commit()


def authenticate_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hashed_password),
    )
    return c.fetchone() is not None


# Broadcast encrypted messages to specific client
def send_private_message(message, sender, recipient):
    encrypted_message = cipher.encrypt(f"{sender}: {message}".encode())
    if recipient in client_socket_map:
        client_socket_map[recipient].send(encrypted_message)


def handle_client(client):
    username = [user for user, sock in client_socket_map.items() if sock == client][0]

    while True:
        try:
            encrypted_message = client.recv(1024)
            if encrypted_message:
                message = cipher.decrypt(encrypted_message).decode()
                if ":" in message:
                    recipient, msg = message.split(":", 1)
                    send_private_message(msg, username, recipient.strip())
                else:
                    # Handle public messages if needed
                    pass
        except:
            index = list(client_socket_map.values()).index(client)
            client.close()
            username = list(client_socket_map.keys())[index]
            del client_socket_map[username]
            del usernames[username]
            break


def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        # Request username
        client.send("USERNAME".encode("utf-8"))
        username = client.recv(1024).decode("utf-8")

        # Request password
        client.send("PASSWORD".encode("utf-8"))
        password = client.recv(1024).decode("utf-8")

        # Check if user exists, else register
        if authenticate_user(username, password):
            client.send("Authenticated!".encode("utf-8"))
        else:
            register_user(username, password)
            client.send("Registered and Authenticated!".encode("utf-8"))

        client_socket_map[username] = client
        usernames[username] = client
        print(f"{username} joined the chat.")

        # Start handling client in a separate thread
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()


print("Server is listening...")
receive()
