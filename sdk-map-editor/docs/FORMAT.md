# `.jmap` binary format v1

The format is deliberately boring: big-endian fixed-width integers, no floats,
no compression library, and no external metadata. A 2005-2007 device can parse
it with `java.io.DataInputStream` and render it with `Graphics.drawRegion`.

All integers are **big endian**. `u8`, `u16` and `u32` mean unsigned 8/16/32-bit.

## Header

| Offset | Size | Field | Notes |
|---:|---:|---|---|
| 0 | 4 | magic | ASCII `JMAP` (`4A 4D 41 50`) |
| 4 | 1 | version | `1` |
| 5 | 1 | flags | bit0 terrain RLE, bit1 collision RLE |
| 6 | 1 | layerMask | bit0 terrain, bit1 collision, bit2 objects; v1 writes `0x07` |
| 7 | 1 | tileSize | pixels per tile, normally `16` |
| 8 | 2 | width | map width in tiles, `1..65535` |
| 10 | 2 | height | map height in tiles, `1..65535` |
| 12 | 2 | objectCount | number of object records |
| 14 | 1 | nameLen | UTF-8 byte length of the map name, `0..255` |
| 15 | nameLen | name | UTF-8, not NUL terminated |
| ... | 4 | terrainLen | byte length of the terrain payload |
| ... | terrainLen | terrain payload | see layers below |
| ... | 4 | collisionLen | byte length of the collision payload |
| ... | collisionLen | collision payload | see layers below |
| ... | objectCount × 10 | objects | see object records |

Layers are always present in this order. The collision layer is omitted if
`layerMask` bit1 is clear; in that case the runtime fills it with zeroes. The
object table is omitted if bit2 is clear.

## Layers

Cell order is **row major**: `index = y * width + x`. There are exactly
`width * height` cells in every layer.

### Raw payload

When the corresponding flag bit is clear, the payload is simply `u16` per cell.

- terrain: tile id `0..4095` (`0` = empty/void)
- collision: "collision byte 0..255" stored in a `u16`; only the low byte is used

### RLE payload

When the flag bit is set, the payload is a sequence of 4-byte pairs until all
cells are filled:

| Size | Field |
|---:|---|
| 2 | `u16 value` |
| 2 | `u16 runLength` (must be `> 0`) |

Runs must not overrun the layer cell count. The encoder picks RLE only when it
is strictly smaller than the raw payload, so decoders must handle both.

Example: four empty terrain cells followed by two tile-7 cells:

```
00 00 00 04  00 07 00 02
```

## Object records

Each object is exactly 10 bytes. Objects are placed on tile coordinates and can
stack. The editor uses the following kinds:

| Size | Field | Meaning |
|---:|---|---|
| 1 | kind | 0 item, 1 enemy, 2 trigger, 3 decor, 4 marker |
| 2 | type | stable id from the SDK ranges below |
| 2 | x | tile column (`0..width-1`) |
| 2 | y | tile row (`0..height-1`) |
| 1 | flags | bit0-1 facing, bit2 active, bit3 respawn, bit4 locked/review |
| 2 | param | item count, enemy group, exit target level, ... |

### Expandable SDK ids

| Range | Use |
|---|---|
| `0` | empty terrain |
| `1..4095` | terrain tiles (maximum 4095 unique tiles) |
| `4096..4351` | item types (256) |
| `4352..4607` | enemy types (256) |
| `4608..4863` | trigger types (256) |
| `4864..5119` | reserved |
| `5120..65535` | future expansion |

Built-in triggers:

| Id | Name |
|---:|---|
| 4608 | `player_spawn` (red marker in the screenshots) |
| 4609 | `level_exit` (green marker) |
| 4610 | `level_start` |
| 4611 | `cutscene` |
| 4612 | `talk_jonathan` (chapter 1 ending) |
| 4613 | `door_crowbar` (chapter 3 ending) |

New tile types get the next free terrain id; existing ids never move when the
tileset is rebuilt. `assets/tileset.json` is the authoritative ID map. Its
`tiles[]` array is sorted by id, and the atlas tile for id `N` is at:

```
sx = (N % columns) * tileSize
sy = (N / columns) * tileSize
```

The atlas itself is a plain RGB PNG. This project uses an 8-column (8x8) grid:
`columns` in `tileset_grid.json` is authoritative and the browser editor reads
it from there.

Recovery may append one synthetic tile named `broken_temp` (manifest field
`"temp": true`, kind `temp`, solid collision). It marks cells whose pixels were
shifted or occupied by a baked-in actor and could not be repaired automatically.
It is excluded from shared-tile counts. Accepting or dismissing the matching
anomaly restores the stored donor tile; the editor's **Clean garbage** action
removes the placeholder and any other tile that is no longer referenced.

## Collision byte

| Bit | Name | Meaning |
|---:|---|---|
| 0 | `SOLID` | blocks walking |
| 1 | `WATER` | water / swim |
| 2 | `PIT` | fall / pit |
| 3 | `HAZARD` | damage |
| 4 | `DOOR` | door / transition |
| 5 | `LADDER` | climb |
| 6 | `TRIGGER` | script / event cell |
| 7 | reserved | |

The recovery pipeline derives the first collision byte for each tile from its
surface colours (paths, floors and snow walkable; foliage, water, void and
masonry solid). The operator then edits the collision layer per cell.

## Minimal loader

```java
InputStream in = getClass().getResourceAsStream("/chapter1.jmap");
JMap map = JMap.load(in);
JMapRenderer renderer = new JMapRenderer(map, Image.createImage("/tileset.png"));
renderer.draw(g, cameraX, cameraY, getWidth(), getHeight());
```

See `j2me/src/jmap/` for a complete CLDC 1.1 / MIDP 2.0 reader, renderer and
playable demo.
