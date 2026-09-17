from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/api":
            response = {
                "backend": "Backend is working!",
                "database": "Hello from MySQL!"
            }

            data = json.dumps(response).encode()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        else:
            data = b"Hello from Backend!"

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

server = HTTPServer(("0.0.0.0", 5000), Handler)
print("Backend running on port 5000")
server.serve_forever()


