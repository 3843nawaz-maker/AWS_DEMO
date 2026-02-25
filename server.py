import json
import pymysql
from http.server import BaseHTTPRequestHandler, HTTPServer

DB_HOST = "database-1.cdi6kisa8159.ap-southeast-2.rds.amazonaws.com" 
DB_USER = "admin"
DB_PASSWORD = "nawaz3843"  
DB_NAME = "assignment_db" 

def get_db_connection():
    temp_conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD)
    temp_cursor = temp_conn.cursor()
    temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    temp_conn.commit()
    temp_conn.close()

    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255))")
    conn.commit()
    return conn

class MyServer(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/users":
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            conn.close()
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(rows).encode())

    def do_POST(self):
        if self.path == "/add":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            name = data.get("name", "").strip()

            if name:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (name) VALUES (%s)", (name,))  
                conn.commit()
                conn.close()
                self.send_response(200)
            else:
                self.send_response(400)
            
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(b"User added")

    def do_PUT(self):
        if self.path == "/update":
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            data = json.loads(put_data)
            user_id = data.get("id")
            new_name = data.get("name", "").strip()

            if user_id and new_name:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET name = %s WHERE id = %s", (new_name, user_id))
                conn.commit()
                conn.close()
                self.send_response(200)
            else:
                self.send_response(400)
                
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(b"User updated")

    def do_DELETE(self):
        if self.path == "/delete":
            content_length = int(self.headers['Content-Length'])
            delete_data = self.rfile.read(content_length)
            data = json.loads(delete_data)
            user_id = data.get("id")

            if user_id:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                conn.commit()
                conn.close()
                self.send_response(200)
            else:
                self.send_response(400)
                
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(b"User deleted")

server = HTTPServer(("0.0.0.0", 5000), MyServer)
print("Server started on port 5000. Connected to AWS RDS!")
server.serve_forever()
