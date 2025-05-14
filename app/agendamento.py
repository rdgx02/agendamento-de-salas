from flask import (
    Flask, render_template, request, redirect, url_for,
    session, send_file, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
import os
import csv
import requests
import re
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev123")

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_path = os.path.join(basedir, "data", "agendamentos.db")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

salas_disponiveis = ["205", "214", "305"]

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sala = db.Column(db.String(10), nullable=False)
    data = db.Column(db.String(10), nullable=False)
    inicio = db.Column(db.DateTime, nullable=False)
    fim = db.Column(db.DateTime, nullable=False)
    ticket = db.Column(db.String(12), unique=True, nullable=False, default=lambda: uuid.uuid4().hex[:8])

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

def enviar_para_n8n(dados):
    try:
        print("\U0001F4E4 Enviando os seguintes dados para o n8n:")
        print(dados)

        headers = {
            "apikey": "326E97B23199-47C5-9AB4-69B2B9B9C71A"
        }
        resposta = requests.post(
            "https://n8n.ladetec.iq.ufrj.br/webhook/confirmar-agendamento",
            json=dados,
            headers=headers
        )

        print("\U0001F501 Status Code:", resposta.status_code)
        print("\U0001F501 Resposta:", resposta.text)

        if resposta.status_code != 200:
            print("❌ Erro ao enviar para o n8n:", resposta.status_code, resposta.text)
        else:
            print("✅ Confirmação enviada com sucesso ao n8n.")
    except Exception as e:
        print("❌ Erro inesperado ao enviar para n8n:", e)

def verificar_disponibilidade(sala, data_str, inicio_dt, fim_dt):
    conflitos = Agendamento.query.filter_by(sala=sala, data=data_str).filter(
        Agendamento.inicio < fim_dt,
        Agendamento.fim > inicio_dt
    ).count()
    return conflitos == 0

def gerar_horarios_disponiveis(sala, data, duracao):
    inicio_dia = datetime.strptime(f"{data} 08:00", "%Y-%m-%d %H:%M")
    fim_dia = datetime.strptime(f"{data} 18:00", "%Y-%m-%d %H:%M")
    agora = datetime.now()
    horarios = []

    while inicio_dia + timedelta(minutes=duracao) <= fim_dia:
        fim_horario = inicio_dia + timedelta(minutes=duracao)
        if inicio_dia >= agora and verificar_disponibilidade(sala, data, inicio_dia, fim_horario):
            horarios.append(inicio_dia.strftime("%H:%M"))
        inicio_dia += timedelta(minutes=60)

    return horarios

def salas_disponiveis_para_data(data, duracao):
    disponiveis = []
    for sala in salas_disponiveis:
        horarios = gerar_horarios_disponiveis(sala, data, duracao)
        if horarios:
            disponiveis.append(sala)
    return disponiveis

@app.route("/", methods=["GET", "POST"])
def agendar():
    session.clear()
    mensagem = ""
    data = request.form.get("data") if request.method == "POST" else request.args.get("data")
    aviso_sem_salas = False
    salas_para_data = []
    horarios_disponiveis = []
    hoje = date.today().strftime("%Y-%m-%d")

    if data:
        try:
            data_dt = datetime.strptime(data, "%Y-%m-%d").date()
        except ValueError:
            return render_template("form.html", salas=[], horarios_disponiveis=[], mensagem="Data inválida.", aviso_sem_salas=True, hoje=hoje)

        if data_dt < date.today():
            return render_template("form.html", salas=[], horarios_disponiveis=[], mensagem="Data já passou.", aviso_sem_salas=True, hoje=hoje)
        if data_dt.weekday() in [5, 6]:
            return render_template("form.html", salas=[], horarios_disponiveis=[], mensagem="Não é possível agendar aos sábados ou domingos.", aviso_sem_salas=True, hoje=hoje)

        salas_para_data = salas_disponiveis_para_data(data, 60)
        if salas_para_data:
            horarios_disponiveis = gerar_horarios_disponiveis(salas_para_data[0], data, 60)
        else:
            aviso_sem_salas = True

    if request.method == "POST":
        nome = request.form["nome"]
        telefone = request.form.get("telefone", "").strip()

        regex_telefone = r"^\+55\s\d{2}\s\d{5}-\d{4}$"
        if not re.match(regex_telefone, telefone):
            return render_template("form.html", salas=salas_para_data, horarios_disponiveis=horarios_disponiveis, mensagem="Telefone inválido. Use o formato +55 21 91234-5678", aviso_sem_salas=aviso_sem_salas, hoje=hoje)

        sala = request.form.get("sala")
        if not sala:
            return render_template("form.html", salas=salas_para_data, horarios_disponiveis=horarios_disponiveis, mensagem="Você precisa selecionar uma sala válida.", aviso_sem_salas=aviso_sem_salas, hoje=hoje)

        horario_inicio = request.form.get("horario_inicio")
        repeticao = request.form.get("repeticao", "nenhum")
        if repeticao == "nenhum":
            duracao_repeticao = 1
        else:
            duracao_repeticao = int(request.form.get("duracao_repeticao") or 1)

        if not horario_inicio:
            return render_template("form.html", salas=salas_para_data, horarios_disponiveis=horarios_disponiveis, mensagem="Você precisa selecionar um horário.", aviso_sem_salas=aviso_sem_salas, hoje=hoje)

        try:
            inicio_base = datetime.strptime(f"{data} {horario_inicio}", "%Y-%m-%d %H:%M")
        except ValueError:
            return render_template("form.html", salas=salas_para_data, horarios_disponiveis=horarios_disponiveis, mensagem="Data ou horário inválido.", aviso_sem_salas=aviso_sem_salas, hoje=hoje)

        if inicio_base < datetime.now():
            return render_template("form.html", salas=salas_para_data, horarios_disponiveis=horarios_disponiveis, mensagem="Horário já passou.", aviso_sem_salas=aviso_sem_salas, hoje=hoje)

        ocorrencias = []
        for i in range(duracao_repeticao):
            if repeticao == "semanal":
                inicio_dt = inicio_base + timedelta(weeks=i)
            elif repeticao == "mensal":
                inicio_dt = inicio_base + timedelta(days=30 * i)
            else:
                inicio_dt = inicio_base

            fim_dt = inicio_dt + timedelta(minutes=60)
            data_str = inicio_dt.strftime("%Y-%m-%d")

            if inicio_dt.weekday() in [5, 6]:
                continue
            if not verificar_disponibilidade(sala, data_str, inicio_dt, fim_dt):
                continue

            ocorrencias.append(Agendamento(nome=nome, sala=sala, data=data_str, inicio=inicio_dt, fim=fim_dt))

        if not ocorrencias:
            return render_template("form.html", salas=salas_para_data, horarios_disponiveis=horarios_disponiveis, mensagem="Nenhum dos horários está disponível nas datas futuras.", aviso_sem_salas=aviso_sem_salas, hoje=hoje)

        for ag in ocorrencias:
            db.session.add(ag)
        db.session.commit()

        ultima = ocorrencias[0]
        ticket = ultima.ticket
        data_formatada = datetime.strptime(ultima.data, "%Y-%m-%d").strftime("%d/%m/%Y")

        session["mensagem_confirmacao"] = f"Sala {sala} agendada com sucesso para {nome}!"
        session["dados_confirmacao"] = {
            "nome": nome,
            "sala": sala,
            "data": data_formatada,
            "inicio": ultima.inicio.strftime("%H:%M"),
            "fim": ultima.fim.strftime("%H:%M"),
            "ticket": ticket,
            "telefone": telefone
        }

        enviar_para_n8n(session["dados_confirmacao"])
        return redirect(url_for("confirmado"))

    return render_template("form.html", salas=salas_para_data, horarios_disponiveis=horarios_disponiveis, mensagem=mensagem, aviso_sem_salas=aviso_sem_salas, hoje=hoje)

@app.route("/salas-disponiveis")
def salas_disponiveis_api():
    data = request.args.get("data")
    if not data:
        return jsonify([])

    try:
        datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        return jsonify([])

    salas = salas_disponiveis_para_data(data, 60)
    return jsonify(salas)

@app.route("/horarios-disponiveis")
def horarios_disponiveis_api():
    sala = request.args.get("sala")
    data = request.args.get("data")
    duracao = int(request.args.get("duracao", 60))
    if not sala or not data:
        return jsonify([])
    horarios = gerar_horarios_disponiveis(sala, data, duracao)
    return jsonify(horarios)

@app.route("/confirmado")
def confirmado():
    mensagem = session.pop("mensagem_confirmacao", None)
    dados = session.pop("dados_confirmacao", None)

    if not dados or "ticket" not in dados:
        return redirect(url_for("agendar"))

    agendamento = Agendamento.query.filter_by(ticket=dados["ticket"]).first()
    return render_template("confirmado.html", mensagem=mensagem, dados=dados, agendamento=agendamento)

@app.route("/meus-agendamentos")
def meus_agendamentos():
    nome = request.args.get("nome", "").strip()
    if nome:
        agendamentos = Agendamento.query.filter(
            Agendamento.nome.ilike(f"%{nome}%")
        ).order_by(Agendamento.data, Agendamento.inicio).all()
    else:
        agendamentos = Agendamento.query.order_by(Agendamento.data, Agendamento.inicio).all()

    for a in agendamentos:
        try:
            a.data_formatada = datetime.strptime(a.data, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            a.data_formatada = a.data

    return render_template("meus_agendamentos.html", agendamentos=agendamentos)

@app.route("/cancelar-por-ticket/<int:id>", methods=["POST"], endpoint="cancelar_por_ticket")
def cancelar_por_ticket(id):
    ticket_digitado = request.form.get("ticket", "").strip()
    agendamento = Agendamento.query.get_or_404(id)
    ticket_esperado = agendamento.ticket

    if ticket_digitado == ticket_esperado:
        db.session.delete(agendamento)
        db.session.commit()
        return render_template("cancelado.html")

    nome = agendamento.nome
    agendamentos = Agendamento.query.filter(
        Agendamento.nome.ilike(f"%{nome}%")
    ).order_by(Agendamento.data, Agendamento.inicio).all()

    for a in agendamentos:
        try:
            a.data_formatada = datetime.strptime(a.data, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            a.data_formatada = a.data
        if a.id == id:
            a.erro_ticket = "❌ Ticket inválido. Verifique o número e tente novamente."

    return render_template("meus_agendamentos.html", agendamentos=agendamentos)

@app.route("/admin", methods=["GET", "POST"])
def login_admin():
    if request.method == "POST":
        senha = request.form.get("senha")
        if senha == "minhasupersecreta":
            session["admin_autorizado"] = True
            return redirect(url_for("listar_agendamentos"))
        else:
            return "Senha incorreta"
    return render_template("login_admin.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_admin"))

@app.route("/agendamentos")
def listar_agendamentos():
    if session.get("admin_autorizado") != True:
        return redirect(url_for("login_admin"))

    agendamentos = Agendamento.query.order_by(Agendamento.data, Agendamento.inicio).all()
    for a in agendamentos:
        try:
            a.data_formatada = datetime.strptime(a.data, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            a.data_formatada = a.data
        a.ticket_formatado = a.ticket

    return render_template("agendamentos.html", agendamentos=agendamentos)

@app.route("/cancelar/<int:id>", methods=["POST"])
def cancelar_agendamento_admin(id):
    if session.get("admin_autorizado") != True:
        return redirect(url_for("login_admin"))
    agendamento = Agendamento.query.get_or_404(id)
    db.session.delete(agendamento)
    db.session.commit()
    return redirect(url_for("listar_agendamentos"))

@app.route("/exportar")
def exportar():
    agendamentos = Agendamento.query.all()
    csv_path = os.path.join(basedir, "data", "agendamentos_export.csv")
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Nome", "Sala", "Data", "Início", "Fim"])
        for a in agendamentos:
            writer.writerow([a.id, a.nome, a.sala, a.data, a.inicio.strftime("%H:%M"), a.fim.strftime("%H:%M")])
    return send_file(csv_path, as_attachment=True)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5050)