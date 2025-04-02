# 🗓️ Sistema de Agendamento de Salas

Este projeto é um sistema simples e funcional para agendamento de salas. Foi desenvolvido com **Flask** e **SQLite**, com foco em usabilidade mobile e praticidade para ambientes internos, como empresas, escolas ou coworkings.

---

## 🚀 Funcionalidades

- 📅 Reservar salas disponíveis por data, horário e duração
- 🔒 Área administrativa com login protegido por senha
- 📋 Listagem de todos os agendamentos
- ❌ Cancelamento por ticket (apenas com código de confirmação)
- 🔍 Consulta de agendamentos por nome
- 📥 Exportação de todos os agendamentos para CSV
- ✅ Proteção contra agendamentos em finais de semana
- 📱 Interface amigável para celular

---

## ⚙️ Como rodar localmente

### Pré-requisitos:
- Python 3.10+
- Git

### Passo a passo:

1. Clone o repositório:
```bash
git clone https://github.com/rdgx02/agendamento-de-salas.git
cd agendamento-de-salas
```

2. Crie o ambiente virtual:
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
- No PowerShell:
```bash
.\venv\Scripts\Activate.ps1
```
- No CMD:
```bash
venv\Scripts\activate.bat
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Execute o sistema:
```bash
python app/agendamento.py
```

6. Acesse no navegador:
```
http://127.0.0.1:5000
```

---

## 🔐 Acesso Admin

- URL: `/admin`
- Senha padrão: `minhasupersecreta`

---

## 📁 Estrutura do projeto
```
├── app
│   ├── agendamento.py
│   ├── gerar_qrcode_fixo.py
│   └── templates
├── data
│   └── agendamentos.db (não vai pro GitHub)
├── static (opcional)
├── venv (ignorado)
├── run.py
├── iniciar.bat (opcional)
├── requirements.txt
└── README.md
```

---

## 👤 Autor

Desenvolvido por [rdgx02](https://github.com/rdgx02) 💻

---

## 📌 Licença

Este projeto está sob a licença MIT. Sinta-se livre para usar, modificar e compartilhar.

