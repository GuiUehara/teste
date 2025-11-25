from db import conectar


class ClienteModel:
    """
    Modelo responsável por todas as operações de banco de dados
    relacionadas aos clientes.
    """

    def cadastrar(self, dados_cliente, dados_endereco, dados_cnh):
        """Insere um novo cliente, endereço e CNH no banco de dados."""
        try:
            conexao = conectar()
            cursor = conexao.cursor()

            # Inserir Endereço
            sql_endereco = "INSERT INTO endereco (logradouro, numero, complemento, bairro, cidade, estado, cep) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql_endereco, dados_endereco)
            id_endereco = cursor.lastrowid

            # Inserir CNH
            sql_cnh = "INSERT INTO cnh (numero_registro, categoria, data_validade) VALUES (%s, %s, %s)"
            cursor.execute(sql_cnh, dados_cnh)
            id_cnh = cursor.lastrowid

            # Inserir Cliente
            sql_cliente = "INSERT INTO cliente (nome_completo, cpf, data_nascimento, telefone, email, tempo_habilitacao_anos, id_endereco, id_cnh) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values_cliente = dados_cliente + (id_endereco, id_cnh)
            cursor.execute(sql_cliente, values_cliente)

            conexao.commit()
            return True
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

    def listar(self, termo_busca=None):
        """Lista os clientes, com opção de busca."""
        try:
            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)
            if termo_busca and len(termo_busca) >= 3:
                sql = "SELECT id_cliente, nome_completo, cpf, email FROM cliente WHERE nome_completo LIKE %s OR cpf LIKE %s OR email LIKE %s"
                like = f"%{termo_busca}%"
                cursor.execute(sql, (like, like, like))
            else:
                cursor.execute(
                    "SELECT id_cliente, nome_completo, cpf, email FROM cliente")

            clientes = cursor.fetchall()
            return clientes
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

    def obter_por_id(self, id_cliente):
        """Busca um cliente completo pelo seu ID."""
        try:
            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(
                "SELECT c.*, e.*, n.* FROM cliente c JOIN endereco e ON c.id_endereco = e.id_endereco JOIN cnh n ON c.id_cnh = n.id_cnh WHERE c.id_cliente = %s", (id_cliente,))
            return cursor.fetchone()
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

    def editar(self, id_cliente, dados_cliente, id_endereco, dados_endereco, id_cnh, dados_cnh):
        """Atualiza os dados de um cliente, seu endereço e CNH."""
        try:
            conexao = conectar()
            cursor = conexao.cursor()

            sql_cliente = "UPDATE cliente SET nome_completo=%s, cpf=%s, data_nascimento=%s, telefone=%s, email=%s, tempo_habilitacao_anos=%s WHERE id_cliente=%s"
            cursor.execute(sql_cliente, dados_cliente + (id_cliente,))

            sql_endereco = "UPDATE endereco SET logradouro=%s, numero=%s, complemento=%s, bairro=%s, cidade=%s, estado=%s, cep=%s WHERE id_endereco=%s"
            cursor.execute(sql_endereco, dados_endereco + (id_endereco,))

            sql_cnh = "UPDATE cnh SET numero_registro=%s, categoria=%s, data_validade=%s WHERE id_cnh=%s"
            cursor.execute(sql_cnh, dados_cnh + (id_cnh,))

            conexao.commit()
            return True
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

    def deletar(self, id_cliente):
        """Deleta um cliente e seus dados associados (endereço e CNH)."""
        try:
            conexao = conectar()
            cursor = conexao.cursor()

            cursor.execute(
                "SELECT id_endereco, id_cnh FROM cliente WHERE id_cliente=%s", (id_cliente,))
            dados = cursor.fetchone()
            if not dados:
                return False

            id_endereco, id_cnh = dados

            cursor.execute(
                "DELETE FROM cliente WHERE id_cliente=%s", (id_cliente,))
            cursor.execute(
                "DELETE FROM endereco WHERE id_endereco=%s", (id_endereco,))
            cursor.execute("DELETE FROM cnh WHERE id_cnh=%s", (id_cnh,))

            conexao.commit()
            return True
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()
