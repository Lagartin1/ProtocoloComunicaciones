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
      self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.sock.bind((self.host, self.port))

      print(f"Servidor escuchando en {self.host}:{self.port}")

    def close(self):
      self.sock.close()

    def init(self,metrics):
      print("Inicializando el servidor...")
      salir = False
      seen = set()  # Para evitar duplicados
      try:
          while True:
              data, addr = self.sock.recvfrom(4096)
              if not data:
                  metrics.incrementar("losses")
                  continue
              response_pkt, error = mainapp(data, metrics)
              if response_pkt is not None:
                  if error:
                      print(f"Error al procesar el paquete sq={response_pkt['seq']}, se envió NACK.")
                      print(f"Error: {error}")
                      metrics.incrementar("incorrect")
                      metrics.incrementar("sent")
                      self.sock.sendto(create_nack(response_pkt['seq'], EXPERCTED_RECEIVER, EMMITER), addr)  # type: ignore
                  else:
                      if response_pkt['seq'] in seen:
                          metrics.incrementar("duplicates")
                          print(f"Paquete duplicado recibido, seq={response_pkt['seq']}, enviando ACK.")
                      else:
                        seen.add(response_pkt['seq'])
                        print(f"Paquete recibido, seq={response_pkt['seq']}, enviando ACK.")
                        if None not in datos:
                          print("Todos los datos recibidos, enviando ACK y Saliendo....")
                          salir = True
                      metrics.ultimo_seq = response_pkt['seq']
                      metrics.incrementar("sent")
                      metrics.incrementar("correct")
                      self.sock.sendto(create_ack(response_pkt['seq'], EXPERCTED_RECEIVER, EMMITER), addr)  # type: ignore
                      if salir:
                          metrics.guardar("receptor")

                          exit(0)

              elif error:
                  print(f"Error {error} en paquete recibido")
                  if isinstance(error, str) and error == "CRC mismatch":
                      metrics.incrementar("crc_errors")
      except Exception as e:
          print(f"Error en el servidor: {e}")
          self.close()
        
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
    global datos
    for i in range(length_data):
      datos.append(None)
    key = parsed.get('key', 0)  # 'key' en handshake es la clave de cifrado
    return None, False
  
  sequence = parsed['sq']
  if sequence in index:
    print(f"Secuencia {parsed['sq']} ya procesada, enviando Ack.")
    return parsed['sq'], False

  
  data_content = parsed.get('data') # Los datos ya vienen descifrados y decodificados como string
  largo = parsed.get('largo', 0)  # Largo del paquete de datos
  
  # Dividir el string en palabras (si el emisor envía palabras individuales)
  # Esto asume que el emisor unió las palabras con `b''.join(item.encode('utf-8') for item in data)`
  # y que no hay espacios adicionales entre ellas.
  # Si el contenido original era una lista de palabras, ahora es un string concatenado.
  # La forma más segura de reconstruir sería enviar la longitud original de las palabras,
  # o re-dividir el string recibido si se sabe el separador original (ej. ' ').
  # Para este ejemplo, asumiremos que los datos se reciben como un solo string y se añaden directamente.
  #:
    # Permitir agregar paquetes perdidos en la posición correcta
  if sequence not in index:
      index.append(sequence)
      if len(datos) <= length_data:
          for i in range(0,len(data_content)):
              if sequence + i < length_data:
                datos[sequence + i] = data_content[i]
              
  ## imprimir posiciones con No
          
  return parsed['sq'], False

if __name__ == "__main__":
  ## incio del servidor
  metrics = Metricas()
  server = SocketServer()
  server.init(metrics)
