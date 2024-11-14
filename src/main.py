from http.server import HTTPServer, BaseHTTPRequestHandler
import json

data = {
    "data": {
        "name": "jack"
    }
}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        # Check root and prepare response
        if self.path == '/':
            response = data
        else:
            response = {"error": "Route not found"}
            self.send_response(404)
        
        # Send response
        self.wfile.write(json.dumps(response).encode())

server = HTTPServer(('', 80), Handler)
server.serve_forever()