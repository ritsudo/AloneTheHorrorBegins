"""Build the near-pixel-exact chapter-1 JMAP from the recovered painting.

This is the high-fidelity path for chapter 1: the painted composite
(tools/ch1_map.png, 34x30 cells) is cut on the 16 px grid, near-duplicate cells
are merged, and the resulting tile library is packed into one 64-column atlas.
The runtime loads it alongside the SDK maps used by chapters 2 and 3.

Outputs:
  res/tileset_ch1.png    near-exact chapter-1 atlas (64 columns)
  res/chapter1.jmap      terrain + recovered collision + gameplay objects

Run from the project root:  python tools/ch1_exact.py
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sdk-map-editor"))

from sdk.jmap import JMap, MapObject, save_map  # noqa: E402

T = 16
COLS = 34
ROWS = 30
ATLAS_COLS = 64
TOL_PX = 16
TOL = 24


def slice_tiles(rgb):
    pad = np.zeros((ROWS * T, COLS * T, 3), np.uint8)
    h = min(rgb.shape[0], ROWS * T)
    w = min(rgb.shape[1], COLS * T)
    pad[:h, :w] = rgb[:h, :w]
    cells = pad.reshape(ROWS, T, COLS, T, 3).transpose(0, 2, 1, 3, 4)
    return cells.reshape(ROWS * COLS, T, T, 3)


def greedy_merge(rgb, occ):
    n = len(rgb)
    order = np.argsort(-occ, kind="stable")
    flat = rgb.reshape(n, -1, 3).astype(np.int16)
    reps = []
    assign = np.zeros(n, np.int32)
    for i in order:
        if reps:
            repmat = flat[np.array(reps, np.int32)]
            d = np.abs(flat[i][None, :] - repmat).sum(2)
            px = (d > TOL).sum(1)
            ok = np.nonzero(px <= TOL_PX)[0]
            if ok.size:
                assign[i] = int(ok[np.argmin(d[ok].sum(1))])
                continue
        assign[i] = len(reps)
        reps.append(int(i))
    return reps, assign


def main():
    rgb = np.asarray(Image.open(ROOT / "tools" / "ch1_map.png").convert("RGB"))
    cells = slice_tiles(rgb)

    index = {}
    uniq = []
    cell_uid = np.zeros(ROWS * COLS, np.int32)
    for i in range(ROWS * COLS):
        key = cells[i].tobytes()
        j = index.get(key)
        if j is None:
            j = len(uniq)
            index[key] = j
            uniq.append(cells[i].copy())
        cell_uid[i] = j
    uniq = np.array(uniq, np.uint8)
    occ = np.bincount(cell_uid, minlength=len(uniq))
    print(f"cells {ROWS * COLS}, unique {len(uniq)}")

    black = (uniq.reshape(len(uniq), -1).sum(1) < 12)
    reps, assign = greedy_merge(uniq, occ)
    groups = [uniq[reps[g]] for g in range(len(reps))]
    cell_group = assign[cell_uid]
    # group 0 must be a full-black void tile
    black_group = None
    for g, tile in enumerate(groups):
        if tile.reshape(-1).sum() < 12:
            black_group = g
            break
    if black_group is None:
        groups.insert(0, np.zeros((T, T, 3), np.uint8))
        cell_group = cell_group + 1
        black_group = 0
    elif black_group != 0:
        groups[0], groups[black_group] = groups[black_group], groups[0]
        cell_group = np.where(
            cell_group == black_group, 0,
            np.where(cell_group == 0, black_group, cell_group),
        )
    # any exact black cell becomes the void id
    for i in range(len(uniq)):
        if black[i]:
            cell_group[cell_uid == i] = 0

    n = len(groups)
    print(f"near-dup merge {len(uniq)} -> {n} tiles (void id 0)")

    rows = (n + ATLAS_COLS - 1) // ATLAS_COLS
    atlas = np.zeros((rows * T, ATLAS_COLS * T, 3), np.uint8)
    for i, tile in enumerate(groups):
        cx, cy = (i % ATLAS_COLS) * T, (i // ATLAS_COLS) * T
        atlas[cy:cy + T, cx:cx + T] = tile
    im = Image.fromarray(atlas, "RGB").quantize(colors=256, method=Image.MEDIANCUT, dither=Image.NONE)
    out_atlas = ROOT / "res" / "tileset_ch1.png"
    im.save(out_atlas, optimize=True)

    solid_rows = [ln.strip() for ln in open(ROOT / "tools" / "ch1_solid.txt") if ln.strip()]
    solid = np.array([[1 if ch == "#" else 0 for ch in row] for row in solid_rows], np.uint8)

    runtime_objects = json.loads((ROOT / "tools" / "ch1_objects_sdk.json").read_text())
    objects = [
        MapObject(o["kind"], o["type"], o["x"] + 3, o["y"] + 2, o["flags"], o["param"])
        for o in runtime_objects
        if 0 <= o["x"] + 3 < COLS and 0 <= o["y"] + 2 < ROWS
    ]

    terrain = cell_group.reshape(ROWS * COLS).astype(int).tolist()
    collision = solid.reshape(ROWS * COLS).astype(int).tolist()
    out_map = ROOT / "res" / "chapter1.jmap"
    save_map(
        JMap("chapter1", COLS, ROWS, terrain, collision, objects, T),
        out_map,
    )
    print(f"atlas {im.size} {out_atlas.stat().st_size} bytes -> {out_atlas}")
    print(f"map {COLS}x{ROWS}, {n} tiles, {len(objects)} objects -> {out_map}")


if __name__ == "__main__":
    main()
