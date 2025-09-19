from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "chave-secreta"

veiculos = [
    {"id": 1, "modelo": "Toyota Corolla", "placa": "ABC-1234", "status": "disponível"},
    {"id": 2, "modelo": "Fiat Uno", "placa": "XYZ-5678", "status": "disponível"},
    {"id": 3, "modelo": "Honda Civic", "placa": "DEF-9012", "status": "alugado"},
]

clientes = []
usuarios = {"admin": {"senha": "1234"}}

@app.route('/')
def index():
    return redirect(url_for("login"))

@app.route('/cadastro', methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        if not nome or not email or not senha:
            flash("Preencha todos os campos", "error")
            return redirect(url_for("cadastro"))
        usuarios[nome] = {"senha": senha}
        flash("Cadastro salvo. Faça login.", "success")
        return redirect(url_for("login"))
    return render_template("cadastro.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nome = request.form.get("nome")
        senha = request.form.get("senha")
        if nome in usuarios and usuarios[nome]["senha"] == senha:
            session["usuario_logado"] = nome
            flash(f"Bem vindo, {nome}", "success")
            return redirect(url_for("listagem_veiculos"))
        else:
            flash("Usuário ou senha inválidos", "error")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop("usuario_logado", None)
    flash("Sessão encerrada.", "success")
    return redirect(url_for("login"))

@app.route("/cadastro_cliente", methods=["GET", "POST"])
def cadastro_cliente():
    if "usuario_logado" not in session:
        flash("Faça login para acessar", "error")
        return redirect(url_for("login"))
    if request.method == "POST":
        cliente = {
            "nome": request.form.get("nomeCliente"),
            "cpf": request.form.get("cpfCliente"),
            "dataNasc": request.form.get("dataNascCliente"),
            "telefone": request.form.get("telefoneCliente"),
            "email": request.form.get("emailCliente"),
            "endereco": request.form.get("enderecoCliente"),
            "cnh": request.form.get("cnhCliente"),
            "categoriaCNH": request.form.get("categoriaCNHCliente"),
            "validadeCNH": request.form.get("validadeCNHCliente"),
            "tempoHabilitacao": request.form.get("tempoHabilitacaoCliente"),
            "formaPagamento": request.form.get("formaPagamentoCliente"),
        }
        clientes.append(cliente)
        flash("Cliente cadastrado com sucesso!", "success")
        return redirect(url_for("cadastro_cliente"))
    return render_template("cadastro_cliente.html")

@app.route("/cadastro_veiculo", methods=["GET", "POST"])
def cadastro_veiculo():
    if "usuario_logado" not in session:
        flash("Faça login para acessar", "error")
        return redirect(url_for("login"))
    if request.method == "POST":
        novo_id = len(veiculos) + 1
        veiculo = {
            "id": novo_id,
            "modelo": request.form.get("modeloVeiculo"),
            "placa": request.form.get("placaVeiculo"),
            "ano": request.form.get("anoVeiculo"),
            "status": "disponível",
        }
        veiculos.append(veiculo)
        flash("Veículo cadastrado com sucesso!", "success")
        return redirect(url_for("cadastro_veiculo"))
    return render_template("cadastro_veiculo.html")

@app.route("/veiculos")
def listagem_veiculos():
    if "usuario_logado" not in session:
        flash("Faça login para acessar", "error")
        return redirect(url_for("login"))
    return render_template("veiculos.html", veiculos=veiculos)

@app.route("/locar/<int:id>", methods=["POST"])
def locar_veiculo(id):
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

if __name__ == "__main__":
    app.run(debug=True)
