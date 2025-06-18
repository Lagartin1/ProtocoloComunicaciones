# Receptor.py

DATA = set()

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

def xor_cipher(data: bytes, key: int = 0x5A) -> bytes:
  return bytes(b ^ key for b in data)

def validate_checksum(pkg: dict) -> bool:
  # Prepare data for checksum (excluding checksum and final fields)
  fields = [pkg["cabecera"], pkg["Emisor"], pkg["receptor"], pkg.get("logitud", 0), pkg.get("sq", 0)]
  if "data" in pkg:
    fields.extend(pkg["data"])
  data_bytes = bytes(fields)
  return crc16_ibm(data_bytes) == pkg["checksum"]

def process_package(pkg: dict) -> dict:
  """
  Process incoming package and return ACK or NACK.
  """
  if not validate_checksum(pkg):
    nack = createNack()
    nack["sq"] = pkg.get("sq", 0)
    return nack

  if pkg["type"] == "pkg":
    # Store data if not already present
    DATA.update(pkg["data"])
    ack = createAck()
    ack["sq"] = pkg.get("sq", 0)
    return ack
  else:
    # Ignore unknown types
    nack = createNack()
    nack["sq"] = pkg.get("sq", 0)
    return nack

def createAck():
  pkg = {
    "cabecera": 0xAA,
    "type": "ack",
    "Emisor": 2,
    "receptor": 1,
    "logitud": 2,
    "sq": 0,
    "checksum": 0,
    "final": 0xAA,
  }
  # Calculate checksum
  fields = [pkg["cabecera"], pkg["Emisor"], pkg["receptor"], pkg["logitud"], pkg["sq"]]
  pkg["checksum"] = crc16_ibm(bytes(fields))
  return pkg

def createNack():
  pkg = {
    "cabecera": 0xAA,
    "type": "nack",
    "Emisor": 2,
    "receptor": 1,
    "logitud": 2,
    "sq": 0,
    "checksum": 0,
    "final": 0xAA,
  }
  # Calculate checksum
  fields = [pkg["cabecera"], pkg["Emisor"], pkg["receptor"], pkg["logitud"], pkg["sq"]]
  pkg["checksum"] = crc16_ibm(bytes(fields))
  return pkg

# Example usage:
if __name__ == "__main__":
  # Simulate receiving a package
  incoming_pkg = {
    "cabecera": 0xAA,
    "type": "pkg",
    "Emisor": 1,
    "receptor": 2,
    "logitud": 5,
    "sq": 2,
    "data": [12, 15, 53, 40, 200],
    "checksum": 0,
    "final": 0xAA,
  }
  # Calculate checksum for incoming package
  fields = [incoming_pkg["cabecera"], incoming_pkg["Emisor"], incoming_pkg["receptor"], incoming_pkg["logitud"], incoming_pkg["sq"]]
  fields.extend(incoming_pkg["data"])
  incoming_pkg["checksum"] = crc16_ibm(bytes(fields))

  response = process_package(incoming_pkg)
  print("Response:", response)
  print("DATA stored:", DATA)