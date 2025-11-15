from flask import render_template, request, redirect, url_for, flash, session
from random import randint
from smtplib import SMTP
from email.message import EmailMessage
from db import conectar


def init_auth(app):
    from app import usuarios, atendentes

    def enviar_codigo_verificacao(email, perfil):
        codigo = ""
        for i in range(6):
            codigo += str(randint(0, 9))

        # Armazena código na sessão
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

            if row and row['senha'] == senha:
                usuario = row
                perfil = usuario['perfil']

            if usuario:
                if perfil == "gerente":  # teste
                    session["usuario_logado"] = email
                    session["perfil"] = perfil
                    flash("Bem-vindo, gerente!", "success")
                    return redirect(url_for("listagem_veiculos"))
                else:
                    if enviar_codigo_verificacao(email, perfil):
                        return redirect(url_for("verificacao"))

            else:
                flash("Email ou senha inválidos", "error")
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

            if not email or not senha:
                flash("Preencha todos os campos obrigatórios", "error")
                return redirect(url_for("cadastro"))

            # Verifica existência no banco
            conexao = conectar()
            cursor = conexao.cursor()

            cursor.execute("SELECT email FROM usuario WHERE email = %s", (email,))
            if cursor.fetchone() is not None:
                cursor.close()
                conexao.close()
                flash("Email já cadastrado", "error")
                return redirect(url_for("cadastro"))

            # Insere usuário
            cursor.execute(
                "INSERT INTO usuario (email, senha, perfil) VALUES (%s, %s, %s)",
                (email, senha, "cliente")
            )
            conexao.commit()
            cursor.close()
            conexao.close()

            perfil = "cliente"

            # gera código de verificação e envia e-mail
            if enviar_codigo_verificacao(email, perfil):
                flash("Cadastro salvo. Código de verificação enviado.")
                return redirect("verificacao")

        return render_template("cadastro.html")

    # -------------------- VERIFICAÇÃO --------------------
    @app.route('/verificacao', methods=["GET", "POST"])
    def verificacao():
        email = session.get("email_verificacao")
        perfil_temp = session.get("perfil_temp")

        if not email:
            flash("Acesso inválido.")
            return redirect(url_for("login"))

        if request.method == "POST":
            codigo_recebido = request.form.get("codigo")
            codigo_armazenado = session.get("codigo_verificacao")

            if codigo_recebido == codigo_armazenado:
                # Login completo: salva dados na sessão
                session["usuario_logado"] = email
                session["perfil"] = perfil_temp

                # Limpa dados temporários
                session.pop("codigo_verificacao", None)
                session.pop("perfil_temp", None)
                session.pop("email_verificacao", None)

                flash("Email verificado. Bem-vindo!", "success")
                return redirect(url_for("listagem_veiculos"))
            else:
                flash("Código incorreto. Tente novamente.", "error")
                return redirect(url_for("verificacao"))

        return render_template("verificacao.html")
