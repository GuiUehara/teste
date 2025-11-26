from flask import render_template, request, redirect, url_for, flash, session, abort
from datetime import datetime
from models.cliente_model import ClienteModel
from models.locacao_model import LocacaoModel

class ClienteController:
    def __init__(self):
        self.cliente_model = ClienteModel()

    # Rota para cadastrar um novo cliente.
    def cadastrar(self):
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("auth.login"))

        if request.method == "POST":
            # --- Validações ---
            data_nasc_str = request.form.get("dataNascCliente")
            if not data_nasc_str:
                 flash("Data de nascimento obrigatória.", "error")
                 return redirect(url_for("clientes.cadastro_cliente"))

            data_nasc = datetime.strptime(data_nasc_str, "%Y-%m-%d")
            idade = (datetime.today() - data_nasc).days // 365

            if idade < 21:
                flash("ERRO: O cliente deve ter no mínimo 21 anos para ser cadastrado!", "error")
                return redirect(url_for("clientes.cadastro_cliente"))

            validade_cnh_str = request.form.get("validadeCNHCliente")
            if not validade_cnh_str:
                 flash("Validade da CNH obrigatória.", "error")
                 return redirect(url_for("clientes.cadastro_cliente"))
                 
            validade_cnh = datetime.strptime(validade_cnh_str, "%Y-%m-%d")

            if validade_cnh < datetime.today():
                flash("ERRO: A CNH está vencida. Cadastro bloqueado!", "error")
                return redirect(url_for("clientes.cadastro_cliente"))

            try:
                validade_tempo_habilitacao = int(request.form.get("tempoHabilitacaoCliente"))
            except ValueError:
                validade_tempo_habilitacao = 0

            if validade_tempo_habilitacao < 2:
                flash("ERRO: Mínimo 2 anos de habilitação. Cadastro bloqueado!", "error")
                return redirect(url_for("clientes.cadastro_cliente"))

            # Dados do Endereço
            dados_endereco = (
                request.form.get("logradouroCliente"),
                request.form.get("numeroCliente"),
                request.form.get("complementoCliente"),
                request.form.get("bairroCliente"),
                request.form.get("cidadeCliente"),
                request.form.get("estadoCliente"),
                request.form.get("cepCliente")
            )

            # Dados da CNH
            dados_cnh = (
                request.form.get("cnhCliente"),
                request.form.get("categoriaCNHCliente").upper(),
                validade_cnh_str
            )

            # Dados do Cliente
            cpf_cliente = request.form.get("cpfCliente")
            dados_cliente = (
                request.form.get("nomeCliente"),
                cpf_cliente,
                data_nasc_str,
                request.form.get("telefoneCliente"),
                request.form.get("emailCliente"),
                validade_tempo_habilitacao
            )

            # Tenta cadastrar
            if self.cliente_model.cadastrar(dados_cliente, dados_endereco, dados_cnh):
                flash("Cliente cadastrado com sucesso!", "success")

                # --- Verifica se há reserva pendente na sessão ---
                if 'reserva_pendente' in session:
                    try:
                        cliente_novo = self.cliente_model.buscar_por_cpf(cpf_cliente)
                        
                        if cliente_novo:
                            pendente = session['reserva_pendente']
                            locacao_model = LocacaoModel()

                            dt_ret = datetime.strptime(f"{pendente['data_retirada']} 12:00", "%Y-%m-%d %H:%M")
                            dt_dev = datetime.strptime(f"{pendente['data_devolucao_prevista']} 12:00", "%Y-%m-%d %H:%M")

                            dados_locacao = {
                                "id_cliente": cliente_novo['id_cliente'],
                                "id_veiculo": pendente['id_veiculo'],
                                "data_retirada": dt_ret,
                                "data_devolucao_prevista": dt_dev,
                                "status": "Reserva"
                            }
                            
                            id_locacao = locacao_model.criar_locacao(dados_locacao, pendente['opcionais'])

                            session['id_locacao_pagamento'] = id_locacao
                            session.pop('reserva_pendente', None)

                            return redirect(url_for("pagamento.pagamento"))
                    except Exception as e:
                        print(f"Erro reserva auto: {e}")
                        flash("Cliente cadastrado, mas erro ao gerar reserva.", "warning")

                if 'id_locacao_pagamento' in session:
                    return redirect(url_for("pagamento.pagamento"))

                return redirect(url_for("clientes.lista_clientes"))

            else:
                # Se cair aqui, é porque o Model retornou False (CPF duplicado, etc)
                flash("Erro ao cadastrar. CPF ou Email já existem.", "error")
                return redirect(url_for("clientes.cadastro_cliente"))

        return render_template("cadastro_cliente.html")

    # Rota para listar e buscar clientes.
    def listar(self):
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
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
            return redirect(url_for("auth.login"))

        if session.get("perfil") not in ["Gerente", "Atendente"]:
            abort(403)

        dados = self.cliente_model.obter_por_id(id_cliente)

        if not dados:
            abort(404)

        if request.method == "POST":
            nome = request.form.get("nomeCliente") or dados["nome_completo"]
            cpf = request.form.get("cpfCliente") or dados["cpf"]
            data_nasc = request.form.get("dataNascCliente") or dados["data_nascimento"]
            telefone = request.form.get("telefoneCliente") or dados["telefone"]
            email = request.form.get("emailCliente") or dados["email"]
            
            try:
                tempo_hab_input = request.form.get("tempoHabilitacaoCliente")
                tempo_hab = int(tempo_hab_input) if tempo_hab_input else dados["tempo_habilitacao_anos"]
            except ValueError:
                tempo_hab = dados["tempo_habilitacao_anos"]

            dados_cliente = (nome, cpf, data_nasc, telefone, email, tempo_hab)

            logradouro = request.form.get("logradouroCliente") or dados["logradouro"]
            numero = request.form.get("numeroCliente") or dados["numero"]
            complemento = request.form.get("complementoCliente") or dados["complemento"]
            bairro = request.form.get("bairroCliente") or dados["bairro"]
            cidade = request.form.get("cidadeCliente") or dados["cidade"]
            estado = request.form.get("estadoCliente") or dados["estado"]
            cep = request.form.get("cepCliente") or dados["cep"]

            dados_endereco = (logradouro, numero, complemento, bairro, cidade, estado, cep)

            num_registro = request.form.get("cnhCliente") or dados["numero_registro"]
            categoria = request.form.get("categoriaCNHCliente") or dados["categoria"]
            validade = request.form.get("validadeCNHCliente") or dados["data_validade"]

            dados_cnh = (num_registro, categoria, validade)

            if self.cliente_model.editar(id_cliente, dados_cliente, dados["id_endereco"], dados_endereco, dados["id_cnh"], dados_cnh):
                flash("Dados atualizados com sucesso!", "success")
            return redirect(url_for("clientes.lista_clientes"))

        return render_template("editar_cliente.html", dados=dados, id_cliente=id_cliente)

    # Rota para deletar um cliente.
    def deletar(self, id_cliente):
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("auth.login"))

        if session.get("perfil") not in ["Gerente", "Atendente"]:
            abort(403)

        if self.cliente_model.deletar(id_cliente):
            flash("Cliente removido!", "success")
        else:
            flash("Erro: Cliente não encontrado ou não pôde ser removido.", "error")
        return redirect(url_for("clientes.lista_clientes"))