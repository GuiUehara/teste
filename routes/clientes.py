from flask import render_template, request, redirect, url_for, flash, session, abort

def init_clientes(app):

    @app.route("/cadastro_cliente", methods=["GET", "POST"])
    def cadastro_cliente():
        from models import Cliente
        from app import clientes
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))
        if session.get("perfil") != "gerente" and session.get("perfil") != "atendente":
            abort(403)
        if request.method == "POST":
            novo_cliente = Cliente(
                nome=request.form.get("nomeCliente"),
                cpf=request.form.get("cpfCliente"),
                data_nasc=request.form.get("dataNascCliente"),
                telefone=request.form.get("telefoneCliente"),
                email=request.form.get("emailCliente"),
                endereco=request.form.get("enderecoCliente"),
                cnh=request.form.get("cnhCliente"),
                categoria_cnh=request.form.get("categoriaCNHCliente"),
                validade_cnh=request.form.get("validadeCNHCliente"),
                tempo_habilitacao=request.form.get("tempoHabilitacaoCliente"),
                forma_pagamento=request.form.get("formaPagamentoCliente")
            )
            clientes.append(novo_cliente)
            flash("Cliente cadastrado com sucesso!", "success")
            return redirect(url_for("cadastro_cliente"))
        
        return render_template("cadastro_cliente.html")
