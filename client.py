import socket
import threading

# Server configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 8000

# Thread function to handle receiving messages from the server
def receive_messages(client_socket):
    while True:
        try:
            # Receive message from server
            message = client_socket.recv(1024).decode()
            print(message)
        except:
            # Unable to receive message, likely disconnected from the server
            print("Disconnected from the server.")
            break

# Main client function
def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Send messages to the server
    while True:
        message = input()
        if message.lower() == 'exit':
            break
        client_socket.send(message.encode())

    # Close the client socket
    client_socket.close()

# Start the client
if __name__ == '__main__':
    start_client()
