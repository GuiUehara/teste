from db import conectar


class ManutencaoModel:
    # Lista veículos disponíveis para manutenção
    def listar_veiculos_para_manutencao(self):
        try:
            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_veiculo, placa FROM veiculo WHERE id_status_veiculo = 1")
            return cursor.fetchall()
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

    # Cadastra uma nova manutenção
    def cadastrar(self, dados_manutencao):
        try:
            conexao = conectar()
            cursor = conexao.cursor()
            sql = "INSERT INTO manutencao (data_entrada, data_saida, descricao_servico, custo, id_veiculo) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, dados_manutencao)
            cursor.execute(
                "UPDATE veiculo SET id_status_veiculo = 3 WHERE id_veiculo = %s", (dados_manutencao[4],))
            conexao.commit()
            return True
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

    # Lista o histórico de manutenções
    def listar_historico(self):
        try:
            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)
            sql = """
                SELECT m.id_manutencao, m.data_entrada, m.data_saida, m.descricao_servico,
                       m.custo, m.status, v.placa, mo.nome_modelo
                FROM manutencao m
                JOIN veiculo v ON m.id_veiculo = v.id_veiculo
                JOIN modelo mo ON v.id_modelo = mo.id_modelo
                ORDER BY m.data_entrada DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

    def atualizar_status(self, id_manutencao, novo_status, id_veiculo):
        """Atualiza o status de uma manutenção e do veículo correspondente."""
        try:
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute(
                "UPDATE manutencao SET status=%s WHERE id_manutencao=%s", (novo_status, id_manutencao))
            id_status_veiculo = 1 if novo_status == "Concluída" else 3
            cursor.execute(
                "UPDATE veiculo SET id_status_veiculo=%s WHERE id_veiculo=%s", (id_status_veiculo, id_veiculo))
            conexao.commit()
            return True
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()
