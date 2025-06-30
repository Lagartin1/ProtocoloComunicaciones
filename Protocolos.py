import random
import json
from datetime import datetime

HEADER = b'\x01'  # header byte
FOOTER = b'\x02'  # footer byte


def parse_pkt(pkt, EXPERCTED_RECEIVER,key:int):
    """
    Parse a packet and return its components.
    """
    if len(pkt) < 10:  # Minimum packet size
        return None, "Packet too short"
    
    if pkt[0] != HEADER[0] or pkt[-1] != FOOTER[0]:
        return None, "Invalid header or footer"

    emisor = pkt[1]
    receptor = pkt[2]
    tipo = chr(pkt[3])
    sq = int.from_bytes(pkt[4:6], byteorder='big')
    
    if tipo == 'p':
        # Data packet: header + emisor + receptor + tipo + secuencia(2) + largo(2) + data + crc(2) + footer
        largo = int.from_bytes(pkt[6:8], byteorder='big')
        data_encrypted = pkt[8:8 + largo]
        crc_received = int.from_bytes(pkt[8 + largo:8 + largo + 2], byteorder='big')
        crc_calculated = crc16_ibm(pkt[1:8 + largo])  # Exclude header and footer
        
        # --- VERIFICACIÓN DE CIFRADO/DESCIFRADO ---
        #print(f"Receptor: Datos cifrados recibidos (raw): {data_encrypted}")
        # Descifrar los datos aquí
        data = descifrar(data_encrypted,key) # Llamada a descifrar
        #print(f"Receptor: Datos descifrados (bytes): {data}")
        # --- FIN VERIFICACIÓN ---

    elif tipo == 'h':
        # Handshake packet: header + emisor + receptor + tipo + secuencia(2) + data(2) + largo(1) + crc(2) + footer
        data_value = int.from_bytes(pkt[6:8], byteorder='big')
        key = pkt[8]  # Key for encryption (1 byte)
        largo = pkt[9]  # Largo de los datos (1 byte)
        crc_received = int.from_bytes(pkt[10:12], byteorder='big')
        crc_calculated = crc16_ibm(pkt[1:10])  # Exclude header and footer
        data = data_value
    else:
        # ACK/NACK packet: header + emisor + receptor + tipo + secuencia(2) + largo(1) + crc(2) + footer
        largo = int.from_bytes(pkt[6:7], byteorder='big')
        crc_received = int.from_bytes(pkt[7:9], byteorder='big')
        crc_calculated = crc16_ibm(pkt[1:7])  # Exclude header and footer
        data = None

    if crc_received != crc_calculated:
        return None, "CRC mismatch"
    
    if receptor != EXPERCTED_RECEIVER[0]:
        print(f"Receptor esperado: {EXPERCTED_RECEIVER[0]}, Receptor recibido: {receptor}")
        return None, "Unexpected receiver"
    
    result = {
        'emisor': emisor,
        'receptor': receptor,
        'tipo': tipo,
        'sq': sq,
    }
    
    if tipo == 'p':
        result['largo'] = largo
        result['data'] = data.decode('utf-8') # Decodificar los datos descifrados a string
        #print(f"Receptor: Datos descifrados y decodificados: {result['data']}") # Imprimir la versión final decodificada
    elif tipo == 'h':
        result['data'] = data
        result['key'] = key
    
    return result, None

# CRC-16 CCITT (XModem)
POLY = 0xA001  # CRC-16 IBM (reflejado)
def crc16_ibm(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ POLY
            else:
                crc >>= 1
    return crc & 0xFFFF


def cifrador(data, key: int):
    ## Cifra un dato con XOR
   
    data_bytes = bytearray(data)
    # Encrypt the data using XOR with the key
    return xor_cipher(data_bytes, key)


def descifrar(data, key: int):
    ## Descifra un dato cifrado con XOR
    data_bytes = bytearray(data)
    return xor_cipher(data_bytes, key)
    

# This function takes a byte array and a key, and returns the XORed result.
def xor_cipher(data: bytes, key:int) -> bytes:
    return bytes(b ^ key for b in data)



def create_data_pkt(sq: int, key:int,data: list[str],EMMITER: bytes, EXPERCTED_RECEIVER: bytes) -> bytes:
    """
    Create a data packet with the given sequence number and data.
    """
    # Convert the data to bytes
    data_bytes = b''.join(item.encode('utf-8') for item in data)
    
    # --- VERIFICACIÓN DE CIFRADO/DESCIFRADO ---
    #print(f"Emisor: Datos originales (bytes): {data_bytes}")
    # Cifrar los datos aquí
    data_encrypted = cifrador(data_bytes,key) # Llamada a cifrador
    #print(f"Emisor: Datos cifrados (bytes): {data_encrypted}")
    ## --- FIN VERIFICACIÓN ---

    largo = len(data_encrypted)  # Length of the encrypted data
    
    # Create the packet structure
    pkt = bytearray()
    pkt.append(HEADER[0])  # Header
    pkt.append(EMMITER[0])  # Emisor
    pkt.append(EXPERCTED_RECEIVER[0])  # Receptor esperado
    pkt.append(ord('p'))  # Tipo de paquete (using 'p' as representation for data packet)
    pkt.extend(sq.to_bytes(2, byteorder='big'))  # Secuencia
    pkt.extend(largo.to_bytes(2, byteorder='big'))  # Largo de los datos (de los datos cifrados)
    #print(f"Emisor: {EMMITER[0]}, Receptor: {EXPERCTED_RECEIVER[0]}, Tipo: 'p', Secuencia: {sq}, Largo: {largo.to_bytes(2, byteorder='big')}")
    pkt.extend(data_encrypted)  # Datos CIFRADOS
    
    # Calculate CRC and append it to the packet
    # El CRC se calcula sobre la parte de control y los datos CIFRADOS
    crc = crc16_ibm(pkt[1:])  # Exclude header and footer for CRC calculation
    pkt.extend(crc.to_bytes(2, byteorder='big'))  # CRC
    pkt.append(FOOTER[0])  # Footer
    
    # Solo test para verificar el crc sin pumba
    # # añadir un error en los datos para probar el CRC
    # en base a una probabilidad, se añade un error en el byte 10
    #if random.random() < 0.2:  # 10% chance to introduce an error
    #    pkt[10] = (pkt[10] + 1) % 256    
    return bytes(pkt)



def create_ack(sq: int, EMMITER: bytes, EXPERCTED_RECEIVER: bytes) -> bytes:
    """
    Create an ACK packet with the given sequence number.
    """
    pkt = bytearray()
    pkt.append(HEADER[0])  # Header
    pkt.append(EMMITER[0])  # Emisor
    pkt.append(EXPERCTED_RECEIVER[0])  # Receptor esperado
    # tipo ack
    pkt.append(ord('a'))  # Tipo ACK (using 'a' as representation)
    pkt.extend(sq.to_bytes(2, byteorder='big'))  # Secuencia
    pkt.extend((1).to_bytes(1, byteorder='big'))  # Largo de los datos (1 para ACK)

    # Calculate CRC and append it to the packet, paquete tiene  header, receptor, emisor, tipo, secuencia y largo
    ## entonces crc sobre todo el packete menos el header
    crc = crc16_ibm(pkt[1:])  # Exclude header and footer for CRC calculation
    pkt.extend(crc.to_bytes(2, byteorder='big'))  # CRC
    pkt.append(FOOTER[0])  # Footer
    
    
    return bytes(pkt)



def create_nack(sq: int, EMMITER: bytes, EXPERCTED_RECEIVER: bytes) -> bytes:   
    """
    Create a NACK packet with the given sequence number.
    """
    pkt = bytearray()
    pkt.append(HEADER[0])  # Header
    pkt.append(EMMITER[0])  # Emisor
    pkt.append(EXPERCTED_RECEIVER[0])  # Receptor esperado
    pkt.append(ord('n'))  # Tipo NACK (using 'n' as representation)
    pkt.extend(sq.to_bytes(2, byteorder='big'))  # Secuencia
    pkt.extend((1).to_bytes(1, byteorder='big'))  # Largo de los datos (1 para NACK)

    # Calculate CRC and append it to the packet
    crc = crc16_ibm(pkt[1:])  # Exclude header and footer for CRC calculation
    pkt.extend(crc.to_bytes(2, byteorder='big'))  # CRC
    pkt.append(FOOTER[0])  # Footer
    
    return bytes(pkt)


def create_handshake_pkt(data:int,key:int,EMMITER: bytes, EXPERCTED_RECEIVER: bytes) -> bytes:
    """
    Create a handshake packet.
    """
    # Convert the data to bytes
    pkt = bytearray()
    pkt.append(HEADER[0])  # Header
    pkt.append(EMMITER[0])  # Emisor
    pkt.append(EXPERCTED_RECEIVER[0])  # Receptor esperado
    pkt.append(ord('h'))  # Tipo Handshake (using 'h' as representation)
    pkt.extend((0).to_bytes(2, byteorder='big'))  # Secuencia (0 for handshake)
    pkt.extend((data).to_bytes(2, byteorder='big'))  # Data (length of the data)
    pkt.extend((key).to_bytes(1, byteorder='big'))  # Key for encryption (1 byte)
    pkt.extend((1).to_bytes(1, byteorder='big'))  # Largo de los datos (1 for handshake)

    # Calculate CRC and append it to the packet
    crc = crc16_ibm(pkt[1:])  # Exclude header and footer for CRC calculation
    pkt.extend(crc.to_bytes(2, byteorder='big'))  # CRC
    pkt.append(FOOTER[0])  # Footer
    
    return bytes(pkt)



class Metricas:
    def __init__(self):
        self.stats = {
            "crc_errors": 0,
            "duplicates": 0,
            "losses": 0,
            "sent": 0,
            "correct": 0,
            "incorrect":0
        }

    def incrementar(self, clave):
        if clave in self.stats:
            self.stats[clave] += 1

    def guardar(self,container):
        newRoute= f"/app/metrics/{container}_metrics.json"
        self.stats["timestamp"] = datetime.now().isoformat()
        with open(newRoute, "w") as f:
            json.dump(self.stats, f, indent=4)

    def mostrar(self):
        for k, v in self.stats.items():
            print(f"{k}: {v}")

