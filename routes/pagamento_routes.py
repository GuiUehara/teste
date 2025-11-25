from flask import Blueprint, render_template
from controllers.pagamento_controller import PagamentoController

pagamento_bp = Blueprint('pagamento', __name__)
controller = PagamentoController()


@pagamento_bp.route("/pagamento", methods=["GET", "POST"])
def pagamento():
    return controller.processar()


@pagamento_bp.route("/pagamento/concluido")
def pagamento_concluido():
    return render_template("pagamento_concluido.html")
