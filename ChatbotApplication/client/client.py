import socket
import threading
from cryptography.fernet import Fernet

# Static encryption key to ensure the same key is used between server and clients
key = b"vzI4iHyZNDaYFZhGd3K49O6cx4FaH-7RGngGLHRmxuM="
cipher = Fernet(key)

# Server connection setup
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 5555))


def receive_messages():
    while True:
        try:
            encrypted_message = client.recv(1024)
            if not encrypted_message:
                break
            message = cipher.decrypt(encrypted_message).decode()
            print(message)
        except:
            print("An error occurred while receiving messages!")
            client.close()
            break


def send_messages():
    while True:
        recipient = input('Enter recipient username (or type "all" for public): ')
        message = input("Enter your message: ")
        if recipient.lower() != "all":
            formatted_message = f"{recipient}: {message}"
        else:
            formatted_message = f"public: {message}"
        encrypted_message = cipher.encrypt(formatted_message.encode())
        client.send(encrypted_message)


def authenticate():
    try:
        # Receive username prompt from server
        message = client.recv(1024).decode("utf-8")
        if message == "USERNAME":
            client.send(input("Enter your username: ").encode("utf-8"))

        # Receive password prompt from server
        message = client.recv(1024).decode("utf-8")
        if message == "PASSWORD":
            client.send(input("Enter your password: ").encode("utf-8"))

        # Receive authentication result from server
        auth_response = client.recv(1024).decode("utf-8")
        print(auth_response)
    except:
        print("An error occurred during authentication.")
        client.close()


# Start threads for receiving and sending messages
authenticate()

receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

send_thread = threading.Thread(target=send_messages)
send_thread.start()
