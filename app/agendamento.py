from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
import os
import csv

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev123")

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '../data/agendamentos.db')
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

def verificar_disponibilidade(sala, data, inicio, fim):
    agendamentos = Agendamento.query.filter_by(sala=sala, data=data).all()
    for agendamento in agendamentos:
        if not (fim <= agendamento.inicio or inicio >= agendamento.fim):
            return False
    return True

def gerar_horarios_disponiveis(sala, data, duracao):
    horarios = []
    agora = datetime.now()
    data_dt = datetime.strptime(data, "%Y-%m-%d")
    if data_dt.weekday() in [5, 6]:
        return []

    inicio = datetime.combine(data_dt.date(), datetime.strptime("08:00", "%H:%M").time())
    fim_limite = datetime.combine(data_dt.date(), datetime.strptime("18:00", "%H:%M").time())
    fim_maximo = fim_limite + timedelta(minutes=120)

    if agora.minute < 30:
        proximo_slot = agora.replace(minute=30, second=0, microsecond=0)
    else:
        proximo_slot = (agora + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

    while inicio <= fim_limite:
        fim_agendamento = inicio + timedelta(minutes=duracao)
        if fim_agendamento <= fim_maximo:
            if data_dt.date() > agora.date() or (data_dt.date() == agora.date() and inicio >= proximo_slot):
                if verificar_disponibilidade(sala, data, inicio, fim_agendamento):
                    horarios.append(inicio.strftime("%H:%M"))
        inicio += timedelta(minutes=30)
    return horarios

def salas_disponiveis_para_data(data, duracao):
    return [sala for sala in salas_disponiveis if gerar_horarios_disponiveis(sala, data, duracao)]

@app.template_filter('datetimeformat')
def formatar_data(data_str):
    try:
        return datetime.strptime(data_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return data_str

@app.route("/horarios-disponiveis")
def horarios_disponiveis():
    sala = request.args.get("sala")
    data = request.args.get("data")
    duracao = int(request.args.get("duracao", 30))
    if not sala or not data:
        return jsonify([])
    return jsonify(gerar_horarios_disponiveis(sala, data, duracao))

@app.route("/salas-disponiveis")
def salas_disponiveis_route():
    data = request.args.get("data")
    if not data:
        return jsonify([])
    return jsonify(salas_disponiveis_para_data(data, 30))

@app.route("/confirmado")
def confirmado():
    mensagem = session.pop("mensagem_confirmacao", None)
    dados = session.pop("dados_confirmacao", None)
    if not dados:
        return redirect(url_for("agendar"))

    response = make_response(render_template("confirmado.html", mensagem=mensagem, dados=dados))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

@app.route("/exportar")
def exportar():
    agendamentos = Agendamento.query.all()
    csv_path = os.path.join(basedir, "../data/agendamentos_export.csv")
    with open(csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Nome", "Sala", "Data", "Início", "Fim"])
        for a in agendamentos:
            writer.writerow([a.id, a.nome, a.sala, a.data, a.inicio.strftime("%H:%M"), a.fim.strftime("%H:%M")])
    return send_file(csv_path, as_attachment=True)

@app.route("/", methods=["GET", "POST"])
def agendar():
    session.clear()
    mensagem = ""
    data = request.form.get("data") if request.method == "POST" else request.args.get("data")
    aviso_sem_salas = False
    salas_para_data = []

    if data:
        data_dt = datetime.strptime(data, "%Y-%m-%d").date()
        if data_dt < date.today():
            mensagem = "Não é possível agendar para uma data que já passou."
            return render_template("form.html", salas=[], mensagem=mensagem, aviso_sem_salas=True)
        if data_dt.weekday() in [5, 6]:
            mensagem = "Não é possível agendar aos sábados ou domingos."
            return render_template("form.html", salas=[], mensagem=mensagem, aviso_sem_salas=True)
        salas_para_data = salas_disponiveis_para_data(data, 30)
        if not salas_para_data:
            aviso_sem_salas = True

    if request.method == "POST":
        nome = request.form["nome"]
        sala = request.form["sala"]
        horario_inicio = request.form.get("horario_inicio")
        duracao = int(request.form["duracao"])

        if not horario_inicio:
            mensagem = "Você precisa selecionar um horário disponível antes de confirmar."
            return render_template("form.html", salas=salas_para_data, mensagem=mensagem, aviso_sem_salas=aviso_sem_salas)

        try:
            inicio_dt = datetime.strptime(f"{data} {horario_inicio}", "%Y-%m-%d %H:%M")
            fim_dt = inicio_dt + timedelta(minutes=duracao)
        except ValueError:
            mensagem = "Data ou horário inválido."
            return render_template("form.html", salas=salas_para_data, mensagem=mensagem, aviso_sem_salas=aviso_sem_salas)

        if inicio_dt < datetime.now():
            mensagem = "Não é possível agendar para um horário que já passou."
            return render_template("form.html", salas=salas_para_data, mensagem=mensagem, aviso_sem_salas=aviso_sem_salas)

        if not verificar_disponibilidade(sala, data, inicio_dt, fim_dt):
            mensagem = "Horário indisponível para essa sala."
            return render_template("form.html", salas=salas_para_data, mensagem=mensagem, aviso_sem_salas=aviso_sem_salas)

        novo_agendamento = Agendamento(nome=nome, sala=sala, data=data, inicio=inicio_dt, fim=fim_dt)
        db.session.add(novo_agendamento)
        db.session.commit()

        session["mensagem_confirmacao"] = f"Sala {sala} agendada com sucesso para {nome}!"
        session["dados_confirmacao"] = {
            "nome": nome,
            "sala": sala,
            "data": data,
            "inicio": inicio_dt.strftime("%H:%M"),
            "fim": fim_dt.strftime("%H:%M")
        }
        return redirect(url_for("confirmado"))

    response = make_response(render_template("form.html", salas=salas_para_data, mensagem=mensagem, aviso_sem_salas=aviso_sem_salas))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response

@app.route("/agendamentos")
def listar_agendamentos():
    if session.get("admin_autorizado") != True:
        return redirect(url_for("login_admin"))
    agendamentos = Agendamento.query.order_by(Agendamento.data, Agendamento.inicio).all()
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
    return '''
        <form method="post">
            Senha: <input type="password" name="senha">
            <input type="submit" value="Entrar">
        </form>
    '''

@app.route("/logout")
def logout():
    session.pop("admin_autorizado", None)
    return redirect(url_for("agendar"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)