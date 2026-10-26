"""Repair the chapter-1 world painting from the level montage.

The recovered painting (tools/ch1_map.png, from assembly_example/map_recovery.png)
lost three regions that the demo's own level montage (levels/chapter1.png) does
show: the top forest block, the right-edge grove and the whole bottom-left
area with its wall torches. This tool copies those regions in from the
montage (offset +32,+24), skips cells that contain baked-in actor sprites,
recomputes the collision grid and writes the two inputs of ch1_exact.py.

Usage: python tools/ch1_repair.py
"""
import os

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, "alonehorror_demo_frames", "levels", "chapter1.png")
MAP = os.path.join(ROOT, "tools", "ch1_map.png")
SOL = os.path.join(ROOT, "tools", "ch1_solid.txt")
T = 16
OX, OY = 32, 24          # map coords = montage coords + (OX, OY)

ref = np.asarray(Image.open(REF).convert("RGB")).astype(int)
mp = np.asarray(Image.open(MAP).convert("RGB")).astype(int)
H, W = mp.shape[:2]

copied = 0
for cy in range(0, (ref.shape[0] + T - 1) // T):
    for cx in range(0, (ref.shape[1] + T - 1) // T):
        ry0, rx0 = cy * T, cx * T
        my0, mx0 = ry0 + OY, rx0 + OX
        if my0 + T > H or mx0 + T > W or ry0 + T > ref.shape[0] or rx0 + T > ref.shape[1]:
            continue
        rcell = ref[ry0:ry0 + T, rx0:rx0 + T]
        mcell = mp[my0:my0 + T, mx0:mx0 + T]
        r_content = (rcell.sum(axis=2) > 40).mean()
        m_void = (mcell.sum(axis=2) < 30).mean()
        if r_content < 0.35 or m_void < 0.55:
            continue
        # skip cells with baked actor pixels (white shirt, blue jeans)
        r, g, b = rcell[:, :, 0], rcell[:, :, 1], rcell[:, :, 2]
        sprite = ((r > 190) & (g > 190) & (b > 190)) \
            | ((b - r > 40) & (b > 90) & (r < 110))
        if sprite.sum() > 6:
            continue
        mp[my0:my0 + T, mx0:mx0 + T] = rcell
        copied += 1

print("cells copied:", copied)
Image.fromarray(mp.astype(np.uint8)).save(MAP, optimize=True)

# ---- collision: walkable unless void or dense foliage ----------------------
rows = (H + T - 1) // T
cols = (W + T - 1) // T
lines = []
for j in range(rows):
    row = ""
    for i in range(cols):
        c = mp[j * T + 4:j * T + 12, i * T + 4:i * T + 12]
        if c.size == 0:
            row += "#"
            continue
        s = c.sum(axis=2)
        if (s < 30).mean() > 0.5:                 # void centre
            row += "#"
            continue
        r, g, b = c[:, :, 0], c[:, :, 1], c[:, :, 2]
        green = ((g > b + 1) & (g > r + 3)).mean()
        row += "#" if green > 0.30 else "."
    lines.append(row)
open(SOL, "w").write("\n".join(lines) + "\n")
print("wrote", SOL)
