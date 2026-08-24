"""Orquesta la suite completa, con log explícito de que cubre cada archivo y su resultado."""
from __future__ import annotations
import subprocess, sys, time
from pathlib import Path

if sys.stdout.encoding is None or sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]

SUITES = [
    ("tests/test_protocol.py", [sys.executable, "tests/test_protocol.py"],
     "ASCII, CRC-32 (Python), SECDED (Python), encabezado v1 y Ruido -- a nivel de bits, sin red"),
    ("dist/protocol_test.js", ["node", "dist/protocol_test.js"],
     "CRC-32 (TypeScript) y SECDED (TypeScript): 13 correcciones simples + 78 dobles errores -- a nivel de bits, sin red"),
    ("tests/test_integration.py", [sys.executable, "tests/test_integration.py"],
     "SECDED y CRC-32 extremo a extremo contra el receptor Node real, por TCP en el puerto 5010"),
]

def main() -> None:
    print(f"Ejecutando {len(SUITES)} suites de prueba")
    for name, command, covers in SUITES:
        print(f"\n- INICIO {name}: {covers} -")
        start = time.monotonic()
        subprocess.run(command, cwd=ROOT, check=True)
        elapsed = time.monotonic() - start
        print(f"- FIN {name}: completado en {elapsed:.2f}s -")
    print("\nTodas las pruebas: OK")

if __name__ == "__main__": main()
