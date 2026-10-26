import javax.microedition.midlet.MIDlet;
import javax.microedition.lcdui.Display;

public class horror extends MIDlet {
    private Game game;

    public void startApp() {
        if (game == null) {
            game = new Game();
            game.midlet = this;
        }
        Display.getDisplay(this).setCurrent(game);
        game.start();
    }

    public void pauseApp() {
        if (game != null) {
            game.pause();
        }
    }

    public void destroyApp(boolean unconditional) {
        if (game != null) {
            game.stop();
        }
    }
}
