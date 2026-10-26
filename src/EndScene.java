import javax.microedition.lcdui.Canvas;
import javax.microedition.lcdui.Graphics;

/** Confirm before leaving the game. */
class EndScene extends Scene {
    int sel;
    Fnt dark;

    EndScene(Game g) {
        super(g);
    }

    void enter() {
        Assets.ensure();
        dark = Fnt.get(Fnt.INK);
        sel = 1;
    }

    void update() {
    }

    void keyPressed(int key, int action) {
        if (action == Canvas.LEFT || action == Canvas.RIGHT || action == Canvas.UP || action == Canvas.DOWN) {
            sel = 1 - sel;
        } else if (action == Canvas.FIRE || key == Canvas.KEY_NUM5) {
            if (sel == 0) {
                g.quit();
            } else {
                g.setScene(new MenuScene(g));
            }
        }
    }

    void paint(Graphics gr) {
        gr.setColor(0);
        gr.fillRect(0, 0, Game.W, Game.H);
        Ui.menuBg(gr);
        dark.drawCenter(gr, "EXIT GAME?", 88, 84);
        dark.drawCenter(gr, "YES", 55, 110);
        dark.drawCenter(gr, "NO", 121, 110);
        String pick = sel == 0 ? "YES" : "NO";
        int cx = sel == 0 ? 55 : 121;
        Ui.campfires(gr, cx, dark.width(pick), 99);
    }
}
