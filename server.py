import threading
import socket
from datetime import datetime


PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = {}
clients_lock = threading.Lock()

def get_current_time():
    """Returns the current time formatted as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def handle_client(conn, addr):
    try:
        # Receive username
        username = conn.recv(1024).decode(FORMAT)
        print(f"\r\033[1m[{get_current_time()}] [NEW CONNECTION]\033[0m {addr} with username: \033[1m{username}\033[0m connected.\n\033[1;36m[Server Message]:\033[0m ", end="", flush=True)
        
        with clients_lock:
            clients[conn] = username
        
        # Notify others that a new user has joined
        join_message = f"\033[3m{username} joined the room\033[0m"  # Italicized join message
        broadcast_message(join_message, conn)

        connected = True
        while connected:
            msg = conn.recv(1024).decode(FORMAT)
            if not msg:
                break

            if msg == DISCONNECT_MESSAGE:
                connected = False
                disconnect_message = f"\033[3m{username} has left the chat.\033[0m"
                print(disconnect_message)
                broadcast_message(disconnect_message, conn)
            else:
            # Display client message
                formatted_message = f"[{get_current_time()}] {username}: {msg}             "
                print(f"\r\033[1m{formatted_message}\033[0m\n\033[1;36m[Server Message]:\033[0m ", end="", flush=True)  # Log the message on server terminal
                broadcast_message(formatted_message, conn)

    finally:
        with clients_lock:
            del clients[conn]
        conn.close()

def broadcast_message(message, sender_conn=None):
    """Broadcasts a message to all connected clients except the sender."""
    with clients_lock:
        for c in clients:
            if c != sender_conn: 
                try:
                    c.sendall(message.encode(FORMAT))
                except Exception as e:
                    print(f"[ERROR] Failed to send message to {clients[c]}: {e}")

def server_input():
    while True:
        message = input("\033[1;36m[Server Message]:\033[0m ") 
        if message:  
            broadcast_message(f"\033[1;36m[Server]: {message}        \033[0m")  

def start():
    print('\033[1;32m[SERVER STARTED]!\033[0m')
    server.listen()

    
    threading.Thread(target=server_input, daemon=True).start()

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        
start()
