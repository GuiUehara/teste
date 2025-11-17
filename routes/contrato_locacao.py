from flask import Flask, request, jsonify, render_template
from db import conectar
from datetime import datetime
import math

# Valor padrão de multa por fração de combustível, caso não exista no veículo
VALOR_MULTA_COMBUSTIVEL_PADRAO = 50.00 

def init_locacao(app):

    # CONVERTER DATA PARA O FORMATO CORRETO
    def parse_datetime(valor):
        if not valor or valor == "":
            return None

        try:
            # Remove o Z do final (ISO 8601)
            valor = valor.replace("Z", "")

            # Se vier com milissegundos: 2025-11-02T02:57:00.000
            if "." in valor:
                valor = valor.split(".")[0]

            # Troca T por espaço (caso exista)
            valor = valor.replace("T", " ")

            # Formato final esperado pelo MySQL
            return datetime.strptime(valor, "%Y-%m-%d %H:%M:%S")

        except:
            # Caso venha sem segundos: 2025-11-02 02:57
            try:
                return datetime.strptime(valor, "%Y-%m-%d %H:%M")
            except:
                raise ValueError(f"Formato inválido: {valor}")




    # --- Páginas HTML ---
    @app.route('/contrato_locacao')
    def contrato_locacao():
        return render_template('contrato_locacao.html')

    @app.route('/historico_locacao')
    def historico_locacao():
        return render_template('historico_locacao.html')

    # --- APIs de suporte ---
    @app.route('/api/clientes')
    def api_clientes():
        termo = request.args.get('termo','').strip()
        conn = conectar()
        if not conn: return jsonify({'erro':'Erro de conexão'}), 500
        try:
            cur = conn.cursor(dictionary=True)
            q = """
            SELECT c.id_cliente, c.nome_completo, c.cpf, cn.numero_registro AS cnh_numero, cn.data_validade AS cnh_validade
            FROM cliente c
            JOIN cnh cn ON c.id_cnh = cn.id_cnh
            WHERE c.cpf LIKE %s OR c.nome_completo LIKE %s
            LIMIT 20
            """
            like = f"%{termo}%"
            cur.execute(q, (like, like))
            rows = cur.fetchall()
            resultados = []
            for r in rows:
                resultados.append({
                    'id_cliente': r['id_cliente'],
                    'texto': f"{r['cpf']} - {r['nome_completo']}",
                    'cpf': r['cpf'],
                    'cnh_numero': r['cnh_numero'],
                    'cnh_validade': r['cnh_validade'].strftime('%Y-%m-%d') if r['cnh_validade'] else ''
                })
            return jsonify(resultados)
        except Exception as e:
            return jsonify({'erro': str(e)}), 500
        finally:
            cur.close(); conn.close()

    @app.route('/api/categorias')
    def api_categorias():
        conn = conectar()
        if not conn: return jsonify({'erro':'Erro de conexão'}), 500
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT id_categoria_veiculo, nome_categoria, valor_diaria FROM categoria_veiculo")
            return jsonify(cur.fetchall())
        finally:
            cur.close(); conn.close()

    @app.route('/api/veiculos')
    def api_veiculos():
        categoria_id = request.args.get('categoria_id')
        categoria_nome = request.args.get('categoria_nome')
        conn = conectar()
        if not conn: return jsonify({'erro':'Erro de conexão'}), 500
        try:
            cur = conn.cursor(dictionary=True)
            if categoria_id:
                cur.execute("""
                    SELECT v.id_veiculo, v.placa, v.quilometragem, v.valor_fracao, m.nome_modelo, c.nome_categoria, c.valor_diaria
                    FROM veiculo v
                    JOIN modelo m ON v.id_modelo = m.id_modelo
                    JOIN categoria_veiculo c ON m.id_categoria_veiculo = c.id_categoria_veiculo
                    WHERE c.id_categoria_veiculo=%s AND v.id_status_veiculo=1
                """, (categoria_id,))
            elif categoria_nome:
                cur.execute("""
                    SELECT v.id_veiculo, v.placa, v.quilometragem, v.valor_fracao, m.nome_modelo, c.nome_categoria, c.valor_diaria
                    FROM veiculo v
                    JOIN modelo m ON v.id_modelo = m.id_modelo
                    JOIN categoria_veiculo c ON m.id_categoria_veiculo = c.id_categoria_veiculo
                    WHERE c.nome_categoria=%s AND v.id_status_veiculo=1
                """, (categoria_nome,))
            else:
                cur.execute("""
                    SELECT v.id_veiculo, v.placa, v.quilometragem, v.valor_fracao, m.nome_modelo, c.nome_categoria, c.valor_diaria
                    FROM veiculo v
                    JOIN modelo m ON v.id_modelo = m.id_modelo
                    JOIN categoria_veiculo c ON m.id_categoria_veiculo = c.id_categoria_veiculo
                    WHERE v.id_status_veiculo=1
                """)
            return jsonify(cur.fetchall())
        finally:
            cur.close(); conn.close()

    # --- Cadastro de locacao ---
    # --- Cadastro de locacao com opcionais ---
    @app.route('/api/cadastrar', methods=['POST'])
    def api_cadastrar():
        dados = request.get_json()
        obrig = ['id_cliente','id_veiculo','data_retirada','data_devolucao_prevista','quilometragem_retirada','tanque_saida','caucao','status']
        for campo in obrig:
            if campo not in dados or dados[campo] in [None,'']:
                return jsonify({'erro': f'Campo obrigatório ausente: {campo}'}), 400

        try:
            data_retirada = parse_datetime(dados['data_retirada'])
            data_devol_prevista = parse_datetime(dados['data_devolucao_prevista'])
            if data_retirada is None or data_devol_prevista is None:
                return jsonify({'erro':'Formato de data inválido. Use YYYY-MM-DDTHH:MM'}), 400
        except:
            return jsonify({'erro':'Formato de data inválido. Use YYYY-MM-DDTHH:MM'}),400

        conn = conectar()
        if not conn: return jsonify({'erro':'Erro conexão BD'}),500
        try:
            cur = conn.cursor()
            cur.execute("SELECT id_usuario FROM funcionario LIMIT 1")
            r = cur.fetchone()
            id_func = r[0] if r else 1

            valor_diaria = float(dados.get('valor_diaria') or 0)
            dias = max(1, math.ceil((data_devol_prevista - data_retirada).total_seconds() / 86400))
            
            # valor base da diária x dias
            valor_total_previsto = valor_diaria * dias

            # SOMAR opcionais no valor total previsto
            for o in dados.get('opcionais', []):
                valor_total_previsto += float(o['valor_diaria']) * int(o['quantidade']) * dias
            
            valor_total_previsto = round(valor_total_previsto,2)

            # Inserir locação
            sql = """
                INSERT INTO locacao (
                    data_retirada, data_devolucao_prevista, valor_total_previsto,
                    quilometragem_retirada, id_cliente, id_veiculo, id_funcionario,
                    status, tanque_saida, caucao, devolucao
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            vals = (
                data_retirada, data_devol_prevista, valor_total_previsto,
                int(dados['quilometragem_retirada']), int(dados['id_cliente']), int(dados['id_veiculo']), id_func,
                dados['status'], int(dados['tanque_saida']), float(dados['caucao']), dados.get('devolucao','na devolução')
            )
            cur.execute(sql, vals)
            conn.commit()
            id_loc = cur.lastrowid

            # Atualiza status do veículo se locado
            if dados['status']=='Locado':
                cur.execute("UPDATE veiculo SET id_status_veiculo=2 WHERE id_veiculo=%s",(int(dados['id_veiculo']),))
                conn.commit()

            # --- Inserir opcionais
            for o in dados.get('opcionais', []):
                cur.execute("""
                    INSERT INTO opcional (descricao, valor_diaria)
                    VALUES (%s,%s)
                """, (o['descricao'], float(o['valor_diaria'])))
                id_op = cur.lastrowid
            conn.commit()

            # --- Inserir dados na tabela "locacao_opcional"
            cur.execute("""
            INSERT INTO locacao_opcional (id_locacao, id_opcional, quantidade)
            VALUES (%s, %s, %s)
            """, (id_loc, id_op, int(o['quantidade'])))


            return jsonify({'mensagem':'Locação cadastrada com sucesso','id_locacao':id_loc}),200
        except Exception as e:
            conn.rollback()
            return jsonify({'erro': str(e)}),500
        finally:
            cur.close(); conn.close()


    # --- Listar locacoes ---
    @app.route('/api/locacoes')
    def api_locacoes():
        conn = conectar()
        if not conn: return jsonify({'erro':'Erro conexão'}),500
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT l.id_locacao, l.status,
                    l.data_retirada, l.data_devolucao_prevista, l.data_devolucao_real,
                    l.valor_total_previsto, l.valor_final,
                    l.quilometragem_retirada, l.quilometragem_devolucao,
                    l.tanque_saida, l.tanque_chegada, l.caucao, l.devolucao,
                    c.nome_completo AS cliente_nome, c.cpf AS cliente_cpf,
                    v.placa, m.nome_modelo, ma.nome_marca
                FROM locacao l
                JOIN cliente c ON l.id_cliente=c.id_cliente
                JOIN veiculo v ON l.id_veiculo=v.id_veiculo
                JOIN modelo m ON v.id_modelo=m.id_modelo
                JOIN marca ma ON m.id_marca=ma.id_marca
                ORDER BY l.id_locacao DESC
                LIMIT 200
            """)
            rows = cur.fetchall()
            # Formatar datas
            for r in rows:
                for k in ['data_retirada','data_devolucao_prevista','data_devolucao_real']:
                    # Usa isoformat para datetimes, o valor pode ser None se for NULL no BD
                    if r.get(k) is not None: 
                        r[k] = r[k].isoformat()
            return jsonify(rows)
        finally:
            cur.close(); conn.close()


    # --- Atualizar locacao ---
    # --- Atualização de locação (com datas funcionando corretamente) ---
    @app.route('/api/locacao/<int:id_locacao>', methods=['PUT'])
    def api_atualizar_locacao(id_locacao):
        dados = request.get_json()
        conn = conectar()
        if not conn: 
            return jsonify({'erro':'Erro conexão'}), 500
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM locacao WHERE id_locacao=%s", (id_locacao,))
            loc = cur.fetchone()
            if not loc:
                return jsonify({'erro':'Locação não encontrada'}), 404

            # --- Chegada ---
            # --- Chegada ---
            if dados.get('status') == 'Chegada':
                km_chegada = dados.get('quilometragem_devolucao')
                tanque_chegada = dados.get('tanque_chegada')

                if km_chegada is None or tanque_chegada is None:
                    return jsonify({'erro':'KM e tanque_chegada obrigatórios para chegada'}), 400

                # Buscar dados da locacao e diária
                cur.execute("""
                    SELECT l.*, c.valor_diaria, v.valor_fracao
                    FROM locacao l
                    JOIN veiculo v ON l.id_veiculo = v.id_veiculo
                    JOIN modelo m ON v.id_modelo = m.id_modelo
                    JOIN categoria_veiculo c ON m.id_categoria_veiculo = c.id_categoria_veiculo
                    WHERE l.id_locacao=%s
                """, (id_locacao,))
                info = cur.fetchone()

                valor_diaria = float(info["valor_diaria"])
                valor_fracao = float(info["valor_fracao"] or VALOR_MULTA_COMBUSTIVEL_PADRAO)

                data_real = datetime.now()

                # ---- Calcular dias usados ----
                diff = data_real - info["data_retirada"]
                dias_usados = max(1, math.ceil(diff.total_seconds() / 86400))

                # ---- Multa de combustível ----
                dif_tanque = int(info['tanque_saida']) - int(tanque_chegada)
                multa_comb = max(0, dif_tanque) * valor_fracao

                # ---- Valor final ----
                # --- SOMAR valor dos opcionais usados ---
                cur.execute("""
                    SELECT o.valor_diaria, lo.quantidade
                    FROM locacao_opcional lo
                    JOIN opcional o ON o.id_opcional = lo.id_opcional
                    WHERE lo.id_locacao = %s
                """, (id_locacao,))
                opcs = cur.fetchall()

                valor_opcionais = 0
                for op in opcs:
                    valor_opcionais += float(op['valor_diaria']) * int(op['quantidade']) * dias_usados

                # valor final incluindo opcionais + combustível
                valor_final = round(dias_usados * valor_diaria + multa_comb + valor_opcionais, 2)


                cur.execute("""
                    UPDATE locacao SET
                        status='Chegada',
                        data_devolucao_real=%s,
                        quilometragem_devolucao=%s,
                        tanque_chegada=%s,
                        valor_final=%s
                    WHERE id_locacao=%s
                """, (data_real, km_chegada, tanque_chegada, valor_final, id_locacao))

                # Disponibiliza veículo
                cur.execute("""
                    UPDATE veiculo 
                    SET quilometragem=%s,
                        id_status_veiculo=(SELECT id_status_veiculo FROM status_veiculo WHERE descricao_status='Disponível' LIMIT 1)
                    WHERE id_veiculo=%s
                """, (km_chegada, info['id_veiculo']))

                conn.commit()

                return jsonify({
                    'mensagem': 'Chegada registrada com sucesso!',
                    'dias_usados': dias_usados,
                    'valor_final': valor_final,
                    'multa_combustivel': multa_comb
                })



            # --- Atualização normal ---
            campos_editar = [
                'id_cliente','id_veiculo','id_funcionario','status',
                'data_retirada','data_devolucao_prevista','data_devolucao_real',
                'quilometragem_retirada','quilometragem_devolucao',
                'valor_total_previsto','valor_final','tanque_saida','tanque_chegada',
                'caucao','devolucao'
            ]
            sets, valores = [], []
            for c in campos_editar:
                if c in dados:
                    v = dados[c]
                    if 'data_' in c:
                        v_original_str = v
                        v = parse_datetime(v)
                        if v is None and v_original_str == '':
                            continue  # ignora datas vazias
                        if v is None and v_original_str != '':
                            return jsonify({'erro': f'Formato de data inválido para {c}. Use YYYY-MM-DDTHH:MM'}), 400
                    valores.append(v)
                    sets.append(f"{c}=%s")

            if sets:
                valores.append(id_locacao)
                cur.execute("UPDATE locacao SET " + ",".join(sets) + " WHERE id_locacao=%s", tuple(valores))
                conn.commit()
                return jsonify({'mensagem':'Locação atualizada com sucesso!'})

            return jsonify({'mensagem': 'Nenhum campo para atualizar'}), 200

        except Exception as e:
            conn.rollback()
            return jsonify({'erro': str(e)}), 500
        finally:
            cur.close()
            conn.close()

    # --- Listar todos os opcionais (CATÁLOGO) ---
    @app.route('/api/opcionais', methods=['GET'])
    def api_listar_opcionais():
        conn = conectar()
        if not conn:
            return jsonify({'erro': 'Erro de conexão'}), 500

        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT id_opcional, descricao, valor_diaria FROM opcional")
            dados = cur.fetchall()
            return jsonify(dados)

        finally:
            cur.close()
            conn.close()

    # --- Listar opcionais de uma locação específica ---
    @app.route('/api/opcionais/<int:id_locacao>', methods=['GET'])
    def api_opcionais_da_locacao(id_locacao):
        conn = conectar()
        if not conn:
            return jsonify({'erro': 'Erro de conexão'}), 500

        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT
                    lo.id_locacao_opcional,
                    o.id_opcional,
                    o.descricao,
                    o.valor_diaria,
                    lo.quantidade
                FROM locacao_opcional lo
                JOIN opcional o ON o.id_opcional = lo.id_opcional
                WHERE lo.id_locacao = %s
            """, (id_locacao,))

            return jsonify(cur.fetchall())

        finally:
            cur.close()
            conn.close()


    # --- Adicionar um opcional ---
    @app.route('/api/opcional', methods=['POST'])
    def api_adicionar_opcional():
        dados = request.get_json()
        obrig = ['descricao', 'valor_diaria', 'quantidade', 'id_locacao']
        for campo in obrig:
            if campo not in dados:
                return jsonify({'erro': f'Campo obrigatório ausente: {campo}'}), 400

        conn = conectar()
        if not conn:
            return jsonify({'erro': 'Erro de conexão'}), 500

        try:
            cur = conn.cursor()

            # cria opcional
            cur.execute("""
                INSERT INTO opcional (descricao, valor_diaria)
                VALUES (%s, %s)
            """, (dados['descricao'], float(dados['valor_diaria'])))
            
            id_op = cur.lastrowid

            # cria vínculo N:N
            cur.execute("""
                INSERT INTO locacao_opcional (id_locacao, id_opcional, quantidade)
                VALUES (%s, %s, %s)
            """, (dados['id_locacao'], id_op, dados['quantidade']))

            conn.commit()
            return jsonify({
                'mensagem': 'Opcional adicionado com sucesso',
                'id_opcional': id_op
            })

        finally:
            cur.close()
            conn.close()


    # --- Atualizar um opcional ---
    @app.route('/api/opcional/<int:id_opcional>', methods=['PUT'])
    def api_atualizar_opcional(id_opcional):
        dados = request.get_json()
        campos_editar = ['descricao', 'valor_diaria']
        
        sets = []
        valores = []

        for c in campos_editar:
            if c in dados:
                sets.append(f"{c}=%s")
                valores.append(dados[c])

        if not sets:
            return jsonify({'mensagem': 'Nenhum campo para atualizar'}), 400

        valores.append(id_opcional)

        conn = conectar()
        if not conn:
            return jsonify({'erro': 'Erro de conexão'}), 500

        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE opcional SET " + ",".join(sets) + " WHERE id_opcional=%s",
                tuple(valores)
            )
            conn.commit()
            return jsonify({'mensagem': 'Opcional atualizado com sucesso'})

        finally:
            cur.close()
            conn.close()


    # --- Remover um opcional ---
    @app.route('/api/opcional/<int:id_opcional>', methods=['DELETE'])
    def api_remover_opcional(id_opcional):
        conn = conectar()
        if not conn:
            return jsonify({'erro': 'Erro de conexão'}), 500

        try:
            cur = conn.cursor()

            # remove vínculos primeiro
            cur.execute("DELETE FROM locacao_opcional WHERE id_opcional=%s", (id_opcional,))

            # remove o opcional
            cur.execute("DELETE FROM opcional WHERE id_opcional=%s", (id_opcional,))

            conn.commit()
            return jsonify({'mensagem': 'Opcional removido com sucesso'})

        finally:
            cur.close()
            conn.close()

