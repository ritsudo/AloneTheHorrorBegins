import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.lcdui.game.Sprite;

/**
 * Top status bar. The heart + artery gauge appears only while combat is in
 * progress (demo: absent in the calm ch2 mountain, present during the ch1
 * woods, the howler fight and the walker fights). The vein is blue in the
 * first chapter and red later (demo 320 vs 3063). The right edge shows one
 * battery icon per cell: the one in use dims yellow -> red -> grey as it
 * drains (demo 2145 / 2000 / 900).
 */
class Hud {
    void paint(Graphics g, Game game, boolean showAlert, boolean redVein) {
        boolean fighting = game.combatT > 0;
        if (fighting) {
            if (Assets.heart != null) {
                g.drawImage(Assets.heart, 0, 0, Graphics.TOP | Graphics.LEFT);
            }
            Image vein = (redVein ? Assets.veinRed : Assets.vein);
            if (vein != null) {
                int full = vein.getWidth();
                int vw = full * game.health / 100;
                if (vw > 0) {
                    g.drawRegion(vein, 0, 0, vw, vein.getHeight(),
                            Sprite.TRANS_NONE, 24, 0,
                            Graphics.TOP | Graphics.LEFT);
                }
            }
        }
        if (showAlert && Assets.alert != null) {
            g.drawImage(Assets.alert, 84, 0, Graphics.TOP | Graphics.LEFT);
        }
        // battery row: current cell first (charge state), then spares
        if (game.hasFlashlight || game.battery > 0 || game.spareBatteries > 0) {
            int x = 168;
            Image cur;
            if (game.battery >= 55) {
                cur = Assets.hudCell;
            } else if (game.battery > 0) {
                cur = Assets.hudCellRed;
            } else {
                cur = Assets.hudCellOff;
            }
            if (cur != null) {
                g.drawImage(cur, x, 2, Graphics.TOP | Graphics.LEFT);
                x -= 8;
            }
            for (int i = 0; i < game.spareBatteries && x >= 152; i++) {
                if (Assets.hudCell != null) {
                    g.drawImage(Assets.hudCell, x, 2, Graphics.TOP | Graphics.LEFT);
                }
                x -= 8;
            }
        }
    }
}
