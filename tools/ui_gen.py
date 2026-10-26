"""Generate page-derived UI overlays from the demo capture.

- res/sign.png     : the "ALONE" wordmark overlay (menu_bg minus page.png)
- res/campfire.png : animated brazier strip (menu highlight marker)

Run from the project root:  python tools/ui_gen.py
"""
import os
import numpy as np
from PIL import Image

RES = r"C:\Users\Admin\j2mewtk\2.5.2\apps\AloneTheHorror\res"
FRAMES = r"C:\Users\Admin\j2mewtk\2.5.2\apps\AloneTheHorror\alonehorror_demo_frames\png"

THRESH = 16


def frame(f):
    return np.asarray(Image.open(os.path.join(FRAMES, "Untitled_%06d.png" % f)).convert("RGB")).astype(int)


def overlay(ref, box):
    x0, y0, x1, y1 = box
    sub = ref[y0:y1, x0:x1]
    return sub


def build_sign():
    page = np.asarray(Image.open(os.path.join(RES, "page.png")).convert("RGB")).astype(int)
    mb = np.asarray(Image.open(os.path.join(RES, "menu_bg.png")).convert("RGB")).astype(int)
    d = np.abs(mb - page).max(axis=2)
    x0, x1, y0, y1 = 3, 156, 6, 70
    sub = mb[y0:y1, x0:x1]
    dsub = d[y0:y1, x0:x1]
    h, w = dsub.shape
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[:, :, 0:3] = sub
    rgba[:, :, 3] = np.where(dsub > THRESH, 255, 0)
    Image.fromarray(rgba, "RGBA").save(os.path.join(RES, "sign.png"))
    print("saved sign.png", (w, h), "at", (x0, y0))


def build_campfire():
    page = np.asarray(Image.open(os.path.join(RES, "page.png")).convert("RGB")).astype(int)
    x0, y0, w, h = 30, 66, 20, 32
    frames = list(range(48, 58))
    strips = []
    for f in frames:
        fr = frame(f)
        sub = fr[y0:y0 + h, x0:x0 + w]
        ref = page[y0:y0 + h, x0:x0 + w]
        d = np.abs(sub - ref).max(axis=2)
        rgba = np.zeros((h, w, 4), np.uint8)
        rgba[:, :, 0:3] = sub
        rgba[:, :, 3] = np.where(d > THRESH, 255, 0)
        strips.append(rgba)
    strip = np.concatenate(strips, axis=1)
    Image.fromarray(strip, "RGBA").save(os.path.join(RES, "campfire.png"))
    print("saved campfire.png", (strip.shape[1], strip.shape[0]), "frames", len(frames), "cell", (w, h))


build_sign()
build_campfire()
