""" HTTP 1.1 tcp message structure
+-------------------------------------------------------------+
| Request Line:   METHOD PATH HTTP/VERSION\r\n                |
+-------------------------------------------------------------+
| Headers:        Header-Name: Value\r\n                      |
|                 Header-Name: Value\r\n                      |
|                 ...                                         |
+-------------------------------------------------------------+
| Empty Line:     \r\n                                        |
+-------------------------------------------------------------+
| Body (optional):[Content-Length bytes of payload]           |
+-------------------------------------------------------------+
"""



import socket
import threading
host = "127.0.0.1"
port = 5599


def read_request(connection):
    buffer = b''

    while b"\r\n\r\n" not in buffer:
        chunk = connection.recv(4096)
        if not chunk:
            return None #client disconnected
        buffer += chunk

    header_meta_bytes, body_start = buffer.split(b"\r\n\r\n", 1)
    header_meta_text = header_meta_bytes.decode("iso-8859-1")
    lines = header_meta_text.split("\r\n")

    line_1 = lines[0].split()
    if len(line_1)<3:
        return
    method, path, version = line_1[0], line_1[1], line_1[2]

    headers = {}
    for line in lines[1:]:
        if ": " in line:
            key, val = line.split(": ")
            headers[key.lower()] = val.strip()

    # read rest of the body if any
    content_length = int(headers.get("content-length",0))
    body = body_start
    while len(body)<content_length:
        chunk = connection.recv(4096)
        if not chunk:
            break
        body += chunk

    return {
        "method": method,
        "path": path,
        "version": version,
        "headers": headers,
        "body": body,
    }




def handle_client(connection, address):
    with connection:
        print(f"connected with {address}")
        request_count = 0

        while True:
            request = read_request(connection)
            if request is None:
                break

            request_count+=1
            method = request["method"]
            path = request["path"]
            headers = request["headers"]
            body = request["body"]
            
            print(f"Request #{request_count} {method} {path} {address}")

            if path == "/":
                status="200 OK"
                resp_body=f"hello from server, request count on this socket {request_count}"
            elif path == "/echo" and method=='POST':
                status="200 OK"
                resp_body=f"You POSTed: {body.decode('utf-8', errors='replace')}\n"
            elif path == "/headers":
                status = "200 OK"
                resp_body = f"Received headers: {headers}\n"
            else:
                status="404 Not Found"
                resp_body="404 Not Found"
            
            connection_header = headers.get("connection", "").lower()
            should_close = (connection_header == "close")

            resp_bytes = resp_body.encode("utf-8")
            response = (
                f"HTTP/1.1 {status}\r\n"
                f"Content-Type: text/plain; charset=utf-8\r\n"
                f"Content-Length: {len(resp_bytes)}\r\n"
                f"Connection: {'close' if should_close else 'keep-alive'}\r\n"
                f"\r\n"
            ).encode("iso-8859-1") + resp_bytes
            connection.sendall(response)

            if should_close:
                break
            
        print(f"[*] Connection closed for {address}")


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host,port))
        s.listen()
        print(f"listening on {host}:{port}")
        while True:
            connection, address = s.accept()
            t = threading.Thread(target=handle_client, args=(connection, address))
            t.daemon = True
            t.start()

if __name__ == "__main__":
    start_server()
