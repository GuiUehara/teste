/**
 * Valida os dados do formulário de funcionário.
 * @param {object} dados - O objeto com os dados do funcionário.
 * @returns {string[]} Uma lista de mensagens de erro. Se a lista estiver vazia, os dados são válidos.
 */
function validarDadosFuncionario(dados) {
    const erros = [];
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const cpfRegex = /^\d{11}$/;

    if (!dados.nome) erros.push("O campo 'Nome' é obrigatório.");
    if (!dados.rg) erros.push("O campo 'RG' é obrigatório.");
    if (!dados.dataNasc) erros.push("O campo 'Data de Nascimento' é obrigatório.");
    if (!dados.sexo) erros.push("O campo 'Sexo' é obrigatório.");
    if (!dados.endereco) erros.push("O campo 'Endereço' é obrigatório.");
    if (!dados.senha) erros.push("O campo 'Senha' é obrigatório.");

    // Validações de formato
    if (!dados.cpf || !cpfRegex.test(dados.cpf)) {
        erros.push("O CPF deve conter 11 dígitos numéricos.");
    }
    if (!dados.email || !emailRegex.test(dados.email)) {
        erros.push("O formato do e-mail é inválido.");
    }

    return erros;
}

/**
 * Manipula o evento de submissão do formulário de cadastro de funcionário.
 * @param {Event} event - O objeto do evento.
 */
function cadastrarFuncionario(event) {
    event.preventDefault();
    const form = event.target;

    const dadosFuncionario = {
        nome: form.nomeFuncionario.value.trim(),
        cpf: form.cpfFuncionario.value.replace(/\D/g, ''), // Remove não-dígitos
        rg: form.rgFuncionario.value.trim(),
        dataNasc: form.dataNascFuncionario.value,
        endereco: form.enderecoFuncionario.value.trim(),
        email: form.emailFuncionario.value.trim(),
        senha: form.senhaFuncionario.value,
    };

    const erros = validarDadosFuncionario(dadosFuncionario);

    if (erros.length > 0) {
        alert("Por favor, corrija os seguintes erros:\n- " + erros.join("\n- "));
        return;
    }

    // Se a validação passar, pode prosseguir com o envio para a API.
    // Por enquanto, apenas exibe um alerta de sucesso.
    alert("Dados do funcionário válidos! (Implementar envio para API)");
}

document.addEventListener('DOMContentLoaded', () => {
    const formFuncionario = document.getElementById('formFuncionario');
    if (formFuncionario) {
        formFuncionario.addEventListener('submit', cadastrarFuncionario);
    }
});
