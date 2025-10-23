const clientes = [];

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

document.addEventListener('DOMContentLoaded', () => {
  const formCliente = document.getElementById('formCliente');
  if (formCliente) formCliente.addEventListener('submit', cadastrarCliente);
});
