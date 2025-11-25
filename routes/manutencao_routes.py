from flask import Blueprint
from controllers.manutencao_controller import ManutencaoController

manutencao_bp = Blueprint('manutencao', __name__)
controller = ManutencaoController()


@manutencao_bp.route("/cadastro_manutencao", methods=["GET", "POST"])
def cadastro_manutencao():
    return controller.cadastrar()


@manutencao_bp.route("/historico_manutencao")
def historico_manutencao():
    return controller.historico()


@manutencao_bp.route("/atualizar_status_manutencao/<int:id_manutencao>", methods=["POST"])
def atualizar_status_manutencao(id_manutencao):
    return controller.atualizar_status(id_manutencao)
