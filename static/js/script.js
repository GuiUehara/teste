const clientes = [];
const veiculos = [];

// Cadastro do cliente via formulário específico (formCliente)
function cadastrarCliente(event) {
  event.preventDefault();
  const nome = document.getElementById('nomeCliente').value.trim();
  const cpf = document.getElementById('cpfCliente')?.value.trim() || '';
  const dataNasc = document.getElementById('dataNascCliente')?.value || '';
  const telefone = document.getElementById('telefoneCliente').value.trim();
  const email = document.getElementById('emailCliente').value.trim();
  const endereco = document.getElementById('enderecoCliente')?.value.trim() || '';
  const cnh = document.getElementById('cnhCliente')?.value.trim() || '';
  const categoriaCNH = document.getElementById('categoriaCNHCliente')?.value.trim() || '';
  const validadeCNH = document.getElementById('validadeCNHCliente')?.value || '';
  const tempoHabilitacao = document.getElementById('tempoHabilitacaoCliente')?.value || '';
  const formaPagamento = document.getElementById('formaPagamentoCliente')?.value.trim() || '';

  if (!nome || !cpf || !dataNasc || !telefone || !email || !endereco || !cnh || !categoriaCNH || !validadeCNH || !tempoHabilitacao) {
    alert('Por favor, preencha todos os campos obrigatórios do cliente!');
    return;
  }

  clientes.push({
    nome, cpf, dataNasc, telefone, email, endereco,
    cnh, categoriaCNH, validadeCNH, tempoHabilitacao, formaPagamento
  });
  atualizarListaClientes();
  document.getElementById('formCliente').reset();
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

// Cadastro do veículo via formulário específico (formVeiculo)
function cadastrarVeiculo(event) {
  event.preventDefault();
  const modelo = document.getElementById('modeloVeiculo').value.trim();
  const placa = document.getElementById('placaVeiculo').value.trim().toUpperCase();
  const ano = document.getElementById('anoVeiculo').value.trim();

  if (!modelo || !placa || !ano) {
    alert('Por favor, preencha todos os campos.');
    return;
  }
  if (isNaN(ano) || ano < 1900 || ano > new Date().getFullYear() + 1) {
    alert('Ano inválido!');
    return;
  }

  veiculos.push({ modelo, placa, ano });
  atualizarListaVeiculos();
  document.getElementById('formVeiculo').reset();
}

function atualizarListaVeiculos() {
  const lista = document.getElementById('listaVeiculos');
  if (!lista) return;
  lista.innerHTML = '';
  veiculos.forEach(v => {
    const li = document.createElement('li');
    li.textContent = `${v.modelo} - Placa: ${v.placa} - Ano: ${v.ano}`;
    lista.appendChild(li);
  });
}

// Validação simples do formulário genérico (formCadastro)
function validarFormCadastro(event) {
  const nome = document.querySelector('input[name="nome"]')?.value.trim();
  const email = document.querySelector('input[name="email"]')?.value.trim();
  const senha = document.querySelector('input[name="senha"]')?.value.trim();

  if (!nome || !email || !senha) {
    alert('Por favor, preencha todos os campos do cadastro genérico.');
    event.preventDefault();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const formCliente = document.getElementById('formCliente');
  if (formCliente) formCliente.addEventListener('submit', cadastrarCliente);

  const formVeiculo = document.getElementById('formVeiculo');
  if (formVeiculo) formVeiculo.addEventListener('submit', cadastrarVeiculo);

  const formCadastro = document.getElementById('formCadastro');
  if (formCadastro) formCadastro.addEventListener('submit', validarFormCadastro);
});
