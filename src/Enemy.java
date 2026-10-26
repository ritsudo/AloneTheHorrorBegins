import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.lcdui.game.Sprite;

/**
 * A creature. HOWLERS are the violet beasts that hate the light: they hunt
 * in the dark, turn white-hot while the beam holds them and dissolve.
 * WALKERS are the pale dead: light means nothing to them, they close in and
 * must be shot or stabbed.
 */
class Enemy {
    static final int HOWLER = 0;
    static final int WALKER = 1;

    static final int FW_Z = 22;      // zombie cell
    static final int FH_Z = 26;
    static final int FW_H = 26;      // howler cell
    static final int FH_H = 32;

    static final int ST_WALK = 0;
    static final int ST_LIT = 1;     // caught in the beam (howler)
    static final int ST_DYING = 2;

    int x, y;
    int type;
    int hp;
    int state = ST_WALK;
    int dir = Game.DIR_DOWN;
    int frame = 0;
    int animT = 0;
    int wanderT = 0;
    int wx = 0, wy = 0;
    int dieT = 0;
    int hurtT = 0;
    int speed = 1;

    Enemy(int x, int y, int type) {
        this.x = x;
        this.y = y;
        this.type = type;
        hp = type == HOWLER ? 2 : 3;
        speed = type == HOWLER ? 2 : 1;
    }

    boolean lit(int px, int py, boolean flash, int radius) {
        if (!flash) {
            return false;
        }
        int dx = x - px;
        int dy = (y - 6) - (py - 10);
        return dx * dx + dy * dy < radius * radius;
    }

    void hit(int dmg) {
        if (state == ST_DYING) {
            return;
        }
        hp -= dmg;
        hurtT = 6;
        if (hp <= 0) {
            state = ST_DYING;
            dieT = 0;
        }
    }

    void update(World world, int px, int py, boolean flash, int radius) {
        if (state == ST_DYING) {
            dieT++;
            return;
        }
        if (hurtT > 0) {
            hurtT--;
        }
        // a howler caught in the beam burns away
        if (type == HOWLER && lit(px, py, flash, radius)) {
            state = ST_LIT;
            hp--;
            if (hp <= 0) {
                state = ST_DYING;
                dieT = 0;
                return;
            }
        } else if (state == ST_LIT) {
            state = ST_WALK;
        }

        int dx = px - x;
        int dy = py - y;
        int d2 = dx * dx + dy * dy;
        boolean afraid = (type == HOWLER) && (state == ST_LIT || lit(px, py, flash, radius));
        int mvx = 0, mvy = 0;
        if (d2 < 90 * 90 && !afraid) {
            if (d2 > 14 * 14) {                     // close in, keep some slack
                if (dx * dx > dy * dy) {
                    mvx = dx > 0 ? speed : -speed;
                } else {
                    mvy = dy > 0 ? speed : -speed;
                }
            }
        } else {
            wanderT--;
            if (wanderT <= 0) {
                wanderT = 30 + (int) (System.currentTimeMillis() % 45);
                long t = System.currentTimeMillis();
                wx = (int) (t % 3) - 1;
                wy = (int) ((t >> 3) % 3) - 1;
                if (wx == 0 && wy == 0) {
                    wx = 1;
                }
            }
            mvx = wx;
            mvy = wy;
        }
        if (afraid && type == HOWLER) {
            // bolt away from the light
            if (dx * dx > dy * dy) {
                mvx = dx > 0 ? -2 : 2;
            } else {
                mvy = dy > 0 ? -2 : 2;
            }
        }
        if (mvx != 0 || mvy != 0) {
            int nx = x + mvx;
            int ny = y + mvy;
            if (!world.blocked(nx / World.T, (ny - 6) / World.T)) {
                x = nx;
                y = ny;
            } else if (!world.blocked(nx / World.T, (y - 6) / World.T)) {
                x = nx;
            } else if (!world.blocked(x / World.T, (ny - 6) / World.T)) {
                y = ny;
            } else {
                wanderT = 0;
            }
            if (mvx != 0) {
                dir = mvx < 0 ? Game.DIR_LEFT : Game.DIR_RIGHT;
            } else {
                dir = mvy < 0 ? Game.DIR_UP : Game.DIR_DOWN;
            }
            animT++;
            if (animT > 7) {
                animT = 0;
                frame = (frame + 1) % 3;
            }
        }
    }

    void paint(Graphics g, int camX, int camY) {
        if (state == ST_DYING) {
            Image[] de = Assets.death;
            if (de == null || de[0] == null) {
                return;
            }
            Image im = dieT < 8 ? de[1] : de[0];    // spread fall, then skull
            int w = im.getWidth();
            int h = im.getHeight();
            g.drawImage(im, x - camX - w / 2, y - camY - h + 4,
                    Graphics.TOP | Graphics.LEFT);
            if (dieT > 26) {
                g.setColor(0);                      // fade the skull into the dark
                g.fillRect(x - camX - w / 2, y - camY - h + 4, w, h);
            }
            return;
        }
        if (type == WALKER) {
            Image sheet = Assets.zombie;
            if (sheet == null) {
                return;
            }
            int sx = frame * FW_Z;
            int tr = dir == Game.DIR_RIGHT ? Sprite.TRANS_MIRROR : Sprite.TRANS_NONE;
            if (hurtT > 0) {
                g.setColor(0xFFFFFF);
            }
            g.drawRegion(sheet, sx, 0, FW_Z, FH_Z, tr,
                    x - camX - FW_Z / 2, y - camY - FH_Z + 4,
                    Graphics.TOP | Graphics.LEFT);
        } else {
            Image sheet = Assets.howler;
            if (sheet == null) {
                return;
            }
            int cell = state == ST_LIT ? 2 : frame % 2;
            g.drawRegion(sheet, cell * FW_H, 0, FW_H, FH_H, Sprite.TRANS_NONE,
                    x - camX - FW_H / 2, y - camY - FH_H + 6,
                    Graphics.TOP | Graphics.LEFT);
        }
    }
}
