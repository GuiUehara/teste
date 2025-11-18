from flask import Flask, request, jsonify, render_template, abort
from db import conectar
from datetime import datetime
import math


# Definição das colunas da tabela locacao para referência
COLUNAS_LOCACAO = [
    'id_locacao', 'data_retirada', 'data_devolucao_prevista', 'data_devolucao_real',
    'valor_total_previsto', 'valor_final', 'quilometragem_retirada', 
    'quilometragem_devolucao', 'id_cliente', 'id_veiculo', 'id_funcionario', 
    'status', 'tanque_saida', 'tanque_chegada', 'caucao', 'devolucao'
]

def init_locacao(app):
    # --- Páginas HTML (rotas existentes) ---
    @app.route('/contrato_locacao')
    def contrato_locacao():
        return render_template('contrato_locacao.html')

    @app.route('/historico_locacao')
    def historico_locacao():
        return render_template('historico_locacao.html')
    
    @app.route('/editar_locacao.html')
    def editar_locacao_html():
        return render_template("editar_locacao.html")