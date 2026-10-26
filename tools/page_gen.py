import numpy as np
from PIL import Image

RES = r"C:\Users\Admin\j2mewtk\2.5.2\apps\AloneTheHorror\res"
FR = r"C:\Users\Admin\j2mewtk\2.5.2\apps\AloneTheHorror\alonehorror_demo_frames\png"

# median of the level-select / config screens removes the moving candle and any
# per-frame noise, leaving the parchment frame and the dark hand silhouette.
frames = []
for n in list(range(176, 184)) + list(range(208, 288)):
    frames.append(np.asarray(Image.open(FR + "\\Untitled_%06d.png" % n).convert("RGB")).astype(np.int16))
med = np.median(np.stack(frames, 0), 0).astype(np.uint8)
img = Image.fromarray(med)

# erase the text blocks (title band and body band) with clean parchment taken
# from a quiet strip of the sheet, then save a plain page background.
src = med[176:200, 12:160]
for yy in range(24, 176):
    for xx in range(14, 162):
        img.putpixel((xx, yy), tuple(int(v) for v in src[(yy - 24) % src.shape[0], xx - 14]))
img.save(RES + r"\page.png")
print("saved page.png", img.size)
