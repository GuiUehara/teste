from flask import Blueprint
from controllers.multa_controller import MultaController

multa_bp = Blueprint('multas', __name__)
controller = MultaController()


@multa_bp.route("/historico_multas")
def historico_multas():
    return controller.historico()
