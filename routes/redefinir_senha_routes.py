from flask import Blueprint
from controllers.redefinir_senha_controller import RedefinirSenhaController

redefinir_senha_bp = Blueprint('redefinir_senha', __name__)
controller = RedefinirSenhaController()


@redefinir_senha_bp.route('/solicitar_redefinir', methods=['GET', 'POST'])
def solicitar_redefinir():
    return controller.solicitar()


@redefinir_senha_bp.route('/resetar_senha/<token>', methods=['GET', 'POST'])
def resetar_senha(token):
    return controller.resetar(token)
