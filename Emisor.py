from Protocolos import *
import socket
import os
import time


HOST = os.environ.get("RECEIVER_HOST", "127.0.0.1")  # Ahora usa variable de entorno
PORT = 5000           # Puerto arbitrario
EMMITER = b'\x01'  # Emisor
EXPERCTED_RECEIVER = b'\x02'  # Receptor esperado
MAX_RETRIES = 3      # cuántos reintentos antes de dar por perdido
TIMEOUT = 2.0        # segundos a esperar por ACK

key = int(0x5A)





class ClienteSocket:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(TIMEOUT)  # Establecer tiempo de espera para recibir datos

    def enviar(self, mensaje):
        self.socket.sendto(mensaje, (self.host, self.port))

    def recibir(self):
        try:
            data = self.socket.recv(1024)
            return data if data else None
        except socket.timeout:
            print("Tiempo de espera agotado para recibir datos.")
            return None

    def cerrar(self):
        self.socket.close()

def main(socket_cliente,datos,metrics):
    handshake = False
    while True:
        i = 0    
        while i < len(datos):
            try:
                if handshake:
                    largo = 20  # Tamaño del paquete de datos
                    
                    if i + largo > len(datos):
                        largo = len(datos) - i
                    mensaje = create_data_pkt(i,key,datos[i:i+largo],EMMITER, EXPERCTED_RECEIVER) # type: ignore
                    ack_ok = False
                    for intento in range(MAX_RETRIES):
                        socket_cliente.enviar(mensaje)
                        metrics.incrementar("sent")
                        respuesta = socket_cliente.recibir()
                        if respuesta:
                            rsp, err = parse_pkt(respuesta, EMMITER, key)
                            if rsp and rsp['tipo'] == 'a' and rsp['sq'] == i:
                                print(f"ACK recibido seq={i}.")
                                metrics.incrementar("correct")
                                i += largo
                                ack_ok = True
                                break
                            elif rsp and rsp['tipo'] == 'n':
                                print(f"NACK recibido seq={i}. Reintentando...")
                                metrics.incrementar("incorrect")
                                continue
                        print(f"[WARN] Timeout seq={i}, intento {intento+1}/{MAX_RETRIES}")
                        metrics.incrementar("timeouts")
                    if not ack_ok:
                        print(f"[ERROR] No llegó ACK seq={i} tras {MAX_RETRIES} intentos.")
                        metrics.incrementar("lost_app")
                        i += largo  # o decide si vuelves a intentar más adelante
                        # Intentar nuevamente o manejar el caso de no respuesta
                else:
                    ## enviar handshake
                    mensaje = create_handshake_pkt(int(len(datos)),key, EMMITER, EXPERCTED_RECEIVER)  # type: ignore
                    ack_ok = False
                    for intento in range(MAX_RETRIES):
                        socket_cliente.enviar(mensaje)
                        metrics.incrementar("sent")
                        respuesta = socket_cliente.recibir()
                        if respuesta:
                            rsp, err = parse_pkt(respuesta, EMMITER, key)
                            if rsp and rsp['tipo'] == 'a':
                               print("ACK recibido para Handshake.")
                               metrics.incrementar("correct")
                               ack_ok = True
                               handshake = True
                               break
                            elif rsp and rsp['tipo'] == 'n':
                               print("NACK recibido para Handshake. Reintentando...")
                               metrics.incrementar("incorrect")
                               continue
                        print(f"[WARN] Timeout handshake, intento {intento+1}/{MAX_RETRIES}")
                        metrics.incrementar("timeouts")
                    if not ack_ok:
                      print(f"[ERROR] Handshake falló tras {MAX_RETRIES} intentos.")
                      metrics.incrementar("lost_app")
                      return  # o break, según quieras abortar
                    
            except Exception as e:
                print(f"Error: {e}")
        metrics.guardar("emisor")
        exit(0)

    
    
if __name__ == "__main__":
    datos = []

    with open('data/C. S. Lewis - Las Crónicas de Narnia 1 - El León, la Bruja y el Ropero.txt', 'r',encoding='utf-8') as file:
        for line in file:
            datos.extend(line.strip().split())

    print(f"Datos cargados: {len(datos)}.")
    socket_cliente = ClienteSocket(HOST, PORT)
    metrics = Metricas()
        # sleep 1 minuto
    print("Esperando 20 segundos antes de enviar los datos...")
    time.sleep(20)  # Espera 1 minuto antes de enviar los datos
    print("Iniciando envío de datos...")
    main(socket_cliente, datos,metrics)
