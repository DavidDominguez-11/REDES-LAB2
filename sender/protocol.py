"""Capas Presentación, Enlace, Ruido y el contrato TCP v1 del Laboratorio 2."""
from __future__ import annotations

import binascii
import struct
from dataclasses import dataclass

VERSION = 1
ALGO_SECDED = 1
ALGO_CRC32 = 2
HEADER_FORMAT = "!BBII"
HEADER_BYTES = struct.calcsize(HEADER_FORMAT)
DATA_POSITIONS = (3, 5, 6, 7, 9, 10, 11, 12)
PARITY_POSITIONS = (1, 2, 4, 8)

@dataclass(frozen=True)
class Frame:
    algorithm: int
    original_bits: int
    link_bits: str

def ascii_to_bits(text: str) -> str:
    try:
        data = text.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError("el mensaje debe usar ASCII") from exc
    return "".join(f"{byte:08b}" for byte in data)

def bits_to_bytes(bits: str) -> bytes:
    padded = bits + "0" * ((-len(bits)) % 8)
    return bytes(int(padded[index:index + 8], 2) for index in range(0, len(padded), 8))

def bytes_to_bits(data: bytes, bit_length: int | None = None) -> str:
    bits = "".join(f"{byte:08b}" for byte in data)
    return bits if bit_length is None else bits[:bit_length]

def encode_secded_byte(data: str) -> str:
    if len(data) != 8 or set(data) - {"0", "1"}:
        raise ValueError("SECDED (13,8) requiere ocho bits")
    word = [0] * 14
    for position, bit in zip(DATA_POSITIONS, data): word[position] = int(bit)
    for parity in PARITY_POSITIONS:
        value = 0
        for position in range(1, 13):
            if position != parity and position & parity: value ^= word[position]
        word[parity] = value
    word[13] = sum(word[1:13]) % 2
    return "".join(map(str, word[1:14]))

def encode_secded(bits: str) -> str:
    if len(bits) % 8: raise ValueError("la carga SECDED debe ser ASCII de ocho bits")
    return "".join(encode_secded_byte(bits[index:index + 8]) for index in range(0, len(bits), 8))

def crc32_iso(bits: str) -> int:
    if len(bits) % 8: raise ValueError("CRC-32/ISO-HDLC requiere bytes completos")
    return binascii.crc32(bits_to_bytes(bits)) & 0xFFFFFFFF

def encode_crc(bits: str) -> str:
    padded = bits if len(bits) >= 32 else bits + "0" * (32 - len(bits))
    return padded + f"{crc32_iso(padded):032b}"
