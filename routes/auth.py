from flask import render_template, request, redirect, url_for, flash, session
from random import randint
from smtplib import SMTP
from email.message import EmailMessage
from db import conectar
from providers import hash_provider

def init_auth(app):
    from app import usuarios, atendentes

    def enviar_codigo_verificacao(email, perfil):
        codigo = ""
        for i in range(6):
            codigo += str(randint(0, 9))

        # Armazena código e dados temporários na sessão
        session['codigo_verificacao'] = codigo
        session['email_verificacao'] = email
        session['perfil_temp'] = perfil

        # Envia o código para o e-mail
        try:
            server = SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login('empresateste74@gmail.com', 'kcno lpdo ejub gpdv')

            msg = EmailMessage()
            msg['Subject'] = "Código de verificação"
            msg['From'] = 'empresateste74@gmail.com'
            msg['To'] = email
            msg.set_content(f"Seu código de verificação é: {codigo}")

            server.send_message(msg)
            server.quit()

            flash("Código de verificação enviado para seu e-mail.", "success")
            return True
        except Exception as e:
            flash(f"Erro ao enviar e-mail: {e}", "error")
            return False

    # -------------------- LOGIN --------------------
    @app.route('/login', methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email")
            senha = request.form.get("senha")

            usuario = None
            perfil = None

            conexao = conectar()
            cursor = conexao.cursor(dictionary=True)

            # Busca usuário no banco
            cursor.execute("SELECT email, senha, perfil FROM usuario WHERE email = %s", (email,))
            row = cursor.fetchone()
            cursor.close()
            conexao.close()

            if row is None:
                flash("Usuário não cadastrado.", "error")
                return redirect(url_for("login"))

            # Verifica senha usando função de criptografar
            if hash_provider.verificar_hash(senha, row['senha']):
                usuario = row
                perfil = usuario['perfil']

                usuario = row
                perfil = usuario['perfil']

                # Marca o processo como 'login' antes de enviar o código
                session["processo"] = "login"

                # Envia o código de verificação para o e-mail
                if enviar_codigo_verificacao(email, perfil):
                    # Armazena os dados temporários na sessão
                    session["email_temp"] = email
                    session["perfil_temp"] = perfil

                    # Redireciona para a página de verificação
                    flash("Código de verificação enviado para seu e-mail.", "success")
                    return redirect(url_for("verificacao"))

            else:
                flash("Email ou senha inválidos.", "error")
                return redirect(url_for("login"))

        return render_template("login.html")


    # -------------------- LOGOUT --------------------
    @app.route('/logout')
    def logout():
        session.pop("usuario_logado", None)
        session.pop("perfil", None)
        flash("Sessão encerrada.", "success")
        return redirect(url_for("login"))

    # -------------------- CADASTRO --------------------
    @app.route('/cadastro', methods=["GET", "POST"])
    def cadastro():
        if request.method == "POST":
            email = request.form.get("email")
            senha = request.form.get("senha")

            senha = hash_provider.gerar_hash(senha)

            if not email or not senha:
                flash("Preencha todos os campos obrigatórios", "error")
                return redirect(url_for("cadastro"))

            conexao = conectar()
            cursor = conexao.cursor()

            # Verifica se já existe o email
            cursor.execute("SELECT email FROM usuario WHERE email = %s", (email,))
            if cursor.fetchone() is not None:
                cursor.close()
                conexao.close()
                flash("Email já cadastrado", "error")
                return redirect(url_for("cadastro"))

            perfil = "cliente"

            # Marca o processo como 'cadastro' antes de enviar o código
            session["processo"] = "cadastro"

            # Gera o código e envia o e-mail
            if enviar_codigo_verificacao(email, perfil):
                session['email_temp'] = email
                session['senha_temp'] = senha
                session['perfil_temp'] = perfil
                flash("Cadastro iniciado. Código de verificação enviado para o e-mail.")
                return redirect(url_for("verificacao"))

        return render_template("cadastro.html")


    # -------------------- VERIFICAÇÃO --------------------
    @app.route('/verificacao', methods=["GET", "POST"])
    def verificacao():
        # Recupera dados temporários da sessão
        email = session.get("email_temp")
        senha = session.get("senha_temp")
        perfil_temp = session.get("perfil_temp")

        if not email:
            flash("Acesso inválido. Complete o cadastro novamente.", "error")
            return redirect(url_for("cadastro"))

        if request.method == "POST":
            codigo_recebido = request.form.get("codigo")
            codigo_armazenado = session.get("codigo_verificacao")

            if codigo_recebido == codigo_armazenado:
                # Verifica se o processo é de login ou cadastro
                if session.get("processo") == "login":
                    session["usuario_logado"] = email
                    session["perfil"] = perfil_temp
                    flash("Login realizado com sucesso!", "success")
                    return redirect(url_for("lista_veiculos"))

                elif session.get("processo") == "cadastro":
                    # Verifica se o email já está registrado
                    conexao = conectar()
                    cursor = conexao.cursor()

                    cursor.execute("SELECT email FROM usuario WHERE email = %s", (email,))
                    if cursor.fetchone():
                        cursor.close()
                        conexao.close()
                        flash("Este email já está registrado.", "error")
                        return redirect(url_for("login"))

                    # Insere o novo usuário no banco após a verificação do código
                    cursor.execute(
                        "INSERT INTO usuario (email, senha, perfil) VALUES (%s, %s, %s)",
                        (email, senha, perfil_temp)
                    )
                    conexao.commit()
                    cursor.close()
                    conexao.close()

                    # Limpa dados temporários da sessão
                    session.pop("email_temp", None)
                    session.pop("senha_temp", None)
                    session.pop("perfil_temp", None)
                    session.pop("codigo_verificacao", None)
                    session.pop("processo", None)

                    # Salva o login no usuário da sessão
                    session["usuario_logado"] = email
                    session["perfil"] = perfil_temp

                    flash("Cadastro completo. Bem-vindo!", "success")
                    return redirect(url_for("lista_veiculos"))
            else:
                flash("Código incorreto. Tente novamente.", "error")
                return redirect(url_for("verificacao"))

        return render_template("verificacao.html")
