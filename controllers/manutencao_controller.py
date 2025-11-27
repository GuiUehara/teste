from flask import render_template, request, redirect, url_for, flash, session, abort
from models.manutencao_model import ManutencaoModel
from db import conectar 


class ManutencaoController:
    def __init__(self):
        self.manutencao_model = ManutencaoModel()

    # Cadastro de nova manutenção.
    def cadastrar(self):
        if "usuario_logado" not in session or session.get("perfil") not in ["Gerente", "Mecânico"]:
            abort(403)

        if request.method == "POST":
            dados_manutencao = (
                request.form.get("dataEntrada"),
                request.form.get("dataSaida") or None,
                request.form.get("descricaoServico"),
                request.form.get("custo"),
                request.form.get("idVeiculo")
            )

            if not all([dados_manutencao[0], dados_manutencao[2], dados_manutencao[3], dados_manutencao[4]]):
                flash("Preencha todos os campos obrigatórios!", "error")
                return redirect(url_for("manutencao.cadastro_manutencao"))

            if self.manutencao_model.cadastrar(dados_manutencao):
                flash("Manutenção cadastrada com sucesso!", "success")
            else:
                flash("Erro ao cadastrar manutenção.", "error")
            return redirect(url_for("manutencao.cadastro_manutencao"))

        veiculos = self.manutencao_model.listar_veiculos_para_manutencao()
        return render_template("cadastro_manutencao.html", veiculos=veiculos)

    # Histórico de manutenções
    def historico(self):
        if "usuario_logado" not in session or session.get("perfil") not in ["Gerente", "Mecânico"]:
            abort(403)

        manutencoes = self.manutencao_model.listar_historico()
        return render_template("historico_manutencao.html", manutencoes=manutencoes)

    # Atualização do status da manutenção (Em andamento, Concluída)
    def atualizar_status(self, id_manutencao):
        if "usuario_logado" not in session or session.get("perfil") not in ["Gerente", "Mecânico"]:
            abort(403)

        novo_status = request.form.get("status")
        if novo_status not in ["Em andamento", "Concluída"]:
            flash("Status inválido!", "error")
            return redirect(url_for("manutencao.historico_manutencao"))

        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_veiculo FROM manutencao WHERE id_manutencao=%s", (id_manutencao,))
        manut = cursor.fetchone()
        cursor.close()
        conexao.close()

        if not manut:
            flash("Manutenção não encontrada!", "error")
        elif self.manutencao_model.atualizar_status(id_manutencao, novo_status, manut['id_veiculo']):
            flash("Status atualizado com sucesso!", "success")

        return redirect(url_for("manutencao.historico_manutencao"))
