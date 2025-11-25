from flask import jsonify, Blueprint
from db import conectar

veiculos_api = Blueprint("veiculos_api", __name__)

# --- Função auxiliar que só retorna as categorias (utilizado no api_locacao.py) ---


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


@veiculos_api.route("/api/modelos/<int:id_marca>")
def api_modelos_por_marca(id_marca):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT m.id_modelo, m.nome_modelo, c.nome_categoria
        FROM modelo m
        JOIN categoria_veiculo c ON c.id_categoria_veiculo = m.id_categoria_veiculo
        WHERE m.id_marca = %s
    """, (id_marca,))
    modelos = [
        # Nome da categoria
        {"id": row[0], "nome": row[1], "id_categoria_nome": row[2]}
        for row in cursor.fetchall()
    ]
    cursor.close()
    conexao.close()
    return jsonify(modelos)
