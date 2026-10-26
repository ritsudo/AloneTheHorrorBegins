import javax.microedition.lcdui.Graphics;

/** Parchment loading screen with an animated ellipsis and a tip. */
class LoadingScene extends Scene {
    int chapter;
    int t;
    Fnt dark, load;
    String tip;

    static final String[] TIPS = {
        "YOUR FIRST INSTINCT SHOULD BE TO RUN.",
        "THE NATURAL LIGHT FROM TORCHES HAS A DEVASTATING EFFECT ON HOWLERS.",
        "BACKUP YOUR PROGRESS. SAVE THE GAME OFTEN."
    };

    LoadingScene(Game g, int chapter) {
        super(g);
        this.chapter = chapter;
    }

    void enter() {
        Assets.ensure();
        dark = Fnt.get(Fnt.INK);
        load = Fnt.getLoad(Fnt.INK);
        tip = TIPS[(chapter - 1) % TIPS.length];
        t = 0;
    }

    void update() {
        t++;
        if (t > 110) {
            advance();
        }
    }

    void keyPressed(int key, int action) {
        advance();
    }

    private void advance() {
        if (chapter == 1) {
            g.setScene(new ConfigScene(g, chapter));
        } else {
            g.setScene(new ChapterScene(g, chapter));
        }
    }

    void paint(Graphics gr) {
        gr.setColor(0);
        gr.fillRect(0, 0, Game.W, Game.H);
        if (Assets.page != null) {
            gr.drawImage(Assets.page, 0, 0, Graphics.TOP | Graphics.LEFT);
        }
        int d = (t / 8) % 4;
        String dots = d == 0 ? "" : (d == 1 ? "." : (d == 2 ? ".." : "..."));
        load.drawCenter(gr, "LOADING" + dots, 88, 74);
        String[] w = dark.wrap(tip, 145);
        for (int i = 0; i < w.length; i++) {
            dark.drawCenter(gr, w[i], 88, 104 + i * 10);
        }
    }
}
