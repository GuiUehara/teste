from flask import Blueprint
from controllers.funcionario_controller import FuncionarioController

funcionario_bp = Blueprint('funcionarios', __name__)
funcionario_controller = FuncionarioController()


@funcionario_bp.route("/cadastro_funcionario", methods=["GET", "POST"])
def cadastro_funcionario():
    return funcionario_controller.cadastrar()


@funcionario_bp.route("/lista_funcionarios")
def lista_funcionarios():
    return funcionario_controller.listar()


@funcionario_bp.route("/editar_funcionario/<int:id_usuario>", methods=["GET", "POST"])
def editar_funcionario(id_usuario):
    return funcionario_controller.editar(id_usuario)


@funcionario_bp.route("/deletar_funcionario/<int:id_usuario>")
def deletar_funcionario(id_usuario):
    return funcionario_controller.deletar(id_usuario)
