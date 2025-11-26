from flask import render_template, request, redirect, url_for, flash, session, abort
from datetime import datetime
from models.cliente_model import ClienteModel
from models.locacao_model import LocacaoModel

class ClienteController:
    def __init__(self):
        self.cliente_model = ClienteModel()

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
                validade_tempo_habilitacao = 0 # Valor padrão caso venha vazio

            if validade_tempo_habilitacao < 2:
                flash("ERRO: Mínimo 2 anos de habilitação. Cadastro bloqueado!", "error")
                return redirect(url_for("clientes.cadastro_cliente"))

            # --- CORREÇÃO AQUI: Removidos os int() de campos VARCHAR ---
            dados_endereco = (
                request.form.get("logradouroCliente"),
                request.form.get("numeroCliente"),  # Agora aceita "10B", "S/N"
                request.form.get("complementoCliente"),
                request.form.get("bairroCliente"),
                request.form.get("cidadeCliente"),
                request.form.get("estadoCliente"),
                request.form.get("cepCliente")      # Mantém zeros a esquerda e traços
            )

            dados_cnh = (
                request.form.get("cnhCliente"),     # Mantém formato texto
                request.form.get("categoriaCNHCliente").upper(),
                validade_cnh_str
            )

            cpf_cliente = request.form.get("cpfCliente")
            dados_cliente = (
                request.form.get("nomeCliente"),
                cpf_cliente,
                data_nasc_str,
                request.form.get("telefoneCliente"),
                request.form.get("emailCliente"),
                validade_tempo_habilitacao
            )

            if self.cliente_model.cadastrar(dados_cliente, dados_endereco, dados_cnh):
                flash("Cliente cadastrado com sucesso!", "success")

                # Lógica de Redirecionamento (Reserva Pendente)
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
                flash("Erro ao cadastrar. CPF ou Email já existem.", "error")
                return redirect(url_for("clientes.cadastro_cliente"))

        return render_template("cadastro_cliente.html")

    # Mantenha os métodos listar, editar e deletar iguais, 
    # APENAS LEMBRE de remover o int() no método editar também!