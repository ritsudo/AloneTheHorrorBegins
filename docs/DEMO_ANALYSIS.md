# Demo analysis

Source: `alonehorror_demo_frames/` — 3823 frames, **176x208**, **10 fps**
(~382 s). Each frame exists as `.bmp` (32bpp) and `.png` with identical pixels.
Frames carry capture noise (consecutive diff mean ~0.2, max 3).

Segmentation was computed from downscaled frame signatures and saved to
`docs/analysis/`:
`diffs.json` (per-frame diff), `runs.json` (identical runs),
`cd.json` (change-descending boundaries), `dlg_groups.json` (dialogue groups),
`diff_report.txt` (threshold sweep).

## Timeline (frame ranges)

| Frames | Scene |
|--------|-------|
| 0–16 | Centerscore logo (black bg) |
| 17–47 | Title screen "ALONE / THE HORROR BEGINS" (dark blue night, walkers) + CENTERSCORE |
| 48–82 | Main menu, NEW GAME selected |
| 83–126 | Options / CONFIG pages |
| 127–174 | Main menu navigation |
| 175–183 | **LEVEL SELECT** — "LEVEL SELECT / ►CHAPTER 1◄" with candle cursor |
| 184–207 | **LOADING… / "YOUR FIRST INSTINCT SHOULD BE TO RUN."** |
| 208–287 | **CONFIG 2/3** — control mapping table (see below) |
| 288–308 | Chapter card "1: FALLEN FROM THE SKY" |
| 309–1694 | Gameplay chapter 1 |
| 1695–1727 | Chapter 2 loading |
| 1728–3249 | Gameplay chapter 2 "PARTING WORDS" |
| 3250–3283 | Chapter 3 loading |
| 3284–3672 | Gameplay chapter 3 "THE TREK WEST" |
| 3673–3809 | Pause / save / exit menus |
| 3810–3822 | Exit-game confirmation |

## Chrome / HUD / layout (measured)

- Screen 176x208. HUD strip y=0..20.
  - Heart + artery health at left `x 0..122`, alert `!` at `x≈84..96`, battery `x≈160..176`.
- Dialogue panel occupies the bottom **72 px** (`y=136..207`), full width.
  - Wooden frame ~6 px; parchment interior; name bar `y 137..154`;
    divider rule `y 155..159`; body text lines at `y 167,177,187,197` (height 9),
    left margin `x≈15`.
  - Speaker name right aligned to `x≈141`, `y≈143`.
  - Portrait at the top-right, head extends **above** the panel (`~x144..176, y120..158`).
  - Portraits seen: `YOU`, `JONATHAN`, `MAN`.
- Menu text rows at `y = 85,98,111,124,137,150` centred on `x≈88`;
  candle cursor drawn on **both sides** of the selected item (flame + grey holder).
- Font: bold serif, ALL CAPS, proportional, cap height ~9 px (Georgia Bold matches).

## Input mapping (from CONFIG 2/3 screen)

```
SEL / FIRE = 5        ACTION = 1
BACK       = 0        INFO   = 3
PAUSE      = *        LIGHT  = 1 (toggle)
FORWARD    = 2 ▲      BACKWARD = 8 ▼
TURN LEFT  = 4 ◄      TURN RIGHT = 6 ►
```

## Enemies / story beats

- **Howlers** — fear light, can be pushed back with the flashlight.
- **Walking dead** — immune to light.
- Items: flashlight, batteries, first-aid kit, key, cattle prod, cell phone.
- Chapters: `1 FALLEN FROM THE SKY`, `2 PARTING WORDS`, `3 THE TREK WEST`.
  Goal line: *"HEAD WEST… FIND ZOE…"*.

## Dialogue transcript (recovered excerpts)

Chapter 1:
- YOU: "UGHH... MY HEAD..." / "I MUST HAVE BEEN THROWN CLEAR OF THE PLANE." / "WHERE IS EVERYONE?"
- YOU: "SHOOT! MY FLASHLIGHT'S OUT!" / "THAT VOICE AGAIN!"
- JONATHAN: "HEY! OVER HERE!" / "LOOK FOR THE ORIGIN OF THE SOUND!"
- YOU: "WHAT WAS THAT HOWL?" — JONATHAN: "HOWLERS. KEEP YOUR LIGHT ON THEM, THEY HATE IT."
- Tutorial prompts: walk with `2`, review items, find the key.

Later chapters:
- JONATHAN: "I'M NOT GOING TO MAKE IT." / "TAKE THE PROD. IT'S ALL I HAVE LEFT."
- MAN: "YOU SHOULDN'T BE OUT HERE."
- Closing: "HEAD WEST... FIND ZOE..."

(the full raw groups are in `docs/analysis/dlg_groups.json`; readable contact
sheets were produced during analysis.)
