import java.io.InputStream;
import java.util.Hashtable;
import javax.microedition.media.Manager;
import javax.microedition.media.Player;

/**
 * One MIDI channel for the whole game. Players are cached after the first
 * prefetch so repeated howls and moans do not recreate/decode MIDI data on the
 * game thread (that is what froze the game when several enemies screamed).
 * Starting a new cue stops the previous one immediately.
 */
class AudioManager {
    private static final AudioManager INSTANCE = new AudioManager();

    private final Hashtable cache = new Hashtable();
    private Player active;
    private String current;

    static void playLoop(String res) {
        INSTANCE.play(res, -1);
    }

    static void playOnce(String res) {
        INSTANCE.play(res, 1);
    }

    static void stopAll() {
        INSTANCE.unloadAll();
    }

    private void play(String res, int loop) {
        if (res == null) {
            return;
        }
        if (loop < 0 && res.equals(current) && active != null) {
            return;                 // the theme is already running
        }
        stopActive();
        try {
            Player p = (Player) cache.get(res);
            if (p == null) {
                InputStream in = getClass().getResourceAsStream("/" + res);
                if (in == null) {
                    in = getClass().getResourceAsStream("/res/" + res);
                }
                if (in == null) {
                    return;
                }
                p = Manager.createPlayer(in, "audio/midi");
                p.realize();
                p.prefetch();
                cache.put(res, p);
            }
            p.setLoopCount(loop);
            try {
                p.setMediaTime(0);
            } catch (Throwable t) {
            }
            p.start();
            active = p;
            current = res;
        } catch (Throwable t) {
            stopActive();
        }
    }

    private void stopActive() {
        Player p = active;
        active = null;
        current = null;
        if (p == null) {
            return;
        }
        try {
            p.stop();
        } catch (Throwable t) {
        }
    }

    /** Stops and unloads every decoded cue (used when gameplay starts/quits). */
    private void unloadAll() {
        stopActive();
        java.util.Enumeration keys = cache.keys();
        while (keys.hasMoreElements()) {
            Player p = (Player) cache.get(keys.nextElement());
            if (p == null) {
                continue;
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
        cache.clear();
    }
}
