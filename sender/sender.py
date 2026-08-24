"""Aplicación emisora: solicita el mensaje, algoritmo y tasa de ruido."""
from __future__ import annotations
import argparse
import socket
import sys
from protocol import ALGO_CRC32, ALGO_SECDED, apply_noise, ascii_to_bits, pack_message, protect

if sys.stdout.encoding is None or sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

ALGO_NAMES = {
    ALGO_SECDED: "SECDED (13,8) Hamming extendido - corrección de errores",
    ALGO_CRC32: "CRC-32/ISO-HDLC - detección de errores",
}
STATUS_EXPLANATIONS = {
    "sin_error": "el receptor no detectó errores; el mensaje llegó íntegro",
    "corregido": "el receptor detectó y corrigió automáticamente un error simple de bit (SECDED)",
    "doble_error_detectado": "el receptor detectó dos bits alterados en una palabra SECDED y NO pudo recuperar el mensaje",
    "crc_error": "el CRC-32 recalculado por el receptor no coincide con el enviado; el mensaje llegó corrupto y no se intenta corregir",
    "encabezado incompleto": "la trama recibida no traía los 10 bytes de encabezado esperados",
    "versión no compatible": "el receptor no reconoce la versión de protocolo enviada",
    "longitud de trama inválida": "el número de bytes recibidos no coincide con la longitud declarada en el encabezado",
    "algoritmo desconocido": "el identificador de algoritmo en el encabezado no es SECDED ni CRC-32",
}

def parse_algorithm(value: str) -> int:
    names = {"secded": ALGO_SECDED, "crc32": ALGO_CRC32}
    if value.lower() not in names: raise argparse.ArgumentTypeError("algoritmo: secded o crc32")
    return names[value.lower()]

def explain_reply(reply: str) -> str:
    if reply.startswith("OK "):
        parts = reply.split(" ", 2)
        status = parts[1] if len(parts) > 1 else ""
        text = parts[2] if len(parts) > 2 else ""
        explanation = STATUS_EXPLANATIONS.get(status, "respuesta reconocida pero sin explicación registrada")
        return f'resultado: {status} - {explanation}\nmensaje mostrado al receptor: "{text}"'
    status = reply[len("ERROR "):] if reply.startswith("ERROR ") else reply
    explanation = STATUS_EXPLANATIONS.get(status, "el receptor reportó un error no clasificado; ver respuesta cruda")
    return f"resultado: ERROR ({status}) - {explanation}"

def main() -> None:
    parser = argparse.ArgumentParser(description="Emisor TCP con SECDED o CRC-32/ISO-HDLC")
    parser.add_argument("message", nargs="?", help="texto ASCII a enviar")
    parser.add_argument("--algorithm", type=parse_algorithm, help="secded o crc32")
    parser.add_argument("--noise", type=float, help="tasa decimal [0,1]")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    message = args.message if args.message is not None else input("Mensaje ASCII: ")
    algorithm = args.algorithm if args.algorithm is not None else parse_algorithm(input("Algoritmo (secded/crc32): "))
    noise = args.noise if args.noise is not None else float(input("Tasa de ruido [0,1]: "))
    bits = ascii_to_bits(message); frame = protect(bits, algorithm); noisy, flips = apply_noise(frame.link_bits, noise, args.seed)
    with socket.create_connection((args.host, args.port)) as client:
        client.sendall(pack_message(frame, noisy)); client.shutdown(socket.SHUT_WR); reply = client.recv(4096).decode("utf-8").strip()
    print(f"algoritmo usado: {ALGO_NAMES[algorithm]}")
    print(f"tasa de ruido solicitada: {noise}")
    print(f"bits_carga={len(bits)} bits_trama={len(frame.link_bits)} inversiones={flips}")
    print(explain_reply(reply))
    print(f"respuesta cruda del receptor: {reply}")

if __name__ == "__main__": main()
