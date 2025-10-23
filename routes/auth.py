from flask import render_template, request, redirect, url_for, flash, session

def init_auth(app):
    from app import usuarios, atendentes 
    @app.route('/login', methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email")
            senha = request.form.get("senha")

            if email in usuarios and usuarios[email]["senha"] == senha:
                session["usuario_logado"] = email
                session["perfil"] = usuarios[email]["perfil"]
                flash(f"Bem vindo", "success")
                return redirect(url_for("listagem_veiculos"))

            usuario_atendente = None
            for a in atendentes:
                if a["email"] == email and a["senha"] == senha:
                    usuario_atendente = a
                    break

            if usuario_atendente:
                session["usuario_logado"] = email
                session["perfil"] = usuario_atendente["perfil"]
                flash(f"Bem vindo", "success")
                return redirect(url_for("listagem_veiculos"))

            flash("Email ou senha inválidos", "error")
            return redirect(url_for("login"))

        return render_template("login.html")


    @app.route('/logout')
    def logout():
        session.pop("usuario_logado", None)
        session.pop("perfil", None)
        flash("Sessão encerrada.", "success")
        return redirect(url_for("login"))

    @app.route('/cadastro', methods=["GET", "POST"])
    def cadastro():
        from app import usuarios
        if request.method == "POST":
            email = request.form.get("email")
            senha = request.form.get("senha")
            if not email or not senha:
                flash("Preencha todos os campos obrigatórios", "error")
                return redirect(url_for("cadastro"))
            if email in usuarios:
                flash("Email já cadastrado", "error")
                return redirect(url_for("cadastro"))
            usuarios[email] = {"senha": senha, "perfil": "atendente"}
            flash("Cadastro salvo. Faça login.", "success")
            return redirect(url_for("login"))
        return render_template("cadastro.html")
