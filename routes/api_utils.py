from flask import jsonify
from db import conectar

# Busca todas as categorias de veículos
def get_categorias():
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
