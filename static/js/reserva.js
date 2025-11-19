let opcionaisTemp = [];

// Carregar opcionais disponíveis
function carregarOpcionais() {
    fetch('/api/opcionais')
        .then(res => res.json())
        .then(opcionais => {
            const select = document.getElementById("select-opcional");
            select.innerHTML = '<option value="">Selecione</option>';
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

// Adiciona item ao carrinho de opcionais
function adicionarOpcionalTemp() {
    const select = document.getElementById("select-opcional");
    const quantidade = parseInt(document.getElementById("quantidade-opcional").value);
    const id_opcional = parseInt(select.value);
    if (!id_opcional || quantidade < 1) return;

    const descricao = select.options[select.selectedIndex].text.split(" - R$")[0];
    const valor_diaria = parseFloat(select.options[select.selectedIndex].dataset.valor);

    const existente = opcionaisTemp.find(o => o.id_opcional === id_opcional);
    if (existente) existente.quantidade += quantidade;
    else opcionaisTemp.push({ id_opcional, descricao, quantidade, valor_diaria });

    listarOpcionaisTemp();
    atualizarValorPrevisto();
}

// Atualiza a lista visual do carrinho
function listarOpcionaisTemp() {
    const lista = document.getElementById("lista-opcionais");
    lista.innerHTML = "";
    opcionaisTemp.forEach((op, idx) => {
        const li = document.createElement("li");
        li.textContent = `${op.descricao} - R$ ${op.valor_diaria.toFixed(2)} x ${op.quantidade}`;
        const btn = document.createElement("button");
        btn.textContent = "Remover";
        btn.type = "button";
        btn.onclick = () => {
            opcionaisTemp.splice(idx, 1);
            listarOpcionaisTemp();
            atualizarValorPrevisto();
        };
        li.appendChild(btn);
        lista.appendChild(li);
    });
}

// Atualiza valor_total_previsto em tempo real
function atualizarValorPrevisto() {
    const idVeiculo = document.getElementById("veiculo").value;
    const dataRetirada = document.getElementById("data_retirada").value;
    const dataPrevista = document.getElementById("data_devolucao_prevista").value;
    const inputValor = document.getElementById("valor_total_previsto");

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

    fetch("/api/valor-previsto-reserva", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados)
    })
    .then(res => res.json())
    .then(json => {
        inputValor.value = json.valor_total_previsto ? parseFloat(json.valor_total_previsto).toFixed(2) : 0;
    })
    .catch(err => console.error("Erro ao calcular valor previsto:", err));
}

// Função para salvar a reserva e redirecionar
function salvarReserva() {
    const idVeiculo = document.getElementById("veiculo").value;
    const dataRetirada = document.getElementById("data_retirada").value;
    const dataPrevista = document.getElementById("data_devolucao_prevista").value;
    const valorPrevisto = document.getElementById("valor_total_previsto").value;

    const dados = {
        id_veiculo: parseInt(idVeiculo),
        data_retirada: dataRetirada,
        data_devolucao_prevista: dataPrevista,
        valor_previsto: parseFloat(valorPrevisto),
        opcionais: opcionaisTemp
    };

    fetch("/reserva/criar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados)
    })
    .then(res => res.json())
    .then(resp => {
        if (resp.sucesso) {
            // use o ID retornado do backend
            // e defina a URL correta dependendo do fluxo
            window.location.href = resp.redirect; // backend deve retornar a URL correta
        } else {
            alert("Erro ao criar reserva: " + (resp.erro || "Erro desconhecido"));
        }
    })
    .catch(err => console.error(err));


    return false; // previne submit padrão
}

// Inicialização unificada
window.addEventListener("load", function() {
    carregarOpcionais();
    document.getElementById("btn-adicionar-opcional").addEventListener("click", adicionarOpcionalTemp);
    document.getElementById("data_retirada").addEventListener("change", atualizarValorPrevisto);
    document.getElementById("data_devolucao_prevista").addEventListener("change", atualizarValorPrevisto);

    // Atualiza valor ao carregar a página
    atualizarValorPrevisto();

    // Adicionar submit do formulário
    document.getElementById("form-locacao").addEventListener("submit", function(event) {
        event.preventDefault();
        salvarReserva();
    });
});
