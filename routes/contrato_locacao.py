# app.py
from flask import Flask, request, jsonify, render_template
from db import conectar
from datetime import datetime
import math

VALOR_MULTA_COMBUSTIVEL_PADRAO = 50.00  # fallback caso não exista valor_fracao

def init_locacao(app):

    # --- Páginas HTML ---
    @app.route('/contrato_locacao')
    def contrato_locacao():
        return render_template('contrato_locacao.html')

    @app.route('/historico_locacao')
    def historico_locacao():
        return render_template('historico_locacao.html')

    # --- APIs de suporte (clientes, categorias, veiculos) ---
    @app.route('/api/clientes')
    def api_clientes():
        termo = request.args.get('termo','').strip()
        conn = conectar()
        if not conn:
            return jsonify({'erro':'Erro de conexão'}), 500
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
            veiculos = cur.fetchall()
            return jsonify(veiculos)
        finally:
            cur.close(); conn.close()

    # --- Cadastro de locacao (POST) ---
    @app.route('/api/cadastrar', methods=['POST'])
    def api_cadastrar():
        dados = request.get_json()
        obrig = ['id_cliente','id_veiculo','data_retirada','data_devolucao_prevista','quilometragem_retirada','tanque_saida','caucao','status']
        for campo in obrig:
            if campo not in dados or dados[campo] in [None, '']:
                return jsonify({'erro': f'Campo obrigatório ausente: {campo}'}), 400

        try:
            data_retirada = datetime.fromisoformat(dados['data_retirada'])
            data_devol_prevista = datetime.fromisoformat(dados['data_devolucao_prevista'])
        except:
            return jsonify({'erro': 'Formato de data inválido. Use YYYY-MM-DDTHH:MM'}), 400

        conn = conectar()
        if not conn: return jsonify({'erro':'Erro conexão BD'}), 500
        try:
            cur = conn.cursor()

            # id_funcionario fixo
            cur.execute("SELECT id_usuario FROM funcionario LIMIT 1")
            r = cur.fetchone()
            id_func = r[0] if r else 1

            valor_diaria = float(dados.get('valor_diaria', 0) or 0)
            segundos = (data_devol_prevista - data_retirada).total_seconds()
            dias = max(1, math.ceil(segundos / (24*3600)))
            valor_total_previsto = round(valor_diaria * dias, 2)

            sql = """
                INSERT INTO locacao (
                    data_retirada, data_devolucao_prevista, valor_total_previsto,
                    quilometragem_retirada, id_cliente, id_veiculo, id_funcionario,
                    status, local_retirada, local_devolucao, tanque_saida, caucao, devolucao
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            vals = (
                data_retirada, data_devol_prevista, valor_total_previsto,
                int(dados['quilometragem_retirada']), int(dados['id_cliente']), int(dados['id_veiculo']), id_func,
                dados['status'], dados.get('local_retirada',''), dados.get('local_devolucao',''),
                int(dados['tanque_saida']), float(dados['caucao']), dados.get('devolucao','na devolução')
            )
            cur.execute(sql, vals)
            conn.commit()
            id_loc = cur.lastrowid

            if dados['status'] == 'Locado':
                cur.execute("UPDATE veiculo SET id_status_veiculo=2 WHERE id_veiculo=%s", (int(dados['id_veiculo']),))
                conn.commit()

            return jsonify({'mensagem':'Locação cadastrada com sucesso','id_locacao': id_loc}), 200
        except Exception as e:
            conn.rollback()
            return jsonify({'erro': str(e)}), 500
        finally:
            cur.close(); conn.close()

    # --- Listar locacoes (historico) ---
    @app.route('/api/locacoes')
    def api_locacoes():
        conn = conectar()
        if not conn: return jsonify({'erro':'Erro conexão'}), 500
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("""
                SELECT l.id_locacao, l.status, l.local_retirada, l.local_devolucao,
                    l.data_retirada, l.data_devolucao_prevista, l.data_devolucao_real,
                    l.valor_total_previsto, l.valor_final,
                    l.quilometragem_retirada, l.quilometragem_devolucao,
                    l.tanque_saida, l.tanque_chegada, l.caucao, l.devolucao,
                    c.nome_completo AS cliente_nome, c.cpf AS cliente_cpf,
                    v.placa, m.nome_modelo, ma.nome_marca
                FROM locacao l
                JOIN cliente c ON l.id_cliente = c.id_cliente
                JOIN veiculo v ON l.id_veiculo = v.id_veiculo
                JOIN modelo m ON v.id_modelo = m.id_modelo
                JOIN marca ma ON m.id_marca = ma.id_marca
                ORDER BY l.id_locacao DESC
                LIMIT 200
            """)
            rows = cur.fetchall()
            for r in rows:
                for k in ['data_retirada','data_devolucao_prevista','data_devolucao_real']:
                    if r.get(k):
                        r[k] = r[k].isoformat()
            return jsonify(rows)
        finally:
            cur.close(); conn.close()

    # --- Atualizar locacao (edição COMPLETA) ---
    @app.route('/api/locacao/<int:id_locacao>', methods=['PUT'])
    def api_atualizar_locacao(id_locacao):
        dados = request.get_json()
        conn = conectar()
        if not conn:
            return jsonify({'erro':'Erro conexão'}), 500

        try:
            cur = conn.cursor(dictionary=True)

            # Verifica se existe
            cur.execute("SELECT * FROM locacao WHERE id_locacao=%s", (id_locacao,))
            loc = cur.fetchone()
            if not loc:
                return jsonify({'erro': 'Locação não encontrada'}), 404

            # EDIÇÃO NORMAL (SEM CHEGADA)
            campos_editar = [
                'id_cliente','id_veiculo','id_funcionario','status','local_retirada','local_devolucao',
                'data_retirada','data_devolucao_prevista','quilometragem_retirada',
                'valor_total_previsto','valor_final','tanque_saida','caucao','devolucao'
            ]

            sets = []
            valores = []

            for c in campos_editar:
                if c in dados:
                    if 'data_' in c:
                        valores.append(datetime.fromisoformat(dados[c]))
                    else:
                        valores.append(dados[c])
                    sets.append(f"{c}=%s")

            # SE STATUS = CHEGADA então processa normalmente
            if dados.get('status') == 'Chegada':
                km_chegada = dados.get('quilometragem_devolucao')
                tanque_chegada = dados.get('tanque_chegada')

                if km_chegada is None or tanque_chegada is None:
                    return jsonify({'erro':'KM e tanque_chegada obrigatórios para chegada'}), 400

                cur.execute("""
                    SELECT v.valor_fracao, c.valor_diaria
                    FROM veiculo v
                    JOIN modelo m ON v.id_modelo = m.id_modelo
                    JOIN categoria_veiculo c ON m.id_categoria_veiculo = c.id_categoria_veiculo
                    WHERE v.id_veiculo=%s
                """, (loc['id_veiculo'],))
                info = cur.fetchone()

                valor_fracao = float(info['valor_fracao'] or VALOR_MULTA_COMBUSTIVEL_PADRAO)
                valor_diaria = float(info['valor_diaria'] or 0)

                # atraso
                data_prevista = loc['data_devolucao_prevista']
                data_real = datetime.now()

                multa_atraso = 0
                if data_real > data_prevista:
                    dias = math.ceil((data_real - data_prevista).total_seconds() / 86400)
                    multa_atraso = round(dias * valor_diaria * 2, 2)

                # combustível
                dif_tanque = int(loc['tanque_saida']) - int(tanque_chegada)
                multa_comb = round(max(0, dif_tanque) * valor_fracao, 2)

                valor_final = round(loc['valor_total_previsto'] + multa_atraso + multa_comb, 2)

                # Atualiza chegada
                cur.execute("""
                    UPDATE locacao SET status='Chegada',
                        data_devolucao_real=%s, quilometragem_devolucao=%s,
                        tanque_chegada=%s, valor_final=%s
                    WHERE id_locacao=%s
                """, (data_real, km_chegada, tanque_chegada, valor_final, id_locacao))

                conn.commit()
                return jsonify({'mensagem':'Chegada registrada com sucesso!','valor_final': valor_final})

            # Atualização normal
            if sets:
                sql = "UPDATE locacao SET " + ", ".join(sets) + " WHERE id_locacao=%s"
                valores.append(id_locacao)
                cur.execute(sql, tuple(valores))
                conn.commit()

            return jsonify({'mensagem':'Locação atualizada com sucesso!'})
        except Exception as e:
            conn.rollback()
            return jsonify({'erro': str(e)}), 500
        finally:
            cur.close(); conn.close()
