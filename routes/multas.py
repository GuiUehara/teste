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
                id_locacao,
                id_cliente,
                id_veiculo,
                valor_total_previsto,
                valor_final,
                data_devolucao_prevista,
                data_devolucao_real,
                CEILING(
                    TIMESTAMPDIFF(HOUR, data_devolucao_prevista, data_devolucao_real) / 24.0
                ) AS dias_atraso
            FROM locacao
            WHERE data_devolucao_real IS NOT NULL
              AND data_devolucao_real > data_devolucao_prevista
            ORDER BY data_devolucao_real DESC
        """)

        multas = cursor.fetchall()

        cursor.close()
        conexao.close()

        return render_template("historico_multas.html", multas=multas)

