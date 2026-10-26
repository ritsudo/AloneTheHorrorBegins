"""Cut the final 12-pose player sheet from hand-picked demo frames.

Each direction has three walk poses (contact A, passing B, contact C); the
idle pose reuses the passing pose. The chosen demo frames were verified
visually against the capture (tmp/final_candidates*.png).

The key is a single-frame colour test (shirt/grey/jeans/skin/hair/flame);
background forest is dark and path brown is excluded by saturation tests,
so no per-pose alignment is needed.

Output:
  res/player.png        12 cells of 20x28: down A B C, up A B C,
                        left A B C, right A B C
  tmp/player_check.png  8x zoom of the sheet for review
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import sprite_extract as se                      # noqa: E402

CW, CH = 20, 28

# (chapter, frame) per direction and pose - verified clean walk frames
PICKS = {
    "down":  [(2, 2901), (2, 2903), (2, 2923)],
    "up":    [(2, 3173), (2, 3158), (2, 2893)],
    "left":  [(2, 3225), (2, 3228), (2, 3229)],
    "right": [(1, 1414), (1, 1415), (1, 1418)],
}


def crop_of(ch, f, tracks):
    se.MASK_MIN = 72 if ch == 2 else 95
    if ch not in tracks:
        tracks[ch] = se.build_tracks(ch)
    x, y = tracks[ch][f]
    im = Image.open(os.path.join(se.FRAMES, f"Untitled_{f:06d}.png")).convert("RGB")
    return se.crop_at(im, x, y)


def color_mask(crop):
    r = crop[:, :, 0].astype(int)
    g = crop[:, :, 1].astype(int)
    b = crop[:, :, 2].astype(int)
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    shirt = (mn > 130) & ((mx - mn) < 60)            # white shirt / face sheen
    grey = (mn > 100) & ((mx - mn) < 30)             # shaded shirt
    jeans = (b - r > 35) & (b > 70)                  # blue jeans
    skin = (r > 130) & (r - b > 25) & (g > 70) & (g < r) & (r - g > 15)
    hair = (r > 60) & (r < 150) & (r - b > 15) & (g - b > 8)
    flame = (r > 180) & (g > 170) & (b < 170)        # torch flame
    return shirt | grey | jeans | skin | hair | flame


def key(crop):
    m0 = color_mask(crop)
    m = ndimage.binary_closing(m0, np.ones((2, 2)))
    lbl, n = ndimage.label(m)
    h, w = m.shape
    # the body is the component covering the hip window (rows 20..24,
    # cols 8..12) - jeans are always there when the tracker is right
    hip = m[20:25, 8:13]
    best, best_n = -1, 0
    for j in range(1, n + 1):
        s = (lbl[20:25, 8:13] == j).sum()
        if s > best:
            best, best_n = s, j
    keep = np.zeros_like(m)
    if best_n > 0 and hip.sum() > 0:
        keep |= lbl == best_n
        bys, bxs = np.nonzero(lbl == best_n)
        bx0, bx1, by0, by1 = bxs.min(), bxs.max(), bys.min(), bys.max()
        for j in range(1, n + 1):
            comp = lbl == j
            if j == best_n or comp.sum() < 8 or comp.sum() > 40:
                continue
            ys, xs = np.nonzero(comp)
            # secondary blobs only when hugging the body (head, torch):
            # inside the body bbox expanded by 2 px
            if (xs.min() >= bx0 - 2 and xs.max() <= bx1 + 2
                    and ys.min() >= by0 - 2 and ys.max() <= by1 + 2
                    and xs.min() > 0 and xs.max() < w - 1):
                keep |= comp
    keep = ndimage.binary_fill_holes(keep)
    return keep


def main():
    tracks = {}
    sheet = Image.new("RGBA", (CW * 12, CH), (0, 0, 0, 0))
    i = 0
    for d in ("down", "up", "left", "right"):
        for ch, f in PICKS[d]:
            c = crop_of(ch, f, tracks)
            m = key(c)
            spr = c.copy()
            spr[~m] = 0
            ys, xs = np.nonzero(m)
            if len(xs) == 0:
                raise SystemExit(f"empty key {d} {f}")
            x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
            src = spr[y0:y1 + 1, x0:x1 + 1].astype(np.uint8)
            amask = m[y0:y1 + 1, x0:x1 + 1]
            h, w = src.shape[:2]
            cell = np.zeros((CH, CW, 4), dtype=np.uint8)
            ox = (CW - w) // 2
            oy = (CH - 2) - h
            sy0, sx0 = max(0, -oy), max(0, -ox)
            dy0, dx0 = max(0, oy), max(0, ox)
            hh = min(h - sy0, CH - dy0)
            ww = min(w - sx0, CW - dx0)
            if hh <= 0 or ww <= 0:
                raise SystemExit(f"sprite too big {d} {f} {src.shape}")
            cell[dy0:dy0 + hh, dx0:dx0 + ww, :3] = src[sy0:sy0 + hh, sx0:sx0 + ww]
            cell[dy0:dy0 + hh, dx0:dx0 + ww, 3] = amask[sy0:sy0 + hh, sx0:sx0 + ww] * 255
            sheet.paste(Image.fromarray(cell), (i * CW, 0))
            print(d, i % 3, f, "bbox", (x0, y0, x1, y1))
            i += 1

    sheet.save(os.path.join(ROOT, "res", "player.png"))
    sheet.resize((sheet.width * 8, sheet.height * 8), Image.NEAREST).save(
        os.path.join(ROOT, "tmp", "player_check.png"))
    print("saved res/player.png", sheet.size)


if __name__ == "__main__":
    main()
