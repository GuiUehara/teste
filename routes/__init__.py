from .clientes import init_clientes
from .veiculos import init_veiculos
from .funcionarios import init_funcionarios
from .auth import init_auth
from .redefinir_senha import init_redefinirSenha
from .pagamento import init_pagamento
from .manutencao import init_manutencao
from .multas import init_multa
from .contrato_locacao import init_locacao
from .api_cep import cep_api
from .teste import init_teste
from .api_veiculos import veiculos_api
from .api_locacao import locacao_api
from .reserva import init_reserva


def init_routes(app):
    init_auth(app)
    init_clientes(app)
    init_veiculos(app)
    init_funcionarios(app)
    init_redefinirSenha(app)
    init_pagamento(app)
    init_manutencao(app)
    init_multa(app)
    init_locacao(app)
    init_teste(app)
    app.register_blueprint(cep_api)
    app.register_blueprint(veiculos_api)
    app.register_blueprint(locacao_api)
    init_reserva(app)
