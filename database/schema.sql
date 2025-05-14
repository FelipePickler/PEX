-- Criação da tabela de agendamentos
CREATE TABLE IF NOT EXISTS agendamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente TEXT NOT NULL,
    servico TEXT NOT NULL,
    data TEXT NOT NULL,
    horario TEXT NOT NULL,
    email TEXT NOT NULL
);
