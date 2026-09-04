import socket
host = "127.0.0.1"
port = 5599

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host,port))
    s.listen()
    connection, address = s.accept()
    with connection:
        print(f"connected with {address}")
        while True:
            data = connection.recv(1024)
            if not data:
                break
            connection.sendall(data)