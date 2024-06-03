from socket import *
import threading
import os
import json
import hashlib
import time

clients = {}
messages = {}
users = {}

def load_users():
    global users
    if os.path.exists("users.json"):
        with open("users.json", "r") as file:
            users = json.load(file)

def save_users():
    with open("users.json", "w") as file:
        json.dump(users, file)

def load_messages():
    global messages
    if os.path.exists("messages.json"):
        with open("messages.json", "r") as file:
            messages = json.load(file)

def save_messages():
    with open("messages.json", "w") as file:
        json.dump(messages, file)

def broadcast_user_list():
    user_list = ",".join(clients.values())
    for client_socket in clients:
        try:
            client_socket.send(f"USERS:{user_list}".encode())
        except:
            client_socket.close()
            remove_client(client_socket)

def send_private_message(sender_socket, recipient, message):
    for client_socket, username in clients.items():
        if username == recipient:
            try:
                client_socket.send(f"{clients[sender_socket]}: {message}".encode())
                print(f"{clients[sender_socket]} to {username}: {message}")
            except:
                client_socket.close()
                remove_client(client_socket)
            return
    save_offline_message(clients[sender_socket], recipient, message)

def save_offline_message(sender, recipient, message):
    if recipient not in messages:
        messages[recipient] = []
    timestamp = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    formatted_message = f"{sender}: {message.strip()} ({timestamp})"
    messages[recipient].append(formatted_message)
    save_messages()
    print(f"Saved offline message from {sender} to {recipient}: {message.strip()}")

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message:
                if message.startswith("REGISTER:"):
                    username, password = message.split(":")[1:]
                    if username in users:
                        client_socket.send("ERROR:Username already taken".encode())
                        print(f"Registration failed for {username}: Username already taken")
                    else:
                        users[username] = hashlib.sha256(password.encode()).hexdigest()
                        save_users()
                        client_socket.send("REGISTER_SUCCESS".encode())
                        print(f"User registered: {username}")
                elif message.startswith("LOGIN:"):
                    username, password = message.split(":")[1:]
                    if username in users and users[username] == hashlib.sha256(password.encode()).hexdigest():
                        clients[client_socket] = username
                        client_socket.send("LOGIN_SUCCESS".encode())
                        print(f"User logged in: {username}")
                        broadcast_user_list()
                        if username in messages:
                            for msg in messages[username]:
                                client_socket.send(msg.encode())
                            del messages[username]
                            save_messages()
                    else:
                        client_socket.send("ERROR:Invalid username or password".encode())
                        print(f"Login failed for {username}: Invalid username or password")
                elif message.startswith("RESET:"):
                    username, password = message.split(":")[1:]
                    if username in users:
                        users[username] = hashlib.sha256(password.encode()).hexdigest()
                        save_users()
                        client_socket.send("RESET_SUCCESS".encode())
                        print(f"Password reset for user: {username}")
                    else:
                        client_socket.send("ERROR:Username not found".encode())
                        print(f"Password reset failed for {username}: Username not found")
                else:
                    recipient, msg = message.split(":", 1)
                    send_private_message(client_socket, recipient, msg)
        except Exception as e:
            print(f"Error handling client {clients.get(client_socket, 'unknown')}: {e}")
            remove_client(client_socket)
            break

def remove_client(client_socket):
    if client_socket in clients:
        print(f"User disconnected: {clients[client_socket]}")
        client_socket.close()
        del clients[client_socket]
        broadcast_user_list()

def accept_connections(server_socket):
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()

def start_server():
    load_users()
    load_messages()
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(('', 5001))
    server_socket.listen(10)
    print("Server started on port 5001")
    accept_connections(server_socket)

if __name__ == "__main__":
    start_server()
