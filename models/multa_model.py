from db import conectar


class MultaModel:
    def listar_historico(self):
        """Busca no banco todas as locações que resultaram em multa por atraso."""
        try:
            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)
            sql = """
                SELECT
                    l.id_locacao, c.nome_completo, v.placa, l.valor_total_previsto,
                    l.valor_final, l.data_devolucao_prevista, l.data_devolucao_real,
                    CEILING(
                        TIMESTAMPDIFF(HOUR, l.data_devolucao_prevista, l.data_devolucao_real) / 24.0
                    ) AS dias_atraso
                FROM locacao l
                JOIN cliente c ON l.id_cliente = c.id_cliente
                JOIN veiculo v ON l.id_veiculo = v.id_veiculo
                WHERE l.data_devolucao_real IS NOT NULL
                  AND l.data_devolucao_real > l.data_devolucao_prevista
                ORDER BY l.data_devolucao_real DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()
