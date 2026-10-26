import javax.microedition.lcdui.Graphics;

/** Chapter title card shown before each chapter starts. */
class ChapterScene extends Scene {
    int chapter;
    int t;
    Fnt dark, big;

    static final String[] NAMES = {
        "FALLEN FROM THE SKY",
        "PARTING WORDS",
        "THE TREK WEST"
    };

    ChapterScene(Game g, int chapter) {
        super(g);
        this.chapter = chapter;
    }

    void enter() {
        Assets.ensure();
        dark = Fnt.get(Fnt.INK);
        big = Fnt.getBig(Fnt.INK);
        t = 0;
    }

    void update() {
        t++;
        if (t > 60) {
            g.setScene(new PlayScene(g, chapter));
        }
    }

    void keyPressed(int key, int action) {
        g.setScene(new PlayScene(g, chapter));
    }

    void paint(Graphics gr) {
        gr.setColor(0);
        gr.fillRect(0, 0, Game.W, Game.H);
        if (Assets.page != null) {
            gr.drawImage(Assets.page, 0, 0, Graphics.TOP | Graphics.LEFT);
        }
        big.drawCenter(gr, "CHAPTER: " + chapter, 88, 83);
        String name = NAMES[(chapter - 1) % NAMES.length];
        String[] w = dark.wrap(name, 140);
        for (int i = 0; i < w.length; i++) {
            dark.drawCenter(gr, w[i], 88, 107 + i * 10);
        }
    }
}
