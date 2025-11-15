from flask import render_template, request, redirect, url_for, flash, session
from db import conectar

def init_veiculos(app):

    @app.route("/cadastro_veiculo", methods=["GET", "POST"])
    def cadastro_veiculo():
        if "usuario_logado" not in session:
            flash("Faça login para acessar", "error")
            return redirect(url_for("login"))

        conexao = conectar()
        cursor = conexao.cursor()

        #busca os dados
        cursor.execute("SELECT id_combustivel, tipo_combustivel FROM combustivel")
        combustiveis = cursor.fetchall()

        cursor.execute("SELECT id_marca, nome_marca FROM marca")
        marcas = cursor.fetchall()

        cursor.execute("SELECT id_modelo, nome_modelo FROM modelo")
        modelos = cursor.fetchall()

        cursor.execute("SELECT id_categoria_veiculo, nome_categoria FROM categoria_veiculo")
        categorias = cursor.fetchall()


        cursor.execute("SELECT id_status_veiculo, descricao_status FROM status_veiculo")
        status = cursor.fetchall()

        if request.method == "POST":

            placa = request.form.get("placaVeiculo")
            chassi = request.form.get("chassiVeiculo")
            ano = int(request.form.get("anoVeiculo"))
            cor = request.form.get("corVeiculo")
            transmissao = request.form.get("transmissaoVeiculo")
            data_compra = request.form.get("dataCompra")
            valor_compra = float(request.form.get("valorCompra"))
            odometro = int(request.form.get("odometro"))
            data_vencimento = request.form.get("vencimentoLicenciamento")

            tanque = int(request.form.get("tanque"))
            tanque_fracao = float(request.form.get("tanqueFracao"))

            valor_fracao = (tanque * 6) / 8 + 5 # '6' referente a um valor fixo para combustível; '8' indica fração; '5' uma taxa fixa para o funcionário ir abastecer

            modelo_nome = request.form.get("modeloVeiculo").strip()
            marca_nome = request.form.get("marca").strip()
            categoria_nome = request.form.get("categoria").strip()
            id_status = request.form.get("status")
            id_combustivel = request.form.get("combustivel")

            # Verifica se a placa já existe
            cursor.execute("SELECT 1 FROM veiculo WHERE placa = %s", (placa,))
            if cursor.fetchone():
                flash("Já existe um veículo cadastrado com essa placa.", "error")
                cursor.close()
                conexao.close()
                return redirect(url_for("cadastro_veiculo"))

            # Verifica se o chassi já existe
            cursor.execute("SELECT 1 FROM veiculo WHERE chassi = %s", (chassi,))
            if cursor.fetchone():
                flash("Já existe um veículo cadastrado com esse chassi.", "error")
                cursor.close()
                conexao.close()
                return redirect(url_for("cadastro_veiculo"))


           # Marca
            cursor.execute("SELECT id_marca FROM marca WHERE nome_marca = %s", (marca_nome,))
            resultado_marca = cursor.fetchone()

            if resultado_marca: #se marca estiver registrada
                id_marca = resultado_marca[0] #pega ID da marca
            else:
                cursor.execute("INSERT INTO marca (nome_marca) VALUES (%s)", (marca_nome,))
                conexao.commit()
                id_marca = cursor.lastrowid #gera ID caso não esteja registrada

            # Categoria
            cursor.execute("SELECT id_categoria_veiculo FROM categoria_veiculo WHERE nome_categoria = %s", (categoria_nome,))
            resultado_categoria = cursor.fetchone()

            if resultado_categoria:
                id_categoria = resultado_categoria[0]
            else:
                cursor.execute("INSERT INTO categoria_veiculo (nome_categoria, valor_diaria) VALUES (%s, %s)",
                            (categoria_nome, 100))  # valor padrão
                conexao.commit()
                id_categoria = cursor.lastrowid

            # Modelo digitado
            cursor.execute("""
                SELECT id_modelo FROM modelo
                WHERE nome_modelo = %s AND id_marca = %s AND id_categoria_veiculo = %s
            """, (modelo_nome, id_marca, id_categoria))

            resultado_modelo = cursor.fetchone()

            if resultado_modelo:
                id_modelo = resultado_modelo[0]
            else:
                cursor.execute("""
                    INSERT INTO modelo (nome_modelo, id_marca, id_categoria_veiculo)
                    VALUES (%s, %s, %s)
                """, (modelo_nome, id_marca, id_categoria))
                conexao.commit()
                id_modelo = cursor.lastrowid


            sql = """
                INSERT INTO veiculo
                (placa, ano, cor, chassi, quilometragem, transmissao, data_compra,
                valor_compra, data_vencimento, tanque, tanque_fracao, valor_fracao,
                id_modelo, id_status_veiculo, id_combustivel)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(sql, (
                placa, ano, cor, chassi, odometro, transmissao, data_compra,
                valor_compra, data_vencimento, tanque, tanque_fracao, valor_fracao,
                id_modelo, id_status, id_combustivel
            ))

            conexao.commit()
            cursor.close()
            conexao.close()

            flash("Veículo cadastrado com sucesso!", "success")
            return redirect(url_for("cadastro_veiculo"))

        return render_template("cadastro_veiculo.html",
                               combustiveis=combustiveis,
                               marcas=marcas,
                               categorias=categorias,
                               modelos=modelos,
                               status=status)



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