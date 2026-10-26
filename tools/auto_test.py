"""Automatic game test: drives the rebuilt MIDlet in the WTK emulator and
asserts every stage of the demo flow plus the core mechanics.

Flow (keys per docs/DEMO_ANALYSIS.md):
  boot -> title -> menu -> NEW GAME -> level select -> loading -> config
  -> chapter card -> gameplay ch1 (dialogue, walk, light toggle, pause)

Every stage grabs the 176x208 MIDlet area and runs pixel assertions.
Screenshots land in docs/reference/qa/ and the summary prints PASS/FAIL.

Usage:
  python tools/auto_test.py            # full run (launches the emulator)
  python tools/auto_test.py --attach   # reuse an emulator that is running
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emu_driver import (EMU, JAD, find_skin, focus, launch,  # noqa: E402
                        send_keys, shot, tap, VK)

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QA = os.path.join(ROOT, "docs", "reference", "qa")

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))
    print(("PASS " if ok else "FAIL ") + name + (" - " + detail if detail else ""))


def grab(name):
    """Screenshot into the QA dir; returns the RGB array or None."""
    os.makedirs(QA, exist_ok=True)
    path = os.path.join(QA, name + ".png")
    h = find_skin()
    if not h:
        return None
    focus(h)
    time.sleep(0.4)
    from PIL import ImageGrab
    r = find_skin()
    from emu_driver import window_rect
    rect = window_rect(r)
    img = ImageGrab.grab(bbox=(rect.L, rect.T, rect.R, rect.B), all_screens=True)
    game = img.crop((73, 200, 73 + 176, 200 + 208))
    game.save(path)
    return np.asarray(game.convert("RGB")).astype(int)


def lit_mask(a, thr=170):
    return a[22:136].sum(axis=2) > thr * 3


def pool_center(a):
    m = lit_mask(a)
    ys, xs = np.nonzero(m)
    if len(xs) < 50:
        return None
    w = m[ys, xs].astype(float)
    return float((xs * w).sum() / w.sum()), float((ys * w).sum() / w.sum()), int(m.sum())


# ---------------------------------------------------------------- assertions
def is_title(a):
    # dark night scene, bright ALONE letters in the upper half
    return a[:100].mean() < 90 and (a[30:80].sum(axis=2) > 500).sum() > 120


def is_menu(a):
    # parchment page mid-screen with menu rows, campfire bright spots
    mid = a[80:160, 30:150]
    return (mid.sum(axis=2) > 420).sum() > 800


def is_level_select(a):
    top = a[30:70, 20:160]
    return (top.sum(axis=2) > 500).sum() > 150


def is_loading(a):
    # parchment page fills most of the screen
    return (a[20:190, 10:170].sum(axis=2) > 420).mean() > 0.5


def is_chapter_card(a):
    mid = a[80:130, 20:160]
    dark = a.mean() < 80
    return dark and (mid.sum(axis=2) > 420).sum() > 100


def has_dialogue_panel(a):
    # parchment panel in the bottom 72 px
    return (a[140:205, 10:166].sum(axis=2) > 420).mean() > 0.5


def has_battery_icon(a):
    # yellow cells top-right
    zone = a[0:14, 150:176]
    r, g, b = zone[:, :, 0], zone[:, :, 1], zone[:, :, 2]
    return ((r > 150) & (g > 120) & (b < 110)).sum() >= 12


def has_light_pool(a):
    m = lit_mask(a)
    return m.sum() > 900


def main():
    attach = "--attach" in sys.argv
    if not attach:
        launch()
    else:
        h = find_skin()
        if not h:
            print("no running emulator")
            return 2

    # 1. logo -> title (logo 70 ticks, title auto after 110): ~9 s total
    time.sleep(9)
    a = grab("t01_title")
    check("title screen renders", a is not None and is_title(a))

    # 2. to the menu (title advances on any key)
    send_keys("enter:1500", 500)
    a = grab("t02_menu")
    if a is not None and not is_menu(a):
        send_keys("enter:1500", 500)
        a = grab("t02_menu")
    check("main menu renders", a is not None and is_menu(a))

    # 3. NEW GAME -> level select
    send_keys("enter:1500", 500)
    a = grab("t03_levelselect")
    check("level select renders", a is not None and is_level_select(a))

    # 4. confirm chapter 1 -> loading page
    send_keys("enter:1200", 500)
    a = grab("t04_loading")
    check("loading page renders", a is not None and is_loading(a))

    # loading auto (4.4 s) + config page (3.2 s) + chapter card (2.4 s)
    time.sleep(8)
    a = grab("t05_config_or_card")
    check("config/chapter card renders", a is not None and (
        is_chapter_card(a) or has_dialogue_panel(a) or is_loading(a)))

    # 5. into gameplay
    send_keys("enter:2500", 500)
    a = grab("t06_gameplay")
    check("gameplay starts with dialogue", a is not None and has_dialogue_panel(a))
    check("HUD battery row present", a is not None and has_battery_icon(a))

    # 6. advance the opening dialogue
    for i in range(4):
        send_keys("enter:900", 100)
    a = grab("t07_dialogue_advanced")
    check("dialogue advances with FIRE", a is not None and has_dialogue_panel(a))

    # 7. keep advancing until the panel closes (max 24 lines)
    for i in range(24):
        a = grab("t08_dialog")
        if a is None:
            break
        if not has_dialogue_panel(a):
            break
        send_keys("enter:900", 100)
    a = grab("t09_world")
    check("dialogue closes into the world", a is not None and not has_dialogue_panel(a))

    # 8. light pool and movement
    c0 = pool_center(a) if a is not None else None
    check("light pool visible", c0 is not None and c0[2] > 900,
          "lit px %s" % (c0[2] if c0 else "n/a"))
    send_keys("2:300,2:300,2:300,2:300,2:300,2:300", 300)
    a = grab("t10_walked")
    c1 = pool_center(a) if a is not None else None
    moved = c0 and c1 and (abs(c0[0] - c1[0]) + abs(c0[1] - c1[1]) > 6)
    check("player walks with key 2", moved is True,
          "pool moved %.1f px" % (abs(c0[0] - c1[0]) + abs(c0[1] - c1[1])) if c0 and c1 else "no pool")

    # 9. light toggle (key 1): the pool shrinks/grows
    send_keys("1:800", 300)
    a = grab("t11_light_toggled")
    c2 = pool_center(a) if a is not None else None
    check("light toggles with key 1", c1 and c2 and abs(c1[2] - c2[2]) > 150,
          "lit %s -> %s" % (c1[2] if c1 else "?", c2[2] if c2 else "?"))
    send_keys("1:800", 300)

    # 10. pause menu
    send_keys("star:900", 300)
    a = grab("t12_pause")
    check("pause menu renders", a is not None and is_menu(a))
    send_keys("enter:800", 300)

    # 11. back to the world alive
    a = grab("t13_resume")
    check("resume returns to the world", a is not None and not has_dialogue_panel(a))

    # summary
    fails = [r for r in RESULTS if not r[1]]
    print("\n=== AUTO TEST: %d passed, %d failed ===" % (
        len(RESULTS) - len(fails), len(fails)))
    for name, ok, detail in fails:
        print("  FAILED:", name, detail)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
