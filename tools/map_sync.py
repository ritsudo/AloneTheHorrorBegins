"""Rebuild the runtime chapter maps from the finalized SDK terrain plus the
hand-placed gameplay objects.

The SDK finalizer intentionally exports terrain-only maps with its compact
chapter-3 tile vocabulary (sdk-map-editor/maps/chapter*.jmap + assets/tileset.png).
The runtime maps in res/ keep the item/enemy/trigger records that were placed in
the editor, so this script merges the two for chapters 2 and 3: final terrain and
collision from the SDK, objects from the current res/ maps (coordinates share the
same world origin). It also refreshes res/tileset.png from the SDK atlas.
Chapter 1 uses the higher-fidelity tools/ch1_exact.py pipeline instead.

Run from the project root:  python tools/map_sync.py
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SDK = ROOT / "sdk-map-editor"
sys.path.insert(0, str(SDK))

from sdk.jmap import load_map, save_map  # noqa: E402

# chapter 1 is produced by tools/ch1_exact.py (near-pixel-exact atlas); this
# script only refreshes the SDK-based chapters.
CHAPTERS = (2, 3)


def main():
    atlas = SDK / "assets" / "tileset.png"
    shutil.copyfile(atlas, ROOT / "res" / "tileset.png")
    for chapter in CHAPTERS:
        terrain = load_map(SDK / "maps" / f"chapter{chapter}.jmap")
        runtime = load_map(ROOT / "res" / f"chapter{chapter}.jmap")
        objects = [
            obj
            for obj in runtime.objects
            if 0 <= obj.x < terrain.width and 0 <= obj.y < terrain.height
        ]
        merged = load_map(SDK / "maps" / f"chapter{chapter}.jmap")
        merged.name = f"chapter{chapter}"
        merged.objects = objects
        save_map(merged, ROOT / "res" / f"chapter{chapter}.jmap")
        print(
            f"chapter{chapter}: {merged.width}x{merged.height} "
            f"terrain from SDK, {len(objects)} objects"
        )


if __name__ == "__main__":
    main()
