import java.io.InputStream;
import javax.microedition.media.Manager;
import javax.microedition.media.Player;

/**
 * One MIDI channel for the whole game: theme, stingers and monster sounds.
 * Starting a new track stops and unloads the previous one immediately.
 */
class AudioManager {
    private static final AudioManager INSTANCE = new AudioManager();

    private Player player;
    private String current;

    static void playLoop(String res) {
        INSTANCE.play(res, -1);
    }

    static void playOnce(String res) {
        INSTANCE.play(res, 1);
    }

    static void stopAll() {
        INSTANCE.stop();
    }

    private void play(String res, int loop) {
        if (res == null) {
            return;
        }
        if (loop < 0 && res.equals(current) && player != null) {
            return;                 // the theme is already running
        }
        stop();
        InputStream in = null;
        try {
            in = getClass().getResourceAsStream("/" + res);
            if (in == null) {
                in = getClass().getResourceAsStream("/res/" + res);
            }
            if (in == null) {
                return;
            }
            Player p = Manager.createPlayer(in, "audio/midi");
            player = p;
            current = res;
            p.setLoopCount(loop);
            p.realize();
            p.prefetch();
            p.start();
        } catch (Throwable t) {
            try {
                if (in != null) {
                    in.close();
                }
            } catch (Throwable t2) {
            }
            stop();
        }
    }

    private void stop() {
        Player p = player;
        player = null;
        current = null;
        if (p == null) {
            return;
        }
        try {
            p.stop();
        } catch (Throwable t) {
        }
        try {
            p.deallocate();
        } catch (Throwable t) {
        }
        try {
            p.close();
        } catch (Throwable t) {
        }
    }
}
