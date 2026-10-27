# Architecture

All classes live in the **default package** (no `package` statement); the MIDlet
class is named `horror` to match `bin/AloneTheHorror.jad`:
`MIDlet-1: AloneTheHorror, AloneTheHorror.png, horror`.

## Core

| Class | Responsibility |
|-------|----------------|
| `horror` | `MIDlet`. Creates `Game`, sets it current, forwards lifecycle. |
| `Game` | `Canvas implements Runnable`. Owns the render buffer (176x208), the frame loop (~25 fps), the active `Scene`, input dispatch, global player state (health/battery/flags/chapter) and RMS save/load. Letterboxes the 176x208 buffer to the real screen size. |
| `Scene` | Abstract base: `enter()`, `update()`, `paint(g)`, `keyPressed(key,action)`, `keyReleased(key)`. |
| `Assets` | Static lazily-loaded image cache (`ensure()`), all bitmaps listed in `ASSETS.md`. |
| `Fnt` | Proportional bitmap text. Draws glyphs with `drawRegion` from a pre-tinted atlas; provides `width`, `draw`, `drawCenter`, `drawRight`, `wrap`. |
| `FntData` | Auto-generated glyph metrics (`GX/GY/GW/ADV/H`). |

## Scenes

| Class | Responsibility |
|-------|----------------|
| `LogoScene` | Centerscore logo, then hands off to the title. |
| `ImageScene` | Generic "show a baked screen for N frames" (used for the title). |
| `MenuScene` | Main menu (NEW GAME / STAT'S / OPTIONS / HELP / ABOUT / EXIT) plus the OPTIONS, HELP, ABOUT, STAT'S sub pages drawn on a parchment page. |
| `LoadingScene` | Parchment loading page with a rotating tip, then the chapter card. |
| `ChapterScene` | "CHAPTER n / NAME" card. |
| `PlayScene` | Exploration state (see below). |
| `PauseScene` | Overlay RESUME / SAVE / OPTIONS / MAIN MENU drawn over a frozen frame. |
| `EndScene` | Exit confirmation. |
| `EndingScene` | Demo ending card after the chapter-3 red doors (credits text). |

`PlayScene` can be re-entered (PauseScene → resume) because world building is
guarded by an `inited` flag.

## World / entities

| Class | Responsibility |
|-------|----------------|
| `World` | Loads a `.jmap` through `TileMap`, finds the spawn/exit triggers and exposes collision/painting. All chapters use the 8x8 grid atlas `tileset_grid.png`. `dark` toggles the lighting pass; `lightRadius` is used by enemy AI. Resources are read with `getClass().getResourceAsStream()` (CLDC has no working class-literal form under JDK 8 `-source 1.4`). |
| `TileMap` | JMAP reader (terrain ids, collision bytes, 10-byte object records), RLE decoding and camera-aware drawRegion renderer. Terrain id `N` is drawn from column `N % 8`, row `N / 8` of `tileset_grid.png`. |
| `Player` | Position, 8-direction facing, 6-frame walk animation (14×25 px cells in `player_walk.png`), `step`/`idle`, aim helpers and sheet drawing. |
| `Enemy` | `HOWLER` (ghost: ignores walls/weapons, projects a howl marker when behind the player and retreats about three tiles when lit while faced) and `WALKER` (collides, chases, can be shot or stabbed). Both use `*_full.png` sheets and the 8-frame `death_full.png` burst. |
| `Item` | KEY / MEDKIT / BATTERY / FLASHLIGHT / PROD; pickup message. |
| `Trigger` | Rect that fires a conversation once, with an optional action (`ACT_DARK`, `ACT_FLASHLIGHT`, `ACT_BATTERY`, `ACT_END`). |
| `DLine` | One dialogue line: portrait id, speaker label, text. |
| `Dialogue` | The wooden box: portrait, right-aligned speaker name, typewriter body text (2 chars/tick). `advance()` → next line / finish. |
| `Hud` | Heart+artery health, danger `!`, battery gauge + charge strip. |
| `Script` | Turns the map object layer into items/enemies/triggers and holds every transcribed dialogue line. Cutscene triggers are indexed by their JMAP `param`. Story trigger ids: 4612 `talk_jonathan`, 4613 `door_crowbar` (needs `Game.hasCrowbar`). |

## Frame flow

`Game.run()` → `scene.update()` → draw into `buffer` → `scene.paint(buffer.getGraphics())`
→ `repaint()`/`serviceRepaints()` → `paint()` blits `buffer` centred on screen → sleep 40 ms.

## Lighting

`PlayScene.applyLight()` fills the area outside a square around the player with
opaque black, then draws `light_g*` (flashlight, 72x72, R=36) or `light_gs*`
(ambient, 110x110, R=55) inside it. The pool is shifted in the current facing
direction (including diagonals) and stays there when the player stops. Two wobble variants are picked from the
player tile. Entities are drawn *before* the mask so they darken with the world;
the HUD is drawn after so it stays readable. Enemy AI uses `lightRadius = 80`
to decide what a howler considers lit.

## Keys

Tank controls: `KEY_NUM4/6` (or D-pad left/right) rotate, `KEY_NUM2/8`
(or D-pad up/down) move forward/backward, `KEY_NUM5`/fire = interact,
`KEY_NUM1/3` = flashlight, `KEY_STAR` = pause, `-6` (F1) = back/cancel.

`AudioManager` owns the single MIDI channel: it loops `main_theme.mid` from the
logo/menu, stops and unloads it when a `PlayScene` starts, and restarts it when
the player returns to `MenuScene`. Starting any other cue stops the previous
one immediately.
