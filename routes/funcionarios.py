from flask import render_template, request, redirect, url_for, flash, session, abort


def init_funcionarios(app):

    @app.route("/cadastro_funcionario", methods=["GET", "POST"])
    def cadastro_funcionario():
        from app import usuarios, atendentes, atendentes_inf
        from models import Funcionario
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))
        if session.get("perfil") != "gerente":
            abort(403)

        if request.method == "POST":
            nome = request.form.get("nomeFuncionario")
            cpf = request.form.get("cpfFuncionario")
            rg = request.form.get("rgFuncionario")
            data_nasc = request.form.get("dataNascFuncionario")
            sexo = request.form.get("sexoFuncionario")
            estado_civil = request.form.get("estadoCivilFuncionario")
            endereco = request.form.get("enderecoFuncionario")
            email = request.form.get("emailFuncionario")
            senha = request.form.get("senhaFuncionario")

            obrigatorios = [nome, cpf, rg, data_nasc, sexo, estado_civil, endereco, email, senha]
            if not all(obrigatorios):
                flash("Preencha todos os campos obrigatórios", "error")
                return redirect(url_for("cadastro_funcionario"))

            if email in usuarios or any(a.email == email for a in atendentes):
                flash("Funcionário com esse email já existe", "error")
                return redirect(url_for("cadastro_funcionario"))

            novo_funcionario = Funcionario(
                nome=nome,
                cpf=cpf,
                rg=rg,
                data_nasc=data_nasc,
                sexo=sexo,
                estado_civil=estado_civil,
                endereco=endereco,
                email=email,
                senha=senha,
                perfil="atendente"
            )

            usuarios[email] = {"senha": senha, "perfil": "atendente"}
            atendentes.append(novo_funcionario)  # lista de objetos Funcionario
            atendentes_inf.append(novo_funcionario)  # pode manter para dados detalhados

            flash("Funcionário atendente cadastrado com sucesso!", "success")
            return redirect(url_for("cadastro_funcionario"))

        return render_template("cadastro_funcionario.html")
