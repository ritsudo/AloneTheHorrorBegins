import javax.microedition.lcdui.Canvas;
import javax.microedition.lcdui.Graphics;

/** Ending card shown after the red doors in chapter 3. */
class EndingScene extends Scene {
    static final String TEXT =
            "This is a demo restoration of the original game in 2026, made by ritsudo. "
            + "If you have any new screenshots, materials of the game feel free to add "
            + "them on my GitHub. Thanks for playing";

    Fnt title;
    Fnt body;
    Fnt prompt;
    String[] lines;

    EndingScene(Game g) {
        super(g);
    }

    void enter() {
        Assets.ensure();
        title = Fnt.getBig(0xC03020);
        body = Fnt.get(0xD8C0A0);
        prompt = Fnt.get(0xD8C0A0);
        lines = body.wrap(TEXT.toUpperCase(), 156);
    }

    void update() {
    }

    void keyPressed(int key, int action) {
        if (action == Canvas.FIRE || key == Canvas.KEY_NUM5) {
            g.setScene(new MenuScene(g));
        }
    }

    void paint(Graphics gr) {
        gr.setColor(0);
        gr.fillRect(0, 0, Game.W, Game.H);
        title.drawCenter(gr, "THE END", 88, 18);
        int y = 50;
        for (int i = 0; i < lines.length; i++) {
            body.drawCenter(gr, lines[i], 88, y);
            y += 12;
        }
        prompt.drawCenter(gr, "PRESS 5", 88, 192);
    }
}
