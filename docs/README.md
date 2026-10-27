# Alone: The Horror Begins — J2ME rebuild

A reconstruction of the lost Centerscore survival-horror mobile game
`Alone: The Horror Begins`, rebuilt as a MIDP 2.0 / CLDC 1.1 MIDlet for a
176x208 Sony-Ericsson class device.

The original binary survives only as a **3823-frame storyboard capture**
(`alonehorror_demo_frames/`, 176x208, 10 fps). All art, the script and the
game logic in this project were reverse-engineered from those frames and, where
the demo showed nothing, generated procedurally.

---

## Quick start

```powershell
# build only
powershell -ExecutionPolicy Bypass -File build.ps1

# build + launch the WTK emulator
powershell -ExecutionPolicy Bypass -File build.ps1 -Run
```

Outputs: `bin\AloneTheHorror.jar` + `bin\AloneTheHorror.jad` (MIDlet class `horror`).

> **WARNING** — running the Sun WTK emulator has been observed to crash the
> development VM (VMware RAM fault). Do **not** run the emulator unless the VM
> has plenty of RAM (>= 6 GB). The build itself is lightweight and safe.

## Toolchain

| Tool | Path on this machine |
|------|----------------------|
| JDK (32-bit) | `D:\Java\jdk1.8.0_131\bin` |
| WTK 2.5.2 | `D:\Java\WTK2.5.2_01` (`bin\preverify.exe`, `bin\emulator.exe`, `lib\cldcapi11.jar`, `lib\midpapi20.jar`) |

The paths are hard-coded at the top of `build.ps1`; edit them after moving the
project to another machine.

Boot classpath used by the build:
`cldcapi11.jar;midpapi20.jar;mmapi.jar;jsr75.jar`.

## Project layout

```
AloneTheHorror/
  build.ps1                 javac -> preverify -> jar/jad
  src/                      24 Java classes (default package)
  res/                      all runtime images (png) + icon
  bin/                      built jar/jad
  classes/ tmpclasses/      build intermediates
  alonehorror_demo_frames/  3823 reference frames (bmp + png) + 1.txt task
  docs/                     this documentation + reference stills
  tools/                    python asset pipeline + emulator helper scripts
```

## Controls

| Action | Key |
|--------|-----|
| Rotate | `4` / `6` or D-pad left/right |
| Move forward / backward | `2` / `8` or D-pad up/down |
| Talk / grab / strike / toggle light | `5` (fire) |
| Back / cancel | `0` |
| Pause | `*` |
| Left soft key | F1 (soft1) |
| Right soft key (EMS "Launch") | F2 (soft2) |

## Documentation map

- [`docs/PROGRESS.md`](PROGRESS.md) — what has been done, current state, next steps.
- [`docs/DEMO_ANALYSIS.md`](DEMO_ANALYSIS.md) — frame-by-frame analysis of the demo.
- [`docs/ASSETS.md`](ASSETS.md) — every asset, size and how it is produced.
- [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) — class-by-class design.
- [`docs/CONTINUE_HERE.md`](CONTINUE_HERE.md) — hand-off notes for the next session.
- [`tools/README.md`](tools/README.md) — asset pipeline usage.
- [`docs/reference/`](reference/) — key stills (demo vs. our build).
- [`docs/analysis/`](analysis/) — raw scene-segmentation data (JSON).
