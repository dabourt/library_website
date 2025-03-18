from flask import Flask, request, jsonify
import json
import os
from functools import wraps

app = Flask(__name__)

BOOKS_FILE = "books.json"
USERS_FILE = "users.json"
DATA_DIR = "/var/lib_db"

AUTH_USERNAME = os.getenv("LIB_DB_USERNAME")
AUTH_PASSWORD = os.getenv("LIB_DB_PASSWORD")

# Ensure the JSON files exist
for file in [BOOKS_FILE, USERS_FILE]:
    file_path = os.path.join(DATA_DIR, file)
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump({"data": []}, f)

def read_data(file):
    with open(file, "r") as f:
        return json.load(f)

def write_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or not (auth.username == AUTH_USERNAME and auth.password == AUTH_PASSWORD):
            return jsonify({"message": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route("/books", methods=["GET"])
@authenticate
def get_books():
    return jsonify(read_data(os.path.join(DATA_DIR, BOOKS_FILE)))

@app.route("/books", methods=["POST"])
@authenticate
def add_book():
    new_entry = request.json
    data = read_data(os.path.join(DATA_DIR, BOOKS_FILE))
    data["data"].append(new_entry)
    write_data(os.path.join(DATA_DIR, BOOKS_FILE), data)
    return jsonify(data)

@app.route("/users", methods=["GET"])
@authenticate
def get_users():
    return jsonify(read_data(os.path.join(DATA_DIR, USERS_FILE)))

@app.route("/users", methods=["POST"])
@authenticate
def add_user():
    new_entry = request.json
    data = read_data(os.path.join(DATA_DIR, USERS_FILE))
    data["data"].append(new_entry)
    write_data(os.path.join(DATA_DIR, USERS_FILE), data)
    return jsonify(data)

@app.route("/data/<filename>", methods=["GET", "POST"])
@authenticate
def handle_data(filename):
    if filename not in [BOOKS_FILE, USERS_FILE]:
        return jsonify({"error": "Invalid file name"}), 400

    file_path = os.path.join(DATA_DIR, filename)

    if request.method == "GET":
        return jsonify(read_data(file_path))
    elif request.method == "POST":
        data = request.json
        write_data(file_path, data)
        return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)