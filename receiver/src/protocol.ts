export const VERSION = 1;
export const HEADER_BYTES = 10;
export const ALGO_SECDED = 1;
export const ALGO_CRC32 = 2;

export interface Header { version: number; algorithm: number; originalBits: number; frameBits: number; }
export type DecodeStatus = "sin_error" | "corregido" | "doble_error_detectado" | "crc_error";

export function unpackHeader(data: Uint8Array): Header {
  if (data.length !== HEADER_BYTES) throw new Error("encabezado incompleto");
  return { version: data[0], algorithm: data[1], originalBits: readU32(data, 2), frameBits: readU32(data, 6) };
}
function readU32(data: Uint8Array, offset: number): number {
  return (((data[offset] * 0x1000000) + (data[offset + 1] << 16) + (data[offset + 2] << 8) + data[offset + 3]) >>> 0);
}
export function bytesToBits(data: Uint8Array, bitLength: number): string {
  let result = "";
  for (const byte of data) result += byte.toString(2).padStart(8, "0");
  return result.slice(0, bitLength);
}
export function bitsToBytes(bits: string): Uint8Array {
  const padded = bits.padEnd(Math.ceil(bits.length / 8) * 8, "0");
  const result = new Uint8Array(padded.length / 8);
  for (let i = 0; i < result.length; i++) result[i] = parseInt(padded.slice(i * 8, i * 8 + 8), 2);
  return result;
}
export function bitsToAscii(bits: string): string {
  if (bits.length % 8 !== 0) throw new Error("longitud ASCII inválida");
  let text = "";
  for (let i = 0; i < bits.length; i += 8) text += String.fromCharCode(parseInt(bits.slice(i, i + 8), 2));
  return text;
}
