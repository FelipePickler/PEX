import sqlite3

def init_db():
    # Conecta ao banco de dados
    conn = sqlite3.connect('database.db')
    
    # Abre e executa o schema.sql
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    
    print("Banco de dados inicializado com sucesso!")

# Chama a função para inicializar o banco de dados
if __name__ == '__main__':
    init_db()
