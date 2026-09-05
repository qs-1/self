import socket
import threading
host = "127.0.0.1"
port = 5599


def handle_client(connection, address):
    with connection:
        print(f"connected with {address}")
        data = connection.recv(4069)
        if not data:
            return
        method, path, version = data.decode("utf-8").split("\r\n")[0].split()
        print(f"{method} {path} {address}")

        if path == "/":
            status="200 OK"
            body="hello from server"
        elif path == "/testing":
            status="200 OK"
            body="tested"
        else:
            status="404 Not Found"
            body="404 Not Found"
        
        response = (
            f"HTTP/1.1 {status}\r\n"
            f"content-type: text/plain\r\n"
            f"content-length: {len(body.encode())}\r\n"
            f"connection: close\r\n"
            f"\r\n"
            f"{body}"
        )

        connection.sendall(response.encode())


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host,port))
    s.listen()
    print(f"listening on {host}:{port}")
    while True:
        connection, address = s.accept()
        threading.Thread(target=handle_client, args=(connection,address)).start()