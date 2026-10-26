"""Ordered-dither shadow masks for the flashlight / ambient darkness.

The original game has no smooth alpha fade: the world is full bright inside the
light and the falloff is drawn as an ordered dither (Bayer 4x4) of solid black
pixels, so the darkness reads as a coarse stipple pattern. Measuring the demo
frames (176x208) gives two sizes:

  * flashlight ON  - bright core ~16 px, dithered falloff to black at ~35 px
                     (a ~72 px mask)
  * flashlight OFF - a larger, dimmer pool, bright core ~11 px, black by ~55 px
                     (a ~110 px mask)

Both are centred on the player and roughly circular; the edge is bent a little
by a sine wobble and two phase-shifted variants are emitted so the lit area
keeps changing shape as the player walks.

    python tools/light_gen.py
"""
from PIL import Image
import math

RES = r"C:\Users\Admin\j2mewtk\2.5.2\apps\AloneTheHorror\res"

BAYER4 = (
    (0, 8, 2, 10),
    (12, 4, 14, 6),
    (3, 11, 1, 9),
    (15, 7, 13, 5),
)


def light(path, size, inner, outer=1.0, wobble=0.05, phase=0.0):
    """inner/outer are fractions of the half-size radius. Inside `inner` the mask
    is fully clear, beyond `outer` it is solid black; between the two the black
    pixels are thresholded against a Bayer matrix over a smoothstep ramp, so the
    edge is a painted blob that dissolves into a stipple rather than a hard cut.
    `wobble` bends the radius with a few sine terms and `phase` shifts them to
    make a second, differently shaped variant."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    c = size / 2.0
    px = im.load()
    span = outer - inner
    for y in range(size):
        for x in range(size):
            dx = x + 0.5 - c
            dy = y + 0.5 - c
            d = (dx * dx + dy * dy) ** 0.5 / c
            a = math.atan2(dy, dx)
            d /= 1.0 + wobble * (math.sin(3 * a + 1.2 + phase)
                                 + 0.6 * math.sin(7 * a + 2.4 - phase)
                                 + 0.4 * math.sin(11 * a + 0.3 + phase))
            if d >= outer:
                px[x, y] = (0, 0, 0, 255)
                continue
            if d <= inner:
                continue
            t = (d - inner) / span
            t = t * t * (3.0 - 2.0 * t)          # smoothstep
            if t * 16.0 >= BAYER4[y & 3][x & 3] + 0.5:
                px[x, y] = (0, 0, 0, 255)
    im.save(path)
    print("saved", path, im.size)


# gameplay, flashlight on: tight bright pool (demo: black by ~35 px)
light(RES + r"\light_g0.png", 72, 0.45, 1.0, 0.05, 0.0)
light(RES + r"\light_g1.png", 72, 0.45, 1.0, 0.05, 2.7)

# gameplay, flashlight off: a wider, dimmer ambient pool (demo: black by ~55 px)
light(RES + r"\light_gs0.png", 110, 0.20, 1.0, 0.05, 0.0)
light(RES + r"\light_gs1.png", 110, 0.20, 1.0, 0.05, 2.7)
