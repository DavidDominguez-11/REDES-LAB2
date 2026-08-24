"""Pruebas de integracion TCP extremo a extremo contra el receptor Node real, con log explícito por caso."""
from __future__ import annotations
import socket, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sender"))
from protocol import ALGO_CRC32, ALGO_SECDED, apply_noise, ascii_to_bits, pack_message, protect

if sys.stdout.encoding is None or sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

def check(condition: bool, label: str, detail: str = "") -> None:
    line = f"[OK] {label}" if condition else f"[FAIL] {label}"
    if detail:
        line += f" -- {detail}"
    print(line)
    if not condition:
        raise AssertionError(f"{label}: {detail}")

def send(packet: bytes, fragment: bool = False) -> str:
    with socket.create_connection(("127.0.0.1", 5010), timeout=10) as client:
        if fragment:
            client.sendall(packet[:4]); client.sendall(packet[4:])
        else: client.sendall(packet)
        client.shutdown(socket.SHUT_WR); return client.recv(4096).decode().strip()

def main() -> None:
    print("test_integration.py: pruebas TCP extremo a extremo contra el receptor Node real (puerto 5010)")
    process = subprocess.Popen(["node", "dist/server.js", "5010"], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        time.sleep(0.4)

        secded = protect(ascii_to_bits("A"), ALGO_SECDED)
        reply = send(pack_message(secded, secded.link_bits), True)
        check(reply == "OK sin_error A",
              "algoritmo=SECDED, ruido=0, trama fragmentada en 2 envios TCP -> se espera sin_error",
              f"respuesta={reply!r}")

        one_error, flips = apply_noise(secded.link_bits, 0.1, 4)
        check(flips == 1, "Ruido: seed=4, p=0.1 sobre trama SECDED('A') produce exactamente 1 inversion", f"inversiones={flips}")
        reply = send(pack_message(secded, one_error))
        check(reply == "OK corregido A",
              "algoritmo=SECDED con 1 bit invertido -> se espera que el receptor corrija y recupere 'A'",
              f"respuesta={reply!r}")

        two_error = "".join("1" if index in (0, 1) and bit == "0" else "0" if index in (0, 1) else bit for index, bit in enumerate(secded.link_bits))
        reply = send(pack_message(secded, two_error))
        check("doble_error_detectado" in reply,
              "algoritmo=SECDED con 2 bits invertidos (posiciones 1,2) -> se espera doble_error_detectado, sin entrega",
              f"respuesta={reply!r}")

        crc = protect(ascii_to_bits("Hola"), ALGO_CRC32)
        reply = send(pack_message(crc, crc.link_bits))
        check(reply == "OK sin_error Hola",
              "algoritmo=CRC-32, ruido=0 -> se espera sin_error",
              f"respuesta={reply!r}")

        corrupted = ("1" if crc.link_bits[0] == "0" else "0") + crc.link_bits[1:]
        reply = send(pack_message(crc, corrupted))
        check("crc_error" in reply,
              "algoritmo=CRC-32 con 1 bit de dato invertido -> se espera crc_error, sin entrega",
              f"respuesta={reply!r}")

        invalid = bytearray(pack_message(crc, crc.link_bits)); invalid[0] = 2
        reply = send(bytes(invalid))
        check("versión no compatible" in reply,
              "Transmision: encabezado con version desconocida (2) -> se espera rechazo por version no compatible",
              f"respuesta={reply!r}")

        print("test_integration.py: TODO OK")
    finally:
        process.terminate(); process.wait(timeout=5)
if __name__ == "__main__": main()
