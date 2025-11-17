from flask import jsonify, Blueprint, request
from db import conectar
from datetime import datetime
from .api_veiculos import get_categorias

locacao_api = Blueprint("locacao_api", __name__)

# --- Buscar locação ---
@locacao_api.route('/api/locacao/<int:id_loc>', methods=['GET'])
def get_locacao(id_loc):
    conn = conectar()
    if not conn:
        return jsonify({"erro":"Erro de conexão"}), 500
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id_locacao, status, data_retirada, data_devolucao_prevista, data_devolucao_real 
            FROM locacao WHERE id_locacao=%s
        """, (id_loc,))
        loc = cur.fetchone()
        if loc:
            # converter datas para string compatível com datetime-local
            for campo in ['data_retirada','data_devolucao_prevista','data_devolucao_real']:
                if loc[campo]:
                    loc[campo] = loc[campo].strftime("%Y-%m-%dT%H:%M")
            return jsonify(loc)
        return jsonify({"erro":"Locação não encontrada"}), 404
    finally:
        cur.close()
        conn.close()

# --- Atualizar locação ---
@locacao_api.route('/api/locacao/<int:id_loc>', methods=['PUT'])
def atualizar_locacao(id_loc):
    dados = request.get_json()
    conn = conectar()
    if not conn:
        return jsonify({"erro":"Erro de conexão"}), 500

    try:
        cur = conn.cursor(dictionary=True)
        # Pegar locacao existente
        cur.execute("""
            SELECT status, data_devolucao_real, quilometragem_retirada, quilometragem_devolucao, id_veiculo, tanque_saida
            FROM locacao 
            WHERE id_locacao=%s
        """, (id_loc,))
        loc = cur.fetchone()
        if not loc:
            return jsonify({"erro":"Locação não encontrada"}), 404

        status_novo = dados.get("status", loc["status"])
        km_saida = loc["quilometragem_retirada"]
        km_chegada = dados.get("quilometragem_devolucao")
        tanque_saida = loc["tanque_saida"]
        tanque_chegada = dados.get("tanque_chegada")

        # --- Validações ---
        # Data de devolucao_real obrigatória se status for 'Chegada'
        if status_novo == "Chegada" and not (dados.get("data_devolucao_real") or loc["data_devolucao_real"]):
            return jsonify({"erro":"Data de chegada real é obrigatória ao alterar para status Chegada"}), 400

        # Quilometragem de chegada e tanque de chegada obrigatória se status 'Chegada'
        if status_novo == "Chegada":
            if km_chegada is None or km_chegada == "":
                return jsonify({"erro": "Quilometragem de chegada é obrigatória ao alterar para status Chegada"}), 400
            #km_chegada DEVE ser maior que km_saida
            if int(km_chegada) < km_saida:
                return jsonify({"erro": "Quilometragem de chegada não pode ser menor que a de saída"}), 400
            # Tanque de chegada obrigatório
            if tanque_chegada is None or tanque_chegada == "":
                return jsonify({"erro": "Tanque de chegada é obrigatório ao alterar para status Chegada"}), 400

        campos = []
        valores = []

        # --- Atualizações ---

        # --- Atualizar data_retirada ---
        if "data_retirada" in dados and dados["data_retirada"]:
            campos.append("data_retirada=%s")
            valores.append(datetime.strptime(dados["data_retirada"], "%Y-%m-%dT%H:%M"))

        # --- Atualizar data_devolucao_prevista ---
        if "data_devolucao_prevista" in dados and dados["data_devolucao_prevista"]:
            campos.append("data_devolucao_prevista=%s")
            valores.append(datetime.strptime(dados["data_devolucao_prevista"], "%Y-%m-%dT%H:%M"))

        # --- Atualizar data_devolucao_real (somente se status Chegada) ---
        if "data_devolucao_real" in dados and status_novo == "Chegada" and dados["data_devolucao_real"]:
            campos.append("data_devolucao_real=%s")
            valores.append(datetime.strptime(dados["data_devolucao_real"], "%Y-%m-%dT%H:%M"))

        if "status" in dados:
            campos.append("status=%s")
            valores.append(status_novo)

        #QUILOMETRAGEM
        # --- QUILOMETRAGEM DE SAÍDA ---
        if status_novo in ["Reserva", "Locado"] and "quilometragem_retirada" not in dados:
            # Pegar quilometragem atual do veículo
            cur.execute("SELECT quilometragem FROM veiculo WHERE id_veiculo=%s", (loc["id_veiculo"],))
            km_saida = cur.fetchone()["quilometragem"]
            campos.append("quilometragem_retirada=%s")
            valores.append(km_saida)

        if km_chegada is not None and status_novo == "Chegada":
            campos.append("quilometragem_devolucao=%s")
            valores.append(int(km_chegada))
            # Atualiza também a quilometragem atual do veículo
            cur.execute("UPDATE veiculo SET quilometragem=%s WHERE id_veiculo=%s", (int(km_chegada), loc["id_veiculo"]))

        # --- Tanque ---
        # Se ainda não tiver tanque_saida e status for Reserva ou Locado, pega do veículo
        if status_novo in ["Reserva", "Locado"] and not tanque_saida:
            cur.execute("SELECT tanque_fracao FROM veiculo WHERE id_veiculo=%s", (loc["id_veiculo"],))
            tanque_saida = cur.fetchone()["tanque_fracao"]
            campos.append("tanque_saida=%s")
            valores.append(tanque_saida)

        # Validação tanque_chegada
        if status_novo == "Chegada":
            if tanque_chegada is None or tanque_chegada == "":
                return jsonify({"erro": "Tanque de chegada é obrigatório ao alterar para status Chegada"}), 400
            if int(tanque_chegada) < 0 or int(tanque_chegada) > 8:
                return jsonify({"erro": "Tanque de chegada inválido"}), 400
            campos.append("tanque_chegada=%s")
            valores.append(int(tanque_chegada))
            # Atualiza também o tanque do veículo
            cur.execute("UPDATE veiculo SET tanque_fracao=%s WHERE id_veiculo=%s", (int(tanque_chegada), loc["id_veiculo"]))

        # --- CAUÇÃO E DEVOLUÇÃO ---
        if "caucao" in dados:
            campos.append("caucao=%s")
            valores.append(float(dados["caucao"]))

        if "devolucao" in dados:
            campos.append("devolucao=%s")
            valores.append(dados["devolucao"])

        # --- Executa atualização ---
        if campos:
            sql = f"UPDATE locacao SET {', '.join(campos)} WHERE id_locacao=%s"
            valores.append(id_loc)
            cur.execute(sql, tuple(valores))
            conn.commit()

        # --- OPCIONAIS ---
        # Atualiza opcionais da locação se enviados
        opcionais = dados.get("opcionais")  # Ex.: [{id_opcional: 1, quantidade: 2}, ...]
        if opcionais and isinstance(opcionais, list):
            # Remove opcionais antigos da locação
            cur.execute("DELETE FROM locacao_opcional WHERE id_locacao=%s", (id_loc,))
            # Insere os novos
            for op in opcionais:
                id_opcional = op.get("id_opcional")
                quantidade = op.get("quantidade", 1)
                cur.execute("""
                    INSERT INTO locacao_opcional (id_locacao, id_opcional, quantidade)
                    VALUES (%s, %s, %s)
                """, (id_loc, id_opcional, quantidade))
            conn.commit()

        return jsonify({"mensagem":"Locação atualizada com sucesso"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        cur.close()
        conn.close()


# --- Buscar clientes por nome ou CPF (autocomplete) ---
@locacao_api.route('/api/clientes', methods=['GET'])
def buscar_clientes():
    termo = request.args.get('termo', '').strip()
    if not termo:
        return jsonify([])  # retorna lista vazia se nada digitado

    conn = conectar()
    if not conn:
        return jsonify({"erro": "Erro de conexão"}), 500

    try:
        cur = conn.cursor(dictionary=True)
        sql = """
            SELECT c.id_cliente, c.nome_completo, c.cpf, ch.numero_registro as cnh, ch.data_validade
            FROM cliente c
            JOIN cnh ch ON c.id_cnh = ch.id_cnh
            WHERE c.nome_completo LIKE %s OR c.cpf LIKE %s
            LIMIT 10
        """
        like_termo = f"%{termo}%"
        cur.execute(sql, (like_termo, like_termo))
        clientes = cur.fetchall()
        # Converter data_validade para string
        for c in clientes:
            c['data_validade'] = c['data_validade'].strftime("%Y-%m-%d")
        return jsonify(clientes)
    finally:
        cur.close()
        conn.close()

# --- Listar categorias usando função do api_veiculos.py ---
@locacao_api.route('/api/categorias', methods=['GET'])
def listar_categorias():
    return jsonify(get_categorias())

# --- Listar veículos por categoria ---
@locacao_api.route('/api/veiculos', methods=['GET'])
def listar_veiculos():
    id_categoria = request.args.get('id_categoria')
    if not id_categoria:
        return jsonify([])

    conn = conectar()
    if not conn:
        return jsonify({"erro": "Erro de conexão"}), 500
    try:
        cur = conn.cursor(dictionary=True)
        # Seleciona veículos disponíveis da categoria
        sql = """
            SELECT v.id_veiculo, v.placa, m.nome_modelo, ma.nome_marca
            FROM veiculo v
            JOIN modelo m ON v.id_modelo = m.id_modelo
            JOIN marca ma ON m.id_marca = ma.id_marca
            WHERE m.id_categoria_veiculo=%s AND v.id_status_veiculo=1
        """
        cur.execute(sql, (id_categoria,))
        veiculos = cur.fetchall()
        # Monta a string "Placa - Modelo - Marca" para frontend
        veiculos_formatados = [
            {"id": v["id_veiculo"], "descricao": f'{v["placa"]} - {v["nome_modelo"]} - {v["nome_marca"]}'}
            for v in veiculos
        ]
        return jsonify(veiculos_formatados)
    finally:
        cur.close()
        conn.close()


# --------- LISTAR OPCIONAIS
@locacao_api.route('/api/opcionais', methods=['GET'])
def listar_opcionais():
    conn = conectar()
    if not conn:
        return jsonify({"erro": "Erro de conexão"}), 500
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id_opcional, descricao, valor_diaria, quantidade FROM opcional")
        opcionais = cur.fetchall()
        return jsonify(opcionais)
    finally:
        cur.close()
        conn.close()

# ADICIONAR OPCIONAIS (múltiplos de uma vez)
@locacao_api.route('/api/locacao/<int:id_loc>/opcionais', methods=['POST'])
def adicionar_opcionais_locacao(id_loc):
    dados = request.get_json()
    # Ex.: dados = [{id_opcional: 1, quantidade: 2}, {...}]
    if not dados or not isinstance(dados, list):
        return jsonify({"erro": "Formato inválido"}), 400

    conn = conectar()
    if not conn:
        return jsonify({"erro": "Erro de conexão"}), 500

    try:
        cur = conn.cursor()
        for item in dados:
            id_opcional = item.get("id_opcional")
            quantidade = item.get("quantidade", 1)
            cur.execute("""
                INSERT INTO locacao_opcional (id_locacao, id_opcional, quantidade)
                VALUES (%s, %s, %s)
            """, (id_loc, id_opcional, quantidade))
        conn.commit()
        return jsonify({"mensagem": "Opcionais adicionados com sucesso"}), 200
    finally:
        cur.close()
        conn.close()
