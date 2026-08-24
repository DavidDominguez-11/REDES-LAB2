# Laboratorio 2 — Control de errores

Implementación por capas de un emisor **Python** y un receptor **TypeScript sobre Node.js** que se comunican por TCP. `lab2.md` es la fuente académica inmutable del proyecto.

## Requisitos

- Python 3.11 o posterior.
- Node.js 20 o posterior. TypeScript se instala como dependencia de desarrollo con `npm install` (no requiere instalación global de `tsc`).

## Estructura

- `sender/`: emisor Python, protocolo, experimentos y generación de gráficas SVG.
- `receiver/src/`: receptor `node:net` y protocolo TypeScript.
- `tests/`: pruebas unitarias e integración TCP.
- `results/`: CSV experimentales y gráficas SVG generadas. El informe formal del laboratorio se prepara aparte, fuera de este repositorio de código.

## Compilación y ejecución

```powershell
npm install
npm run build
node dist/server.js 5000
python sender/sender.py "Hola" --algorithm secded --noise 0 --port 5000
python sender/sender.py "Hola" --algorithm crc32 --noise 0.001 --seed 7 --port 5000
```

El receptor permanece escuchando y procesa conexiones sucesivas. El emisor acepta `secded` o `crc32`; la tasa de ruido es decimal e inclusiva entre 0 y 1. Tanto el emisor como el receptor imprimen, por cada envío, el algoritmo usado y una explicación del resultado (sin error, corregido, doble error detectado, o CRC no coincide), no solo la respuesta cruda.

## Protocolo TCP v1

Cada conexión lleva un encabezado no ruidoso de 10 bytes, big-endian: versión `u8=1`, algoritmo `u8` (`1=SECDED_13_8`, `2=CRC32_ISO_HDLC`), longitud original `u32` en bits y longitud de trama de Enlace `u32` en bits. Después se envía la trama empaquetada. Ruido afecta únicamente esa trama, incluidos datos, padding y redundancia.

SECDED usa bloques (13,8), con paridad Hamming en posiciones 1, 2, 4 y 8 y paridad global en 13. Corrige un error, detecta dos y no garantiza clasificación fiable con tres o más errores por bloque. CRC utiliza CRC-32/ISO-HDLC (`0x04C11DB7`, init/xorout `0xFFFFFFFF`, refin/refout verdaderos). Cargas menores de 32 bits se completan con ceros finales; la longitud original permite restaurarlas.

## Pruebas

```powershell
npm install
npm run build
python tests/run_all.py
```

Las pruebas cubren ASCII, encabezado, ruido, CRC, SECDED (incluidas las 78 parejas de errores), framing fragmentado, encabezado inválido y conexiones consecutivas. Cada caso imprime una línea `[OK]`/`[FAIL]` explícita con el algoritmo/capa involucrado y el valor esperado vs. obtenido (no solo un "OK" final), y `tests/run_all.py` marca el inicio/fin y duración de cada una de las 3 suites (`test_protocol.py`, `dist/protocol_test.js`, `test_integration.py`).

## Experimentos y gráficas

Con el receptor activo en otro terminal:

```powershell
python sender/experiment.py --output results/raw_results.csv
python sender/generate_graphs.py --input results/raw_results.csv --output-dir results
```

La campaña usa 2 algoritmos × 5 tamaños (16, 64, 256, 1024, 4096 caracteres) × 4 tasas (0, 0.001, 0.01, 0.05) × 30 repeticiones = 1,200 registros. Para una comprobación rápida puede pasarse `--repetitions 1`.

`generate_graphs.py` produce cuatro gráficas SVG en `results/`, cada una derivada directamente de `raw_results.csv`:

- `success_by_rate.svg`: tasa de entrega correcta por algoritmo y tasa de ruido.
- `success_by_size.svg`: tasa de entrega correcta por algoritmo y tamaño de mensaje (tasas de ruido > 0).
- `overhead_by_size.svg`: overhead promedio por algoritmo y tamaño de mensaje.
- `outcome_breakdown.svg`: desglose de `sin_error`/`corregido`/`doble_error_detectado`/`crc_error` por algoritmo y tasa de ruido.
