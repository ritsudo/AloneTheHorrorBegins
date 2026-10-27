import javax.microedition.lcdui.Canvas;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.rms.RecordStore;

public class Game extends Canvas implements Runnable {
    public static final int W = 176;
    public static final int H = 208;

    public static final int DIR_LEFT = 0;
    public static final int DIR_RIGHT = 1;
    public static final int DIR_UP = 2;
    public static final int DIR_DOWN = 3;

    // global player state
    public int health = 100;
    public int battery = 100;          // charge of the cell in use
    public int spareBatteries = 0;     // full cells waiting in the pocket
    public boolean hasFlashlight = false;
    public boolean hasGun = false;
    public int gunAmmo = 0;
    public boolean hasKey = false;
    public boolean hasCrowbar = false;
    public int chapter = 1;
    public String playerName = "YOU";

    // combat display: the heart gauge appears only while fighting
    public int combatT = 0;

    Scene scene;
    Thread thread;
    volatile boolean running = false;
    Image buffer;
    public horror midlet;

    public Game() {
        setFullScreenMode(true);
        buffer = Image.createImage(W, H);
    }

    public void start() {
        if (running) {
            return;
        }
        running = true;
        thread = new Thread(this);
        thread.start();
        if (scene == null) {
            setScene(new LogoScene(this));
        }
    }

    public void pause() {
    }

    public void stop() {
        running = false;
        thread = null;
        AudioManager.stopAll();
    }

    public void setScene(Scene s) {
        if (s instanceof PlayScene) {
            AudioManager.stopAll();      // gameplay has its own sound effects
        } else if (s instanceof MenuScene || s instanceof LogoScene) {
            AudioManager.playLoop("main_theme.mid");
        }
        scene = s;
        scene.enter();
    }

    public void quit() {
        if (midlet != null) {
            midlet.notifyDestroyed();
        }
    }

    public void run() {
        while (running) {
            try {
                Scene s = scene;
                if (s != null) {
                    Ui.anim++;
                    if (combatT > 0) {
                        combatT--;
                    }
                    s.update();
                    Graphics g = buffer.getGraphics();
                    s.paint(g);
                    repaint();
                    serviceRepaints();
                }
                Thread.sleep(40);
            } catch (Throwable t) {
                // keep the loop alive
            }
        }
    }

    protected void paint(Graphics g) {
        int cw = getWidth();
        int ch = getHeight();
        int ox = (cw - W) / 2;
        int oy = (ch - H) / 2;
        if (ox > 0 || oy > 0) {
            g.setColor(0);
            g.fillRect(0, 0, cw, ch);
        }
        g.drawImage(buffer, ox, oy, Graphics.TOP | Graphics.LEFT);
    }

    protected void keyPressed(int key) {
        int a = 0;
        try {
            a = getGameAction(key);
        } catch (Exception e) {
        }
        Scene s = scene;
        if (s != null) {
            s.keyPressed(key, a);
        }
    }

    protected void keyReleased(int key) {
        Scene s = scene;
        if (s != null) {
            s.keyReleased(key);
        }
    }

    protected void showNotify() {
    }

    // ------------------------------------------------------------ save game
    public void saveGame() {
        try {
            RecordStore rs = RecordStore.openRecordStore("alone", true);
            byte[] data = new byte[10];
            data[0] = (byte) chapter;
            data[1] = (byte) health;
            data[2] = (byte) battery;
            data[3] = (byte) (hasFlashlight ? 1 : 0);
            data[4] = (byte) (hasKey ? 1 : 0);
            data[5] = (byte) (hasGun ? 1 : 0);
            data[6] = (byte) gunAmmo;
            data[7] = (byte) spareBatteries;
            data[8] = (byte) (hasCrowbar ? 1 : 0);
            data[9] = 0;
            if (rs.getNumRecords() == 0) {
                rs.addRecord(data, 0, data.length);
            } else {
                rs.setRecord(1, data, 0, data.length);
            }
            rs.closeRecordStore();
        } catch (Exception e) {
        }
    }

    public boolean hasSave() {
        try {
            RecordStore rs = RecordStore.openRecordStore("alone", false);
            boolean ok = rs.getNumRecords() > 0;
            rs.closeRecordStore();
            return ok;
        } catch (Exception e) {
            return false;
        }
    }

    public void loadGame() {
        try {
            RecordStore rs = RecordStore.openRecordStore("alone", false);
            byte[] data = rs.getRecord(1);
            chapter = data[0];
            health = data[1];
            battery = data[2];
            hasFlashlight = data[3] != 0;
            hasKey = data[4] != 0;
            hasGun = data[5] != 0;
            gunAmmo = data[6];
            spareBatteries = data[7];
            hasCrowbar = data[8] != 0;
            rs.closeRecordStore();
        } catch (Exception e) {
        }
    }
}
