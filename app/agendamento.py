from flask import (
    Flask, render_template, request, redirect, url_for,
    session, send_file, make_response, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
import os
import csv

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

@app.route("/horarios-disponiveis")
def horarios_disponiveis():
    sala = request.args.get("sala")
    data = request.args.get("data")
    duracao = 60
    if not sala or not data:
        return jsonify([])
    return jsonify(gerar_horarios_disponiveis(sala, data, duracao))

@app.route("/salas-disponiveis")
def salas_disponiveis_route():
    data = request.args.get("data")
    if not data:
        return jsonify([])
    return jsonify(salas_disponiveis_para_data(data, 60))

def verificar_disponibilidade(sala, data, inicio, fim):
    agendamentos = Agendamento.query.filter_by(sala=sala, data=data).all()
    for a in agendamentos:
        if not (fim <= a.inicio or inicio >= a.fim):
            return False
    return True

def gerar_horarios_disponiveis(sala, data, duracao):
    horarios = []
    agora = datetime.now()
    try:
        data_dt = datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        return []

    if data_dt.weekday() in [5, 6]:
        return []

    inicio = datetime.combine(data_dt.date(), datetime.strptime("08:00", "%H:%M").time())
    fim_limite = datetime.combine(data_dt.date(), datetime.strptime("18:00", "%H:%M").time())

    while inicio <= fim_limite:
        fim_agendamento = inicio + timedelta(minutes=duracao)
        if fim_agendamento <= fim_limite:
            if data_dt.date() > agora.date() or (data_dt.date() == agora.date() and inicio >= agora):
                if verificar_disponibilidade(sala, data, inicio, fim_agendamento):
                    if inicio.minute == 0:
                        horarios.append(inicio.strftime("%H:%M"))
        inicio += timedelta(minutes=30)
    return horarios

def salas_disponiveis_para_data(data, duracao):
    return [sala for sala in salas_disponiveis if gerar_horarios_disponiveis(sala, data, duracao)]

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
        sala = request.form["sala"]
        horario_inicio = request.form.get("horario_inicio")
        duracao = 60

        if not horario_inicio:
            return render_template("form.html", salas=salas_para_data, horarios_disponiveis=horarios_disponiveis, mensagem="Você precisa selecionar um horário.", aviso_sem_salas=aviso_sem_salas, hoje=hoje)

        try:
            inicio_dt = datetime.strptime(f"{data} {horario_inicio}", "%Y-%m-%d %H:%M")
            fim_dt = inicio_dt + timedelta(minutes=duracao)
        except ValueError:
            return render_template("form.html", salas=salas_para_data, horarios_disponiveis=horarios_disponiveis, mensagem="Data ou horário inválido.", aviso_sem_salas=aviso_sem_salas, hoje=hoje)

        if inicio_dt < datetime.now():
            return render_template("form.html", salas=salas_para_data, horarios_disponiveis=horarios_disponiveis, mensagem="Horário já passou.", aviso_sem_salas=aviso_sem_salas, hoje=hoje)

        if not verificar_disponibilidade(sala, data, inicio_dt, fim_dt):
            return render_template("form.html", salas=salas_para_data, horarios_disponiveis=horarios_disponiveis, mensagem="Horário indisponível para essa sala.", aviso_sem_salas=aviso_sem_salas, hoje=hoje)

        novo_agendamento = Agendamento(nome=nome, sala=sala, data=data, inicio=inicio_dt, fim=fim_dt)
        db.session.add(novo_agendamento)
        db.session.commit()

        data_formatada = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
        ticket = f"{novo_agendamento.id:06d}"

        session["mensagem_confirmacao"] = f"Sala {sala} agendada com sucesso para {nome}!"
        session["dados_confirmacao"] = {
            "nome": nome,
            "sala": sala,
            "data": data_formatada,
            "inicio": inicio_dt.strftime("%H:%M"),
            "fim": fim_dt.strftime("%H:%M"),
            "ticket": ticket
        }
        return redirect(url_for("confirmado"))

    response = make_response(render_template(
        "form.html",
        salas=salas_para_data,
        horarios_disponiveis=horarios_disponiveis,
        mensagem=mensagem,
        aviso_sem_salas=aviso_sem_salas,
        hoje=hoje
    ))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

@app.route("/confirmado")
def confirmado():
    mensagem = session.pop("mensagem_confirmacao", None)
    dados = session.pop("dados_confirmacao", None)
    if not dados:
        return redirect(url_for("agendar"))
    return render_template("confirmado.html", mensagem=mensagem, dados=dados)

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

@app.route("/cancelar-por-ticket/<int:id>", methods=["POST"])
def cancelar_por_ticket(id):
    ticket_digitado = request.form.get("ticket", "").strip()
    agendamento = Agendamento.query.get_or_404(id)
    ticket_esperado = f"{agendamento.id:06d}"

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
        a.ticket_formatado = f"{a.id:06d}"

    return render_template("agendamentos.html", agendamentos=agendamentos)

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

@app.route("/cancelar/<int:id>", methods=["POST"])
def cancelar_agendamento_admin(id):
    if session.get("admin_autorizado") != True:
        return redirect(url_for("login_admin"))
    agendamento = Agendamento.query.get_or_404(id)
    db.session.delete(agendamento)
    db.session.commit()
    return redirect(url_for("listar_agendamentos"))

@app.route("/painel-publico")
def painel_publico():
    agendamentos = Agendamento.query.order_by(Agendamento.data, Agendamento.inicio).all()
    for a in agendamentos:
        try:
            a.data_formatada = datetime.strptime(a.data, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            a.data_formatada = a.data
    return render_template("painel_publico.html", agendamentos=agendamentos)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
