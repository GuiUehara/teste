from flask import Flask, redirect, url_for
from routes import init_routes

app = Flask(__name__)
app.secret_key = "chave-secreta"

clientes = []
veiculos = []
usuarios = {
    "admin@empresa.com": {"senha": "1234", "perfil": "gerente"}
}
atendentes = [
    {
        "email": "funcionario@empresa.com",
        "senha": "1234",
        "perfil": "atendente",
    }
]

atendentes_inf = []


init_routes(app)

@app.route('/')
def index():
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
