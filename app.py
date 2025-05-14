from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import sqlite3
import os
import datetime
from io import StringIO
import csv
from config import Config
# from utils import send_confirmation_email  <- Remoção da importação da funcionalidade de e-mail

app = Flask(__name__)
app.config.from_object(Config)
DATABASE = app.config['DATABASE']
MAX_AGENDAMENTOS = app.config['MAX_AGENDAMENTOS']
HORARIO_INICIO = app.config['HORARIO_INICIO']
HORARIO_FIM = app.config['HORARIO_FIM']
HORARIOS_DISPONIVEIS = [f"{h:02d}:{m:02d}" for h in range(HORARIO_INICIO, HORARIO_FIM + 1) for m in [0, 30]]

def get_db_connection():
    """Estabelece e retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome (como um dicionário)
    return conn

def init_db():
    """Inicializa o banco de dados se ele não existir, criando a tabela de agendamentos."""
    if not os.path.exists(DATABASE):
        conn = get_db_connection()
        with conn:
            conn.execute('''CREATE TABLE agendamentos (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                nome TEXT NOT NULL,
                                data TEXT NOT NULL,
                                horario TEXT NOT NULL,
                                servico TEXT NOT NULL
                                -- email TEXT NOT NULL <- Remoção da coluna de e-mail
                            )''')
        print("Banco de dados inicializado.")

@app.route('/')
def index():
    """Rota para a página inicial, exibindo o calendário de agendamentos."""
    return render_template('index.html')

@app.route('/agendar', methods=['GET', 'POST'])
def agendar():
    """Rota para a página de agendamento. Permite exibir o formulário (GET) e processar o agendamento (POST)."""
    conn = get_db_connection()
    try:
        if request.method == 'POST':
            nome = request.form['nome']
            data = request.form['data']
            horario = request.form['horario']
            servico = request.form['servico']
            # email = request.form['email'] <- Remoção da coleta de e-mail

            # Valida o formato do horário
            if horario not in HORARIOS_DISPONIVEIS:
                flash("Horário inválido.", 'error')
                return render_template('agendar.html', horarios=HORARIOS_DISPONIVEIS)

            # Verifica se o limite de agendamentos para este horário foi atingido
            existing_agendamentos = conn.execute('''SELECT COUNT(*) FROM agendamentos WHERE data = ? AND horario = ?''', (data, horario)).fetchone()[0]

            if existing_agendamentos >= MAX_AGENDAMENTOS:
                flash("Limite de agendamentos atingido para este horário. Tente outro horário.", 'warning')
                return render_template('agendar.html', horarios=HORARIOS_DISPONIVEIS)

            try:
                with conn:
                    conn.execute('''INSERT INTO agendamentos (nome, data, horario, servico) VALUES (?, ?, ?, ?)''',
                                 (nome, data, horario, servico)) # <- Remoção do e-mail na inserção
                flash("Agendamento realizado com sucesso!", 'success')
                # send_confirmation_email(nome, data, horario, servico, email, app.config) <- Remoção do envio de e-mail
                return redirect(url_for('index'))
            except sqlite3.Error as e:
                flash(f"Erro ao agendar: {e}", 'error')

        # Se for uma requisição GET, exibe o formulário com os horários disponíveis para a data selecionada
        data_selecionada = request.args.get('data', datetime.date.today().isoformat())
        # Busca os horários já ocupados para a data selecionada
        ocupados = [row['horario'] for row in conn.execute('''SELECT horario FROM agendamentos WHERE data = ?''', (data_selecionada,)).fetchall()]
        # Filtra os horários disponíveis que não estão ocupados
        horarios_disponiveis_data = [h for h in HORARIOS_DISPONIVEIS if h not in ocupados]
        return render_template('agendar.html', horarios=horarios_disponiveis_data, data_selecionada=data_selecionada)

    finally:
        conn.close()

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Rota para o painel administrativo, permitindo visualizar, filtrar, editar e excluir agendamentos."""
    conn = get_db_connection()
    agendamentos = []
    filtro_data = request.form.get('data', '') if request.method == 'POST' else request.args.get('filtro_data', '')
    filtro_servico = request.form.get('servico', '') if request.method == 'POST' else request.args.get('filtro_servico', '')
    filtro_nome = request.form.get('nome', '') if request.method == 'POST' else request.args.get('filtro_nome', '')

    # Construção dinâmica da query SQL para aplicar os filtros
    query = 'SELECT id, nome, data, horario, servico FROM agendamentos WHERE 1=1' # Remoção do e-mail da seleção
    params = []

    if filtro_data:
        query += ' AND data = ?'
        params.append(filtro_data)
    if filtro_servico:
        query += ' AND servico = ?'
        params.append(filtro_servico)
    if filtro_nome:
        query += ' AND nome LIKE ?'
        params.append(f'%{filtro_nome}%')

    agendamentos = conn.execute(query, tuple(params)).fetchall()
    servicos = ['Corte', 'Barba', 'Corte + Barba']
    conn.close()
    return render_template('admin.html', agendamentos=agendamentos, servicos=servicos,
                           filtro_data=filtro_data, filtro_servico=filtro_servico, filtro_nome=filtro_nome)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    """Rota para editar um agendamento específico, identificado pelo ID."""
    conn = get_db_connection()
    agendamento = conn.execute('SELECT id, nome, data, horario, servico FROM agendamentos WHERE id = ?', (id,)).fetchone() # Remoção do e-mail da seleção

    if agendamento is None:
        flash("Agendamento não encontrado.", 'error')
        conn.close()
        return redirect(url_for('admin'))

    if request.method == 'POST':
        nome = request.form['nome']
        data = request.form['data']
        horario = request.form['horario']
        servico = request.form['servico']
        # email = request.form['email'] <- Remoção da coleta de e-mail

        # Valida o formato do horário
        if horario not in HORARIOS_DISPONIVEIS:
            flash("Horário inválido.", 'error')
            conn.close()
            return render_template('editar.html', agendamento=agendamento, horarios=HORARIOS_DISPONIVEIS)

        # Verifica se o limite de agendamentos para este horário foi atingido (excluindo o agendamento atual)
        existing_agendamentos = conn.execute('''SELECT COUNT(*) FROM agendamentos WHERE data = ? AND horario = ? AND id != ?''', (data, horario, id)).fetchone()[0]
        if existing_agendamentos >= MAX_AGENDAMENTOS:
            flash("Limite de agendamentos atingido para este horário.", 'warning')
            conn.close()
            return render_template('editar.html', agendamento=agendamento, horarios=HORARIOS_DISPONIVEIS)

        try:
            with conn:
                conn.execute('''UPDATE agendamentos
                                   SET nome = ?, data = ?, horario = ?, servico = ?
                                   WHERE id = ?''', (nome, data, horario, servico, id)) # Remoção do e-mail da atualização
            flash("Agendamento atualizado com sucesso!", 'success')
            return redirect(url_for('admin'))
        except sqlite3.Error as e:
            flash(f"Erro ao editar: {e}", 'error')
        finally:
            conn.close()

    return render_template('editar.html', agendamento=agendamento, horarios=HORARIOS_DISPONIVEIS)

@app.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    """Rota para excluir um agendamento específico, identificado pelo ID."""
    conn = get_db_connection()
    try:
        with conn:
            conn.execute('DELETE FROM agendamentos WHERE id = ?', (id,))
        flash("Agendamento excluído com sucesso!", 'success')
    except sqlite3.Error as e:
        flash(f"Erro ao excluir: {e}", 'error')
    finally:
        conn.close()
    return redirect(url_for('admin'))

@app.route('/exportar', methods=['GET'])
def exportar():
    """Rota para exportar todos os agendamentos para um arquivo CSV."""
    conn = get_db_connection()
    agendamentos = conn.execute('SELECT id, nome, data, horario, servico FROM agendamentos').fetchall() # Remoção do e-mail da seleção
    conn.close()

    output = StringIO()
    csv_writer = csv.writer(output)

    # Escreve o cabeçalho do CSV
    if agendamentos:
        csv_writer.writerow(agendamentos[0].keys())

    # Escreve os dados dos agendamentos
    for agendamento in agendamentos:
        csv_writer.writerow([agendamento['nome'], agendamento['servico'], agendamento['data'], agendamento['horario']]) # Remoção do e-mail da linha

    output.seek(0)
    return send_file(output, as_attachment=True, download_name="agendamentos.csv", mimetype="text/csv")

@app.route('/estatisticas', methods=['GET'])
def estatisticas():
    """Rota para exibir estatísticas sobre os agendamentos."""
    conn = get_db_connection()
    hoje = datetime.date.today()
    uma_semana_atras = hoje - datetime.timedelta(days=7)
    um_mes_atras = hoje - datetime.timedelta(days=30)

    periodo = request.args.get('periodo', 'semana')

    # Estatísticas de agendamentos por dia
    if periodo == 'semana':
        agendamentos_data_rows = conn.execute('''SELECT strftime('%Y-%m-%d', data) AS data, COUNT(*) AS count
                                                   FROM agendamentos
                                                   WHERE data >= ? AND data <= ?
                                                   GROUP BY data
                                                   ORDER BY data''', (uma_semana_atras.strftime('%Y-%m-%d'), hoje.strftime('%Y-%m-%d'))).fetchall()
    elif periodo == 'mes':
        agendamentos_data_rows = conn.execute('''SELECT strftime('%Y-%m-%d', data) AS data, COUNT(*) AS count
                                                   FROM agendamentos
                                                   WHERE data >= ? AND data <= ?
                                                   GROUP BY strftime('%Y-%m-%d', data)
                                                   ORDER BY data''', (um_mes_atras.strftime('%Y-%m-%d'), hoje.strftime('%Y-%m-%d'))).fetchall()
    else:
        agendamentos_data_rows = conn.execute('''SELECT strftime('%Y-%m-%d', data) AS data, COUNT(*) AS count
                                                   FROM agendamentos
                                                   GROUP BY data
                                                   ORDER BY data''').fetchall()

    agendamentos_data = [dict(row) for row in agendamentos_data_rows]

    # Estatísticas de agendamentos por serviço
    servicos_stats = conn.execute('''SELECT servico, COUNT(*) AS count FROM agendamentos GROUP BY servico''').fetchall()
    servicos_labels = [stat['servico'] for stat in servicos_stats]
    servicos_values = [stat['count'] for stat in servicos_stats]

    # --- Novas Estatísticas ---
    # Horários de maior movimento
    horarios_movimentados_rows = conn.execute('''SELECT horario, COUNT(*) AS count
                                                  FROM agendamentos
                                                  GROUP BY horario
                                                  ORDER BY count DESC
                                                  LIMIT 5''').fetchall()
    horarios_movimentados = [{'horario': row['horario'], 'count': row['count']} for row in horarios_movimentados_rows]

    # Combinações de serviços mais populares (exige uma análise mais complexa se múltiplos serviços pudessem ser agendados juntos)
    # Para simplificar, vamos apenas listar a frequência de cada serviço individualmente (já feito acima)

    # Taxa de cancelamento (requer uma coluna para indicar se um agendamento foi cancelado)
    # Sem essa coluna, não podemos calcular a taxa de cancelamento diretamente.

    conn.close()
    return render_template('estatisticas.html', agendamentos_por_dia=agendamentos_data,
                           agendamentos_por_servico={'labels': servicos_labels, 'values': servicos_values},
                           horarios_movimentados=horarios_movimentados, periodo=periodo)

@app.route('/get_agendamentos')
def get_agendamentos():
    """Rota para fornecer dados dos agendamentos em formato JSON para o calendário."""
    conn = get_db_connection()
    agendamentos = conn.execute('SELECT id, nome AS title, data AS start FROM agendamentos').fetchall()
    conn.close()
    return jsonify([dict(row) for row in agendamentos])

@app.route('/horarios_disponiveis/<data>')
def horarios_disponiveis(data):
    """Rota para obter os horários disponíveis para uma data específica em formato JSON."""
    conn = get_db_connection()
    ocupados = [row['horario'] for row in conn.execute('''SELECT horario FROM agendamentos WHERE data = ?''', (data,)).fetchall()]
    disponiveis = [h for h in HORARIOS_DISPONIVEIS if h not in ocupados]
    conn.close()
    return jsonify(disponiveis)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)