# Progress

## Objective

Recreate the lost Centerscore J2ME game **Alone: The Horror Begins** as a
MIDP 2.0 / CLDC 1.1 MIDlet for a 176x208 device, reverse-engineered from a
3823-frame storyboard capture (`alonehorror_demo_frames/`). Anything the demo
never shows is generated procedurally.

## Session 7 (v1.0.3: howler retreat + audio freeze)

- The howler light test now uses the actual beam pool position (ahead of the
  player), so lighting a howler starts the retreat reliably; retreating
  howlers cannot deal contact damage and die after ~3 tiles.
- MIDI cues are cached/prefetched once and restarted with `setMediaTime(0)`.
  Several howls/zombie sounds no longer recreate the decoder on the game thread,
  which caused the freeze.

## Session 6 (v1.0.2: audio, tank controls, enemy sheets)

- Single MIDI channel (`AudioManager`): looping `main_theme.mid` from the logo
  until gameplay, restart on return to the main menu, one-shot
  `game_over.mid`/`zombie.mid`/`howler1/2.mid`/`enemy_death.mid`; a new cue
  stops and unloads the previous one.
- Tank controls: 4/6 rotate, 2/8 move forward/backward.
- New enemy sheets: `howler_full.png` (10 frames), `zombie_full.png` (4x4) and
  `death_full.png` (8-frame burst). Howlers ignore walls/weapons, howl when
  behind the player and retreat three tiles when lit while faced.
- Pause menu uses `page_pause.png`; campfire moved up 10 px.
- MIDlet vendor is `Centerscope ritsudo`, version `1.0.2`.

## Session 5 (final recovered terrain + SDK object integration)

- **Final terrain/maps integrated** - `sdk-map-editor/assets/tileset_grid.*`
  and `sdk-map-editor/maps/chapter*.jmap` are now the source of truth;
  `tools/integrate_final.py` copies them to `res/` and the SDK bundle.
- **Unified object catalog** - `sdk-map-editor/assets/game_objects.json` defines
  every item (medkit/ammo/key/note/battery/flashlight/prod/crowbar/gun), enemy
  and trigger in one place. The editor bundle carries it, so the object palette
  is populated and items/enemies/triggers can be placed and edited (type, x, y,
  param, flags).
- **New story triggers** - `talk_jonathan` (4612), `door_crowbar` (4613).
  Chapter 1 ends by talking to Jonathan; chapter 2 runs right-to-left and ends
  at the left edge; chapter 3 starts right, requires the crowbar, and the red
  barn doors end the demo.
- **Ending screen** - `EndingScene` shows the restoration credits and returns
  to the menu.

## Session 4 (grid atlas + map/editor repair)

- **8x8 grid atlas** - `res/tileset_grid.png` replaces the 64x1 strip; ids are
  now row-major (`id = row * 8 + column`) and the tiles are grouped by kind
  (roads, rocks, foliage, stone/wood, barn). `TileMap`/`Assets` load it directly.
- **Maps rebuilt** - `tools/build_grid.py` remaps every terrain id, rebuilds
  collision (chapter 1 from `ch1_solid.txt`, chapters 2-3 from tile classes) and
  writes clean JMAP layers so the object table is read at the right offset. All
  chapters have a real `player_spawn` (chapter 1 at the red square, tile 12,25)
  and a level exit; the spawn->exit path is connected on every map.
- **Cutscenes fixed** - the corrupt collision payloads used to shift the object
  layer, so map items were taken while cutscene triggers were misread. The maps
  now expose their `cutscene` records with params 1..5, indexing `Script.java`.
- **Editor bundle rebuilt** - `editor/bundle.js` embeds the new atlas and maps,
  the object palette lists all items (medkit/ammo/key/note/battery/flashlight/
  prod/crowbar/gun), enemies and triggers, and the inspector can edit an
  object's type/x/y/param/flags (cutscene params, spawn points, counts).
- **New item ids** - `4103` crowbar and `4104` gun added next to the existing
  item range; `Script` maps them to `Item.CROWBAR` / `Item.GUN`.

## Latest session (build recovery + fidelity pass)

- **Build fixed** — `World.readResource()` used a class literal
  (`World.class.getResourceAsStream`), which the JDK 8 `-source 1.4` compiler
  rejects against CLDC (`initCause` fatal error). It now uses the instance
  `getClass()` form; `build.ps1` also waits out the emulator/antivirus JAR lock
  instead of failing midway.
- **Runtime maps repaired** — the checked-in `res/chapter*.jmap` were exported
  before the SDK terrain finalizer and referenced the wrong atlas (parchment
  tiles in the forest). `tools/map_sync.py` now merges the finalized SDK terrain
  with the hand-placed objects for chapters 2-3 and refreshes the atlas.
- **Chapter 1 near-pixel-exact** — `tools/ch1_exact.py` rebuilds the world from
  `tools/ch1_map.png` (605 unique cells → 527 tiles, 34x30) and writes a
  dedicated `res/tileset_ch1.png` (1024x144, 116 KB). The in-game art now
  matches the painted demo composite instead of the chapter-3 remap.
- **Image refinements** — body font narrowed to match the demo's line breaks;
  the title font is now tall/condensed like the source; menu rows, level-select,
  chapter card and candle positions aligned to the capture; the dialogue panel
  body sits at y=167..205 exactly and the bottom border no longer clips the last
  line; the battery gauge draws its red charge cells.
- **Flow fixes** — CONFIG 2/3 is shown only before chapter 1 (as in the demo);
  later chapters go straight from LOADING to the chapter card.
- Screenshots from the current build: `docs/reference/emu2/final_*.png`.

## Done

- **Demo analysed** — segmented into scenes, measured chrome/HUD/font, recovered
  the dialogue transcript and the control mapping. See `DEMO_ANALYSIS.md`.
- **Asset pipeline** — Python generators in `tools/` produced all 39 files in
  `res/` (screens, panel, portraits, HUD, candles, sprites, tiles, items,
  lighting masks, three font atlases, icon). See `ASSETS.md`.
- **Game code** — 24 Java classes in `src/` (default package): MIDlet, canvas
  game loop, 8 scenes, world/entities, dialogue box, HUD, proportional font,
  script data. See `ARCHITECTURE.md`.
- **Chapter 1 map recovered** — the full world is the painted composite
  `alonehorror_demo_frames/assembly_example/map_recovery.png` (537x479, 1:1 with
  the demo). `tools/map_recover.py` cleans the two baked-in survivor sprites,
  writes `tools/ch1_map.png` (palette source, void → black), derives a 34x30
  collision grid (`tools/ch1_solid.txt`) and a checking preview.
- **Tile system (binary levels)** — `tools/ch1_exact.py` slices `ch1_map.png`
  on the 16px grid, merges near-identical cells (605 unique → 527 tiles) and
  packs them into `res/tileset_ch1.png`; every painted corner and colour
  transition is reproduced (only isolated 1-2px merge artefacts remain).
  Terrain, collision and the 10-byte object records are written to the shared
  `JMAP` format (`res/chapter*.jmap`); `TileMap`/`World` read it and fall back to
  a flat walkable box when a map is unavailable. Chapters 2-3 use the SDK
  terrain maps and the compact `res/tileset.png` atlas.
- **Build** — `build.ps1` (javac 1.4 target → WTK `preverify` → `jar`) produces
  `bin/AloneTheHorror.jar` (≈451 KB) and `.jad`.
- **Runtime verified** (before the emulator stop-order) — logo → title → menu →
  options → level card → loading → gameplay with HUD and typewriter dialogue →
  dark flashlight world; screenshots in `docs/reference/`.
- **Documentation** — `README.md`, `DEMO_ANALYSIS.md`, `ASSETS.md`,
  `ARCHITECTURE.md`, this file, `CONTINUE_HERE.md`, `tools/README.md`.

- **UI polish pass (level 1)** — `res/sign.png` extracted from the menu art so
  `menu_bg` is now composed at runtime (`page.png` + ALONE overlay); a single
  animated brazier strip `res/campfire.png` (extracted from the demo, 10 frames)
  flanks the selected entry on both sides with the gap derived from the label
  width; dialogue/name boxes are now built from `page.png` itself (ornate top +
  bottom borders, tiled paper interior) so `panel.png`/`panel_narr.png` are
  gone; fonts reduced to two natural-width serif sizes (body 13, title 18, no
  horizontal   squish) replacing the five squished atlases; the darkness masks are hard 1-bit
  masks (full bright inside the radius, then a Bayer 4x4 dither of solid black
  pixels). Shared helpers live in
  `src/Ui.java`; generators in `tools/ui_gen.py`, `tools/font_gen.py`,
  `tools/light_gen.py`.

## Next-chapter material (demo2)

`alonehorror_demo_frames/additional_screens/demo2/` is a 600-frame, 120x146
capture of **Chapter 2 (the barn)**. It shows: the red barn exterior with
"DOOR IS JAMMED SHUT!", "I SHOULD CHECK BEHIND THE BARN.", a top-down barn
overview/map (roof, fence, hay bales, ladder, trough), a crowbar pickup
("YOU FOUND A CROWBAR." / "I CAN OPEN THE DOOR WITH THIS!"), a green walker, and
the same named/narration dialogue boxes. Use it as the reference for chapter 2
art, map and script.

## Known limitations

- Chapter 1's tiles are near pixel-exact (527 tiles from 605 cells); only
  isolated 1-2px merge differences remain. Collision comes from the recovered
  `tools/ch1_solid.txt` grid and is approximate (void/foliage block, paths and
  floors walk). Chapters 2-3 use the SDK terrain finalizer (chapter-3 tile
  vocabulary), so they are faithful in layout but not pixel-identical.
- Lighting: cut scenes/dialogue use the wide 180/160 masks, gameplay a tight
  140 (flashlight) or 110 (ambient) blob. Two wobble variants plus a rotation
  per facing make the overlay shift as the player moves; it is still a
  screen-space mask, not a per-tile light field.
- `res/page.png` is a reconstructed blank page; the inpaint can show faint
  horizontal banding where the source texture tiles.
- Sound is not implemented (no audio was recoverable from the capture).
- The emulator **must not be run on this VM** — it has crashed the VM (VMware
  RAM fault). Build steps are safe; run only on a machine with >= 6 GB RAM.

## Not implemented / possible next work

- In-game MAP / INVENTORY / NOTES screens (the demo mentions them on the `9`
  key). The data exists in the objects/flags; only the UI is missing.
- Save/load is a single RMS record (`RecordStore "alone"`); no named slots.
- Sound is still not implemented (no audio was recoverable from the capture).

## Build

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1        # build
powershell -ExecutionPolicy Bypass -File build.ps1 -Run   # build + emulator
```

Toolchain on this machine: JDK 1.8 (32-bit) at `D:\Java\jdk1.8.0_131`,
WTK 2.5.2 at `D:\Java\WTK2.5.2_01` (the paths hard-coded at the top of
`build.ps1`). Python 3 + Pillow + numpy are needed for `tools/`.

## Recovery rebuild (session 3)

- **Exact plot recovered** - every distinct dialogue panel was extracted from
  the demo capture (typewriter-state aware), transcribed via vision and
  merged into `docs/analysis/dlg_script.txt` (58 lines, real frame numbers,
  verbatim caps). The real chapter 1 story is the crashed plane / delivery
  manifest / heavy cage hook / deserted village with one lit window;
  chapter 2 is the mountain tunnel, torch and avalanches; chapter 3 is the
  stranger who helps the freezing player. The old Jonathan/Zoe draft text
  was replaced by these lines in `src/Script.java`.
- **True tileset extracted from the game render** - the level montages are
  painterly concept art (their 16px cells do not repeat at ANY grid phase;
  best phase gives only ~26% duplicate cells), so they cannot yield the
  game's tile vocabulary. `sdk-map-editor/tools/extract_tiles.py` samples
  every 16px window of the native 176x208 gameplay frames and counts
  brightness-normalised signatures; `cluster_tiles.py` reduces the 31k
  frequent candidates to the dominant families. The top 128
  (`sdk-map-editor/assets/game_tiles.png`) were vision-validated as a
  coherent period tileset (forest floor / paths with corners / water /
  planks / set pieces).
- **Map rebuild** (`sdk-map-editor/tools/rebuild_maps.py`) - slices the
  montages at the duplicate-maximising phases, inpaints the baked actor
  sprites from clean neighbours, overlays the engine-truth cells stitched
  from the demo frames (`tools/stitch_frames.py`: camera tracking on the
  lit pool with the player masked), then reduces every cell onto the
  extracted vocabulary (feature matching, shift/dim tolerant) with a
  bounded set of special tiles for set pieces. Writes `res/chapter*.jmap`
  (terrain + collision + objects) and `res/tileset.png`.
- **Per-chapter atlas** - chapter 1 now uses its own near-exact atlas
  `res/tileset_ch1.png` (526 tiles) selected via `TileMap.useAtlas`; the
  shared 169-tile atlas serves chapters 2-3. Both are palette PNGs.
- **Runtime** - `TileMap` reads the JMAP binary (RLE terrain/collision,
  10-byte object records); `World.load` pulls the map from the JAR with
  `getClass().getResourceAsStream` (instance form; the class-literal form
  trips the CLDC `NoClassDefFoundError.initCause` compile error, and static
  byte[] embedding exceeds the 32 kB method limit). Items/enemies/cutscene
  triggers spawn from the map object layer; cutscene params index the
  transcript tables in `Script.java`; new trigger actions ACT_TORCH and
  ACT_DAMAGE cover the chapter 2 torch lighting and avalanches.
- **Verified in the WTK emulator** - menu -> level select -> loading ->
  config -> gameplay for chapters 1-3: tiles, player sprite, flashlight
  pool (lit-area fraction matches the demo), HUD and the verbatim dialogue
  all render; screenshots in `docs/reference/emu2/`.
- JAR is ~420 KB with both atlases.

### Build note

`powershell -File build.ps1` is currently blocked from this Git Bash session
(returns -1 with no output; `-Command` works). The same pipeline runs
directly: javac (1.4 target, CLDC bootclasspath) -> WTK preverify -> copy
res -> jar/jad. `tools/emu_driver.py` drives the emulator and captures the
176x208 MIDlet area without PowerShell.
