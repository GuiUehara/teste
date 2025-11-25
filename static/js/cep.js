// Função genérica para limpar campos de endereço
function clearAddressFields(logradouroId, bairroId, cidadeId, estadoId) {
    document.getElementById(logradouroId).value = '';
    document.getElementById(bairroId).value = '';
    document.getElementById(cidadeId).value = '';
    document.getElementById(estadoId).value = '';
}

// Função genérica para consultar o CEP
function consultaCep(cepFieldId, logradouroId, bairroId, cidadeId, estadoId) {
    const cepInput = document.getElementById(cepFieldId);
    const cep = cepInput.value.replace(/\D/g, ''); // remove tudo que não for número

    if (cep.length !== 8) {
        alert("Por favor, digite um CEP válido com 8 números.");
        clearAddressFields(logradouroId, bairroId, cidadeId, estadoId);
        return;
    }

    // Mostra um feedback de "carregando" (opcional)
    document.getElementById(logradouroId).value = "Buscando...";
    document.getElementById(bairroId).value = "Buscando...";

    fetch(`/api/cep/${cep}`)
        .then(resp => resp.json())
        .then(dados => {
            if (dados.erro) {
                alert("CEP não encontrado.");
                clearAddressFields(logradouroId, bairroId, cidadeId, estadoId);
                return;
            }
            document.getElementById(logradouroId).value = dados.logradouro || '';
            document.getElementById(bairroId).value = dados.bairro || '';
            document.getElementById(cidadeId).value = dados.localidade || '';
            document.getElementById(estadoId).value = dados.uf || '';
        })
        .catch(() => {
            alert("Erro ao consultar o CEP.");
            clearAddressFields(logradouroId, bairroId, cidadeId, estadoId);
        });
}