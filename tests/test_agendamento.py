import pytest
import sqlite3
from app import app, get_db_connection


@pytest.fixture
def client():
    # Configura o ambiente para os testes
    app.config['TESTING'] = True
    app.config['DATABASE'] = 'test_database.db'

    with app.test_client() as client:
        with app.app_context():
            # Inicializa o banco de dados para os testes
            conn = sqlite3.connect('test_database.db')
            conn.execute('''CREATE TABLE IF NOT EXISTS agendamentos (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                cliente TEXT NOT NULL,
                                servico TEXT NOT NULL,
                                data TEXT NOT NULL,
                                horario TEXT NOT NULL,
                                email TEXT NOT NULL
                            )''')
            conn.close()
        yield client
        # Limpeza após os testes
        with app.app_context():
            conn = sqlite3.connect('test_database.db')
            conn.execute('DROP TABLE IF EXISTS agendamentos')
            conn.close()


def test_agendar(client):
    # Testa a criação de um agendamento
    response = client.post('/agendar', data={
        'nome': 'João',
        'data': '2025-05-15',
        'horario': '10:00',
        'servico': 'Corte',
        'email': 'joao@example.com'
    })

    assert response.status_code == 302  # Redireciona para a página inicial
    conn = get_db_connection()
    agendamento = conn.execute('SELECT * FROM agendamentos WHERE nome = "João"').fetchone()
    conn.close()

    assert agendamento is not None
    assert agendamento['nome'] == 'João'


def test_editar(client):
    # Testa a edição de um agendamento
    response = client.post('/agendar', data={
        'nome': 'Maria',
        'data': '2025-05-16',
        'horario': '14:00',
        'servico': 'Barba',
        'email': 'maria@example.com'
    })

    conn = get_db_connection()
    agendamento = conn.execute('SELECT * FROM agendamentos WHERE nome = "Maria"').fetchone()
    conn.close()

    agendamento_id = agendamento['id']

    # Edita o agendamento
    response = client.post(f'/editar/{agendamento_id}', data={
        'nome': 'Maria Silva',
        'data': '2025-05-17',
        'horario': '15:00',
        'servico': 'Corte + Barba',
        'email': 'maria.silva@example.com'
    })

    conn = get_db_connection()
    agendamento = conn.execute('SELECT * FROM agendamentos WHERE id = ?', (agendamento_id,)).fetchone()
    conn.close()

    assert agendamento['nome'] == 'Maria Silva'
    assert agendamento['data'] == '2025-05-17'
    assert agendamento['horario'] == '15:00'


def test_excluir(client):
    # Testa a exclusão de um agendamento
    response = client.post('/agendar', data={
        'nome': 'Carlos',
        'data': '2025-05-18',
        'horario': '16:00',
        'servico': 'Corte',
        'email': 'carlos@example.com'
    })

    conn = get_db_connection()
    agendamento = conn.execute('SELECT * FROM agendamentos WHERE nome = "Carlos"').fetchone()
    agendamento_id = agendamento['id']
    conn.close()

    # Exclui o agendamento
    response = client.post(f'/excluir/{agendamento_id}')

    conn = get_db_connection()
    agendamento = conn.execute('SELECT * FROM agendamentos WHERE id = ?', (agendamento_id,)).fetchone()
    conn.close()

    assert agendamento is None
