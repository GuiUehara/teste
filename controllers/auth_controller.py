from flask import render_template, request, redirect, url_for, flash, session
from random import randint
from smtplib import SMTP
from email.message import EmailMessage
import os
from providers import hash_provider
from models import auth_model


class AuthController:
    # Método privado para gerar e enviar o código de verificação por e-mail.
    def _enviar_codigo_verificacao(self, email, perfil):
        codigo = "".join([str(randint(0, 9)) for _ in range(6)])
        session['codigo_verificacao'] = codigo
        session['email_verificacao'] = email
        session['perfil_temp'] = perfil

        try:
            with SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login('empresateste74@gmail.com',
                             os.environ.get("EMAIL_PASSWORD"))

                msg = EmailMessage()
                msg['Subject'] = "Código de verificação"
                msg['From'] = 'empresateste74@gmail.com'
                msg['To'] = email
                msg.set_content(f"Seu código de verificação é: {codigo}")

                server.send_message(msg)

            flash("Código de verificação enviado para seu e-mail.", "success")
            return True
        except Exception as e:
            flash(f"Erro ao enviar e-mail: {e}", "error")
            return False

    # Rota para o login do usuário.
    def login(self):
        """Processa o login do usuário."""
        if request.method == "POST":
            email = request.form.get("email")
            senha = request.form.get("senha")

            usuario = auth_model.obter_usuario_por_email(email)

            if not usuario:
                flash("Usuário não cadastrado.", "error")
                return redirect(url_for("auth.login"))

            if hash_provider.verificar_hash(senha, usuario['senha']):
                session["processo"] = "login"
                if self._enviar_codigo_verificacao(email, usuario['perfil']):
                    session["email_temp"] = email
                    session["perfil_temp"] = usuario['perfil']
                    
                    return redirect(url_for("auth.verificacao"))
            else:
                flash("Email ou senha inválidos.", "error")
                return redirect(url_for("auth.login"))
        return render_template("login.html")

    def logout(self):
        """Encerra a sessão do usuário."""
        session.pop("usuario_logado", None)
        session.pop("perfil", None)
        flash("Sessão encerrada.", "success")
        return redirect(url_for("auth.login"))

    # Rota para o cadastro de novos usuários.
    def cadastro(self):
        """Processa o cadastro de um novo usuário."""
        if request.method == "POST":
            email = request.form.get("email")
            senha = request.form.get("senha")

            if not email or not senha:
                flash("Preencha todos os campos obrigatórios", "error")
                return redirect(url_for("auth.cadastro"))

            senha_hash = hash_provider.gerar_hash(senha)

            if auth_model.obter_usuario_por_email(email):
                flash("Email já cadastrado", "error")
                return redirect(url_for("auth.cadastro"))

            perfil = "cliente"
            session["processo"] = "cadastro"
            if self._enviar_codigo_verificacao(email, perfil):
                session['email_temp'] = email
                session['senha_temp'] = senha_hash
                session['perfil_temp'] = perfil
                
                return redirect(url_for("auth.verificacao"))
        return render_template("cadastro.html")

    # Rota para a página de verificação do código. (cadastro ou login)
    def verificacao(self):
        email = session.get("email_temp")
        senha = session.get("senha_temp")
        perfil_temp = session.get("perfil_temp")

        if not email:
            flash("Acesso inválido. Complete o cadastro novamente.", "error")
            return redirect(url_for("auth.cadastro"))
            
        if request.method == "POST":
            codigo_recebido = request.form.get("codigo")
            codigo_armazenado = session.get("codigo_verificacao")
            
            if codigo_recebido == codigo_armazenado:
                # Salva o processo antes de limpar a sessão
                processo = session.get("processo")
                
                # Limpa dados temporários AGORA (antes do return)
                for key in ['email_temp', 'senha_temp', 'perfil_temp', 'codigo_verificacao', 'processo']:
                    session.pop(key, None)

                if processo == "login":
                    session["usuario_logado"] = email
                    session["perfil"] = perfil_temp
                    flash("Login realizado com sucesso!", "success")
                    
                    # MUDANÇA AQUI: Redireciona para a página inicial (index)
                    return redirect(url_for("index"))
                
                elif processo == "cadastro":
                    if auth_model.obter_usuario_por_email(email):
                        flash("Este email já está registrado.", "error")
                        return redirect(url_for("auth.login"))
                        
                    auth_model.criar_usuario(email, senha, perfil_temp)

                    session["usuario_logado"] = email
                    session["perfil"] = perfil_temp

                    flash("Cadastro completo. Bem-vindo!", "success")
                    
                    # MUDANÇA AQUI: Redireciona para a página inicial (index)
                    return redirect(url_for("index"))
            else:
                flash("Código incorreto. Tente novamente.", "error")
                return redirect(url_for("auth.verificacao"))
                
        return render_template("verificacao.html")