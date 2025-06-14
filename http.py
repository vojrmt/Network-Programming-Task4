import os
from glob import glob
from datetime import datetime
from urllib.parse import urlparse, parse_qs

class HttpServer:
    def __init__(self):
        self.types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.txt': 'text/plain',
            '.html': 'text/html',
        }
        self.base_dir = 'files'
        os.makedirs(self.base_dir, exist_ok=True)

    def response(self, kode=200, message='OK', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        response_line = f"HTTP/1.0 {kode} {message}\r\n"
        header_lines = ''.join(f"{k}: {v}\r\n" for k, v in headers.items())
        return (response_line + f"Date: {tanggal}\r\n" +
                "Server: MyHTTPServer/0.1\r\n" +
                header_lines +
                f"Content-Length: {len(messagebody)}\r\n\r\n").encode() + messagebody

    def handle_request(self, data):
        lines = data.split('\r\n')
        method, full_path, _ = lines[0].split()
        parsed = urlparse(full_path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if method == 'GET' and path == '/list':
            return self.list_files()
        elif method == 'DELETE' and path == '/delete':
            filename = query.get('filename', [None])[0]
            return self.delete_file(filename)
        elif method == 'POST' and path == '/upload':
            return self.handle_upload(data)
        else:
            return self.response(404, 'Not Found', b'Not Found')

    def list_files(self):
        file_list = os.listdir(self.base_dir)
        body = str(file_list).encode()
        return self.response(200, 'OK', body, {'Content-Type': 'application/json'})

    def delete_file(self, filename):
        if not filename:
            return self.response(400, 'Bad Request', b'Filename required')
        filepath = os.path.join(self.base_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return self.response(200, 'OK', b'File deleted')
        return self.response(404, 'Not Found', b'File not found')

    def handle_upload(self, data):
        try:
            boundary = data.split('\r\n')[0]
            filename_line = [l for l in data.split('\r\n') if 'filename=' in l][0]
            filename = filename_line.split('filename="')[1].split('"')[0]

            file_content = data.split(boundary)[1]
            file_body = file_content.split('\r\n\r\n', 1)[1].rsplit('\r\n', 2)[0]

            with open(os.path.join(self.base_dir, filename), 'wb') as f:
                f.write(file_body.encode())

            return self.response(200, 'OK', f'Uploaded {filename}'.encode())
        except Exception as e:
            return self.response(500, 'Internal Server Error', f'Error: {e}'.encode())
