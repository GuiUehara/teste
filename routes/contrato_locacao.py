from flask import Flask, request, jsonify, render_template
from db import conectar
from datetime import datetime
import math

# Valor padrão de multa por fração de combustível, caso não exista no veículo
VALOR_MULTA_COMBUSTIVEL_PADRAO = 50.00 

def init_locacao(app):
    # --- Páginas HTML ---
    @app.route('/contrato_locacao')
    def contrato_locacao():
        return render_template('contrato_locacao.html')

    @app.route('/historico_locacao')
    def historico_locacao():
        return render_template('historico_locacao.html')

    # --- APIs de suporte ---
  