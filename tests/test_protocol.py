"""Pruebas unitarias de protocolo (Presentación, Enlace, encabezado, Ruido), con log explícito por caso."""
from __future__ import annotations
import struct
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sender"))
from protocol import ALGO_CRC32, ALGO_SECDED, HEADER_BYTES, apply_noise, ascii_to_bits, crc32_iso, encode_crc, encode_secded, encode_secded_byte, pack_message, protect

if sys.stdout.encoding is None or sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

def check(condition: bool, label: str, detail: str = "") -> None:
    line = f"[OK] {label}" if condition else f"[FAIL] {label}"
    if detail:
        line += f" -- {detail}"
    print(line)
    if not condition:
        raise AssertionError(f"{label}: {detail}")

def flip(bits: str, *positions: int) -> str:
    output = list(bits)
    for position in positions: output[position] = "1" if output[position] == "0" else "0"
    return "".join(output)

def main() -> None:
    print("test_protocol.py: pruebas a nivel de bits, sin red")

    bits = ascii_to_bits("A")
    check(bits == "01000001", "Presentacion: 'A' se codifica como ASCII binario de 8 bits", f"obtenido={bits}")

    crc_vector = crc32_iso(ascii_to_bits("123456789"))
    check(crc_vector == 0xCBF43926, "Enlace/CRC-32: vector de referencia CRC-32/ISO-HDLC('123456789')",
          f"esperado=0x{0xCBF43926:08X} obtenido=0x{crc_vector:08X}")

    secded = encode_secded(bits)
    check(secded == "1000100100010", "Enlace/SECDED (13,8): codificacion de 'A' (paridad Hamming en 1,2,4,8 + paridad global en 13)",
          f"obtenido={secded}")

    crc = encode_crc(bits)
    check(len(crc) == 64, "Enlace/CRC-32: trama de 'A' = 32 bits de carga con padding + 32 bits de CRC", f"len={len(crc)}")

    frame = protect(bits, ALGO_SECDED)
    packet = pack_message(frame, frame.link_bits)
    check(len(packet) == HEADER_BYTES + 2, "Transmision: empaquetado SECDED = encabezado (10B) + trama de 13 bits (2B)",
          f"len(packet)={len(packet)}")
    header_fields = struct.unpack("!BBII", packet[:HEADER_BYTES])
    check(header_fields == (1, ALGO_SECDED, 8, 13), "Transmision: encabezado v1 (version=1, algoritmo=SECDED, bits_carga=8, bits_trama=13)",
          f"obtenido={header_fields}")

    unchanged, count = apply_noise(frame.link_bits, 0, 12)
    check(unchanged == frame.link_bits and count == 0, "Ruido: probabilidad p=0 no altera la trama de Enlace (SECDED)", f"inversiones={count}")

    noisy, count = apply_noise(frame.link_bits, 1, 12)
    check(noisy == flip(frame.link_bits, *range(len(frame.link_bits))) and count == len(frame.link_bits),
          "Ruido: probabilidad p=1 invierte todos los bits de la trama de Enlace (SECDED)", f"inversiones={count}/{len(frame.link_bits)}")

    check(protect(bits, ALGO_CRC32).algorithm == ALGO_CRC32, "Enlace: protect() con algoritmo=CRC-32 etiqueta la trama como CRC-32")

    for length in (1, 8, 31):
        crc_short = encode_crc("1" * length)
        check(len(crc_short) == 64, f"Enlace/CRC-32: carga corta de {length} bit(s) se rellena con ceros a 32 bits antes del CRC",
              f"len(trama)={len(crc_short)}")

    try:
        ascii_to_bits("á")
        check(False, "Presentacion: rechaza caracteres no ASCII ('á')", "no se lanzo ValueError")
    except ValueError:
        check(True, "Presentacion: rechaza caracteres no ASCII ('á')", "ValueError lanzado correctamente")

    try:
        apply_noise("0", -0.1)
        check(False, "Ruido: rechaza tasa fuera de [0,1] (p=-0.1)", "no se lanzo ValueError")
    except ValueError:
        check(True, "Ruido: rechaza tasa fuera de [0,1] (p=-0.1)", "ValueError lanzado correctamente")

    print("test_protocol.py: TODO OK")

if __name__ == "__main__": main()
