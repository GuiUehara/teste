from flask import jsonify, request, session, flash, redirect, url_for, abort 
from models.locacao_model import LocacaoModel
from datetime import datetime


class LocacaoController:
    def __init__(self):
        self.locacao_model = LocacaoModel()

    def criar_locacao(self):
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Nenhum dado enviado"}), 400

        opcionais = dados.pop("opcionais", [])

        try:
            # Converte as datas antes de passar para o model
            dados['data_retirada'] = datetime.strptime(
                dados['data_retirada'], "%Y-%m-%dT%H:%M")
            dados['data_devolucao_prevista'] = datetime.strptime(
                dados['data_devolucao_prevista'], "%Y-%m-%dT%H:%M")

            id_nova_locacao = self.locacao_model.criar_locacao(
                dados, opcionais)

            return jsonify({
                "mensagem": "Locação criada com sucesso",
                "id_locacao": id_nova_locacao
            }), 201

        except Exception as e:
            return jsonify({"erro": str(e)}), 500

    def get_locacao(self, id_locacao):
        try:
            locacao, opcionais = self.locacao_model.obter_por_id(id_locacao)
            if not locacao:
                return jsonify({"erro": "Locação não encontrada"}), 404

            return jsonify({"locacao": locacao, "opcionais": opcionais})

        except Exception as e:
            print(f"Erro ao buscar locação {id_locacao}: {e}")
            return jsonify({"erro": str(e)}), 500

    def atualizar_locacao(self, id_loc):
        dados = request.get_json()
        try:
            valores_atualizados = self.locacao_model.atualizar_locacao(
                id_loc, dados)
            return jsonify({
                "mensagem": "Locação atualizada com sucesso",
                "valor_total_previsto": valores_atualizados["valor_total_previsto"],
                "valor_final": valores_atualizados["valor_final"]
            }), 200

        except Exception as e:
            print(f"Erro ao atualizar locação {id_loc}: {str(e)}")
            return jsonify({"erro": str(e)}), 500

    def buscar_clientes(self):
        termo = request.args.get('termo', '').strip()
        try:
            clientes = self.locacao_model.buscar_clientes_autocomplete(termo)
            return jsonify(clientes)
        except Exception as e:
            return jsonify({"erro": str(e)}), 500

    def listar_categorias(self):
        try:
            categorias = self.locacao_model.listar_categorias_veiculos()
            return jsonify(categorias)
        except Exception as e:
            return jsonify({"erro": str(e)}), 500

    def listar_veiculos(self):
        id_categoria = request.args.get('id_categoria')
        try:
            veiculos = self.locacao_model.listar_veiculos_por_categoria(
                id_categoria)
            return jsonify(veiculos)
        except Exception as e:
            return jsonify({"erro": str(e)}), 500

    def get_veiculo(self, id_veiculo):
        try:
            veiculo = self.locacao_model.obter_detalhes_veiculo(id_veiculo)
            if not veiculo:
                return jsonify({"erro": "Veículo não encontrado"}), 404
            return jsonify(veiculo)
        except Exception as e:
            return jsonify({"erro": str(e)}), 500

    def listar_opcionais(self):
        try:
            opcionais = self.locacao_model.listar_opcionais_disponiveis()
            return jsonify(opcionais)
        except Exception as e:
            return jsonify({"erro": str(e)}), 500

    def valor_previsto(self):
        dados = request.get_json()
        id_veiculo = dados.get("id_veiculo")
        data_retirada = dados.get("data_retirada")
        data_prevista = dados.get("data_devolucao_prevista")
        opcionais = dados.get("opcionais", [])

        if not id_veiculo or not data_retirada or not data_prevista:
            return jsonify({"erro": "Veículo e datas são obrigatórios"}), 400

        try:
            dt_retirada = datetime.strptime(data_retirada, "%Y-%m-%dT%H:%M")
            dt_prevista = datetime.strptime(data_prevista, "%Y-%m-%dT%H:%M")

            valor_total = self.locacao_model.calcular_valor_previsto(
                id_veiculo, dt_retirada, dt_prevista, opcionais)

            return jsonify({"valor_total_previsto": valor_total})

        except Exception as e:
            return jsonify({"erro": str(e)}), 500

    def listar_historico_locacao(self):
        if "usuario_logado" not in session:
            return jsonify({"erro": "Acesso não autorizado. Faça login."}), 401

        perfil = session.get("perfil")
        email_usuario = session.get("usuario_logado")

        try:
            locacoes = self.locacao_model.listar_historico(
                perfil, email_usuario)
            return jsonify(locacoes), 200
        except Exception as e:
            print(f"Erro ao buscar histórico: {e}")
            return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

    def calcular_simulacao(self, id_loc):
        dados_chegada = request.get_json()
        data_devolucao_real = dados_chegada.get("data_devolucao_real")
        km_chegada = dados_chegada.get("km_chegada")
        tanque_chegada = dados_chegada.get("tanque_chegada")

        if not data_devolucao_real or km_chegada is None or tanque_chegada is None:
            return jsonify({"erro": "Faltando campos de chegada para simulação."}), 400

        try:
            resultado = self.locacao_model.simular_valor_final(
                id_loc, dados_chegada)

            if 'erro' in resultado:
                return jsonify(resultado), 400

            return jsonify({
                "mensagem": "Valor final simulado com sucesso",
                "valor_total_previsto": resultado["valor_total_previsto"],
                "valor_final": resultado["valor_final"]
            }), 200

        except Exception as e:
            print("ERRO calcular_simulacao controller:", e)
            return jsonify({"erro": str(e)}), 500
        
    def deletar_locacao(self, id_locacao):
        # Apenas Gerente ou Atendente podem deletar locações
        if session.get("perfil") not in ["Gerente", "Atendente"]:
            abort(403)

        try:
            if self.locacao_model.deletar_locacao(id_locacao):
                flash("Locação removida com sucesso! O veículo está novamente disponível.", "success")
            else:
                flash("Erro ao remover locação. Locação não encontrada ou falha no banco de dados.", "error")
        except Exception as e:
            print(f"Erro ao deletar locação {id_locacao}: {e}")
            flash("Erro interno ao tentar deletar a locação.", "error")
            
        return redirect(url_for("locacao.historico_locacao"))
