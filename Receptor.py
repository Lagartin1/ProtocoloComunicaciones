# Receptor.py
from Protocolos import *
import socket


HOST = '127.0.0.1'  # Localhost for testing
PORT = 5000  # Arbitrary port for testing

EMMITER = b'\x01'  # Emiter
EXPERCTED_RECEIVER = b'\x02'  # Expected receiver

datos = []
length_data = 0
index = []



class SocketServer:
    def __init__(self, host=HOST, port=PORT):
      self.host = host
      self.port = port
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.sock.bind((self.host, self.port))
      self.sock.listen()
      print(f"Servidor escuchando en {self.host}:{self.port}")

    def accept_connection(self):
      conn, addr = self.sock.accept()
      print(f"Conexión aceptada de {addr}")
      return conn, addr

    def close(self):
      self.sock.close()

    def init(self):
      print("Inicializando el servidor...")
      self.sock.listen()
      try:
        conn, addr = server.accept_connection()
        with conn:
          while True:
            data = conn.recv(1024)
            if not data:
              continue
            response_pkt, error = mainapp(data)
            if response_pkt is not None:
              if error:
                print("Error al procesar el paquete, se envió NACK.")
                conn.sendall(create_nack(response_pkt['seq'],EXPERCTED_RECEIVER,EMMITER)) # type: ignore
              else:
                print("Paquete procesado correctamente, se envió ACK.")
                conn.sendall(create_ack(response_pkt['seq'],EXPERCTED_RECEIVER,EMMITER)) # type: ignore
      except Exception as e:
        print(f"Error en el servidor: {e}")
        server.close()
        
def mainapp(data):
  
  sq, error = process_data(data)
  
  if sq is None and not error:
    # send ACK with no sequence number
    print(f"Recibido,sq={sq}")
    return {
      'type': 'ack',
      'seq': 0
    }, False
  elif not error:
    # send ACK
    return {
      'type': 'ack',
      'seq': sq
    }, False
  elif sq is not None and error:
    # send NACK
    return {
      'type': 'nack',
      'seq': sq
    }, True
  else:
    print("No se pudo procesar el paquete correctamente.")
    return None, True
  
  

def process_data(data):
  """
  Process the received data.
  """
  parsed,error = parse_pkt(data, EXPERCTED_RECEIVER) 
  if error:
    print(f"Error al procesar el paquete: {error}")
    return None, True
  
  sequence = parsed['sq']
  if sequence in index:
    print(f"Secuencia {parsed['sq']} ya procesada, enviando NACK.")
    return parsed['sq'], True
  index.append(sequence)
  for i in range(sequence-1,len(parsed['data'])+1):
    if i >= length_data: 
      break
    datos.append(parsed['data'][i])
      
  return parsed['sq'], False




if __name__ == "__main__":
  ## incio del servidor
  server = SocketServer()
  server.init()
  
