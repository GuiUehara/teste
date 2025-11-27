from flask import Blueprint, render_template, flash, redirect, url_for
from controllers.veiculo_controller import VeiculoController
from db import conectar

veiculo_bp = Blueprint('veiculos', __name__)
veiculo_controller = VeiculoController()


@veiculo_bp.route("/cadastro_veiculo", methods=["GET", "POST"])
def cadastro_veiculo():
    return veiculo_controller.cadastrar()


@veiculo_bp.route("/lista_veiculos")
def lista_veiculos():
    return veiculo_controller.listar()


@veiculo_bp.route("/editar_veiculo/<int:id_veiculo>", methods=["GET", "POST"])
def editar_veiculo(id_veiculo):
    return veiculo_controller.editar(id_veiculo)


@veiculo_bp.route("/deletar_veiculo/<int:id_veiculo>")
def deletar_veiculo(id_veiculo):
    return veiculo_controller.deletar(id_veiculo)


@veiculo_bp.route("/grupo_carros")
def grupo_carros():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id_categoria_veiculo as id_categoria, nome_categoria, valor_diaria FROM categoria_veiculo")
    categorias = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("grupo_carros.html", categorias=categorias)


@veiculo_bp.route('/categoria/<int:id_categoria>')
def veiculos_por_categoria(id_categoria):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    # Busca a categoria pelo id
    cursor.execute(
        "SELECT id_categoria_veiculo as id_categoria, nome_categoria, valor_diaria FROM categoria_veiculo WHERE id_categoria_veiculo = %s", (id_categoria,))
    categoria = cursor.fetchone()

    if not categoria:
        flash("Categoria não encontrada.", "danger")
        return redirect(url_for('veiculos.grupo_carros'))

    # Busca os veículos disponíveis da categoria
    query = """
        SELECT v.id_veiculo, v.imagem, m.nome_marca, mo.nome_modelo
        FROM veiculo v
        JOIN modelo mo ON v.id_modelo = mo.id_modelo
        JOIN marca m ON mo.id_marca = m.id_marca
        WHERE mo.id_categoria_veiculo = %s AND v.id_status_veiculo = 1
        ORDER BY m.nome_marca, mo.nome_modelo;
    """
    cursor.execute(query, (id_categoria,))
    veiculos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template(
        "veiculos_por_categoria.html", categoria=categoria, veiculos=veiculos)
