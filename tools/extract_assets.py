import os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FR = r"C:\Users\Admin\j2mewtk\2.5.2\apps\AloneTheHorror\alonehorror_demo_frames\png"
RES = r"C:\Users\Admin\j2mewtk\2.5.2\apps\AloneTheHorror\res"
os.makedirs(RES, exist_ok=True)

def frame(n):
    return Image.open(os.path.join(FR, f"Untitled_{n:06d}.png")).convert("RGB")

def arr(n):
    return np.asarray(frame(n)).astype(np.int16)

def save(im, name):
    im.save(os.path.join(RES, name))
    print("saved", name, im.size)

def save_rgba(rgb, mask, name):
    a = np.dstack([rgb, mask]).astype(np.uint8)
    Image.fromarray(a, "RGBA").save(os.path.join(RES, name))
    print("saved", name, (rgb.shape[1], rgb.shape[0]))

# ---------------------------------------------------------------- parchment
# max-composite over the dialogue body to erase text, keep paper
frames = list(range(310, 1680, 7)) + list(range(1730, 3240, 11))
acc = np.zeros((208, 176, 3), np.int16)
for n in frames:
    acc = np.maximum(acc, arr(n))
# body parchment region single tile (no rule line, no frame)
tile = acc[160:205, 12:140]
Image.fromarray(tile.astype(np.uint8)).save(os.path.join(RES, "paper.png"))
print("saved paper.png", tile.shape)

# ---------------------------------------------------------------- panel.png
panel = Image.new("RGB", (176, 72), (0, 0, 0))
# fill interior with tiled paper
paper = Image.fromarray(tile.astype(np.uint8))
for y in range(72):
    for x in range(176):
        panel.putpixel((x, y), paper.getpixel((x % paper.width, y % paper.height)))
d = ImageDraw.Draw(panel)
# wooden frame colours (sampled)
dark = (22, 13, 6)
wood = (74, 51, 28)
hl = (120, 92, 58)
for i in range(6):
    c = dark if i < 2 else (wood if i < 5 else hl)
    d.rectangle([i, i, 175 - i, 71 - i], outline=c)
d.rectangle([6, 6, 169, 65], outline=(6, 4, 2))
# name-bar divider rule (y=155..159 abs -> 19..23 rel)
d.rectangle([7, 19, 169, 23], fill=(28, 16, 8))
d.line([7, 19, 169, 19], fill=(96, 74, 46))
save(panel, "panel.png")

# ---------------------------------------------------------------- portraits
def portrait(n, name, box):
    im = np.asarray(frame(n)).astype(np.uint8)
    x0, y0, x1, y1 = box
    crop = im[y0:y1, x0:x1]
    # alpha: everything that is not "paper" -> keep; but we want full rect drawn over panel
    Image.fromarray(crop).save(os.path.join(RES, name))
    print("saved", name, crop.shape)

portrait(344, "p_you.png", (144, 126, 176, 158))
portrait(2080, "p_jonathan.png", (144, 124, 176, 158))
portrait(2560, "p_man.png", (144, 124, 176, 158))

# ---------------------------------------------------------------- HUD icons
hud = frame(309)
hud.crop((0, 0, 60, 20)).save(os.path.join(RES, "hud_heart.png"))
hud.crop((60, 0, 122, 20)).save(os.path.join(RES, "hud_vein.png"))
hud.crop((82, 0, 98, 20)).save(os.path.join(RES, "hud_alert.png"))
hud.crop((158, 0, 176, 20)).save(os.path.join(RES, "hud_batt.png"))
print("saved hud icons")

# ---------------------------------------------------------------- candles
c = frame(55)
c.crop((32, 66, 52, 102)).save(os.path.join(RES, "candle_l.png"))
c.crop((124, 66, 144, 102)).save(os.path.join(RES, "candle_r.png"))
print("saved candles")

# ---------------------------------------------------------------- baked screens
frame(8).save(os.path.join(RES, "logo.png"))
frame(30).save(os.path.join(RES, "title.png"))
print("saved logo/title")

# ---------------------------------------------------------------- menu bg
# median of menu frames removes moving candle; then erase item text area with paper
menu = []
for n in range(48, 83):
    menu.append(arr(n))
med = np.median(np.stack(menu, 0), 0).astype(np.uint8)
mimg = Image.fromarray(med)
d = ImageDraw.Draw(mimg)
# item text block approx (48,82)-(146,172): fill with surrounding parchment rows
src = med[176:200, 12:146]   # clean-ish lower parchment strip
for yy in range(82, 172):
    for xx in range(48, 146):
        mimg.putpixel((xx, yy), tuple(int(v) for v in src[(yy - 82) % src.shape[0], xx - 48]))
mimg.save(os.path.join(RES, "menu_bg.png"))
print("saved menu_bg.png")

# ---------------------------------------------------------------- player sprite
a = arr(2080)
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
# keep character pixels: white/grey torso, blue jeans, skin, dark hair inside a box
box = a[62:108, 72:104]
mask = np.zeros((46, 32), np.uint8)
bb = box
br, bg, bb2 = bb[:, :, 0], bb[:, :, 1], bb[:, :, 2]
grey = (br > 120) & (abs(br - bg) < 30) & (abs(bg - bb2) < 40)
blue = (bb2 > 90) & (bb2 - br > 25)
skin = (br > 150) & (br - bb2 > 30) & (bg > 100)
lum = bb.mean(2)
dark = lum < 45
inside = grey | blue | skin
mask[inside] = 255
save_rgba(bb.astype(np.uint8), mask, "player.png")

print("DONE")
