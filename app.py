from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.json
        return {"message": "Datos recibidos", "data": data}, 200
    return {"message": "¡Servidor HTTPS funcionando!"}, 200

if __name__ == '__main__':
    app.run()
