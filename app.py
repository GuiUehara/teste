
from flask import Flask, redirect, url_for
from routes import init_routes

app = Flask(__name__)
app.secret_key = "chave-secreta"
app.config['SECRET_KEY'] = 'uma_chave_secreta_segura_aqui'
app.config['SENHA_SECRETA'] = 'chave_secreta_para_token'
app.config['SENHA_SALT'] = 'salt'
app.config['TESTE'] = 'teste'

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
mecanicos = [
    {
        "email": "mecanico@empresa.com",
        "senha": "1234",
        "perfil": "mecanico",
    }
]

init_routes(app)

@app.route('/')
def index():
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
