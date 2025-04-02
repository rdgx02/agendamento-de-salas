@echo off
echo 🔁 Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo 🚀 Iniciando sistema...
start http://127.0.0.1:5000
python app\agendamento.py

echo 🔒 Pressione qualquer tecla para sair...
pause >nul
