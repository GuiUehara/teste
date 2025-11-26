from flask import render_template, request, redirect, url_for, flash, session, abort
from models.funcionario_model import FuncionarioModel
from datetime import date, datetime
from db import conectar


class FuncionarioController:
    def __init__(self):
        self.funcionario_model = FuncionarioModel()

    # Rota para cadastrar um novo funcionário.
    def cadastrar(self):
        if session.get("perfil") != "Gerente":
            abort(403)

        if request.method == "POST":
            nome = request.form.get("nomeFuncionario")
            cpf = ''.join(filter(str.isdigit, request.form.get(
                "cpfFuncionario", "")))  # Remove não-dígitos
            rg = request.form.get("rgFuncionario", "")
            cargo = request.form.get("cargoFuncionario")
            data_nasc = request.form.get("dataNascFuncionario")
            email = request.form.get("emailUsuario", "")
            senha = request.form.get("senhaUsuario")
            logradouro = request.form.get("logradouro")
            numero = request.form.get("numero")
            complemento = request.form.get("complemento")
            bairro = request.form.get("bairro")
            cidade = request.form.get("cidade")
            estado = request.form.get("estado")
            cep = request.form.get("cep")

            obrigatorios = [nome, cpf, rg, data_nasc, cargo, email,
                            senha, logradouro, numero, bairro, cidade, estado, cep]

            if not all(obrigatorios):
                flash("Preencha todos os campos obrigatórios.", "error")
                return redirect(url_for("funcionarios.cadastro_funcionario"))

            # --- VALIDAÇÕES ---
            if len(cpf) != 11:
                flash("O CPF deve conter exatamente 11 dígitos.", "error")
                return redirect(url_for("funcionarios.cadastro_funcionario"))

            if len(rg) > 14:
                flash("O RG não pode ter mais de 14 caracteres.", "error")
                return redirect(url_for("funcionarios.cadastro_funcionario"))

            data_nasc_obj = datetime.strptime(data_nasc, "%Y-%m-%d").date()
            idade = (date.today() - data_nasc_obj).days / 365.25
            if idade < 18:
                flash("O funcionário deve ter no mínimo 18 anos.", "error")
                return redirect(url_for("funcionarios.cadastro_funcionario"))

            dados_funcionario = (nome, cpf, rg, cargo, data_nasc)
            dados_usuario = (email, senha, cargo)
            dados_endereco = (logradouro, numero, complemento,
                              bairro, cidade, estado, cep)

            resultado = self.funcionario_model.cadastrar(
                dados_funcionario, dados_usuario, dados_endereco)

            if resultado == "sucesso":
                flash("Funcionário cadastrado com sucesso!", "success")
            elif resultado == "email_duplicado":
                flash("Já existe um usuário com esse email!", "error")
            elif resultado == "cargo_invalido":
                flash("Cargo inválido!", "error")

            return redirect(url_for("funcionarios.cadastro_funcionario"))

        return render_template("cadastro_funcionario.html")

    # Rota para listar e buscar funcionários.
    def listar(self):
        if "usuario_logado" not in session:
            flash("Faça login para acessar.", "error")
            return redirect(url_for("auth.login"))

        if session.get("perfil") != "Gerente":
            abort(403)

        busca = request.args.get("busca", "").strip()
        funcionarios = self.funcionario_model.listar(busca)

        return render_template("lista_funcionarios.html", funcionarios=funcionarios, busca=busca)

    # Rota para editar um funcionário existente.
    def editar(self, id_usuario):
        if session.get("perfil") != "Gerente":
            abort(403)

        if request.method == "GET":
            funcionario = self.funcionario_model.obter_por_id_usuario(
                id_usuario)
            if not funcionario:
                abort(404)

            return render_template("editar_funcionario.html", funcionario=funcionario, id_usuario=id_usuario)

        nome = request.form.get("nomeFuncionario")
        cpf = ''.join(
            filter(str.isdigit, request.form.get("cpfFuncionario", "")))
        rg = request.form.get("rgFuncionario", "")
        data_nasc = request.form.get("dataNascFuncionario")
        cargo = request.form.get("cargoFuncionario")
        email_novo = request.form.get("emailUsuario", "")
        nova_senha = request.form.get("senhaUsuario")
        logradouro = request.form.get("logradouro")
        numero = request.form.get("numero")
        complemento = request.form.get("complemento")
        bairro = request.form.get("bairro")
        cidade = request.form.get("cidade")
        estado = request.form.get("estado")
        cep = request.form.get("cep")

        # --- VALIDAÇÕES ---
        if len(cpf) != 11:
            flash("O CPF deve conter exatamente 11 dígitos.", "error")
            return redirect(url_for("funcionarios.editar_funcionario", id_usuario=id_usuario))

        if len(rg) > 14:
            flash("O RG não pode ter mais de 14 caracteres.", "error")
            return redirect(url_for("funcionarios.editar_funcionario", id_usuario=id_usuario))

        data_nasc_obj = datetime.strptime(data_nasc, "%Y-%m-%d").date()
        idade = (date.today() - data_nasc_obj).days / 365.25
        if idade < 18:
            flash("O funcionário deve ter no mínimo 18 anos.", "error")
            return redirect(url_for("funcionarios.editar_funcionario", id_usuario=id_usuario))

        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            "SELECT id_cargo FROM cargo WHERE nome_cargo=%s", (cargo,))
        id_cargo = cursor.fetchone()["id_cargo"]

        cursor.execute(
            "SELECT id_endereco FROM funcionario WHERE id_usuario=%s", (id_usuario,))
        id_endereco = cursor.fetchone()["id_endereco"]

        cursor.execute(
            "SELECT email FROM usuario WHERE id_usuario=%s", (id_usuario,))
        email_atual = cursor.fetchone()["email"]

        if email_novo != email_atual:
            cursor.execute(
                "SELECT id_usuario FROM usuario WHERE email=%s AND id_usuario!=%s", (email_novo, id_usuario))
            if cursor.fetchone():
                flash("Este e-mail já está em uso!", "error")
                return redirect(url_for("funcionarios.editar_funcionario", id_usuario=id_usuario))
            cursor.execute(
                "UPDATE usuario SET email=%s WHERE id_usuario=%s", (email_novo, id_usuario))

        if nova_senha and nova_senha.strip():
            cursor.execute(
                "UPDATE usuario SET senha=%s WHERE id_usuario=%s", (nova_senha, id_usuario))

        cursor.execute("UPDATE endereco SET logradouro=%s, numero=%s, complemento=%s, bairro=%s, cidade=%s, estado=%s, cep=%s WHERE id_endereco=%s",
                       (logradouro, numero, complemento, bairro, cidade, estado, cep, id_endereco))
        cursor.execute("UPDATE funcionario SET nome=%s, cpf=%s, rg=%s, data_nascimento=%s, id_cargo=%s WHERE id_usuario=%s",
                       (nome, cpf, rg, data_nasc, id_cargo, id_usuario))
        cursor.execute(
            "UPDATE usuario SET perfil=%s WHERE id_usuario=%s", (cargo, id_usuario))

        conexao.commit()
        cursor.close()
        conexao.close()

        flash("Dados atualizados com sucesso!", "success")
        return redirect(url_for("funcionarios.lista_funcionarios"))

    # Rota para deletar um funcionário.
    def deletar(self, id_usuario):
        if session.get("perfil") != "Gerente":
            abort(403)

        if self.funcionario_model.deletar(id_usuario):
            flash("Funcionário removido com sucesso!", "success")
        else:
            flash("Erro: Funcionário não encontrado ou não pôde ser removido.", "error")

        return redirect(url_for("funcionarios.lista_funcionarios"))
