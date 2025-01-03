import os
import hashlib
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Base de datos simulada (en memoria)
users = {}

def generate_sha256(username, password):
    data = f"{username}:{password}".encode('utf-8')
    return hashlib.sha256(data).hexdigest()

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Hola :)"})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username y password son requeridos"}), 400

    if username in users:
        return jsonify({"error": "El usuario ya existe"}), 400

    token = generate_sha256(username, password)
    users[username] = {"password": password, "token": token}

    return jsonify({"message": "Usuario registrado con éxito", "token": token}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username y password son requeridos"}), 400

    if username not in users or users[username]['password'] != password:
        return jsonify({"error": "Credenciales inválidas"}), 401

    return jsonify({"message": "Inicio de sesión exitoso", "token": users[username]['token']}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
