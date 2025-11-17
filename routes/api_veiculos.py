from flask import jsonify, Blueprint
from db import conectar

veiculos_api = Blueprint("veiculos_api", __name__)

# Retorna todas as marcas
@veiculos_api.route("/api/marcas")
def api_marcas():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id_marca, nome_marca FROM marca")
    marcas = [{"id": row[0], "nome": row[1]} for row in cursor.fetchall()]
    cursor.close()
    conexao.close()
    return jsonify(marcas)

# Retorna todas as categorias
@veiculos_api.route("/api/categorias")
def api_categorias():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id_categoria_veiculo, nome_categoria FROM categoria_veiculo")
    categorias = [{"id": row[0], "nome": row[1]} for row in cursor.fetchall()]
    cursor.close()
    conexao.close()
    return jsonify(categorias)


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
        {"id": row[0], "nome": row[1], "id_categoria_nome": row[2]}  # Nome da categoria
        for row in cursor.fetchall()
    ]
    cursor.close()
    conexao.close()
    return jsonify(modelos)

