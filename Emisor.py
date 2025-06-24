from Protocolos import *
import socket

""" 
    opciones para canal:
    -web socket
    -archivos compartidos
    -pipeline
    -sockets con docker y pumba para jitter,perdida de paquetes y latencia
"""
HOST = '127.0.0.1'  # IP local para pruebas
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

def main(socket_cliente):
    frase = ["hola", "mundo", "este", "es", "un", "mensaje"]
    while True:
        i = 0
        while i < len(frase):
            try:
                largo = 3
                
                if i + largo > len(frase):
                    largo = len(frase) - i
                mensaje = create_data_pkt(i,frase[i:i+largo],EMMITER, EXPERCTED_RECEIVER) # type: ignore
                socket_cliente.enviar(mensaje)
                respuesta = socket_cliente.recibir()
                if respuesta:
                    rsp,err = parse_pkt(respuesta, EMMITER)  # type: ignore
                    print()
                    if rsp is None:
                        print("Paquete recibido no válido o error en el procesamiento.")
                    elif rsp['tipo'] == 'a':
                        print(f"ACK recibido para secuencia {rsp['sq']}.")
                        i += largo
                    elif rsp['tipo'] == 'n':
                        print(f"NACK recibido para secuencia {rsp['sq']}. Reintentando...")
                        continue
                    
                else:
                    print("No se recibió respuesta del servidor.")
                    # Intentar nuevamente o manejar el caso de no respuesta
                exit(0)
            except Exception as e:
                print(f"Error: {e}")

    
    
if __name__ == "__main__":
    socket_cliente = ClienteSocket(HOST, PORT)
    socket_cliente.conectar()
    main(socket_cliente)