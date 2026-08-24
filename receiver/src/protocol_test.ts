import { ALGO_CRC32, ALGO_SECDED, bitsToAscii, crc32Iso, decodeCrc, decodeSecded } from "./protocol";

function check(condition: boolean, label: string, detail: string = ""): void {
  const suffix = detail ? ` -- ${detail}` : "";
  if (condition) {
    console.log(`[OK] ${label}${suffix}`);
  } else {
    console.log(`[FAIL] ${label}${suffix}`);
    throw new Error(`${label}: ${detail}`);
  }
}

console.log("protocol_test.ts: pruebas a nivel de bits (Enlace: SECDED, CRC-32), sin red");

const a = "01000001";
const secdedWord = "1000100100010";

check(bitsToAscii(a) === "A", "Presentacion: bitsToAscii decodifica '01000001' a 'A'");

const crcVector = crc32Iso("001100010011001000110011001101000011010100110110001101110011100000111001");
check(
  crcVector === 0xcbf43926,
  "Enlace/CRC-32: vector de referencia CRC-32/ISO-HDLC('123456789')",
  `esperado=0x${(0xcbf43926).toString(16)} obtenido=0x${crcVector.toString(16)}`
);

let crcShortAllOk = true;
for (const length of [1, 8, 31]) {
  const shortBits = "1".repeat(length), padded = shortBits.padEnd(32, "0");
  const crcFrame = padded + crc32Iso(padded).toString(2).padStart(32, "0");
  const ok = decodeCrc(crcFrame, length).bits === shortBits;
  if (!ok) check(false, `Enlace/CRC-32: carga corta de ${length} bit(s) se recupera tras padding+CRC`, "bits recuperados no coinciden con el original");
  crcShortAllOk = crcShortAllOk && ok;
}
check(crcShortAllOk, "Enlace/CRC-32: cargas cortas de 1, 8 y 31 bits se recuperan exactamente tras padding+CRC", "3/3 casos");

check(decodeSecded(secdedWord, 8).bits === a, "Enlace/SECDED (13,8): decodifica la palabra sin errores y recupera 'A'");

let correctionAllOk = true;
for (let index = 0; index < 13; index++) {
  const broken = secdedWord.slice(0, index) + (secdedWord[index] === "0" ? "1" : "0") + secdedWord.slice(index + 1);
  const ok = decodeSecded(broken, 8).bits === a;
  if (!ok) check(false, `Enlace/SECDED (13,8): corrige error simple en la posicion ${index + 1}`, "no se recupero 'A'");
  correctionAllOk = correctionAllOk && ok;
}
check(correctionAllOk, "Enlace/SECDED (13,8): corrige error simple en cada una de las 13 posiciones (paridad Hamming, datos y paridad global)", "13/13 posiciones");

let doubleAllOk = true;
let pairsChecked = 0;
for (let first = 0; first < 13; first++) {
  for (let second = first + 1; second < 13; second++) {
    pairsChecked++;
    const broken = secdedWord.split("");
    broken[first] = broken[first] === "0" ? "1" : "0";
    broken[second] = broken[second] === "0" ? "1" : "0";
    const ok = decodeSecded(broken.join(""), 8).status === "doble_error_detectado";
    if (!ok) check(false, `Enlace/SECDED (13,8): detecta doble error en posiciones ${first + 1},${second + 1}`, "no se clasifico como doble_error_detectado");
    doubleAllOk = doubleAllOk && ok;
  }
}
check(doubleAllOk, "Enlace/SECDED (13,8): detecta doble error en las 78 combinaciones de pares de posiciones (sin entregar la carga)", `${pairsChecked}/${pairsChecked} pares`);

check(ALGO_SECDED === 1 && ALGO_CRC32 === 2, "Transmision: identificadores de algoritmo del encabezado (SECDED=1, CRC-32=2)");

console.log("protocol_test.ts: TODO OK");
