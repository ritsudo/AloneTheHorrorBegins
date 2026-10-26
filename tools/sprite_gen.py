import os, random
from PIL import Image

random.seed(7)
RES = r"C:\Users\Admin\j2mewtk\2.5.2\apps\AloneTheHorror\res"

def new(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))

def px(im, x, y, c):
    if 0 <= x < im.width and 0 <= y < im.height:
        im.putpixel((x, y), c)

SKIN = (214, 172, 140, 255)
HAIR = (58, 40, 30, 255)
SHIRT = (198, 198, 205, 255)
SHIRT_D = (150, 150, 160, 255)
PANTS = (52, 78, 156, 255)
PANTS_D = (36, 54, 116, 255)
BOOT = (40, 32, 26, 255)
OUT = (18, 12, 10, 255)

def body(base=SHIRT, bd=SHIRT_D, leg=PANTS, ld=PANTS_D):
    """top-down 3/4 character, 16x22. returned list of 4 dirs x 2 frames"""
    frames = {}
    for d in ["down", "up", "left", "right"]:
        imgs = []
        for f in (0, 1):
            im = new(16, 22)
            # shadow
            for x in range(3, 13):
                px(im, x, 21, (0, 0, 0, 70))
            # legs
            if d in ("down", "up"):
                lx = 4 if f == 0 else 6
                rx = 8 if f == 0 else 10
                for y in range(15, 21):
                    px(im, lx, y, ld); px(im, lx + 1, y, leg)
                    px(im, rx, y, ld); px(im, rx + 1, y, leg)
                px(im, lx, 20, BOOT); px(im, lx + 1, 20, BOOT)
                px(im, rx, 20, BOOT); px(im, rx + 1, 20, BOOT)
            else:
                lx = 5 if f == 0 else 7
                for y in range(15, 21):
                    px(im, lx, y, ld); px(im, lx + 1, y, leg); px(im, lx + 2, y, ld)
                px(im, lx, 20, BOOT); px(im, lx + 1, 20, BOOT); px(im, lx + 2, 20, BOOT)
            # torso
            for y in range(8, 15):
                for x in range(4, 12):
                    px(im, x, y, base if x < 11 else bd)
            for y in range(8, 15):
                px(im, 4, y, OUT); px(im, 11, y, OUT)
            # arms
            aw = 0 if f == 0 else 1
            for y in range(9, 14):
                px(im, 3 - aw, y, bd); px(im, 3 - aw, y, base if y < 12 else bd)
                px(im, 12 + aw, y, bd); px(im, 12 + aw, y, base if y < 12 else bd)
            # head
            hx = 5 if d != "left" else 4
            for y in range(2, 8):
                for x in range(hx, hx + 6):
                    px(im, x, y, SKIN)
            # hair / cap
            for y in range(2, 5):
                for x in range(hx, hx + 6):
                    px(im, x, y, HAIR)
            if d == "up":
                for y in range(2, 8):
                    for x in range(hx, hx + 6):
                        px(im, x, y, HAIR)
            if d == "down":
                px(im, hx + 1, 5, (30, 20, 15, 255))
                px(im, hx + 4, 5, (30, 20, 15, 255))
            if d == "left":
                px(im, hx, 5, (30, 20, 15, 255))
            if d == "right":
                px(im, hx + 5, 5, (30, 20, 15, 255))
            imgs.append(im)
        frames[d] = imgs
    return frames

def sheet(frames, order, path):
    imgs = [frames[d][f] for d in order for f in (0, 1)]
    s = new(16 * len(imgs), 22)
    for i, im in enumerate(imgs):
        s.paste(im, (i * 16, 0), im)
    s.save(path)
    print("saved", os.path.basename(path), s.size)

HOW = body((120, 150, 96), (86, 112, 66), (86, 92, 70), (58, 62, 48))
sheet(HOW, ["down", "up", "left", "right"], os.path.join(RES, "howler.png"))

wlk = body((132, 132, 128), (96, 96, 96), (78, 74, 70), (52, 50, 48))
# dead-ish skin for walker
for d in wlk:
    for im in wlk[d]:
        for y in range(2, 8):
            for x in range(4, 11):
                p = im.getpixel((x, y))
                if p[3] and p[:3] == SKIN[:3]:
                    im.putpixel((x, y), (150, 150, 128, 255))
sheet(wlk, ["down", "up", "left", "right"], os.path.join(RES, "walker.png"))

# ---------------------------------------------------------------- bush
random.seed(12)
b = new(22, 16)
for y in range(2, 16):
    for x in range(1, 21):
        d = abs(x - 11) / 11 + (y - 2) / 14
        if d < 1:
            g = 48 + random.randint(-16, 22)
            px(b, x, y, (g // 3, g, g // 2, 255))
b.save(os.path.join(RES, "bush.png"))

# ---------------------------------------------------------------- items
def icon(path, draw, w, h):
    im = new(w, h)
    draw(im)
    im.save(path)
    print("saved", os.path.basename(path), im.size)

def key(i):
    for x in range(3, 12):
        px(i, x, 5, (220, 190, 70, 255)); px(i, x, 6, (200, 165, 50, 255))
    for y in range(2, 9):
        px(i, 3, y, (220, 190, 70, 255))
    px(i, 3, 2, (240, 220, 120, 255))
    for y in range(5, 11): px(i, 10, y, (200, 165, 50, 255))
    for y in range(5, 9): px(i, 12, y, (200, 165, 50, 255))
    px(i, 11, 9, (200, 165, 50, 255)); px(i, 13, 9, (200, 165, 50, 255))
icon(os.path.join(RES, "item_key.png"), key, 14, 12)

def medkit(i):
    for y in range(2, 12):
        for x in range(1, 14):
            px(i, x, y, (235, 235, 235, 255))
    for x in range(1, 14): px(i, x, 2, (140, 140, 140, 255))
    for x in range(1, 14): px(i, x, 11, (120, 120, 120, 255))
    for y in range(5, 9):
        for x in range(6, 9):
            px(i, x, y, (200, 30, 30, 255))
    for x in range(4, 11):
        for y in range(6, 8):
            px(i, x, y, (200, 30, 30, 255))
icon(os.path.join(RES, "item_medkit.png"), medkit, 15, 13)

def batt(i):
    for y in range(1, 17):
        for x in range(2, 9):
            px(i, x, y, (40, 40, 40, 255))
    for y in range(3, 15):
        for x in range(3, 8):
            px(i, x, y, (210, 30, 30, 255))
    px(i, 4, 16, (200, 200, 200, 255)); px(i, 5, 16, (200, 200, 200, 255))
    px(i, 6, 16, (200, 200, 200, 255))
icon(os.path.join(RES, "item_batt.png"), batt, 11, 18)

print("SPRITES DONE")
