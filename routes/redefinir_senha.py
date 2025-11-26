from flask import render_template, request, redirect, url_for, flash, session, current_app
from itsdangerous import URLSafeTimedSerializer
from email.message import EmailMessage
from smtplib import SMTP
import os
from db import conectar
from providers import hash_provider


def init_redefinirSenha(app):
    def gerar_token(email):
        serializer = URLSafeTimedSerializer(
            current_app.config['TOKEN_SECRET_KEY'])
        # transforma o email em um token (um link) seguro pela função dumps; salt garante que tokens diferentes sejam gerados mesmo em email igual
        return serializer.dumps(email, salt=current_app.config['TOKEN_SALT'])

    def confirmar_token(token, expiration=1800):
        serializer = URLSafeTimedSerializer(
            current_app.config['TOKEN_SECRET_KEY'])
        try:
            # "serializer" decodifica o token (email) usando salt e pela função loads
            email = serializer.loads(
                token, salt=current_app.config['TOKEN_SALT'], max_age=expiration)
        except Exception:
            return False
        # retorna o endereço original do email (xy@gmail.com), e não como um token
        return email

    def enviar_email_reset(email, token):
        reset_url = url_for('resetar_senha', token=token, _external=True)
        mensagem = EmailMessage()
        mensagem['Subject'] = "Solicitação de Redefinição de Senha"
        mensagem['From'] = "empresateste74@gmail.com"
        mensagem['To'] = email
        mensagem.set_content(
            f"Para redefinir sua senha, clique no link abaixo:\n{reset_url}\n")

        with SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login('empresateste74@gmail.com',
                         os.environ.get("EMAIL_PASSWORD"))
            server.send_message(mensagem)

    @app.route('/solicitar_redefinir', methods=['GET', 'POST'])
    def solicitar_redefinir():
        if request.method == 'POST':
            email = request.form.get('email')
            conn = conectar()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuario WHERE email=%s", (email,))
            usuario = cursor.fetchone()
            conn.close()

            if usuario:
                token = gerar_token(email)
                enviar_email_reset(email, token)
                flash(
                    "Email enviado com instruções para redefinir sua senha.", "success")
            else:
                flash("Email não cadastrado.", "error")
            return redirect(url_for('auth.login'))
        return render_template('solicitar_redefinir.html')

    @app.route('/resetar_senha/<token>', methods=['GET', 'POST'])
    def resetar_senha(token):
        email = confirmar_token(token)
        if not email:
            flash("Link inválido ou expirado.", "error")
            return redirect(url_for('redefinir_senha.solicitar_redefinir'))

        if request.method == 'POST':
            nova_senha = request.form.get('nova_senha')
            confirmar_senha = request.form.get('confirmar_senha')
            if nova_senha != confirmar_senha:
                flash("As senhas não coincidem", "error")
                return redirect(url_for('redefinir_senha.resetar_senha', token=token))

            nova_senha = hash_provider.gerar_hash(nova_senha)

            # Atualiza senha
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE usuario SET senha=%s WHERE email=%s", (nova_senha, email))
            conn.commit()
            conn.close()

            flash("Senha redefinida com sucesso!", "success")
            return redirect(url_for('auth.login'))

        return render_template('resetar_senha.html')
