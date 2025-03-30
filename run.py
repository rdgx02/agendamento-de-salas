from app.agendamento import app
import sys

if __name__ == "__main__":
    port = 5000  # porta padrão
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Porta inválida. Usando a porta padrão 5000.")
    app.run(debug=True, port=port)
