# Alonehorror map recovery

Recovered layered maps and a map-editor SDK from three stitched game
screenshots. Everything is tile-cut on a 16x16 grid, deduplicated across
chapters, edited in an offline browser editor, and exported as a small
big-endian `.jmap` binary that a 2005-2007 CLDC 1.1 / MIDP 2.0 MIDlet can read.
The checked-in terrain is finalized from `maps_edited/` against the chapter-3
tile vocabulary and contains no objects or triggers yet.

![chapter 1 recovery](previews/chapter1.png)

## What is included

| Path | Description |
|---|---|
| `chapter1.png` ... `chapter3.png` | Original screenshots (also copied to `screenshots/`) |
| `sdk/` | Python recovery SDK: tile cutting, verified alignment, cleaning, codec, renderer, CLI |
| `sdk/jmap.py` | `.jmap` binary reader/writer (pure Python) |
| `sdk/recover.py` | Grid detection, marker/sprite detection, anomaly reporting |
| `sdk/tileset.py` | Stable expandable tile ids, auto classification, atlas generation |
| `sdk/finalize.py` | Terrain finalizer: chapter-3 remap, compact atlas, object-free export |
| `tools/finalize_project.py` | Rebuilds the checked-in project from `maps_edited/` |
| `maps_edited/` | Hand-edited source terrain (`chapter1_2`, `chapter2_1`, `chapter3_2`) |
| `editor/` | Offline single-page map editor (`index.html`, no server required) |
| `editor/jmap.js` | Browser codec byte-identical to `sdk/jmap.py` |
| `assets/tileset_grid.png` + `.json` | Final 8x8 type-sorted atlas and tile manifest |
| `assets/game_objects.json` | Unified item / enemy / trigger catalog used by the palette |
| `assets/reference_tileset.png` + `.json` | Frozen source atlas used for repeatable finalization |
| `maps/chapter*.jmap` | Finalized terrain-only binary maps |
| `maps/project.json` | Generated terrain report: offsets, empty object layers |
| `previews/` | Clean previews, collision overlays and anomaly overlays |
| `j2me/` | CLDC 1.1 / MIDP 2.0 reader, renderer and playable demo |
| `docs/FORMAT.md` | Byte-level `.jmap` specification |
| `tests/` | Python and Node test suites |

## Quick start

```powershell
pip install -r requirements.txt
python tools/finalize_project.py
start editor/index.html
```

`tools/finalize_project.py` rebuilds the compact atlas, finalized maps,
previews, `maps/project.json` and `editor/bundle.js` from `maps_edited/`.
The editor bundle embeds the atlas, source screenshots and map binaries as data
URIs, so `file://` works without a web server. The finalizer is repeatable: it
reads the frozen `assets/reference_tileset.*` source atlas, then rewrites the
compact `assets/tileset.*` output.

`tools/build_project.py` is the original screenshot recovery builder. It uses
the verified grid offsets by default; pass `--auto` for the heuristic detector,
or `--offsets 7,13;1,10;11,3` to override them.

Other useful commands:

```powershell
python -m sdk.cli validate --assets assets maps/chapter1.jmap maps/chapter2.jmap maps/chapter3.jmap
python -m sdk.cli render maps/chapter1.jmap --assets assets -o out.png --collision
python -m unittest discover -s tests -v
node tests/test_jmap_codec.js
```

## Recovery pipeline

1. **Grid phase.** The build uses verified offsets `(7,13)`, `(1,10)` and
   `(11,3)`. They are confirmed by the 32x16 chapter-3 window and by the green
   hedge rows, which now fall on single whole tiles instead of being split.
   `--auto` keeps the old exact-match heuristic as a fallback; it is not used
   for the checked-in assets.
2. **Tile cutting and IDs.** All cells are hashed. Identical cells get the same
   stable terrain id. The finalized atlas has 172 records (54 shared) and tile
   0 is empty (black/void). The ID ranges are reserved up front so new content
   never renumbers old content (`1..4095` terrain, `4096+` items, `4352+`
   enemies, `4608+` triggers, then expansion space - see `docs/FORMAT.md`).
3. **Clean-up.** Pure red/green annotation rectangles are converted to trigger
   objects (red = player spawn, green = level exit). Bright actor sprites are
   detected and their touched cells are replaced with the `broken_temp`
   checker texture. Each anomaly stores its donor tile ids, so Accept/Dismiss
   restores the background; the temporary texture is never silently kept.
4. **Collision.** Each unique tile is classified by colour (path/floor/snow =
   walkable; foliage/water/masonry/void = solid) to seed the collision layer.
   Every cell can be overridden in the editor.
5. **Manual fixes.** Screenshots contain baked-in props that no generic mask can
   classify. These are listed in `maps/project.json`, highlighted in the
   editor, and can be fixed by painting terrain, placing enemies/items, or
   changing the grid offset and re-slicing.

Chapter 3 has no green exit marker in the screenshot. The recovery builder
reports it as a warning; the finalized terrain-only maps intentionally have no
triggers yet.

## Terrain finalization

`python tools/finalize_project.py` is the current authoritative build step.
It reads the hand-edited maps in `maps_edited/` and uses the chapter-3 tile
vocabulary as the visual reference:

- Candidate tiles are the unique non-placeholder tiles used by `chapter3_2`.
- Chapter-1/2 tiles already present in that vocabulary are kept.
- Remaining chapter-1/2 tiles are replaced by the closest chapter-3 tile with
  the same collision class; a small kind penalty keeps foliage, trunks and
  paths from swapping roles.
- Empty/temporary cells are filled with the chapter-3 forest-floor tile `815`.
- Objects and markers are cleared; the final maps are terrain-only.
- The atlas is rebuilt from used tiles only, with fresh contiguous ids and no
  `broken_temp` slot.

The generated maps are `chapter1`, `chapter2` and `chapter3`, each with an empty
object layer ready for item/enemy/trigger placement.

## Editor

Open `editor/index.html` after running the builder.

- **Layers:** terrain, collision, objects (items / enemies / triggers) and
  anomalies.
- **Tools:** brush, eraser, flood fill, tile picker, undo/redo (60 steps),
  right-click erase.
- **Terrain palette:** filters for tiles used by the current map, tiles shared
  between chapters, all tiles, and unique tiles; search by id/name/kind.
- **Objects:** trigger palette includes red spawn and green exit. Accepting an
  anomaly creates/clears the matching object.
- **Anomalies panel:** focus, accept or dismiss each detected sprite. Accept
  and Dismiss both restore the stored donor background; Accept also keeps the
  suggested enemy/item object. "Accept all" does this for the whole map.
- **Warnings:** missing spawn/exit, unresolved anomalies, alignment confidence.
- **Offset + Re-slice:** cut the active screenshot again with a corrected
  16x16 phase. Newly discovered tiles are appended to the atlas and exported
  with the tileset.
- **Pre-render PNG:** renders the whole map at 1:1 to a downloadable PNG,
  including triggers/objects.
- **Export `.jmap`:** saves the active map in the J2ME binary format.
- **Export tileset:** downloads an updated `tileset.json` + `tileset.png`.
- **Clean garbage:** removes every tile that is no longer referenced by any
  map or unresolved anomaly, zeroes its atlas slot, and refreshes the palette.
  Use it after accepting/reassigning temporary broken textures.
- **Source overlay:** shows the original screenshot on top of the recovered
  map for quick misalignment checks.

Useful shortcuts: `1..4` layers, `B/E/F/I` brush/erase/fill/pick, `G` grid,
`Ctrl+Z` / `Ctrl+Y`, `Ctrl+S` export map, `Space`+drag or middle-drag to pan,
mouse wheel to zoom.

## Binary format

- Header: `JMAP`, version, compression flags, layer mask, tile size, width,
  height, object count, UTF-8 name.
- Terrain layer: `u16` tile ids, optionally RLE (`u16 value, u16 run`).
- Collision layer: one collision byte per cell, optionally RLE.
- Objects: 10-byte records (`kind u8, type u16, x u16, y u16, flags u8,
  param u16`).
- Big endian, no floating point, no external compression library.

Full layouts and ID ranges: [`docs/FORMAT.md`](docs/FORMAT.md).

## J2ME runtime

`j2me/src/jmap/` contains:

- `JMap.java` - a strict loader with RLE decoding and collision helpers.
- `JMapRenderer.java` - `Image` / `Graphics.drawRegion` renderer using the
  atlas layout above.
- `JMapDemo.java` - a playable MIDlet: arrows move, solid collision blocks,
  the green exit returns to the red spawn.

See [`j2me/README.md`](j2me/README.md) for JAD properties and packaging notes.
Generated maps and the atlas are copied to `j2me/res/`.

## Generated recovery summary

| Map | Size | Offset | Objects | Anomalies | Binary |
|---|---|---:|---:|---:|---:|
| chapter1 | 30x27 | 7,13 | 0 | 0 | 1863 B |
| chapter2 | 44x11 | 1,10 | 0 | 0 | 955 B |
| chapter3 | 36x24 | 11,3 | 0 | 0 | 1995 B |

Atlas: 171 tile records (54 shared) plus the empty id-0 slot, 1024x48 RGB PNG.
The finalized project contains no `broken_temp` cells. These numbers are
regenerated in `build-summary.json` and `maps/project.json`.

## Known limitations

- Terrain finalization is a nearest-tile visual remap, not a semantic
  reconstruction. Review `previews/*.png` after changes; the chapter-3
  vocabulary has many one-off transition tiles.
- The screenshots are painterly, so a 16x16 grid cannot make every sprite
  cleanly separable. The recovery builder still uses `broken_temp` for actor
  cells; the finalized terrain fills those cells with tile `815`.
- The `--auto` chapter-3 phase is still unreliable because its art palette
  shares almost no exact tiles with chapters 1-2. The verified offset `(11,3)`
  is used instead.
- Collision is derived from the finalized tile metadata, not from a hand-made
  tile pass. Review `previews/*_collision.png` before placing gameplay objects.

## Session 3 recovery tools (game-accurate tile pipeline)

The montages turned out to be painterly concept art (16px cells do not
repeat at any phase), so the tile vocabulary now comes from the native demo
frames and the montages provide layout only:

| Tool | Purpose |
|---|---|
| `tools/phase_scan.py` | duplicate-maximising 16px grid phase per screenshot |
| `tools/extract_tiles.py` | stride-1 window sampling of gameplay frames, frequency counting |
| `tools/cluster_tiles.py` | feature leader-clustering of candidates -> `assets/game_tiles.png` (top N) |
| `tools/stitch_frames.py` | camera tracking + per-cell voting -> `assets/cells_<ch>.npy`, `stitched_<ch>.png` |
| `tools/rebuild_maps.py` | full map build: montage slice -> sprite inpaint -> engine-cell overlay -> vocabulary reduction -> collision/objects -> `../../res/chapter*.jmap` |

`tools/dialogue_recover.py` / `dialogue_finalize.py` (in the game's
`tools/`) recover the verbatim script into `docs/analysis/dlg_script.txt`.
