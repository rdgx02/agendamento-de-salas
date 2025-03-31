# Agendamento de Salas

Sistema simples e eficiente para agendamento de salas de reunião. Desenvolvido com Python, Flask e SQLite.

---

## 📄 Visão Geral
Permite que usuários reservem salas de reunião com data, horário e duração, respeitando regras como:

- Não permite agendar para datas passadas
- Bloqueia finais de semana (sábado e domingo)
- Garante que uma sala não tenha choques de horário
- Mostra mensagens de erro claras
- Painel administrativo para visualização e cancelamento de reservas

---

## 📁 Estrutura do Projeto
```
agendamento-de-salas/
├── agendamento.py
├── gerar_qrcode_fixo.py
├── templates/
│   ├── agendamentos.html
│   ├── confirmado.html
│   ├── form.html
│   └── login_admin.html
├── data/
│   ├── agendamentos.db
│   └── agendamentos_export.csv
├── static/
├── run.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🚀 Como Executar Localmente

### 1. Clone o repositório
```bash
git clone https://github.com/rdgx02/agendamento-de-salas.git
cd agendamento-de-salas
```

### 2. Crie um ambiente virtual (opcional, mas recomendado)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Rode o projeto
```bash
python run.py
```

Acesse: [http://localhost:5000](http://localhost:5000)

---

## 🔒 Acesso Admin

- Acesse: [http://localhost:5000/admin](http://localhost:5000/admin)
- Senha padrão: `minhasupersecreta`

---

## 🎨 Prints
### Formulário
![Formulário](https://user-images.githubusercontent.com/rdgx02/formulario.png)

### Confirmação
![Confirmação](https://user-images.githubusercontent.com/rdgx02/confirmado.png)

### Painel Admin
![Admin](https://user-images.githubusercontent.com/rdgx02/painel.png)

> (Se preferir, posso gerar essas imagens e te enviar os links ou README atualizado com elas.)

---

## 🚜 Futuras Melhorias
- Autenticação por login
- Cancelamento via QR Code
- Integração com e-mail
- Bloqueio automático de feriados nacionais e regionais (RJ)

---

## ❤️ Feito por [@rdgx02](https://github.com/rdgx02)

Sistema de agendamento criado com foco em aprendizado prático e utilidade real no ambiente corporativo ou institucional.

