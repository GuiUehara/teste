const clientes = [];

/**
 * Valida os dados do formulário de cliente.
 * @param {object} dadosCliente - O objeto com os dados do cliente.
 * @returns {string[]} Uma lista de mensagens de erro. Se a lista estiver vazia, os dados são válidos.
 */
function validarDadosCliente(dadosCliente) {
    const erros = [];
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const cpfRegex = /^\d{11}$/;

    if (!dadosCliente.nome) erros.push("O campo 'Nome' é obrigatório.");
    if (!dadosCliente.dataNasc) erros.push("O campo 'Data de Nascimento' é obrigatório.");
    if (!dadosCliente.telefone) erros.push("O campo 'Telefone' é obrigatório.");
    if (!dadosCliente.endereco) erros.push("O campo 'Endereço' é obrigatório.");
    if (!dadosCliente.cnh) erros.push("O campo 'CNH' é obrigatório.");
    if (!dadosCliente.categoriaCNH) erros.push("O campo 'Categoria CNH' é obrigatório.");
    if (!dadosCliente.validadeCNH) erros.push("O campo 'Validade CNH' é obrigatório.");
    if (!dadosCliente.tempoHabilitacao) erros.push("O campo 'Tempo de Habilitação' é obrigatório.");

    // Validações de formato
    if (!dadosCliente.cpf || !cpfRegex.test(dadosCliente.cpf)) {
        erros.push("O CPF deve conter 11 dígitos numéricos.");
    }
    if (!dadosCliente.email || !emailRegex.test(dadosCliente.email)) {
        erros.push("O formato do e-mail é inválido.");
    }

    return erros;
}

function cadastrarCliente(event) {
    event.preventDefault();
    const form = event.target;

    const dadosCliente = {
        nome: form.nomeCliente.value.trim(),
        cpf: form.cpfCliente?.value.replace(/\D/g, '') || '', // Remove não-dígitos
        dataNasc: form.dataNascCliente?.value || '',
        telefone: form.telefoneCliente.value.trim(),
        email: form.emailCliente.value.trim(),
        endereco: form.enderecoCliente?.value.trim() || '',
        cnh: form.cnhCliente?.value.trim() || '',
        categoriaCNH: form.categoriaCNHCliente?.value.trim() || '',
        validadeCNH: form.validadeCNHCliente?.value || '',
        tempoHabilitacao: form.tempoHabilitacaoCliente?.value || '',
        formaPagamento: form.formaPagamentoCliente?.value.trim() || ''
    };

    const erros = validarDadosCliente(dadosCliente);

    if (erros.length > 0) {
        alert("Por favor, corrija os seguintes erros:\n- " + erros.join("\n- "));
        return;
    }

    // Adiciona à lista local (comportamento original)
    clientes.push(dadosCliente);
    atualizarListaClientes();
    form.reset();
    alert("Cliente cadastrado com sucesso!");
}

function atualizarListaClientes() {
    const lista = document.getElementById('listaClientes');
    if (!lista) return;
    lista.innerHTML = '';
    clientes.forEach(c => {
        const li = document.createElement('li');
        li.textContent = `${c.nome} - CPF: ${c.cpf} - CNH: ${c.cnh} (${c.categoriaCNH}) - Email: ${c.email}`;
        lista.appendChild(li);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const formCliente = document.getElementById('formCliente');
    if (formCliente) formCliente.addEventListener('submit', cadastrarCliente);
});
