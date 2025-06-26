from Protocolos import *
import socket

""" 
    opciones para canal:
    -web socket
    -archivos compartidos
    -pipeline
    -sockets con docker y pumba para jitter,perdida de paquetes y latencia
"""
import os
import time
HOST = os.environ.get("RECEIVER_HOST", "127.0.0.1")  # Ahora usa variable de entorno
PORT = 5000           # Puerto arbitrario
EMMITER = b'\x01'  # Emisor
EXPERCTED_RECEIVER = b'\x02'  # Receptor esperado




class ClienteSocket:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)  # Establecer un tiempo de espera de 5 segundos para las operaciones de socket

    def conectar(self):
        self.socket.connect((self.host, self.port))

    def enviar(self, mensaje):
        self.socket.sendall(mensaje)

    def recibir(self):
        try:
            data = self.socket.recv(1024)
            return data if data else None
        except socket.timeout:
            print("Tiempo de espera agotado para recibir datos.")
            return None

    def cerrar(self):
        self.socket.close()

def main(socket_cliente,datos):
    handshake = False
    while True:
        i = 0    
        while i < len(datos):
            try:
                if handshake:
                    largo = 20  # Tamaño del paquete de datos
                    
                    if i + largo > len(datos):
                        largo = len(datos) - i
                    mensaje = create_data_pkt(i,datos[i:i+largo],EMMITER, EXPERCTED_RECEIVER) # type: ignore
                    socket_cliente.enviar(mensaje)
                    respuesta = socket_cliente.recibir()
                    if respuesta:
                        rsp,err = parse_pkt(respuesta, EMMITER)  # type: ignore
                        print()
                        if rsp is None:
                            print("Paquete recibido no válido o error en el procesamiento.")
                        elif rsp['tipo'] == 'a':
                            print(f"ACK recibido para secuencia {rsp['sq']}.")
                            if rsp['sq'] != i:
                                print(f"Secuencia esperada {i}, pero se recibió {rsp['sq']}. Reintentando...")
                                continue
                            #print(f"Datos enviados: {datos[i:i+largo]}")
                            i += largo
                        elif rsp['tipo'] == 'n':
                            print(f"NACK recibido para secuencia {rsp['sq']}. Reintentando...")
                            continue
                        
                    else:
                        print("No se recibió respuesta del servidor.")
                        # Intentar nuevamente o manejar el caso de no respuesta
                else:
                    ## enviar handshake
                    mensaje = create_handshake_pkt(int(len(datos)), EMMITER, EXPERCTED_RECEIVER)
                    socket_cliente.enviar(mensaje)
                    respuesta = socket_cliente.recibir()
                    if respuesta:
                        rsp,err = parse_pkt(respuesta, EMMITER)  # type: ignore
                        print()
                        if rsp is None:
                            print("Paquete recibido no válido o error en el procesamiento.")
                        elif rsp['tipo'] == 'a':
                            print(f"ACK recibido para Handshake.")
                            handshake = True
                        elif rsp['tipo'] == 'n':
                            print(f"NACK recibido para Handshake. Reintentando...")
                            continue
            except Exception as e:
                print(f"Error: {e}")
        exit(0)

    
    
if __name__ == "__main__":
    datos = []

    with open('data/C. S. Lewis - Las Crónicas de Narnia 1 - El León, la Bruja y el Ropero.txt', 'r',encoding='utf-8') as file:
        for line in file:
            datos.extend(line.strip().split())

    print(f"Datos cargados: {len(datos)}.")
    socket_cliente = ClienteSocket(HOST, PORT)
    socket_cliente.conectar()
    # sleep 1 minuto
    print("Esperando 20 segundos antes de enviar los datos...")
    time.sleep(20)  # Espera 1 minuto antes de enviar los datos
    print("Iniciando envío de datos...")
    main(socket_cliente, datos)
