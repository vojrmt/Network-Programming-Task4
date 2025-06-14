import socket
import sys
import os

HOST = '127.0.0.1'
PORT = 8805  # 8806 utk process pool / 8805 utk thread pool

def send_request(request):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(request.encode())
        response = s.recv(1024 * 100).decode()
        print(response)

def list_files():
    request = "GET /list HTTP/1.0\r\n\r\n"
    send_request(request)

def upload_file(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, 'rb') as f:
        file_data = f.read()

    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    content_type = f"multipart/form-data; boundary={boundary}"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    request = (
        f"POST /upload HTTP/1.0\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n\r\n"
    ).encode() + body

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(request)
        response = s.recv(1024 * 100).decode()
        print(response)

def delete_file(filename):
    request = f"DELETE /delete?filename={filename} HTTP/1.0\r\n\r\n"
    send_request(request)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: client.py [list | upload <filepath> | delete <filename>]")
    elif sys.argv[1] == 'list':
        list_files()
    elif sys.argv[1] == 'upload' and len(sys.argv) == 3:
        upload_file(sys.argv[2])
    elif sys.argv[1] == 'delete' and len(sys.argv) == 3:
        delete_file(sys.argv[2])
    else:
        print("Invalid arguments.")
