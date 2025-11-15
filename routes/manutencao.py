from flask import render_template, request, redirect, url_for, flash, session, abort
from db import conectar

def init_manutencao(app):

    # --- Cadastro de manutenção ---
    @app.route("/cadastro_manutencao", methods=["GET", "POST"])
    def cadastro_manutencao():
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))

        if session.get("perfil") not in ["Gerente", "Mecânico"]:
            abort(403)

        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        if request.method == "POST":
            data_entrada = request.form.get("dataEntrada")
            data_saida = request.form.get("dataSaida") or None
            descricao = request.form.get("descricaoServico")
            custo = request.form.get("custo")
            id_veiculo = request.form.get("idVeiculo")
            seguro = request.form.get("seguro") or None   # novo campo

            if not all([data_entrada, descricao, custo, id_veiculo]):
                flash("Preencha todos os campos obrigatórios!", "error")
                return redirect(url_for("cadastro_manutencao"))

            cursor.execute("""
                INSERT INTO manutencao
                (data_entrada, data_saida, seguro, descricao_servico, custo, id_veiculo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (data_entrada, data_saida, seguro, descricao, custo, id_veiculo))

            # Atualiza status do veículo para 3 = "Em Manutenção"
            cursor.execute("""
                UPDATE veiculo SET id_status_veiculo = 3 WHERE id_veiculo = %s
            """, (id_veiculo,))

            conexao.commit()
            flash("Manutenção cadastrada com sucesso!", "success")
            return redirect(url_for("cadastro_manutencao"))

        # Lista veículos disponíveis (status 1 = Disponível) para seleção
        cursor.execute("SELECT id_veiculo, placa FROM veiculo WHERE id_status_veiculo = 1")
        veiculos = cursor.fetchall()

        cursor.close()
        conexao.close()

        return render_template("cadastro_manutencao.html", veiculos=veiculos)

    # --- Histórico de manutenção ---
    @app.route("/historico_manutencao")
    def historico_manutencao():
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))

        if session.get("perfil") not in ["Gerente", "Mecânico"]:
            abort(403)

        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT m.id_manutencao, m.data_entrada, m.data_saida, m.seguro, m.descricao_servico,
                   m.custo, m.status, v.placa, mo.nome_modelo
            FROM manutencao m
            JOIN veiculo v ON m.id_veiculo = v.id_veiculo
            JOIN modelo mo ON v.id_modelo = mo.id_modelo
            ORDER BY m.data_entrada DESC
        """)
        manutencoes = cursor.fetchall()

        cursor.close()
        conexao.close()

        return render_template("historico_manutencao.html", manutencoes=manutencoes)

    @app.route("/atualizar_status_manutencao/<int:id_manutencao>", methods=["POST"])
    def atualizar_status_manutencao(id_manutencao):
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))

        if session.get("perfil") not in ["Gerente", "Mecânico"]:
            abort(403)

        novo_status = request.form.get("status")
        if novo_status not in ["Em andamento", "Concluída"]:
            flash("Status inválido!", "error")
            return redirect(url_for("historico_manutencao"))

        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        # Pega o veículo da manutenção
        cursor.execute("SELECT id_veiculo FROM manutencao WHERE id_manutencao=%s", (id_manutencao,))
        manut = cursor.fetchone()
        if not manut:
            flash("Manutenção não encontrada!", "error")
            cursor.close()
            conexao.close()
            return redirect(url_for("historico_manutencao"))

        id_veiculo = manut['id_veiculo']

        # Atualiza o status da manutenção
        cursor.execute("UPDATE manutencao SET status=%s WHERE id_manutencao=%s", (novo_status, id_manutencao))

        # Atualiza o status do veículo de acordo com a manutenção
        if novo_status == "Concluída":
            cursor.execute("UPDATE veiculo SET id_status_veiculo=1 WHERE id_veiculo=%s", (id_veiculo,))
        else:  # Em andamento
            cursor.execute("UPDATE veiculo SET id_status_veiculo=3 WHERE id_veiculo=%s", (id_veiculo,))

        conexao.commit()
        cursor.close()
        conexao.close()

        flash("Status atualizado com sucesso!", "success")
        return redirect(url_for("historico_manutencao"))
