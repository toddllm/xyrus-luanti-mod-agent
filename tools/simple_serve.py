#!/usr/bin/env python3
import http.server
import socketserver

PORT = 8080

class SimpleMarkdownHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            
            with open('/home/tdeshane/luanti/server_status_report.md', 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

with socketserver.TCPServer(("", PORT), SimpleMarkdownHandler) as httpd:
    print(f"Serving markdown at http://0.0.0.0:{PORT}/")
    httpd.serve_forever()