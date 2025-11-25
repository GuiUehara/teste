from flask import Blueprint
from controllers.locacao_controller import LocacaoController

locacao_api = Blueprint("locacao_api", __name__)
controller = LocacaoController()

# CRIAR LOCAÇÃO


@locacao_api.route('/api/locacao', methods=['POST'])
def criar_locacao():
    return controller.criar_locacao()


# buscar locação para editar_locacao.html
@locacao_api.route("/api/locacao/<int:id_locacao>")
def get_locacao(id_locacao):
    return controller.get_locacao(id_locacao)


@locacao_api.route('/api/locacao/<int:id_loc>', methods=['PUT'])
def atualizar_locacao(id_loc):
    return controller.atualizar_locacao(id_loc)


# --- Buscar clientes por nome ou CPF (autocomplete) ---
@locacao_api.route('/api/clientes', methods=['GET'])
def buscar_clientes():
    return controller.buscar_clientes()

# --- Listar categorias usando função do api_veiculos.py ---


@locacao_api.route('/api/categorias', methods=['GET'])
def listar_categorias():
    return controller.listar_categorias()

# --- Listar veículos por categoria ---


@locacao_api.route('/api/veiculos', methods=['GET'])
def listar_veiculos():
    return controller.listar_veiculos()

# --- Buscar um veículo específico (quilometragem para preencher KM de saída) ---


@locacao_api.route('/api/veiculo/<int:id_veiculo>', methods=['GET'])
def get_veiculo(id_veiculo):
    return controller.get_veiculo(id_veiculo)

# --- Listar opcionais disponíveis ---


@locacao_api.route('/api/opcionais', methods=['GET'])
def listar_opcionais():
    return controller.listar_opcionais()

# --- Rota para valor previsto em tempo real ---


@locacao_api.route('/api/valor-previsto', methods=['POST'])
def valor_previsto():
    return controller.valor_previsto()


@locacao_api.route('/api/historico-locacao', methods=['GET'])
def listar_historico_locacao():
    return controller.listar_historico_locacao()

# Rota para SIMULAR o cálculo do VALOR FINAL em tempo real


@locacao_api.route("/api/locacao/calcular_final/<int:id_loc>", methods=["POST"])
def calcular_simulacao(id_loc):
    return controller.calcular_simulacao(id_loc)
