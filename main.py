import cv2
from pyzbar.pyzbar import decode
import numpy as np
import time
import requests 

# IP do dispositivo
ip = "192.168.1.65"

# URL para o ESP32CAM
url = 'http://'+ip

# Função para enviar a cor do led
def send_response_to_esp(color):
    esp_ip = url
    payload = {'color': color}

    try:
        response = requests.post(f"{esp_ip}", json=payload)
        print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"Erro ao enviar dados: {e}")

# Função para validar o QRcode
def validate_qrcode(qr_data):
    print(f"Validando QR code: {qr_data}")
    send_response_to_esp("Yellow")
    print("PROCESSANDO")
    user = "test"
    if qr_data == user:
        if user:
            print("APROVADO")
            send_response_to_esp("green")
    else:
        print("REPROVADO")
        send_response_to_esp("red")

    
    # Exemplo de requisição para validar o QR code em uma API
    # response = requests.post('http://api-url/validate', json={'qrcode': qr_data})
    # return response.status_code == 200

# Loop contínuo para capturar QRcode a cada 5 segundos
while True:
    # Capturando imagem
    cap = cv2.VideoCapture(url+"/scan")

    # Lendo uma única imagem da URL
    ret, frame = cap.read()

    # Verificando se a captura foi bem-sucedida
    if ret:
        # Exibe a imagem capturada
        #cv2.imshow('ESP32-CAM - Captura de Imagem', frame)
        # Salva a imagem capturada (opcional)
        #cv2.imwrite('captura_esp32cam.jpg', frame)

        # Decodificar o QRcode na imagem
        decoded_qrcodes = decode(frame)
        
        if decoded_qrcodes:
            for qr in decoded_qrcodes:
                # Extrai os dados do QR code
                qr_data = qr.data.decode('utf-8')
                print(f"QR code detectado: {qr_data}")
                
                # Valida o QR code
                if validate_qrcode(qr_data):
                    print(f"QR code válido: {qr_data}")
                else:
                    print(f"QR code inválido: {qr_data}")
                
                # Desenha um retângulo ao redor do QR code
                pts = qr.polygon
                if len(pts) == 4:  # Certifica que são quatro pontos (um quadrado)
                    # Converte os pontos para o formato adequado do OpenCV
                    pts = [(point.x, point.y) for point in pts]
                    pts = [pts]  # Adiciona os pontos em uma lista para polylines
                    pts = np.array(pts, dtype=np.int32)  # Converte para matriz de inteiros
                    cv2.polylines(frame, pts, isClosed=True, color=(0, 255, 0), thickness=2)
        else:
            print("Nenhum QR code detectado")
        
        # Exibe a imagem com os QR codes detectados, se houver
        cv2.imshow('ESP32-CAM - QR code detectado', frame)
        
        # Fecha a janela automaticamente após captura
        cv2.waitKey(1)
    
    else:
        print("Falha ao capturar a imagem")

    # Libera o recurso da câmera
    cap.release()
    
    # Espera por 5 segundos antes de capturar novamente, ajustar se necessario
    time.sleep(0.1)

    # Para o loop quando a tecla 'q' for pressionada
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Fecha todas as janelas ao sair
cv2.destroyAllWindows()
