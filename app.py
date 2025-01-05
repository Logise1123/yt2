import os
import hashlib
import random
import string
from flask import Flask, request, jsonify
from flask_cors import CORS
from moviepy.editor import VideoFileClip
import base64
import io
from PIL import Image

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas las rutas

# Base de datos simulada (en memoria)
users = {}
videos = {}

# Función para generar hashes seguros
def generate_sha256(username, password):
    data = f"{username}:{password}".encode('utf-8')
    return hashlib.sha256(data).hexdigest()

# Función para generar un ID alfanumérico único de 8 caracteres
def generate_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# Función para procesar video y reducir resolución
def process_video(dataurl):
    header, encoded = dataurl.split(',', 1)
    binary_data = base64.b64decode(encoded)
    
    with open("temp_video.mp4", "wb") as f:
        f.write(binary_data)

    clip = VideoFileClip("temp_video.mp4")
    if clip.h > 720:  # Reducción de resolución si es mayor a 720p
        clip = clip.resize(height=720)

    output_path = "processed_video.mp4"
    clip.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None)
    clip.close()

    with open(output_path, "rb") as f:
        processed_binary = f.read()

    os.remove("temp_video.mp4")
    os.remove(output_path)

    processed_dataurl = "data:video/mp4;base64," + base64.b64encode(processed_binary).decode('utf-8')
    return processed_dataurl, clip

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
    token = data.get('token')
    dataurl = data.get('dataurl')
    metadata = data.get('metadata')

    if not token or not dataurl or not metadata:
        return jsonify({"error": "Token, dataurl y metadata son requeridos"}), 400

    # Verificar autenticación
    username = None
    for user, info in users.items():
        if info['token'] == token:
            username = user
            break

    if not username:
        return jsonify({"error": "Token inválido"}), 401

    # Procesar el video
    try:
        processed_dataurl, clip = process_video(dataurl)
    except Exception as e:
        return jsonify({"error": "Error procesando el video", "details": str(e)}), 500

    # Generar un ID único para el video
    video_id = generate_id()

    # Guardar el video y sus metadatos en la base de datos simulada
    videos[video_id] = {
        "username": username,
        "metadata": metadata,
        "dataurl": processed_dataurl
    }

    return jsonify({"message": "Video subido con éxito", "id": video_id}), 201

@app.route('/download', methods=['GET'])
def download():
    video_id = request.args.get('id')

    if not video_id:
        return jsonify({"error": "El ID del video es requerido"}), 400

    if video_id not in videos:
        return jsonify({"error": "Video no encontrado"}), 404

    video = videos[video_id]

    return jsonify({
        "username": video['username'],
        "metadata": video['metadata'],
        "dataurl": video['dataurl']
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
