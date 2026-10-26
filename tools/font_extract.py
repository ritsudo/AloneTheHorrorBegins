from PIL import Image
import numpy as np, glob, os, sys
from collections import defaultdict, Counter

FRAMES = sorted(glob.glob(r'C:\Users\Admin\j2mewtk\2.5.2\apps\AloneTheHorror\alonehorror_demo_frames\png\*.png'))

def dark_mask(n):
    a = np.asarray(Image.open(FRAMES[n]).convert('RGB')).astype(int)
    s = a.sum(axis=2)
    return s < 200  # text

# body lines are at y=167,177,187,197 height 9; x range
def line_band(y0):
    return y0, y0+9

def spans(mask_band, x0, x1, gap):
    col = mask_band[:, x0:x1].sum(axis=0)
    runs = []
    st = None
    for i, v in enumerate(col):
        if v > 0 and st is None:
            st = i
        if v == 0 and st is not None:
            runs.append((st, i-1)); st = None
    if st is not None:
        runs.append((st, len(col)-1))
    # merge with gap
    merged = []
    for r in runs:
        if merged and r[0]-merged[-1][1]-1 < gap:
            merged[-1] = (merged[-1][0], r[1])
        else:
            merged.append(list(r))
    return [(a+x0, b+x0) for a, b in merged]

def seg_glyphs(mask_band, x0, x1):
    # piece segmentation with gap>=1 (no merge)
    return spans(mask_band, x0, x1, 1)

chars = defaultdict(list)   # ch -> list of (bitmap np.array of 0/1, w)
samples_used = 0
FAILS = []

def process(frame, lines):
    global samples_used
    m = dark_mask(frame)
    band_ok = True
    parsed = []
    for i, text in enumerate(lines):
        y0, y1 = line_band(167+10*i)
        band = m[y0:y1, :]
        toks = spans(band, 12, 150, 5)
        words = text.split(' ')
        if any(b > 150 for a, b in toks):
            FAILS.append((frame, i, text, 'oob'))
            return None
        if len(toks) != len(words):
            FAILS.append((frame, i, text, 'toks', toks, len(words)))
            return None
        for (ta, tb), word in zip(toks, words):
            pieces = seg_glyphs(band, ta, tb+1)
            if len(pieces) != len(word):
                FAILS.append((frame, i, word, 'glyphs', len(pieces), len(word)))
                return None
            for (pa, pb), ch in zip(pieces, word):
                bm = band[:, pa:pb+1].astype(np.uint8)
                chars[ch].append((bm, pb-pa+1))
    samples_used += 1
    return True

# sample data: frame -> body lines (as displayed)
SAMPLES = [
 (309, ["YOU STUMBLE","ABOUT, YOUR HEAD","THROBBING FROM","THE JARRING"]),
 (330, ["AS YOUR EYES","ADJUST TO THE","DARKNESS, YOU CAN","SEE A CRASHED"]),
 (331, ["SEE A CRASHED","PLANE IN THE","DISTANCE."]),
 (344, ["LOOKS LIKE I WAS","THROWN CLEAR..."]),
 (375, ["IT'S A MIRACLE I","SURVIVED!"]),
 (391, ["I SHOULD LOOK FOR","MORE SURVIVORS."]),
 (401, ["SHOOT! MY","FLASHLIGHT'S OUT!"]),
 (412, ["THE BATTERIES ARE","DEAD..."]),
 (427, ["AS YOU COME OUT OF","SHOCK, YOU FEEL","PAIN IN YOUR LEG..."]),
 (462, ["ARGH... MY LEG IS","TORN OPEN!"]),
 (471, ["I CAN BARELY","WALK..."]),
 (483, ["I NEED HELP, FAST..."]),
 (491, ["PRESS '2' TO WALK","FORWARD."]),
 (501, ["WALK BACKWARD BY","PRESSING '8'."]),
 (512, ["USE THE '4' AND '6'","KEYS TO TURN LEFT","AND RIGHT."]),
 (522, ["CHANGE YOUR","CONTROL SETUP BY","PRESSING 'PAUSE' TO","ACCESS THE PAUSE"]),
 (528, ["MENU."]),
 (537, ["I NEED TO STOP THE","BLEEDING..."]),
 (546, ["I SHOULD SEARCH","THE PLANE FOR","MEDICAL SUPPLIES."]),
 (555, ["THE 'FIRE' AND '5'","KEYS PERFORM","CONTEXT SENSITIVE","ACTIONS."]),
 (563, ["USE THEM TO","INTERACT WITH","VARIOUS OBJECTS."]),
 (571, ["PRESS 'FIRE' OR '5'","TO SEARCH THE","PLANE."]),
 (745, ["YOU SEARCH THE","PLANE FOR","SALVAGEABLE","SUPPLIES."]),
 (758, ["THERE'S NOTHING","HERE--"]),
 (767, ["HOLD ON... WHAT'S","THIS?"]),
 (775, ["YOU FOUND A KEY."]),
 (784, ["ITEMS YOU FIND CAN","BE VIEWED FROM","YOUR INVENTORY."]),
 (791, ["YOUR INVENTORY","CONTAINS QUEST","ITEMS, SUCH AS","YOUR FLASHLIGHT"]),
 (792, ["AND THE KEY YOU","JUST FOUND."]),
 (799, ["TO ACCESS YOUR","MAP, INVENTORY"]),
 (800, ["AND NOTES."]),
 (807, ["OBSTACLES SUCH AS","BROWN AND","UNEXPLORED AREAS","AS BLACK. RED"]),
 (808, ["INDICATES AREAS OF","INTEREST."]),
 (817, ["YOUR NOTES KEEP","TRACK OF YOUR","OBJECTIVES AND","OTHER USEFUL"]),
 (823, ["INFORMATION."]),
 (832, ["THE RED","EXCLAMATION POINT","FLASHES WHEN","YOUR NOTES ARE"]),
 (840, ["UPDATED."]),
 (847, ["HMM..."]),
 (853, ["I SHOULD SEARCH","NEARBY FOR","FALLEN CARGO."]),
 (896, ["THERE'S GOTTA BE","MORE MEDICAL","SUPPLIES..."]),
 (1014, ["FIRST AID KITS","RESTORE SOME","HEALTH."]),
 (1025, ["MY LEG IS STILL","BLEEDING."]),
 (1040, ["IT'S ONE OF THE","CARGO CRATES!"]),
 (1079, ["TO OPEN, STAND","NEXT TO THE CRATE","AND PRESS 'FIRE' OR","'5'."]),
 (1122, ["LOCKED!"]),
 (1137, ["C'MON..."]),
 (1146, ["YOU UNLOCK THE","CRATE."]),
 (1159, ["YOU FOUND A FIRST","AID KIT."]),
 (1185, ["NICE!"]),
 (1195, ["MUCH BETTER!"]),
 (1205, ["THE BLEEDING HAS","STOPPED, BUT I'M IN","NO CONDITION TO","RUN."]),
 (1217, ["YOU CAN SAVE YOUR","PROGRESS BY","SELECTING 'SAVE'","WHEN THE GAME IS"]),
 (1226, ["PAUSED."]),
 (1246, ["IS ANYONE THERE?"]),
 (1270, ["THAT SOUNDED LIKE","A VOICE!"]),
 (1359, ["COULD THERE BE","MORE SURVIVORS?"]),
 (1377, ["BUT WHERE?"]),
 (1453, ["I THINK IT CAME","FROM DOWN THIS","PATH!"]),
 (1465, ["WHEN LOST, PRESS","THE '9' KEY TO USE","YOUR MAP."]),
 (1487, ["REMEMBER, BLACK","REGIONS INDICATE","UNEXPLORED AREAS."]),
 (1507, ["HEY! IS SOMEONE","THERE?!" ]),
 (1575, ["THAT VOICE AGAIN!"]),
 (1606, ["OVER HERE!"]),
 (1644, ["YOU APPROACH THE","MAN."]),
 (1855, ["HE APPEARS TO BE","MORTALLY WOUNDED","BUT NOT FROM THE","CRASH. WHO IS HE?"]),
 (1886, ["I SAW YOUR PLANE","FALL FROM THE","SKY!"]),
 (1931, ["IT'S A MIRACLE YOU","SURVIVED!"]),
 (1961, ["LISTEN, YOU NEED","TO GET OUT OF","HERE. IT'S","ALMOST TIME!"]),
 (1978, ["TIME?! TIME FOR","WHAT?"]),
 (2008, ["THEY GOT ME GOOD...","BUT, YOU HAVE A","CHANCE."]),
 (2043, ["TAKE THESE..."]),
 (2077, ["YOU RECEIVED A","BATTERY."]),
 (2096, ["YOU RECEIVED A","CELL PHONE."]),
 (2115, ["WHAT WAS THAT?"]),
 (2251, ["QUICKLY... TURN ON","THE FLASHLIGHT!"]),
 (2267, ["WHAT ARE YOU","DOING?! TURN ON","THE LIGHT!"]),
 (2284, ["IT'S HERE!"]),
 (2307, ["LOOK FOR THE","ORIGIN OF THE","SOUND!"]),
 (2358, ["REMEMBER, THE","HOWLERS HATE THE","LIGHT!"]),
 (2415, ["KEEP YOUR LIGHT","ON THEM AS LONG","AS POSSIBLE."]),
 (2452, ["WALKING DEAD!"]),
 (2464, ["HERE THEY COME!"]),
 (2543, ["OVER THERE! RISING","FROM THE EARTH!"]),
 (2599, ["UNLIKE THE","HOWLERS, THE DEAD","ARE IMMUNE TO","LIGHT!"]),
 (2643, ["USE THE CATTLE","PROD!"]),
 (2669, ["PRESS 'FIRE' OR '5'","TO ATTACK!"]),
 (2799, ["WELL DONE!"]),
 (2838, ["REMEMBER, THE","CATTLE PROD WILL","DRAIN BATTERIES AS","WELL."]),
 (3023, ["YOU'LL NEED TO","CONSERVE","BATTERIES FOR YOUR","LIGHT TO SURVIVE."]),
 (3137, ["RUNNING IS OFTEN","YOUR BEST CHANCE","FOR SURVIVAL...."]),
 (3149, ["TAKE THESE","SUPPLIES."]),
 (3179, ["HEAD WEST...","FIND ZOE..."]),
 (3226, ["ZOE?"]),
 (3295, ["FOLLOW THE PATH...","PAST THE BARN..."]),
 (3356, ["THERE'S A HOUSE...","QUICKLY... BEFORE","THE..."]),
 (3381, ["GENERATORS..."]),
 (3397, ["..." ]),
 (3503, ["WAIT!"]),
 (3522, ["WHAT ARE YOU","TALKING ABOUT?!"]),
 (3569, ["WHAT GENERATOR?"]),
 (3591, ["WHO'S ZOE?!"]),
 (3636, ["HE... HE'S DEAD..."]),
 (3654, ["I BETTER GET","MOVING..."]),
 (3011, ["SHOOT! THAT ZOMBIE","WAS A LOT TOUGHER","THAN THE OTHERS."]),
 (3481, ["SHOOT! MORE","HOWLERS!"]),
 (3658, ["I BETTER GET","MOVING..."]),
]

for frame, lines in SAMPLES:
    try:
        process(frame, lines)
    except Exception as e:
        print("ERR", frame, e)

print("samples_used", samples_used)
for f in FAILS[:40]:
    print("FAIL", f)
cover = sorted(chars.keys())
print("chars", ''.join(cover))
missing = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" if c not in chars]
print("missing", missing)
counts = {c: len(v) for c, v in sorted(chars.items())}
print(counts)
np.save(r'C:\Temp\opencode\ah\font_raw.npy', np.array([1]))  # placeholder
import pickle
pickle.dump(chars, open(r'C:\Temp\opencode\ah\font_raw.pkl','wb'))
