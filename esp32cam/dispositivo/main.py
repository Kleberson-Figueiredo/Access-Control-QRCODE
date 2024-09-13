import network
import socket
import machine
import json
import time
import camera

# Configurando os pinos dos LEDs
green_led = machine.Pin(13, machine.Pin.OUT)
red_led = machine.Pin(12, machine.Pin.OUT)
blue_led = machine.Pin(15, machine.Pin.OUT)

# Função para acender o LED baseado na cor recebida
def control_led(color):
    # Apagar todos os LEDs primeiro
    green_led.value(0)
    red_led.value(0)
    blue_led.value(0)
    
    # Acender o LED correspondente
    if color == "green":
        green_led.value(1)
    elif color == "red":
        red_led.value(1)
    elif color == "yellow":
        red_led.value(1)
        green_led.value(1)

try:
    # Conectando ao Wi-Fi
    def connect_wifi(ssid, password):
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
        print('Conectado ao Wi-Fi:', wlan.ifconfig())


    # Configuração da câmera
    def setup_camera():
        camera.init(0, format=camera.JPEG)
        camera.framesize(camera.FRAME_VGA) # Configurando a resolução para VGA (640x480)
        print("Câmera inicializada")

    # Iniciar servidor HTTP que também serve o stream da câmera
    def start_server():
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        s = socket.socket()
        s.bind(addr)
        s.listen(1)
        blue_led.value(1)
        print('Servidor HTTP iniciado, aguardando conexões...')

        while True:
            blue_led.value(1)
            cl, addr = s.accept()
            print('Cliente conectado desde', addr)
            request = cl.recv(1024).decode('utf-8')
            print('Requisição recebida:', request)

            # Verificando se é uma requisição POST para acionar LEDs
            if 'POST /' in request:
                try:
                    # Extraindo o corpo da requisição JSON
                    json_start = request.find('{')
                    json_end = request.rfind('}') + 1
                    json_data = request[json_start:json_end]
                    data = json.loads(json_data)

                    # Obtendo a cor do JSON
                    color = data.get('color', '').strip().lower()
                    print("Cor recebida: " + color)
                    control_led(color)
                    response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nLED controlado com sucesso!"
                except Exception as e:
                    print("Erro ao processar a requisição:", e)
                    response = "HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\n\r\nErro ao processar a requisição."

                cl.send(response)

            # Verificando se é uma requisição GET para acessar a captura da imagem da câmera
            elif 'GET /scan' in request:
                cl.send(b"HTTP/1.1 200 OK\r\n")

                #cl.send(b"Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n")
                frame = camera.capture()
                cl.send(b"--frame\r\n")
                cl.send(b"Content-Type: image/jpeg\r\n\r\n")
                cl.send(frame)
                cl.send(b"\r\n")

            cl.close()
            time.sleep(3)
            control_led(color=0)
            
    # Configuração e execução
    ssid = 'brasil' # Nome do wifi
    password = '123456789' # Senha do wifi 
    connect_wifi(ssid, password)
    setup_camera()
    start_server()
except Exception as e:
    print("Erro: ",e)
    control_led(color="red")