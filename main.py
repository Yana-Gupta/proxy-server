import socket
import requests
import threading
import db_connection
import utils
import ssl
import asyncio

def handle_client_request(client_socket, redis):
    print("Received request:\n")

    request = b''
    client_socket.setblocking(False) 
    data = None
    
    while data == None:
        try:
            data = client_socket.recv(1024)
            request += data
            print(data)
        except:
            continue
    
    url = extract_url_from_request(request)
    status, url = utils.validate_and_sanitize_url(url=url)
    
    if ( status == 400 ):
        response = response = "HTTP/1.1 404 Bad Request\r\nContent-Length: 0\r\n\r\n"
        client_socket.sendall(response.encode('utf-8'))
        client_socket.close()
        return
    
    if utils.is_url_blocked(redis_connection=redis, url=url):
        response = response = "HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n"
        client_socket.sendall(response.encode('utf-8'))
        client_socket.close()
        return
        
    if url is not None and redis.exists(url):
        value = redis.get(url)
        try:
            print("Try to send data to client after fetching redis here")
            response = "HTTP/1.1 200 OK\r\nContent-Length: {}\r\n\r\n{}".format(len(value), value)
            client_socket.sendall(response.encode('utf-8'))
        except Exception as e:
            print("There is an exception")
            print(e)

    else:
        if url is not None:
            print("The url is", url)
            status_code, response_data = send_request_to_url(url=url)
            if status_code == 200 and response_data is not None:
                if utils.filter_content(redis_connection=redis, content=response_data):
                    data_bytes = response_data.encode('utf-8')
                    redis.setex(url, 21600, data_bytes)
                    try:
                        response = "HTTP/1.1 200 OK\r\nContent-Length: {}\r\n\r\n{}".format(len(data_bytes), data_bytes.decode('utf-8'))
                        client_socket.sendall(response.encode('utf-8'))
                    except Exception as e:
                        print("There is an exception")
                        print(e)
                else:
                    redis.sadd(utils.BLOCKED_URLS, url)
                    response = response = "HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n"
                    client_socket.sendall(response.encode('utf-8'))
            else:
                response = response = "HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n"
                client_socket.sendall(response.encode('utf-8'))  
    client_socket.close()


def extract_url_from_request(request):
    lines = request.split(b'\r\n')
    if len(lines) < 2 :
        return
    host_info = lines[2].decode('utf-8')[6:]
    return host_info


def send_request_to_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:  
            return response.status_code, response.text  
        else:
            return 404, None
    except requests.exceptions.RequestException as e:
        return 404, None

def start_proxy_server():
    port = 8001

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', port))
    server.listen(10)
    redis_connection = db_connection.db_connection()

    print(f"Proxy server listening on port {port}...")

    # Create SSL context
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile="server.crt", keyfile="server.key")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr[0]}:{addr[1]}")

        ssl_client_socket = ssl_context.wrap_socket(client_socket, server_side=True)

        client_handler = threading.Thread(target=handle_client_request, args=(ssl_client_socket, redis_connection))
        client_handler.start()

if __name__ == "__main__":

    start_proxy_server()

