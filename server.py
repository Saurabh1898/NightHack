import socket
import threading
import sqlite3

# Server configuration
HOST = 'localhost'
PORT = 8000

# Database configuration
DB_FILE = 'chat.db'

# List of connected clients
clients = []

# Chatrooms dictionary to track chatrooms and users
chatrooms = {}

# Thread function to handle client connections
def handle_client(client_socket, db_conn):
    while True:
        try:
            # Receive message from client
            message = client_socket.recv(1024).decode()
            if message:
                process_message(message, client_socket)
        except:
            # Remove disconnected client
            if client_socket in clients:
                clients.remove(client_socket)
                remove_client_from_chatroom(client_socket)
            break

# Process message from client
def process_message(message, client_socket):
    if message.startswith("SAVE_CHAT:"):
        save_chatroom_history(client_socket)
    else:
        broadcast(message, client_socket)

# Broadcast message to all clients except the sender
def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode())
            except:
                # Remove disconnected client
                if client in clients:
                    clients.remove(client)
                    remove_client_from_chatroom(client)

# Remove client from chatroom
def remove_client_from_chatroom(client_socket):
    for chatroom_id, chatroom in chatrooms.items():
        if client_socket in chatroom['users']:
            chatroom['users'].remove(client_socket)
            if len(chatroom['users']) == 0:
                # If no users left in the chatroom, remove it
                del chatrooms[chatroom_id]

# Save chatroom history to database
def save_chatroom_history(client_socket):
    chatroom_id = get_chatroom_id(client_socket)
    if chatroom_id is not None:
        chatroom = chatrooms[chatroom_id]
        chatroom['votes'] = chatroom.get('votes', [])
        chatroom['votes'].append(client_socket)
        if len(chatroom['votes']) == 2:
            chatroom['history'] = chatroom.get('history', [])
            chatroom['history'].extend(chatroom['messages'])
            chatroom['messages'] = []
            notify_clients("Chat saved.", chatroom['users'])
            save_chat_to_db(chatroom_id, chatroom['history'])
        else:
            notify_clients("Waiting for the other user to vote.", chatroom['users'])

# Save chat to the database
def save_chat_to_db(chatroom_id, chat_history):
    db_conn.execute("INSERT INTO chat_history (chatroom_id, history) VALUES (?, ?)", (chatroom_id, chat_history))
    db_conn.commit()

# Notify clients with a message
def notify_clients(message, user_sockets):
    for user_socket in user_sockets:
        user_socket.send(message.encode())

# Get the chatroom ID for a given client socket
def get_chatroom_id(client_socket):
    for chatroom_id, chatroom in chatrooms.items():
        if client_socket in chatroom['users']:
            return chatroom_id
    return None

# Create chat history table in the database
def create_chat_history_table():
    db_conn.execute("CREATE TABLE IF NOT EXISTS chat_history (id INTEGER PRIMARY KEY AUTOINCREMENT, chatroom_id INTEGER, history TEXT)")
    db_conn.commit()

# Main server function
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    print(f"Server started on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()

        clients.append(client_socket)

        print(f"Client connected: {client_address}")

        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

# Start the server
if __name__ == '__main__':
    # Create or connect to the database
    db_conn = sqlite3.connect(DB_FILE)
    create_chat_history_table()

    try:
        start_server()
    finally:
        # Close the database connection
        db_conn.close()
