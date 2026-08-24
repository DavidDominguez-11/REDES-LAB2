"""Genera gráficos SVG reproducibles sin dependencias externas a partir de resultados reales."""
from __future__ import annotations
import argparse, csv, html, sys
from collections import defaultdict
from pathlib import Path

if sys.stdout.encoding is None or sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

OUTCOME_LABELS = {
    "sin_error": "sin error",
    "corregido": "corregido",
    "doble_error_detectado": "doble error detectado",
    "crc_error": "CRC no coincide",
}
SECDED_OUTCOMES = ("sin_error", "corregido", "doble_error_detectado")
CRC_OUTCOMES = ("sin_error", "crc_error")

def normalize_outcome(result: str) -> str:
    return result[len("ERROR "):] if result.startswith("ERROR ") else result

def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))

def bar_chart(title: str, footer: str, rows: list[tuple[str, float, str]], max_value: float = 1.0) -> str:
    width, height = 900, max(180, 70 + 35 * len(rows))
    available = 580
    bars = []
    for index, (label, value, display) in enumerate(rows):
        y = 35 + index * 35
        bar_width = int((value / max_value) * available) if max_value > 0 else 0
        bars.append(
            f'<text x="10" y="{y + 15}">{html.escape(label)}</text>'
            f'<rect x="260" y="{y}" width="{bar_width}" height="20" fill="#2674b8"/>'
            f'<text x="850" y="{y + 15}">{html.escape(display)}</text>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
        f'<style>text{{font:14px sans-serif}}</style>'
        f'<text x="10" y="20">{html.escape(title)}</text>'
        f'<text x="10" y="{height - 8}">{html.escape(footer)}</text>'
        f'{"".join(bars)}</svg>'
    )

def success_by_rate(rows: list[dict[str, str]], source: str) -> str:
    groups: dict[tuple[str, str], list[bool]] = defaultdict(list)
    for row in rows:
        groups[(row["algorithm"], row["noise_rate"])].append(row["result"] in {"sin_error", "corregido"})
    chart_rows = []
    for (algo, rate), values in sorted(groups.items()):
        success = sum(values) / len(values)
        chart_rows.append((f"{algo} p={rate}", success, f"{success:.1%} ({sum(values)}/{len(values)})"))
    footer = f"Fuente: {source}; éxito = sin_error o corregido, agregado sobre todos los tamaños y repeticiones"
    return bar_chart("Tasa de entrega correcta por algoritmo y tasa de ruido", footer, chart_rows)

def success_by_size(rows: list[dict[str, str]], source: str) -> str:
    groups: dict[tuple[str, str], list[bool]] = defaultdict(list)
    for row in rows:
        if row["noise_rate"] == "0.0":
            continue
        groups[(row["algorithm"], int(row["characters"]))].append(row["result"] in {"sin_error", "corregido"})
    chart_rows = []
    for (algo, size), values in sorted(groups.items(), key=lambda item: (item[0][0], item[0][1])):
        success = sum(values) / len(values)
        chart_rows.append((f"{algo} n={size}", success, f"{success:.1%} ({sum(values)}/{len(values)})"))
    footer = f"Fuente: {source}; éxito = sin_error o corregido, agregado sobre tasas de ruido > 0 y repeticiones"
    return bar_chart("Tolerancia al error por algoritmo y tamaño de mensaje", footer, chart_rows)

def overhead_by_size(rows: list[dict[str, str]], source: str) -> str:
    groups: dict[tuple[str, int], list[float]] = defaultdict(list)
    for row in rows:
        groups[(row["algorithm"], int(row["characters"]))].append(float(row["overhead_ratio"]))
    chart_rows = []
    max_value = max((sum(v) / len(v) for v in groups.values()), default=1.0)
    for (algo, size), values in sorted(groups.items(), key=lambda item: (item[0][0], item[0][1])):
        overhead = sum(values) / len(values)
        chart_rows.append((f"{algo} n={size}", overhead, f"{overhead:.1%}"))
    footer = f"Fuente: {source}; overhead = bits de redundancia / bits de carga, promedio por tamaño"
    return bar_chart("Overhead por algoritmo y tamaño de mensaje", footer, chart_rows, max_value=max_value)

def outcome_breakdown(rows: list[dict[str, str]], source: str) -> str:
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in rows:
        groups[(row["algorithm"], row["noise_rate"])].append(normalize_outcome(row["result"]))
    chart_rows = []
    for (algo, rate), outcomes in sorted(groups.items()):
        applicable = SECDED_OUTCOMES if algo == "secded" else CRC_OUTCOMES
        total = len(outcomes)
        for outcome in applicable:
            count = outcomes.count(outcome)
            fraction = count / total if total else 0.0
            label = f"{algo} p={rate} [{OUTCOME_LABELS.get(outcome, outcome)}]"
            chart_rows.append((label, fraction, f"{fraction:.1%} ({count}/{total})"))
    footer = f"Fuente: {source}; desglose de resultado por algoritmo y tasa de ruido"
    return bar_chart("Detección y corrección por algoritmo y tasa de ruido", footer, chart_rows)

def main() -> None:
    parser = argparse.ArgumentParser(description="Genera gráficas SVG desde la campaña experimental")
    parser.add_argument("--input", default="results/raw_results.csv")
    parser.add_argument("--output-dir", default="results")
    args = parser.parse_args()

    input_path = Path(args.input)
    rows = load_rows(input_path)
    if not rows:
        raise SystemExit(f"{input_path} no contiene registros; ejecuta sender/experiment.py primero")
    source = html.escape(input_path.as_posix())

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    charts = {
        "success_by_rate.svg": success_by_rate(rows, source),
        "success_by_size.svg": success_by_size(rows, source),
        "overhead_by_size.svg": overhead_by_size(rows, source),
        "outcome_breakdown.svg": outcome_breakdown(rows, source),
    }
    for filename, svg in charts.items():
        (output_dir / filename).write_text(svg, encoding="utf-8")
        print(f"Gráfica guardada en {output_dir / filename}")

if __name__ == "__main__": main()
