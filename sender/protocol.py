"""Capas Presentación, Enlace, Ruido y el contrato TCP v1 del Laboratorio 2."""
from __future__ import annotations

import struct
from dataclasses import dataclass

VERSION = 1
ALGO_SECDED = 1
ALGO_CRC32 = 2
HEADER_FORMAT = "!BBII"
HEADER_BYTES = struct.calcsize(HEADER_FORMAT)

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
