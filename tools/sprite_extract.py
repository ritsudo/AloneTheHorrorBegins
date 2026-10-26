"""Extract the ground-truth player sprites from the demo capture.

The demo (alonehorror_demo_frames/png/Untitled_*.png, 176x208, 10 fps) shows
the player walking through the chapters. This tool:

1. finds the player in every frame via a white-shirt-over-blue-jeans
   template (the plane wreck and medkits have no jeans below them),
2. keeps walking frames only (displacement >= 1.2 px/frame over +-2 frames,
   measured on a local +-14 px track so the tracker cannot jump to
   background objects),
3. clusters the crops per direction into distinct walk poses by the leg
   signature (XOR leader clustering),
4. median-stacks each cluster: the background differs between samples, the
   sprite is constant, so the median is the clean sprite.

Output: tmp/sprites_ch<n>_<dir>.png contact sheets and tmp/sprites_ch<n>.pkl.

Usage:  python tools/sprite_extract.py [chapter]
"""
import os
import pickle
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAMES = os.path.join(ROOT, "alonehorror_demo_frames", "png")
TMP = os.path.join(ROOT, "tmp")

RANGES = {1: (309, 1694), 2: (1728, 3249), 3: (3284, 3672)}

CW, CH = 20, 32          # crop window: x-10..x+10, y-22..y+10
SEED_SCORE = 80
TRACK_SCORE = 55


def load(f):
    return np.array(Image.open(os.path.join(
        FRAMES, f"Untitled_{f:06d}.png")).convert("RGB")).astype(int)


def has_dialogue(a):
    return (a[140:205, 10:166].sum(axis=2) > 420).mean() > 0.05


def score_map(a, x0, y0, rad):
    """Best shirt+jeans template score within +-rad of (x0, y0).

    Returns (score, x, y) with y the shirt/jeans boundary in screen coords.
    """
    world = a[22:136]
    r, g, b = world[:, :, 0], world[:, :, 1], world[:, :, 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    white = ((mn > 120) & ((mx - mn) < 70)).astype(np.int32)
    blue = ((b - r > 40) & (b > 80)).astype(np.int32)

    def ii(m):
        return np.pad(m.cumsum(0).cumsum(1), ((1, 0), (1, 0)))

    Wi, Bi = ii(white), ii(blue)

    def box(I, ya, yb, xa, xb):
        return I[yb, xb] - I[ya, xb] - I[yb, xa] + I[ya, xa]

    H, W = white.shape
    best = (-1, 0, 0)
    lo = max(10, y0 - rad) if x0 >= 0 else 10
    hi = min(H - 8, y0 + rad) if x0 >= 0 else H - 8
    xlo = max(3, x0 - rad) if x0 >= 0 else 3
    xhi = min(W - 4, x0 + rad) if x0 >= 0 else W - 4
    for y in range(lo, hi):
        for x in range(xlo, xhi):
            s = box(Wi, y - 9, y - 1, x - 3, x + 4) \
                + 2 * box(Bi, y + 1, y + 7, x - 3, x + 4)
            if s > best[0]:
                best = (s, x, y)
    return best


def build_tracks(chapter):
    """Local tracks through walking frames; {frame: (x, y)}."""
    lo, hi = RANGES[chapter]
    frames = {}
    for f in range(lo, hi):
        a = load(f)
        if has_dialogue(a):
            continue
        s, x, y = score_map(a, -1, 0, 0)     # global search
        frames[f] = (s, x, y + 22)

    tracks = {}
    for f, (s, x, y) in sorted(frames.items()):
        if s < SEED_SCORE:
            continue
        if f in tracks:
            continue
        tr = {f: (x, y)}
        # walk the track both ways
        for step in (-1, 1):
            i = f
            while True:
                i += step
                if i not in frames or i in tr:
                    break
                px, py = tr[i - step]
                s2, x2, y2 = score_map(load(i), px, py, 14)
                if s2 < TRACK_SCORE:
                    break
                tr[i] = (x2, y2)
        for k, v in tr.items():
            if k not in tracks:
                tracks[k] = v
    return tracks


def crop_at(im, x, y):
    c = im.crop((x - CW // 2, y - 22, x - CW // 2 + CW, y - 22 + CH))
    return np.array(c).astype(int)


def gather(chapter, tracks):
    keys = sorted(tracks)
    out = []
    for i, f in enumerate(keys):
        pa = tracks.get(keys[i - 2]) if i >= 2 else None
        pb = tracks.get(keys[i + 2]) if i + 2 < len(keys) else None
        p = tracks[f]
        d = None
        if pa and pb:
            dx, dy = pb[0] - pa[0], pb[1] - pa[1]
            if dx * dx + dy * dy < 9:        # < 1.2 px/frame: standing
                continue
            if abs(dx) >= abs(dy):
                d = "right" if dx > 0 else "left"
            else:
                d = "down" if dy > 0 else "up"
        im = Image.open(os.path.join(FRAMES, f"Untitled_{f:06d}.png"))
        out.append((f, d, crop_at(im, p[0], p[1])))
    return out


MASK_MIN = 95


def sprite_mask(crop):
    r, g, b = crop[:, :, 0], crop[:, :, 1], crop[:, :, 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    return ((mn > MASK_MIN) | ((b - r > 40) & (b > 80)))


def sprite_centered(crop):
    """True when a plausible sprite sits near the crop centre."""
    m = sprite_mask(crop)
    if m.sum() < 40:
        return False
    ys, xs = np.nonzero(m)
    cx, cy = xs.mean(), ys.mean()
    return abs(cx - CW / 2) < 5 and 14 < cy < 26


def cluster(crops, thresh=30):
    """Leader-cluster crops of one direction into walk poses (legs only)."""
    legs = [sprite_mask(c)[21:29, 4:16] for c in crops]
    clusters = []
    for idx, m in enumerate(legs):
        for cl in clusters:
            if (m ^ legs[cl[1][0]]).sum() < thresh:
                cl[1].append(idx)
                break
        else:
            clusters.append([m, [idx]])
    return clusters


def stack(crops, idxs):
    """Median-stack same-pose crops with two alignment refinement passes."""
    arr = [crops[i] for i in idxs]
    for _ in range(2):
        rough = np.median(np.stack(arr), axis=0)
        rm = sprite_mask(rough)
        fixed = []
        for a in arr:
            best = (1 << 30, 0, 0)
            for dy in (-2, -1, 0, 1, 2):
                for dx in (-2, -1, 0, 1, 2):
                    s = np.roll(np.roll(sprite_mask(a), dy, 0), dx, 1)
                    d = (s ^ rm).sum()
                    if d < best[0]:
                        best = (d, dx, dy)
            fixed.append(np.roll(np.roll(a, best[1], 1), best[2], 0))
        arr = fixed
    arr = np.stack(arr)
    med = np.median(arr, axis=0).astype(int)
    masks = np.stack([sprite_mask(a) for a in arr])
    keep = masks.mean(axis=0) >= 0.55
    out = med.copy()
    out[~keep] = 0
    return out, keep


def main():
    global MASK_MIN
    chapter = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    if chapter == 2:
        MASK_MIN = 72          # the barn chapter renders the sprite darker
    os.makedirs(TMP, exist_ok=True)
    tracks = build_tracks(chapter)
    print("tracked frames:", len(tracks))
    crops = gather(chapter, tracks)
    crops = [c for c in crops if sprite_centered(c[2])]
    print("walking crops:", len(crops))
    result = {}
    for d in ("down", "up", "left", "right"):
        sel = [c for _, dd, c in crops if dd == d]
        if not sel:
            continue
        cls = cluster(sel)
        cls.sort(key=lambda c: -len(c[1]))
        sheets = []
        for m, idxs in cls:
            if len(idxs) < 2:
                continue
            spr, mask = stack(sel, idxs)
            sheets.append((len(idxs), spr, mask))
        result[d] = sheets
        im = Image.new("RGB", (CW * len(sheets) + 4, CH + 4), (30, 30, 40))
        for i, (n, spr, mask) in enumerate(sheets):
            im.paste(Image.fromarray(spr.astype(np.uint8)), (i * CW + 2, 2))
        im.resize((im.width * 6, im.height * 6), Image.NEAREST).save(
            os.path.join(TMP, f"sprites_ch{chapter}_{d}.png"))
        print(d, [n for n, _, _ in sheets])
    pickle.dump(result, open(os.path.join(TMP, f"sprites_ch{chapter}.pkl"), "wb"))


if __name__ == "__main__":
    main()
