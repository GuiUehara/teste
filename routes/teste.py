from flask import render_template, flash

def init_teste(app):
    @app.route("/teste", methods=["GET", "POST"])
    def teste():
        flash("Teste")
        return render_template("teste.html")  # <- DENTRO da função
