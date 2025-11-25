var opcionaisTemp = []; 

// Carrega os opcionais disponíveis da API e popula um <select>
function carregarOpcionais(selectId) {
    fetch('/api/opcionais')
        .then(res => res.json())
        .then(opcionais => {
            const select = document.getElementById(selectId);
            if (!select) return;
            select.innerHTML = '<option value="">Selecione um opcional</option>';
            opcionais.forEach(o => {
                const option = document.createElement("option");
                option.value = o.id_opcional;
                option.textContent = `${o.descricao} - R$ ${parseFloat(o.valor_diaria).toFixed(2)}`;
                option.dataset.valor = parseFloat(o.valor_diaria);
                select.appendChild(option);
            });
        })
        .catch(err => console.error("Erro ao carregar opcionais:", err));
}

// Adiciona um opcional à lista temporária 'opcionaisTemp'
function adicionarOpcionalTemp(selectId, quantidadeId) {
    const select = document.getElementById(selectId);
    const quantidadeInput = document.getElementById(quantidadeId);
    if (!select || !quantidadeInput) return;

    const quantidade = parseInt(quantidadeInput.value);
    const id_opcional = parseInt(select.value);
    if (!id_opcional || quantidade < 1) return;

    const descricao = select.options[select.selectedIndex].text.split(" - R$")[0];
    const valor_diaria = parseFloat(select.options[select.selectedIndex].dataset.valor);

    const existente = opcionaisTemp.find(o => o.id_opcional === id_opcional);
    if (existente) {
        existente.quantidade += quantidade;
    } else {
        opcionaisTemp.push({ id_opcional, descricao, quantidade, valor_diaria });
    }

    listarOpcionaisTemp('lista-opcionais');
    // Dispara um evento para que outras funções (como a de cálculo) saibam da mudança
    document.dispatchEvent(new Event('opcionaisAtualizados'));
}

// Renderiza a lista de opcionais selecionados em uma <ul>
function listarOpcionaisTemp(listaId) {
    const lista = document.getElementById(listaId);
    if (!lista) return;

    lista.innerHTML = "";
    if (opcionaisTemp.length === 0) {
        lista.innerHTML = "<li>Nenhum opcional adicionado.</li>";
        return;
    }

    opcionaisTemp.forEach((op, idx) => {
        const li = document.createElement("li");
        li.textContent = `${op.descricao} - R$ ${op.valor_diaria.toFixed(2)} x ${op.quantidade}`;
        const btn = document.createElement("button");
        btn.textContent = "Remover";
        btn.type = "button";
        btn.className = "btn-remover-opcional"; 
        btn.onclick = () => {
            opcionaisTemp.splice(idx, 1);
            listarOpcionaisTemp(listaId);
            document.dispatchEvent(new Event('opcionaisAtualizados'));
        };
        li.appendChild(btn);
        lista.appendChild(li);
    });
}