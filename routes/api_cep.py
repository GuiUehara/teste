from flask import Blueprint, jsonify
import requests

cep_api = Blueprint("cep_api", __name__)

# API externa para buscar informações de CEP

@cep_api.route("/api/cep/<cep>", methods=["GET"])
def buscar_cep(cep):
    cep = cep.replace("-", "").replace(".", "").replace(" ", "")

    if len(cep) != 8:
        return jsonify({"erro": "CEP inválido"}), 400

    url = f"https://viacep.com.br/ws/{cep}/json/"
    resp = requests.get(url)

    if resp.status_code != 200:
        return jsonify({"erro": "Não foi possível consultar o CEP"}), 500

    dados = resp.json()
    if "erro" in dados:
        return jsonify({"erro": "CEP não encontrado"}), 404

    return jsonify(dados)
