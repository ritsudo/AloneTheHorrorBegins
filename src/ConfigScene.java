import javax.microedition.lcdui.Graphics;

/** Controls tutorial shown once after loading, before the chapter card. */
class ConfigScene extends Scene {
    int chapter;
    int t;
    Fnt small, smallRed, big;

    ConfigScene(Game g, int chapter) {
        super(g);
        this.chapter = chapter;
    }

    void enter() {
        Assets.ensure();
        small = Fnt.getSmall(Fnt.INK);
        smallRed = Fnt.getSmall(0xB02018);
        big = Fnt.getBig(Fnt.INK);
        t = 0;
    }

    void update() {
        t++;
        if (t > 80) {
            g.setScene(new ChapterScene(g, chapter));
        }
    }

    void keyPressed(int key, int action) {
        g.setScene(new ChapterScene(g, chapter));
    }

    void paint(Graphics gr) {
        gr.setColor(0);
        gr.fillRect(0, 0, Game.W, Game.H);
        if (Assets.page != null) {
            gr.drawImage(Assets.page, 0, 0, Graphics.TOP | Graphics.LEFT);
        }
        big.drawCenter(gr, "CONFIG 2/3", 88, 33);
        small.draw(gr, "SEL,FIRE,5", 16, 55);
        smallRed.drawRight(gr, "ACTION", 159, 55);
        small.draw(gr, "0", 19, 65);
        smallRed.drawRight(gr, "INFO", 159, 65);
        small.draw(gr, "BACK", 16, 75);
        smallRed.drawRight(gr, "PAUSE", 159, 75);
        gr.fillRect(16, 95, 144, 3);
        small.draw(gr, "1,3", 19, 95);
        smallRed.drawRight(gr, "LIGHT", 159, 95);
        gr.fillRect(16, 115, 144, 3);
        small.draw(gr, "2,", 18, 115);
        smallRed.drawRight(gr, "FORWARD", 159, 115);
        small.draw(gr, "8,", 18, 125);
        smallRed.drawRight(gr, "BACKWARD", 159, 125);
        small.draw(gr, "4,", 18, 135);
        smallRed.drawRight(gr, "TURN LEFT", 159, 135);
        small.draw(gr, "6,", 18, 145);
        smallRed.drawRight(gr, "TURN RIGHT", 159, 145);
        gr.fillTriangle(34, 121, 30, 128, 38, 128);
        gr.fillTriangle(30, 131, 38, 131, 34, 138);
        gr.fillTriangle(30, 140, 38, 144, 30, 148);
        gr.fillTriangle(38, 150, 30, 154, 38, 158);
    }
}
