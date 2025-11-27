from flask import render_template, request, redirect, url_for, flash, session, jsonify, Blueprint
from db import conectar
from datetime import datetime, date
from models.locacao_model import LocacaoModel

reserva_bp = Blueprint('reserva', __name__)


@reserva_bp.route("/reservar/<int:id_veiculo>", methods=["GET", "POST"])
def reservar_veiculo(id_veiculo):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
            SELECT v.id_veiculo, v.placa, v.ano, m.nome_modelo, ma.nome_marca,
                   c.nome_categoria, c.valor_diaria
            FROM veiculo v 
            JOIN modelo m ON v.id_modelo = m.id_modelo
            JOIN marca ma ON m.id_marca = ma.id_marca
            JOIN categoria_veiculo c ON m.id_categoria_veiculo = c.id_categoria_veiculo
            WHERE v.id_veiculo=%s
        """, (id_veiculo,))
    veiculo = cursor.fetchone()
    cursor.close()

    if not veiculo:
        cursor.close()
        conn.close()
        flash("Veículo não encontrado.", "error")
       
        return redirect(url_for("veiculos.grupo_carros"))

    return render_template("reserva_veiculo.html", veiculo=veiculo)

# Calcula o valor em tempo real
@reserva_bp.route("/api/valor-previsto-reserva", methods=["POST"])
def api_valor_previsto_reserva():
    dados = request.get_json()
    id_veiculo = dados.get("id_veiculo")
    dt_retirada = dados.get("data_retirada")
    dt_prevista = dados.get("data_devolucao_prevista")
    opcionais = dados.get("opcionais", [])

    if not id_veiculo or not dt_retirada or not dt_prevista:
        return jsonify({"valor_total_previsto": 0.0})

    try:
        dt_retirada_obj = datetime.strptime(dt_retirada, "%Y-%m-%d")
        dt_prevista_obj = datetime.strptime(dt_prevista, "%Y-%m-%d")
        locacao_model = LocacaoModel()
        valor_total = locacao_model.calcular_valor_previsto(
            id_veiculo, dt_retirada_obj, dt_prevista_obj, opcionais)
        return jsonify({"valor_total_previsto": float(valor_total or 0)})

    except Exception as e:
        print("Erro ao calcular valor previsto:", e)
        return jsonify({"valor_total_previsto": 0.0})


@reserva_bp.route("/reserva/criar", methods=["POST"])
def criar_reserva_json():
    dados = request.get_json()
    if not dados:
        return jsonify({"sucesso": False, "erro": "Nenhum dado enviado"})

    usuario_email = session.get("usuario_logado")
    if not usuario_email:
        return jsonify({"sucesso": False, "erro": "Usuário não está logado.", "redirect": url_for("auth.login")})

    # --- 1. Obter dados da requisição ---
    id_veiculo = dados.get("id_veiculo")
    dt_retirada_str = dados.get("data_retirada")
    dt_prevista_str = dados.get("data_devolucao_prevista")
    opcionais = dados.get("opcionais", [])

    if not id_veiculo or not dt_retirada_str or not dt_prevista_str:
        return jsonify({"sucesso": False, "erro": "Campos obrigatórios faltando"})

    locacao_model = LocacaoModel()

    try:
        with conectar() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # --- 2. Buscar id_cliente a partir do email na sessão ---
                cursor.execute(
                    "SELECT id_cliente FROM cliente WHERE email = %s", (usuario_email,))
                cliente = cursor.fetchone()
                if not cliente:
                    # --- SALVA A RESERVA NA SESSÃO ANTES DE IR EMBORA ---
                    session['reserva_pendente'] = {
                        "id_veiculo": id_veiculo,
                        "data_retirada": dt_retirada_str,
                        "data_devolucao_prevista": dt_prevista_str,
                        "opcionais": opcionais
                    }
                    
                    # Agora sim, redireciona para o cadastro
                    return jsonify({"sucesso": True, "redirect": url_for("clientes.cadastro_cliente")})
                id_cliente = cliente["id_cliente"]

        # --- 3. Converter datas (adicionando hora padrão 12:00) ---
        dt_retirada = datetime.strptime(
            f"{dt_retirada_str} 12:00", "%Y-%m-%d %H:%M")
        dt_prevista = datetime.strptime(
            f"{dt_prevista_str} 12:00", "%Y-%m-%d %H:%M")

        # --- 4. Chamar o Model para criar a locação (ele já calcula o valor previsto) ---
        dados_para_criar = {
            "id_cliente": id_cliente,
            "id_veiculo": id_veiculo,
            "data_retirada": dt_retirada,
            "data_devolucao_prevista": dt_prevista,
            "status": "Reserva"
        }

        id_locacao = locacao_model.criar_locacao(dados_para_criar, opcionais)

        # --- 5. Redirecionar para pagamento ---
        # Armazena o ID da locação na sessão para a página de pagamento usar
        session['id_locacao_pagamento'] = id_locacao
        redirect_url = url_for("pagamento.pagamento")

        return jsonify({"sucesso": True, "redirect": redirect_url})

    except Exception as e:
        # Log do erro no servidor para depuração
        print(f"Erro ao criar reserva: {e}")
        return jsonify({"sucesso": False, "erro": str(e)})
