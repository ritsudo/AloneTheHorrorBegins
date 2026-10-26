# ---------------------------------------------------------------------------
# dialogue_recover.py - extract every distinct dialogue panel from the demo
# capture and lay them out on labelled contact sheets for transcription.
#
# The dialogue panel occupies the bottom 72 px of the 176x208 capture
# (y=136..207, name bar / divider / body lines). Portraits extend up to
# y~120, so sheets crop y=112..208. A panel is emitted only after it has
# been stable for STABLE frames (typewriter finished) and is not a
# near-duplicate of an already emitted panel.
#
# Output: docs/analysis/dlg_sheets/ch{1,2,3}_sheet{N}.png (4 panels each,
# 2x nearest-upscaled) and docs/analysis/dlg_panels.txt (frame list).
# ---------------------------------------------------------------------------
import os

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PNG = os.path.join(ROOT, "alonehorror_demo_frames", "png")
OUT = os.path.join(ROOT, "docs", "analysis", "dlg_sheets")

# gameplay ranges per chapter (from docs/DEMO_ANALYSIS.md)
RANGES = {1: (309, 1694), 2: (1728, 3249), 3: (3284, 3672)}

PANEL_Y0, PANEL_Y1 = 112, 208
PANEL_H = PANEL_Y1 - PANEL_Y0
STABLE = 5          # consecutive frames before a panel counts as settled
STEP = 1            # look at every frame so runs are measured correctly


def panel_hash(im):
    """Noise-tolerant signature: 44x24 blocks quantised to 2 bits/channel."""
    small = im.resize((44, 24), Image.BILINEAR)
    bits = []
    for (r, g, b) in small.getdata():
        bits.append((r >> 6) << 4 | (g >> 6) << 2 | (b >> 6))
    return bytes(bits)


def hamming(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


def panel_present(im):
    """The parchment panel makes the bottom rows much brighter than a dark world."""
    px = im.load()
    tot = 0
    cnt = 0
    for y in range(150, 204, 6):
        for x in range(10, 166, 10):
            r, g, b = px[x, y][:3]
            tot += r + g + b
            cnt += 1
    return tot / cnt > 150


def main():
    os.makedirs(OUT, exist_ok=True)
    index = open(os.path.join(ROOT, "docs", "analysis", "dlg_panels.txt"), "w")
    for ch, (f0, f1) in sorted(RANGES.items()):
        emitted = []          # (frame, crop, hash) accepted in order
        run_hash = None
        run_crop = None
        run_frame = 0
        run_len = 0

        def flush():
            # emit the last stable crop if it settled and is new
            if run_crop is not None and run_len >= STABLE:
                h = run_hash
                for (_, _, old) in emitted:
                    if hamming(h, old) < 8:
                        return
                emitted.append((run_frame, run_crop, h))

        for f in range(f0, f1 + 1, STEP):
            im = Image.open(os.path.join(PNG, "Untitled_%06d.png" % f)).convert("RGB")
            if not panel_present(im):
                flush()
                run_hash, run_crop, run_len = None, None, 0
                continue
            crop = im.crop((0, PANEL_Y0, 176, PANEL_Y1))
            h = panel_hash(crop)
            if run_hash is not None and hamming(h, run_hash) < 8:
                run_len += 1
                run_crop, run_frame = crop, f   # keep the latest state
                run_hash = h
            else:
                flush()
                run_hash, run_crop, run_frame, run_len = h, crop, f, 1
        flush()

        n_sheet = 0
        for i in range(0, len(emitted), 4):
            chunk = emitted[i:i + 4]
            sheet = Image.new("RGB", (176 * 2, (PANEL_H * 2 + 18) * len(chunk)), (40, 40, 40))
            dr = ImageDraw.Draw(sheet)
            for j, (f, crop, _) in enumerate(chunk):
                y = j * (PANEL_H * 2 + 18)
                big = crop.resize((352, PANEL_H * 2), Image.NEAREST)
                sheet.paste(big, (0, y + 18))
                dr.text((6, y + 4), "ch%d frame %d" % (ch, f), fill=(255, 255, 0))
            n_sheet += 1
            sheet.save(os.path.join(OUT, "ch%d_sheet%02d.png" % (ch, n_sheet)))
        for f, _, _ in emitted:
            index.write("ch%d %d\n" % (ch, f))
        print("chapter %d: %d panels -> %d sheets" % (ch, len(emitted), n_sheet))
    index.close()


if __name__ == "__main__":
    main()
