from flask import jsonify, Blueprint, request
from db import conectar
from datetime import datetime
from .api_veiculos import get_categorias

locacao_api = Blueprint("locacao_api", __name__)

# Função auxiliar para cálculo de valor previsto
def calcular_valor_previsto(id_veiculo, dt_retirada, dt_prevista, opcionais, cur):
    dias = (dt_prevista - dt_retirada).days
    if dias < 1:
        dias = 1

    # valor da diária
    cur.execute("""
        SELECT c.valor_diaria 
        FROM categoria_veiculo c
        JOIN modelo m ON m.id_categoria_veiculo = c.id_categoria_veiculo
        JOIN veiculo v ON v.id_modelo = m.id_modelo
        WHERE v.id_veiculo=%s
    """, (id_veiculo,))
    r = cur.fetchone()
    if not r:
        raise Exception("Não foi possível obter valor da diária")
    valor_diaria = float(r["valor_diaria"])

    # total dos opcionais
    total_opcionais = 0
    for op in opcionais:
        cur.execute("SELECT valor_diaria FROM opcional WHERE id_opcional=%s", (op["id_opcional"],))
        r_op = cur.fetchone()
        if r_op:
            total_opcionais += float(r_op["valor_diaria"]) * int(op["quantidade"]) * dias

    return dias * valor_diaria + total_opcionais

@locacao_api.route('/api/locacao', methods=['POST'])
def criar_locacao():
    dados = request.get_json()
    conn = conectar()
    if not conn:
        return jsonify({"erro": "Erro de conexão"}), 500

    try:
        cur = conn.cursor(dictionary=True)

        # -------------------------------------------------------------
        # 1) PEGAR DADOS BÁSICOS
        # -------------------------------------------------------------
        id_cliente = dados.get("id_cliente")
        id_veiculo = dados.get("id_veiculo")
        data_retirada = dados.get("data_retirada")
        data_prevista = dados.get("data_devolucao_prevista")
        caucao = dados.get("caucao")
        devolucao = dados.get("devolucao")
        km_saida = dados.get("quilometragem_saida")
        km_chegada = dados.get("quilometragem_devolucao")
        tanque_saida = dados.get("tanque_saida")
        opcionais = dados.get("opcionais", [])
        status = dados.get("status", "Reserva")

        # Pegar quilometragem do veículo caso não tenha sido enviada
        if not km_saida or km_saida == "":
            cur.execute("SELECT quilometragem FROM veiculo WHERE id_veiculo=%s", (id_veiculo,))
            row = cur.fetchone()
            if row and row["quilometragem"] is not None:
                km_saida = row["quilometragem"]
            else:
                km_saida = 0  # valor padrão mínimo se não houver quilometragem cadastrada

        # Converter para inteiro
        km_saida = int(km_saida)

        #tratar km_chegada para ser None se for nulo (para evitar erro no banco de dados)
        if km_chegada in [None, ""]:
            km_chegada
        else:
            km_chegada = int(km_chegada)


        if not id_cliente:
            return jsonify({"erro": "id_cliente é obrigatório"}), 400
        if not id_veiculo:
            return jsonify({"erro": "id_veiculo é obrigatório"}), 400

        # Converter datas
        dt_retirada = datetime.strptime(data_retirada, "%Y-%m-%dT%H:%M")
        dt_prevista = datetime.strptime(data_prevista, "%Y-%m-%dT%H:%M")

        # CALCULAR valor_total_previsto usando função auxiliar
        valor_total_previsto = calcular_valor_previsto(id_veiculo, dt_retirada, dt_prevista, opcionais, cur)

        # CONFIGURAR CAMPOS DE CHEGADA
        # -------------------------------------------------------------
        data_devolucao_real = None
        quilometragem_devolucao = None
        tanque_chegada = None

        if status == "Chegada":
            data_devolucao_real = dados.get("data_devolucao_real")
            quilometragem_devolucao = dados.get("quilometragem_devolucao")
            tanque_chegada = dados.get("tanque_chegada")

            if not data_devolucao_real:
                return jsonify({"erro": "Data de chegada real obrigatória para status Chegada"}), 400
            if quilometragem_devolucao is None:
                return jsonify({"erro": "Quilometragem de chegada obrigatória para status Chegada"}), 400
            if tanque_chegada is None:
                return jsonify({"erro": "Tanque de chegada obrigatório para status Chegada"}), 400

            # converter data para datetime
            data_devolucao_real = datetime.strptime(data_devolucao_real, "%Y-%m-%dT%H:%M")

        # -------------------------------------------------------------
        # INSERIR LOCAÇÃO
        # -------------------------------------------------------------
        valor_final = None
        if status == "Chegada":
            valor_final = valor_total_previsto
        sql = """
            INSERT INTO locacao 
                (id_cliente, id_veiculo, status, data_retirada, data_devolucao_prevista,
                 caucao, devolucao, quilometragem_retirada, tanque_saida, valor_total_previsto,
                 data_devolucao_real, quilometragem_devolucao, tanque_chegada, valor_final)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        valores = (
            id_cliente,
            id_veiculo,
            status,
            dt_retirada,
            dt_prevista,
            caucao,
            devolucao,
            km_saida,
            tanque_saida,
            valor_total_previsto,
            data_devolucao_real,
            quilometragem_devolucao,
            tanque_chegada,
            valor_final
        )

        cur.execute(sql, valores)
        id_nova = cur.lastrowid

        # ATUALIZAR VEÍCULO APENAS SE STATUS = "CHEGADA"
        if status == "Chegada":
            cur.execute("""
                UPDATE veiculo
                SET quilometragem = %s,
                    id_status_veiculo = 1,
                    tanque_fracao = %s
                WHERE id_veiculo = %s
            """, (km_chegada, tanque_chegada, id_veiculo))
        else:
            # SE STATUS = "RESERVA" OU "LOCADO", ATUALIZA APENAS SE O CARRO ESTÁ "DISPONÍVEL" OU "ALUGADO"
            cur.execute("""
                UPDATE veiculo
                SET id_status_veiculo = 2
                WHERE id_veiculo = %s
            """, (id_veiculo,))

        # -------------------------------------------------------------
        # 8) INSERIR OPCIONAIS NA TABELA locacao_opcional
        # -------------------------------------------------------------
        for op in opcionais:
            cur.execute("""
                INSERT INTO locacao_opcional (id_locacao, id_opcional, quantidade)
                VALUES (%s, %s, %s)
            """, (id_nova, op["id_opcional"], op["quantidade"]))

        conn.commit()

        return jsonify({
            "mensagem": "Locação criada",
            "id_locacao": id_nova,
            "valor_total_previsto": valor_total_previsto
        }), 201
    

    except Exception as e:
        conn.rollback()
        return jsonify({"erro": str(e)}), 500
    finally:
        cur.close()
        conn.close()

# buscar locação para editar_locacao.html
@locacao_api.route("/api/locacao/<int:id_locacao>")
def get_locacao(id_locacao):
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT l.*, 
                   v.id_veiculo, v.placa, v.quilometragem,
                   mo.id_modelo, mo.nome_modelo AS modelo,
                   m.id_marca, m.nome_marca AS marca,
                   c.id_categoria_veiculo AS id_categoria, c.nome_categoria AS categoria_nome, c.valor_diaria,
                   cl.id_cliente, cl.nome_completo AS cliente_nome, cl.cpf AS cliente_cpf,
                   cn.numero_registro AS cliente_cnh, cn.data_validade AS cliente_validade
            FROM locacao l
            JOIN veiculo v ON v.id_veiculo = l.id_veiculo
            JOIN modelo mo ON mo.id_modelo = v.id_modelo
            JOIN marca m ON m.id_marca = mo.id_marca
            JOIN categoria_veiculo c ON c.id_categoria_veiculo = mo.id_categoria_veiculo
            JOIN cliente cl ON cl.id_cliente = l.id_cliente
            JOIN cnh cn ON cn.id_cnh = cl.id_cnh
            WHERE l.id_locacao = %s
        """, (id_locacao,))
        loc = cursor.fetchone()

        cursor.execute("""
            SELECT o.id_opcional, o.descricao, lo.quantidade
            FROM locacao_opcional lo
            JOIN opcional o ON o.id_opcional = lo.id_opcional
            WHERE lo.id_locacao = %s
        """, (id_locacao,))
        opcionais = cursor.fetchall()

        if loc:
            loc['quilometragem_saida'] = loc.get('quilometragem_retirada')
            loc['quilometragem_devolucao'] = loc.get('quilometragem_devolucao')
            loc['tanque_saida'] = loc.get('tanque_saida')
            loc['tanque_chegada'] = loc.get('tanque_chegada')

            if loc.get('cliente_validade'):
                loc['cliente_validade'] = loc['cliente_validade'].strftime('%Y-%m-%d')

        return jsonify({"locacao": loc, "opcionais": opcionais})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500







    

@locacao_api.route('/api/locacao/<int:id_loc>', methods=['PUT'])
def atualizar_locacao(id_loc):
    dados = request.get_json()
    conn = conectar()
    if not conn:
        return jsonify({"erro":"Erro de conexão com o banco de dados"}), 500

    try:
        cur = conn.cursor(dictionary=True)
        
        # 1. Pegar dados da locação existente
        cur.execute("""
            SELECT status, data_devolucao_real, quilometragem_retirada, quilometragem_devolucao,
                   id_veiculo, tanque_saida, valor_total_previsto
            FROM locacao 
            WHERE id_locacao=%s
        """, (id_loc,))
        loc = cur.fetchone()
        
        if not loc:
            return jsonify({"erro":"Locação não encontrada"}), 404

        # 2. Obter e preparar variáveis
        status_novo = dados.get("status", loc["status"])
        km_saida = loc["quilometragem_retirada"]
        km_chegada = dados.get("quilometragem_devolucao")
        tanque_saida = loc["tanque_saida"] # Mantém o valor original se não for alterado
        tanque_chegada = dados.get("tanque_chegada")

        # --- 3. Validações para mudança de status para 'Chegada' ---
        if status_novo == "Chegada":
            # Data de devolucao_real obrigatória
            if not (dados.get("data_devolucao_real") or loc["data_devolucao_real"]):
                return jsonify({"erro":"Data de chegada real é obrigatória ao alterar para status Chegada"}), 400

            # Quilometragem de chegada obrigatória
            if km_chegada is None or km_chegada == "":
                return jsonify({"erro": "Quilometragem de chegada é obrigatória ao alterar para status Chegada"}), 400
            
            # Quilometragem de chegada não pode ser menor que a de saída
            if int(km_chegada) < km_saida:
                return jsonify({"erro": "Quilometragem de chegada não pode ser menor que a de saída"}), 400
            
            # Tanque de chegada obrigatório
            if tanque_chegada is None or tanque_chegada == "":
                return jsonify({"erro": "Tanque de chegada é obrigatório ao alterar para status Chegada"}), 400
            
            # Validação do valor do tanque (de 0 a 8)
            if int(tanque_chegada) < 0 or int(tanque_chegada) > 8:
                return jsonify({"erro": "Tanque de chegada inválido (deve ser entre 0 e 8)"}), 400
            
            # Converte a quilometragem para int
            km_chegada = int(km_chegada)
            tanque_chegada = int(tanque_chegada)
            
        campos = []
        valores = []

        # --- 4. Atualizações de datas ---
        data_retirada_nova = None
        data_prevista_nova = None

        if "data_retirada" in dados and dados["data_retirada"]:
            data_retirada_nova = datetime.strptime(dados["data_retirada"], "%Y-%m-%dT%H:%M")
            campos.append("data_retirada=%s")
            valores.append(data_retirada_nova)

        if "data_devolucao_prevista" in dados and dados["data_devolucao_prevista"]:
            data_prevista_nova = datetime.strptime(dados["data_devolucao_prevista"], "%Y-%m-%dT%H:%M")
            campos.append("data_devolucao_prevista=%s")
            valores.append(data_prevista_nova)

        # Data de devolução real (só atualiza se o status for Chegada e o campo foi enviado/atualizado)
        if "data_devolucao_real" in dados and status_novo == "Chegada" and dados["data_devolucao_real"]:
            campos.append("data_devolucao_real=%s")
            valores.append(datetime.strptime(dados["data_devolucao_real"], "%Y-%m-%dT%H:%M"))
        
        # Atualização do status
        if "status" in dados:
            campos.append("status=%s")
            valores.append(status_novo)

        # --- 5. Atualizações de Quilometragem ---
        # Se o status for Reserva ou Locado e quilometragem_retirada não foi enviada
        if status_novo in ["Reserva", "Locado"] and "quilometragem_retirada" not in dados:
            # Busca a quilometragem atual do veículo para preencher a quilometragem de retirada
            cur.execute("SELECT quilometragem FROM veiculo WHERE id_veiculo=%s", (loc["id_veiculo"],))
            row = cur.fetchone()
            if row:
                km_saida = row["quilometragem"]
                campos.append("quilometragem_retirada=%s")
                valores.append(km_saida)
        
        # Quilometragem de devolução (somente se status for Chegada)
        if status_novo == "Chegada" and km_chegada is not None:
            campos.append("quilometragem_devolucao=%s")
            valores.append(km_chegada)
            # Atualiza a quilometragem do veículo no cadastro
            cur.execute("UPDATE veiculo SET quilometragem=%s WHERE id_veiculo=%s", (km_chegada, loc["id_veiculo"]))

        # --- 6. Atualizações de Tanque ---
        # Tanque de Saída (se for Reserva/Locado e não tiver valor de saída registrado)
        if status_novo in ["Reserva", "Locado"] and not loc["tanque_saida"]:
            # Pega a fração de tanque atual do veículo
            cur.execute("SELECT tanque_fracao FROM veiculo WHERE id_veiculo=%s", (loc["id_veiculo"],))
            tanque_saida = cur.fetchone()["tanque_fracao"]
            campos.append("tanque_saida=%s")
            valores.append(tanque_saida)
            
        # Tanque de Chegada (somente se status for Chegada)
        if status_novo == "Chegada" and tanque_chegada is not None:
            campos.append("tanque_chegada=%s")
            valores.append(tanque_chegada)
            # Atualiza a fração de tanque do veículo no cadastro
            cur.execute("UPDATE veiculo SET tanque_fracao=%s WHERE id_veiculo=%s", (tanque_chegada, loc["id_veiculo"]))

        # --- 7. Caução e Devolução ---
        if "caucao" in dados:
            campos.append("caucao=%s")
            valores.append(float(dados["caucao"]))

        if "devolucao" in dados:
            campos.append("devolucao=%s")
            valores.append(dados["devolucao"])

        # --- 8. Recalcular valor_total_previsto se datas mudaram ---
        valor_previsto_novo = loc["valor_total_previsto"] # Mantém o valor original como default
        if data_retirada_nova or data_prevista_nova:
            
            # Pega as datas atuais no banco de dados para garantir que temos ambas as datas
            cur.execute("""
                SELECT data_retirada, data_devolucao_prevista
                FROM locacao WHERE id_locacao=%s
            """, (id_loc,))
            datas = cur.fetchone()

            # Usa a data nova ou a data do banco (caso não tenha sido alterada)
            dt_retirada = data_retirada_nova or datas["data_retirada"]
            dt_prevista = data_prevista_nova or datas["data_devolucao_prevista"]

            # Busca os opcionais vinculados a esta locação
            cur.execute("""
                SELECT lo.id_opcional, lo.quantidade
                FROM locacao_opcional lo
                WHERE lo.id_locacao=%s
            """, (id_loc,))
            ops_db = cur.fetchall() 
            
            # Prepara a lista de opcionais no formato esperado
            opcionais_para_calculo = [
                {"id_opcional": op["id_opcional"], "quantidade": op["quantidade"]}
                for op in ops_db
            ]

            # Recalcula o valor previsto
            valor_previsto_novo = calcular_valor_previsto(
                loc["id_veiculo"],
                dt_retirada,
                dt_prevista,
                opcionais_para_calculo,
                cur
            )

            campos.append("valor_total_previsto=%s")
            valores.append(valor_previsto_novo)


        # --- 9. Executar atualização no banco de dados ---
        if campos:
            sql = f"UPDATE locacao SET {', '.join(campos)} WHERE id_locacao=%s"
            valores.append(id_loc)
            cur.execute(sql, tuple(valores))
            
            # Se o status foi alterado para Chegada ou Locado, atualiza o status do veículo
            if status_novo == "Chegada":
                 # Status 2: Disponível (assumindo que 2 é o status de "disponível para locação" após a devolução)
                 cur.execute("UPDATE veiculo SET id_status_veiculo = 1 WHERE id_veiculo = %s", (loc["id_veiculo"],))
            elif status_novo == "Locado":
                 # Status 3: Locado (assumindo que 3 é o status de "alugado/em uso")
                 cur.execute("UPDATE veiculo SET id_status_veiculo = 2 WHERE id_veiculo = %s", (loc["id_veiculo"],))
            elif status_novo == "Reserva":
                 # Status 4: Reservado (assumindo que 4 é o status de "reservado")
                 cur.execute("UPDATE veiculo SET id_status_veiculo = 2 WHERE id_veiculo = %s", (loc["id_veiculo"],))


            conn.commit()
        else:
            # Caso não haja campos para atualizar, apenas retorna o status 200
            pass

        # 10. Retornar valores atualizados (incluindo valor_final que pode ter sido calculado por trigger)
        cur.execute("SELECT valor_total_previsto, valor_final FROM locacao WHERE id_locacao=%s", (id_loc,))
        valores_atualizados = cur.fetchone()

        # O valor_final só é calculado/definido se a locação for de fato finalizada (Chegada)
        valor_final_retorno = float(valores_atualizados["valor_final"]) if valores_atualizados["valor_final"] is not None else None

        return jsonify({
            "mensagem":"Locação atualizada com sucesso",
            "valor_total_previsto": float(valores_atualizados["valor_total_previsto"]),
            "valor_final": valor_final_retorno
        }), 200

    except Exception as e:
        conn.rollback()
        # Loga o erro no console
        print(f"Erro ao atualizar locação {id_loc}: {str(e)}")
        return jsonify({"erro": str(e)}), 500
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if conn:
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

        sql = """
            SELECT 
                v.id_veiculo,
                v.placa,
                v.quilometragem,
                m.nome_modelo,
                ma.nome_marca
            FROM veiculo v
            JOIN modelo m ON v.id_modelo = m.id_modelo
            JOIN marca ma ON m.id_marca = ma.id_marca
            WHERE m.id_categoria_veiculo=%s 
              AND v.id_status_veiculo=1
        """

        cur.execute(sql, (id_categoria,))
        veiculos = cur.fetchall()

        veiculos_formatados = [
            {
                "id": v["id_veiculo"],
                "descricao": f'{v["placa"]} - {v["nome_modelo"]} - {v["nome_marca"]}',
                "quilometragem": v["quilometragem"]   
            }
            for v in veiculos
        ]

        return jsonify(veiculos_formatados)

    finally:
        cur.close()
        conn.close()

# --- Buscar um veículo específico (quilometragem para preencher KM de saída) ---
@locacao_api.route('/api/veiculo/<int:id_veiculo>', methods=['GET'])
def get_veiculo(id_veiculo):
    conn = conectar()
    if not conn:
        return jsonify({"erro": "Erro de conexão"}), 500

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                id_veiculo,
                placa,
                quilometragem,
                tanque_fracao
            FROM veiculo
            WHERE id_veiculo=%s
        """, (id_veiculo,))
        
        veiculo = cur.fetchone()

        if not veiculo:
            return jsonify({"erro": "Veículo não encontrado"}), 404
        
        return jsonify(veiculo)

    finally:
        cur.close()
        conn.close()

# --- Listar opcionais disponíveis ---
@locacao_api.route('/api/opcionais', methods=['GET'])
def listar_opcionais():
    conn = conectar()
    if not conn:
        return jsonify({"erro": "Erro de conexão"}), 500
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id_opcional, descricao, valor_diaria FROM opcional")
        opcionais = cur.fetchall()
        return jsonify(opcionais)
    finally:
        cur.close()
        conn.close()

# --- Rota para valor previsto em tempo real ---
@locacao_api.route('/api/valor-previsto', methods=['POST'])
def valor_previsto():
    dados = request.get_json()
    id_veiculo = dados.get("id_veiculo")
    data_retirada = dados.get("data_retirada")
    data_prevista = dados.get("data_devolucao_prevista")
    opcionais = dados.get("opcionais", [])

    if not id_veiculo or not data_retirada or not data_prevista:
        return jsonify({"erro":"Veículo e datas são obrigatórios"}), 400

    try:
        dt_retirada = datetime.strptime(data_retirada, "%Y-%m-%dT%H:%M")
        dt_prevista = datetime.strptime(data_prevista, "%Y-%m-%dT%H:%M")

        conn = conectar()
        cur = conn.cursor(dictionary=True)

        valor_total = calcular_valor_previsto(id_veiculo, dt_retirada, dt_prevista, opcionais, cur)

        cur.close()
        conn.close()

        return jsonify({"valor_total_previsto": valor_total})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
@locacao_api.route('/api/historico-locacao', methods=['GET'])
def listar_historico_locacao():
    conn = conectar()
    if not conn:
        return jsonify({"erro": "Erro de conexão com o banco de dados"}), 500

    try:
        cur = conn.cursor(dictionary=True)
        
        # Query para buscar todos os dados de locação com JOINs para Cliente e Veículo/Modelo/Marca
        sql = """
            SELECT
                l.id_locacao,
                l.status,
                l.data_retirada,
                l.data_devolucao_prevista,
                l.data_devolucao_real,
                c.nome_completo,
                v.placa,
                m.nome_modelo,
                ma.nome_marca
            FROM locacao l
            JOIN cliente c ON l.id_cliente = c.id_cliente
            JOIN veiculo v ON l.id_veiculo = v.id_veiculo
            JOIN modelo m ON v.id_modelo = m.id_modelo
            JOIN marca ma ON m.id_marca = ma.id_marca
            ORDER BY l.id_locacao DESC
        """
        
        cur.execute(sql)
        locacoes = cur.fetchall()

        # Formatar as datas e criar a descrição do veículo
        for loc in locacoes:
            # Formata datas para o padrão YYYY-MM-DD HH:MM
            date_format = "%Y-%m-%d %H:%M"
            
            loc["data_retirada"] = loc["data_retirada"].strftime(date_format)
            loc["data_devolucao_prevista"] = loc["data_devolucao_prevista"].strftime(date_format)
            
            if loc["data_devolucao_real"]:
                loc["data_devolucao_real"] = loc["data_devolucao_real"].strftime(date_format)
            else:
                loc["data_devolucao_real"] = "N/A" # Mostrar "N/A" se não houver devolução real
            
            # Combina placa, modelo e marca para o campo 'veiculo'
            loc["veiculo"] = f'{loc["placa"]} - {loc["nome_modelo"]} ({loc["nome_marca"]})'
            
            # Remove campos desnecessários após a formatação
            del loc["placa"]
            del loc["nome_modelo"]
            del loc["nome_marca"]

        return jsonify(locacoes), 200

    except Exception as e:
        print(f"Erro ao buscar histórico: {e}")
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
    finally:
        if conn:
            cur.close()
            conn.close()
