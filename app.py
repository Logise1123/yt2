import os
import hashlib
import random
import string
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Base de datos simulada (en memoria)
users = {}
files = {}

def generate_sha256(username, password):
    data = f"{username}:{password}".encode('utf-8')
    return hashlib.sha256(data).hexdigest()

def generate_random_id(length=8):
    """Genera un ID aleatorio alfanumérico de 8 caracteres."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

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

@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    data_url = data.get('dataurl')

    if not data_url:
        return jsonify({"error": "Data URL es requerido"}), 400

    # Verificar que el Data URL sea válido (tiene formato de imagen por ejemplo)
    if not data_url.startswith('data:'):
        return jsonify({"error": "El Data URL no tiene formato válido"}), 400

    # Generar un ID único para el archivo
    file_id = generate_random_id()

    # Guardar el archivo con su ID
    files[file_id] = data_url

    return jsonify({"message": "Archivo subido con éxito", "id": file_id}), 201

@app.route('/download', methods=['GET'])
def download():
    file_id = request.args.get('id')

    if not file_id:
        return jsonify({"error": "ID de archivo es requerido"}), 400

    if file_id not in files:
        return jsonify({"error": "Archivo no encontrado"}), 404

    return jsonify({"dataurl": files[file_id]}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
