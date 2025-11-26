from flask import render_template, request, redirect, url_for, flash, session, abort
from models.veiculo_model import VeiculoModel


class VeiculoController:
    def __init__(self):
        self.veiculo_model = VeiculoModel()

    # Rota para cadastrar um novo veículo.
    def cadastrar(self):
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("auth.login"))

        if session.get("perfil") not in ["Gerente", "Atendente"]:
            abort(403)

        dados_suporte = self.veiculo_model.get_dados_suporte()

        if request.method == "POST":
            id_seguro = int(request.form.get("companhiaSeguro"))
            vencimento_seguro = request.form.get("vencimentoSeguro")

            placa = request.form.get("placaVeiculo")
            chassi = request.form.get("chassiVeiculo")
            ano = int(request.form.get("anoVeiculo"))
            cor = request.form.get("corVeiculo")
            transmissao = request.form.get("transmissaoVeiculo")
            data_compra = request.form.get("dataCompra")
            valor_compra = float(request.form.get("valorCompra"))
            odometro = int(request.form.get("odometro"))
            data_vencimento = request.form.get("vencimentoLicenciamento")

            tanque_str = request.form.get("tanque")
            mapa_tanque = {"Cheio": 8, "7/8": 7, "6/8": 6, "5/8": 5,
                           "4/8": 4, "3/8": 3, "2/8": 2, "1/8": 1, "Vazio": 0}
            tanque = mapa_tanque.get(tanque_str, 0)
            tanque_fracao = tanque / 8
            valor_fracao = (tanque * 6) / 8 + 5

            id_status = int(request.form.get("status"))
            id_combustivel = int(request.form.get("combustivel"))
            id_modelo = int(request.form.get("modeloVeiculo"))

            dados_veiculo = (
                placa, ano, cor, chassi, odometro, transmissao, data_compra,
                valor_compra, data_vencimento, tanque, tanque_fracao, valor_fracao,
                id_modelo, id_status, id_combustivel, id_seguro
            )

            resultado = self.veiculo_model.cadastrar(
                dados_veiculo, id_seguro, vencimento_seguro)

            if resultado == "sucesso":
                flash("Veículo cadastrado com sucesso!", "success")
            elif resultado == "placa_duplicada":
                flash("Já existe um veículo com esta placa.", "error")
            elif resultado == "chassi_duplicado":
                flash("Já existe um veículo com este chassi.", "error")

            return redirect(url_for("veiculos.cadastro_veiculo"))

        return render_template("cadastro_veiculo.html",
                               combustiveis=dados_suporte["combustiveis"],
                               status=dados_suporte["status"],
                               marcas=dados_suporte["marcas"],
                               seguros=dados_suporte["seguros"])

    # Rota para listar e buscar veículos.
    def listar(self):
        if "usuario_logado" not in session:
            flash("Faça login para acessar.", "error")
            return redirect(url_for("auth.login"))

        busca = request.args.get("busca", "").strip()
        veiculos = self.veiculo_model.listar(busca)

        return render_template("lista_veiculos.html", veiculos=veiculos, busca=busca)

    # Rota para editar um veículo existente.
    def editar(self, id_veiculo):

        if request.method == "POST":
            placa = request.form.get("placaVeiculo")
            chassi = request.form.get("chassiVeiculo")
            ano = request.form.get("anoVeiculo")
            cor = request.form.get("corVeiculo")
            transmissao = request.form.get("transmissaoVeiculo")
            data_compra = request.form.get("dataCompra")
            valor_compra = request.form.get("valorCompra")
            quilometragem = request.form.get("odometro")
            data_vencimento = request.form.get("vencimentoLicenciamento")
            tanque = request.form.get("tanque")
            tanque_fracao = request.form.get("tanqueFracao")
            id_combustivel = request.form.get("combustivel")
            id_modelo = request.form.get("modeloVeiculo")
            id_status_veiculo = request.form.get("status")
            id_seguro = request.form.get("companhiaSeguro") or None
            vencimento_seguro = request.form.get("vencimentoSeguro") or None

            dados_veiculo = (
                placa, chassi, ano, cor, transmissao, data_compra, valor_compra,
                quilometragem, data_vencimento, tanque, tanque_fracao,
                id_combustivel, id_modelo, id_status_veiculo, id_seguro
            )

            resultado = self.veiculo_model.editar(
                id_veiculo, dados_veiculo, id_seguro, vencimento_seguro)

            if resultado == "sucesso":
                flash("Veículo atualizado com sucesso!", "success")
            elif resultado == "placa_duplicada":
                flash("Já existe um veículo com essa placa!", "error")
                return redirect(url_for("veiculos.editar_veiculo", id_veiculo=id_veiculo))
            elif resultado == "chassi_duplicado":
                flash("Já existe um veículo com esse chassi!", "error")
                return redirect(url_for("veiculos.editar_veiculo", id_veiculo=id_veiculo))

            return redirect(url_for("veiculos.lista_veiculos"))

        veiculo = self.veiculo_model.obter_por_id(id_veiculo)
        if not veiculo:
            abort(404)

        dados_suporte = self.veiculo_model.get_dados_suporte()

        return render_template("editar_veiculo.html",
                               veiculo=veiculo,
                               combustiveis=dados_suporte["combustiveis"],
                               marcas=dados_suporte["marcas"],
                               modelos=dados_suporte["modelos"],
                               status=dados_suporte["status"],
                               seguros=dados_suporte["seguros"],
                               id_veiculo=id_veiculo)

    # Rota para deletar um veículo.
    def deletar(self, id_veiculo):
        if "usuario_logado" not in session:
            flash("Faça login para acessar.", "error")
            return redirect(url_for("auth.login"))

        if self.veiculo_model.deletar(id_veiculo):
            flash("Veículo removido com sucesso!", "success")
        else:
            flash("Erro ao remover veículo.", "error")
        return redirect(url_for("veiculos.lista_veiculos"))
