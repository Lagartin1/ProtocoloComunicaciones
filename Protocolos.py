
HEADER = b'\x01'  # header byte
FOOTER = b'\xAA'  # Footer byte 


def parse_pkt(pkt, EXPERCTED_RECEIVER):
    """
    Parse a packet and return its components.
    """
    if len(pkt) < 7:
        return None, "Packet too short"
    
    if pkt[0] != HEADER[0] or pkt[-1] != FOOTER[0]:
        return None, "Invalid header or footer"

    emisor = pkt[1]
    receptor = pkt[2]
    tipo = chr(pkt[3])
    sq = int.from_bytes(pkt[4:6], byteorder='big')
    largo = int.from_bytes(pkt[6:8], byteorder='big')
    
    if len(pkt) < 8 + largo + 2:
        return None, "Packet length mismatch"
    
    data = pkt[8:8 + largo]
    crc_received = int.from_bytes(pkt[-3:-1], byteorder='big')
    
    # Calculate CRC
    crc_calculated = crc16_ibm(pkt[1:-2])
    
    if crc_received != crc_calculated:
        return None, "CRC mismatch"
    
    if receptor != EXPERCTED_RECEIVER:
        return None, "Unexpected receiver"
    
    return {
        'emisor': emisor,
        'receptor': receptor,
        'tipo': tipo,
        'sq': sq,
        'largo': largo,
        'data': data
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


def create_pkt(tipo, sq, data, HEADER=HEADER, FOOTER=FOOTER, EMITER=b'\x01', EXPERCTED_RECEIVER=b'\x02'):
    """
    Create a package with the data.
    """
    
    if tipo == 'pkt':
        largo = len(data)
        pkt = bytearray()
        pkt.append(HEADER[0])
        pkt.append(EMITER[0])
        pkt.append(EXPERCTED_RECEIVER[0])
        pkt.append(ord(tipo[0]))
        pkt.extend(sq.to_bytes(2, byteorder='big'))
        pkt.extend(largo.to_bytes(2, byteorder='big'))
        pkt.extend(data) 
        crc = crc16_ibm(pkt[1:])
        pkt.extend(crc.to_bytes(2, byteorder='big'))
        pkt.append(FOOTER[0])
    elif tipo in ['ack', 'nak']:
        pkt = bytearray()
        pkt.append(HEADER[0])
        pkt.append(EMITER[0])
        pkt.append(EXPERCTED_RECEIVER[0])
        pkt.append(ord(tipo[0]))
        pkt.extend(sq.to_bytes(2, byteorder='big'))
        crc = crc16_ibm(pkt[1:])
        pkt.extend(crc.to_bytes(2, byteorder='big'))
        pkt.append(FOOTER[0])
    else:
        raise ValueError("Unknown packet type")
        
    
def create_ack(sq, EMITER=b'\x01', EXPERCTED_RECEIVER=b'\x02'):
    """
    Create an ACK packet.
    """
    return create_pkt('ack', sq, b'', EMITER, EXPERCTED_RECEIVER)

def create_nak(sq, EMITER=b'\x01', EXPERCTED_RECEIVER=b'\x02'):
    """
    Create a NAK packet.
    """
    return create_pkt('nak', sq, b'', EMITER, EXPERCTED_RECEIVER)

def create_data_pkt(sq, data, EMITER=b'\x01', EXPERCTED_RECEIVER=b'\x02'):
    """
    Create a data packet.
    """
    return create_pkt('pkt', sq, data, EMITER, EXPERCTED_RECEIVER)