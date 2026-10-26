# ---------------------------------------------------------------------------
# dialogue_finalize.py - merge the raw vision transcript into a clean ordered
# script table.
#
# The raw transcript (docs/analysis/dlg_transcript_raw.txt) was transcribed
# from ordered contact sheets, so its line ORDER is reliable even where a
# frame label was misread. Real frame numbers come positionally from
# docs/analysis/dlg_panels.txt (the extractor's own index, same order).
# Consecutive duplicates and typewriter prefixes are collapsed.
#
# Output: docs/analysis/dlg_script.txt
#   ch1 320 N YOU STUMBLE ABOUT, ...
# ---------------------------------------------------------------------------
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "docs/analysis/dlg_transcript_raw.txt"
IDX = ROOT / "docs/analysis/dlg_panels.txt"
OUT = ROOT / "docs/analysis/dlg_script.txt"


def load_index():
    frames = {"ch1": [], "ch2": [], "ch3": []}
    for line in IDX.read_text().splitlines():
        m = re.match(r"(ch\d) (\d+)", line)
        if m:
            frames[m.group(1)].append(int(m.group(2)))
    return frames


def main():
    frames = load_index()
    raw = [l.rstrip("\n") for l in RAW.read_text().splitlines() if l.strip()]
    pos = {"ch1": 0, "ch2": 0, "ch3": 0}
    out = []          # (chapter, frame, speaker, text)
    for line in raw:
        m = re.match(r"(ch\d) (\S+) (\S+) (.*)", line)
        if not m:
            continue
        ch, _lbl, who, txt = m.group(1), m.group(2), m.group(3), m.group(4).strip()
        i = min(pos[ch], len(frames[ch]) - 1)
        frame = frames[ch][i]
        pos[ch] += 1
        who = "" if who.upper() == "NONE" else who.upper()
        txt = re.sub(r"\s+", " ", txt).strip().upper()
        if not txt:
            continue
        # collapse consecutive duplicates / typewriter prefixes
        prev = out[-1] if out else None
        if prev and prev[0] == ch:
            ptxt = prev[3]
            if txt == ptxt:
                continue
            if ptxt.endswith("...") and (txt.startswith(ptxt[:-3]) or txt.replace(" ", "").startswith(ptxt.replace(" ", "")[:-3])):
                out[-1] = (ch, prev[1], prev[2], txt)   # longer state of same line
                continue
            if txt.endswith("...") and ptxt.startswith(txt[:-3]):
                continue                                 # shorter state after long
        out.append((ch, frame, who, txt))

    with open(OUT, "w") as fh:
        for ch, frame, who, txt in out:
            fh.write("%s %d %s %s\n" % (ch, frame, who or "-", txt))
    print(f"{len(out)} script lines -> {OUT}")
    for ch in ("ch1", "ch2", "ch3"):
        n = sum(1 for l in out if l[0] == ch)
        print(f"  {ch}: {n} lines")


if __name__ == "__main__":
    main()
