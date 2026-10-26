import javax.microedition.lcdui.Canvas;
import javax.microedition.lcdui.Graphics;

/** Parchment level select: only the unlocked chapter is listed. */
class LevelSelectScene extends Scene {
    int sel;
    int chapters;
    Fnt dark, big;

    LevelSelectScene(Game g) {
        super(g);
    }

    void enter() {
        Assets.ensure();
        dark = Fnt.get(Fnt.INK);
        big = Fnt.getBig(Fnt.INK);
        chapters = g.hasSave() ? g.chapter : 1;
        if (chapters < 1) {
            chapters = 1;
        }
        if (chapters > 3) {
            chapters = 3;
        }
        sel = 0;
    }

    void update() {
    }

    void keyPressed(int key, int action) {
        if (key == -6) {
            g.setScene(new MenuScene(g));
            return;
        }
        if (action == Canvas.UP || key == Canvas.KEY_NUM2) {
            sel = (sel + chapters - 1) % chapters;
        } else if (action == Canvas.DOWN || key == Canvas.KEY_NUM8) {
            sel = (sel + 1) % chapters;
        } else if (action == Canvas.FIRE || key == Canvas.KEY_NUM5) {
            g.setScene(new LoadingScene(g, sel + 1));
        }
    }

    void paint(Graphics gr) {
        gr.setColor(0);
        gr.fillRect(0, 0, Game.W, Game.H);
        if (Assets.page != null) {
            gr.drawImage(Assets.page, 0, 0, Graphics.TOP | Graphics.LEFT);
        }
        big.drawCenter(gr, "LEVEL SELECT", 88, 86);
        String label = "CHAPTER " + (sel + 1);
        dark.drawCenter(gr, label, 88, 114);
        Ui.campfires(gr, 88, dark.width(label), 104);
    }
}
