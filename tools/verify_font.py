from PIL import Image
import numpy as np
R = r"C:\Users\Admin\j2mewtk\2.5.2\apps\AloneTheHorror\res"
a = np.asarray(Image.open(R + r"\font.png"))
m = {}
for ln in open(R + r"\font.txt").read().splitlines()[1:]:
    p = ln.split()
    m[int(p[0])] = (int(p[1]), int(p[2]), int(p[3]), int(p[4]))
out = Image.new("RGB", (420, 44), (10, 10, 20))
def draw(s, x, y):
    for ch in s:
        k = ord(ch)
        if k not in m:
            x += 4
            continue
        gx, gy, gw, adv = m[k]
        if gw > 0:
            gl = Image.fromarray(a[gy:gy + 14, gx:gx + gw], "RGBA")
            out.paste(gl, (x, y), gl)
        x += adv
draw("THE HORROR BEGINS", 5, 4)
draw("LOOK FOR THE 1ST KEY! 123, OK?", 5, 24)
out.resize((420 * 3, 44 * 3), Image.NEAREST).save(r"C:/Temp/opencode/ah/chk_text.png")
print("ok")
