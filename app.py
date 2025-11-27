from flask import Flask, redirect, url_for, render_template, session, jsonify
from flask_login import LoginManager, UserMixin
from routes import (auth_routes, cliente_routes, veiculo_routes, funcionario_routes, redefinir_senha_routes, manutencao_routes, reserva,
                    multa_routes, locacao_routes, pagamento_routes, api_cep, api_locacao, api_veiculos, api_utils, institucional_routes)
from dotenv import load_dotenv
import os
# Importa a função de conexão com o banco de dados
from db import conectar

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

app = Flask(__name__)

# --- Configurações do App ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['TOKEN_SECRET_KEY'] = os.environ.get('TOKEN_SECRET_KEY')
app.config['TOKEN_SALT'] = os.environ.get('TOKEN_SALT')

# --- Classe de Usuário para o Flask-Login ---


class User(UserMixin):
    def __init__(self, id, email, user_type):
        self.id = id
        self.email = email
        # Garante que o user_type seja capitalizado para consistência (ex: 'gerente' -> 'Gerente')
        if user_type:
            self.user_type = user_type.strip().capitalize()
        else:
            self.user_type = None


# --- Configuração do Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
# Página para redirecionar se não estiver logado
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    """Carrega o usuário do banco de dados a partir do ID da sessão."""
    with conectar() as conn:
        with conn.cursor(dictionary=True) as cursor:
            # Correção: A coluna se chama 'id_usuario', não 'id'.
            cursor.execute(
                "SELECT id_usuario, email, perfil FROM usuario WHERE id_usuario = %s", (user_id,))
            user_data = cursor.fetchone()
            if user_data:
                return User(id=user_data['id_usuario'], email=user_data['email'], user_type=user_data['perfil'])
    return None
# ------------------------------------


# Registra as rotas e os Blueprints no aplicativo
app.register_blueprint(auth_routes.auth_bp)
app.register_blueprint(cliente_routes.cliente_bp)
app.register_blueprint(veiculo_routes.veiculo_bp)
app.register_blueprint(funcionario_routes.funcionario_bp)
app.register_blueprint(reserva.reserva_bp)
app.register_blueprint(redefinir_senha_routes.redefinir_senha_bp)
app.register_blueprint(manutencao_routes.manutencao_bp)
app.register_blueprint(multa_routes.multa_bp)
app.register_blueprint(locacao_routes.locacao_bp)
app.register_blueprint(pagamento_routes.pagamento_bp)
app.register_blueprint(api_cep.cep_api)
app.register_blueprint(api_locacao.locacao_api)
# Registra as rotas de /api/modelos
app.register_blueprint(api_veiculos.veiculos_api)
app.register_blueprint(institucional_routes.institucional_bp)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
