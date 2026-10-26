"""Recover the Chapter 1 world map from the demo composite.

Produces:
  tools/ch1_map.png - full world image (void -> black), palette PNG (tile_map.py input)
  tools/ch1_solid.txt - 34x30 collision grid ('#' solid, '.' walkable)
  %TEMP%/opencode/ah/ch1_preview.png - collision overlay for checking
"""
import os
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "alonehorror_demo_frames", "assembly_example", "map_recovery.png")
OUT_IMG = os.path.join(ROOT, "tools", "ch1_map.png")
OUT_SOL = os.path.join(ROOT, "tools", "ch1_solid.txt")
TMP = os.path.join(os.environ.get("TEMP", "."), "opencode", "ah")
T = 16

map_im = Image.open(SRC).convert("RGBA")
px = np.asarray(map_im).astype(np.uint8)

# ---- remove the two baked-in survivor sprites at the spawn -----------------
# copy clean ground from ~37px to the right (same rows: hedge/floor/path are
# horizontal there, so the seam is invisible)
def clean(x0, y0, x1, y1, dx=37):
    dst = px[y0:y1, x0:x1].copy()
    src = px[y0:y1, x0 + dx:x1 + dx].copy()
    # only replace pixels that are figure-ish (light shirt / blue jeans)
    r, g, b, a = dst[:, :, 0].astype(int), dst[:, :, 1].astype(int), dst[:, :, 2].astype(int), dst[:, :, 3]
    fig = (a > 80) & (
        ((r > 110) & (g > 110) & (b > 110)) |          # pale skin / white shirt
        ((b > 90) & (b > r + 30) & (b > g + 10))       # blue jeans
    )
    dst[fig] = src[fig]
    px[y0:y1, x0:x1] = dst

clean(79, 85, 97, 117)
clean(97, 89, 115, 119)

# ---- background: composite on black, palette PNG ---------------------------
rgb = px[:, :, :3].astype(np.float32)
alpha = px[:, :, 3:4].astype(np.float32) / 255.0
comp = (rgb * alpha).clip(0, 255).astype(np.uint8)
bg = Image.fromarray(comp, "RGB")
q = bg.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.NONE)
q.save(OUT_IMG, optimize=True)
mae = np.abs(np.asarray(q.convert("RGB")).astype(int) - comp.astype(int)).mean()
print("wrote", OUT_IMG, os.path.getsize(OUT_IMG), "bytes, quant MAE", round(mae, 2))

# ---- collision grid --------------------------------------------------------
h, w = comp.shape[:2]
cols = (w + T - 1) // T
rows = (h + T - 1) // T
solid = []
lines = []
for j in range(rows):
    row = ""
    for i in range(cols):
        # sample the middle of the cell: paths that only clip a tile edge stay
        # walkable, while hedge/void centres block
        c = px[j * T + 4:j * T + 12, i * T + 4:i * T + 12]
        if c.size == 0:
            row += "#"
            continue
        a = c[:, :, 3] > 80
        tot = float(a.sum())
        if tot < c.shape[0] * c.shape[1] * 0.35:
            row += "#"
            continue
        sel = c[a]
        r = sel[:, 0].astype(int)
        g = sel[:, 1].astype(int)
        b = sel[:, 2].astype(int)
        green = ((g > b + 1) & (g > r + 3)).mean()
        bad = green > 0.30
        solid.append(1 if bad else 0)
        row += "#" if bad else "."
    lines.append(row)
    print("%02d %s" % (j, row))
open(OUT_SOL, "w").write("\n".join(lines) + "\n")
print("wrote", OUT_SOL)

# ---- preview ---------------------------------------------------------------
prev = np.asarray(q.convert("RGB")).copy().astype(np.float32)
for j in range(rows):
    for i in range(cols):
        y, x = j * T, i * T
        col = np.array((255, 30, 30) if lines[j][i] == "#" else (30, 220, 255), dtype=np.float32)
        prev[y:y + T, x:x + T] = prev[y:y + T, x:x + T] * 0.55 + col * 0.45
im = Image.fromarray(prev.clip(0, 255).astype(np.uint8))
im.save(os.path.join(TMP, "ch1_preview.png"))
print("preview", im.size)

# ---- connectivity check ----------------------------------------------------
spawn = (4, 7)  # tile of the survivor group on the upper path
seen = set([spawn])
stack = [spawn]
while stack:
    i, j = stack.pop()
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ni, nj = i + di, j + dj
        if 0 <= ni < cols and 0 <= nj < rows and (ni, nj) not in seen:
            if lines[nj][ni] == ".":
                seen.add((ni, nj))
                stack.append((ni, nj))
walk = sum(1 for j in range(rows) for i in range(cols) if lines[j][i] == ".")
print("walkable cells", walk, "reachable from spawn", len(seen))
far = max(seen, key=lambda p: p[0] + p[1])
print("farthest reachable tile", far)
