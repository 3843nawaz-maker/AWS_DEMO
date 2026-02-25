import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer

# Initialize database
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
conn.commit()

class MyServer(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        # Allowed methods updated to include PUT and DELETE
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    # READ (Get all users)
    def do_GET(self):
        if self.path == "/users":
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(rows).encode())

    # CREATE (Add a new user)
    def do_POST(self):
        if self.path == "/add":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            name = data.get("name", "").strip()
            if name:
                cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
                conn.commit()
                self.send_response(200)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(b"User added successfully")
            else:
                self.send_response(400)
                self._send_cors_headers()
                self.end_headers()

    # UPDATE (Edit an existing user)
    def do_PUT(self):
        if self.path == "/update":
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            data = json.loads(put_data)

            user_id = data.get("id")
            new_name = data.get("name", "").strip()

            if user_id and new_name:
                cursor.execute("UPDATE users SET name = ? WHERE id = ?", (new_name, user_id))
                conn.commit()
                self.send_response(200)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(b"User updated successfully")
            else:
                self.send_response(400)
                self._send_cors_headers()
                self.end_headers()

    # DELETE (Remove a user)
    def do_DELETE(self):
        if self.path == "/delete":
            content_length = int(self.headers['Content-Length'])
            delete_data = self.rfile.read(content_length)
            data = json.loads(delete_data)

            user_id = data.get("id")

            if user_id:
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                self.send_response(200)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(b"User deleted successfully")
            else:
                self.send_response(400)
                self._send_cors_headers()
                self.end_headers()

server = HTTPServer(("0.0.0.0", 5000), MyServer)
print("Server started on port 5000. Full CRUD enabled!")
server.serve_forever()