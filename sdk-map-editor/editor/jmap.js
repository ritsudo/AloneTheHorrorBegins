/* Shared .jmap codec used by the editor and by Node tests.
 * The byte layout is identical to sdk/jmap.py; see docs/FORMAT.md.
 */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.JMapCodec = factory();
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

class Writer {
  constructor() { this.buf = new Uint8Array(512); this.len = 0; }
  ensure(n) {
    if (this.len + n <= this.buf.length) return;
    let size = this.buf.length * 2;
    while (size < this.len + n) size *= 2;
    const next = new Uint8Array(size);
    next.set(this.buf.subarray(0, this.len));
    this.buf = next;
  }
  u8(v) { this.ensure(1); this.buf[this.len++] = v & 255; }
  u16(v) {
    this.ensure(2);
    this.buf[this.len++] = (v >>> 8) & 255;
    this.buf[this.len++] = v & 255;
  }
  u32(v) {
    this.ensure(4);
    this.buf[this.len++] = (v >>> 24) & 255;
    this.buf[this.len++] = (v >>> 16) & 255;
    this.buf[this.len++] = (v >>> 8) & 255;
    this.buf[this.len++] = v & 255;
  }
  bytes(arr) { this.ensure(arr.length); this.buf.set(arr, this.len); this.len += arr.length; }
  toBytes() { return this.buf.slice(0, this.len); }
}

function rleEncode(values) {
  const w = new Writer();
  let i = 0;
  while (i < values.length) {
    const value = values[i];
    let run = 1;
    while (i + run < values.length && values[i + run] === value && run < 65535) run++;
    w.u16(value); w.u16(run);
    i += run;
  }
  return w.toBytes();
}

function encodeLayer(values) {
  const raw = new Uint8Array(values.length * 2);
  const dv = new DataView(raw.buffer);
  for (let i = 0; i < values.length; i++) dv.setUint16(i * 2, values[i]);
  const packed = rleEncode(values);
  return packed.length < raw.length
    ? { payload: packed, compressed: true }
    : { payload: raw, compressed: false };
}

function decodeLayer(dv, bytes, posRef, count, compressed) {
  if (posRef.p + 4 > bytes.length) throw new Error('truncated layer length');
  const length = dv.getUint32(posRef.p); posRef.p += 4;
  if (posRef.p + length > bytes.length) throw new Error('truncated layer payload');
  const start = posRef.p; const end = start + length;
  const out = new Uint16Array(count);
  if (compressed) {
    let p = start; let i = 0;
    while (p < end) {
      if (p + 4 > end) throw new Error('truncated RLE');
      const value = dv.getUint16(p); p += 2;
      const run = dv.getUint16(p); p += 2;
      if (!run || i + run > count) throw new Error('bad RLE run');
      out.fill(value, i, i + run);
      i += run;
    }
    if (i !== count) throw new Error('RLE underrun');
  } else {
    if (length !== count * 2) throw new Error('raw layer size mismatch');
    for (let i = 0; i < count; i++) out[i] = dv.getUint16(start + i * 2);
  }
  posRef.p = end;
  return out;
}

function decodeJMap(bytes) {
  if (bytes.length < 15) throw new Error('file too short');
  const dv = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const magic = String.fromCharCode(bytes[0], bytes[1], bytes[2], bytes[3]);
  if (magic !== 'JMAP') throw new Error('bad magic (expected JMAP)');
  const version = dv.getUint8(4);
  if (version !== 1) throw new Error('unsupported version ' + version);
  const flags = dv.getUint8(5);
  const layerMask = dv.getUint8(6);
  const tileSize = dv.getUint8(7);
  const width = dv.getUint16(8);
  const height = dv.getUint16(10);
  const objectCount = dv.getUint16(12);
  const nameLen = dv.getUint8(14);
  let pos = 15;
  if (pos + nameLen > bytes.length) throw new Error('truncated name');
  const name = new TextDecoder().decode(bytes.subarray(pos, pos + nameLen));
  pos += nameLen;
  const count = width * height;
  const posRef = { p: pos };
  const terrain = decodeLayer(dv, bytes, posRef, count, !!(flags & 1));
  const collision = (layerMask & 2)
    ? decodeLayer(dv, bytes, posRef, count, !!(flags & 2))
    : new Uint16Array(count);
  const objects = [];
  for (let i = 0; i < objectCount; i++) {
    if (posRef.p + 10 > bytes.length) throw new Error('truncated object');
    objects.push({
      kind: dv.getUint8(posRef.p), type: dv.getUint16(posRef.p + 1),
      x: dv.getUint16(posRef.p + 3), y: dv.getUint16(posRef.p + 5),
      flags: dv.getUint8(posRef.p + 7), param: dv.getUint16(posRef.p + 8),
    });
    posRef.p += 10;
  }
  if (posRef.p !== bytes.length) throw new Error('trailing map bytes');
  return {
    name, width, height, tileSize,
    terrain, collision: Uint8Array.from(collision.map((v) => v & 255)),
    objects, flags, layerMask,
  };
}

function encodeJMap(map) {
  const terrain = encodeLayer(map.terrain);
  const collision = encodeLayer(map.collision);
  let flags = 0;
  if (terrain.compressed) flags |= 1;
  if (collision.compressed) flags |= 2;
  const nameBytes = new TextEncoder().encode(map.name || '');
  if (nameBytes.length > 255) throw new Error('map name longer than 255 bytes');
  const w = new Writer();
  w.bytes([0x4A, 0x4D, 0x41, 0x50]);
  w.u8(1); w.u8(flags); w.u8(7); w.u8(map.tileSize || 16);
  w.u16(map.width); w.u16(map.height); w.u16(map.objects.length);
  w.u8(nameBytes.length); w.bytes(nameBytes);
  w.u32(terrain.payload.length); w.bytes(terrain.payload);
  w.u32(collision.payload.length); w.bytes(collision.payload);
  for (const o of map.objects) {
    w.u8(o.kind); w.u16(o.type); w.u16(o.x); w.u16(o.y);
    w.u8(o.flags); w.u16(o.param);
  }
  return w.toBytes();
}

function base64ToBytes(b64) {
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}

function fnv1a(bytes) {
  let h = 0xCBF29CE484222325n;
  const prime = 0x100000001B3n;
  const mask = 0xFFFFFFFFFFFFFFFFn;
  for (let i = 0; i < bytes.length; i++) {
    h = ((h ^ BigInt(bytes[i])) * prime) & mask;
  }
  return h.toString(16).padStart(16, '0');
}

  return { Writer, rleEncode, encodeLayer, decodeLayer, decodeJMap, encodeJMap, base64ToBytes, fnv1a };
});
