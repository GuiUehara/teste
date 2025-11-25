from flask import Blueprint
from controllers.cliente_controller import ClienteController

cliente_bp = Blueprint('clientes', __name__)
cliente_controller = ClienteController()


@cliente_bp.route("/cadastro_cliente", methods=["GET", "POST"])
def cadastro_cliente():
    return cliente_controller.cadastrar()


@cliente_bp.route("/lista_clientes")
def lista_clientes():
    return cliente_controller.listar()


@cliente_bp.route("/editar_cliente/<int:id_cliente>", methods=["GET", "POST"])
def editar_cliente(id_cliente):
    return cliente_controller.editar(id_cliente)


@cliente_bp.route("/deletar_cliente/<int:id_cliente>", methods=["POST", "GET"])
def deletar_cliente(id_cliente):
    return cliente_controller.deletar(id_cliente)
