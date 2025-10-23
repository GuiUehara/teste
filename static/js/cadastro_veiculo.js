const veiculos = [];

function atualizarValorPorFracao() {
  const tanque = parseFloat(document.getElementById('tanque').value) || 0;
  const fracao = parseFloat(document.getElementById('tanqueFracao').value) || 1;
  const valorCombustivel = 6.50;
  const valorFinal = tanque * fracao * valorCombustivel + 8;
  document.getElementById('valorPorFracao').value = valorFinal.toFixed(2);
}

document.getElementById('tanque').addEventListener('input', atualizarValorPorFracao);
document.getElementById('tanqueFracao').addEventListener('change', atualizarValorPorFracao);


document.getElementById('tanque').addEventListener('input', atualizarValorPorFracao);
document.getElementById('tanqueFracao').addEventListener('change', atualizarValorPorFracao);


document.getElementById('tanque').addEventListener('input', atualizarValorPorFracao);
document.getElementById('tanqueFracao').addEventListener('change', atualizarValorPorFracao);

function cadastrarVeiculo(event) {
  event.preventDefault();
  const placa = document.getElementById('placaVeiculo').value.trim().toUpperCase();
  const renavam = document.getElementById('renavamVeiculo').value.trim();
  const chassi = document.getElementById('chassiVeiculo').value.trim().toUpperCase();
  const marca = document.getElementById('marcaVeiculo').value.trim();
  const modelo = document.getElementById('modeloVeiculo').value.trim();
  const ano = document.getElementById('anoVeiculo').value.trim();
  const cor = document.getElementById('corVeiculo').value.trim();
  const transmissao = document.getElementById('transmissaoVeiculo').value;
  const motor = document.getElementById('motorVeiculo').value.trim();
  const dataCompra = document.getElementById('dataCompra').value;
  const valorCompra = parseFloat(document.getElementById('valorCompra').value);
  const odometro = parseInt(document.getElementById('odometro').value);
  const vencimentoLicenciamento = document.getElementById('vencimentoLicenciamento').value;
  const companhiaSeguro = document.getElementById('companhiaSeguro').value.trim();
  const vencimentoSeguro = document.getElementById('vencimentoSeguro').value;
  const tanqueFracao = document.getElementById('tanqueFracao').value;
  const valorPorFracao = parseFloat(document.getElementById('valorPorFracao').value);
  const tiposCombustivel =document.getElementById('tiposCombustivel').value;


  if (!placa || !renavam || !chassi || !marca || !modelo || !ano || !cor || !transmissao) {
    alert('Por favor, preencha todos os campos obrigatórios.');
    return;
  }

  veiculos.push({
    placa, renavam, chassi, marca, modelo, ano, cor, transmissao, motor, dataCompra, valorCompra, odometro,
    vencimentoLicenciamento, companhiaSeguro, vencimentoSeguro, tanqueFracao, valorPorFracao, tiposCombustivel
  });

  atualizarListaVeiculos();
  document.getElementById('formVeiculo').reset();
  document.getElementById('valorPorFracao').value = '';
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
  if (formVeiculo) formVeiculo.addEventListener('submit', cadastrarVeiculo);
  document.getElementById('tanque').addEventListener('input', atualizarValorPorFracao);
  document.getElementById('tanqueFracao').addEventListener('change', atualizarValorPorFracao);
});
