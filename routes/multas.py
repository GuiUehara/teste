from flask import render_template, request, redirect, url_for, flash, session, abort
from db import conectar


def init_multa(app):

    @app.route("/historico_multas")
    def historico_multas():
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))

        # Apenas Gerente ou Atendente pode ver multas
        if session.get("perfil") not in ["Gerente", "Atendente"]:
            abort(403)

        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                l.id_locacao,
                c.nome_completo,
                v.placa,
                l.valor_total_previsto,
                l.valor_final,
                l.data_devolucao_prevista,
                l.data_devolucao_real,
                CEILING(
                    TIMESTAMPDIFF(HOUR, l.data_devolucao_prevista, l.data_devolucao_real) / 24.0
                ) AS dias_atraso
            FROM locacao l
            JOIN cliente c ON l.id_cliente = c.id_cliente
            JOIN veiculo v ON l.id_veiculo = v.id_veiculo
            WHERE l.data_devolucao_real IS NOT NULL
              AND l.data_devolucao_real > l.data_devolucao_prevista
            ORDER BY l.data_devolucao_real DESC
        """)

        multas = cursor.fetchall()

        cursor.close()
        conexao.close()

        return render_template("historico_multas.html", multas=multas)
