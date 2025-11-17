from flask import render_template, request, redirect, url_for, flash, session
from db import conectar

def init_veiculos(app):

    @app.route("/cadastro_veiculo", methods=["GET", "POST"])
    def cadastro_veiculo():
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))

        conexao = conectar()
        cursor = conexao.cursor()

        # Combustível e status
        cursor.execute("SELECT id_combustivel, tipo_combustivel FROM combustivel")
        combustiveis = cursor.fetchall()

        cursor.execute("SELECT id_status_veiculo, descricao_status FROM status_veiculo")
        status = cursor.fetchall()

        # Carregar as seguradoras
        cursor.execute("SELECT id_seguro, companhia FROM seguro")
        seguros = cursor.fetchall()

        # Marcas e categorias
        marcas_fixas = [(1, "Renault"), (2, "Volkswagen"), (3, "BYD"), (4, "FIAT"), (5, "BMW")]
        categorias_fixas = [(1, "Compacto"), (2, "Sedan Médio"), (3, "SUV"), (4, "Picape"), (5, "Elétrico")]

        # ----------------------------------------------------------------------
        # PROCESSAMENTO DO POST
        # ----------------------------------------------------------------------
        if request.method == "POST":

            # Agora sim pode pegar o seguro
            id_seguro = request.form.get("companhiaSeguro")

            if not id_seguro or id_seguro == "":
                flash("Selecione uma companhia de seguro.", "error")
                return redirect(url_for("cadastro_veiculo"))

            id_seguro = int(id_seguro)

            cursor.execute("SELECT companhia FROM seguro WHERE id_seguro = %s", (id_seguro,))
            resultado_seguro = cursor.fetchone()

            if not resultado_seguro:
                flash("Seguro inválido.", "error")
                return redirect(url_for("cadastro_veiculo"))

            companhia = resultado_seguro[0]

            # Dados do veículo
            placa = request.form.get("placaVeiculo")
            chassi = request.form.get("chassiVeiculo")
            ano = int(request.form.get("anoVeiculo"))
            cor = request.form.get("corVeiculo")
            transmissao = request.form.get("transmissaoVeiculo")
            data_compra = request.form.get("dataCompra")
            valor_compra = float(request.form.get("valorCompra"))
            odometro = int(request.form.get("odometro"))
            data_vencimento = request.form.get("vencimentoLicenciamento")
            tanque = int(request.form.get("tanque"))
            tanque_fracao = float(request.form.get("tanqueFracao"))
            valor_fracao = (tanque * 6) / 8 + 5

            id_status = int(request.form.get("status"))
            id_combustivel = int(request.form.get("combustivel"))
            id_modelo = int(request.form.get("modeloVeiculo"))

            # Verifica duplicidade
            cursor.execute("SELECT 1 FROM veiculo WHERE placa = %s", (placa,))
            if cursor.fetchone():
                flash("Já existe um veículo com esta placa.", "error")
                cursor.close()
                conexao.close()
                return redirect(url_for("cadastro_veiculo"))

            cursor.execute("SELECT 1 FROM veiculo WHERE chassi = %s", (chassi,))
            if cursor.fetchone():
                flash("Já existe um veículo com este chassi.", "error")
                cursor.close()
                conexao.close()
                return redirect(url_for("cadastro_veiculo"))

            # Inserir veículo
            cursor.execute("""
                INSERT INTO veiculo
                (placa, ano, cor, chassi, quilometragem, transmissao, data_compra,
                valor_compra, data_vencimento, tanque, tanque_fracao, valor_fracao,
                id_modelo, id_status_veiculo, id_combustivel, id_seguro)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                placa, ano, cor, chassi, odometro, transmissao, data_compra,
                valor_compra, data_vencimento, tanque, tanque_fracao, valor_fracao,
                id_modelo, id_status, id_combustivel, id_seguro
            ))

            conexao.commit()
            cursor.close()
            conexao.close()

            flash("Veículo cadastrado com sucesso!", "success")
            return redirect(url_for("cadastro_veiculo"))

        # ----------------------------------------------------------------------

        return render_template("cadastro_veiculo.html",
                               combustiveis=combustiveis,
                               status=status,
                               marcas=marcas_fixas,
                               categorias=categorias_fixas,
                               seguros=seguros)


    @app.route("/veiculos")
    def listagem_veiculos():
        from app import veiculos
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))
        return render_template("veiculos.html", veiculos=veiculos)

    @app.route("/locar/<int:id>", methods=["POST"])
    def locar_veiculo(id):
        from app import veiculos
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))
        for veiculo in veiculos:
            if veiculo["id"] == id:
                if veiculo["status"] == "disponível":
                    veiculo["status"] = "alugado"
                    flash(f"Veículo {veiculo['modelo']} alugado com sucesso!", "success")
                else:
                    flash(f"O veículo {veiculo['modelo']} já está alugado.", "error")
                break
        else:
            flash("Veículo não encontrado.", "error")
        return redirect(url_for("listagem_veiculos"))
