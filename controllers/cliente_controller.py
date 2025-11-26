from flask import render_template, request, redirect, url_for, flash, session, abort
from datetime import datetime
from models.cliente_model import ClienteModel


class ClienteController:
    def __init__(self):
        self.cliente_model = ClienteModel()

    # Rota para cadastrar um novo cliente.
    def cadastrar(self):
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            # Correção já estava ok, mantido por consistência.
            return redirect(url_for("auth.login"))

        if request.method == "POST":
            # Validar idade mínima de 21 anos
            data_nasc_str = request.form.get("dataNascCliente")
            data_nasc = datetime.strptime(data_nasc_str, "%Y-%m-%d")
            idade = (datetime.today() - data_nasc).days // 365

            if idade < 21:
                flash(
                    "ERRO: O cliente deve ter no mínimo 21 anos para ser cadastrado!", "error")
                return redirect(url_for("clientes.cadastro_cliente"))

            # Validar vencimento da CNH
            validade_cnh_str = request.form.get("validadeCNHCliente")
            validade_cnh = datetime.strptime(validade_cnh_str, "%Y-%m-%d")

            if validade_cnh < datetime.today():
                flash("ERRO: A CNH está vencida. Cadastro bloqueado!", "error")
                return redirect(url_for("clientes.cadastro_cliente"))

            # Verificar tempo de habilitação
            validade_tempo_habilitacao = int(
                request.form.get("tempoHabilitacaoCliente"))
            if validade_tempo_habilitacao < 2:
                flash("ERRO: Mínimo 2 anos de habilitação. Cadastro bloqueado!", "error")
                return redirect(url_for("clientes.cadastro_cliente"))

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
                validade_cnh_str
            )

            dados_cliente = (
                request.form.get("nomeCliente"),
                request.form.get("cpfCliente"),
                data_nasc_str,
                request.form.get("telefoneCliente"),
                request.form.get("emailCliente"),
                validade_tempo_habilitacao
            )

            if self.cliente_model.cadastrar(dados_cliente, dados_endereco, dados_cnh):
                flash("Cliente cadastrado com sucesso!", "success")
                # Se o cadastro de cliente foi feito durante uma reserva, redireciona para o pagamento
                if 'id_locacao_pagamento' in session:
                    return redirect(url_for("pagamento.pagamento"))
            else:
                flash("Erro ao cadastrar cliente.", "error")
                return redirect(url_for("clientes.cadastro_cliente"))

        return render_template("cadastro_cliente.html")

    # Rota para listar e buscar clientes.
    def listar(self):
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            # Correção já estava ok, mantido por consistência.
            return redirect(url_for("auth.login"))

        if session.get("perfil") not in ["Gerente", "Atendente"]:
            abort(403)

        termo = request.args.get("busca", "").strip()
        clientes = self.cliente_model.listar(termo)

        return render_template("lista_clientes.html", clientes=clientes, busca=termo)

    # Rota para editar um cliente existente.
    def editar(self, id_cliente):
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            # Correção já estava ok, mantido por consistência.
            return redirect(url_for("auth.login"))

        if session.get("perfil") not in ["Gerente", "Atendente"]:
            abort(403)

        dados = self.cliente_model.obter_por_id(id_cliente)

        if not dados:
            abort(404)

        if request.method == "POST":
            nome = request.form.get("nomeCliente") or dados["nome_completo"]
            cpf = request.form.get("cpfCliente") or dados["cpf"]
            data_nasc = request.form.get(
                "dataNascCliente") or dados["data_nascimento"]
            telefone = request.form.get("telefoneCliente") or dados["telefone"]
            email = request.form.get("emailCliente") or dados["email"]
            tempo_hab = request.form.get(
                "tempoHabilitacaoCliente") or dados["tempo_habilitacao_anos"]

            dados_cliente = (nome, cpf, data_nasc, telefone, email, tempo_hab)

            logradouro = request.form.get(
                "logradouroCliente") or dados["logradouro"]
            numero = request.form.get("numeroCliente") or dados["numero"]
            complemento = request.form.get(
                "complementoCliente") or dados["complemento"]
            bairro = request.form.get("bairroCliente") or dados["bairro"]
            cidade = request.form.get("cidadeCliente") or dados["cidade"]
            estado = request.form.get("estadoCliente") or dados["estado"]
            cep = request.form.get("cepCliente") or dados["cep"]

            dados_endereco = (logradouro, numero, complemento,
                              bairro, cidade, estado, cep)

            num_registro = request.form.get(
                "cnhCliente") or dados["numero_registro"]
            categoria = request.form.get(
                "categoriaCNHCliente") or dados["categoria"]
            validade = request.form.get(
                "validadeCNHCliente") or dados["data_validade"]

            dados_cnh = (num_registro, categoria, validade)

            if self.cliente_model.editar(id_cliente, dados_cliente, dados["id_endereco"], dados_endereco, dados["id_cnh"], dados_cnh):
                flash("Dados atualizados com sucesso!", "success")
            return redirect(url_for("clientes.lista_clientes"))

        return render_template("editar_cliente.html", dados=dados, id_cliente=id_cliente)

    # Rota para deletar um cliente.
    def deletar(self, id_cliente):
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            # Correção já estava ok, mantido por consistência.
            return redirect(url_for("auth.login"))

        if session.get("perfil") not in ["Gerente", "Atendente"]:
            abort(403)

        if self.cliente_model.deletar(id_cliente):
            flash("Cliente removido!", "success")
        else:
            flash("Erro: Cliente não encontrado ou não pôde ser removido.", "error")
        return redirect(url_for("clientes.lista_clientes"))
