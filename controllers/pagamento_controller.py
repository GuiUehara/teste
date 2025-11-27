from flask import render_template, request, redirect, url_for, flash, session
from models.pagamento_model import PagamentoModel


class PagamentoController:
    def __init__(self):
        self.pagamento_model = PagamentoModel()

    # Processa o pagamento de uma locação
    def processar(self):
        id_locacao = session.get('id_locacao_pagamento')
        if not id_locacao:
            flash("Nenhuma reserva encontrada para pagamento.", "warning")
            return redirect(url_for("veiculos.grupo_carros"))

        try:
            locacao = self.pagamento_model.get_dados_locacao_para_pagamento(
                id_locacao)

            if not locacao:
                flash("Locação não encontrada.", "error")
                return redirect(url_for("veiculos.grupo_carros"))
            # Pega os valores brutos
            valor_bruto = locacao['valor_total_previsto']
            caucao_bruto = locacao.get('caucao', 0.0)
            
            # --- Correção 1: Criando as variáveis certas ---
            valor_formatado = "{:.2f}".format(float(valor_bruto))
            caucao_formatado = "{:.2f}".format(float(caucao_bruto))

            formas_pagamento = self.pagamento_model.get_formas_pagamento()

            if request.method == "POST":
                id_forma_pagamento = request.form.get("forma_pagamento")

                if not id_forma_pagamento:
                    flash("Selecione uma forma de pagamento.", "error")
                    return render_template(
                        "pagamento.html", 
                        valor_a_pagar=valor_formatado, 
                        caucao=caucao_formatado,     
                        formas_pagamento=formas_pagamento
                    )

                self.pagamento_model.registrar_pagamento(
                    id_locacao, id_forma_pagamento, valor_bruto)

                flash("Pagamento registrado com sucesso!", "success")
                session.pop('id_locacao_pagamento', None)  
                return redirect(url_for("pagamento.pagamento_concluido"))

            return render_template(
                "pagamento.html", 
                valor_a_pagar=valor_formatado, 
                caucao=caucao_formatado,       
                formas_pagamento=formas_pagamento
            )

        except Exception as e:
            flash(f"Ocorreu um erro ao processar o pagamento: {e}", "error")
            return redirect(url_for("veiculos.grupo_carros"))
