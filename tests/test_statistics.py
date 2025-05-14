import pytest
from app import get_agendamento_statistics


def test_get_agendamento_statistics():
    # Testa a contagem de agendamentos por semana
    stats = get_agendamento_statistics('semana')
    assert isinstance(stats, dict)
    assert '2025-05-15' in stats  # Verifica se existe a data esperada

    # Testa a contagem de agendamentos por mês
    stats = get_agendamento_statistics('mes')
    assert isinstance(stats, dict)
    assert '2025-05' in stats  # Verifica se existe o mês esperado
