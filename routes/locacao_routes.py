from flask import Blueprint, render_template

locacao_bp = Blueprint('locacao', __name__)


@locacao_bp.route('/contrato_locacao')
def contrato_locacao():
    return render_template('contrato_locacao.html')


@locacao_bp.route('/historico_locacao')
def historico_locacao():
    return render_template('historico_locacao.html')


@locacao_bp.route('/editar_locacao/<int:id_locacao>')
def editar_locacao(id_locacao):
    # Apenas renderiza a página, o JavaScript fará o resto
    return render_template("editar_locacao.html", id_locacao=id_locacao)
