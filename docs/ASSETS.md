# Assets (`res/`)

Every image is a PNG. Runtime paths are relative to the JAR root
(`/name.png`), with a `/res/name.png` fallback.

## Extracted from the demo

| File | Size | Source |
|------|------|--------|
| `logo.png` | 176x208 | baked frame 8 — Centerscore logo |
| `title.png` | 176x208 | baked frame 30 — ALONE / THE HORROR BEGINS title |
| `page.png` | 176x208 | median of level/config screens 176-288, text inpainted |
| `sign.png` | 153x64 | ALONE wordmark overlay, diffed out of the menu art |
| `campfire.png` | 200x32 | 10-frame brazier strip (menu selection cursor) |
| `p_you.png` `p_jonathan.png` `p_man.png` | ~32x34 | speaker portraits |
| `hud_heart.png` | 60x20 | health icon (heart + artery origin) |
| `hud_vein.png` | 62x20 | health bar (clipped by health %) |
| `hud_alert.png` | 16x20 | red danger `!` |
| `hud_batt.png` | 18x20 | battery gauge outline (charge cells are drawn at runtime) |
| `AloneTheHorror.png` | 32x38 | MIDlet icon (title crop) |
| `player_walk.png` | 84x200 | 8 directions x 6 frames, 14x25 |
| `howler_full.png` | 200x24 | howler: 10 frames, 20x24 |
| `zombie_full.png` | 56x96 | walker: 4x4 frames, 14x24 |
| `death_full.png` | 256x32 | 8-frame enemy death burst, 32x32 |

## Map atlases

| File | Size | Notes |
|------|------|-------|
| `tileset_grid.png` | 128x128 | 8x8 type-sorted atlas used by all chapters |
| `chapter1.jmap` | 2575 B | 34x30, terrain + recovered collision + objects |
| `chapter2.jmap` | 1091 B | 44x11, terrain + collision + objects |
| `chapter3.jmap` | 2015 B | 36x24, terrain + collision + objects |

All chapters use `tileset_grid.png`. Tiles are grouped by type (roads, rocks,
foliage, stone/wood, barn) and ids are row-major:
`sx = (id % 8) * 16`, `sy = (id / 8) * 16`. `TileMap` derives the column count
from the atlas width, so the loader still works with any square grid atlas.

## Generated procedurally / by the tools

| File | Tool | Notes |
|------|------|-------|
| MIDI cues | — | `main_theme.mid`, `game_over.mid`, `zombie.mid`, `howler1/2.mid`, `enemy_death.mid` |
| `bush.png` | `sprite_gen.py` | prop |
| `item_key.png` `item_medkit.png` `item_batt.png` | `sprite_gen.py` | pickup icons |
| `font.png` `font_red.png` `font_cream.png` | `font_gen.py` | body font: Times Bold 13 at 92% width, metrics in `src/FntData.java` |
| `font_big.png` | `font_gen.py` | title font: Times Bold 18, 85% wide / 125% tall, metrics in `src/FntDataBig.java` |
| `light_g0/1.png` `light_gs0/1.png` | `light_gen.py` | gameplay masks (flashlight / ambient), two wobble variants |
| `tileset_grid.png`, `chapter*.jmap` | `tools/integrate_final.py` | final recovered 8x8 atlas, maps and story triggers |
| `sdk-map-editor/assets/game_objects.json` | `tools/integrate_final.py` | unified item/enemy/trigger catalog |
| `sdk-map-editor/editor/bundle.js` | `tools/integrate_final.py` | editor bundle with atlas, maps and object palette |

## Regenerating

```powershell
python tools\extract_assets.py   # demo-derived screens, portraits, HUD, player
python tools\sprite_gen.py       # sprites + props
python tools\font_gen.py         # font atlases + FntData*.java
python tools\light_gen.py        # light masks
python tools\ui_gen.py           # sign.png + campfire.png
python tools\integrate_final.py   # final atlas/maps + object catalog + editor bundle
```

Then rebuild the JAR with `build.ps1`.
