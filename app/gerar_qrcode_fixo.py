import qrcode

def gerar_qrcode_fixo():
    link_fixo = "https://exemplo.com/agendamento"  # substitua pelo link real
    qr = qrcode.make(link_fixo)
    qr.save("qrcode_sala.png")
    print("✅ QR Code fixo gerado e salvo como 'qrcode_sala.png'")

gerar_qrcode_fixo()
