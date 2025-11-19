from flask import render_template, request, redirect, url_for, flash, session, abort, jsonify
from db import conectar
from datetime import datetime
from .api_locacao import calcular_valor_previsto

def init_veiculos(app):

    @app.route("/cadastro_veiculo", methods=["GET", "POST"])
    def cadastro_veiculo():
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))
        
        if session.get("perfil") not in ["Gerente", "Atendente"]:
            abort(403)

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

            # --- Seleciona seguro existente ---
            id_seguro = int(request.form.get("companhiaSeguro"))
            vencimento_seguro = request.form.get("vencimentoSeguro")

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

            # --- Captura e converte tanque ---
            tanque_str = request.form.get("tanque")

            mapa_tanque = {
                "Cheio": 8, "7/8": 7, "6/8": 6, "5/8": 5,
                "4/8": 4, "3/8": 3, "2/8": 2, "1/8": 1,
                "Vazio": 0
            }

            tanque = mapa_tanque.get(tanque_str, 0)  # padrão = vazio
            tanque_fracao = tanque / 8
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

            # Atualizar vencimento do seguro
            cursor.execute("""
                UPDATE seguro
                SET vencimento=%s
                WHERE id_seguro=%s
            """, (vencimento_seguro, id_seguro))

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


        # ==========================
    #   LISTAR VEÍCULOS
    # ==========================
    @app.route("/lista_veiculos")
    def lista_veiculos():
        if "usuario_logado" not in session:
            flash("Faça login para acessar.", "error")
            return redirect(url_for("login"))

        busca = request.args.get("busca", "").strip()

        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        if len(busca) >= 3:
            like = f"%{busca}%"
            cursor.execute("""
                SELECT v.id_veiculo, v.placa, v.chassi, v.ano, v.cor,
                    m.nome_modelo, c.nome_categoria, s.descricao_status
                FROM veiculo v
                JOIN modelo m ON v.id_modelo = m.id_modelo
                JOIN categoria_veiculo c ON m.id_categoria_veiculo = c.id_categoria_veiculo
                JOIN status_veiculo s ON v.id_status_veiculo = s.id_status_veiculo
                WHERE v.placa LIKE %s OR v.chassi LIKE %s
            """, (like, like))
        else:
            cursor.execute("""
                SELECT v.id_veiculo, v.placa, v.chassi, v.ano, v.cor,
                    m.nome_modelo, c.nome_categoria, s.descricao_status
                FROM veiculo v
                JOIN modelo m ON v.id_modelo = m.id_modelo
                JOIN categoria_veiculo c ON m.id_categoria_veiculo = c.id_categoria_veiculo
                JOIN status_veiculo s ON v.id_status_veiculo = s.id_status_veiculo
            """)

        veiculos = cursor.fetchall()
        cursor.close()
        conexao.close()

        return render_template("lista_veiculos.html", veiculos=veiculos, busca=busca)


    @app.route("/editar_veiculo/<int:id_veiculo>", methods=["GET", "POST"])
    def editar_veiculo(id_veiculo):
        conn = conectar()
        if not conn:
            flash("Erro na conexão com o banco", "error")
            return redirect(url_for("lista_veiculos"))

        cursor = conn.cursor(dictionary=True)

        if request.method == "POST":
            # Aqui você pegaria os dados do form e atualizaria o veículo
            # Exemplo:
            placa = request.form.get("placaVeiculo")
            chassi = request.form.get("chassiVeiculo")
            ano = request.form.get("anoVeiculo")
            cor = request.form.get("corVeiculo")
            transmissao = request.form.get("transmissaoVeiculo")
            data_compra = request.form.get("dataCompra")
            valor_compra = request.form.get("valorCompra")
            quilometragem = request.form.get("odometro")
            data_vencimento = request.form.get("vencimentoLicenciamento")
            tanque = request.form.get("tanque")
            tanque_fracao = request.form.get("tanqueFracao")
            id_combustivel = request.form.get("combustivel")
            id_modelo = request.form.get("modeloVeiculo")
            id_status_veiculo = request.form.get("status")
            id_seguro = request.form.get("companhiaSeguro") or None
            vencimento_seguro = request.form.get("vencimentoSeguro") or None

             #Verificar duplicidade de placa
            cursor.execute("SELECT id_veiculo FROM veiculo WHERE placa=%s AND id_veiculo != %s", (placa, id_veiculo))
            if cursor.fetchone():
                flash("Já existe um veículo com essa placa!", "error")
                return redirect(url_for("editar_veiculo", id_veiculo=id_veiculo))

            # Verificar duplicidade de chassi
            cursor.execute("SELECT id_veiculo FROM veiculo WHERE chassi=%s AND id_veiculo != %s", (chassi, id_veiculo))
            if cursor.fetchone():
                flash("Já existe um veículo com esse chassi!", "error")
                return redirect(url_for("editar_veiculo", id_veiculo=id_veiculo))

            
            sql_update = """
                UPDATE veiculo SET
                    placa=%s, chassi=%s, ano=%s, cor=%s,
                    transmissao=%s, data_compra=%s, valor_compra=%s,
                    quilometragem=%s, data_vencimento=%s, tanque=%s,
                    tanque_fracao=%s, id_combustivel=%s, id_modelo=%s,
                    id_status_veiculo=%s, id_seguro=%s
                WHERE id_veiculo=%s
            """
            cursor.execute(sql_update, (
                placa, chassi, ano, cor, transmissao, data_compra, valor_compra,
                quilometragem, data_vencimento, tanque, tanque_fracao,
                id_combustivel, id_modelo, id_status_veiculo, id_seguro, id_veiculo
            ))

             # Atualizar vencimento do seguro
            cursor.execute("""
                UPDATE seguro
                SET vencimento=%s
                WHERE id_seguro=%s
            """, (vencimento_seguro, id_seguro))

            conn.commit()
            flash("Veículo atualizado com sucesso!", "success")
            return redirect(url_for("lista_veiculos"))
        
        

        # --- GET: buscar dados atuais do veículo ---
        cursor.execute("""
            SELECT v.*, m.id_marca, m.nome_marca, mo.id_modelo, mo.nome_modelo,
                   c.nome_categoria AS nome_categoria, s.id_status_veiculo,
                   s.descricao_status, comb.id_combustivel, comb.tipo_combustivel,
                   seg.id_seguro, seg.companhia, seg.vencimento AS vencimento_seguro
            FROM veiculo v
            JOIN modelo mo ON v.id_modelo = mo.id_modelo
            JOIN marca m ON mo.id_marca = m.id_marca
            JOIN categoria_veiculo c ON mo.id_categoria_veiculo = c.id_categoria_veiculo
            JOIN status_veiculo s ON v.id_status_veiculo = s.id_status_veiculo
            JOIN combustivel comb ON v.id_combustivel = comb.id_combustivel
            LEFT JOIN seguro seg ON v.id_seguro = seg.id_seguro
            WHERE v.id_veiculo=%s
        """, (id_veiculo,))
        veiculo = cursor.fetchone()
        if not veiculo:
            abort(404)

        # --- buscar listas para selects ---
        cursor.execute("SELECT * FROM combustivel")
        combustiveis = cursor.fetchall()

        cursor.execute("SELECT * FROM marca")
        marcas = cursor.fetchall()

        cursor.execute("SELECT mo.*, c.nome_categoria FROM modelo mo JOIN categoria_veiculo c ON mo.id_categoria_veiculo = c.id_categoria_veiculo")
        modelos = cursor.fetchall()

        cursor.execute("SELECT * FROM status_veiculo")
        status = cursor.fetchall()

        cursor.execute("SELECT * FROM seguro")
        seguros = cursor.fetchall()

        conn.close()

        return render_template(
            "editar_veiculo.html",
            veiculo=veiculo,
            combustiveis=combustiveis,
            marcas=marcas,
            modelos=modelos,
            status=status,
            seguros=seguros,
            id_veiculo=id_veiculo
        )


    # ==========================
    #   DELETAR VEÍCULO
    # ==========================
    @app.route("/deletar_veiculo/<int:id_veiculo>")
    def deletar_veiculo(id_veiculo):

        if "usuario_logado" not in session:
            flash("Faça login para acessar.", "error")
            return redirect(url_for("login"))

        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("SELECT id_seguro FROM veiculo WHERE id_veiculo=%s", (id_veiculo,))
        row = cursor.fetchone()
        if not row:
            abort(404)

        id_seguro = row["id_seguro"]

        # Deletar veículo
        cursor.execute("DELETE FROM veiculo WHERE id_veiculo=%s", (id_veiculo,))
        # Opcional: deletar seguro vinculado se desejar
        # cursor.execute("DELETE FROM seguro WHERE id_seguro=%s", (id_seguro,))

        conexao.commit()
        cursor.close()
        conexao.close()

        flash("Veículo removido com sucesso!", "success")
        return redirect(url_for("lista_veiculos"))


   