import os
import subprocess
import webbrowser

print("🔁 Preparando ambiente e iniciando sistema de agendamento...")

# Verifica se a pasta data existe
if not os.path.exists("data"):
    print("📂 Pasta 'data' não encontrada. Criando...")
    os.makedirs("data")

# Caminho do script a ser executado
script_path = r"app\agendamento.py"

# Comando para ativar o venv e rodar o app
comando = rf"venv\Scripts\activate && python {script_path}"

try:
    # Abre navegador automaticamente na aplicação
    webbrowser.open("http://127.0.0.1:5000")

    # Executa o servidor com ambiente ativado
    subprocess.run(["cmd", "/k", comando], check=True)

except subprocess.CalledProcessError as e:
    print("❌ Erro ao iniciar o sistema:", e)
    print("Verifique se o ambiente está configurado corretamente.")