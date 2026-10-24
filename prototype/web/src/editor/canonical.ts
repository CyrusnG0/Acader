// Canonical JSON and doc_hash, byte-compatible with engine/events/canonical.py:
// UTF-8, sorted keys, no whitespace, no floats. The client sends doc_hash with
// each checkpoint and the server's replay compares it (event-log.md §5).
export function canonicalJson(value: unknown): string {
  if (value === null || typeof value === "boolean" || typeof value === "string") return JSON.stringify(value);
  if (typeof value === "number") {
    if (!Number.isInteger(value)) throw new TypeError("float not allowed in canonical JSON");
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(",")}]`;
  if (typeof value === "object") {
    const obj = value as Record<string, unknown>;
    const keys = Object.keys(obj).filter((k) => obj[k] !== undefined).sort(byCodePoint);
    return `{${keys.map((k) => `${JSON.stringify(k)}:${canonicalJson(obj[k])}`).join(",")}}`;
  }
  throw new TypeError(`type ${typeof value} not allowed in canonical JSON`);
}

// Python sorts str keys by code point; JS sort() compares UTF-16 units. Match Python.
function byCodePoint(a: string, b: string): number {
  const ca = [...a].map((c) => c.codePointAt(0)!);
  const cb = [...b].map((c) => c.codePointAt(0)!);
  for (let i = 0; i < Math.min(ca.length, cb.length); i++) if (ca[i] !== cb[i]) return ca[i] - cb[i];
  return ca.length - cb.length;
}

export async function sha256Hex(text: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

export function docHash(docJson: unknown): Promise<string> {
  return sha256Hex(canonicalJson(docJson));
}
