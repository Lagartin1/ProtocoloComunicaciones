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


class ClienteSocket:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def conectar(self):
        self.socket.connect((self.host, self.port))

    def enviar(self, mensaje):
        self.socket.sendall(mensaje.encode())

    def recibir(self):
        data = self.socket.recv(1024)
        
        return data.decode() if data else None

    def cerrar(self):
        self.socket.close()

def main(socket_cliente):
    while True:
        try:
            mensaje = input("Ingrese el mensaje a enviar (o 'exit' para salir): ")
            if mensaje.lower() == 'exit':
                break
            socket_cliente.enviar(mensaje)
            respuesta = socket_cliente.recibir()
            # time out de respuesta no recibida, reintentar
        except Exception as e:
            print(f"Error: {e}")

    
if __name__ == "__main__":
    socket_cliente = ClienteSocket(HOST, PORT)
    socket_cliente.conectar()
    main(socket_cliente)