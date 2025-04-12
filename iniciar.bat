@echo off
title 🧠 Iniciando Agendamento de Salas

echo 🔄 Ativando ambiente virtual...
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else (
    echo ❌ Ambiente virtual ".venv" não encontrado!
    pause
    exit /b
)

echo 📦 Atualizando pip...
python -m pip install --upgrade pip

echo 🚀 Iniciando sistema de agendamento...
start "" http://127.0.0.1:5000
python app\agendamento.py

echo 🔒 Pressione qualquer tecla para sair...
pause >nul
