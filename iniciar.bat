@echo off
title 🧠 Iniciando Agendamento de Salas

echo 🔄 Ativando ambiente virtual e iniciando sistema...
start "" cmd /k "cd /d \"%~dp0app\" && call \"..\venv\Scripts\activate.bat\" && python agendamento.py"

echo 🔒 Pressione qualquer tecla para sair...
pause >nul
