import os

class Config:
    # Configuração do banco de dados SQLite
    DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')

    # Configurações do e-mail (removidas)
    # EMAIL_SENDER = "seu_email@gmail.com"
    # EMAIL_PASSWORD = "sua_senha"
    # EMAIL_RECEIVER pode ser definido no app.py ou utils.py conforme necessário

    # Limite de agendamentos por horário
    MAX_AGENDAMENTOS = 5

    # Horário de início e término para agendamentos
    HORARIO_INICIO = 9
    HORARIO_FIM = 18

    # Configurações para o Flask
    SECRET_KEY = os.urandom(24)  # Gere uma chave secreta diretamente
    SESSION_COOKIE_NAME = 'barbearia_session'
    FLASK_APP = 'app.py'

    # Outros parâmetros personalizados
    APP_NAME = "Barbearia System"

    # Caminho para salvar relatórios exportados