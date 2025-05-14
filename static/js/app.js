// Modal de confirmação de exclusão
document.addEventListener('DOMContentLoaded', function () {
  const modal = document.getElementById('modal-confirmacao');
  const btnConfirmar = document.getElementById('btn-confirmar-exclusao');
  const btnCancelar = document.getElementById('btn-cancelar-exclusao');
  const formExcluir = document.getElementById('form-exclusao');

  if (formExcluir) {
    formExcluir.addEventListener('submit', function (e) {
      e.preventDefault();
      modal.style.display = 'block';

      btnConfirmar.onclick = function () {
        modal.style.display = 'none';
        formExcluir.submit();
      };

      btnCancelar.onclick = function () {
        modal.style.display = 'none';
      };
    });
  }

  // Fechar modal clicando fora
  window.onclick = function (event) {
    if (event.target === modal) {
      modal.style.display = 'none';
    }
  }
});

// Atualização dinâmica de horários no formulário de agendamento
document.addEventListener('DOMContentLoaded', function () {
  const dataInput = document.getElementById('data');
  const horarioSelect = document.getElementById('horario');

  if (dataInput && horarioSelect) {
    dataInput.addEventListener('change', function () {
      const dataSelecionada = dataInput.value;
      fetch(`/agendar?data=${dataSelecionada}`)
        .then(response => response.text())
        .then(html => {
          // Extraímos apenas as opções de horário do HTML retornado
          const parser = new DOMParser();
          const doc = parser.parseFromString(html, 'text/html');
          const novasOpcoes = doc.getElementById('horario').innerHTML;

          horarioSelect.innerHTML = novasOpcoes;
        })
        .catch(error => console.error('Erro ao buscar horários:', error));
    });
  }
});
