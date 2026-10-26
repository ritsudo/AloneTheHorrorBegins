import javax.microedition.lcdui.Canvas;
import javax.microedition.lcdui.Graphics;

/** Overlay menu shown over a frozen playing field. */
class PauseScene extends Scene {
    PlayScene play;
    int sel = 0;
    int msgT = 0;
    Fnt dark;
    static final String[] ITEMS = { "RESUME", "SAVE GAME", "OPTIONS", "MAIN MENU" };

    PauseScene(Game g, PlayScene play) {
        super(g);
        this.play = play;
    }

    void enter() {
        Assets.ensure();
        dark = Fnt.get(Fnt.INK);
    }

    void update() {
        if (msgT > 0) {
            msgT--;
        }
    }

    void keyPressed(int key, int action) {
        if (action == Canvas.UP || key == Canvas.KEY_NUM2) {
            sel = (sel + ITEMS.length - 1) % ITEMS.length;
        } else if (action == Canvas.DOWN || key == Canvas.KEY_NUM8) {
            sel = (sel + 1) % ITEMS.length;
        } else if (action == Canvas.FIRE || key == Canvas.KEY_NUM5) {
            switch (sel) {
                case 0:
                    g.setScene(play);
                    break;
                case 1:
                    g.saveGame();
                    msgT = 40;
                    break;
                case 2:
                    g.setScene(new MenuScene(g));
                    break;
                default:
                    g.setScene(new MenuScene(g));
                    break;
            }
        }
    }

    void paint(Graphics gr) {
        play.paintWorldOnly(gr);
        gr.setColor(0x402818);
        gr.fillRect(20, 40, 136, 118);
        gr.setColor(0xE8D8B8);
        gr.fillRect(21, 41, 134, 116);
        dark.drawCenter(gr, "PAUSED", 88, 50);
        for (int i = 0; i < ITEMS.length; i++) {
            int y = 72 + i * 16;
            dark.drawCenter(gr, ITEMS[i], 88, y);
            if (i == sel) {
                Ui.campfire(gr, 28, y - 10);
            }
        }
        if (msgT > 0) {
            dark.drawCenter(gr, "GAME SAVED", 88, 150);
        }
    }
}
