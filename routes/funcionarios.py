from flask import render_template, request, redirect, url_for, flash, session, abort
from db import conectar

def init_funcionarios(app):

    # ==========================
    #   CADASTRAR FUNCIONÁRIO
    # ==========================
    @app.route("/cadastro_funcionario", methods=["GET", "POST"])
    def cadastro_funcionario():

        if session.get("perfil") != "Gerente":
            abort(403)

        if request.method == "POST":

            # ====== DADOS FUNCIONÁRIO ======
            nome = request.form.get("nomeFuncionario")
            cpf = request.form.get("cpfFuncionario")
            rg = request.form.get("rgFuncionario")
            cargo = request.form.get("cargoFuncionario")
            data_nasc = request.form.get("dataNascFuncionario")

            # ====== DADOS LOGIN ======
            email = request.form.get("emailUsuario")
            senha = request.form.get("senhaUsuario")

            # ====== ENDEREÇO ======
            logradouro = request.form.get("logradouro")
            numero = request.form.get("numero")
            complemento = request.form.get("complemento")
            bairro = request.form.get("bairro")
            cidade = request.form.get("cidade")
            estado = request.form.get("estado")
            cep = request.form.get("cep")

            obrigatorios = [
                nome, cpf, rg, data_nasc, cargo, email, senha,
                logradouro, numero, bairro, cidade, estado, cep
            ]

            if not all(obrigatorios):
                flash("Preencha todos os campos obrigatórios.", "error")
                return redirect(url_for("cadastro_funcionario"))

            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)

            # Verifica duplicidade de email
            cursor.execute("SELECT id_usuario FROM usuario WHERE email=%s", (email,))
            if cursor.fetchone():
                flash("Já existe um usuário com esse email!", "error")
                return redirect(url_for("cadastro_funcionario"))

            # ID DO CARGO
            cursor.execute("SELECT id_cargo FROM cargo WHERE nome_cargo=%s", (cargo,))
            cargo_row = cursor.fetchone()
            if not cargo_row:
                flash("Cargo inválido!", "error")
                return redirect(url_for("cadastro_funcionario"))

            id_cargo = cargo_row["id_cargo"]

            # INSERE LOGIN
            cursor.execute("""
                INSERT INTO usuario (email, senha, perfil)
                VALUES (%s, %s, %s)
            """, (email, senha, cargo))
            id_usuario = cursor.lastrowid

            # INSERE ENDEREÇO
            cursor.execute("""
                INSERT INTO endereco (logradouro, numero, complemento, bairro, cidade, estado, cep)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (logradouro, numero, complemento, bairro, cidade, estado, cep))
            id_endereco = cursor.lastrowid

            # INSERE FUNCIONÁRIO
            cursor.execute("""
                INSERT INTO funcionario (id_usuario, nome, cpf, rg, data_nascimento, id_cargo, id_endereco)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (id_usuario, nome, cpf, rg, data_nasc, id_cargo, id_endereco))

            conexao.commit()
            cursor.close()
            conexao.close()

            flash("Funcionário cadastrado com sucesso!", "success")
            return redirect(url_for("cadastro_funcionario"))

        return render_template("cadastro_funcionario.html")

    # ==========================
    #   LISTAR FUNCIONÁRIOS
    # ==========================
    @app.route("/lista_funcionarios")
    def lista_funcionarios():
        if "usuario_logado" not in session:
            flash("Faça login para acessar.", "error")
            return redirect(url_for("login"))

        if session.get("perfil") != "Gerente":
            abort(403)

        busca = request.args.get("busca", "").strip()

        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        if len(busca) >= 3:
            like = f"%{busca}%"
            cursor.execute("""
                SELECT f.id_usuario, f.nome, f.cpf, c.nome_cargo AS cargo
                FROM funcionario f
                JOIN cargo c ON f.id_cargo = c.id_cargo
                JOIN usuario u ON f.id_usuario = u.id_usuario
                WHERE f.nome LIKE %s OR f.cpf LIKE %s OR u.email LIKE %s
            """, (like, like, like))
        else:
            cursor.execute("""
                SELECT f.id_usuario, f.nome, f.cpf, c.nome_cargo AS cargo
                FROM funcionario f
                JOIN cargo c ON f.id_cargo = c.id_cargo
            """)

        funcionarios = cursor.fetchall()

        cursor.close()
        conexao.close()

        return render_template("lista_funcionarios.html", funcionarios=funcionarios, busca=busca)

    # ==========================
    #   EDITAR FUNCIONÁRIO
    # ==========================
    @app.route("/editar_funcionario/<int:id_usuario>", methods=["GET", "POST"])
    def editar_funcionario(id_usuario):

        if session.get("perfil") != "Gerente":
            abort(403)

        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        # ------ GET ------
        if request.method == "GET":
            
            cursor.execute("""
                SELECT 
                    f.nome, f.cpf, f.rg, f.data_nascimento,
                    u.email AS email_usuario,
                    c.nome_cargo AS cargo,
                    e.logradouro, e.numero, e.complemento,
                    e.bairro, e.cidade, e.estado, e.cep
                FROM funcionario f
                JOIN usuario u ON u.id_usuario = f.id_usuario
                JOIN cargo c ON c.id_cargo = f.id_cargo
                JOIN endereco e ON e.id_endereco = f.id_endereco
                WHERE f.id_usuario=%s
            """, (id_usuario,))

            funcionario = cursor.fetchone()
            cursor.close()
            conexao.close()

            if not funcionario:
                abort(404)

            return render_template(
                "editar_funcionario.html",
                funcionario=funcionario,
                id_usuario=id_usuario
            )

        # ------ POST ------
        nome = request.form.get("nomeFuncionario")
        cpf = request.form.get("cpfFuncionario")
        rg = request.form.get("rgFuncionario")
        data_nasc = request.form.get("dataNascFuncionario")
        cargo = request.form.get("cargoFuncionario")

        email_novo = request.form.get("emailUsuario")
        nova_senha = request.form.get("senhaUsuario")

        logradouro = request.form.get("logradouro")
        numero = request.form.get("numero")
        complemento = request.form.get("complemento")
        bairro = request.form.get("bairro")
        cidade = request.form.get("cidade")
        estado = request.form.get("estado")
        cep = request.form.get("cep")

        # ID DO CARGO
        cursor.execute("SELECT id_cargo FROM cargo WHERE nome_cargo=%s", (cargo,))
        id_cargo = cursor.fetchone()["id_cargo"]

        # ID ENDEREÇO
        cursor.execute("SELECT id_endereco FROM funcionario WHERE id_usuario=%s", (id_usuario,))
        id_endereco = cursor.fetchone()["id_endereco"]

        # EMAIL ATUAL
        cursor.execute("SELECT email FROM usuario WHERE id_usuario=%s", (id_usuario,))
        email_atual = cursor.fetchone()["email"]

        # EMAIL DUPLICADO?
        if email_novo != email_atual:
            cursor.execute("""
                SELECT id_usuario FROM usuario WHERE email=%s AND id_usuario!=%s
            """, (email_novo, id_usuario))
            if cursor.fetchone():
                flash("Este e-mail já está em uso!", "error")
                return redirect(url_for("editar_funcionario", id_usuario=id_usuario))

            cursor.execute("UPDATE usuario SET email=%s WHERE id_usuario=%s", (email_novo, id_usuario))

        # SENHA OPCIONAL
        if nova_senha and nova_senha.strip():
            cursor.execute("UPDATE usuario SET senha=%s WHERE id_usuario=%s", (nova_senha, id_usuario))

        # ENDEREÇO
        cursor.execute("""
            UPDATE endereco SET logradouro=%s, numero=%s, complemento=%s,
                                bairro=%s, cidade=%s, estado=%s, cep=%s
            WHERE id_endereco=%s
        """, (logradouro, numero, complemento, bairro, cidade, estado, cep, id_endereco))

        # FUNCIONÁRIO
        cursor.execute("""
            UPDATE funcionario SET nome=%s, cpf=%s, rg=%s, data_nascimento=%s, id_cargo=%s
            WHERE id_usuario=%s
        """, (nome, cpf, rg, data_nasc, id_cargo, id_usuario))

        # Buscar nome do cargo
        cursor.execute("SELECT nome_cargo FROM cargo WHERE id_cargo=%s", (id_cargo,))
        cargo_nome = cursor.fetchone()["nome_cargo"]

        # Atualizar perfil na tabela usuario
        cursor.execute("""
            UPDATE usuario
            SET perfil=%s
            WHERE id_usuario=%s
        """, (cargo_nome, id_usuario))



        conexao.commit()
        cursor.close()
        conexao.close()

        flash("Dados atualizados com sucesso!", "success")
        return redirect(url_for("lista_funcionarios"))

    # ==========================
    #   DELETAR FUNCIONÁRIO
    # ==========================
    @app.route("/deletar_funcionario/<int:id_usuario>")
    def deletar_funcionario(id_usuario):

        if session.get("perfil") != "Gerente":
            abort(403)

        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("SELECT id_endereco FROM funcionario WHERE id_usuario=%s", (id_usuario,))
        row = cursor.fetchone()
        if not row:
            abort(404)

        id_endereco = row["id_endereco"]

        cursor.execute("DELETE FROM funcionario WHERE id_usuario=%s", (id_usuario,))
        cursor.execute("DELETE FROM usuario WHERE id_usuario=%s", (id_usuario,))
        cursor.execute("DELETE FROM endereco WHERE id_endereco=%s", (id_endereco,))

        conexao.commit()
        cursor.close()
        conexao.close()

        flash("Funcionário removido com sucesso!", "success")
        return redirect(url_for("lista_funcionarios"))
