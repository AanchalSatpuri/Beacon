#!/usr/bin/env python3
"""
Simple HTTP server to serve the WeWork Chatbot UI
"""

import http.server
import socketserver
import webbrowser
import os
import sys

# Set the port
PORT = 8080

# Change to the directory containing the HTML files
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def start_server():
    """Start the HTTP server"""
    try:
        with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
            print(f"🚀 WeWork Chatbot UI Server starting...")
            print(f"📱 Server running at: http://localhost:{PORT}")
            print(f"💡 Open the above URL in your browser to test the chatbot")
            print(f"🛑 Press Ctrl+C to stop the server")
            print("-" * 50)
            
            # Try to open browser automatically
            try:
                webbrowser.open(f'http://localhost:{PORT}')
                print("🌐 Opening browser automatically...")
            except:
                print("⚠️  Could not open browser automatically")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Port {PORT} is already in use. Try a different port or stop the existing server.")
        else:
            print(f"❌ Error starting server: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    start_server()
