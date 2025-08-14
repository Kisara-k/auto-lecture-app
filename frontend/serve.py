#!/usr/bin/env python3
"""
Simple HTTP server to serve the frontend files.
This is for development/testing purposes only.
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 3000
DIRECTORY = Path(__file__).parent

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with CORS headers for local development"""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def main():
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"🌐 Frontend server starting on http://localhost:{PORT}")
        print(f"📁 Serving files from: {DIRECTORY}")
        print(f"🎓 Auto Lecture App frontend available at: http://localhost:{PORT}")
        print(f"📚 Make sure the backend is running on http://localhost:8000")
        print(f"\n🔧 To stop the server, press Ctrl+C")
        
        # Try to open the browser automatically
        try:
            webbrowser.open(f'http://localhost:{PORT}')
            print(f"🌍 Browser opened automatically")
        except Exception:
            print(f"🌍 Please open http://localhost:{PORT} in your browser")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n👋 Frontend server stopped")

if __name__ == "__main__":
    main()
