import socket
import requests
import threading
import redis
import db_connection

def handle_client_request(client_socket):
    print("Received request:\n")

    request = b''
    client_socket.setblocking(False) 

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            request += data
        except:
            break

    url = extract_url_from_request(request)

    if url is not None:
        print("The url is", url)
        status_code, response_data = send_request_to_url(url=url)
        if status_code == 200 and response_data is not None:
            data_bytes = response_data.encode('utf-8')
            try:
                print("Try to send data to client after fetching")
                print(data_bytes)
                response = "HTTP/1.1 200 OK\r\nContent-Length: {}\r\n\r\n{}".format(len(data_bytes), data_bytes.decode('utf-8'))
                print(response)
                client_socket.sendall(response.encode('utf-8'))

            except Exception as e:
                print("There is an exception")
                print(e)
            

    client_socket.close()
    print("Received request:\n")

    request = b''

    client_socket.close()
    print("Received request:\n")

    request = b''

def extract_url_from_request(request):
    print(request)
    lines = request.split(b'\r\n')
    if len(lines) < 2 :
        return
    host_info = lines[2].decode('utf-8')[6:]
    print(host_info)
    return host_info

def send_request_to_url(url):
    try:
        response = requests.get(url)
        print("Received response from URL:", response)
        if response.status_code == 200:  
            return response.status_code, response.text  
        else:
            print("Error: Status code", response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print("Error sending request to URL:", e)
        return None

def start_proxy_server():

    port = 8888

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind(('127.0.0.1', port))

    server.listen(10)
    redis_connection = db_connection.db_connection()

    print(f"Proxy server listening on port {port}...")

    while True:

        client_socket, addr = server.accept()

        print(f"Accepted connection from {addr[0]}:{addr[1]}")

        client_handler = threading.Thread(target=handle_client_request, args=(client_socket,))

        client_handler.start()

if __name__ == "__main__":

    start_proxy_server()

