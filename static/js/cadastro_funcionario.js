document.addEventListener('DOMContentLoaded', () => {
  const formFuncionario = document.getElementById('formFuncionario');
  if (!formFuncionario) return;

  formFuncionario.addEventListener('submit', (event) => {
    const camposObrigatorios = [
      'nomeFuncionario',
      'cpfFuncionario',
      'rgFuncionario',
      'dataNascFuncionario',
      'sexoFuncionario',
      'estadoCivilFuncionario',
      'enderecoFuncionario',
      'emailFuncionario',
      'senhaFuncionario',
    ];

    for (const campo of camposObrigatorios) {
      const input = document.getElementById(campo);
      if (!input || !input.value.trim()) {
        alert('Por favor, preencha todos os campos obrigatórios');
        event.preventDefault();
        return;
      }
    }
  });
});
