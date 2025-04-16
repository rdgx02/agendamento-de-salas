@echo off
cd /d "%~dp0"

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Atualizando projeto via Git...
git pull

echo Iniciando sistema de agendamento...
start "" http://127.0.0.1:5000
python app/agendamento.py

pause
