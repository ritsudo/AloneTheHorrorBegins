"""Integrate the final recovered tiles/maps into the game and the SDK editor.

Sources (produced in the map editor):
  sdk-map-editor/assets/tileset_grid.png / .json
  sdk-map-editor/maps/chapter1.jmap ... chapter3.jmap

The script:
  * keeps the final terrain and collision untouched;
  * adds the story triggers required by the game flow (Jonathan, left exit,
    crowbar door) without duplicating them on a re-run;
  * copies the atlas and maps to res/ for the MIDlet;
  * writes the shared object catalog assets/game_objects.json;
  * rebuilds editor/bundle.js so the SDK palette lists items, enemies and
    triggers and the maps open ready to edit.

Run from the project root:  python tools/integrate_final.py
"""
import base64
import io
import json
import struct
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SDK = ROOT / "sdk-map-editor"
ASSETS = SDK / "assets"
FINAL = SDK / "maps"        # SDK/source maps (maps_final was merged here)
res = ROOT / "res"
EDITOR = SDK / "editor"

T = 16

OBJECT_CATALOG = {
    "format": "alonehorror-objects",
    "version": 1,
    "ranges": {
        "terrain": [1, 4095],
        "items": [4096, 4351],
        "enemies": [4352, 4607],
        "triggers": [4608, 4863],
        "reserved": [4864, 5119],
        "expansion": [5120, 65535],
    },
    "items": [
        {"id": 4096, "name": "medkit", "icon": "item_medkit.png",
         "color": [225, 60, 60], "param": 25,
         "description": "Restores the player's health."},
        {"id": 4097, "name": "ammo", "icon": "item_ammo.png",
         "color": [225, 190, 60], "param": 10,
         "description": "Shotgun shells."},
        {"id": 4098, "name": "key", "icon": "item_key.png",
         "color": [245, 220, 90], "param": 1,
         "description": "Opens a locked door."},
        {"id": 4099, "name": "note", "icon": "item_note.png",
         "color": [220, 220, 220], "param": 1,
         "description": "Readable story item."},
        {"id": 4100, "name": "battery", "icon": "item_batt.png",
         "color": [90, 210, 120], "param": 1,
         "description": "Spare flashlight cell."},
        {"id": 4101, "name": "flashlight", "icon": "item_batt.png",
         "color": [120, 190, 255], "param": 1,
         "description": "Lights the darkness; howlers fear it."},
        {"id": 4102, "name": "cattle_prod", "icon": "item_batt.png",
         "color": [200, 140, 255], "param": 1,
         "description": "Improvised weapon."},
        {"id": 4103, "name": "crowbar", "icon": "item_crowbar.png",
         "color": [190, 190, 210], "param": 1,
         "description": "Pries open the red barn doors."},
        {"id": 4104, "name": "gun", "icon": "item_gun.png",
         "color": [255, 120, 90], "param": 1,
         "description": "Jonathan's shotgun."},
    ],
    "enemies": [
        {"id": 4352, "name": "howler", "icon": "howler.png",
         "color": [210, 110, 230], "param": 0,
         "description": "Hunts in the dark; flees the flashlight."},
        {"id": 4353, "name": "walker", "icon": "zombie.png",
         "color": [150, 90, 230], "param": 0,
         "description": "Slow zombie; ignores the light."},
    ],
    "triggers": [
        {"id": 4608, "name": "player_spawn", "kind": "spawn",
         "color": [235, 32, 32], "description": "Red marker: where the player starts."},
        {"id": 4609, "name": "level_exit", "kind": "exit",
         "color": [32, 220, 64], "description": "Ends the chapter."},
        {"id": 4610, "name": "level_start", "kind": "start",
         "color": [255, 190, 32], "description": "Optional entry marker."},
        {"id": 4611, "name": "cutscene", "kind": "cutscene",
         "color": [64, 140, 255], "description": "Param selects the Script.java dialogue table."},
        {"id": 4612, "name": "talk_jonathan", "kind": "talk",
         "color": [255, 120, 200], "description": "Chapter 1 ending: talk to Jonathan."},
        {"id": 4613, "name": "door_crowbar", "kind": "door",
         "color": [200, 40, 40], "description": "Chapter 3 ending: open the red doors with the crowbar."},
    ],
}

T_SPAWN = 4608
T_EXIT = 4609
T_TALK = 4612
T_DOOR = 4613


def decode_map(blob):
    if blob[:4] != b"JMAP":
        raise ValueError("bad magic")
    flags = blob[5]
    w, h, oc = struct.unpack(">HHH", blob[8:14])
    nl = blob[14]
    name = blob[15:15 + nl].decode("utf-8", "replace")
    p = 15 + nl
    count = w * h

    def layer(comp):
        nonlocal p
        ln = struct.unpack(">I", blob[p:p + 4])[0]
        p += 4
        end = p + ln
        out = []
        if comp:
            while p < end and len(out) < count:
                v, r = struct.unpack(">HH", blob[p:p + 4])
                p += 4
                out.extend([v] * r)
        else:
            for _ in range(count):
                out.append(struct.unpack(">H", blob[p:p + 2])[0])
                p += 2
        p = end
        return out[:count]

    terrain = layer(flags & 1)
    collision = layer(flags & 2) if blob[6] & 2 else [0] * count
    p = len(blob) - oc * 10
    objects = []
    for _ in range(oc):
        k, t, x, y, fl, par = struct.unpack(">BHHHBH", blob[p:p + 10])
        p += 10
        objects.append(dict(kind=k, type=t, x=x, y=y, flags=fl, param=par))
    return dict(name=name, width=w, height=h, terrain=terrain,
                collision=[c & 255 for c in collision], objects=objects)


def rle(values):
    out = bytearray()
    i = 0
    while i < len(values):
        v = values[i]
        run = 1
        while i + run < len(values) and values[i + run] == v and run < 65535:
            run += 1
        out += struct.pack(">HH", v, run)
        i += run
    return bytes(out)


def encode_layer(values):
    raw = b"".join(struct.pack(">H", v) for v in values)
    packed = rle(values)
    return (packed, True) if len(packed) < len(raw) else (raw, False)


def encode_map(m):
    terrain_payload, terrain_rle = encode_layer(m["terrain"])
    collision_payload, collision_rle = encode_layer(m["collision"])
    flags = (1 if terrain_rle else 0) | (2 if collision_rle else 0)
    nb = m["name"].encode("utf-8")
    out = bytearray(b"JMAP")
    out += struct.pack(">BBBB", 1, flags, 7, T)
    out += struct.pack(">HHH", m["width"], m["height"], len(m["objects"]))
    out += struct.pack(">B", len(nb)) + nb
    out += struct.pack(">I", len(terrain_payload)) + terrain_payload
    out += struct.pack(">I", len(collision_payload)) + collision_payload
    for o in m["objects"]:
        out += struct.pack(">BHHHBH", o["kind"], o["type"], o["x"], o["y"],
                           o["flags"], o["param"])
    return bytes(out)


def add_object(m, kind, typ, x, y, param=0):
    if any(o["kind"] == kind and o["type"] == typ for o in m["objects"]):
        return False
    x = max(0, min(m["width"] - 1, x))
    y = max(0, min(m["height"] - 1, y))
    m["objects"].append(dict(kind=kind, type=typ, x=x, y=y, flags=0, param=param))
    return True


def apply_flow(ch, m):
    """Make the three chapters follow the scripted game flow."""
    if ch == 1:
        # the old level exit marker is where Jonathan waits
        if not any(o["type"] == T_TALK for o in m["objects"]):
            for o in m["objects"]:
                if o["kind"] == 2 and o["type"] == T_EXIT:
                    o["type"] = T_TALK
                    break
            else:
                add_object(m, 2, T_TALK, 13, 7)
    elif ch == 2:
        # start on the right (already in maps_final), walk left to the exit
        add_object(m, 2, T_EXIT, 1, 5)
    elif ch == 3:
        # start on the right, take the crowbar, open the red doors (2..3,11..12)
        for o in m["objects"]:
            if o["kind"] == 2 and o["type"] == T_EXIT:
                o["type"] = T_DOOR
        add_object(m, 2, T_DOOR, 2, 13)


def main():
    tileset = json.loads((ASSETS / "tileset_grid.json").read_text(encoding="utf-8"))
    atlas = Image.open(ASSETS / "tileset_grid.png").convert("RGB")
    if atlas.size != (tileset["columns"] * T, tileset["rows"] * T):
        raise SystemExit("atlas size does not match tileset_grid.json")

    # the game ships the final atlas + the final maps with the flow triggers
    atlas.save(res / "tileset_grid.png", optimize=True)
    (res / "tileset_grid.json").write_text(
        json.dumps(tileset, indent=2), encoding="utf-8")

    maps = {}
    for ch in (1, 2, 3):
        m = decode_map((FINAL / ("chapter%d.jmap" % ch)).read_bytes())
        m["name"] = "chapter%d" % ch
        apply_flow(ch, m)
        blob = encode_map(m)
        # write back to the SDK map folder so the editor opens the game maps
        if not FINAL.is_dir():
            FINAL.mkdir(parents=True)
        (FINAL / ("chapter%d.jmap" % ch)).write_bytes(blob)
        (res / ("chapter%d.jmap" % ch)).write_bytes(blob)
        maps[ch] = m
        print("chapter%d %dx%d %d objects -> res + maps" %
              (ch, m["width"], m["height"], len(m["objects"])))

    catalog = OBJECT_CATALOG
    (ASSETS / "game_objects.json").write_text(
        json.dumps(catalog, indent=2), encoding="utf-8")

    # editor bundle: final atlas + maps + the full object palette
    project_maps = []
    encoded = {}
    for ch in (1, 2, 3):
        m = maps[ch]
        name = "chapter%d" % ch
        encoded[name] = base64.b64encode(
            (res / (name + ".jmap")).read_bytes()).decode("ascii")
        project_maps.append(dict(
            name=name, source="", offset=[0, 0],
            width=m["width"], height=m["height"],
            jmap="maps/%s.jmap" % name, preview="",
            collisionPreview="", anomalyPreview="", anomalies=[],
            warnings=[], markers=[], sharedTiles=0, alignmentConfidence=1,
            objects=m["objects"],
        ))

    project = dict(
        format="alonehorror-project", version=1, terrainOnly=False,
        tileSize=T,
        assets=dict(manifest="assets/tileset_grid.json",
                    atlas="assets/tileset_grid.png",
                    objects="assets/game_objects.json"),
        alignment=dict(offsets=[[0, 0], [0, 0], [0, 0]],
                       sharedTileMatches=[], confidence=1),
        objectTypes=catalog,
        maps=project_maps,
    )

    buf = io.BytesIO()
    atlas.save(buf, format="PNG", optimize=True)
    atlas_uri = "data:image/png;base64," + \
        base64.b64encode(buf.getvalue()).decode("ascii")

    bundle = dict(project=project, tileset=tileset, atlas=atlas_uri,
                  objectTypes=catalog, sources={}, maps=encoded)
    (EDITOR / "bundle.js").write_text(
        "window.ALONEHORROR_BUNDLE = " +
        json.dumps(bundle, separators=(",", ":")) + ";\n",
        encoding="utf-8")

    print("object catalog ->", ASSETS / "game_objects.json")
    print("editor bundle ->", EDITOR / "bundle.js",
          (EDITOR / "bundle.js").stat().st_size, "bytes")


if __name__ == "__main__":
    main()
