import { createServer, Socket } from "node:net";
import { ALGO_CRC32, ALGO_SECDED, bitsToAscii, bytesToBits, decodeCrc, decodeSecded, DecodeStatus, HEADER_BYTES, Header, unpackHeader, VERSION } from "./protocol";

const ALGO_NAMES: Record<number, string> = { [ALGO_SECDED]: "SECDED (13,8) Hamming extendido — corrección de errores", [ALGO_CRC32]: "CRC-32/ISO-HDLC — detección de errores" };

function describeOutcome(status: DecodeStatus, corrected: number, doubles: number, text: string | undefined): string {
  switch (status) {
    case "sin_error": return `sin errores detectados; mensaje íntegro: "${text}"`;
    case "corregido": return `error simple corregido (${corrected} bit(s) de paridad/dato invertidos); mensaje recuperado: "${text}"`;
    case "doble_error_detectado": return `doble error detectado en ${doubles} palabra(s) SECDED; mensaje NO recuperable, se descarta`;
    case "crc_error": return "CRC-32 recalculado no coincide con el recibido; mensaje corrupto, no se intenta corrección";
    default: return `estado desconocido (${status})`;
  }
}

function processMessage(data: Uint8Array): { reply: string; log: string } {
  if (data.length < HEADER_BYTES) return { reply: "ERROR encabezado incompleto", log: `encabezado incompleto: se recibieron ${data.length} de ${HEADER_BYTES} bytes esperados` };
  let header: Header;
  try { header = unpackHeader(data.slice(0, HEADER_BYTES)); } catch (error) { return { reply: `ERROR ${String(error)}`, log: `encabezado inválido: ${String(error)}` }; }
  const algoName = ALGO_NAMES[header.algorithm] ?? `desconocido (id=${header.algorithm})`;
  if (header.version !== VERSION) return { reply: "ERROR versión no compatible", log: `versión de protocolo no compatible: recibida=${header.version}, esperada=${VERSION}` };
  const frameBytes = Math.ceil(header.frameBits / 8);
  if (data.length !== HEADER_BYTES + frameBytes) return { reply: "ERROR longitud de trama inválida", log: `longitud de trama inválida: esperados ${HEADER_BYTES + frameBytes} bytes, recibidos ${data.length}` };
  const frame = bytesToBits(data.slice(HEADER_BYTES), header.frameBits);
  const prefix = `algoritmo=${algoName} bits_carga=${header.originalBits} bits_trama=${header.frameBits}`;
  try {
    if (header.algorithm === ALGO_SECDED) {
      const decoded = decodeSecded(frame, header.originalBits);
      const text = decoded.bits ? bitsToAscii(decoded.bits) : undefined;
      return { reply: decoded.bits ? `OK ${decoded.status} ${text}` : `ERROR ${decoded.status}`, log: `${prefix} -> ${describeOutcome(decoded.status, decoded.corrected, decoded.doubles, text)}` };
    }
    if (header.algorithm === ALGO_CRC32) {
      const decoded = decodeCrc(frame, header.originalBits);
      const text = decoded.bits ? bitsToAscii(decoded.bits) : undefined;
      return { reply: decoded.bits ? `OK ${decoded.status} ${text}` : `ERROR ${decoded.status}`, log: `${prefix} -> ${describeOutcome(decoded.status, 0, 0, text)}` };
    }
    return { reply: "ERROR algoritmo desconocido", log: `algoritmo desconocido: id=${header.algorithm}` };
  } catch (error) { return { reply: `ERROR ${String(error)}`, log: `${prefix} -> error al decodificar: ${String(error)}` }; }
}

const port = Number(process.argv[2] ?? "5000");
const server = createServer((socket: Socket) => {
  const chunks: number[] = [];
  socket.on("data", (part: unknown) => { for (const value of part as Uint8Array) chunks.push(value); });
  socket.on("end", () => { const { reply, log } = processMessage(new Uint8Array(chunks)); console.log(log); socket.write(new TextEncoder().encode(reply + "\n")); socket.end(); });
  socket.on("error", (error: unknown) => console.error(`socket error: ${String(error)}`));
});
server.on("error", (error: unknown) => { console.error(`server error: ${String(error)}`); process.exitCode = 1; });
server.listen(port, "0.0.0.0", () => console.log(`Receptor escuchando en puerto ${port}`));
