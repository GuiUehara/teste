const veiculos = [];

function atualizarValorPorFracao() {
    const tanque = parseFloat(document.getElementById('tanque').value) || 0;
    const fracao = parseFloat(document.getElementById('tanqueFracao').value) || 1;
    const valorCombustivel = 6.50;
    const valorFinal = tanque * fracao * valorCombustivel + 8;
    document.getElementById('valorPorFracao').value = valorFinal.toFixed(2);
}

/**
 * Valida os dados do formulário de veículo.
 * @param {object} dadosVeiculo - O objeto com os dados do veículo.
 * @returns {string[]} Uma lista de mensagens de erro.
 */
function validarDadosVeiculo(dadosVeiculo) {
    const erros = [];
    // Regex para placa padrão (ABC1234) e Mercosul (ABC1D23)
    const placaRegex = /^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$/;

    if (!dadosVeiculo.placa || !placaRegex.test(dadosVeiculo.placa)) {
        erros.push("A placa do veículo é inválida. Use o formato ABC1234 ou ABC1D23.");
    }
    if (!dadosVeiculo.renavam) erros.push("O campo 'Renavam' é obrigatório.");
    if (!dadosVeiculo.chassi) erros.push("O campo 'Chassi' é obrigatório.");
    if (!dadosVeiculo.marca) erros.push("O campo 'Marca' é obrigatório.");
    if (!dadosVeiculo.modelo) erros.push("O campo 'Modelo' é obrigatório.");
    if (!dadosVeiculo.ano) erros.push("O campo 'Ano' é obrigatório.");
    if (!dadosVeiculo.cor) erros.push("O campo 'Cor' é obrigatório.");
    if (!dadosVeiculo.transmissao) erros.push("O campo 'Transmissão' é obrigatório.");

    return erros;
}

function cadastrarVeiculo(event) {
    event.preventDefault();
    const form = event.target;

    const dadosVeiculo = {
        placa: form.placaVeiculo.value.trim().toUpperCase(),
        renavam: form.renavamVeiculo.value.trim(),
        chassi: form.chassiVeiculo.value.trim().toUpperCase(),
        marca: form.marcaVeiculo.value.trim(),
        modelo: form.modeloVeiculo.value.trim(),
        ano: form.anoVeiculo.value.trim(),
        cor: form.corVeiculo.value.trim(),
        transmissao: form.transmissaoVeiculo.value,
        motor: form.motorVeiculo.value.trim(),
        dataCompra: form.dataCompra.value,
        valorCompra: parseFloat(form.valorCompra.value),
        odometro: parseInt(form.odometro.value),
        vencimentoLicenciamento: form.vencimentoLicenciamento.value,
        companhiaSeguro: form.companhiaSeguro.value.trim(),
        vencimentoSeguro: form.vencimentoSeguro.value,
        tanqueFracao: form.tanqueFracao.value,
        valorPorFracao: parseFloat(form.valorPorFracao.value),
        tiposCombustivel: form.tiposCombustivel.value
    };

    const erros = validarDadosVeiculo(dadosVeiculo);
    if (erros.length > 0) {
        alert("Por favor, corrija os seguintes erros:\n- " + erros.join("\n- "));
        return;
    }

    veiculos.push(dadosVeiculo);
    atualizarListaVeiculos();
    form.reset();
    form.valorPorFracao.value = '';
    alert("Veículo cadastrado com sucesso!");
}

function atualizarListaVeiculos() {
    const lista = document.getElementById('listaVeiculos');
    if (!lista) return;
    lista.innerHTML = '';
    veiculos.forEach(v => {
        const li = document.createElement('li');
        li.textContent = `${v.marca} ${v.modelo} - Placa: ${v.placa} - Ano: ${v.ano} - Cor: ${v.cor}`;
        lista.appendChild(li);
    });
}


document.addEventListener('DOMContentLoaded', () => {
    const formVeiculo = document.getElementById('formVeiculo');
    if (formVeiculo) {
        formVeiculo.addEventListener('submit', cadastrarVeiculo);
    }
    // Adiciona os listeners apenas uma vez
    const tanqueInput = document.getElementById('tanque');
    const tanqueFracaoSelect = document.getElementById('tanqueFracao');
    if (tanqueInput) tanqueInput.addEventListener('input', atualizarValorPorFracao);
    if (tanqueFracaoSelect) tanqueFracaoSelect.addEventListener('change', atualizarValorPorFracao);
});
