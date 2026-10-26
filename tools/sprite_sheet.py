"""Build the final 12-pose player sheet from the extracted demo crops.

Input:  tmp/sprites_ch<n>.pkl          (from sprite_extract.py)
Output: tmp/poses.png  (all candidate poses, keyed, zoomed)
        tmp/poses.pkl  (keyed sprites per direction, ranked)

The sprite palette is learned from the cleanest crops (k-means over the
masked pixels); every candidate crop is keyed against it, the largest
connected component is kept and holes are filled.
"""
import os
import pickle
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import sprite_extract as se                      # noqa: E402

TMP = os.path.join(ROOT, "tmp")
CW, CH = se.CW, se.CH


def kmeans(px, k, iters=12):
    """Tiny k-means; px is n x 3 float."""
    rng = np.random.RandomState(7)
    cent = px[rng.choice(len(px), k, replace=False)]
    for _ in range(iters):
        d = ((px[:, None, :] - cent[None, :, :]) ** 2).sum(-1)
        lab = d.argmin(1)
        for j in range(k):
            m = px[lab == j]
            if len(m):
                cent[j] = m.mean(0)
    return cent


def learn_palette(crops):
    px = []
    for c in crops:
        m = se.sprite_mask(c)
        px.append(c[m])
    px = np.concatenate(px).astype(float)
    # keep the brighter half: sprite pixels, not dark-world noise
    px = px[px.sum(1) > np.percentile(px.sum(1), 45)]
    return kmeans(px, 10)


def key(crop, pal, dist=62):
    d = ((crop[:, :, None, :] - pal[None, None, :, :]) ** 2).sum(-1)
    m = d.min(-1) < dist ** 2
    # largest connected component + hole filling
    from scipy import ndimage
    lbl, n = ndimage.label(m)
    if n > 1:
        sizes = ndimage.sum(m, lbl, range(1, n + 1))
        m = lbl == (sizes.argmax() + 1)
    m = ndimage.binary_closing(m, np.ones((2, 2)))
    m = ndimage.binary_fill_holes(m)
    out = crop.copy()
    out[~m] = 0
    return out, m


def main():
    all_crops = []
    for ch in (1, 2, 3):
        se.MASK_MIN = 72 if ch == 2 else 95
        tracks = se.build_tracks(ch)
        crops = se.gather(ch, tracks)
        crops = [c for c in crops if c[1] and se.sprite_centered(c[2])]
        all_crops += crops
    print("crops:", len(all_crops))

    pal = learn_palette([c for _, _, c in all_crops])
    print("palette:", pal.astype(int).tolist())

    result = {}
    for d in ("down", "up", "left", "right"):
        sel = [(f, c) for f, dd, c in all_crops if dd == d]
        if not sel:
            continue
        cls = se.cluster([c for _, c in sel])
        cls.sort(key=lambda c: -len(c[1]))
        poses = []
        for m, idxs in cls:
            if len(idxs) < 2:
                continue
            idxs = sorted(idxs, key=lambda i: -se.sprite_mask(sel[i][1]).sum())
            f, crop = sel[idxs[0]]
            spr, mask = key(crop, pal)
            poses.append({"n": len(idxs), "frame": f, "spr": spr, "mask": mask})
        result[d] = poses

    # contact sheet
    maxp = max(len(v) for v in result.values())
    im = Image.new("RGB", (CW * maxp * 4 + 60, CH * 4), (25, 25, 35))
    dr = ImageDraw = None
    x = 0
    for d in ("down", "up", "left", "right"):
        for p in result.get(d, []):
            s = Image.fromarray(p["spr"].astype(np.uint8)).resize(
                (CW * 4, CH * 4), Image.NEAREST)
            im.paste(s, (x, 0))
            x += CW * 4 + 4
    im.save(os.path.join(TMP, "poses.png"))
    pickle.dump(result, open(os.path.join(TMP, "poses.pkl"), "wb"))
    for d, v in result.items():
        print(d, [(p["n"], p["frame"]) for p in v])


if __name__ == "__main__":
    main()
