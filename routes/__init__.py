from .clientes import init_clientes
from .veiculos import init_veiculos
from .funcionarios import init_funcionarios
from .auth import init_auth

def init_routes(app):
    init_auth(app)
    init_clientes(app)
    init_veiculos(app)
    init_funcionarios(app)
