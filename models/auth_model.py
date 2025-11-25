from db import conectar


def obter_usuario_por_email(email):
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    # CORREÇÃO: Adicionado 'id_usuario' na consulta SQL.
    cursor.execute(
        "SELECT id_usuario, email, senha, perfil FROM usuario WHERE email = %s", (email,))
    usuario = cursor.fetchone()
    cursor.close()
    conexao.close()
    return usuario


def criar_usuario(email, senha, perfil):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO usuario (email, senha, perfil) VALUES (%s, %s, %s)", (email, senha, perfil))
    conexao.commit()
    cursor.close()
    conexao.close()
