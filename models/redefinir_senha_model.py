from db import conectar
from providers import hash_provider


class RedefinirSenhaModel:
    def atualizar_senha(self, email, nova_senha):
        """Atualiza a senha de um usuário a partir do email."""
        try:
            nova_senha_hash = hash_provider.gerar_hash(nova_senha)
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute(
                "UPDATE usuario SET senha=%s WHERE email=%s", (nova_senha_hash, email))
            conexao.commit()
            return True
        finally:
            if 'conexao' in locals() and conexao.is_connected():
                cursor.close()
                conexao.close()
