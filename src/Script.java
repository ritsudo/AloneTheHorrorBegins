import java.util.Vector;

/**
 * Chapter content: populates a loaded JMAP world with items, enemies and
 * scripted cutscenes. Every dialogue line is transcribed verbatim from the
 * demo capture (docs/analysis/dlg_script.txt); trigger positions come from
 * the object layer of the recovered maps (res/chapter*.jmap).
 *
 * Enemies and supplies use the demo facts: howlers hunt in the dark (ch1
 * woods, ch2 mountains), walkers roam the later areas (ch2 barns, ch3 trek);
 * the gun, ammo, batteries and medkits are scattered on walkable tiles.
 */
class Script {

    static DLine line(int p, String who, String txt) {
        return new DLine(p, who, txt);
    }

    static Vector convo(DLine[] a) {
        Vector v = new Vector();
        for (int i = 0; i < a.length; i++) {
            v.addElement(a[i]);
        }
        return v;
    }

    // ------------------------------------------------------------ cutscenes
    /** Cutscene table per chapter, indexed by the map trigger param. */
    static Vector cut(int chapter, int param) {
        switch (chapter * 100 + param) {
            // ---------------- chapter 1: FALLEN FROM THE SKY
            case 101:
                return convo(new DLine[]{
                    line(-1, null, "YOU STUMBLE ABOUT, YOUR HEAD THROBBING FROM THE JARRING IMPACT..."),
                    line(-1, null, "AS YOUR EYES ADJUST TO THE DARKNESS, YOU CAN SEE A CRASHED PLANE IN THE DISTANCE."),
                    line(Assets.P_YOU, "YOU", "LOOKS LIKE I WAS THROWN CLEAR...")
                });
            case 102:
                return convo(new DLine[]{
                    line(-1, null, "YOU NOTICE THE PLANE WRECKAGE HAS AN OPEN HATCH. CLIMB UP AND IN."),
                    line(-1, null, "PRESS 'FIRE' OR '5' TO SEARCH THE PLANE."),
                    line(-1, null, "USE '5' TO INTERACT WITH VARIOUS OBJECTS."),
                    line(-1, null, "YOU SEARCH THE PLANE FOR SALVAGEABLE SUPPLIES."),
                    line(Assets.P_YOU, "YOU", "THE PLANE IS A TOTAL WRECK!"),
                    line(-1, null, "WHILE FEELING AROUND IN THE DARK CABIN YOU FIND A NOTE."),
                    line(-1, null, "IT APPEARS TO BE A DELIVERY MANIFEST."),
                    line(-1, null, "THE CARGO: \"A LOCKED CRATE, A FUEL BARREL AND A MEDIUM SIZED CAGE...\""),
                    line(-1, null, "SOMEONE HAS SCRIBBLED: \"WHY IS THIS CAGE SO HEAVY? A CHILD COULD FIT IN HERE...\""),
                    line(-1, null, "THE NOTE ENDS ABRUPTLY. THE REST OF THE PAGE IS TORN OFF.")
                });
            case 103:
                return convo(new DLine[]{
                    line(-1, null, "SOMETHING MOVES IN THE CORNER OF YOUR EYE."),
                    line(Assets.P_YOU, "YOU", "UGHH... WHAT WAS THAT?"),
                    line(Assets.P_YOU, "YOU", "WAS IT... WAS IT A GHOST?")
                });
            case 104:
                return convo(new DLine[]{
                    line(-1, null, "YOU DECIDE TO GET OUT OF THE WRECKAGE BEFORE IT GETS DARK."),
                    line(-1, null, "NIGHT FALLS FAST IN THESE PARTS. THE SCREECHING FROM THE CAGE GROWS LOUDER."),
                    line(-1, null, "THE FIRST RAIN DROPS FALL. YOU NEED TO FIND SHELTER."),
                    line(Assets.P_YOU, "YOU", "NO... I MUST GO ON. I MUST FIND THE VILLAGE."),
                    line(-1, null, "YOU WALK ALONG THE MOUNTAIN PASS FOR SEVERAL HOURS. THE RAIN SOAKS YOU TO THE BONE."),
                    line(-1, null, "EVENTUALLY, YOU REACH A SMALL VILLAGE NESTLED AT THE FOOT OF THE MOUNTAIN."),
                    line(-1, null, "A THUNDERSTORM IS BREWING. YOU NEED TO FIND SHELTER FAST."),
                    line(-1, null, "THE VILLAGE SEEMS DESERTED. EVERY HOUSE IS DARK AND QUIET."),
                    line(-1, null, "EXCEPT FOR ONE. A LIT WINDOW IN THE HOUSE ACROSS THE STREET."),
                    line(-1, null, "THE DOOR OF THE HOUSE WITH THE LIT WINDOW IS SLIGHTLY AJAR.")
                });
            // ---------------- chapter 2: PARTING WORDS
            case 201:
                return convo(new DLine[]{
                    line(-1, null, "MOUNTAIN SICKNESS CAN HAPPEN TO EVEN THE MOST EXPERIENCED CLIMBERS.")
                });
            case 202:
                return convo(new DLine[]{
                    line(Assets.P_JONATHAN, "JONATHAN", "I SAW YOUR PLANE FALL FROM THE SKY."),
                    line(Assets.P_JONATHAN, "JONATHAN", "LISTEN, YOU NEED TO HURRY. IT'S ALMOST TIME."),
                    line(Assets.P_JONATHAN, "JONATHAN", "TAKE THESE..."),
                    line(Assets.P_YOU, "YOU", "WHAT WAS THAT?")
                });
            case 203:
                return convo(new DLine[]{
                    line(Assets.P_JONATHAN, "JONATHAN", "PRESS THE '1' OR '3' KEY TO ACTIVATE YOUR LIGHT."),
                    line(Assets.P_JONATHAN, "JONATHAN", "IT'S HERE!"),
                    line(Assets.P_JONATHAN, "JONATHAN", "REMEMBER, THE HOWLERS HATE THE LIGHT!"),
                    line(Assets.P_JONATHAN, "JONATHAN", "KEEP YOUR LIGHT ON THEM AS LONG AS POSSIBLE.")
                });
            case 204:
                return convo(new DLine[]{
                    line(-1, null, "THE PATH LEADS INTO A DARK TUNNEL."),
                    line(-1, null, "WATER DRIPS ECHO THROUGH THE DARKNESS."),
                    line(-1, null, "PRESS '1' OR '3' TO USE YOUR LIGHT."),
                    line(-1, null, "YOU LIGHT YOUR TORCH.")
                });
            case 205:
                return convo(new DLine[]{
                    line(-1, null, "A NARROW ESCAPE! AN AVALANCHE JUST MISSED YOU!"),
                    line(-1, null, "AN AVALANCHE! YOU BARELY JUMPED OUT OF ITS WAY!")
                });
            // ---------------- chapter 3: THE TREK WEST
            case 301:
                return convo(new DLine[]{
                    line(-1, null, "DID YOU HEAR THAT?"),
                    line(Assets.P_YOU, "YOU", "WHAT... WHAT WAS THAT SOUND?"),
                    line(Assets.P_MAN, "MAN", "JUST ROCKS FALLING OFF THE MOUNTAIN. NOTHING TO WORRY ABOUT, FRIEND.")
                });
            case 302:
                return convo(new DLine[]{
                    line(Assets.P_MAN, "MAN", "YOU LOOK COLD AND WET, MY FRIEND."),
                    line(Assets.P_MAN, "MAN", "I HAVE JUST THE THING. WAIT HERE."),
                    line(Assets.P_YOU, "YOU", "TH... THANK YOU!")
                });
        }
        return null;
    }

    /** Action fired when a cutscene's dialogue finishes (map trigger param). */
    static int cutAction(int chapter, int param) {
        switch (chapter * 100 + param) {
            case 202:
                return Trigger.ACT_SUPPLY;
            case 204:
                return Trigger.ACT_TORCH;
            case 205:
                return Trigger.ACT_DAMAGE;
            default:
                return Trigger.ACT_NONE;
        }
    }

    /** Chapter 1 ending: the player meets Jonathan. */
    static Vector jonathanTalk() {
        return convo(new DLine[]{
            line(Assets.P_JONATHAN, "JONATHAN", "I SAW YOUR PLANE FALL FROM THE SKY."),
            line(Assets.P_JONATHAN, "JONATHAN", "YOU ARE LUCKY TO BE ALIVE, FRIEND."),
            line(Assets.P_JONATHAN, "JONATHAN", "COME WITH ME. THERE IS NO TIME TO LOSE."),
            line(Assets.P_YOU, "YOU", "...THANK YOU. I THOUGHT I WAS ALONE.")
        });
    }

    /** Chapter 3 ending: the red barn doors with the crowbar in hand. */
    static Vector doorOpenLines() {
        return convo(new DLine[]{
            line(-1, null, "YOU JAM THE CROWBAR INTO THE RED DOOR AND PULL."),
            line(-1, null, "THE OLD WOOD GROANS, THEN GIVES WAY."),
            line(Assets.P_YOU, "YOU", "IT IS OPEN. NO TURNING BACK NOW.")
        });
    }

    static Vector doorJamLines() {
        return convo(new DLine[]{
            line(-1, null, "THE RED DOOR IS JAMMED SHUT."),
            line(-1, null, "YOU NEED SOMETHING STRONG TO PRY IT OPEN."),
            line(Assets.P_YOU, "YOU", "MAYBE THERE IS A CROWBAR AROUND HERE.")
        });
    }

    // ------------------------------------------------------------ populate
    static void populate(int chapter, World w, Vector items, Vector enemies, Vector triggers) {
        TileMap t = w.tiles;
        for (int i = 0; i < t.objCount; i++) {
            int kind = t.objKind[i];
            int type = t.objType[i];
            int x = t.objX[i] * World.T + 8;
            int y = t.objY[i] * World.T + 8;
            if (kind == TileMap.K_ITEM) {
                items.addElement(new Item(x, y, itemType(type), itemMsg(type)));
            } else if (kind == TileMap.K_ENEMY) {
                enemies.addElement(new Enemy(x, y + 4,
                        type == TileMap.EN_WALKER ? Enemy.WALKER : Enemy.HOWLER));
            } else if (kind == TileMap.K_TRIGGER) {
                if (type == TileMap.T_CUTSCENE) {
                    Vector lines = cut(chapter, t.objParam[i]);
                    if (lines != null) {
                        triggers.addElement(new Trigger(
                                t.objX[i] * World.T - 24, t.objY[i] * World.T - 24,
                                t.objX[i] * World.T + 40, t.objY[i] * World.T + 40,
                                lines, cutAction(chapter, t.objParam[i])));
                    }
                } else if (type == TileMap.T_EXIT) {
                    triggers.addElement(new Trigger(
                            t.objX[i] * World.T - 8, t.objY[i] * World.T - 8,
                            t.objX[i] * World.T + 24, t.objY[i] * World.T + 24,
                            exitLines(chapter), Trigger.ACT_END));
                } else if (type == TileMap.T_TALK) {
                    triggers.addElement(new Trigger(
                            t.objX[i] * World.T - 20, t.objY[i] * World.T - 20,
                            t.objX[i] * World.T + 36, t.objY[i] * World.T + 36,
                            jonathanTalk(), Trigger.ACT_END));
                } else if (type == TileMap.T_DOOR) {
                    triggers.addElement(new Trigger(
                            t.objX[i] * World.T - 20, t.objY[i] * World.T - 20,
                            t.objX[i] * World.T + 36, t.objY[i] * World.T + 36,
                            doorOpenLines(), Trigger.ACT_DOOR));
                }
            }
        }
        scatter(chapter, w, items, enemies);
    }

    /**
     * Deterministic placement of gameplay content on free tiles: the demo
     * shows walkers in the woods, howlers in the mountains, medkits and
     * batteries along the way, the gun in chapter 2.
     */
    static void scatter(int chapter, World w, Vector items, Vector enemies) {
        TileMap t = w.tiles;
        int W = t.w, H = t.h;
        // walkable tiles, scanned top-left to bottom-right
        Vector free = new Vector();
        for (int y = 1; y < H - 1; y++) {
            for (int x = 1; x < W - 1; x++) {
                if (!t.blocked(x, y) && (t.ids[y * W + x] & 0xFFFF) != 0) {
                    free.addElement(new int[]{x, y});
                }
            }
        }
        int n = free.size();
        if (n == 0) {
            return;
        }
        int step = Math.max(1, n / 24);
        int[] howlers = chapter == 1 ? new int[]{4, 10, 16} : chapter == 2 ? new int[]{3, 9} : new int[]{2};
        int[] walkers = chapter == 1 ? new int[]{20} : chapter == 2 ? new int[]{6, 14} : new int[]{4, 8, 12};
        for (int i = 0; i < howlers.length; i++) {
            int[] p = at(free, howlers[i] * step);
            if (p != null) {
                enemies.addElement(new Enemy(p[0] * World.T + 8, p[1] * World.T + 10, Enemy.HOWLER));
            }
        }
        for (int i = 0; i < walkers.length; i++) {
            int[] p = at(free, walkers[i] * step);
            if (p != null) {
                enemies.addElement(new Enemy(p[0] * World.T + 8, p[1] * World.T + 10, Enemy.WALKER));
            }
        }
        // supplies: medkits, batteries, ammo; the gun enters in chapter 2
        int[] meds = chapter == 1 ? new int[]{7, 18} : new int[]{5, 15};
        int[] batts = chapter == 1 ? new int[]{12} : new int[]{2, 11, 20};
        for (int i = 0; i < meds.length; i++) {
            int[] p = at(free, meds[i] * step);
            if (p != null) {
                items.addElement(new Item(p[0] * World.T + 8, p[1] * World.T + 8,
                        Item.MEDKIT, "YOU FOUND A FIRST AID KIT."));
            }
        }
        for (int i = 0; i < batts.length; i++) {
            int[] p = at(free, batts[i] * step);
            if (p != null) {
                items.addElement(new Item(p[0] * World.T + 8, p[1] * World.T + 8,
                        Item.BATTERY, "YOU FOUND SPARE BATTERIES."));
            }
        }
        if (chapter == 2) {
            int[] p = at(free, n / 2);
            if (p != null) {
                items.addElement(new Item(p[0] * World.T + 8, p[1] * World.T + 8,
                        Item.GUN, "JONATHAN GAVE YOU HIS GUN."));
            }
            p = at(free, n / 2 + step);
            if (p != null) {
                items.addElement(new Item(p[0] * World.T + 8, p[1] * World.T + 8,
                        Item.AMMO, "YOU FOUND A BOX OF SHELLS."));
            }
            p = at(free, n / 3);
            if (p != null) {
                items.addElement(new Item(p[0] * World.T + 8, p[1] * World.T + 8,
                        Item.CROWBAR, "YOU FOUND A CROWBAR. IT CAN OPEN THE DOOR."));
            }
        }
        if (chapter == 3) {
            int[] p = at(free, n / 2);
            if (p != null) {
                items.addElement(new Item(p[0] * World.T + 8, p[1] * World.T + 8,
                        Item.AMMO, "YOU FOUND A BOX OF SHELLS."));
            }
        }
    }

    private static int[] at(Vector free, int idx) {
        if (free.size() == 0) {
            return null;
        }
        while (idx >= free.size()) {
            idx -= free.size();
        }
        return (int[]) free.elementAt(idx);
    }

    static int itemType(int mapType) {
        switch (mapType) {
            case TileMap.IT_KEY:
                return Item.KEY;
            case TileMap.IT_NOTE:
                return Item.NOTE;
            case TileMap.IT_BATTERY:
                return Item.BATTERY;
            case TileMap.IT_FLASHLIGHT:
                return Item.FLASHLIGHT;
            case TileMap.IT_PROD:
                return Item.PROD;
            case TileMap.IT_CROWBAR:
                return Item.CROWBAR;
            case TileMap.IT_GUN:
                return Item.GUN;
            case TileMap.IT_AMMO:
                return Item.AMMO;
            default:
                return Item.MEDKIT;
        }
    }

    static String itemMsg(int mapType) {
        switch (mapType) {
            case TileMap.IT_KEY:
                return "YOU FOUND A SMALL KEY.";
            case TileMap.IT_NOTE:
                return "YOU TAKE THE NOTE. \"WHY IS THIS CAGE SO HEAVY? A CHILD COULD FIT IN HERE...\"";
            case TileMap.IT_BATTERY:
                return "YOU FOUND SPARE BATTERIES.";
            case TileMap.IT_FLASHLIGHT:
                return "YOU FOUND A FLASHLIGHT. IT WILL HOLD THE HOWLERS BACK.";
            case TileMap.IT_PROD:
                return "YOU FOUND THE CATTLE PROD. IT STILL CRACKLES.";
            case TileMap.IT_CROWBAR:
                return "YOU FOUND A CROWBAR. IT CAN OPEN THE DOOR.";
            case TileMap.IT_GUN:
                return "YOU FOUND A SHOTGUN.";
            case TileMap.IT_AMMO:
                return "YOU FOUND A BOX OF SHELLS.";
            default:
                return "YOU FOUND A FIRST AID KIT.";
        }
    }

    static Vector exitLines(int chapter) {
        if (chapter == 1) {
            return convo(new DLine[]{
                line(-1, null, "YOU ENTER THE HOUSE...")
            });
        }
        if (chapter == 2) {
            return convo(new DLine[]{
                line(-1, null, "THE MOUNTAIN PATH CONTINUES WEST, TOWARD THE VILLAGE...")
            });
        }
        return convo(new DLine[]{
            line(-1, null, "THE VILLAGE LIES JUST AHEAD..."),
            line(Assets.P_YOU, "YOU", "TH... THANK YOU!")
        });
    }
}
