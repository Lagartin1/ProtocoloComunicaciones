
HEADER = b'\x01'  # header byte


def parse_pkt(pkt, EXPERCTED_RECEIVER):
    """
    Parse a packet and return its components.
    """
    if len(pkt) < 7:
        return None, "Packet too short"
    
    if pkt[0] != HEADER[0] :
        return None, "Invalid header or footer"

    emisor = pkt[1]
    receptor = pkt[2]
    tipo = chr(pkt[3])
    sq = int.from_bytes(pkt[4:6], byteorder='big')
    # largo es un int de valor 3 o 1,
    largo = int.from_bytes(pkt[6:10], byteorder='big')
    ## verifcar tipo
    if tipo == 'p':
        data = pkt[10:10 + largo]
        crc_received = int.from_bytes(pkt[10 + largo:10 + largo + 2], byteorder='big')
        crc_calculated = crc16_ibm(pkt[1:10 + largo])  # Exclude header and footer for CRC calculation
    else:
        # header + emisor + receptor + tipo + secuencia + largo+ crc, para paquetes tipo a y n
        crc_received = int.from_bytes(pkt[8:10], byteorder='big')
        crc_calculated = crc16_ibm(pkt[1:8])  # Exclude header and footer for CRC calculation

    if crc_received != crc_calculated:
        return None, "CRC mismatch"
    
    if receptor != EXPERCTED_RECEIVER[0]:
        print(f"Receptor esperado: {EXPERCTED_RECEIVER}, Receptor recibido: {receptor}")
        return None, "Unexpected receiver"
    
    if tipo == 'p':
        return {
            'emisor': emisor,
            'receptor': receptor,
            'tipo': tipo,
            'sq': sq,
            'largo': largo,
            'data': data
        }, None
    return {
        'emisor': emisor,
        'receptor': receptor,
        'tipo': tipo,
        'sq': sq,
    }, None
    

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


def cifrador(data, key: int = 0x5A):
    ## Cifra un dato con XOR
   
    data_bytes = bytearray(data)
    # Encrypt the data using XOR with the key
    return xor_cipher(data_bytes, key)


def descifrar(data, key: int = 0x5A):
    ## Descifra un dato cifrado con XOR
    data_bytes = bytearray(data)
    return xor_cipher(data_bytes, key)
    

# This function takes a byte array and a key, and returns the XORed result.
def xor_cipher(data: bytes, key: int = 0x5A) -> bytes:
    return bytes(b ^ key for b in data)



def create_data_pkt(sq: int, data: list[str],EMMITER: bytes, EXPERCTED_RECEIVER: bytes) -> bytes:
    """
    Create a data packet with the given sequence number and data.
    """
    # Convert the data to bytes
    data_bytes = b''.join(item.encode('utf-8') for item in data)
    largo = len(data_bytes)  # Length of the data
    
    # Create the packet structure
    pkt = bytearray()
    pkt.append(HEADER[0])  # Header
    pkt.append(EMMITER[0])  # Emisor
    pkt.append(EXPERCTED_RECEIVER[0])  # Receptor esperado
    pkt.append(ord('p'))  # Tipo de paquete (using 'p' as representation for data packet)
    pkt.extend(sq.to_bytes(2, byteorder='big'))  # Secuencia
    pkt.extend(largo.to_bytes(4, byteorder='big'))  # Largo de los datos
    print(f"Emisor: {EMMITER[0]}, Receptor: {EXPERCTED_RECEIVER[0]}, Tipo: 'p', Secuencia: {sq}, Largo: {largo.to_bytes(4, byteorder='big')}")
    pkt.extend(data_bytes)  # Datos
    
    # Calculate CRC and append it to the packet
    crc = crc16_ibm(pkt[1:])  # Exclude header and footer for CRC calculation
    pkt.extend(crc.to_bytes(2, byteorder='big'))  # CRC

    
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
    pkt.extend((0).to_bytes(2, byteorder='big'))  # Largo de los datos (0 para ACK)
    
    # Calculate CRC and append it to the packet, paquete tiene  header, receptor, emisor, tipo, secuencia y largo
    ## entonces crc sobre todo el packete menos el header
    crc = crc16_ibm(pkt[1:])  # Exclude header and footer for CRC calculation
    pkt.extend(crc.to_bytes(2, byteorder='big'))  # CRC
    
    
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
    pkt.extend((0).to_bytes(2, byteorder='big'))  # Largo de los datos (0 para NACK)
    
    # Calculate CRC and append it to the packet
    crc = crc16_ibm(pkt[1:])  # Exclude header and footer for CRC calculation
    pkt.extend(crc.to_bytes(2, byteorder='big'))  # CRC
    
    return bytes(pkt)