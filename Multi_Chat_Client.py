import tkinter as tk
from tkinter import messagebox, scrolledtext, Toplevel, Listbox
from socket import *
import threading
import time
import os
import json

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat Client")
        self.master.geometry("900x600")
        self.master.configure(bg="#F6F7F9")

        self.server_ip = tk.StringVar()
        self.username = tk.StringVar()
        self.password = tk.StringVar()

        self.load_last_username()

        self.server_socket = None
        self.connected = False
        self.chat_windows = {}
        self.active_chat = None
        self.user_chats = {}
        self.unread_messages = {}

        self.setup_login_screen()

    def load_last_username(self):
        if os.path.exists("last_username.json"):
            with open("last_username.json", "r") as file:
                data = json.load(file)
                self.username.set(data.get("username", ""))

    def save_username(self):
        with open("last_username.json", "w") as file:
            json.dump({"username": self.username.get()}, file)

    def setup_login_screen(self):
        self.login_frame = tk.Frame(self.master, padx=20, pady=20, bg="#F6F7F9")
        self.login_frame.pack(expand=True)

        tk.Label(self.login_frame, text="Server's IP-address:", font=("Helvetica", 14), bg="#F6F7F9").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(self.login_frame, textvariable=self.server_ip, font=("Helvetica", 14), width=20).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.login_frame, text="Username:", font=("Helvetica", 14), bg="#F6F7F9").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(self.login_frame, textvariable=self.username, font=("Helvetica", 14), width=20).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.login_frame, text="Password:", font=("Helvetica", 14), bg="#F6F7F9").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(self.login_frame, textvariable=self.password, font=("Helvetica", 14), width=20, show="*").grid(row=2, column=1, padx=5, pady=5)

        self.register_button = tk.Button(self.login_frame, text="Register", font=("Helvetica", 14), bg="#4CAF50", fg="white", command=self.show_register_screen)
        self.register_button.grid(row=3, column=0, padx=5, pady=10, sticky=tk.E)

        self.login_button = tk.Button(self.login_frame, text="Login", font=("Helvetica", 14), bg="#4CAF50", fg="white", command=self.login_user)
        self.login_button.grid(row=3, column=1, padx=5, pady=10, sticky=tk.E)

        self.reset_button = tk.Button(self.login_frame, text="Forgot Password?", font=("Helvetica", 10), bg="#F6F7F9", fg="blue", bd=0, command=self.show_reset_screen)
        self.reset_button.grid(row=4, column=1, padx=5, pady=10, sticky=tk.W)

    def show_register_screen(self):
        self.login_frame.pack_forget()
        self.register_frame = tk.Frame(self.master, padx=20, pady=20, bg="#F6F7F9")
        self.register_frame.pack(expand=True)

        tk.Label(self.register_frame, text="Server's IP-address:", font=("Helvetica", 14), bg="#F6F7F9").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(self.register_frame, textvariable=self.server_ip, font=("Helvetica", 14), width=20).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.register_frame, text="Username:", font=("Helvetica", 14), bg="#F6F7F9").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(self.register_frame, textvariable=self.username, font=("Helvetica", 14), width=20).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.register_frame, text="Password:", font=("Helvetica", 14), bg="#F6F7F9").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(self.register_frame, textvariable=self.password, font=("Helvetica", 14), width=20, show="*").grid(row=2, column=1, padx=5, pady=5)

        self.password_requirements_label = tk.Label(self.register_frame, text="Password must be at least 8 characters long, include a number and a letter.", font=("Helvetica", 10), bg="#F6F7F9", fg="red")
        self.password_requirements_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.register_button = tk.Button(self.register_frame, text="Register", font=("Helvetica", 14), bg="#4CAF50", fg="white", command=self.register_user)
        self.register_button.grid(row=4, column=1, padx=5, pady=10, sticky=tk.E)

        self.back_button = tk.Button(self.register_frame, text="Back to Login", font=("Helvetica", 14), bg="#4CAF50", fg="white", command=self.back_to_login)
        self.back_button.grid(row=4, column=0, padx=5, pady=10, sticky=tk.W)

    def show_reset_screen(self):
        self.login_frame.pack_forget()
        self.reset_frame = tk.Frame(self.master, padx=20, pady=20, bg="#F6F7F9")
        self.reset_frame.pack(expand=True)

        tk.Label(self.reset_frame, text="Server's IP-address:", font=("Helvetica", 14), bg="#F6F7F9").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(self.reset_frame, textvariable=self.server_ip, font=("Helvetica", 14), width=20).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.reset_frame, text="Username:", font=("Helvetica", 14), bg="#F6F7F9").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(self.reset_frame, textvariable=self.username, font=("Helvetica", 14), width=20).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.reset_frame, text="New Password:", font=("Helvetica", 14), bg="#F6F7F9").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(self.reset_frame, textvariable=self.password, font=("Helvetica", 14), width=20, show="*").grid(row=2, column=1, padx=5, pady=5)

        self.password_requirements_label = tk.Label(self.reset_frame, text="Password must be at least 8 characters long, include a number and a letter.", font=("Helvetica", 10), bg="#F6F7F9", fg="red")
        self.password_requirements_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        self.reset_button = tk.Button(self.reset_frame, text="Reset Password", font=("Helvetica", 14), bg="#4CAF50", fg="white", command=self.reset_password)
        self.reset_button.grid(row=4, column=1, padx=5, pady=10, sticky=tk.E)

        self.back_button = tk.Button(self.reset_frame, text="Back to Login", font=("Helvetica", 14), bg="#4CAF50", fg="white", command=self.back_to_login)
        self.back_button.grid(row=4, column=0, padx=5, pady=10, sticky=tk.W)

    def back_to_login(self):
        if hasattr(self, 'register_frame'):
            self.register_frame.pack_forget()
        if hasattr(self, 'reset_frame'):
            self.reset_frame.pack_forget()
        self.setup_login_screen()

    def register_user(self):
        ip = self.server_ip.get()
        username = self.username.get()
        password = self.password.get()

        if not ip or not username or not password:
            messagebox.showerror("Error", "Please enter IP address, username, and password")
            return

        if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            messagebox.showerror("Error", "Password must be at least 8 characters long, include a number and a letter")
            return

        self.server_socket = socket(AF_INET, SOCK_STREAM)
        try:
            self.server_socket.connect((ip, 5001))
            self.server_socket.send(f"REGISTER:{username}:{password}".encode())
            response = self.server_socket.recv(1024).decode()
            if response == "REGISTER_SUCCESS":
                messagebox.showinfo("Success", "Registration successful! Please login.")
                self.server_socket.close()
                self.back_to_login()
            else:
                messagebox.showerror("Error", response.split(":")[1])
                self.server_socket.close()
        except:
            messagebox.showerror("Error", "Could not connect to server")
            self.server_socket.close()

    def login_user(self):
        ip = self.server_ip.get()
        username = self.username.get()
        password = self.password.get()

        if not ip or not username or not password:
            messagebox.showerror("Error", "Please enter IP address, username, and password")
            return

        self.server_socket = socket(AF_INET, SOCK_STREAM)
        try:
            self.server_socket.connect((ip, 5001))
            self.server_socket.send(f"LOGIN:{username}:{password}".encode())
            response = self.server_socket.recv(1024).decode()
            if response == "LOGIN_SUCCESS":
                self.connected = True
                self.save_username()
                self.setup_chat_screen()
                threading.Thread(target=self.receive_messages).start()
                self.load_user_chats()
            else:
                messagebox.showerror("Error", response.split(":")[1])
                self.server_socket.close()
        except:
            messagebox.showerror("Error", "Could not connect to server")
            self.server_socket.close()

    def reset_password(self):
        ip = self.server_ip.get()
        username = self.username.get()
        password = self.password.get()

        if not ip or not username or not password:
            messagebox.showerror("Error", "Please enter IP address, username, and new password")
            return

        if len(password) < 8 or not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password):
            messagebox.showerror("Error", "Password must be at least 8 characters long, include a number and a letter")
            return

        self.server_socket = socket(AF_INET, SOCK_STREAM)
        try:
            self.server_socket.connect((ip, 5001))
            self.server_socket.send(f"RESET:{username}:{password}".encode())
            response = self.server_socket.recv(1024).decode()
            if response == "RESET_SUCCESS":
                messagebox.showinfo("Success", "Password reset successful! Please login.")
                self.server_socket.close()
                self.back_to_login()
            else:
                messagebox.showerror("Error", response.split(":")[1])
                self.server_socket.close()
        except:
            messagebox.showerror("Error", "Could not connect to server")
            self.server_socket.close()

    def setup_chat_screen(self):
        self.login_frame.destroy()
        if hasattr(self, 'register_frame'):
            self.register_frame.destroy()
        if hasattr(self, 'reset_frame'):
            self.reset_frame.destroy()

        self.chat_frame = tk.Frame(self.master, bg="#F6F7F9")
        self.chat_frame.pack(fill=tk.BOTH, expand=True)

        self.contact_list_frame = tk.Frame(self.chat_frame, width=250, bg="#E8EAF6")
        self.contact_list_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.header_frame = tk.Frame(self.contact_list_frame, bg="#3F51B5")
        self.header_frame.pack(fill=tk.X)

        self.contacts_label = tk.Label(self.header_frame, text=self.username.get(), bg="#3F51B5", fg="white", font=("Helvetica", 18, "bold"), pady=10)
        self.contacts_label.pack(side=tk.LEFT, padx=5)

        self.disconnect_button = tk.Button(self.header_frame, text="❌", font=("Helvetica", 14), bg="#3F51B5", fg="white", bd=0, command=self.disconnect_from_server)
        self.disconnect_button.pack(side=tk.RIGHT, padx=5)

        self.search_entry = tk.Entry(self.contact_list_frame, font=("Helvetica", 14), bg="#FFF", bd=0)
        self.search_entry.pack(fill=tk.X, padx=5, pady=5)
        self.search_entry.insert(0, "Search")

        self.contacts_listbox = tk.Listbox(self.contact_list_frame, font=("Helvetica", 14), bg="#E8EAF6", bd=0, selectbackground="#3F51B5", selectforeground="white")
        self.contacts_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.contacts_listbox.bind('<<ListboxSelect>>', self.select_chat)

        self.message_frame = tk.Frame(self.chat_frame, bg="#FFF")
        self.message_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.messages_text = scrolledtext.ScrolledText(self.message_frame, state=tk.DISABLED, wrap=tk.WORD, font=("Helvetica", 14), bg="#FFF", bd=0, padx=10, pady=10)
        self.messages_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.entry_frame = tk.Frame(self.message_frame, bg="#FFF")
        self.entry_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        self.message_entry = tk.Entry(self.entry_frame, font=("Helvetica", 14), bg="#F0F0F0", bd=0)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.message_entry.bind('<Return>', lambda event: self.send_message())

        self.emoji_button = tk.Button(self.entry_frame, text="😊", font=("Helvetica", 14), bg="#FFC107", fg="white", bd=0, command=self.show_emoji_picker)
        self.emoji_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.send_button = tk.Button(self.entry_frame, text="Send", font=("Helvetica", 14), bg="#4CAF50", fg="white", bd=0, command=self.send_message)
        self.send_button.pack(side=tk.RIGHT, padx=5, pady=5)

    def show_emoji_picker(self):
        emoji_window = Toplevel(self.master)
        emoji_window.title("Emoji Picker")
        emoji_window.geometry("200x200")
        emoji_window.configure(bg="#FFF")

        emojis = ["😊", "😂", "😍", "😭", "😒", "😘", "😔", "😁", "😢", "😎", "😡", "😴"]

        emoji_listbox = Listbox(emoji_window, font=("Helvetica", 14))
        emoji_listbox.pack(fill=tk.BOTH, expand=True)

        for emoji in emojis:
            emoji_listbox.insert(tk.END, emoji)

        def insert_selected_emoji(event):
            selected_emoji = emoji_listbox.get(emoji_listbox.curselection())
            self.message_entry.insert(tk.END, selected_emoji)
            emoji_window.destroy()

        emoji_listbox.bind('<<ListboxSelect>>', insert_selected_emoji)

    def disconnect_from_server(self):
        if self.connected:
            self.server_socket.send("DISCONNECT".encode())
            self.server_socket.close()
            self.connected = False
            self.master.quit()

    def load_user_chats(self):
        if os.path.exists(f"{self.username.get()}_chats.json"):
            with open(f"{self.username.get()}_chats.json", "r") as file:
                self.user_chats = json.load(file)
                for user in self.user_chats.keys():
                    self.contacts_listbox.insert(tk.END, user)

    def save_user_chats(self):
        with open(f"{self.username.get()}_chats.json", "w") as file:
            json.dump(self.user_chats, file)

    def select_chat(self, event):
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            self.active_chat = event.widget.get(index).split(" ")[0]
            if self.active_chat in self.unread_messages:
                del self.unread_messages[self.active_chat]
            self.display_messages()

    def display_messages(self):
        self.messages_text.config(state=tk.NORMAL)
        self.messages_text.delete('1.0', tk.END)
        if self.active_chat in self.user_chats:
            current_date = ""
            for message in self.user_chats[self.active_chat]:
                msg_date = message.split("(")[-1].split(" ")[0]
                try:
                    msg_date_formatted = time.strftime("%B %d", time.strptime(msg_date, "%Y-%m-%d"))
                except ValueError:
                    msg_date_formatted = ""
                if current_date != msg_date_formatted:
                    self.messages_text.insert(tk.END, f"\n{msg_date_formatted}\n", "date_centered")
                    current_date = msg_date_formatted
                self.format_message(message)
        self.messages_text.config(state=tk.DISABLED)
        self.messages_text.yview(tk.END)

    def format_message(self, message):
        parts = message.split(": ", 1)
        sender = parts[0]
        rest = parts[1].rsplit("(", 1)
        msg = rest[0].strip()
        timestamp = rest[1].strip(")").split(" ")[1]

        tag = "sent" if sender == "You" else "received"

        bubble_color = "#DCF8C6" if sender == "You" else "#F1F0F0"
        align = "right" if sender == "You" else "left"

        self.messages_text.tag_configure(tag, justify=align, background=bubble_color, wrap='word')
        self.messages_text.tag_configure(f"{tag}_timestamp", font=("Helvetica", 8), foreground="#999999", justify=align)
        self.messages_text.tag_configure("date_centered", font=("Helvetica", 10), foreground="#888888", justify="center")

        self.messages_text.insert(tk.END, msg + " ", tag)
        self.messages_text.insert(tk.END, f"{timestamp}\n", f"{tag}_timestamp")

    def receive_messages(self):
        while self.connected:
            try:
                message = self.server_socket.recv(1024).decode()
                if message.startswith("USERS:"):
                    users = message[6:].split(',')
                    self.update_user_list(users)
                else:
                    self.process_message(message)
            except:
                self.connected = False
                self.server_socket.close()
                break

    def update_user_list(self, users):
        self.contacts_listbox.delete(0, tk.END)
        for user in users:
            if user != self.username.get():
                self.contacts_listbox.insert(tk.END, user)
        for user in self.user_chats.keys():
            if user not in users and user != self.username.get():
                self.contacts_listbox.insert(tk.END, user)

    def process_message(self, message):
        sender, msg = message.split(":", 1)
        timestamp = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        formatted_message = f"{sender}: {msg.strip()} ({timestamp})"
        if sender not in self.user_chats:
            self.user_chats[sender] = []
        self.user_chats[sender].append(formatted_message)
        if sender != self.active_chat:
            if sender not in self.unread_messages:
                self.unread_messages[sender] = 0
            self.unread_messages[sender] += 1
        self.save_user_chats()
        self.update_contacts_list()
        if self.active_chat == sender:
            self.display_messages()

    def update_contacts_list(self):
        self.contacts_listbox.delete(0, tk.END)
        for user in self.user_chats.keys():
            if user != self.username.get():
                display_name = user
                if user in self.unread_messages:
                    display_name += f" ({self.unread_messages[user]})"
                self.contacts_listbox.insert(tk.END, display_name)

    def send_message(self):
        if self.active_chat:
            msg = self.message_entry.get().strip()
            if msg:
                if self.active_chat not in self.user_chats:
                    self.user_chats[self.active_chat] = []
                timestamp = time.strftime("%Y-%m-%d %H:%M", time.localtime())
                formatted_message = f"You: {msg} ({timestamp})"
                self.user_chats[self.active_chat].append(formatted_message)
                self.display_messages()
                self.server_socket.send(f"{self.active_chat}:{msg}".encode())
                self.message_entry.delete(0, tk.END)
                self.save_user_chats()

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
