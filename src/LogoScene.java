import javax.microedition.lcdui.Graphics;

/** Centerscore logo, then the animated title screen. */
class LogoScene extends Scene {
    int ticks;

    LogoScene(Game g) {
        super(g);
    }

    void enter() {
        ticks = 0;
        Assets.ensure();
    }

    void update() {
        ticks++;
        if (ticks == 70) {
            g.setScene(new ImageScene(g, "title.png", 110));
        }
    }

    void keyPressed(int key, int action) {
        g.setScene(new MenuScene(g));
    }

    void paint(Graphics gr) {
        gr.setColor(0);
        gr.fillRect(0, 0, Game.W, Game.H);
        if (Assets.logo != null) {
            gr.drawImage(Assets.logo, 0, 0, Graphics.TOP | Graphics.LEFT);
        }
    }
}
