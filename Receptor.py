# Receptor.py
from Protocolos import *
import socket


import os
HOST = os.environ.get("HOST", "0.0.0.0")  # Ahora escucha en todas las interfaces

PORT = 5000  # Arbitrary port for testing

EMMITER = b'\x01'  # Emiter
EXPERCTED_RECEIVER = b'\x02'  # Expected receiver

datos = []
length_data = 0
index = []
key = 0


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

    def init(self,metrics):
      print("Inicializando el servidor...")
      self.sock.listen()
      try:
        conn, _ = server.accept_connection()
        with conn:
          while True:
            data = conn.recv(1024)
            if not data:
              metrics.incrementar("losses")
              continue
            response_pkt, error = mainapp(data,metrics)
            if response_pkt is not None:
              if error:
                print(f"Error al procesar el paquete sq={response_pkt['seq']}, se envió NACK.")
                print(f"Error: {error}")
                # Asegurarse de enviar el NACK con el número de secuencia correcto.
                metrics.incrementar("incorrect")
                metrics.incrementar("sent")
                conn.sendall(create_nack(response_pkt['seq'],EXPERCTED_RECEIVER,EMMITER)) # type: ignore
              else:
                print(f"Paquete procesado correctamente seq={response_pkt['seq']}, se envió ACK.")
                # Asegurarse de enviar el ACK con el número de secuencia correcto.
                if error is not None:
                  metrics.incrementar("duplicates")
                metrics.incrementar("sent")
                metrics.incrementar("correct")
                conn.sendall(create_ack(response_pkt['seq'],EXPERCTED_RECEIVER,EMMITER)) # type: ignore
            elif error:
              print(f"Error {error} en paquete recibido")
              if isinstance(error, str) and error == "CRC mismatch":
                metrics.incrementar("crc_errors")
            
      except Exception as e:
        print(f"Error en el servidor: {e}")
        server.close()
        
def mainapp(data,metrics):
  
  sq, error = process_data(data)
  if error is not None and isinstance(error,str) and error == "complete":
    metrics.guardar("receptor")
    print("Datos completos recibidos, guardando métricas.")
    exit(0)

  
  if sq is None and not error:
  # send ACK with no sequence number (for handshake)
    print(f"Recibido, sq={sq} (Handshake)")
    return {
      'type': 'ack',
      'seq': 0
    }, False
  elif not error:
  # send ACK
    print(f"Recibido, sq={sq} (Datos)")
    return {
      'type': 'ack',
      'seq': sq
    }, False
  elif sq is not None and error:
  # send NACK
    print(f"Error, sq={sq} (NACK)")
    return {
      'type': 'nack',
      'seq': sq
    }, True
  else:
    return None, error
    
  

def process_data(data):
  """
  Process the received data.
  """
  global key 

  parsed,error = parse_pkt(data, EXPERCTED_RECEIVER,key)  # type: ignore
  if error:
    return None, error
  
  # Check if it's a handshake packet
  if parsed.get('tipo') == 'h':
    print("Handshake recibido")
    global length_data

    length_data = parsed.get('data', 0) # 'data' en handshake es la longitud total
    key = parsed.get('key', 0)  # 'key' en handshake es la clave de cifrado
    return None, False
  
  sequence = parsed['sq']
  if sequence in index:
    print(f"Secuencia {parsed['sq']} ya procesada, enviando Ack.")
    return parsed['sq'], False
  index.append(sequence)
  
  data_content_str = parsed.get('data', '') # Los datos ya vienen descifrados y decodificados como string
  
  # Dividir el string en palabras (si el emisor envía palabras individuales)
  # Esto asume que el emisor unió las palabras con `b''.join(item.encode('utf-8') for item in data)`
  # y que no hay espacios adicionales entre ellas.
  # Si el contenido original era una lista de palabras, ahora es un string concatenado.
  # La forma más segura de reconstruir sería enviar la longitud original de las palabras,
  # o re-dividir el string recibido si se sabe el separador original (ej. ' ').
  # Para este ejemplo, asumiremos que los datos se reciben como un solo string y se añaden directamente.
  
  if isinstance(data_content_str, str):
    # Opcional: si sabes que los datos originales eran palabras separadas, puedes intentar dividirlos de nuevo.
    # Por ejemplo, si siempre se usó un espacio como separador:
    # palabras_recibidas = data_content_str.split(' ') 
    
    # Para este ejemplo, simplemente añadiremos el string completo a la lista de datos del receptor.
    # Si la intención es reconstruir la lista de palabras original, esto sería más complejo.
    # Por simplicidad y para demostrar el cifrado/descifrado, añadimos el string tal cual.
    if len(datos) < length_data: # Asegurarse de no exceder la longitud total esperada
        datos.append(data_content_str)
        # Verificar si ya se recibieron todos los datos después de agregar el nuevo elemento
        if len(datos) >= length_data:
            print("Todos los datos recibidos.")
            # Aquí podrías guardar los datos en un archivo o procesarlos como necesites
            return None, "complete"
  return parsed['sq'], False

if __name__ == "__main__":
  ## incio del servidor
  metrics = Metricas()
  server = SocketServer()
  server.init(metrics)
