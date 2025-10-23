from flask import render_template, request, redirect, url_for, flash, session

def init_veiculos(app):

    @app.route("/cadastro_veiculo", methods=["GET", "POST"])
    def cadastro_veiculo():
        from app import veiculos
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))
        if request.method == "POST":
            novo_id = len(veiculos) + 1
            
            veiculo = {
                "id": novo_id,
                "placa": request.form.get("placaVeiculo"),
                "renavam": request.form.get("renavamVeiculo"),
                "chassi": request.form.get("chassiVeiculo"),
                "marca": request.form.get("marcaVeiculo"),
                "modelo": request.form.get("modeloVeiculo"),
                "ano": request.form.get("anoVeiculo"),
                "cor": request.form.get("corVeiculo"),
                "transmissao": request.form.get("transmissaoVeiculo"),
                "motor": request.form.get("motorVeiculo"),
                "data_compra": request.form.get("dataCompra"),
                "valor_compra": float(request.form.get("valorCompra") or 0),
                "odometro": int(request.form.get("odometro") or 0),
                "vencimento_licenciamento": request.form.get("vencimentoLicenciamento"),
                "companhia_seguro": request.form.get("companhiaSeguro"),
                "vencimento_seguro": request.form.get("vencimentoSeguro"),
                "tanque_fracao": request.form.get("tanqueFracao"),
                "valor_por_fracao": float(request.form.get("valorPorFracao") or 0),
                "tipos_combustivel": request.form.getlist("tipoCombustivel"),
                "status": "disponível",
            }
            veiculos.append(veiculo)
            flash("Veículo cadastrado com sucesso!", "success")
            return redirect(url_for("cadastro_veiculo"))
        return render_template("cadastro_veiculo.html")

    @app.route("/veiculos")
    def listagem_veiculos():
        from app import veiculos
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))
        return render_template("veiculos.html", veiculos=veiculos)
    
    @app.route("/locar/<int:id>", methods=["POST"])
    def locar_veiculo(id):
        from app import veiculos
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))
        for veiculo in veiculos:
            if veiculo["id"] == id:
                if veiculo["status"] == "disponível":
                    veiculo["status"] = "alugado"
                    flash(f"Veículo {veiculo['modelo']} alugado com sucesso!", "success")
                else:
                    flash(f"O veículo {veiculo['modelo']} já está alugado.", "error")
                break
        else:
            flash("Veículo não encontrado.", "error")
        return redirect(url_for("listagem_veiculos"))
from flask import render_template, request, redirect, url_for, flash, session

def init_veiculos(app):

    @app.route("/cadastro_veiculo", methods=["GET", "POST"])
    def cadastro_veiculo():
        from app import veiculos
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))
        if request.method == "POST":
            novo_id = len(veiculos) + 1
            
            veiculo = {
                "id": novo_id,
                "placa": request.form.get("placaVeiculo"),
                "renavam": request.form.get("renavamVeiculo"),
                "chassi": request.form.get("chassiVeiculo"),
                "marca": request.form.get("marcaVeiculo"),
                "modelo": request.form.get("modeloVeiculo"),
                "ano": request.form.get("anoVeiculo"),
                "cor": request.form.get("corVeiculo"),
                "transmissao": request.form.get("transmissaoVeiculo"),
                "motor": request.form.get("motorVeiculo"),
                "data_compra": request.form.get("dataCompra"),
                "valor_compra": float(request.form.get("valorCompra") or 0),
                "odometro": int(request.form.get("odometro") or 0),
                "vencimento_licenciamento": request.form.get("vencimentoLicenciamento"),
                "companhia_seguro": request.form.get("companhiaSeguro"),
                "vencimento_seguro": request.form.get("vencimentoSeguro"),
                "tanque_fracao": request.form.get("tanqueFracao"),
                "valor_por_fracao": float(request.form.get("valorPorFracao") or 0),
                "tipos_combustivel": request.form.getlist("tipoCombustivel"),
                "status": "disponível",
            }
            veiculos.append(veiculo)
            flash("Veículo cadastrado com sucesso!", "success")
            return redirect(url_for("cadastro_veiculo"))
        return render_template("cadastro_veiculo.html")

    @app.route("/veiculos")
    def listagem_veiculos():
        from app import veiculos
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))
        return render_template("veiculos.html", veiculos=veiculos)
    
    @app.route("/locar/<int:id>", methods=["POST"])
    def locar_veiculo(id):
        from app import veiculos
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))
        for veiculo in veiculos:
            if veiculo["id"] == id:
                if veiculo["status"] == "disponível":
                    veiculo["status"] = "alugado"
                    flash(f"Veículo {veiculo['modelo']} alugado com sucesso!", "success")
                else:
                    flash(f"O veículo {veiculo['modelo']} já está alugado.", "error")
                break
        else:
            flash("Veículo não encontrado.", "error")
        return redirect(url_for("listagem_veiculos"))
