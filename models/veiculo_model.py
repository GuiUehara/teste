from db import conectar


class VeiculoModel:
    """
    Modelo responsável por todas as operações de banco de dados
    relacionadas aos veículos.
    """

    # Busca de dados como combustíveis, status, seguros, marcas e modelos
    def get_dados_suporte(self):
        try:
            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)

            cursor.execute(
                "SELECT id_combustivel, tipo_combustivel FROM combustivel")
            combustiveis = cursor.fetchall()

            cursor.execute(
                "SELECT id_status_veiculo, descricao_status FROM status_veiculo")
            status = cursor.fetchall()

            cursor.execute("SELECT id_seguro, companhia FROM seguro")
            seguros = cursor.fetchall()

            cursor.execute("SELECT * FROM marca")
            marcas = cursor.fetchall()

            cursor.execute(
                "SELECT mo.*, c.nome_categoria FROM modelo mo JOIN categoria_veiculo c ON mo.id_categoria_veiculo = c.id_categoria_veiculo")
            modelos = cursor.fetchall()

            return {
                "combustiveis": combustiveis,
                "status": status,
                "seguros": seguros,
                "marcas": marcas,
                "modelos": modelos
            }
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

    # Insere um novo veículo no banco de dados
    def cadastrar(self, dados_veiculo, id_seguro, vencimento_seguro):
        try:
            conexao = conectar()
            cursor = conexao.cursor()

            cursor.execute(
                "SELECT 1 FROM veiculo WHERE placa = %s", (dados_veiculo[0],))
            if cursor.fetchone():
                return "placa_duplicada"

            cursor.execute(
                "SELECT 1 FROM veiculo WHERE chassi = %s", (dados_veiculo[3],))
            if cursor.fetchone():
                return "chassi_duplicado"

            sql = """
                INSERT INTO veiculo
                (placa, ano, chassi, quilometragem, transmissao, data_compra,
                valor_compra, data_vencimento, tanque, tanque_fracao, valor_fracao,
                id_modelo, id_status_veiculo, id_combustivel, id_seguro, imagem, vencimento_seguro)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
            
            # Adiciona o vencimento_seguro no final da lista de dados
            valores = list(dados_veiculo)
            valores.append(vencimento_seguro)
            
            cursor.execute(sql, tuple(valores))

            conexao.commit()
            return "sucesso"
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

    # Atualiza os dados de um veículo existente
    def editar(self, id_veiculo, dados_veiculo, id_seguro, vencimento_seguro, nova_imagem=None):
        try:
            conexao = conectar()
            cursor = conexao.cursor()

            # --- 1. VERIFICAÇÕES ---
            
            # Verifica se a PLACA já existe em outro veículo (dados_veiculo[0] é a placa)
            cursor.execute(
                "SELECT id_veiculo FROM veiculo WHERE placa=%s AND id_veiculo != %s", 
                (dados_veiculo[0], id_veiculo)
            )
            if cursor.fetchone():
                return "placa_duplicada"

            # Verifica se o CHASSI já existe em outro veículo (dados_veiculo[1] é o chassi)
            cursor.execute(
                "SELECT id_veiculo FROM veiculo WHERE chassi=%s AND id_veiculo != %s", 
                (dados_veiculo[1], id_veiculo)
            )
            if cursor.fetchone():
                return "chassi_duplicado"

            # --- 2. ATUALIZAÇÃO) ---

            sql = """
                UPDATE veiculo SET
                    placa=%s, chassi=%s, ano=%s, transmissao=%s, data_compra=%s,
                    valor_compra=%s, quilometragem=%s, data_vencimento=%s, tanque=%s,
                    tanque_fracao=%s, id_combustivel=%s, id_modelo=%s, id_status_veiculo=%s, 
                    id_seguro=%s, vencimento_seguro=%s
            """
            
            valores = list(dados_veiculo)
            valores.append(vencimento_seguro)

            if nova_imagem:
                sql += ", imagem=%s"
                valores.append(nova_imagem)

            sql += " WHERE id_veiculo=%s"
            valores.append(id_veiculo)

            cursor.execute(sql, tuple(valores))
            

            conexao.commit()
            return "sucesso"
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

    # Busca um veículo pelo ID
    def obter_por_id(self, id_veiculo):
        try:
            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("""
                SELECT v.*, 
                       m.id_marca, m.nome_marca, 
                       mo.id_modelo, mo.nome_modelo,
                       c.nome_categoria AS nome_categoria, 
                       s.id_status_veiculo, s.descricao_status, 
                       comb.id_combustivel, comb.tipo_combustivel,
                       seg.id_seguro, seg.companhia, 
                       v.vencimento_seguro AS vencimento_seguro -- <--- CORRIGIDO AQUI
                FROM veiculo v
                JOIN modelo mo ON v.id_modelo = mo.id_modelo
                JOIN marca m ON mo.id_marca = m.id_marca
                JOIN categoria_veiculo c ON mo.id_categoria_veiculo = c.id_categoria_veiculo
                JOIN status_veiculo s ON v.id_status_veiculo = s.id_status_veiculo
                JOIN combustivel comb ON v.id_combustivel = comb.id_combustivel
                LEFT JOIN seguro seg ON v.id_seguro = seg.id_seguro
                WHERE v.id_veiculo=%s
            """, (id_veiculo,))
            return cursor.fetchone()
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

    def editar(self, id_veiculo, dados_veiculo, id_seguro, vencimento_seguro, nova_imagem=None):
        """Atualiza os dados de um veículo no banco."""
        try:
            conexao = conectar()
            cursor = conexao.cursor()

            # Verifica duplicidade de placa (excluindo o próprio veículo)
            cursor.execute(
                "SELECT id_veiculo FROM veiculo WHERE placa=%s AND id_veiculo != %s", (dados_veiculo[0], id_veiculo))
            if cursor.fetchone():
                return "placa_duplicada"

            # Verifica duplicidade de chassi
            cursor.execute(
                "SELECT id_veiculo FROM veiculo WHERE chassi=%s AND id_veiculo != %s", (dados_veiculo[1], id_veiculo))
            if cursor.fetchone():
                return "chassi_duplicado"

            # Atualização do veículo
            sql = """
                UPDATE veiculo SET
                    placa=%s, chassi=%s, ano=%s, transmissao=%s, data_compra=%s,
                    valor_compra=%s, quilometragem=%s, data_vencimento=%s, tanque=%s,
                    tanque_fracao=%s, id_combustivel=%s, id_modelo=%s, id_status_veiculo=%s, id_seguro=%s
            """
            
            valores = list(dados_veiculo)

            if nova_imagem:
                sql += ", imagem=%s"
                valores.append(nova_imagem)
            
            sql += " WHERE id_veiculo=%s"
            valores.append(id_veiculo)

            cursor.execute(sql, tuple(valores))
            
            cursor.execute(
                "UPDATE seguro SET vencimento=%s WHERE id_seguro=%s", (vencimento_seguro, id_seguro))

            conexao.commit()
            return "sucesso"
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

    # Deleta um veículo do banco de dados
    def deletar(self, id_veiculo):
        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute(
                "DELETE FROM veiculo WHERE id_veiculo=%s", (id_veiculo,))
            conexao.commit()
            return cursor.rowcount > 0
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

    # Lista os veículos, com opção de busca por placa, modelo ou marca
    def listar(self, termo_busca=None):
        try:
            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)
            sql = """
                SELECT v.id_veiculo, v.placa, v.ano, v.quilometragem, v.transmissao,
                       mo.nome_modelo, ma.nome_marca, c.nome_categoria, s.descricao_status
                FROM veiculo v
                JOIN modelo mo ON v.id_modelo = mo.id_modelo
                JOIN marca ma ON mo.id_marca = ma.id_marca
                JOIN categoria_veiculo c ON mo.id_categoria_veiculo = c.id_categoria_veiculo
                JOIN status_veiculo s ON v.id_status_veiculo = s.id_status_veiculo
            """
            if termo_busca:
                sql += " WHERE v.placa LIKE %s OR mo.nome_modelo LIKE %s OR ma.nome_marca LIKE %s"
                cursor.execute(sql, (f"%{termo_busca}%", f"%{termo_busca}%", f"%{termo_busca}%"))
            else:
                cursor.execute(sql)
            return cursor.fetchall()
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()
