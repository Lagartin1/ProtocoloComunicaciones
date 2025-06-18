


""" 
    opciones para canal:
    -web socket
    -archivos compartidos
    -pipeline
    -sockets con docker y pumba para jitter,perdida de paquetes y latencia
"""


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


DATA = {12,15,53,40,200}
#XOR Cipher for data encryption
# This function takes a byte array and a key, and returns the XORed result.
def xor_cipher(data: bytes, key: int = 0x5A) -> bytes:
    return bytes(b ^ key for b in data)

## ejemplos
def creaPkgt():
    """
    Create a package with the data.
    """
    pkg = {
        "cabecera": 0xAA,
        "type": "pkg",
        "Emisor":01,
        "receptor": 02,
        "logitud" : 2,
        "sq": 2,
        "data": DATA,
        "checksum": 0,
        "final": 0xAA,
    }
    return pkg

def createAck():
    """
    Create a package with the data.
    """
    pkg = {
        "cabecera": 0xAA,
        "type": "ack",
        "Emisor":01,
        "receptor": 02,
        "logitud" : 2,
        "sq": 2, # secuencuia de paquete acpetado
        "checksum": 0,
        "final": 0xAA,
    }
    return pkg

def createNack():
    """
    Create a package with the data.
    """
    pkg = {
        "cabecera": 0xAA,
        "type": "nack",
        "Emisor":01,
        "receptor": 02,
        "logitud" : 2,
        "sq": 2, # secuencia paquete no aceptado
        "checksum": 0,
        "final": 0xAA,
    }
    return pkg

## enviar paquete




## envio  de imagen , o un libro en txt


def main():
    data = {1,1,1,1,1,1,1,1,1,1,1} 
       
    
    
if __name__ == "__main__":
    main()