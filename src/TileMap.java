import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.lcdui.game.Sprite;

/**
 * A JMAP binary map: terrain tile ids + collision bytes + object records.
 *
 * Format (big endian, see sdk-map-editor/docs/FORMAT.md):
 *   "JMAP", u8 version, u8 flags, u8 layerMask, u8 tileSize,
 *   u16 width, u16 height, u16 objectCount, u8 nameLen, name,
 *   u32 terrainLen + payload (raw u16 or RLE u16 value/u16 run),
 *   u32 collisionLen + payload (same coding),
 *   objectCount * { u8 kind, u16 type, u16 x, u16 y, u8 flags, u16 param }
 *
 * The terrain ids index the 8x8 grid atlas res/tileset_grid.png
 * (8 columns of 16px tiles, id N at N%8 / N/8). Tile 0 is void/black.
 */
class TileMap {
    int tw = 16;
    int w, h;
    short[] ids;
    byte[] solid;
    int objCount;
    //@CM: objects arrays
    int[] objKind;
    int[] objType;
    int[] objX;
    int[] objY;
    int[] objParam;
    Image atlas;
    int cols;
    static final int ATLAS_COLS = 8;    // tileset_grid.png is 8x8 tiles

    // collision bits (FORMAT.md)
    static final int C_SOLID = 0x01;
    static final int C_WATER = 0x02;
    static final int C_HAZARD = 0x08;

    // object kinds / ids (sdk ranges)
    static final int K_ITEM = 0;
    static final int K_ENEMY = 1;
    static final int K_TRIGGER = 2;

    static final int T_SPAWN = 4608;
    static final int T_EXIT = 4609;
    static final int T_CUTSCENE = 4611;
    static final int T_TALK = 4612;      // chapter 1: talk to Jonathan
    static final int T_DOOR = 4613;      // chapter 3: crowbar door

    // item types
    static final int IT_HEALTH = 4096;
    static final int IT_AMMO = 4097;
    static final int IT_KEY = 4098;
    static final int IT_NOTE = 4099;
    static final int IT_BATTERY = 4100;
    static final int IT_FLASHLIGHT = 4101;
    static final int IT_PROD = 4102;
    static final int IT_CROWBAR = 4103;
    static final int IT_GUN = 4104;

    // enemy types
    static final int EN_HOWLER = 4352;
    static final int EN_WALKER = 4353;

    private int pos;
    private byte[] buf;

    static TileMap load(byte[] blob) {
        TileMap m = new TileMap();
        if (blob == null || blob.length < 17 || blob[0] != 'J' || blob[1] != 'M'
                || blob[2] != 'A' || blob[3] != 'P') {
            return m;
        }
        try {
            m.buf = blob;
            m.pos = 4;
            int version = m.u8();
            int flags = m.u8();
            int layerMask = m.u8();
            m.tw = m.u8();
            m.w = m.u16();
            m.h = m.u16();
            m.objCount = m.u16();
            int nameLen = m.u8();
            m.pos += nameLen;
            int count = m.w * m.h;
            m.ids = m.readLayer(count, (flags & 1) != 0);
            short[] col = m.readLayer(count, (flags & 2) != 0);
            m.solid = new byte[count];
            for (int i = 0; i < count; i++) {
                m.solid[i] = (byte) col[i];
            }
            m.objKind = new int[m.objCount];
            m.objType = new int[m.objCount];
            m.objX = new int[m.objCount];
            m.objY = new int[m.objCount];
            m.objParam = new int[m.objCount];
            for (int i = 0; i < m.objCount; i++) {
                m.objKind[i] = m.u8();
                m.objType[i] = m.u16();
                m.objX[i] = m.u16();
                m.objY[i] = m.u16();
                m.u8();              // flags
                m.objParam[i] = m.u16();
            }
        } catch (Throwable t) {
            m.ids = null;
            return m;
        }
        m.atlas = Assets.tileset;
        if (m.atlas != null) {
            int c = m.atlas.getWidth() / m.tw;
            m.cols = c > 0 ? c : ATLAS_COLS;
        }
        return m;
    }

    private int u8() {
        return buf[pos++] & 0xFF;
    }

    private int u16() {
        int hi = u8();
        return (hi << 8) | u8();
    }

    private short[] readLayer(int count, boolean rle) {
        int len = u16() << 16;      // u32 length, maps are small
        len |= u16();
        short[] values = new short[count];
        if (!rle) {
            for (int i = 0; i < count; i++) {
                values[i] = (short) u16();
            }
        } else {
            int done = 0;
            int end = pos + len;
            while (done < count && pos + 4 <= end) {
                int value = u16();
                int run = u16();
                for (int i = 0; i < run && done < count; i++) {
                    values[done++] = (short) value;
                }
            }
            pos = end;          // the object layer starts after the payload
        }
        return values;
    }

    boolean ready() {
        return ids != null && atlas != null;
    }

    /** Selects the atlas image this map's terrain ids refer to. */
    void useAtlas(Image im) {
        if (im == null) {
            return;
        }
        atlas = im;
        cols = im.getWidth() / tw;
    }

    boolean blocked(int tx, int ty) {
        if (tx < 0 || ty < 0 || tx >= w || ty >= h) {
            return true;
        }
        return (solid[ty * w + tx] & C_SOLID) != 0;
    }

    /** First object of the given trigger type, or null. */
    int[] findTrigger(int type) {
        for (int i = 0; i < objCount; i++) {
            if (objKind[i] == K_TRIGGER && objType[i] == type) {
                return new int[]{objX[i], objY[i], objParam[i]};
            }
        }
        return null;
    }

    void paint(Graphics g, int camX, int camY) {
        int x0 = camX / tw;
        int y0 = camY / tw;
        int x1 = (camX + Game.W) / tw + 1;
        int y1 = (camY + Game.H) / tw + 1;
        for (int ty = y0; ty <= y1; ty++) {
            for (int tx = x0; tx <= x1; tx++) {
                int sx = tx * tw - camX;
                int sy = ty * tw - camY;
                if (tx < 0 || ty < 0 || tx >= w || ty >= h) {
                    g.setColor(0);
                    g.fillRect(sx, sy, tw, tw);
                    continue;
                }
                int id = ids[ty * w + tx] & 0xFFFF;
                if (id == 0) {
                    g.setColor(0);
                    g.fillRect(sx, sy, tw, tw);
                    continue;
                }
                int cx = (id % cols) * tw;
                int cy = (id / cols) * tw;
                g.drawRegion(atlas, cx, cy, tw, tw, Sprite.TRANS_NONE,
                        sx, sy, Graphics.TOP | Graphics.LEFT);
            }
        }
    }
}
