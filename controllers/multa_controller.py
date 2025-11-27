from flask import render_template, redirect, url_for, flash, session, abort
from models.multa_model import MultaModel


class MultaController:
    def __init__(self):
        self.multa_model = MultaModel()

    # Histórico de multas
    def historico(self):
        if "usuario_logado" not in session or session.get("perfil") not in ["Gerente", "Atendente"]:
            abort(403)

        multas = self.multa_model.listar_historico()
        return render_template("historico_multas.html", multas=multas)
