
EXPERCTED_HEADER = b'\x01'

HEADER = b'\x01'  # header byte
FOOTER = b'\xAA'  # Footer byte 

EMITER = b'\x01'  # Emisor byte

EXPERCTED_RECEIVER = b'\x02'

def parse_pkt(pkt):
    if len(pkt) < 3:
        return None, "Packet too short" 

    # Extract the first 4 bytes as an integer
    try:
        if EXPERCTED_HEADER != pkt[:1]:  # 
            return None, "Invalid header"
        value = int.from_bytes(pkt[2:3], byteorder='big')
        if EXPERCTED_RECEIVER != pkt[3:4]:
            return None, "Invalid receiver"
        pkt_parsed = {}
        pkt_tipo = pkt[4:5]
        ### Solo RECEPTOR
        if  pkt_tipo == 'pkt' :
            pkt_parsed['tipo'] = pkt_tipo
            pkt_parsed['sq'] = int.from_bytes(pkt[5:7], byteorder='big')
            pkt_parsed['largo'] = int.from_bytes(pkt[7:9], byteorder='big')
            pkt_parsed['data'] = pkt[9:9 + pkt_parsed['largo']]
            pkt_parsed['crc'] = pkt[9 + pkt_parsed['largo']:11 + pkt_parsed['largo']]
        #######
        #### SOLO EMISOR
        elif pkt_tipo == 'ack':
            pkt_parsed['tipo'] = pkt_tipo
            pkt_parsed['sq'] = int.from_bytes(pkt[5:7], byteorder='big')
            pkt_parsed['crc'] = pkt[7:9]
        elif pkt_tipo == 'nak':
            pkt_parsed['tipo'] = pkt_tipo
            pkt_parsed['sq'] = int.from_bytes(pkt[5:7], byteorder='big')
            pkt_parsed['crc'] = pkt[7:9]
        else:
            return None, "Unknown packet type"
        #######
        return pkt_parsed, None
         
    except ValueError as e:
        return None, f"Error parsing packet: {e}"

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


# This function takes a byte array and a key, and returns the XORed result.
def xor_cipher(data: bytes, key: int = 0x5A) -> bytes:
    return bytes(b ^ key for b in data)




def create_pkt(tipo, sq, data):
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
        
    