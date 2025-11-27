from flask import Blueprint, render_template, redirect, url_for, flash
from controllers.locacao_controller import LocacaoController # Adicionado

locacao_bp = Blueprint('locacao', __name__)
locacao_controller = LocacaoController() # Adicionado


@locacao_bp.route('/contrato_locacao')
def contrato_locacao():
    return render_template('contrato_locacao.html')


@locacao_bp.route('/historico_locacao')
def historico_locacao():
    return render_template('historico_locacao.html')


@locacao_bp.route('/editar_locacao/<int:id_locacao>')
def editar_locacao(id_locacao):
 
    return render_template("editar_locacao.html", id_locacao=id_locacao)

@locacao_bp.route('/deletar_locacao/<int:id_locacao>')
def deletar_locacao(id_locacao):
    return locacao_controller.deletar_locacao(id_locacao)