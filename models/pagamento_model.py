from db import conectar
from datetime import datetime


class PagamentoModel:
    def get_dados_locacao_para_pagamento(self, id_locacao):
        """Busca os dados da locação necessários para a página de pagamento."""
        try:
            conn = conectar()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT valor_total_previsto, caucao FROM locacao WHERE id_locacao = %s", (id_locacao,))
            locacao = cursor.fetchone()
            return locacao
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def get_formas_pagamento(self):
        """Busca todas as formas de pagamento disponíveis."""
        try:
            conn = conectar()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_forma_pagamento, descricao_pagamento FROM forma_pagamento")
            return cursor.fetchall()
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

    def registrar_pagamento(self, id_locacao, id_forma_pagamento, valor):
        """Insere um novo registro de pagamento no banco de dados."""
        with conectar() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO pagamento (id_locacao, id_forma_pagamento, valor, data_pagamento) VALUES (%s, %s, %s, %s)",
                    (id_locacao, id_forma_pagamento, valor, datetime.now())
                )
                conn.commit()
