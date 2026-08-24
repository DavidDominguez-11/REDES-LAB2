"""Ejecutor reproducible de la matriz experimental especificada."""
from __future__ import annotations
import argparse, csv, socket
from pathlib import Path
from protocol import ALGO_CRC32, ALGO_SECDED, apply_noise, ascii_to_bits, pack_message, protect

SIZES = (16, 64, 256, 1024, 4096)
RATES = (0.0, 0.001, 0.01, 0.05)
ALGORITHMS = (("secded", ALGO_SECDED), ("crc32", ALGO_CRC32))

def transmit(packet: bytes, host: str, port: int) -> str:
    with socket.create_connection((host, port), timeout=15) as client:
        client.sendall(packet); client.shutdown(socket.SHUT_WR); return client.recv(4096).decode().strip()

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1"); parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--output", default="results/raw_results.csv"); parser.add_argument("--repetitions", type=int, default=30)
    args = parser.parse_args(); output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["algorithm", "characters", "noise_rate", "repetition", "seed", "payload_bits", "redundancy_bits", "overhead_ratio", "flipped_bits", "out_of_guarantee_words", "result"]
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader()
        for name, algorithm in ALGORITHMS:
            for size in SIZES:
                text = "A" * size; payload = ascii_to_bits(text); frame = protect(payload, algorithm)
                for rate in RATES:
                    for repetition in range(args.repetitions):
                        seed = (algorithm * 10_000_000) + (size * 10_000) + int(rate * 1_000_000) + repetition
                        noisy, flips = apply_noise(frame.link_bits, rate, seed); reply = transmit(pack_message(frame, noisy), args.host, args.port)
                        outside = sum(sum(a != b for a, b in zip(frame.link_bits[i:i+13], noisy[i:i+13])) >= 3 for i in range(0, len(frame.link_bits), 13)) if algorithm == ALGO_SECDED else 0
                        writer.writerow({"algorithm": name, "characters": size, "noise_rate": rate, "repetition": repetition, "seed": seed, "payload_bits": len(payload), "redundancy_bits": len(frame.link_bits)-len(payload), "overhead_ratio": (len(frame.link_bits)-len(payload))/len(payload), "flipped_bits": flips, "out_of_guarantee_words": outside, "result": reply.split(" ", 2)[1] if reply.startswith("OK ") else reply})
    print(f"Datos guardados en {output}")
if __name__ == "__main__": main()
