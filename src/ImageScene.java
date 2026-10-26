import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;

/** Shows one baked full screen image for a while, then moves on. */
class ImageScene extends Scene {
    Image img;
    int ticks;
    int delay;

    ImageScene(Game g, String res, int delay) {
        super(g);
        this.img = Assets.load(res);
        this.delay = delay;
    }

    void enter() {
        ticks = 0;
    }

    void update() {
        ticks++;
        if (ticks > delay) {
            advance();
        }
    }

    private void advance() {
        g.setScene(new MenuScene(g));
    }

    void keyPressed(int key, int action) {
        advance();
    }

    void paint(Graphics gr) {
        gr.setColor(0);
        gr.fillRect(0, 0, Game.W, Game.H);
        if (img != null) {
            gr.drawImage(img, 0, 0, Graphics.TOP | Graphics.LEFT);
        }
    }
}
