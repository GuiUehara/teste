from flask import render_template, request, redirect, url_for, flash, current_app
from itsdangerous import URLSafeTimedSerializer
from email.message import EmailMessage
from smtplib import SMTP
import os
from models import auth_model
from models.redefinir_senha_model import RedefinirSenhaModel


class RedefinirSenhaController:
    def __init__(self):
        self.redefinir_senha_model = RedefinirSenhaModel()

    def _gerar_token(self, email):
        serializer = URLSafeTimedSerializer(
            current_app.config['TOKEN_SECRET_KEY'])
        return serializer.dumps(email, salt=current_app.config['TOKEN_SALT'])

    def _confirmar_token(self, token, expiration=1800):
        serializer = URLSafeTimedSerializer(
            current_app.config['TOKEN_SECRET_KEY'])
        try:
            email = serializer.loads(
                token, salt=current_app.config['TOKEN_SALT'], max_age=expiration)
            return email
        except Exception:
            return False

    def _enviar_email_reset(self, email, token):
        reset_url = url_for('redefinir_senha.resetar_senha',
                            token=token, _external=True)
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

    def solicitar(self):
        """Processa a solicitação de redefinição de senha."""
        if request.method == 'POST':
            email = request.form.get('email')
            usuario = auth_model.obter_usuario_por_email(email)

            if usuario:
                token = self._gerar_token(email)
                self._enviar_email_reset(email, token)
                flash(
                    "Email enviado com instruções para redefinir sua senha.", "success")
            else:
                flash("Email não cadastrado.", "error")
            # Correção já estava ok, mantido por consistência.
            return redirect(url_for('auth.login'))
        return render_template('solicitar_redefinir.html')

    def resetar(self, token):
        """Processa a redefinição da senha a partir do token."""
        email = self._confirmar_token(token)
        if not email:
            flash("Link inválido ou expirado.", "error")
            # Correção já estava ok, mantido por consistência.
            return redirect(url_for('redefinir_senha.solicitar_redefinir'))

        if request.method == 'POST':
            nova_senha = request.form.get('nova_senha')
            confirmar_senha = request.form.get('confirmar_senha')

            if nova_senha != confirmar_senha:
                flash("As senhas não coincidem", "error")
                # Correção já estava ok, mantido por consistência.
                return redirect(url_for('redefinir_senha.resetar_senha', token=token))

            if self.redefinir_senha_model.atualizar_senha(email, nova_senha):
                flash("Senha redefinida com sucesso!", "success")
                return redirect(url_for('auth.login'))
            else:
                flash("Ocorreu um erro ao redefinir a senha.", "error")
                # Correção já estava ok, mantido por consistência.
                return redirect(url_for('redefinir_senha.resetar_senha', token=token))

        return render_template('resetar_senha.html')
