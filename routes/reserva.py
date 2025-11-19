from flask import render_template, request, redirect, url_for, flash, session, jsonify
from db import conectar
from datetime import datetime
from .api_locacao import calcular_valor_previsto

def init_reserva(app):
    # =============================
    # LISTAR GRUPO DE CARROS
    # =============================
    @app.route("/grupo_carros")
    def grupo_carros():
        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_categoria_veiculo, nome_categoria, valor_diaria FROM categoria_veiculo")
        categorias = cursor.fetchall()

        for categoria in categorias:
            cursor.execute("""
                SELECT v.id_veiculo, v.placa, v.ano, v.cor, m.nome_modelo, ma.nome_marca
                FROM veiculo v
                JOIN modelo m ON v.id_modelo = m.id_modelo
                JOIN marca ma ON m.id_marca = ma.id_marca
                WHERE m.id_categoria_veiculo = %s
            """, (categoria["id_categoria_veiculo"],))
            categoria["veiculos"] = cursor.fetchall()

        cursor.close()
        conn.close()
        return render_template("grupo_carros.html", categorias=categorias)

    # =============================
    # RESERVAR VEÍCULO
    # =============================
    @app.route("/reservar/<int:id_veiculo>", methods=["GET", "POST"])
    def reservar_veiculo(id_veiculo):
        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT v.id_veiculo, v.placa, v.ano, v.cor, m.nome_modelo, ma.nome_marca,
                   c.nome_categoria, c.valor_diaria
            FROM veiculo v
            JOIN modelo m ON v.id_modelo = m.id_modelo
            JOIN marca ma ON m.id_marca = ma.id_marca
            JOIN categoria_veiculo c ON m.id_categoria_veiculo = c.id_categoria_veiculo
            WHERE v.id_veiculo=%s
        """, (id_veiculo,))
        veiculo = cursor.fetchone()

        if not veiculo:
            cursor.close()
            conn.close()
            flash("Veículo não encontrado.", "error")
            return redirect(url_for("grupo_carros"))

        valor_previsto = 0
        try:
            dt_hoje = datetime.today().date()
            valor_previsto = calcular_valor_previsto(id_veiculo, dt_hoje, dt_hoje, [], cursor)
        except Exception as e:
            print("Erro ao calcular valor previsto:", e)

        cursor.close()
        conn.close()
        return render_template("reserva_veiculo.html", veiculo=veiculo, valor_previsto=valor_previsto)

    # =============================
    # API VALOR PREVISTO
    # =============================
    @app.route("/api/valor-previsto-reserva", methods=["POST"])
    def api_valor_previsto_reserva():
        dados = request.get_json()
        id_veiculo = dados.get("id_veiculo")
        dt_retirada = dados.get("data_retirada")
        dt_prevista = dados.get("data_devolucao_prevista")
        opcionais = dados.get("opcionais", [])

        if not id_veiculo or not dt_retirada or not dt_prevista:
            return jsonify({"valor_total_previsto": 0.0})

        dt_retirada = datetime.strptime(dt_retirada, "%Y-%m-%d")
        dt_prevista = datetime.strptime(dt_prevista, "%Y-%m-%d")

        valor = 0.0
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        try:
            valor = calcular_valor_previsto(id_veiculo, dt_retirada, dt_prevista, opcionais, cursor)
        except Exception as e:
            print("Erro ao calcular valor previsto:", e)

        cursor.close()
        conn.close()
        return jsonify({"valor_total_previsto": float(valor or 0)})

    # =============================
    # CRIAR RESERVA TEMPORÁRIA
    # =============================
    def criar_reserva(id_veiculo, dt_retirada, dt_prevista, opcionais, cursor, conn):
        usuario_email = session.get("usuario_logado")
        cursor.execute("SELECT id_usuario FROM usuario WHERE email = %s", (usuario_email,))
        row = cursor.fetchone()
        if not row:
            raise Exception("Usuário logado não encontrado no banco.")
        id_usuario = row["id_usuario"]

        valor_total = calcular_valor_previsto(id_veiculo, dt_retirada, dt_prevista, opcionais, cursor)

        # Inserir reserva temporária (sem id_cliente ainda)
        cursor.execute("""
            INSERT INTO reserva (id_veiculo, data_retirada, data_devolucao_prevista, valor_total_previsto, status, id_usuario)
            VALUES (%s, %s, %s, %s, 'Reserva', %s)
        """, (id_veiculo, dt_retirada, dt_prevista, valor_total, id_usuario))
        conn.commit()
        id_reserva = cursor.lastrowid

        # Inserir opcionais
        for op in opcionais:
            id_opcional = op["id_opcional"]
            quantidade = op.get("quantidade", 1)
            cursor.execute("""
                INSERT INTO reserva_opcional (id_reserva, id_opcional, quantidade)
                VALUES (%s, %s, %s)
            """, (id_reserva, id_opcional, quantidade))
        conn.commit()

        # Verifica se já existe cliente cadastrado
        cursor.execute("SELECT id_cliente FROM cliente WHERE email = %s", (usuario_email,))
        cliente = cursor.fetchone()

        if cliente:
            redirect_url = url_for("pagamento")
        else:
            redirect_url = url_for("cadastro_cliente", id_reserva=id_reserva)

        return id_reserva, redirect_url

    # =============================
    # ROTA JSON PARA CRIAR RESERVA
    # =============================
    @app.route("/reserva/criar", methods=["POST"])
    def criar_reserva_json():
        dados = request.get_json()
        if not dados:
            return jsonify({"sucesso": False, "erro": "Nenhum dado enviado"})

        id_veiculo = dados.get("id_veiculo")
        dt_retirada = dados.get("data_retirada")
        dt_prevista = dados.get("data_devolucao_prevista")
        opcionais = dados.get("opcionais", [])

        if not id_veiculo or not dt_retirada or not dt_prevista:
            return jsonify({"sucesso": False, "erro": "Campos obrigatórios faltando"})

        try:
            dt_retirada = datetime.strptime(dt_retirada, "%Y-%m-%d")
            dt_prevista = datetime.strptime(dt_prevista, "%Y-%m-%d")
        except Exception as e:
            return jsonify({"sucesso": False, "erro": f"Erro ao converter datas: {e}"})

        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        try:
            id_reserva, redirect_url = criar_reserva(id_veiculo, dt_retirada, dt_prevista, opcionais, cursor, conn)
        except Exception as e:
            cursor.close()
            conn.close()
            return jsonify({"sucesso": False, "erro": str(e)})

        cursor.close()
        conn.close()
        return jsonify({"sucesso": True, "redirect": redirect_url})
