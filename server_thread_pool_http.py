import socket
from concurrent.futures import ThreadPoolExecutor
from http import HttpServer

server = HttpServer()
HOST = '0.0.0.0'
PORT = 8805

def handle_client(conn, addr):
    try:
        data = conn.recv(1024 * 100).decode()
        if data:
            response = server.handle_request(data)
            conn.sendall(response)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(100)
    print(f"ThreadPool HTTP server running on port {PORT}")

    with ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            conn, addr = s.accept()
            executor.submit(handle_client, conn, addr)
