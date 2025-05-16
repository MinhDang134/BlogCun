from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from datetime import datetime

VERSIONS_DIR = 'versions'

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api.php':
            try:
                # Lấy phiên bản mới nhất từ thư mục versions
                files = [f for f in os.listdir(VERSIONS_DIR) if f.startswith('database') and f.endswith('.json')]
                if not files:
                    # Nếu không có file nào, tạo file mới
                    latest_file = os.path.join(VERSIONS_DIR, 'database.json')
                    os.makedirs(VERSIONS_DIR, exist_ok=True)
                    with open(latest_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            "profile": {
                                "name": "Cún",
                                "nickname": "Cún cute 😊",
                                "about": "Mình là một người yêu thích công nghệ và sáng tạo. Mình thích khám phá những điều mới mẻ, đọc sách và nghe nhạc. Mình luôn cố gắng sống tích cực và lan tỏa năng lượng tốt đến mọi người xung quanh.",
                                "slogan": "\"Hãy sống như một bông hoa, tỏa hương thơm ngát cho đời 🌸\""
                            }
                        }, f, ensure_ascii=False, indent=4)
                else:
                    # Lấy file mới nhất
                    latest_file = os.path.join(VERSIONS_DIR, max(files, key=lambda x: os.path.getctime(os.path.join(VERSIONS_DIR, x))))
                
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_POST(self):
        if self.path == '/api.php':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                # Tạo tên file mới dựa trên thời gian
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_file = os.path.join(VERSIONS_DIR, f'database_{timestamp}.json')
                
                # Đảm bảo thư mục versions tồn tại
                os.makedirs(VERSIONS_DIR, exist_ok=True)
                
                # Thêm thời gian vào dữ liệu
                data['saved_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Lưu dữ liệu vào file mới
                with open(new_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    server_address = ('', 8082)
    httpd = HTTPServer(server_address, APIHandler)
    print('Server running on port 8082...')
    httpd.serve_forever() 