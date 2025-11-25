var opcionaisTemp = []; // Usando var para consistência com locacao.js

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
        btn.onclick = () => {
            opcionaisTemp.splice(idx, 1);
            listarOpcionaisTemp(listaId);
            document.dispatchEvent(new Event('opcionaisAtualizados'));
        };
        li.appendChild(btn);
        lista.appendChild(li);
    });
}

// Atualiza valor_total_previsto em tempo real
async function atualizarValorPrevisto() {
    const idVeiculo = document.getElementById("veiculo").value;
    const dataRetirada = document.getElementById("data_retirada").value;
    const dataPrevista = document.getElementById("data_devolucao_prevista").value;
    const inputValor = document.getElementById("valor_total_previsto");
    
    // Elementos visuais do resumo
    const displayValorTotal = document.getElementById("valor_total_previsto_display");
    const displayDiaria = document.getElementById("diaria_valor");
    const displayOpcionais = document.getElementById("opcionais_valor");
    const displayDetalheTotal = document.getElementById("valor_previsto_detalhe");

    if (!idVeiculo || !dataRetirada || !dataPrevista) {
        inputValor.value = 0;
        return;
    }

    const dados = {
        id_veiculo: parseInt(idVeiculo),
        data_retirada: dataRetirada,
        data_devolucao_prevista: dataPrevista,
        opcionais: opcionaisTemp.map(op => ({
            id_opcional: op.id_opcional,
            quantidade: op.quantidade
        }))
    };

    try {
        const res = await fetch("/api/valor-previsto-reserva", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dados)
        });
        if (res.ok) {
            const json = await res.json();
            if (json.valor_total_previsto !== undefined) {
                const valorTotal = parseFloat(json.valor_total_previsto);
                const valorDiaria = parseFloat(json.diaria_veiculo);
                const valorOpcionais = parseFloat(json.valor_opcionais);

                // 1. Atualiza o input oculto para o formulário
                inputValor.value = valorTotal.toFixed(2);

                // 2. Atualiza os elementos visíveis no card de resumo
                const formatarMoeda = (valor) => valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

                displayValorTotal.textContent = valorTotal.toFixed(2).replace('.', ',');
                displayDiaria.textContent = formatarMoeda(valorDiaria);
                displayOpcionais.textContent = formatarMoeda(valorOpcionais);
                displayDetalheTotal.textContent = formatarMoeda(valorTotal);
            }
        }
    } catch (err) {
        console.error("Erro ao calcular valor previsto:", err);
    }
}

// Função para salvar a reserva e redirecionar
async function salvarReserva() {
    const idVeiculo = document.getElementById("veiculo").value;
    const dataRetirada = document.getElementById("data_retirada").value;
    const dataPrevista = document.getElementById("data_devolucao_prevista").value;

    const dados = {
        id_veiculo: parseInt(idVeiculo),
        data_retirada: dataRetirada,
        data_devolucao_prevista: dataPrevista,
        opcionais: opcionaisTemp
    };

    try {
        const res = await fetch("/reserva/criar", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dados)
        });
        const resp = await res.json();
        if (resp.sucesso) {
            window.location.href = resp.redirect;
        } else {
            alert("Erro ao criar reserva: " + (resp.erro || "Erro desconhecido"));
        }
    } catch (err) {
        console.error(err);
        alert("Erro de conexão ao tentar salvar a reserva.");
    }
}
