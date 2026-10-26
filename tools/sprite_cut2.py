"""Cut the enemy / gun / death sheets from verified demo frames.

  res/zombie.png   3 left-facing walk poses, 22x24 per cell (mirror for right)
  res/howler.png   2 violet poses + 1 lit-white pose, 24x26 per cell
  res/death.png    green skull corpse + spread-eagle fall, 26x24 per cell
  res/gunman.png   the player aiming the red gun (facing left), 20x28

All source frames were verified visually:
  zombie walk  3048/3049/3051 (head anchor (61|62|64,106))
  howler       2144/2145 violet, 2146 lit  (176x208 main capture)
  death        2506 skull, 2512 spread
  gunman       3067 (player holding the red gun)
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FR = os.path.join(ROOT, "alonehorror_demo_frames", "png")


def frame(f):
    return Image.open(os.path.join(FR, f"Untitled_{f:06d}.png")).convert("RGB")


def mask_zombie(c):
    r, g, b = c[:, :, 0].astype(int), c[:, :, 1].astype(int), c[:, :, 2].astype(int)
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    pale = (mn > 90) & ((mx - mn) < 40) & (mx > 95)
    jeans = (b - r > 30) & (b > 60)
    return pale | jeans


def mask_howler(c):
    r, g, b = c[:, :, 0].astype(int), c[:, :, 1].astype(int), c[:, :, 2].astype(int)
    violet = (b > 130) & (b - g > 50) & (r > 70) & (r < 235)
    white = (mn := np.minimum(np.minimum(r, g), b)) > 150
    claw = (r > 180) & (g > 150) & (b < 120)
    return violet | white | claw


def mask_green(c):
    r, g, b = c[:, :, 0].astype(int), c[:, :, 1].astype(int), c[:, :, 2].astype(int)
    green = (g > 90) & (g - r > 40) & (g - b > 40)
    white = np.minimum(np.minimum(r, g), b) > 150
    return green | white


def cut(im, cx, cy, w, h, mask_fn, name):
    """Crop, key, return an RGBA cell with the sprite bottom-centred."""
    c = np.array(im.crop((cx - w // 2, cy, cx + w // 2, cy + h))).astype(int)
    m = mask_fn(c)
    m = ndimage.binary_closing(m, np.ones((2, 2)))
    lbl, n = ndimage.label(m)
    H, W = m.shape
    # body = the component nearest the window centre-bottom
    best, bn = -1e9, 0
    for j in range(1, n + 1):
        comp = lbl == j
        ys, xs = np.nonzero(comp)
        d = abs(xs.mean() - W / 2) + abs(ys.mean() - H * 0.7)
        s = len(xs)
        if s < 12 or s > 400:
            continue
        score = -d + (0 if ys.max() >= H - 3 else -6)
        if score > best:
            best, bn = score, j
    if not bn:
        raise SystemExit(f"no body in {name}")
    keep = lbl == bn
    ys, xs = np.nonzero(keep)
    bx0, bx1, by0, by1 = xs.min(), xs.max(), ys.min(), ys.max()
    for j in range(1, n + 1):
        comp = lbl == j
        if j == bn or comp.sum() < 8 or comp.sum() > 60:
            continue
        ys, xs = np.nonzero(comp)
        if (xs.min() >= bx0 - 2 and xs.max() <= bx1 + 2
                and ys.min() >= by0 - 2 and ys.max() <= by1 + 2):
            keep |= comp
    keep = ndimage.binary_fill_holes(keep)
    spr = c.copy()
    spr[~keep] = 0
    ys, xs = np.nonzero(keep)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    src = spr[y0:y1 + 1, x0:x1 + 1].astype(np.uint8)
    amask = keep[y0:y1 + 1, x0:x1 + 1]
    hh, ww = src.shape[:2]
    cell = np.zeros((h, w, 4), dtype=np.uint8)
    ox, oy = (w - ww) // 2, (h - 2) - hh
    if oy < 0:
        raise SystemExit(f"{name}: sprite {hh} taller than cell {h}")
    cell[oy:oy + hh, ox:ox + ww, :3] = src
    cell[oy:oy + hh, ox:ox + ww, 3] = amask * 255
    print(name, "bbox", (x0, y0, x1, y1))
    return cell


def main():
    # ---- zombie: 3 left walk poses
    CW, CH = 22, 26
    sheet = Image.new("RGBA", (CW * 3, CH), (0, 0, 0, 0))
    for i, (f, cx, cy) in enumerate([(3048, 61, 104), (3049, 62, 104), (3051, 64, 104)]):
        cell = cut(frame(f), cx, cy, CW, CH, mask_zombie, f"zombie{i}")
        sheet.paste(Image.fromarray(cell), (i * CW, 0))
    sheet.save(os.path.join(ROOT, "res", "zombie.png"))

    # ---- howler: pose A, pose B, lit-white
    CW, CH = 26, 32
    sheet = Image.new("RGBA", (CW * 3, CH), (0, 0, 0, 0))
    for i, (f, cx, cy) in enumerate([(2144, 167, 93), (2145, 156, 96)]):
        cell = cut(frame(f), cx, cy, CW, CH, mask_howler, f"howler{i}")
        sheet.paste(Image.fromarray(cell), (i * CW, 0))
    # lit pose: the light burns the howler white-hot (demo 2146)
    lit = np.array(sheet.crop((0, 0, CW, CH)))
    m = lit[:, :, 3] > 0
    claw = (lit[:, :, 0] > 180) & (lit[:, :, 1] > 140) & (lit[:, :, 2] < 120)
    lit[:, :, 0] = np.where(m & ~claw, 238, lit[:, :, 0])
    lit[:, :, 1] = np.where(m & ~claw, 236, lit[:, :, 1])
    lit[:, :, 2] = np.where(m & ~claw, 245, lit[:, :, 2])
    sheet.paste(Image.fromarray(lit), (2 * CW, 0))
    sheet.save(os.path.join(ROOT, "res", "howler.png"))

    # ---- death: skull + spread
    CW, CH = 26, 24
    sheet = Image.new("RGBA", (CW * 2, CH), (0, 0, 0, 0))
    for i, (f, cx, cy) in enumerate([(2506, 60, 66), (2512, 60, 62)]):
        cell = cut(frame(f), cx, cy, CW, CH, mask_green, f"death{i}")
        sheet.paste(Image.fromarray(cell), (i * CW, 0))
    sheet.save(os.path.join(ROOT, "res", "death.png"))
    sheet.crop((0, 0, CW, CH)).save(os.path.join(ROOT, "res", "death_skull.png"))
    sheet.crop((CW, 0, CW * 2, CH)).save(os.path.join(ROOT, "res", "death_spread.png"))

    # ---- gunman: player aiming the red gun (facing left)
    CW, CH = 22, 30
    sheet = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))

    def mask_gun(c):
        r, g, b = c[:, :, 0].astype(int), c[:, :, 1].astype(int), c[:, :, 2].astype(int)
        mx = np.maximum(np.maximum(r, g), b)
        mn = np.minimum(np.minimum(r, g), b)
        shirt = (mn > 120) & ((mx - mn) < 70)
        grey = (mn > 95) & ((mx - mn) < 35)
        jeans = (b - r > 35) & (b > 70)
        skin = (r > 130) & (r - b > 25) & (g > 70) & (g < r) & (r - g > 15)
        hair = (r > 60) & (r < 150) & (r - b > 15) & (g - b > 8)
        gun = (r > 120) & (r - g > 40) & (g < 110)     # red-brown gun
        return shirt | grey | jeans | skin | hair | gun

    cell = cut(frame(3108), 84, 104, 22, 30, mask_gun, "gunman")
    sheet.paste(Image.fromarray(cell), (0, 0))
    sheet.save(os.path.join(ROOT, "res", "gunman.png"))

    # ---- review sheet
    imgs = ["zombie.png", "howler.png", "death.png", "gunman.png"]
    tiles = [Image.open(os.path.join(ROOT, "res", n)).convert("RGBA") for n in imgs]
    W = sum(t.width for t in tiles) + 12
    H = max(t.height for t in tiles)
    rev = Image.new("RGBA", (W, H), (20, 20, 30, 255))
    x = 0
    for t in tiles:
        rev.paste(t, (x, 0), t)
        x += t.width + 4
    rev.resize((rev.width * 8, rev.height * 8), Image.NEAREST).save(
        os.path.join(ROOT, "tmp", "enemies_check.png"))
    print("saved enemy sheets")


if __name__ == "__main__":
    main()
