from flask import render_template, request, redirect, url_for, flash

def init_pagamento(app):

    @app.route("/pagamento", methods=["GET", "POST"])
    def pagamento():
        if request.method == "POST":
            numero_cartao = request.form.get("numero_cartao")
            validade = request.form.get("validade")
            cvv = request.form.get("cvv")
            cpf = request.form.get("cpf")

            try:
                flash("Pagamento concluído", "success")
                return redirect(url_for("listagem_veiculos"))  # Redireciona para página inicial ou de confirmação

            except Exception as e:
                flash(f"Erro ao processar pagamento: {e}", "error")
                return redirect(url_for("pagamento"))

        return render_template("pagamento.html")
