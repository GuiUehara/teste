document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("pagamentoForm");

  form.addEventListener("submit", function (event) {
    let errors = [];

    const nomeNoCartao = form.nome_no_cartao.value.trim();
    const numeroCartao = form.numero_cartao.value.trim();
    const validade = form.validade.value.trim();
    const cvv = form.cvv.value.trim();
    const cpf = form.cpf.value.trim();

    if (nomeNoCartao === "") {
      errors.push("O nome no cartão é obrigatório.");
    }

    if (!/^\d{16}$/.test(numeroCartao)) {
      errors.push("Número do cartão deve ter 16 dígitos.");
    }

    if (!/^(0[1-9]|1[0-2])\/\d{2}$/.test(validade)) {
      errors.push("Validade deve estar no formato MM/AA.");
    }

    if (!/^\d{3,4}$/.test(cvv)) {
      errors.push("CVV deve ter 3 ou 4 dígitos.");
    }

    if (!/^\d{11}$/.test(cpf)) {
      errors.push("CPF deve ter 11 dígitos sem pontos ou traços.");
    }

    if (errors.length > 0) {
      event.preventDefault(); // Impede envio
      alert(errors.join("\n"));
    }
  });
});
