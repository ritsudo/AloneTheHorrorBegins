import javax.microedition.lcdui.Canvas;
import javax.microedition.lcdui.Graphics;

/** Main menu plus the OPTIONS / HELP / ABOUT / STAT'S sub screens. */
class MenuScene extends Scene {
    static final int MAIN = 0;
    static final int OPTIONS = 1;
    static final int HELP = 2;
    static final int ABOUT = 3;
    static final int STATS = 4;
    static final int CONFIG = 5;

    int mode = MAIN;
    int sel = 0;

    static final String[] MAIN_ITEMS = {
        "NEW GAME", "STAT'S", "OPTIONS", "HELP", "ABOUT", "EXIT"
    };

    static final int MENU_TOP = 85;
    static final int MENU_STEP = 13;
    static final int MENU_CX = 88;

    static final int OPT_TOP = 77;
    static final int OPT_STEP = 13;

    boolean sound = true;
    boolean vibrate = true;
    String diff = "NORMAL";

    Fnt dark, light, menu, big;

    MenuScene(Game g) {
        super(g);
    }

    void enter() {
        Assets.ensure();
        dark = Fnt.get(Fnt.INK);
        light = Fnt.get(0xE8D8B8);
        menu = Fnt.getMenu(Fnt.INK);
        big = Fnt.getBig(Fnt.INK);
    }

    private boolean isMain() {
        return mode == MAIN;
    }

    void update() {
    }

    void keyPressed(int key, int action) {
        if (key == -6) { // left soft key (F1): leave a sub screen
            if (!isMain()) {
                mode = MAIN;
                sel = 2;
            }
            return;
        }
        if (isMain()) {
            if (action == Canvas.UP || key == Canvas.KEY_NUM2) {
                sel = (sel + MAIN_ITEMS.length - 1) % MAIN_ITEMS.length;
            } else if (action == Canvas.DOWN || key == Canvas.KEY_NUM8) {
                sel = (sel + 1) % MAIN_ITEMS.length;
            } else if (action == Canvas.FIRE || key == Canvas.KEY_NUM5) {
                select();
            }
        } else if (mode == OPTIONS) {
            int n = 6;
            if (action == Canvas.UP || key == Canvas.KEY_NUM2) {
                sel = (sel + n - 1) % n;
            } else if (action == Canvas.DOWN || key == Canvas.KEY_NUM8) {
                sel = (sel + 1) % n;
            } else if (action == Canvas.LEFT || action == Canvas.RIGHT
                    || action == Canvas.FIRE || key == Canvas.KEY_NUM5) {
                option();
            }
        } else if (mode == CONFIG) {
            if (action == Canvas.FIRE || key == Canvas.KEY_NUM5) {
                mode = OPTIONS;
                sel = 2;
            }
        } else {
            if (action == Canvas.FIRE || key == Canvas.KEY_NUM5) {
                mode = MAIN;
                sel = 0;
            }
        }
    }

    private void option() {
        if (sel == 0) {
            sound = !sound;
        } else if (sel == 1) {
            vibrate = !vibrate;
        } else if (sel == 2) {
            mode = CONFIG;
            sel = 0;
        } else if (sel == 3) {
            diff = diff.equals("NORMAL") ? "HARD" : (diff.equals("HARD") ? "EASY" : "NORMAL");
        } else if (sel == 4) {
            g.health = 100;
            g.battery = 100;
            g.hasFlashlight = false;
            g.hasKey = false;
            g.hasGun = false;
        } else {
            mode = MAIN;
            sel = 2;
        }
    }

    private void select() {
        switch (sel) {
            case 0:
                g.setScene(new LevelSelectScene(g));
                break;
            case 1:
                mode = STATS;
                sel = 0;
                break;
            case 2:
                mode = OPTIONS;
                sel = 0;
                break;
            case 3:
                mode = HELP;
                sel = 0;
                break;
            case 4:
                mode = ABOUT;
                sel = 0;
                break;
            case 5:
                g.setScene(new EndScene(g));
                break;
        }
    }

    void paint(Graphics gr) {
        gr.setColor(0);
        gr.fillRect(0, 0, Game.W, Game.H);
        if (isMain()) {
            Ui.menuBg(gr);
            paintMain(gr);
        } else {
            if (Assets.page != null) {
                gr.drawImage(Assets.page, 0, 0, Graphics.TOP | Graphics.LEFT);
            }
            paintSub(gr);
        }
    }

    private void paintMain(Graphics gr) {
        for (int i = 0; i < MAIN_ITEMS.length; i++) {
            int y = MENU_TOP + i * MENU_STEP;
            menu.drawCenter(gr, MAIN_ITEMS[i], MENU_CX, y);
        }
        int y = MENU_TOP + sel * MENU_STEP;
        Ui.campfires(gr, MENU_CX, menu.width(MAIN_ITEMS[sel]), y - 19);
    }

    private void paintSub(Graphics gr) {
        int cx = 88;
        if (mode == OPTIONS) {
            big.drawCenter(gr, "OPTIONS", cx, 49);
            String[] items = {
                "SOUND: " + (sound ? "ON" : "OFF"),
                "VIBRATION: " + (vibrate ? "ON" : "OFF"),
                "CONTROLS",
                "DIFF: " + diff,
                "RESET STAT'S?",
                "BACK"
            };
            for (int i = 0; i < items.length; i++) {
                int yy = OPT_TOP + i * OPT_STEP;
                menu.drawCenter(gr, items[i], cx, yy);
            }
            int y = OPT_TOP + sel * OPT_STEP;
            Ui.campfires(gr, cx, menu.width(items[sel]), y - 19);
        } else if (mode == CONFIG) {
            big.drawCenter(gr, "CONFIG 2/3", cx, 33);
            Fnt small = Fnt.getSmall(Fnt.INK);
            Fnt red = Fnt.getSmall(0xB02018);
            small.draw(gr, "SELF-FIRE:5", 18, 55);
            red.draw(gr, "ACTION", 84, 55);
            small.draw(gr, "BACK", 18, 65);
            red.draw(gr, "INFO", 84, 65);
            small.draw(gr, "0", 18, 75);
            red.draw(gr, "PAUSE", 84, 75);
            small.draw(gr, "1:3", 18, 85);
            red.draw(gr, "LIGHT", 84, 85);
            small.draw(gr, "2:4", 18, 95);
            red.draw(gr, "FORWARD", 84, 95);
            small.draw(gr, "6:8", 18, 105);
            red.draw(gr, "BACKWARD", 84, 105);
            red.draw(gr, "TURN LEFT", 84, 115);
            red.draw(gr, "TURN RIGHT", 84, 125);
            small.drawCenter(gr, "PRESS 5", cx, 165);
        } else if (mode == HELP) {
            big.drawCenter(gr, "HELP", cx, 55);
            String[] lines = {
                "MOVE WITH THE 2, 4, 6, 8",
                "KEYS OR THE D-PAD.",
                "USE 5 TO TALK, GRAB AN",
                "ITEM OR USE THE PROD.",
                "KEEP THE FLASHLIGHT",
                "CHARGED. HOWLERS FEAR",
                "THE LIGHT, THE WALKING",
                "DEAD DO NOT.",
                "PRESS 5 TO RETURN."
            };
            for (int i = 0; i < lines.length; i++) {
                dark.drawCenter(gr, lines[i], cx, 90 + i * 10);
            }
        } else if (mode == ABOUT) {
            big.drawCenter(gr, "ABOUT", cx, 55);
            String[] lines = {
                "ALONE",
                "THE HORROR BEGINS",
                "",
                "A SURVIVAL HORROR",
                "ADVENTURE.",
                "",
                "ORIGINAL BY CENTERSCORE",
                "REBUILT FOR MIDP 2.0.",
                "",
                "PRESS 5 TO RETURN."
            };
            for (int i = 0; i < lines.length; i++) {
                dark.drawCenter(gr, lines[i], cx, 90 + i * 10);
            }
        } else if (mode == STATS) {
            big.drawCenter(gr, "STAT'S", cx, 55);
            String[] lines = {
                "CHAPTER: " + g.chapter,
                "HEALTH: " + g.health,
                "BATTERIES: " + g.battery,
                "",
                "FLASHLIGHT: " + (g.hasFlashlight ? "YES" : "NO"),
                "KEY: " + (g.hasKey ? "YES" : "NO"),
                "GUN: " + (g.hasGun ? "YES" : "NO"),
                "SHELLS: " + g.gunAmmo + ", CELLS: " + g.spareBatteries,
                "",
                "PRESS 5 TO RETURN."
            };
            for (int i = 0; i < lines.length; i++) {
                dark.drawCenter(gr, lines[i], cx, 90 + i * 10);
            }
        }
    }
}
