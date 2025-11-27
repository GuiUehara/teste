from db import conectar
from datetime import datetime
import math


class LocacaoModel:

    def _calcular_valor_previsto(self, id_veiculo, dt_retirada, dt_prevista, opcionais, cursor):
        """Lógica de cálculo do valor previsto, agora dentro do model."""
        dias = (dt_prevista - dt_retirada).days
        if dias < 1:
            dias = 1

        cursor.execute("""
            SELECT c.valor_diaria 
            FROM categoria_veiculo c
            JOIN modelo m ON m.id_categoria_veiculo = c.id_categoria_veiculo
            JOIN veiculo v ON v.id_modelo = m.id_modelo
            WHERE v.id_veiculo=%s
        """, (id_veiculo,))
        r = cursor.fetchone()
        if not r:
            raise Exception(
                "Não foi possível obter valor da diária do veículo.")
        valor_diaria = float(r["valor_diaria"])

        total_opcionais = 0
        if opcionais:
            for op in opcionais:
                cursor.execute(
                    "SELECT valor_diaria FROM opcional WHERE id_opcional=%s", (op["id_opcional"],))
                r_op = cursor.fetchone()
                if r_op:
                    total_opcionais += float(r_op["valor_diaria"]) * \
                        int(op.get("quantidade", 1)) * dias

        return dias * valor_diaria + total_opcionais

    def calcular_valor_previsto(self, id_veiculo, dt_retirada, dt_prevista, opcionais):
        """Interface pública para cálculo de valor previsto."""
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        try:
            return self._calcular_valor_previsto(id_veiculo, dt_retirada, dt_prevista, opcionais, cursor)
        finally:
            cursor.close()
            conn.close()

    def criar_locacao(self, dados_locacao, opcionais):
        """
        Centraliza a criação de uma locação, seja ela uma Reserva ou um Contrato.
        """
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        try:
            # Calcula o valor previsto antes de qualquer coisa
            valor_total_previsto = self._calcular_valor_previsto(
                dados_locacao['id_veiculo'], dados_locacao['data_retirada'], dados_locacao['data_devolucao_prevista'], opcionais, cursor
            )

            # --- 1. Buscar dados complementares (caução, km, etc.) ---
            cursor.execute("""
                SELECT v.quilometragem, v.tanque_fracao, cv.valor_caucao
                FROM veiculo v
                JOIN modelo m ON v.id_modelo = m.id_modelo
                JOIN categoria_veiculo cv ON m.id_categoria_veiculo = cv.id_categoria_veiculo
                WHERE v.id_veiculo = %s
            """, (dados_locacao['id_veiculo'],))
            veiculo_data = cursor.fetchone()

            if not veiculo_data:
                raise Exception("Veículo não encontrado.")

            # --- 2. Preparar os dados para inserção ---
            # Usa o valor do banco ou um padrão seguro.
            caucao = veiculo_data.get('valor_caucao', 700.00)
            # Usa o KM do formulário (contrato) ou o do banco (reserva).
            km_saida = dados_locacao.get(
                'quilometragem_retirada') or veiculo_data.get('quilometragem', 0)
            # Usa o tanque do formulário (contrato) ou o do banco (reserva).
            tanque_saida = dados_locacao.get(
                'tanque_saida') or veiculo_data.get('tanque_fracao', 8)

            # --- 3. Inserir na tabela `locacao` ---
            sql = """
                    INSERT INTO locacao 
                        (id_cliente, id_veiculo, id_funcionario, status, data_retirada, data_devolucao_prevista,
                         quilometragem_retirada, tanque_saida, valor_total_previsto, caucao, devolucao)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Não devolvido')
                """
            valores = (
                dados_locacao['id_cliente'], dados_locacao['id_veiculo'],
                dados_locacao.get('id_funcionario', 1),  # Usa 1 como padrão
                dados_locacao.get('status', 'Reserva'),
                dados_locacao['data_retirada'], dados_locacao['data_devolucao_prevista'],
                km_saida, tanque_saida,
                dados_locacao.get('valor_total_previsto',
                                  valor_total_previsto), caucao
            )
            cursor.execute(sql, valores)
            id_locacao = cursor.lastrowid

            # --- 4. Inserir opcionais ---
            if opcionais:
                for op in opcionais:
                    cursor.execute("""
                        INSERT INTO locacao_opcional (id_locacao, id_opcional, quantidade)
                        VALUES (%s, %s, %s)
                    """, (id_locacao, op["id_opcional"], op.get("quantidade", 1)))

            # --- 5. Atualizar status do veículo para 'Alugado' (indisponível) ---
            cursor.execute(
                "UPDATE veiculo SET id_status_veiculo = 2 WHERE id_veiculo = %s", (dados_locacao['id_veiculo'],))

            conn.commit()
            return id_locacao

        except Exception as e:
            conn.rollback()
            # Propaga a exceção para que a rota possa tratá-la
            raise e
        finally:
            cursor.close()
            conn.close()

    # Atualiza uma locação existente
    def atualizar_locacao(self, id_loc, dados):
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        try:
            # 1. Pegar dados da locação existente
            cursor.execute("""
                SELECT status, data_retirada, data_devolucao_prevista, quilometragem_retirada, 
                       id_veiculo, tanque_saida, valor_total_previsto
                FROM locacao 
                WHERE id_locacao=%s
            """, (id_loc,))
            loc_original = cursor.fetchone()

            if not loc_original:
                raise Exception("Locação não encontrada")

            # 2. Preparar variáveis e validar
            status_novo = dados.get("status", loc_original["status"])
            km_chegada = dados.get("quilometragem_devolucao")
            tanque_chegada = dados.get("tanque_chegada")

            if status_novo == "Chegada":
                if not dados.get("data_devolucao_real"):
                    raise ValueError(
                        "Data de chegada real é obrigatória para o status 'Chegada'")
                if km_chegada is None or km_chegada == "":
                    raise ValueError(
                        "Quilometragem de chegada é obrigatória para o status 'Chegada'")
                if int(km_chegada) < loc_original["quilometragem_retirada"]:
                    raise ValueError(
                        "Quilometragem de chegada não pode ser menor que a de saída")
                if tanque_chegada is None or tanque_chegada == "":
                    raise ValueError(
                        "Tanque de chegada é obrigatório para o status 'Chegada'")

            # 3. Montar a query de atualização dinamicamente
            campos_update = []
            valores_update = []

            # Campos simples
            for campo in ["status", "caucao", "devolucao"]:
                if campo in dados:
                    campos_update.append(f"{campo}=%s")
                    valores_update.append(dados[campo])

            # Campos de data
            for campo_data in ["data_retirada", "data_devolucao_prevista", "data_devolucao_real"]:
                if campo_data in dados and dados[campo_data]:
                    campos_update.append(f"{campo_data}=%s")
                    valores_update.append(datetime.strptime(
                        dados[campo_data], "%Y-%m-%dT%H:%M"))

            # Campos de chegada (KM e Tanque)
            if status_novo == "Chegada":
                if km_chegada is not None:
                    campos_update.append("quilometragem_devolucao=%s")
                    valores_update.append(int(km_chegada))
                if tanque_chegada is not None:
                    campos_update.append("tanque_chegada=%s")
                    valores_update.append(int(tanque_chegada))

            # 4. Recalcular valor previsto se as datas mudaram
            if "data_retirada" in dados or "data_devolucao_prevista" in dados:
                dt_retirada = datetime.strptime(dados["data_retirada"], "%Y-%m-%dT%H:%M") if "data_retirada" in dados and dados.get(
                    "data_retirada") else loc_original["data_retirada"]
                dt_prevista = datetime.strptime(dados["data_devolucao_prevista"], "%Y-%m-%dT%H:%M") if "data_devolucao_prevista" in dados and dados.get(
                    "data_devolucao_prevista") else loc_original["data_devolucao_prevista"]

                cursor.execute(
                    "SELECT id_opcional, quantidade FROM locacao_opcional WHERE id_locacao=%s", (id_loc,))
                opcionais_db = cursor.fetchall()

                valor_previsto_recalculado = self._calcular_valor_previsto(
                    loc_original["id_veiculo"], dt_retirada, dt_prevista, opcionais_db, cursor)

                campos_update.append("valor_total_previsto=%s")
                valores_update.append(valor_previsto_recalculado)

            # 5. Executar a atualização da locação
            if campos_update:
                sql_update = f"UPDATE locacao SET {', '.join(campos_update)} WHERE id_locacao=%s"
                valores_update.append(id_loc)
                cursor.execute(sql_update, tuple(valores_update))

            # 6. Atualizar o status do veículo
            id_status_veiculo = None
            if status_novo == "Chegada":
                id_status_veiculo = 1  # Disponível
                # Atualiza KM e Tanque do veículo
                if km_chegada is not None:
                    cursor.execute(
                        "UPDATE veiculo SET quilometragem=%s WHERE id_veiculo=%s", (int(km_chegada), loc_original["id_veiculo"]))
                if tanque_chegada is not None:
                    cursor.execute(
                        "UPDATE veiculo SET tanque_fracao=%s WHERE id_veiculo=%s", (int(tanque_chegada) / 8.0, loc_original["id_veiculo"]))

            elif status_novo in ["Locado", "Reserva"]:
                id_status_veiculo = 2  # Alugado

            if id_status_veiculo:
                cursor.execute(
                    "UPDATE veiculo SET id_status_veiculo=%s WHERE id_veiculo=%s", (id_status_veiculo, loc_original["id_veiculo"]))

            conn.commit()

            # 7. Retornar os valores atualizados para a API
            cursor.execute(
                "SELECT valor_total_previsto, valor_final FROM locacao WHERE id_locacao=%s", (id_loc,))
            valores_finais = cursor.fetchone()

            return {
                "valor_total_previsto": float(valores_finais["valor_total_previsto"]),
                "valor_final": float(valores_finais["valor_final"]) if valores_finais["valor_final"] is not None else None
            }

        except Exception as e:
            conn.rollback()
            raise e  # Propaga a exceção para a rota tratar
        finally:
            cursor.close()
            conn.close()

    # Busca uma locação específica por ID, incluindo dados relacionados
    def obter_por_id(self, id_locacao):
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        try:
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

            if not loc:
                return None, None

            cursor.execute("""
                SELECT o.id_opcional, o.descricao, lo.quantidade
                FROM locacao_opcional lo
                JOIN opcional o ON o.id_opcional = lo.id_opcional
                WHERE lo.id_locacao = %s
            """, (id_locacao,))
            opcionais = cursor.fetchall()

            # Formatação para consistência
            if loc.get('cliente_validade'):
                loc['cliente_validade'] = loc['cliente_validade'].strftime(
                    '%Y-%m-%d')

            return loc, opcionais
        finally:
            cursor.close()
            conn.close()

    # Busca clientes
    def buscar_clientes_autocomplete(self, termo):
        if not termo or len(termo) < 2:
            return []
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        try:
            sql = """
                SELECT c.id_cliente, c.nome_completo, c.cpf, ch.numero_registro as cnh, ch.data_validade
                FROM cliente c
                JOIN cnh ch ON c.id_cnh = ch.id_cnh
                WHERE c.nome_completo LIKE %s OR c.cpf LIKE %s
                LIMIT 10
            """
            like_termo = f"%{termo}%"
            cursor.execute(sql, (like_termo, like_termo))
            clientes = cursor.fetchall()
            for c in clientes:
                c['data_validade'] = c['data_validade'].strftime("%Y-%m-%d")
            return clientes
        finally:
            cursor.close()
            conn.close()

    # Lista todas as categorias de veículos
    def listar_categorias_veiculos(self):
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id_categoria_veiculo AS id, nome_categoria AS nome, valor_diaria
                FROM categoria_veiculo
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    # Lista veículos disponíveis por categoria
    def listar_veiculos_por_categoria(self, id_categoria):
        if not id_categoria:
            return []
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT v.id_veiculo, v.placa, v.quilometragem, m.nome_modelo, ma.nome_marca
                FROM veiculo v
                JOIN modelo m ON v.id_modelo = m.id_modelo
                JOIN marca ma ON m.id_marca = ma.id_marca
                WHERE m.id_categoria_veiculo=%s AND v.id_status_veiculo=1
            """, (id_categoria,))
            veiculos = cursor.fetchall()
            return [{"id": v["id_veiculo"], "descricao": f'{v["placa"]} - {v["nome_modelo"]} - {v["nome_marca"]}'} for v in veiculos]
        finally:
            cursor.close()
            conn.close()

    # Obtém detalhes de um veículo específico (placa, km, caução, etc.)
    def obter_detalhes_veiculo(self, id_veiculo):
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT v.id_veiculo, v.placa, v.quilometragem, v.tanque_fracao, cv.valor_caucao
                FROM veiculo v
                JOIN modelo m ON v.id_modelo = m.id_modelo
                JOIN categoria_veiculo cv ON m.id_categoria_veiculo = cv.id_categoria_veiculo
                WHERE v.id_veiculo=%s
            """, (id_veiculo,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    # Lista os opcionais disponíveis para locação
    def listar_opcionais_disponiveis(self):
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id_opcional, descricao, valor_diaria FROM opcional")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    # Lista o histórico de locações com base no perfil do usuário (Cliente ou Funcionário)
    def listar_historico(self, perfil, email_usuario):
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        try:
            params = []
            where_clause = ""
            if perfil == "cliente":
                cursor.execute(
                    "SELECT id_cliente FROM cliente WHERE email = %s", (email_usuario,))
                cliente = cursor.fetchone()
                if not cliente:
                    return []
                where_clause = "WHERE l.id_cliente = %s"
                params.append(cliente['id_cliente'])

            sql = f"""
                SELECT l.id_locacao, l.status, l.data_retirada, l.data_devolucao_prevista,
                       l.data_devolucao_real, l.valor_total_previsto, l.valor_final,
                       c.nome_completo, v.placa, m.nome_modelo, ma.nome_marca
                FROM locacao l
                JOIN cliente c ON l.id_cliente = c.id_cliente
                JOIN veiculo v ON l.id_veiculo = v.id_veiculo
                JOIN modelo m ON v.id_modelo = m.id_modelo
                JOIN marca ma ON m.id_marca = ma.id_marca
                {where_clause}
                ORDER BY l.id_locacao DESC
            """
            cursor.execute(sql, tuple(params))
            locacoes = cursor.fetchall()

            for loc in locacoes:
                loc["data_retirada"] = loc["data_retirada"].strftime(
                    "%Y-%m-%d %H:%M")
                loc["data_devolucao_prevista"] = loc["data_devolucao_prevista"].strftime(
                    "%Y-%m-%d %H:%M")
                loc["data_devolucao_real"] = loc["data_devolucao_real"].strftime(
                    "%Y-%m-%d %H:%M") if loc["data_devolucao_real"] else "N/A"
                loc["veiculo"] = f'{loc["placa"]} - {loc["nome_modelo"]} ({loc["nome_marca"]})'
            return locacoes
        finally:
            cursor.close()
            conn.close()

    # Simula o valor final de uma locação com base nos dados de chegada (quilometragem, tanque, atraso, etc.)
    def simular_valor_final(self, id_loc, dados_chegada):
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT l.data_devolucao_prevista, l.valor_total_previsto, l.tanque_saida, v.valor_fracao
                FROM locacao l JOIN veiculo v ON l.id_veiculo = v.id_veiculo
                WHERE l.id_locacao=%s
            """, (id_loc,))
            loc_data = cursor.fetchone()

            if not loc_data:
                return {"erro": "Locação não encontrada"}

            # Lógica de cálculo
            taxa_diaria_atraso = 400.00
            percentual_multa_fixa = 0.20
            valor_final = float(loc_data['valor_total_previsto'])
            dt_prevista = loc_data['data_devolucao_prevista']
            dt_real = datetime.strptime(
                dados_chegada['data_devolucao_real'], "%Y-%m-%dT%H:%M")

            if dt_real > dt_prevista:
                dias_atraso = math.ceil(
                    (dt_real - dt_prevista).total_seconds() / 3600 / 24.0)
                valor_final += (valor_final * percentual_multa_fixa) + \
                    (dias_atraso * taxa_diaria_atraso)

            tanque_chegada = int(dados_chegada['tanque_chegada'])
            tanque_saida = int(loc_data['tanque_saida'])
            if tanque_chegada < tanque_saida:
                fracoes_faltando = tanque_saida - tanque_chegada
                valor_final += fracoes_faltando * \
                    float(loc_data['valor_fracao'])

            return {
                "valor_total_previsto": float(loc_data["valor_total_previsto"]),
                "valor_final": round(valor_final, 2)
            }
        finally:
            cursor.close()
            conn.close()
