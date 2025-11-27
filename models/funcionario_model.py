from db import conectar


class FuncionarioModel:
    """
    Modelo responsável por todas as operações de banco de dados
    relacionadas aos funcionários.
    """

    # Cadastro de um novo funcionário
    def cadastrar(self, dados_funcionario, dados_usuario, dados_endereco):
        try:
            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)

            cursor.execute(
                "SELECT id_usuario FROM usuario WHERE email=%s", (dados_usuario[0],))
            if cursor.fetchone():
                return "email_duplicado"

            cursor.execute(
                "SELECT id_cargo FROM cargo WHERE nome_cargo=%s", (dados_funcionario[3],))
            cargo_row = cursor.fetchone()
            if not cargo_row:
                return "cargo_invalido"

            id_cargo = cargo_row["id_cargo"]

            cursor.execute(
                "INSERT INTO usuario (email, senha, perfil) VALUES (%s, %s, %s)", dados_usuario)
            id_usuario = cursor.lastrowid

            cursor.execute(
                "INSERT INTO endereco (logradouro, numero, complemento, bairro, cidade, estado, cep) VALUES (%s, %s, %s, %s, %s, %s, %s)", dados_endereco)
            id_endereco = cursor.lastrowid

            sql_func = "INSERT INTO funcionario (id_usuario, nome, cpf, rg, data_nascimento, id_cargo, id_endereco) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            valores_func = (id_usuario, dados_funcionario[0], dados_funcionario[1],
                            dados_funcionario[2], dados_funcionario[4], id_cargo, id_endereco)
            cursor.execute(sql_func, valores_func)

            conexao.commit()
            return "sucesso"
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

    # Lista todos os funcionários
    def listar(self, termo_busca=None):
        try:
            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)
            if termo_busca and len(termo_busca) >= 3:
                like = f"%{termo_busca}%"
                sql = """
                    SELECT f.id_funcionario, f.id_usuario, f.nome, f.cpf, c.nome_cargo AS cargo
                    FROM funcionario f
                    JOIN cargo c ON f.id_cargo = c.id_cargo
                    JOIN usuario u ON f.id_usuario = u.id_usuario
                    WHERE f.nome LIKE %s OR f.cpf LIKE %s OR u.email LIKE %s
                """
                cursor.execute(sql, (like, like, like))
            else:
                sql = """
                    SELECT f.id_funcionario, f.id_usuario, f.nome, f.cpf, c.nome_cargo AS cargo
                    FROM funcionario f JOIN cargo c ON f.id_cargo = c.id_cargo
                """
                cursor.execute(sql)
            return cursor.fetchall()
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

    # Busca um funcionário pelo ID do usuário
    def obter_por_id_usuario(self, id_usuario):
        try:
            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)
            sql = """
                SELECT f.id_funcionario, f.id_endereco, f.nome, f.cpf, f.rg, f.data_nascimento,
                       u.email AS email_usuario, c.nome_cargo AS cargo, e.logradouro, e.numero, e.complemento,
                       e.bairro, e.cidade, e.estado, e.cep
                FROM funcionario f
                JOIN usuario u ON u.id_usuario = f.id_usuario
                JOIN cargo c ON c.id_cargo = f.id_cargo
                JOIN endereco e ON e.id_endereco = f.id_endereco
                WHERE f.id_usuario=%s
            """
            cursor.execute(sql, (id_usuario,))
            return cursor.fetchone()
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()

    # Deleta um funcionário 
    def deletar(self, id_usuario):
        try:
            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(
                "SELECT id_endereco FROM funcionario WHERE id_usuario=%s", (id_usuario,))
            row = cursor.fetchone()
            if not row:
                return False

            cursor.execute(
                "DELETE FROM funcionario WHERE id_usuario=%s", (id_usuario,))
            cursor.execute(
                "DELETE FROM usuario WHERE id_usuario=%s", (id_usuario,))
            cursor.execute(
                "DELETE FROM endereco WHERE id_endereco=%s", (row["id_endereco"],))
            conexao.commit()
            return True
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()
