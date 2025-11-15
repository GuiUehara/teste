from flask import render_template, request, redirect, url_for, flash, session, abort
from db import conectar

def init_funcionarios(app):

    @app.route("/cadastro_funcionario", methods=["GET", "POST"])
    def cadastro_funcionario():

        if session.get("perfil") not in ["Gerente"]:
            abort(403)

        if request.method == "POST":
            nome = request.form.get("nomeFuncionario")
            cpf = request.form.get("cpfFuncionario")
            rg = request.form.get("rgFuncionario")
            cargo = request.form.get("cargoFuncionario")
            data_nasc = request.form.get("dataNascFuncionario")
            email = request.form.get("emailFuncionario")
            senha = request.form.get("senhaFuncionario")

            # Endereço completo
            logradouro = request.form.get("logradouro")
            numero = request.form.get("numero")
            complemento = request.form.get("complemento")
            bairro = request.form.get("bairro")
            cidade = request.form.get("cidade")
            estado = request.form.get("estado")
            cep = request.form.get("cep")

            obrigatorios = [nome, cpf, rg, data_nasc, email, senha,
                            logradouro, numero, bairro, cidade, estado, cep]

            if not all(obrigatorios):
                flash("Preencha todos os campos obrigatórios.", "error")
                return redirect(url_for("cadastro_funcionario"))

            conexao = conectar()
            cursor = conexao.cursor()

            # Verifica email duplicado
            cursor.execute("SELECT email FROM usuario WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("Já existe um usuário com esse email.", "error")
                cursor.close()
                conexao.close()
                return redirect(url_for("cadastro_funcionario"))

            # Busca id_cargo
            cursor.execute("SELECT id_cargo FROM cargo WHERE nome_cargo = %s", (cargo,))
            cargo_tupla = cursor.fetchone()

            if cargo_tupla is None:
                flash("Cargo inválido!", "error")
                return redirect(url_for("cadastro_funcionario"))

            id_cargo = cargo_tupla[0]

            # INSERE ENDEREÇO
            cursor.execute("""
                INSERT INTO endereco (logradouro, numero, complemento, bairro, cidade, estado, cep)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (logradouro, numero, complemento, bairro, cidade, estado, cep))
            id_endereco = cursor.lastrowid

            # INSERE FUNCIONÁRIO
            cursor.execute("""
                INSERT INTO funcionario (nome, cpf, rg, data_nascimento, email, senha, id_cargo, id_endereco)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, cpf, rg, data_nasc, email, senha, id_cargo, id_endereco))

            # INSERE USUÁRIO PARA LOGIN
            cursor.execute("""
                INSERT INTO usuario (email, senha, perfil)
                VALUES (%s, %s, %s)
            """, (email, senha, cargo))

            conexao.commit()
            cursor.close()
            conexao.close()

            flash("Funcionário cadastrado com sucesso!", "success")
            return redirect(url_for("cadastro_funcionario"))

        return render_template("cadastro_funcionario.html")
    
    @app.route("/lista_funcionarios")
    def lista_funcionarios():
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))

        if session.get("perfil") not in ["Gerente"]:
            abort(403)

        termo = request.args.get("busca", "").strip()

        conexao = conectar()
        cursor = conexao.cursor()

        if len(termo) >= 3:
            sql = """
                SELECT f.id_usuario, f.nome, f.cpf, f.email, c.nome_cargo
                FROM funcionario f
                JOIN cargo c ON f.id_cargo = c.id_cargo
                WHERE f.nome LIKE %s OR f.cpf LIKE %s OR f.email LIKE %s
            """
            like = f"%{termo}%"
            cursor.execute(sql, (like, like, like))
        else:
            sql = """
                SELECT f.id_usuario, f.nome, f.cpf, f.email, c.nome_cargo
                FROM funcionario f
                JOIN cargo c ON f.id_cargo = c.id_cargo
            """
            cursor.execute(sql)

        funcionarios = cursor.fetchall()
        cursor.close()
        conexao.close()

        return render_template("lista_funcionarios.html", funcionarios=funcionarios, busca=termo)

    # --- EDITAR FUNCIONÁRIO ---
    @app.route("/editar_funcionario/<int:id_usuario>", methods=["GET", "POST"])
    def editar_funcionario(id_usuario):
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))

        if session.get("perfil") not in ["Gerente"]:
            abort(403)

        conexao = conectar()
        cursor = conexao.cursor()

        if request.method == "POST":
            # Dados pessoais
            nome = request.form.get("nomeFuncionario")
            cpf = request.form.get("cpfFuncionario")
            rg = request.form.get("rgFuncionario")
            cargo = request.form.get("cargoFuncionario")
            data_nasc = request.form.get("dataNascFuncionario")
            email = request.form.get("emailFuncionario")
            senha = request.form.get("senhaFuncionario")

            # Endereço
            logradouro = request.form.get("logradouro")
            numero = request.form.get("numero")
            complemento = request.form.get("complemento")
            bairro = request.form.get("bairro")
            cidade = request.form.get("cidade")
            estado = request.form.get("estado")
            cep = request.form.get("cep")

            # Busca id_cargo
            cursor.execute("SELECT id_cargo FROM cargo WHERE nome_cargo = %s", (cargo,))
            cargo_tupla = cursor.fetchone()
            if cargo_tupla is None:
                flash("Cargo inválido!", "error")
                return redirect(url_for("editar_funcionario", id_usuario=id_usuario))
            id_cargo = cargo_tupla[0]

            # Busca id_endereco do funcionário
            cursor.execute("SELECT id_endereco FROM funcionario WHERE id_usuario=%s", (id_usuario,))
            id_endereco = cursor.fetchone()[0]

            # Atualiza endereço
            cursor.execute("""
                UPDATE endereco SET logradouro=%s, numero=%s, complemento=%s,
                                    bairro=%s, cidade=%s, estado=%s, cep=%s
                WHERE id_endereco=%s
            """, (logradouro, numero, complemento, bairro, cidade, estado, cep, id_endereco))

            # Atualiza funcionário
            cursor.execute("""
                UPDATE funcionario SET nome=%s, cpf=%s, rg=%s, data_nascimento=%s,
                                      email=%s, senha=%s, id_cargo=%s
                WHERE id_usuario=%s
            """, (nome, cpf, rg, data_nasc, email, senha, id_cargo, id_usuario))

            conexao.commit()
            cursor.close()
            conexao.close()

            flash("Funcionário atualizado com sucesso!", "success")
            return redirect(url_for("lista_funcionarios"))

        # GET - preenche formulário
        cursor.execute("""
            SELECT f.nome, f.cpf, f.rg, f.data_nascimento, f.email, c.nome_cargo,
                   e.logradouro, e.numero, e.complemento, e.bairro, e.cidade, e.estado, e.cep
            FROM funcionario f
            JOIN cargo c ON f.id_cargo = c.id_cargo
            JOIN endereco e ON f.id_endereco = e.id_endereco
            WHERE f.id_usuario=%s
        """, (id_usuario,))
        funcionario = cursor.fetchone()
        cursor.close()
        conexao.close()

        if not funcionario:
            abort(404)

        return render_template("editar_funcionario.html", funcionario=funcionario, id_usuario=id_usuario)

    # --- DELETAR FUNCIONÁRIO ---
    @app.route("/deletar_funcionario/<int:id_usuario>", methods=["POST", "GET"])
    def deletar_funcionario(id_usuario):
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))

        if session.get("perfil") not in ["Gerente"]:
            abort(403)

        conexao = conectar()
        cursor = conexao.cursor()

        # Pega id_endereco
        cursor.execute("SELECT id_endereco FROM funcionario WHERE id_usuario=%s", (id_usuario,))
        result = cursor.fetchone()
        if not result:
            abort(404)
        id_endereco = result[0]

        # Deleta funcionário e endereço
        cursor.execute("DELETE FROM funcionario WHERE id_usuario=%s", (id_usuario,))
        cursor.execute("DELETE FROM endereco WHERE id_endereco=%s", (id_endereco,))

        conexao.commit()
        cursor.close()
        conexao.close()

        flash("Funcionário removido com sucesso!", "success")
        return redirect(url_for("lista_funcionarios"))

