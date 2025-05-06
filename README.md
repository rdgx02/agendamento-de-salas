🗓️ Sistema de Agendamento de Salas
Este projeto é um sistema simples e funcional para agendamento de salas. Foi desenvolvido com Flask e SQLite, com foco em usabilidade mobile e praticidade para ambientes internos, como empresas, escolas ou coworkings.

🚀 Funcionalidades
📅 Reservar salas disponíveis por data, horário e duração

🔒 Área administrativa com login protegido por senha

📋 Listagem completa de todos os agendamentos (admin)

👀 Painel público para visualização dos agendamentos (sem login)

❌ Cancelamento de agendamento com verificação por ticket

🔍 Consulta de agendamentos por nome

📥 Exportação de agendamentos para CSV

✅ Bloqueio de agendamentos em finais de semana e feriados

🔐 Proteção contra navegação via setas (voltar/avançar) em telas sensíveis

💾 Opção de salvar o cartão de confirmação como imagem (PNG)

🔁 Agendamento recorrente (semanal ou mensal)

📱 Interface amigável e 100% responsiva para dispositivos móveis

🤖 Integração com WhatsApp via n8n + Evolution API

⚙️ Como rodar localmente
Pré-requisitos:
Python 3.10+

Git

1. Clone o repositório:
- git clone https://github.com/rdgx02/agendamento-de-salas.git
- cd agendamento-de-salas

2. Crie o ambiente virtual:
python -m venv venv

3. Ative o ambiente virtual:
- No PowerShell:  .\venv\Scripts\Activate.ps1

- No CMD:  venv\Scripts\activate.bat

4. Instale as dependências:
- pip install -r requirements.txt

5. Execute o sistema:
- python app/agendamento.py

6. Acesse no navegador:

http://127.0.0.1:5000


🔐 Acesso Admin
URL: /admin

Senha padrão: minhasupersecreta


🤖 Integração com WhatsApp (n8n + Evolution API)
Este sistema está integrado ao n8n para envio automático de mensagens de confirmação via WhatsApp, utilizando a Evolution API.

. Como funciona:

- O sistema envia um POST com os dados do agendamento para o Webhook do n8n

- O n8n valida a chave de API e, se correta, envia a mensagem formatada ao número do usuário via Evolution API

- A mensagem contém: nome, sala, data, horário e o número do ticket

Segurança:

- Autenticação por API Key nos headers

- O fluxo do n8n só continua se a chave for válida


📁 Estrutura do projeto:

├── app
│   ├── agendamento.py
│   ├── gerar_qrcode_fixo.py
│   └── templates
├── data
│   └── agendamentos.db (não vai pro GitHub)
├── static
│   ├── qrcodes
│   ├── comprovantes
│   └── styles.css
├── venv (ignorado)
├── run.py
├── iniciar.bat (opcional)
├── requirements.txt
└── README.md


👤 Autor
Desenvolvido por rdgx02 💻
Instituto de Química – LADETEC / UFRJ

📌 Licença
Este projeto está sob a licença MIT. Sinta-se livre para usar, modificar e compartilhar.