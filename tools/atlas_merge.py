"""Merge duplicate tiles in the runtime atlases and remap the JMAP ids.

res/tileset.png (chapters 2-3) and res/tileset_ch1.png (chapter 1) contain
atlas slots whose pixels are identical; they come from the recovery
pipeline's per-cell vocabulary. This tool:

1. hashes every 16x16 slot,
2. renumbers duplicate slots onto the lowest id of their group,
3. rewrites res/chapter*.jmap terrain ids accordingly (RLE re-packed),
4. writes a compacted atlas PNG with no empty slots between used ids.

Usage: python tools/atlas_merge.py
"""
import os
import struct

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "res")


def read_jmap(path):
    b = open(path, "rb").read()
    pos = 4

    def u8():
        nonlocal pos
        v = b[pos]
        pos += 1
        return v

    def u16():
        nonlocal pos
        v = (b[pos] << 8) | b[pos + 1]
        pos += 2
        return v

    ver = u8()
    flags = u8()
    lm = u8()
    ts = u8()
    w, h, oc = u16(), u16(), u16()
    nl = u8()
    name = b[pos:pos + nl]
    pos += nl

    def layer():
        nonlocal pos
        ln = (u16() << 16) | u16()
        end = pos + ln
        vals = []
        if flags & 1:
            while pos < end:
                v, r = u16(), u16()
                vals += [v] * r
        else:
            while pos < end:
                vals.append(u16())
        return vals

    terr = layer()
    col = layer()
    objs = b[pos:]
    return {"ver": ver, "flags": flags, "lm": lm, "ts": ts, "w": w, "h": h,
            "name": name, "terr": terr, "col": col, "objs": objs}


def write_jmap(path, m, terrain_rle=True):
    terr = m["terr"]
    col = m["col"]
    out = bytearray()
    out += b"JMAP"
    flags = m["flags"]
    if terrain_rle:
        flags |= 1
    else:
        flags &= ~1 & 0xFF
    out += struct.pack(">BBBBHHHB", m["ver"], flags, m["lm"], m["ts"],
                       m["w"], m["h"], len(m["objs"]) // 10, len(m["name"]))
    out += m["name"]

    def pack(vals, rle):
        buf = bytearray()
        if rle:
            i = 0
            while i < len(vals):
                v = vals[i]
                j = i
                while j < len(vals) and vals[j] == v:
                    j += 1
                buf += struct.pack(">HH", v, min(j - i, 0xFFFF))
                i = j
        else:
            for v in vals:
                buf += struct.pack(">H", v)
        out.extend(struct.pack(">I", len(buf)))
        out.extend(buf)

    pack(terr, terrain_rle)
    pack(col, False)
    out += m["objs"]
    open(path, "wb").write(bytes(out))


def merge(atlas_path, jmap_paths):
    im = Image.open(atlas_path).convert("RGB")
    cols = im.width // 16
    rows = im.height // 16
    n = cols * rows
    sigs = {}
    remap = list(range(n))
    for i in range(n):
        cx, cy = (i % cols) * 16, (i // cols) * 16
        s = np.array(im.crop((cx, cy, cx + 16, cy + 16))).tobytes()
        if s in sigs:
            remap[i] = sigs[s]
        else:
            sigs[s] = i
    dups = sum(1 for i in range(n) if remap[i] != i)
    print(f"{os.path.basename(atlas_path)}: {n} slots, {len(sigs)} unique, {dups} duplicates")

    # keep id 0 as void even if duplicated
    used = sorted({remap[v] for jp in jmap_paths for v in read_jmap(jp)["terr"]})
    if 0 in remap[1:] and 0 not in used:
        pass
    newidx = {0: 0}
    nxt = 1
    for u in used:
        if u != 0:
            newidx[u] = nxt
            nxt += 1
    # slot 0 must be void (black); if a used tile hashes to slot 0, keep it
    # there and let the renderer draw black (TileMap treats 0 as void).

    for jp in jmap_paths:
        m = read_jmap(jp)
        m["terr"] = [newidx[remap[v]] for v in m["terr"]]
        write_jmap(jp, m)
        print("  rewrote", os.path.basename(jp), "->", len(newidx), "tiles")

    # compact atlas: new ids map to slots row-major from the old pixels
    out = Image.new("RGB", (64 * 16, ((nxt + 63) // 64) * 16), (0, 0, 0))
    for old, new in newidx.items():
        cx, cy = (old % cols) * 16, (old // cols) * 16
        ox, oy = (new % 64) * 16, (new // 64) * 16
        out.paste(im.crop((cx, cy, cx + 16, cy + 16)), (ox, oy))
    out.save(atlas_path)
    print(f"  compacted atlas {out.size}, {nxt} tiles")


def main():
    merge(os.path.join(RES, "tileset_ch1.png"),
          [os.path.join(RES, "chapter1.jmap")])
    merge(os.path.join(RES, "tileset.png"),
          [os.path.join(RES, "chapter2.jmap"), os.path.join(RES, "chapter3.jmap")])


if __name__ == "__main__":
    main()
