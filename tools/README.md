# tools

Python 3 asset pipeline (needs **Pillow** + **numpy**) and emulator helper
scripts. These are development-time only — the MIDlet never runs them.

> **Paths are absolute.** Every generator hard-codes `RES`, and most also `FR`
> / `FRAMES`, pointing at this project on *this* machine. Edit those constants
> (top of each file) after moving the project to another machine.

## Asset pipeline

| Script | Reads | Writes |
|--------|-------|--------|
| `extract_assets.py` | `alonehorror_demo_frames/png/` | `logo.png title.png menu_bg.png page.png paper.png panel.png p_you.png p_jonathan.png p_man.png hud_*.png candle_l.png candle_r.png AloneTheHorror.png` |
| `sprite_gen.py` | — (seeded RNG) | `player.png howler.png walker.png bush.png item_*.png` |
| `font_gen.py` | `C:\Windows\Fonts\timesbd.ttf` | `font.png font_red.png font_cream.png font.txt` **and `src/FntData.java`** |
| `light_gen.py` | — | `light.png light_s.png` (cut scenes) + `light_g0/1.png light_gs0/1.png` (gameplay) |
| `page_gen.py` | `alonehorror_demo_frames/png/` | `page.png` (blank page bg) |
| `map_recover.py` | `assembly_example/map_recovery.png` | `ch1_map.png` (clean 537x479 palette source), `ch1_solid.txt`, preview |
| `ch1_exact.py` | `ch1_map.png` + `ch1_solid.txt` + `ch1_objects_sdk.json` | legacy exact atlas + `res/chapter1.jmap` |
| `integrate_final.py` | `sdk-map-editor/assets/tileset_grid.*` + `maps/*.jmap` | `res/tileset_grid.png`, `res/chapter*.jmap`, `assets/game_objects.json`, editor bundle |
| `ch1_exact.py` | recovered chapter-1 painting | legacy chapter-1 atlas/map (not used after the final recovery) |
| `map_sync.py` | `sdk-map-editor/maps/*.jmap` + current `res/chapter2-3.jmap` | `res/tileset.png` + `res/chapter2-3.jmap` (SDK terrain + objects) |
| `tile_map.py` | `ch1_map.png` + `ch1_solid.txt` | legacy `ch1.tiles.N.png`, `ch1.map`, `src/Ch1Data.java` (not used by the JMAP runtime) |
| `font_extract.py` | demo frames | scratch: recovered glyph metrics (input to `font_gen.py`) |
| `verify_font.py` | `res/font.png` + `res/font.txt` | scratch: glyph-box debug report |

Typical full rebuild:

```powershell
python tools\extract_assets.py
python tools\sprite_gen.py
python tools\font_gen.py      # also rewrites src\FntData*.java
python tools\light_gen.py
python tools\page_gen.py
python tools\map_recover.py   # only if re-deriving ch1_map.png
python tools\build_grid.py    # 8x8 grid atlas + clean maps + editor bundle
```

Then rebuild the JAR with `build.ps1`.

## emu/ (screenshot automation)

PowerShell helpers used to drive the WTK emulator and grab stills:

| Script | Purpose |
|--------|---------|
| `emu.ps1` | launch the emulator on the built JAD |
| `appact.ps1` | activate the emulator window (`AppActivate "DefaultColorPhone"`) |
| `act.ps1` | send keys via `SendKeys` |
| `listwin.ps1` | list top-level windows |
| `capture.ps1` / `capture2.ps1` | capture the emulator window to a PNG |

> **WARNING** — do **not** run the emulator on a low-RAM machine (it has crashed
> the dev VM). Use only where >= 6 GB RAM is available.
