import socket

def handle_request(client_socket):
    request = client_socket.recv(1024)
    if not request:
        return
    request = request.decode("utf-8")
    print(f"Received request:\n{request}")

    response = "HTTP/1.1 200 OK\r\nContent-Length: 12\r\n\r\nHello World!"
    client_socket.sendall(response.encode("utf-8"))

def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 8000))
    server.listen(5)
    print("Server listening on port 8000...")

    while True:
        client_socket, _ = server.accept()
        handle_request(client_socket)
        client_socket.close()

    server.close()

if __name__ == "__main__":
    run_server()
