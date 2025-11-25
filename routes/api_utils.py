from flask import jsonify
from db import conectar


def get_categorias():
    """Busca e retorna todas as categorias de veículos."""
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            id_categoria_veiculo AS id,
            nome_categoria AS nome,
            valor_diaria
        FROM categoria_veiculo
    """)

    categorias = cursor.fetchall()
    cursor.close()
    conexao.close()
    return categorias
