import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import javax.microedition.lcdui.Graphics;

/**
 * A scrollable tile map world loaded from a JMAP binary (see TileMap).
 * Terrain, collision and the object layer all come from the recovered
 * chapter maps; gameplay entities are spawned from the object records.
 *
 * The .jmap payloads live in the JAR (res/chapter*.jmap) and are read
 * through getResourceAsStream - embedding them as static byte[] initialisers
 * exceeds the CLDC 32 kB per-method bytecode limit.
 */
class World {
    static final int T = 16;

    TileMap tiles;
    String name;
    boolean dark = true;
    int lightRadius = 80;

    int spawnX, spawnY;
    int exitX = -1, exitY = -1;

    World(String name) {
        this.name = name;
    }

    /** Reads a packaged resource fully; returns null when unavailable. */
    byte[] readResource(String name) {
        InputStream in = null;
        try {
            in = getClass().getResourceAsStream(name);
            if (in == null) {
                in = getClass().getResourceAsStream("/res/" + name.substring(1));
            }
            if (in == null) {
                return null;
            }
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buf = new byte[512];
            int n;
            while ((n = in.read(buf)) != -1) {
                out.write(buf, 0, n);
            }
            in.close();
            return out.toByteArray();
        } catch (Throwable t) {
            try {
                if (in != null) {
                    in.close();
                }
            } catch (Throwable t2) {
            }
            return null;
        }
    }

    static World load(int chapter) {
        World w = new World("chapter" + chapter);
        byte[] blob = w.readResource("/chapter" + chapter + ".jmap");
        w.tiles = TileMap.load(blob);
        if (!w.tiles.ready()) {
            // fall back to a flat walkable box so the chapter still plays
            w.tiles.w = 20;
            w.tiles.h = 15;
        }
        int[] sp = w.tiles.findTrigger(TileMap.T_SPAWN);
        if (sp != null) {
            w.spawnX = sp[0] * T + 8;
            w.spawnY = sp[1] * T + 8;
        } else {
            w.spawnX = T + 8;
            w.spawnY = T + 8;
        }
        int[] ex = w.tiles.findTrigger(TileMap.T_EXIT);
        if (ex != null) {
            w.exitX = ex[0] * T + 8;
            w.exitY = ex[1] * T + 8;
        }
        return w;
    }

    int widthTiles() {
        return tiles.w;
    }

    int heightTiles() {
        return tiles.h;
    }

    boolean blocked(int tx, int ty) {
        if (tiles.ready()) {
            return tiles.blocked(tx, ty);
        }
        return tx <= 0 || ty <= 0 || tx >= tiles.w - 1 || ty >= tiles.h - 1;
    }

    void paint(Graphics g, int camX, int camY) {
        if (tiles.ready()) {
            tiles.paint(g, camX, camY);
            return;
        }
        g.setColor(0x0A140A);
        g.fillRect(0, 0, Game.W, Game.H);
    }
}
