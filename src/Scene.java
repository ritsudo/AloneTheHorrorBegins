import javax.microedition.lcdui.Graphics;

abstract class Scene {
    protected Game g;

    Scene(Game g) {
        this.g = g;
    }

    void enter() {
    }

    abstract void update();

    abstract void paint(Graphics gr);

    void keyPressed(int key, int action) {
    }

    void keyReleased(int key) {
    }
}
