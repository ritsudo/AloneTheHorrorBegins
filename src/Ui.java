import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.lcdui.game.Sprite;

/**
 * Shared drawing helpers for the parchment screens and the animated brazier
 * that marks the selected menu entry. The page background and the brazier are
 * composed at runtime (page.png + sign.png overlay) instead of shipping baked
 * duplicate screens.
 */
class Ui {
    static final int SIGN_X = 3;
    static final int SIGN_Y = 6;

    static final int CAMP_W = 20;
    static final int CAMP_H = 32;
    static final int CAMP_FRAMES = 10;
    static final int CAMP_GAP = 3;

    /** Global animation clock, advanced once per game tick. */
    static int anim;

    static void menuBg(Graphics g) {
        if (Assets.page != null) {
            g.drawImage(Assets.page, 0, 0, Graphics.TOP | Graphics.LEFT);
        }
        if (Assets.sign != null) {
            g.drawImage(Assets.sign, SIGN_X, SIGN_Y, Graphics.TOP | Graphics.LEFT);
        }
    }

    static void campfire(Graphics g, int x, int y) {
        if (Assets.campfire == null) {
            return;
        }
        int f = anim % CAMP_FRAMES;
        g.drawRegion(Assets.campfire, f * CAMP_W, 0, CAMP_W, CAMP_H,
                Sprite.TRANS_NONE, x, y, Graphics.TOP | Graphics.LEFT);
    }

    /** Draws a brazier on both sides of a label centred at cx. */
    static void campfires(Graphics g, int cx, int textW, int y) {
        int lx = cx - textW / 2 - CAMP_W - CAMP_GAP;
        int rx = cx + (textW + 1) / 2 + CAMP_GAP;
        campfire(g, lx, y);
        campfire(g, rx, y);
    }
}
