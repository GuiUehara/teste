function validarFormCadastro(event) {
  const email = document.querySelector('input[name="email"]')?.value.trim();
  const senha = document.querySelector('input[name="senha"]')?.value.trim();

  if (!email || !senha) {
    alert('Por favor, preencha todos os campos.');
    event.preventDefault();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const formCadastro = document.getElementById('formCadastro');
  if (formCadastro) formCadastro.addEventListener('submit', validarFormCadastro);
});
