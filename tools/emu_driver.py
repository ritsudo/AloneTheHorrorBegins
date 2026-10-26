# ---------------------------------------------------------------------------
# emu_driver.py - pure-python WTK emulator driver (no PowerShell needed).
#
# Launches the emulator with the built JAD, finds the DefaultColorPhone
# window, sends key events and grabs screenshots of the 176x208 MIDlet area.
#
# Usage:
#   python tools/emu_driver.py launch            # start emulator + MIDlet
#   python tools/emu_driver.py keys 5,2,2,2      # send keys (with delays)
#   python tools/emu_driver.py shot menu         # screenshot -> docs/reference/emu2/<name>.png
#   python tools/emu_driver.py run "5:1500,2:400" menu   # keys then shot
# ---------------------------------------------------------------------------
import ctypes
import os
import subprocess
import sys
import time

from PIL import ImageGrab

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMU = r"D:\Java\WTK2.5.2_01\bin\emulator.exe"
JAD = os.path.join(ROOT, "bin", "AloneTheHorror.jad")
OUT = os.path.join(ROOT, "docs", "reference", "emu2")

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

VK = {
    "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27, "enter": 0x0D,
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "esc": 0x1B,
    "0": 0x60, "1": 0x61, "2": 0x62, "3": 0x63, "4": 0x64,
    "5": 0x65, "6": 0x66, "7": 0x67, "8": 0x68, "9": 0x69,
    "star": 0x6A, "pound": 0x6B,
}


class RECT(ctypes.Structure):
    _fields_ = [("L", ctypes.c_long), ("T", ctypes.c_long),
                ("R", ctypes.c_long), ("B", ctypes.c_long)]


WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)


def find_skin():
    found = []

    def cb(h, l):
        n = user32.GetWindowTextLengthW(h)
        buf = ctypes.create_unicode_buffer(n + 1)
        user32.GetWindowTextW(h, buf, n + 1)
        cls = ctypes.create_unicode_buffer(64)
        user32.GetClassNameW(h, cls, 64)
        if user32.IsWindowVisible(h) and "DefaultColorPhone" in buf.value:
            found.append(h)
        return True

    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return found[0] if found else None


def window_rect(h):
    r = RECT()
    user32.GetWindowRect(h, ctypes.byref(r))
    return r


def tap(vk, ms=60):
    user32.keybd_event(vk, 0, 0, None)
    time.sleep(ms / 1000.0)
    user32.keybd_event(vk, 0, 2, None)


def focus(h):
    r = window_rect(h)
    user32.SetForegroundWindow(h)
    time.sleep(0.3)
    user32.SetFocus(h)
    return r


def shot(name):
    h = find_skin()
    if not h:
        print("no skin window")
        return
    r = window_rect(h)
    img = ImageGrab.grab(bbox=(r.L, r.T, r.R, r.B), all_screens=True)
    lcd = img.crop((41, 144, 41 + 240, 144 + 320))
    game = img.crop((73, 200, 73 + 176, 200 + 208))
    os.makedirs(OUT, exist_ok=True)
    lcd.save(os.path.join(OUT, name + ".lcd.png"))
    game.save(os.path.join(OUT, name + ".png"))
    print("shot", name)


def launch():
    subprocess.Popen([EMU, "-Xdevice:DefaultColorPhone", "-Xdescriptor:" + JAD],
                     cwd=os.path.dirname(EMU))
    print("waiting for emulator...")
    for _ in range(40):
        time.sleep(1)
        h = find_skin()
        if h:
            break
    time.sleep(6)
    h = find_skin()
    if not h:
        print("emulator window not found")
        return
    focus(h)
    time.sleep(0.5)
    tap(VK["enter"])          # AMS launch confirmation
    time.sleep(6)
    shot("launch")


def send_keys(spec, default_ms=700):
    h = find_skin()
    if not h:
        print("no skin window")
        return
    focus(h)
    for part in spec.split(","):
        part = part.strip().lower()
        if not part:
            continue
        if ":" in part:
            k, ms = part.split(":", 1)
            ms = int(ms)
        else:
            k, ms = part, default_ms
        if k in VK:
            tap(VK[k], 60)
            time.sleep(ms / 1000.0)
        else:
            print("unknown key", k)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "launch"
    if cmd == "launch":
        launch()
    elif cmd == "keys":
        send_keys(sys.argv[2] if len(sys.argv) > 2 else "")
    elif cmd == "shot":
        shot(sys.argv[2] if len(sys.argv) > 2 else "shot")
    elif cmd == "run":
        send_keys(sys.argv[2] if len(sys.argv) > 2 else "")
        shot(sys.argv[3] if len(sys.argv) > 3 else "after")
