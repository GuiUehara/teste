from flask import render_template, request, redirect, url_for, flash, session, abort
from db import conectar

def init_clientes(app):

    @app.route("/cadastro_cliente", methods=["GET", "POST"])
    def cadastro_cliente():
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))

        if session.get("perfil") not in ["Gerente", "Atendente"]:
            abort(403)

        if request.method == "POST":

            dados_endereco = (
                request.form.get("logradouroCliente"),
                int(request.form.get("numeroCliente")),
                request.form.get("complementoCliente"),
                request.form.get("bairroCliente"),
                request.form.get("cidadeCliente"),
                request.form.get("estadoCliente"),
                int(request.form.get("cepCliente"))
            )

            dados_cnh = (
                int(request.form.get("cnhCliente")),
                request.form.get("categoriaCNHCliente").upper(),
                request.form.get("validadeCNHCliente")
            )

            dados_cliente = (
                request.form.get("nomeCliente"),
                request.form.get("cpfCliente"),
                request.form.get("dataNascCliente"),
                request.form.get("telefoneCliente"),
                request.form.get("emailCliente"),
                int(request.form.get("tempoHabilitacaoCliente"))
            )

            conexao = conectar()
            cursor = conexao.cursor()

            # INSERIR ENDEREÇO
            sql_endereco = """
                INSERT INTO endereco (logradouro, numero, complemento, bairro, cidade, estado, cep)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_endereco, dados_endereco)
            id_endereco = cursor.lastrowid

            # INSERIR CNH
            sql_cnh = """
                INSERT INTO cnh (numero_registro, categoria, data_validade)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql_cnh, dados_cnh)
            id_cnh = cursor.lastrowid

            # INSERIR CLIENTE
            sql_cliente = """
                INSERT INTO cliente
                (nome_completo, cpf, data_nascimento, telefone, email, tempo_habilitacao_anos, id_endereco, id_cnh)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values_cliente = dados_cliente + (id_endereco, id_cnh)
            cursor.execute(sql_cliente, values_cliente)

            conexao.commit()
            cursor.close()
            conexao.close()

            flash("Cliente cadastrado com sucesso!", "success")
            return redirect(url_for("cadastro_cliente"))

        return render_template("cadastro_cliente.html")


    @app.route("/lista_clientes")
    def lista_clientes():

        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))

        if session.get("perfil") not in ["Gerente", "Atendente"]:
            abort(403)

        termo = request.args.get("busca", "").strip()

        conexao = conectar()
        cursor = conexao.cursor()

        if len(termo) >= 3:
            sql = """
                SELECT id_cliente, nome_completo, cpf, email
                FROM cliente
                WHERE nome_completo LIKE %s OR cpf LIKE %s OR email LIKE %s
            """
            like = f"%{termo}%"
            cursor.execute(sql, (like, like, like))
        else:
            cursor.execute("SELECT id_cliente, nome_completo, cpf, email FROM cliente")

        clientes = cursor.fetchall()
        cursor.close()
        conexao.close()

        return render_template("lista_clientes.html", clientes=clientes, busca=termo)


    @app.route("/editar_cliente/<int:id_cliente>", methods=["GET", "POST"])
    def editar_cliente(id_cliente):

        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))

        if session.get("perfil") not in ["Gerente", "Atendente"]:
            abort(403)

        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)  # facilita usar por nome

        # BUSCAR CLIENTE + ENDEREÇO + CNH
        cursor.execute("""
            SELECT c.*, e.*, n.*
            FROM cliente c
            JOIN endereco e ON c.id_endereco = e.id_endereco
            JOIN cnh n ON c.id_cnh = n.id_cnh
            WHERE c.id_cliente = %s
        """, (id_cliente,))
        
        dados = cursor.fetchone()

        if not dados:
            cursor.close()
            conexao.close()
            abort(404)

        if request.method == "POST":

            # CLIENTE 
            nome = request.form.get("nomeCliente") or dados["nome_completo"]
            cpf = request.form.get("cpfCliente") or dados["cpf"]
            data_nasc = request.form.get("dataNascCliente") or dados["data_nascimento"]
            telefone = request.form.get("telefoneCliente") or dados["telefone"]
            email = request.form.get("emailCliente") or dados["email"]
            tempo_hab = request.form.get("tempoHabilitacaoCliente") or dados["tempo_habilitacao_anos"]

            sql_cliente = """
                UPDATE cliente SET
                    nome_completo=%s, cpf=%s, data_nascimento=%s,
                    telefone=%s, email=%s, tempo_habilitacao_anos=%s
                WHERE id_cliente=%s
            """
            cursor.execute(sql_cliente, (
                nome, cpf, data_nasc, telefone, email, tempo_hab, id_cliente
            ))

            # ENDEREÇO 
            logradouro = request.form.get("logradouroCliente") or dados["logradouro"]
            numero = request.form.get("numeroCliente") or dados["numero"]
            complemento = request.form.get("complementoCliente") or dados["complemento"]
            bairro = request.form.get("bairroCliente") or dados["bairro"]
            cidade = request.form.get("cidadeCliente") or dados["cidade"]
            estado = request.form.get("estadoCliente") or dados["estado"]
            cep = request.form.get("cepCliente") or dados["cep"]

            sql_endereco = """
                UPDATE endereco SET
                    logradouro=%s, numero=%s, complemento=%s,
                    bairro=%s, cidade=%s, estado=%s, cep=%s
                WHERE id_endereco=%s
            """
            cursor.execute(sql_endereco, (
                logradouro, numero, complemento,
                bairro, cidade, estado, cep,
                dados["id_endereco"]
            ))

            # CNH
            num_registro = request.form.get("cnhCliente") or dados["numero_registro"]
            categoria = request.form.get("categoriaCNHCliente") or dados["categoria"]
            validade = request.form.get("validadeCNHCliente") or dados["data_validade"]

            sql_cnh = """
                UPDATE cnh SET
                    numero_registro=%s, categoria=%s, data_validade=%s
                WHERE id_cnh=%s
            """
            cursor.execute(sql_cnh, (
                num_registro, categoria, validade,
                dados["id_cnh"]
            ))

            conexao.commit()
            cursor.close()
            conexao.close()

            flash("Dados atualizados com sucesso!", "success")
            return redirect(url_for("lista_clientes"))

        cursor.close()
        conexao.close()

        return render_template("editar_cliente.html", dados=dados, id_cliente=id_cliente)



    @app.route("/deletar_cliente/<int:id_cliente>", methods=["POST", "GET"])
    def deletar_cliente(id_cliente):

        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))

        if session.get("perfil") not in ["Gerente", "Atendente"]:
            abort(403)

        conexao = conectar()
        cursor = conexao.cursor()

        cursor.execute("SELECT id_endereco, id_cnh FROM cliente WHERE id_cliente=%s", (id_cliente,))
        dados = cursor.fetchone()

        if not dados:
            abort(404)

        id_endereco, id_cnh = dados

        cursor.execute("DELETE FROM cliente WHERE id_cliente=%s", (id_cliente,))
        cursor.execute("DELETE FROM endereco WHERE id_endereco=%s", (id_endereco,))
        cursor.execute("DELETE FROM cnh WHERE id_cnh=%s", (id_cnh,))

        conexao.commit()
        cursor.close()
        conexao.close()

        flash("Cliente removido!", "success")
        return redirect(url_for("lista_clientes"))
