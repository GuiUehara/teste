/**
 * Busca categorias de veículos na API.
 * @returns {Promise<Array>} Uma promessa que resolve para uma lista de categorias.
 */
async function fetchCategorias() {
    const response = await fetch('/api/categorias');
    if (!response.ok) {
        throw new Error('Falha ao buscar categorias.');
    }
    return response.json();
}

/**
 * Busca veículos de uma categoria específica.
 * @param {number} idCategoria - O ID da categoria.
 * @returns {Promise<Array>} Uma promessa que resolve para uma lista de veículos.
 */
async function fetchVeiculosPorCategoria(idCategoria) {
    if (!idCategoria) return [];
    const response = await fetch(`/api/veiculos?id_categoria=${idCategoria}`);
    if (!response.ok) {
        throw new Error('Falha ao buscar veículos.');
    }
    return response.json();
}

/**
 * Busca os dados detalhados de um único veículo.
 * @param {number} idVeiculo - O ID do veículo.
 * @returns {Promise<Object>} Uma promessa que resolve para o objeto do veículo.
 */
async function fetchDetalhesVeiculo(idVeiculo) {
    if (!idVeiculo) return null;
    const response = await fetch(`/api/veiculo/${idVeiculo}`);
    if (!response.ok) {
        throw new Error('Falha ao buscar detalhes do veículo.');
    }
    return response.json();
}