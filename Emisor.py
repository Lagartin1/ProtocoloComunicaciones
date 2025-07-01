from Protocolos import *
import socket
import os
import time


HOST = os.environ.get("RECEIVER_HOST", "127.0.0.1")  # Ahora usa variable de entorno
PORT = 5000           # Puerto arbitrario
EMMITER = b'\x01'  # Emisor
EXPERCTED_RECEIVER = b'\x02'  # Receptor esperado
TIMEOUT = 5.0        # segundos a esperar por ACK

key = int(0x5A)


False


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
    last = False
    while True:
        i = 0    
        while i <= len(datos):
            try:
                if handshake:
                    largo = 20  # Tamaño del paquete de datos
                    #9640
                    if i + largo > len(datos):
                        largo = len(datos) - i
                        last = True
                    mensaje = create_data_pkt(i,key,datos[i:i+largo],EMMITER, EXPERCTED_RECEIVER) # type: ignore
                    print(f"Enviando datos con secuencia {i}.")
                    socket_cliente.enviar(mensaje)
                    metrics.incrementar("sent")
                    respuesta = socket_cliente.recibir()
                    if respuesta:
                        rsp, err = parse_pkt(respuesta, EMMITER, key)
                        #print(f"Respuesta recibida:{i} {rsp}, Error: {err}")
                        if last and rsp and rsp['tipo'] == 'a' and rsp['sq'] == i:
                            print(f"ACK recibido seq={i + largo}.")
                            metrics.incrementar("correct")
                            i += largo
                            metrics.guardar("emisor")
                            return
                        elif last and rsp and rsp['tipo'] == 'a' and rsp['sq'] != i :
                            print(f"ACK recibido con secuencia {rsp['sq']} en lugar de {i}, Reintentando...")
                            metrics.incrementar("incorrect")
                        else:
                            if rsp and rsp['tipo'] == 'a' and rsp['sq'] == i :
                                print(f"ACK recibido seq={i}.")
                                metrics.incrementar("correct")
                                i += largo
                            elif rsp and rsp['tipo'] == 'a' and rsp['sq'] != i :
                                print(f"ACK recibido con secuencia {rsp['sq']} en lugar de {i}, Reintentando...")
                                
                            elif rsp and rsp['tipo'] == 'n':
                                print(f"NACK recibido seq={i}.")
                                metrics.incrementar("incorrect")
                        
                    else:
                        print(f"[WARN] Timeout seq={i}. Reintentando...")
                        metrics.incrementar("losses")
                        
                else:
                    ## enviar handshake
                    mensaje = create_handshake_pkt(int(len(datos)),key, EMMITER, EXPERCTED_RECEIVER)  # type: ignore
                    
                    socket_cliente.enviar(mensaje)
                    metrics.incrementar("sent")
                    respuesta = socket_cliente.recibir()
                    if respuesta:
                        rsp, err = parse_pkt(respuesta, EMMITER, key)
                        if rsp and rsp['tipo'] == 'a':
                           print("ACK recibido para Handshake.")
                           metrics.incrementar("correct")
                           handshake = True
                        elif rsp and rsp['tipo'] == 'n':
                           print("NACK recibido para Handshake.")
                           metrics.incrementar("incorrect")
                    else:
                        print("[WARN] Timeout handshake")
                        metrics.incrementar("timeouts")   
            except Exception as e:
                print(f"Error: {e}")
        metrics.guardar("emisor")
        exit(0)

    
    
if __name__ == "__main__":
    datos = []

    with open('data/Scott Fitzgerald - El extraño caso de Benjamin Button.txt', 'r',encoding='utf-8') as file:
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
