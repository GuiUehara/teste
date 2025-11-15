document.getElementById("redefinirSenhaForm").addEventListener("submit", function(event) {
    var novaSenha = document.querySelector("input[name='nova_senha']").value;
    var confirmarSenha = document.querySelector("input[name='confirmar_senha']").value;

    if (novaSenha !== confirmarSenha) {
        alert("As senhas não coincidem. Tente novamente.");
        event.preventDefault();  // Impede o envio do formulário
    }
});
