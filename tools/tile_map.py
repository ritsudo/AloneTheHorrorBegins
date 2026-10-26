"""Convert the recovered painted chapter map into a tileset + binary level.

Slices the map on the 16px grid, collapses cells that differ by only a few
pixels into one reusable tile and writes a compact binary (tile indices +
collision flags) that the MIDP engine reads at runtime.

Two things keep the library honest:

  * tiles are merged greedily, most-frequent first, so a tile only shares a
    representative when it is genuinely near-identical to it (the old union-find
    could chain A~B~C into one tile even when A and C were far apart);
  * the sheets are packed tight - the last sheet is only as tall as the tiles
    it still needs - so the library never carries a block of identical blank
    padding tiles (the old writer emitted whole 256x256 sheets, which meant ~200
    duplicate black tiles in the last one).

Setting LIB_N caps the library with k-means (smaller JAR, softer corners):

    python tools/tile_map.py                 # near-exact art (one tile per group)
    set LIB_N=96 && python tools/tile_map.py # capped k-means library

Re-runnable and general enough for later chapters (barn, red house, ...) -
change SRC/OUT/SOLID below.
"""
import os
import struct
import numpy as np
from PIL import Image

PROJ = r"C:\Users\Admin\j2mewtk\2.5.2\apps\AloneTheHorror"
SRC = os.path.join(PROJ, "tools", "ch1_map.png")
SOLID = os.path.join(PROJ, "tools", "ch1_solid.txt")
OUT_SHEET = os.path.join(PROJ, "res", "ch1.tiles.%d.png")
OUT_MAP = os.path.join(PROJ, "res", "ch1.map")
OUT_JAVA = os.path.join(PROJ, "src", "Ch1Data.java")

T = 16
TCOLS = 16       # tiles per atlas row (every sheet keeps this width)
SHEET_ROWS = 16  # full sheets are 16x16 tiles = 256x256 px
PER_SHEET = TCOLS * SHEET_ROWS

LIB_N = int(os.environ.get("LIB_N", "0"))
SMOOTH = 2
LM_BRIGHT = 70
SEED = 0

# a cell may share a tile when it differs from the representative in at most
# TOL_PX pixels, each by more than TOL total RGB - below this the merge is
# invisible on the 176x208 screen
TOL_PX = 16
TOL = 24


def slice_tiles(a):
    h, w = a.shape[:2]
    cols = (w + T - 1) // T
    rows = (h + T - 1) // T
    extra = a.ndim - 2
    pads = [(0, rows * T - h), (0, cols * T - w)]
    if extra:
        pads.append((0, 0))
    pad = np.pad(a, pads, mode="edge")
    shp = (rows, T, cols, T) + tuple(a.shape[2:])
    return pad.reshape(shp).transpose(0, 2, 1, 3, *range(4, 4 + extra)), cols, rows


def kmeans(x, k, iters=60):
    rs = np.random.RandomState(SEED)
    n = len(x)
    cent = x[[rs.randint(n)]]
    d = ((x - cent[0]) ** 2).sum(1)
    for _ in range(1, k):
        p = d / d.sum()
        cent = np.vstack([cent, x[rs.choice(n, p=p)]])
        d = np.minimum(d, ((x - cent[-1]) ** 2).sum(1))
    lab = np.zeros(n, np.int32)
    for _ in range(iters):
        d = ((x[:, None, :] - cent[None]) ** 2).sum(2)
        lab = d.argmin(1)
        new = cent.copy()
        for i in range(k):
            m = lab == i
            if m.any():
                new[i] = x[m].mean(0)
        if np.allclose(new, cent):
            break
        cent = new
    return lab, cent


def greedy_merge(rgb, occ, tol_px=TOL_PX, tol=TOL):
    """Assign every unique cell to the closest existing representative within
    tolerance, or start a new one. Processing the most frequent cells first
    keeps the common art as the representative. Returns the representative
    indices and the group each unique cell belongs to."""
    n = len(rgb)
    order = np.argsort(-occ, kind="stable")
    flat = rgb.reshape(n, -1, 3).astype(np.int16)
    reps = []
    assign = np.zeros(n, np.int32)
    for i in order:
        if reps:
            repmat = flat[np.array(reps, np.int32)]
            d = np.abs(flat[i][None, :] - repmat).sum(2)   # (k, T*T)
            px = (d > tol).sum(1)
            ok = np.nonzero(px <= tol_px)[0]
            if ok.size:
                j = int(ok[np.argmin(d[ok].sum(1))])
                assign[i] = j
                continue
        assign[i] = len(reps)
        reps.append(int(i))
    return reps, assign


def main():
    # keep the original 8-bit palette: an RGB atlas is 3-4x larger in the JAR
    im = Image.open(SRC)
    palette = im.getpalette()
    if im.mode != "P" or palette is None:
        im = im.convert("RGB").quantize(colors=256, method=Image.FASTOCTREE)
        palette = im.getpalette()
    a = np.asarray(im)
    rgb = np.asarray(im.convert("RGB"))
    cells, cols, rows = slice_tiles(a)
    rgb_cells, _, _ = slice_tiles(rgb)

    solid_rows = [ln.strip() for ln in open(SOLID) if ln.strip()]
    assert len(solid_rows) == rows, (len(solid_rows), rows)

    # unique cells (byte-exact)
    index = {}
    uniq = []
    tile_of_cell = np.zeros(rows * cols, np.int32)
    for i in range(rows * cols):
        key = cells.reshape(-1, T, T)[i].tobytes()
        j = index.get(key)
        if j is None:
            j = len(uniq)
            index[key] = j
            uniq.append(cells.reshape(-1, T, T)[i].copy())
        tile_of_cell[i] = j
    U = np.array(uniq, np.uint8)
    n_uniq = len(U)
    print("cells %d, unique %d" % (rows * cols, n_uniq))

    # the RGB of each unique cell (for near-duplicate merging)
    rgb_u = np.array([rgb_cells.reshape(-1, T, T, 3)[np.nonzero(tile_of_cell == i)[0][0]]
                      for i in range(n_uniq)], np.uint8)
    occ = np.bincount(tile_of_cell, minlength=n_uniq)

    reps, assign = greedy_merge(rgb_u, occ)
    ngroups = len(reps)
    lib = [U[reps[g]] for g in range(ngroups)]
    lib_rgb = [rgb_u[reps[g]] for g in range(ngroups)]
    cell_tile = assign[tile_of_cell].astype(np.int32)
    print("near-dup merge %d -> %d groups (exact art)" % (n_uniq, ngroups))

    if 0 < LIB_N < ngroups:
        k = LIB_N
        x = rgb_u[reps].reshape(ngroups, -1).astype(np.float32) / 255.0
        lab_g, cent = kmeans(x, k)
        lab = lab_g[assign]
        print("near-dup merge %d -> %d groups, k-means %d" % (n_uniq, ngroups, k))

        rep_of_cluster = np.zeros(k, np.int32)
        for i in range(k):
            m = np.nonzero(lab == i)[0]
            if len(m):
                rep_of_cluster[i] = int(m[np.argmax(occ[m])])

        cell_cluster = lab[tile_of_cell].reshape(rows, cols)
        # bright landmark cells (wreckage, markers) stay exactly as painted
        cellmean = rgb_cells.reshape(rows, cols, -1).mean(2)
        lm = cellmean >= LM_BRIGHT
        lm_tiles = []
        lm_ids = {}
        for r in range(rows):
            for c in range(cols):
                if lm[r, c]:
                    u = int(tile_of_cell[r * cols + c])
                    if u not in lm_ids:
                        lm_ids[u] = len(lm_tiles)
                        lm_tiles.append(u)
                    cell_cluster[r, c] = k + lm_ids[u]

        sizes = np.bincount(lab, minlength=k)
        bright = np.zeros(k, np.float32)
        flat_rgb = rgb_cells.reshape(-1, T * T, 3)
        for i in range(k):
            m = np.nonzero(tile_of_cell == rep_of_cluster[i])[0]
            if len(m):
                bright[i] = flat_rgb[m[0]].mean()
        protect = ((sizes[lab[tile_of_cell]] <= 3) | (bright[lab[tile_of_cell]] > 80)
                   ).reshape(rows, cols) | lm

        # majority smoothing removes isolated labels but keeps landmark art
        for _ in range(SMOOTH):
            src = cell_cluster.copy()
            for r in range(rows):
                for c in range(cols):
                    if protect[r, c]:
                        continue
                    votes = {}
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if 0 <= r + dr < rows and 0 <= c + dc < cols:
                                v = int(src[r + dr, c + dc])
                                votes[v] = votes.get(v, 0) + (dr == 0 and dc == 0)
                    best = max(votes, key=votes.get)
                    if best != src[r, c] and votes[best] >= 6:
                        cell_cluster[r, c] = best

        lib = [U[rep_of_cluster[i]] for i in range(k)] + [U[u] for u in lm_tiles]
        lib_rgb = ([rgb_u[rep_of_cluster[i]] for i in range(k)]
                   + [rgb_u[u] for u in lm_tiles])
        cell_tile = cell_cluster.reshape(-1).astype(np.int32)
        print("library %d tiles (%d clusters + %d landmarks)"
              % (len(lib), k, len(lm_tiles)))

    n = len(lib)
    ns = (n + PER_SHEET - 1) // PER_SHEET
    sheets = []
    for s in range(ns):
        start = s * PER_SHEET
        cnt = min(PER_SHEET, n - start)
        srows = (cnt + TCOLS - 1) // TCOLS
        sheet = np.zeros((srows * T, TCOLS * T), np.uint8)
        for k in range(cnt):
            c, r = k % TCOLS, k // TCOLS
            sheet[r * T:(r + 1) * T, c * T:(c + 1) * T] = lib[start + k]
        sheets.append(sheet)

    solid = np.zeros((rows, cols), np.uint8)
    for ty in range(rows):
        row = solid_rows[ty]
        for tx in range(cols):
            solid[ty, tx] = 1 if row[tx] == "#" else 0

    ids = cell_tile.reshape(rows, cols)
    with open(OUT_MAP, "wb") as f:
        f.write(b"ATH1")
        f.write(struct.pack("<BBHHHH", 1, T, cols, rows, TCOLS, n))
        f.write(ids.astype("<u2").tobytes())
        f.write(solid.tobytes())

    # remove stale sheets from a previous, larger run
    old = 0
    while os.path.exists(OUT_SHEET % old):
        os.remove(OUT_SHEET % old)
        old += 1
    sheet_bytes = 0
    for s, sheet in enumerate(sheets):
        path = OUT_SHEET % s
        out = Image.fromarray(sheet, "P")
        out.putpalette(palette)
        out.save(path, optimize=True)
        sheet_bytes += os.path.getsize(path)

    # report how faithful the rebuilt map is to the source
    rec = np.array(lib_rgb, np.uint8)[cell_tile].reshape(rows, cols, T, T, 3) \
        .transpose(0, 2, 1, 3, 4).reshape(rows * T, cols * T, 3)
    src = np.asarray(im.convert("RGB"))
    h = min(rec.shape[0], src.shape[0])
    w = min(rec.shape[1], src.shape[1])
    diff = np.abs(rec[:h, :w].astype(np.int16) - src[:h, :w].astype(np.int16))
    pxdiff = (diff.sum(2) > 30).mean() * 100.0
    print("rebuild error: %.3f%% of pixels differ by >30 total RGB" % pxdiff)

    # CLDC has no Class.getResourceAsStream, so the blob travels as a class
    # constant; res/ch1.map stays the source of truth for tools.
    raw = open(OUT_MAP, "rb").read()
    rowsrc = []
    for i in range(0, len(raw), 16):
        chunk = raw[i:i + 16]
        rowsrc.append("        " + " ".join("(byte)0x%02X," % b for b in chunk))
    with open(OUT_JAVA, "w") as f:
        f.write("// Generated by tools/tile_map.py - do not edit.\n")
        f.write("class Ch1Data {\n")
        f.write("    static final byte[] MAP = {\n")
        f.write("\n".join(rowsrc) + "\n")
        f.write("    };\n")
        f.write("}\n")

    print("map %dx%d -> %d tiles" % (cols, rows, n))
    print("tileset %d sheets, last %dx%d -> res/ch1.tiles.N.png (%d bytes)"
          % (ns, sheets[-1].shape[1], sheets[-1].shape[0], sheet_bytes))
    print("binary -> %s (%d bytes)" % (OUT_MAP, os.path.getsize(OUT_MAP)))
    print("java -> %s" % OUT_JAVA)


main()
